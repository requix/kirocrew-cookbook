---
title: The knowledge library
description: Give the agent your docs to search by meaning, with citations. What it stores, how it indexes, and how it differs from memory.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [knowledge, search, retrieval, memory, embeddings]
updated: 2026-10-30
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
  - A folder of docs, runbooks, specs or notes you want the agent to use
---

You have a folder of runbooks, an architecture spec, a wiki export. You want the agent to answer from them instead of guessing, and to tell you which document an answer came from. That is the knowledge library: a local index of your own documents that the agent searches by meaning and cites back to source.

The first thing to get straight is what it is not. People reach for the knowledge library when they mean memory, and the two solve opposite problems. Memory is the small, distilled picture injected into every prompt — lossy by design, it dedups and paraphrases. The knowledge library holds the verbatim, cited detail memory can only approximate, and the agent pulls it on demand through one tool. The [comparison table](#knowledge-library-vs-memory-vs-skills-vs-steering) below draws the full line.

## What it stores, and how

Everything lives in one SQLite database at `~/.kiro/crew/workspace/knowledge/knowledge.db`. Three layers sit inside it:

- **Sources** — where content comes from: a folder you registered (`local_folder`), an uploaded file, the saved-artifacts source, the agent's "Auto-added" source, a fetched web page. A source is the unit you add, pause, sync and remove.
- **Documents and items** — a source holds documents; each document's text is split into overlapping **chunks** (the `HeadingAwareChunker` targets 800 words with 200 words of overlap). Chunks are the rows that get searched, so a match can be quoted in the context it appeared in.
- **A graph** — entity and relation rows extracted from each chunk by a bounded LLM worker pool, linking passages that mention the same thing across different files.

### Hybrid retrieval

Search is not one index. `HybridRetriever` runs three legs and fuses them with reciprocal-rank fusion (RRF):

1. **Keyword** — FTS5 full-text over the chunks. Always available; no model behind it.
2. **Graph** — traversal over the extracted entities, which is what connects a multi-hop answer spread across two documents.
3. **Vector** — semantic similarity from embeddings, weighted `2.0` in the fusion so a meaning match outranks an incidental keyword hit.

This degrades in a defined order rather than failing. When the embedding model is still downloading or unloaded, the vector leg drops and you get keyword-and-graph results; the agent's answer notes that only keyword results were used. Embeddings run in-process against a vendored runtime (the same `qwen3-embedding:0.6b` model the memory subsystem uses), so nothing leaves the machine and there is no inference endpoint to stand up.

### Namespaces

Each item can carry a `namespace` label (up to 64 characters). It is an organisational filter you can scope a search to — not a security boundary. Graph traversal still crosses namespaces to surface connections.

## How content gets in

| Way in | What it is | Fetches anything? |
|---|---|---|
| Upload | Add Source → a file or archive you upload | No |
| Synced folder | Add Source → a local folder; `FolderWatcher` scans it recursively and re-ingests on change | No |
| Web page | Add Source → Web Page → paste an `https://` link | Yes — the gateway fetches it once itself |
| Saved artifacts | Opt-in: `knowledge.auto_ingest_artifacts` | No |
| Agent-added documents | Opt-in: `knowledge.auto_add_documents` | No — the agent fetches with its own tools |

A folder scan only ingests files whose extension is in the reader's `SUPPORTED` set — Markdown, text, the common source-code extensions, `.pdf`, `.docx`, `.html`, AsciiDoc, CSV, JSON/JSONL, YAML and more. `.pptx` is deliberately excluded. Directories like `.git`, `node_modules`, `__pycache__`, `.venv`, `dist` and `build` are never walked, and a source caps at 5000 files, newest first.

Two inputs are gated and off by default:

- `knowledge.auto_ingest_artifacts` (default `false`) indexes saved artifacts as a searchable "Artifacts" source and keeps them in sync. Enabling it backfills the artifacts you already have. The eligible kinds are `knowledge.auto_ingest_artifact_kinds` (default `["markdown", "text", "html", "json"]` — `widget` is UI, not a document, and `svg` has no reader).
- `knowledge.auto_add_documents` (default `false`) lets the agent add documents it reads while working, as one aggregate "Auto-added" source. The agent fetches the content with its own tools under your approval; the gateway fetches nothing on this path. This is the setting behind the `knowledge_add_document` tool — with it off, that tool refuses and names the key.

Web-page sources are the one path where the gateway itself fetches. It only fetches hosts listed in `knowledge.doc_ingest_hosts`, which is **empty by default**, so nothing is fetched until you add a host:

```bash
kirocrew config set knowledge.doc_ingest_hosts '["example.com"]'
```

The match is exact (`https://` only, default port, no subdomain matching), the host must resolve to public addresses, and a redirect to another host is refused. `example.com` does not cover `docs.example.com`.

## How the agent uses it

The agent reaches the library through four MCP tools, never through per-turn context injection:

| Tool | Does |
|---|---|
| `local_knowledge_search` | The main one. `query` plus an optional `limit` (1–5, default 3), `source_id` and `namespace`. Returns ranked, cited passages. |
| `knowledge_list_sources` | Lists the sources, so the agent can find a `source_id` to scope to. |
| `knowledge_add_document` | Adds a document the agent read (gated by `auto_add_documents`). |
| `knowledge_dedup` | Collapses cross-source duplicates; dry-run by default. |

The agent does not search on every message, and that is intentional. `local_knowledge_search` is meant for an explicit signal — "what do we know about X", "check the knowledge base", a named document, "according to our runbooks" — not for general coding questions it can answer from the open files. Scoping by `source_id` narrows a search to one source; `namespace` narrows it to one organisational label. Both are relevance filters applied before the keyword/vector seeding; graph traversal can still surface a connected item outside the scope.

Each result carries a citation naming where it came from: `**Source:**` for a document, `**File:**` for a file inside a synced folder, `**Artifact:**` for a saved artifact, `**Link:**` for a URL. Below the retriever's score floor (`0.012`) nothing is returned, so an absent answer comes back as "No relevant knowledge found." rather than a false near-match.

## Deduplication

Two gates keep duplicates out. The per-write gate catches byte-identical documents immediately — so uploading the same file directly and through a folder sync does not double every hit. A fuller cross-source pass runs every Nth watcher sweep (`knowledge.dedup_every_n_sweeps`, default 12) to collapse near-identical passages that are not byte-identical. You can also run it on demand:

```bash
kirocrew knowledge dedup
```

Without `--apply` this is a dry run: it opens the database read-only, lists the collapses it would make, and writes nothing. Pass `--apply` to perform the deletes. (This is the only `kirocrew knowledge` CLI verb; everything else is on the dashboard Knowledge tab.)

## Limits and costs

- **Per-file size cap** — `knowledge.max_ingest_file_mb` (default `100.0`); oversized files are skipped. `0` disables it.
- **Ingestion pacing** — a folder you add ingests `knowledge.folder_ingest_chunk_budget` chunks per sweep (default 300); nothing is dropped, the rest continue on later sweeps. `knowledge.sweep_chunk_budget` (default 500) caps chunks across all sources per sweep.
- **Extraction** — entity extraction runs a pool of `knowledge.extraction_pool_size` LLM workers (default 3) at reasoning effort `knowledge.extraction_effort` (default `high`). This spends model tokens, because extraction is an LLM turn per chunk.
- **Embedding** — in-process, no server; `knowledge.embed_rate_limit` caps generations per minute (default 120). The model needs ~610 MB on disk and ~700 MB RAM when loaded, shared with memory, and downloads in the background on first gateway start.

## Knowledge library vs memory vs skills vs steering

These four feed the agent different things at different times. Confusing them is the usual cause of "why didn't it use my docs".

| | What it holds | Who writes it | When it is read |
|---|---|---|---|
| **Knowledge library** | Verbatim, cited detail from your documents | You (add sources); the agent (if `auto_add_documents` on) | On demand, only via `local_knowledge_search` |
| **Memory** | Small distilled facts, preferences, project context, lessons | The consolidator, and the agent via `learn_add` | Injected into prompts automatically (per the memory config toggles) |
| **Skills** | Markdown procedures for a tool or task | You, or installed from the registry | Loaded when the task matches, by the agent |
| **Steering** | Standing instructions for a project (`.kiro/steering/**/*.md`, `AGENTS.md`) | You | Loaded as always-on context by the harness |

The short version: memory shapes every answer and is lossy; the knowledge library is pulled only when asked and is exact; skills tell it *how* to do a thing; steering tells it the rules of *this* project. See [Make it remember](../recipes/make-it-remember.md) for the memory side of this line.

## Steps

Add a folder of docs, confirm it indexed, and ask a question that uses it.

### 1. Add the folder as a source

On the dashboard, open the **Knowledge** tab, choose **Add Source**, and pick the folder. Confirming the source starts the first scan. The watcher ingests the first paced batch immediately (newest files first) and the rest on later sweeps, so a large folder fills in over a few passes rather than all at once.

### 2. Check it was indexed

Watch the source row on the Knowledge tab: its item count climbs as chunks land, and each file shows its state. Ask the agent what it can see:

```prompt
List my knowledge sources and how many items each has.
```

It calls `knowledge_list_sources` and reports the sources with their counts. A source sitting at zero items usually means the files were an unsupported extension or over the size cap.

### 3. Ask a question that uses it

Ask something whose answer lives in those docs, and make the signal explicit so the agent searches instead of guessing:

```prompt
According to my runbooks, what's the rollback procedure for the payments service?
```

It calls `local_knowledge_search`, pulls the ranked passages, and answers from them.

### 4. Confirm the answer cites the source

The answer should name where each passage came from — a `**File:**` citation for a file inside your synced folder. If the agent answered without a citation, it probably did not search; re-ask with a clearer signal ("check the knowledge base") or point it at the source.

## Verify

- `knowledge_list_sources` shows your folder with a non-zero item count.
- A question whose answer is only in those docs comes back with a citation naming the file.
- Ask something the docs do not cover. You should get "No relevant knowledge found." rather than a confident wrong answer.

## Gotchas

- **Stale content.** The library is a point-in-time index of the files as scanned. A synced folder re-ingests on change, but an uploaded file does not update itself — re-upload it, or sync the source, after the underlying document changes.
- **Duplicates inflate results.** Adding the same document both directly and through a folder is the common case. The per-write gate catches byte-identical copies; run `kirocrew knowledge dedup` (dry run first) to collapse the near-identical ones, or let the periodic sweep do it.
- **Do not put code, secrets or generated files in it.** The library is for durable prose that explains intent — specs, runbooks, design docs, wiki pages. Source code belongs in the project, not re-indexed as prose; generated and machine-readable files add noise that makes every search worse; and anything with a credential in it should never be ingested, because the chunks are searchable and quoted back verbatim. A polluted library degrades recall for everything else in it.
- **It only searches when asked.** The agent will not consult the library for a general coding question it can answer from the open files. If you want it grounded in your docs, say so — name the source, or use words like "according to our docs" / "check the knowledge base".
- **Web pages need an allow-listed host first.** A Web Page source is refused until its host is in `knowledge.doc_ingest_hosts`, and the match is exact with no subdomain wildcard.
