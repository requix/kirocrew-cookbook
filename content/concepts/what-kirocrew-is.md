---
title: What KiroCrew actually is
description: The mental model in one page. Harness, agent config, gateway, and the five words behind the dashboard.
category: Concepts
difficulty: beginner
time: 5 min
surfaces: [dashboard, cli]
tags: [concepts, gateway, harness]
updated: 2026-10-31
featured: false
---

You already know agents. You have used Kiro in your editor and on the CLI. So skip the pitch. Here is the one thing that matters:

**KiroCrew is not an agent. It is the layer around the agent.**

## The three layers

There are three things, stacked. People confuse them, and that is where the trouble starts.

| Layer | What it is | Example |
|---|---|---|
| The harness | The agent runtime. Runs the model, runs tools, holds one session. | `kiro-cli` |
| The agent config | A JSON file that says how the agent behaves: prompt, tools, MCP servers. | `~/.kiro/agents/kirocrew.json` |
| KiroCrew | The gateway. One process that wraps the harness and adds everything it lacks. | the `kirocrew` gateway |

`kiro-cli` on its own gives you one session in one terminal. That is it. No memory between sessions. No schedule. No second agent.

KiroCrew wraps that same harness and adds the missing parts:

- **Many sessions at once** — dashboard tabs, chat channels, cron jobs, subagents.
- **Memory** — it remembers across sessions. Preferences, projects, lessons.
- **Schedules** — cron jobs that run work while you sleep.
- **Subagents** — spin up helpers to do parts in parallel.
- **Learning** — it turns your corrections into rules for later.
- **A safety gate** — every tool call is checked before it runs.

The agent is the same. KiroCrew is what makes it a system.

## The picture

```flow
- box: You
- box: KiroCrew gateway
  note: One process. Memory, schedules, safety, tabs.
  accent: true
- box: "`kiro-cli`, the harness"
  note: It runs the model and the tools.
  via: ACP, a JSON-RPC pipe
- split:
    - - box: The model
    - - box: Tools
        note: bash, files, grep, MCP
```

One line to remember: **the gateway talks to the harness; the harness talks to the model.**

## Words you will see

These five words are the whole vocabulary. Learn them and the dashboard stops being confusing.

- **Gateway** — the KiroCrew process. Everything runs through it.
- **Session** — one conversation. A dashboard tab is a session. A cron run is a session.
- **Agent** — a config that sets the behavior. `kirocrew` is the default one; it is just another config.
- **Memory** — what carries between sessions. Not every session shares the same memory (see the memory recipe).
- **Harness** — the runtime under the agent. `kiro-cli` by default.

## Why the gateway, not just the CLI

Three reasons, plain:

1. **Work runs without you.** Cron jobs and subagents act with nobody typing.
2. **It gets better over time.** Corrections become lessons. A later session starts smarter.
3. **One safety line.** The gateway checks every tool call, and the agent cannot turn that check off.

That is the model. Everything in the recipes is one of these five words doing its job.

The rest of the vocabulary, from projects and steering to mates and apps, is on one diagram in [How the pieces fit](how-it-fits.md).
