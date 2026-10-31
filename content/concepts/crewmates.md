---
title: "Crewmates: agents with their own job"
description: When and why to create a crewmate, what it is made of, and how memory stays isolated.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [crewmates, memory, routing, agents]
updated: 2026-10-30
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
  - You have used the default agent for real work
---

The default agent carries everything you teach it in one shared memory, works in your default workspace, and runs one standing conversation. That is the right setup until two jobs start fighting over it. You tell it your incident runbook and later its notes about a side project leak into an on-call answer. You want a build watcher that wakes on its own schedule without cluttering your main chat. You want one assistant that only ever reasons about Terraform and never about the frontend.

A crewmate is a named assistant with its own memory store, so what it learns stays with it. The repo calls the same object a **mate**, a **crew member**, or a **crew** depending on where you look - the dashboard page is **Mates**, the config calls them crews, and the routing tools say member. They are one entry in the `agents` map of `~/.kiro/crew/config.json`.

## What a crewmate is made of

Creating a crewmate allocates one new thing - a memory store - and binds four existing things it points at: a workspace, an agent template, a default model, and a name. Everything else is a setting on top of those.

| Part | What it controls | Where you set it |
|---|---|---|
| Name | Its identity everywhere: the roster row, its chat thread, `crew=` on a delegation | **New mate** form (Mates page), or `kirocrew agent create --name` |
| Agent template (`kiro_agent`) | The spec it boots from: system prompt, tools, MCP servers, permissions | **Built from** in the create form; `--kiro-agent`; both the crew manager and the API refuse a crewmate without one |
| Memory store | The SQLite database holding its facts, rules, experiences and briefing | Allocated at creation; cannot be repointed or shared later |
| Workspace | The folder it reads and writes | **Advanced settings**; `--workspace`; defaults to your `default_workspace` |
| Model | Default model for its sessions | **Model** control on the Profile card; `--model` (`--model ""` clears it) |
| Reasoning effort | How long its sessions think before answering | Crew editor; ignored by models that do not reason |
| Triggers | Free-text phrases saying when work should route to it | **Advanced settings** / crew editor; empty means never auto-selected |
| Tools / approvals / MCP / skills | What its sessions and its worker can call, and what runs without asking | **Permissions** on the Profile card, or the crew editor |
| Appearance | Ghost-face traits or an uploaded picture, plus a session color | **Edit avatar** on the create form; the crew editor for packs and pictures |
| Description | One line shown on the roster | Crew editor, or the crewmate writes its own with `update_self` |

A per-session model or reasoning-effort pick wins over the crewmate's defaults, and the crewmate's defaults win over the global ones. The name is free-form display text (`Dr. Eggbot` is a valid name); the server derives a stable member id and a path-safe slug from it, and those stay fixed when you rename.

## How work reaches a crewmate

There are four ways, and they are not interchangeable.

**Its own chat.** Opening a crewmate on the Mates page opens one durable, pinned thread - the same thread every time, with its history, surviving gateway restarts. This is the point of a crewmate over an ordinary session: the context you built with it is where you left it. These threads are deliberately kept out of the Sessions list; the Mates page is their only home.

**Routing by triggers.** An orchestrating agent reads the roster and decides where a task belongs. Triggers are comma-separated phrases; a phrase scores as the fraction of its own words present in the task text, and a crewmate scores as its best phrase. Anything below a 0.7 overlap is not a match. A phrase prefixed with `!` is a negative - if all its words appear, that crewmate is excluded. A phrase prefixed with `=` must match case exactly (`=Excel` fires on "Excel", not "excel"). The same matcher picks skills, so "this phrasing matches" means one thing across the product.

**A parent agent spawning a run.** Delegation only moves work onto a crewmate's memory and template when you pass `crew=`:

```text
spawn_run(crew="oncall")      # runs on oncall's memory store + template
spawn_run(agent="oncall")     # runs oncall's TEMPLATE on the CALLER's memory
```

This distinction is the one that bites. `agent=` names an installed template and nothing else; from a default-crew orchestrator it runs on the default store, which is how one crewmate's work ends up in another's notes. `crew=` is the only argument that selects the memory store.

**Cron jobs owned by a member.** A scheduled job can be bound to a crewmate so it runs on that crewmate's memory. Bind it with `member_id` when you create the cron, or hand an existing job over with `kirocrew cron adopt <id> --session-of <slot>`. A member-bound cron is refused the session-control calls (`open_session`, `send_to_session`), because those belong to a dashboard slot, not a member thread.

## Memory isolation

Each crewmate reads and writes only its own store. What you teach one stays with it; the default agent will not know, and neither will any sibling.

- A crewmate with a V2 store receives its identity, permanent rules, current briefing, manual anchors and admitted project guides at the start of a conversation. The snapshot refreshes once when something changes, and is restored after compaction or a new provider conversation.
- The store lives at `<data-home>/memory_stores/<name>/`; the global default lives at `<data-home>/workspace/`. A crewmate's stable identity selects its database, so renaming it or changing its provider does not move its learned memory.
- The store cannot be repointed or shared after creation. `kirocrew agent update --memory-store` refuses it, because a crewmate's memory is its identity.
- Two crewmates pointed at one store (an older crewmate cloned into a new one) can read each other's files and memory. The crew editor says so on the field when that is the case.
- `route_crew` returns a crewmate whose memory binding cannot be resolved under `unavailable` with a reason. Report that and handle the task on the default crew - running it on the default store instead is the one substitution never to make.

Routing records intent; it changes nothing until you spawn. When `route_crew` returns nothing in either `matches` or `unavailable`, no crewmate claims the task - handle it on the default crew rather than picking the least-bad row.

## Goals, milestones and check-ins

A crewmate's **Goals** tab holds what it works toward, and this is agent-managed through cards you press.

- **Goals** - as many as you like, each one paragraph. A new goal starts as a conversation: the crewmate asks what matters, writes the goal down, and proposes it on a card (`set_goal`). Nothing is stored until you press it.
- **Milestones** - key results that show how far it is from its goals. The crewmate works them out, links each to its goals, and proposes them on one card (`set_key_results`). After you confirm, it records readings itself with `key_result_progress`; a reading is a number or a short note.
- **Check-ins** - three switches, each off by default and only available once a goal is set, sharing one time of day:
  - **Daily Goal Reminder** - the crewmate takes fresh readings, then carries on with its next task.
  - **Weekly report** - on a weekday you pick.
  - **Monthly review** - on a day of the month you pick; when it finds the goal or its key results no longer fit the work, it proposes new ones on a card.

Weekly reports and monthly reviews are saved under `Crewmates/<name>/Reports` in Artifacts, with a notification linking each. The goal record lives at `member-records/member-goals/<slug>.json`, apart from the crewmate's rules and with the same protection: nothing the crewmate runs can read or change that folder, so it only ever changes a goal through a card you press.

## Capability changes and how you approve them

A crewmate cannot grant itself tools. In its own chat it can ask for a change, and each ask is a card with a button - nothing changes until you press it.

- `request_capabilities` - add or remove tools, MCP servers or skills. The card says where each server comes from and exactly which of its tools would run without asking. Pressing it adds the server or skill to this crewmate's own settings only, not to your global MCP config.
- `set_model` - a different model or reasoning effort.
- `set_approval_mode` - a different approval mode for that chat.

Asking for tools this way is a preview, off by default per crewmate. While it is off, the crewmate asks you once, on a card marked **Preview**, whether it may ask at all. Turning that on only lets it ask; each tool still needs its own approval card. Its workspace, memory store and template are never the crewmate's to ask for - those stay yours to set in the editor.

## When a crewmate is the wrong tool

A crewmate is a standing identity with its own memory and thread. That is overhead you do not want for one-off or stateless work.

- **A repeated action with no memory of its own is a cron job.** "Check pipeline health every 30 minutes" is a `persistent_session=false`, `minimal_context=true` script or command cron, not a crewmate.
- **A reusable procedure is a skill.** If what you want is "always prepare a PR this way", write a skill and map it to an agent. A skill is markdown on disk; it needs no memory store, no thread and no roster row.
- **A one-off parallel fan-out is a subagent.** "Review these three packages at once" is `spawn_run(tasks=[...])`. Subagents are disposable; a crewmate is for work you come back to.

Reach for a crewmate when the job needs its own accumulating memory, its own workspace or tools, or its own standing conversation you return to over days.

## Steps

Create a build watcher: a crewmate that owns one repo, watches CI, and keeps its notes out of your main memory.

### 1. Open the Mates page

In the dashboard, open **Mates** (the left-rail row under Sessions, route `/members`). The page is a preview, so it shows only after you turn on **Settings → Developer → Mates**. Without it, **Customize → Mates** makes mates with the same form. On an empty roster press **Create your first mate**; otherwise use **New mate** from the roster header's **Add…** menu.

### 2. Name it and open Advanced settings

Enter a name - `build-watcher`. Press **Edit avatar** if you want a distinct face and color so its sessions are easy to spot. Then unfold **Advanced settings** to set the rest in the same card.

### 3. Pick its workspace and set triggers

Under Advanced, set **Built from** to a template (leave it as `kirocrew` unless you have a reason). The **workspace** is a named KiroCrew workspace: the folder that holds its notes and files. It is not your repo. Keep the default unless you run a separate workspace for this kind of work; you point it at the repo in its chat in step 5. Then give it **triggers** that route build work to it:

```text
ci, build, pipeline, failing test, broken build
```

Keep phrases specific. A single generic word like `build` will match loosely; a two-word phrase like `failing test` has to match more completely to score.

### 4. Create it from the CLI instead (optional)

The whole thing is one command:

```bash
kirocrew agent create --name build-watcher --kiro-agent kirocrew --workspace default
```

Check the pin with `kirocrew agent list`. To change the model later:

```bash
kirocrew agent update build-watcher --model <model-id>
kirocrew agent update build-watcher --model ""   # clear it, inherit again
```

### 5. Give it a goal and a check-in

Press **Create**. The crewmate opens its chat and asks what you want it to do. Tell it in plain words, with the repo path: "watch CI on the repo at /home/me/projects/my-app and tell me when main goes red". It writes the goal down and puts it on a card (`set_goal`); press the card. Then it suggests check-ins on its **Goals** tab. Turn on **Daily Goal Reminder** if you want a daily readout; leave the weekly and monthly ones off unless you want saved reports.

### 6. Send work to it

From an orchestrating chat, delegate by crew so the run uses the crewmate's memory:

```prompt
Spawn build-watcher to triage the failing CI run on my-app and summarize the root cause.
```

Or just open its own thread on the Mates page and talk to it directly.

## Verify

- On the Mates page, `build-watcher` has its own row and opening it shows one standing thread, not a fresh chat each time.
- Ask it something in its chat, then ask the default agent the same thing in a plain session. The default agent should not know what you told the crewmate - that confirms the stores are separate.
- `kirocrew agent list` shows `build-watcher` with its model pin (or `(inherit)`).
- A delegated `crew="build-watcher"` run answers from what you told the crewmate, not from the default agent's notes.

## Gotchas

- **`agent=` is not `crew=`.** `spawn_run(agent="build-watcher")` runs the template on the caller's memory, silently. Only `crew=` moves the run onto the crewmate's store. This is the most common way one crewmate's work lands in the wrong memory.
- **No triggers means no auto-routing.** A crewmate with empty triggers is omitted from the roster and never ranked. You can still reach it by name with `crew=`; triggers only steer automatic selection, and there is no separate "accept delegated tasks" switch.
- **The memory store is permanent.** You cannot repoint or share a crewmate's store after creation. If you need two crewmates to share memory, clone one into the other at creation; you cannot merge them later.
- **Deleting keeps the data.** **Delete mate** unbinds the crewmate from new sessions but keeps its workspace, memory store and past transcripts. A session still bound to a deleted template falls back to the default agent spec and keeps running with the default prompt and tools - so repoint bindings before you remove a template file.
- **Slack picks templates, not crewmates.** Slack's per-thread `!ta <name>` resolves against spec files in `~/.kiro/agents/`, not your roster, so it selects a template. A crewmate whose name has no spec file comes back as `Unknown agent`.
- **A capability card only lets the crewmate ask.** Enabling the tool-request preview does not grant anything. Each tool still needs its own approval card, and the crewmate never gets its workspace, store or template that way.

For the memory model behind all this, see [make-it-remember.md](../recipes/make-it-remember.md). For the layer crewmates sit on, see [what-kirocrew-is.md](what-kirocrew-is.md).
