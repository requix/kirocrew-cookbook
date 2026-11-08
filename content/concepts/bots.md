---
title: "Bots: agents with their own job"
description: When and why to create a bot, what it is made of, and how memory stays isolated.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [bots, crewmates, memory, routing, agents]
updated: 2026-11-08
featured: true
prerequisites:
  - Kiro Crew running (see Your first hour)
  - You have used the default agent for real work
---

The default agent carries everything you teach it in one shared memory, works in your default workspace, and runs one standing conversation. That works until two jobs start fighting over it. You tell it your incident runbook and later its notes about a side project leak into an on-call answer. You want a build watcher that wakes on its own schedule without cluttering your main chat. You want one assistant that only reasons about Terraform and never about the frontend.

A bot is a named assistant with its own memory store, so what it learns stays with it. The codebase still calls this object a **mate**, a **crew member**, or a **crewmate** in places — the config key is `crews`, and the routing tools say `member`. The dashboard and the product call them **Bots**. They are one entry in the `agents` map of `~/.kiro/crew/config.json`.

## What a bot is made of

Creating a bot allocates one new thing — a memory store — and binds four existing things it points at: a workspace, an agent template, a default model, and a name.

| Part | What it controls | Where you set it |
|---|---|---|
| Name | Its identity everywhere: the roster row, its chat thread, `crew=` on a delegation | **New Bot** form (Bots page), or `kirocrew agent create --name` |
| Agent template (`kiro_agent`) | The spec it boots from: system prompt, tools, MCP servers, permissions | **Built from** in the create form; `--kiro-agent` |
| Memory store | The SQLite database holding its facts, rules, experiences and briefing | Allocated at creation; cannot be repointed or shared later |
| Workspace | The folder it reads and writes | **Advanced settings**; `--workspace` |
| Model | Default model for its sessions | **Model** control on the Profile card; `--model` |

A per-session model or reasoning-effort pick wins over the bot's defaults, and the bot's defaults win over the global ones.

## The conductor/worker split

A bot's chat runs on its **conductor** — a special agent that only plans and dispatches. It never does the heavy work itself. When you ask a bot to review code, research something, or fix a bug, the conductor hands that task to a **worker** session. Workers appear in the sidebar, so you can see what is running and take over if you need to.

This split matters for three reasons:

1. **The bot stays responsive.** While a worker spends twenty minutes on a code review, you can still talk to the conductor and ask questions or redirect.
2. **Parallel work is natural.** The conductor can spin up several workers at once — one per task — and bring results back to one thread.
3. **Context stays clean.** The conductor carries your conversation and your direction. Workers carry the task context. They do not mix.

The conductor has no `spawn_run` or subagent tools. It hands work to worker sessions using `session_create` and `session_send`, then reads results with `session_read_message`. That is the only delegation path a bot has.

## How work reaches a bot

There are four ways, and they are not interchangeable.

**Its own chat.** Opening a bot on the Bots page opens one durable, pinned thread — the same thread every time, with its history, surviving gateway restarts. This is the point of a bot over an ordinary session: the context you built with it is where you left it. These threads are deliberately kept out of the Sessions list; the Bots page is their only home.

**Routing by triggers.** An orchestrating agent reads the roster and decides where a task belongs. Triggers are comma-separated phrases; a phrase scores as the fraction of its own words present in the task text, and a bot scores as its best phrase. Anything below a 0.7 overlap is not a match. A phrase prefixed with `!` is a negative — if all its words appear, that bot is excluded. A phrase prefixed with `=` must match case exactly (`=Excel` fires on "Excel", not "excel").

**A parent agent spawning a run.** Delegation only moves work onto a bot's memory and template when you pass `crew=`:

```text
spawn_run(crew="oncall")      # runs on oncall's memory store + template
spawn_run(agent="oncall")     # runs oncall's TEMPLATE on the CALLER's memory
```

This distinction bites people. `agent=` names an installed template and nothing else; from a default-crew orchestrator it runs on the default store, which is how one bot's work ends up in another's notes. `crew=` is the only argument that selects the memory store.

**Cron jobs owned by a bot.** A scheduled job can be bound to a bot so it runs on that bot's memory. Bind it with `member_id` when you create the cron.

## Memory isolation

Each bot reads and writes only its own store. What you teach one stays with it; the default agent does not know, and neither do its siblings.

- A bot with a V2 store receives its identity, permanent rules, current briefing, manual anchors and admitted project guides at the start of a conversation. The snapshot refreshes once when something changes, and is restored after compaction or a new provider conversation.
- The store lives at `<data-home>/memory_stores/<name>/`. A bot's stable identity selects its database, so renaming it or changing its provider does not move its learned memory.
- The store cannot be repointed or shared after creation.

Routing records intent; it changes nothing until you spawn. When `route_crew` returns nothing in either `matches` or `unavailable`, no bot claims the task — handle it on the default crew rather than picking the least-bad row.

## Goals, milestones and check-ins

A bot's **Goals** tab holds what it works toward. This is agent-managed through cards you press.

- **Goals** — as many as you like, each one paragraph. A new goal starts as a conversation: the bot asks what matters, writes the goal down, and proposes it on a card (`set_goal`). Nothing is stored until you press it.
- **Milestones** — key results that show how far the bot is from its goals. The bot works them out, links each to its goals, and proposes them on one card (`set_key_results`). After you confirm, it records readings itself with `key_result_progress`; a reading is a number or a short note.
- **Check-ins** — four switches, each off by default:
  - **Daily Goal Reminder** — the bot takes fresh readings, then carries on with its next task.
  - **Weekly report** — on a weekday you pick.
  - **Monthly review** — on a day of the month you pick; when the bot finds a goal or its key results no longer fit the work, it proposes new ones on a card.
  - **Heartbeat** — the bot wakes every 30 minutes, 1 hour, 2 hours, or 4 hours (you pick) to move work forward on its own. It only writes in the chat when something needs your attention. Otherwise it works quietly and records what it did on its Dashboard tab.

Weekly reports and monthly reviews are saved under `Crewmates/<name>/Reports` in Artifacts. The goal record lives at `member-records/member-goals/<slug>.json`, apart from the bot's rules and with the same protection: nothing the bot runs can read or change that folder, so it only ever changes a goal through a card you press.

## The dashboard tab

A bot can maintain its own **Dashboard tab** — a custom page that shows where its work stands without you opening any session transcript. The bot proposes a page once, after its milestones are confirmed, with `offer_dashboard_page`. You press the card; the bot writes the page.

What goes on the dashboard:

- What the bot is doing — every workstream it runs, every task inside each one
- What it cost — credits per task, per workstream, over time
- What came out — accepted, rejected, still in flight
- What it needs from you — blocked tasks, open questions, and the lines the bot itself wants you to act on

The bot updates this page using `dashboard_write` and `dashboard_save`. The chat stays focused on findings, handoffs, and questions that need your attention. When you want to inspect activities, the related sessions are available to review.

## Capability changes and how you approve them

A bot cannot grant itself tools. In its own chat it can ask for a change, and each ask is a card with a button — nothing changes until you press it.

- `request_capabilities` — add or remove tools, MCP servers or skills. The card says where each server comes from and exactly which of its tools would run without asking. Pressing it adds the server or skill to this bot's own settings only, not to your global MCP config.
- `set_model` — a different model or reasoning effort.
- `set_approval_mode` — a different approval mode for that chat.

Asking for tools this way is a preview, off by default per bot. While it is off, the bot asks you once, on a card marked **Preview**, whether it may ask at all. Turning that on only lets it ask; each tool still needs its own approval card.

## When a bot is the wrong tool

A bot is a standing identity with its own memory and thread. That is overhead you do not want for one-off or stateless work.

| What you want | Reach for |
|---|---|
| A repeated action with no memory of its own | A cron job — `persistent_session=false`, `minimal_context=true` |
| A reusable procedure | A skill — markdown on disk, no memory store, no roster row |
| A one-off parallel fan-out | A subagent — `spawn_run(tasks=[...])`, disposable |
| Memory isolation and a standing thread | A bot |

## Steps: create a build watcher

A bot that owns one repo, watches CI, and keeps its notes out of your main memory.

### 1. Open the Bots page

In the dashboard, open **Bots** (the left-rail row under Sessions, route `/members`). On an empty roster press **Create your first Bot**; otherwise use **New Bot** from the roster header's **Add…** menu.

### 2. Name it and open Advanced settings

Enter a name — `build-watcher`. Press **Edit avatar** if you want a distinct face and color so its sessions are easy to spot. Then unfold **Advanced settings** to set the rest in the same card.

### 3. Pick its workspace and set triggers

Under Advanced, set **Built from** to a template (leave it as `kirocrew` unless you have a reason). The **workspace** is a named Kiro Crew workspace: the folder that holds its notes and files. Then give it **triggers** that route build work to it:

```text
ci, build, pipeline, failing test, broken build
```

Keep phrases specific. A single generic word like `build` will match loosely; a two-word phrase like `failing test` has to match more completely to score.

### 4. Create it from the CLI (optional)

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

Press **Create**. The bot opens its chat and asks what you want it to do. Tell it in plain words, with the repo path: "watch CI on the repo at /home/me/projects/my-app and tell me when main goes red". It writes the goal down and puts it on a card (`set_goal`); press the card. Then it suggests check-ins on its **Goals** tab. Turn on **Daily Goal Reminder** if you want a daily readout; turn on **Heartbeat** if you want it to proactively check and fix things between your messages.

### 6. Send work to it

From an orchestrating chat, delegate by crew so the run uses the bot's memory:

```prompt
Spawn build-watcher to triage the failing CI run on my-app and summarize the root cause.
```

Or open its own thread on the Bots page and talk to it directly.

## Verify

- On the Bots page, `build-watcher` has its own row and opening it shows one standing thread, not a fresh chat each time.
- Ask it something in its chat, then ask the default agent the same thing in a plain session. The default agent should not know what you told the bot — that confirms the stores are separate.
- `kirocrew agent list` shows `build-watcher` with its model pin (or `(inherit)`).
- A delegated `crew="build-watcher"` run answers from what you told the bot, not from the default agent's notes.

## Gotchas

- **`agent=` is not `crew=`.** `spawn_run(agent="build-watcher")` runs the template on the caller's memory, silently. Only `crew=` moves the run onto the bot's store. This is the most common way one bot's work lands in the wrong memory.
- **No triggers means no auto-routing.** A bot with empty triggers is omitted from the roster and never ranked. You can still reach it by name with `crew=`; triggers only steer automatic selection.
- **The memory store is permanent.** You cannot repoint or share a bot's store after creation.
- **Deleting keeps the data.** **Delete mate** unbinds the bot from new sessions but keeps its workspace, memory store and past transcripts.
- **A capability card only lets the bot ask.** Enabling the tool-request preview does not grant anything. Each tool still needs its own approval card, and the bot never gets its workspace, store or template that way.

For the memory model behind all this, see [make-it-remember](../recipes/make-it-remember.md). For the layer bots sit on, see [what-kirocrew-is](what-kirocrew-is.md).
