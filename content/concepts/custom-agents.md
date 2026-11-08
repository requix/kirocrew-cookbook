---
title: "Custom agents: shaping the agent that answers you"
description: When and why to write your own agent spec, what goes in it, and how Kiro Crew layers memory and rules on top.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [agents, custom-agents, prompt, model, spec]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew running (see Your first hour)
  - You have used the default agent for real work
---

Every Kiro Crew session starts with the `kirocrew` agent: a managed prompt, every MCP tool, and the memory store you share across sessions. That is a sensible default until you want something more focused — a code reviewer that only reads files, a background worker with a stripped-down prompt, or a translator that always answers in one specific style. A custom agent is a JSON spec file you write; it sets the prompt, narrows the tools, and picks a default model. Kiro Crew's memory, learned corrections, and reply rules still ride every session on top of your spec unless you explicitly turn them off.

If what you actually want is memory isolation — a separate store that stays out of your main chat — that is a [Mate](crewmates.md), not a custom agent. A Mate uses a spec too, but it gets its own memory and a standing thread. A custom agent shapes the session; a Mate shapes the identity.

## What a custom agent is made of

A custom agent is a JSON file at `~/.kiro/agents/<name>.json`. Kiro Crew picks up every file there and lists it in the agent picker under the composer. A file at `<project>/.kiro/agents/<name>.json` is also listed when that project is set as the chat's folder.

| Field | What it controls |
|---|---|
| `prompt` | The agent's system prompt; inline text or a path to a `.md` file; appended to every turn as the `[AGENT SYSTEM PROMPT]` block on every harness |
| `model` | The preferred model for this agent's sessions; wins over the global default but a per-session pick still overrides it |
| `mcpServers` | MCP servers this agent mounts; Kiro Crew's control-plane servers are always added beside yours |
| `tools` | Allowlist of `@server/tool` refs; an empty list (`[]`) mounts nothing from the MCP array |
| `disabledTools` | Block specific tools by `@server/tool` while keeping the rest of their server mounted |
| `includeCrewContext` | Kiro Crew-specific; `false` drops the dashboard reply rules and tool reminders from every turn |
| `name` | The display name in the agent picker; defaults to the filename without the extension |

A minimal spec needs only a prompt. Everything else is optional.

```json
{
  "prompt": "You review code. Name the file and line. State the class of problem. Suggest the fix in one sentence."
}
```

Save that as `~/.kiro/agents/reviewer.json`. It shows up immediately in the agent picker as `reviewer`.

## JSON vs Markdown

An agent can be JSON (`<name>.json`) or a Markdown file (`<name>.md` with YAML frontmatter and a prompt body). Both live in the same directory, and both show in the picker.

On the **KAS** harness (the default), both forms work. On the **kiro-cli harness** (`acp_backend="kiro"`), kiro-cli reads JSON only; a Markdown-only agent fails at session start with an error naming the file. If you share specs with others or run both harnesses, write JSON.

When a `.json` and a `.md` of the same name exist side by side, the JSON wins and the Markdown is silently dropped — the gateway logs which file was shadowed. Keep one file per name.

## What Kiro Crew adds to every session

Your spec's prompt arrives as the `[AGENT SYSTEM PROMPT]` block in every turn, on every harness. That is a separate injection from everything else Kiro Crew adds: the session's memory and learned corrections, and — for dashboard sessions — the reply rules that control formatting and tool reminders.

Setting `"includeCrewContext": false` in your spec removes the reply rules and reminders. Memory and learned corrections are not affected; those belong to the session, not the spec. Use `includeCrewContext: false` when you need a clean prompt surface for a background worker or a specialized agent you are testing:

```json
{
  "prompt": "You are a strict JSON validator. Output only valid JSON. No prose.",
  "includeCrewContext": false
}
```

Some formatting guidance still arrives because parts of it are tied to the harness, not the spec, but removing `includeCrewContext` cuts most of the reply-rules block.

If you want a session with no Kiro Crew memory at all, that requires a Mate with its own store, or a `spawn_run` call with `include_memory=false`. A spec alone cannot do it.

## When a custom agent is the right tool

| You want | Reach for |
|---|---|
| A different prompt for one kind of work | Custom agent |
| A narrower or different MCP tool surface | Custom agent |
| A specific default model for this kind of session | Custom agent |
| Memory that stays separate from your main chat | [Mate](crewmates.md) |
| A standing thread you return to over days | [Mate](crewmates.md) |
| A rule that applies to all agents automatically | [Steering file](../start/bring-your-kiro-setup.md#steering) |
| A reusable procedure or checklist | Skill |
| A one-off parallel task with no standing identity | Subagent |

Custom agents and Mates compose. You can bind a Mate to a custom agent spec with `--kiro-agent <name>` so every session on that Mate boots from your prompt and tool set. The Mate still gets its own memory store.

## MCP tools on a custom agent

By default, a custom agent inherits Kiro Crew's full MCP surface. The `tools` field narrows it to an explicit allowlist:

```json
{
  "tools": [
    "@kirocrew-core/read_file",
    "@kirocrew-core/grep_search",
    "@kirocrew-core/file_search"
  ]
}
```

`"tools": []` means mount nothing from the MCP array. This does not block the harness's own native tools (Bash and file access on the claude harness, for example), because those sit outside the array. On the claude and codex harnesses, native tools can still run even on a `tools: []` spec, so `tools: []` is a starting point, not a hard guarantee.

To block one specific tool rather than narrowing the whole list, use `disabledTools`:

```json
{
  "disabledTools": ["@kirocrew-core/file_send"]
}
```

One thing to know about `@server/tool` refs: on the kiro-cli harness, a ref like `@kirocrew-core/read_file` narrows to exactly that one tool. On every other harness — KAS, claude, and others — it mounts the whole server, because the tool inventory is not knowable without connecting. If you need a tight surface on KAS or claude, `disabledTools` is more reliable for blocking specific calls.

## Steps: write a focused code-review agent

### 1. Create the spec

```bash
cat > ~/.kiro/agents/reviewer.json << 'EOF'
{
  "name": "Reviewer",
  "prompt": "You review code changes. For each problem: name the file, name the line, state the class of bug or concern, and suggest the fix in one sentence. If there are no problems, say so in one line. Do not summarize what the code does.",
  "tools": [
    "@kirocrew-core/read_file",
    "@kirocrew-core/grep_search",
    "@kirocrew-core/file_search",
    "@kirocrew-core/list_directory"
  ]
}
EOF
```

No `includeCrewContext: false` here — the dashboard rules keep the output formatted cleanly. If this were a background worker, you would drop them.

### 2. Switch a chat to the new agent

Pick **Reviewer** in the agent chip under the composer, or type:

```prompt
/agent reviewer
```

A name that does not match any spec is refused rather than silently falling back, so a clean switch confirms the file loaded.

### 3. Review some code

```prompt
Review the changes in src/auth/login.py against the main branch.
```

### 4. Confirm the tool surface

```prompt
List the tools you have available.
```

You should see only the four read tools from the spec. If the full tool set appears, the spec did not load — check the filename and path.

### 5. Set it as the default (optional)

Open **Customize → Custom agents** and set **New sessions use** to `reviewer`. To undo:

```bash
kirocrew config set agent.default_agent ""
```

## Verify

- The agent chip shows your agent name, not `kirocrew`.
- `List the tools you have available` returns only what the spec declares.
- Memory works normally — the store belongs to the session, not the spec, so the agent answers from your full history.
- If the agent does not appear in the picker, check the gateway log. On the kiro-cli harness, an unknown JSON key causes a silent fallback to the default agent; the only sign is a line in stderr. `kirocrew config get agent.acp_backend` tells you which harness is active.

## Gotchas

- **On kiro-cli, an unknown key silently drops the whole spec.** kiro-cli validates with `deny_unknown_fields` and falls back to the default agent with only a line in stderr. Remove any key kiro-cli does not recognize, or use the KAS harness.
- **`includeMcpJson` is pinned `false` on every agent Kiro Crew manages.** Kiro Crew already merged your global `~/.kiro/settings/mcp.json` into the rendered agent file, so allowing the merge a second time would let a stale path shadow the live one. Add servers directly to your spec's own `mcpServers` instead.
- **`tools: []` does not block the harness's native tools.** It covers the MCP array only. On the claude and codex harnesses, the harness's own tools (Bash, file access) are outside that array and can still run.
- **Memory is the session's, not the spec's.** Switching to a custom agent does not reset or isolate memory. For a separate store, create a Mate built from your spec.
- **A Markdown agent will not run on the kiro-cli harness.** kiro-cli reads JSON only. A `.json` beside a `.md` of the same name shadows the Markdown; keep one file per name.
- **`includeCrewContext: false` removes the reply-rules block, not all Kiro Crew context.** Memory, briefing, and learned corrections still arrive. Use this flag for background workers or when you need a clean prompt surface, not when you want a blank slate.
- **`@server/tool` narrows to one tool on kiro-cli only.** On every other harness, it mounts the whole server. Use `disabledTools` when you need to block specific tools reliably across harnesses.

For the memory model behind sessions, see [make-it-remember.md](../recipes/make-it-remember.md). When memory isolation is the goal, see [crewmates.md](crewmates.md). For how existing agent files carry over from kiro-cli, see [bring-your-kiro-setup.md](../start/bring-your-kiro-setup.md).
