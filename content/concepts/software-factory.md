---
title: Kiro Crew as a software factory
description: What recent papers say an AI software factory needs, and which Kiro Crew feature plays each part.
category: Concepts
difficulty: intermediate
time: 20 min
surfaces: [dashboard, channels, cli]
tags: [software-factory, agentic-coding, conductor-mode, work-ledger, worktree, governance]
updated: 2026-11-20
featured: true
prerequisites:
  - Kiro Crew 0.13.0 or later
  - A git repository the agent may work on
---

"Software factory" is what people call a setup where issues go in at one end and pull requests come out at the other, with agents doing most of the steps between. Kiro Crew has no feature with that name. It has the parts, so the useful question is which part does which job.

I leaned on five papers from 2025 and 2026 about building software with agents. Each section below says what the papers ask for and which Kiro Crew feature answers it. Click a part to see both at once.

```widget factory-map
```

## What the papers agree on

The five sources come from different places: two model vendors, a consultancy, Google's DORA research program and an independent architect. They still land on the same handful of rules, which I find more convincing than any single one of them:

| Rule | Sources |
|---|---|
| One coordinating agent hands work to helpers, each with its own context | Anthropic, OpenAI, Sogeti |
| The written spec is the contract between people and agents, not the chat | Sogeti, Janda |
| Exactly one agent writes to each working copy | Janda, Sogeti |
| The agent that wrote the change does not approve it | Janda, Anthropic |
| A person steps in on risky actions and after repeated failures | OpenAI, Anthropic, Sogeti |
| Agents ask for help instead of guessing | Anthropic |
| Small batches under version control | DORA, Sogeti |
| Security is designed in from the start | Anthropic, OpenAI |
| AI makes an organization's existing strengths and weaknesses larger | DORA |

That last one frames the rest. DORA's 2025 report says AI's "primary role is as an amplifier, magnifying an organization's existing strengths and weaknesses." A factory with weak gates produces bad pull requests faster, so most of this page is about the gates.

## 1. Orders come in

Work reaches a factory in two ways here:

- **You** give a conductor mode chat a goal and point it at the issue list.
- **Cron jobs** start work on a schedule. See [Schedule real work](../recipes/schedule-real-work.md).

```flow
- split:
    - - box: You
        note: A goal in a chat
    - - box: The clock
        note: Cron job
- box: A Kiro Crew session
  via: each one starts
  accent: true
```

> **What the papers say.** Sogeti's agents start with "product discovery" that frames the problem and its success criteria before anyone builds. DORA lists a user-centric focus among the seven capabilities that decide whether AI helps a team. An order that arrives without a clear outcome is the first place a factory goes wrong.


## 2. Planning turns an order into work

**Conductor mode** plans from a goal. Start it as a dashboard chat with the **Conductor mode** switch on, rather than as a background subagent or a scheduled job. The conductor keeps the goal and a list of items, and hands each item to its own worker chat. An item qualifies only when it is independent of the others, has a completion condition you can name up front, and runs long enough to be worth watching. With fewer than two such items, one plain session is the better shape. See [Conductor mode](conductor-mode.md).

```flow
- box: Goal
- box: Conductor
  note: Splits the goal into items
  accent: true
- box: Work that a worker can pick up
```

> **What the papers say.** Sogeti puts it plainly: "Specifications — not prompts — become the enduring contract between humans and agents." OpenAI's guide pushes the other way on size: "maximize a single agent's capabilities first," and split into several agents only when one agent fails to follow complicated instructions or keeps picking the wrong tools. Kiro Crew's own rule about two qualifying items says the same thing.


## 3. Work orders say what done means

A conductor's items live in the **work ledger**. The conductor writes each item's title and its acceptance condition before dispatch. The worker writes back a status, a short summary, what it produced and, if it opened one, a pull request number. The conductor reads those fields, not the worker's transcript. A session that owns a ledger has **Crew board** in its session actions menu, which shows the items read-only.

The acceptance condition is one of five kinds: `pr_checks`, `pr_merged`, `edition_check`, `file` or `human_approval`. There is no "run this command" kind, so "the tests pass" is expressed as `pr_checks` on the pull request, and CI's verdict counts.

```flow
- box: Work order (ledger item)
  accent: true
  items:
    - "Written by the conductor: title, acceptance, state"
    - "Written by the worker: status, summary, artifacts, pull request"
- box: Crew board
  via: you read it
  note: Read-only. Items that need you come first.
```

> **What the papers say.** Sogeti: "Conversations are transient; artifacts are authoritative." Janda's paper opens with the requirement that agent work must be specified, bounded, isolated, checked, approved and reconstructable afterwards (my translation from the German). The ledger is Kiro Crew's answer to the "specified" and "reconstructable" parts.


## 4. The line moves items through fixed steps

The line here is the one the conductor sets up: goal, item, worker, tests, acceptance, review, integration and merge. The names are this page's own, not dashboard labels. Press Play to follow one issue through it, including a failed test run that sends the worker back.

```widget factory-run
```

> **What the papers say.** DORA counts platform engineering among the seven AI capabilities: a platform gives agents "automated, secure pathways" instead of one-off scripts. Sogeti wants agents to operate "within a governed SDLC". A fixed order of steps that every item follows is that kind of pathway.


## 5. Workbenches keep workers apart

Each worker is its own chat with its own context. For code, its bench is a **git worktree**: a separate checkout of the same repository on its own branch. Give each worker its own worktree and branch in the item's brief, and never let two workers write to the same one. A bot has a **Workers at once** setting that caps how many workers it runs together. See [Bots](bots.md).

```flow
- box: Conductor or crew
- split:
    - - box: Worker 1
        note: Own chat, own worktree
    - - box: Worker 2
        note: Own chat, own worktree
    - - box: Worker 3
        note: Waits for a free bench
  via: hands out items, within the cap
```

> **What the papers say.** Anthropic's 2026 trends report describes multi-agent setups where "an orchestrator ... coordinate[s] specialized agents working in parallel—each with dedicated context." Janda's first principle is a single writer per workspace: exactly one agent writes to each working copy.


## 6. Quality control checks every claim

When a worker reports `done`, the item stays open. The conductor runs an acceptance check against the item's own condition and records `pass`, `fail` or `pending`. Only `pass` closes it.

The `file` kind has a catch: it checks that a file exists, and the worker writes that file itself. A worker that writes it too early passes the check, so make the worker write it only after the tests pass and the commit is made.

Add a second reader for each change. A separate agent that wrote none of it reads the branch against the issue and approves or rejects it. A **monitor loop** keeps one conversation watching for a condition, such as a file appearing, and stops when it is met.

```flow
- box: Worker says done
- box: Acceptance check
  via: the conductor runs
  accent: true
  note: "Checks the item's own condition, not the worker's summary."
- split:
    - - box: pass
        note: Item closes
    - - box: fail
        note: Back to work
    - - box: pending
        note: Wait, at most 24 hours on end
```

> **What the papers say.** Janda separates the roles outright: whoever writes does not approve. One of Anthropic's four priorities for 2026 is "Scaling human-agent oversight through AI-automated review systems that focus human attention where it matters most." Janda adds a warning that applies to every gate on this page: a gate whose failure looks like success is worse than no gate (my translation).


## 7. Safety: fences and the stop button

- **Tool approvals** stop a worker before a risky tool call until someone approves it, once.
- **Read-only folders** (`agent.sandbox_readonly_paths`) let the agent read a folder and never write it. See [Fence the agent](../recipes/fence-the-agent.md).
- **Needs you** on the conductor's Board lists every worker waiting on your answer. [Answer from anywhere](../recipes/answer-from-anywhere.md) shows how to answer from the sidebar or a chat app.
- **Pause all** on the Board stops every running worker until **Resume all**. Workers carry on from where they stopped.

Approvals depend on the chat's approval mode. A worker in a conductor chat can run a command like `rm` without asking, while the same command in a normal chat with the default mode waits for approval. Check the mode before you rely on it.

```flow
- box: Worker wants to act
- box: Fences
  accent: true
  items:
    - Read-only folders
    - Tool approval
- split:
    - - box: Allowed
        note: The step runs
    - - box: Needs you
        note: Waits for your answer
  via: then
- box: Pause all
  note: Stops every worker at once
  via: at any time
```

> **What the papers say.** OpenAI's guide names two triggers for handing control back to a person: "Exceeding failure thresholds" and "High-risk actions," and suggests rating each tool low, medium or high risk by whether it writes, whether it can be undone, and what it can cost. It calls guardrails "a layered defense mechanism". Anthropic wants agents that learn "when to ask for help, rather than blindly attempting every task."


## 8. Shipping ends at a pull request

What leaves this factory is a branch with a commit, or a pull request if your workers push. Tell workers to commit on their own branches and never merge or push. The merge to the main branch stays with a person.

Everything before it can run without me, but the merge is where code reaches the main branch, and I want one human decision there.

Parallel workers create one more job that nobody owns by default: putting their branches back together. Workers that finish at the same time often touched the same files, for example each one appending tests to the same test file, so their branches conflict even though each one is fine on its own. Kiro Crew has no built-in step for this, so I give it to one worker as a separate item:

1. Create an integration branch from main and merge the first finished branch into it.
2. Merge the next branch. If git reports a conflict, the worker resolves it keeping both sides' intent, for example every test from both branches.
3. Run the tests. Move on only when they pass.
4. Repeat for each remaining branch, then hand the integration branch to the human merge.

Only one worker writes to the integration branch, which keeps the one-writer rule intact.

```flow
- box: Worker branches
  note: One commit each, tests pass
- box: Integration branch
  accent: true
  note: One worker merges them one at a time
- box: You merge
```

> **What the papers say.** DORA lists working in small batches and version control among its AI capabilities, because faster change needs a safety net. Sogeti describes reintegration "in stages rather than as a single disruptive merge," with an orchestrator that tracks merge readiness. In Sogeti's role table the reviewer stays human.


## 9. Gauges show where work piles up

A session that owns a ledger has **Crew board** in its session actions menu. It shows the goal, what is done, what **needs your input** and a recap of the milestones, read-only. For one turn, [traces](../recipes/trace-agent-turns.md) show where the time went: `kirocrew trace show` draws the turn and its tool calls as nested spans, and a refused action shows as an error. Turn traces on from your own terminal, because the dashboard row is read-only.

```flow
- box: Crew board
  accent: true
  items:
    - Done, needs your input, recap
- box: Traces
  note: One turn, drawn as a waterfall
```

> **What the papers say.** If AI amplifies what is already there, as DORA finds, you need to see what is there before you speed it up. Anthropic's report notes that engineers "fully delegate" only 0 to 20 percent of tasks even while using AI in about 60 percent of their work, so the gauges that matter show where people still spend their time.


## 10. Getting better every run

A correction you give with "always" or "never" becomes a **lesson** that comes back in later sessions. A worker you start later follows the rule without being told. See [Make it remember](../recipes/make-it-remember.md).

```flow
- box: A run goes wrong
- box: You correct it
- box: Lesson
  accent: true
  note: Comes back in later sessions
- box: Next run starts smarter
```

> **What the papers say.** OpenAI: "Add new guardrails based on real-world edge cases and failures you encounter." DORA's capabilities include AI-accessible internal data and a healthy data ecosystem: what the organization already knows has to reach the agent.


## Pick a size

| Size | Parts | Fits |
|---|---|---|
| One session | A normal chat, with tool approvals on | One issue you watch |
| Conductor | A conductor mode chat, one worker per item, the Board, Pause all, a reviewer and an integration worker | A day of parallel work you watch |

## Sources

- Anthropic, *2026 Agentic Coding Trends Report*, January 2026. [PDF](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf). Short quotes, pages 3, 8, 10 and 17.
- OpenAI, *A practical guide to building agents*, April 2025. [PDF](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). Short quotes, pages 16, 25, 27 and 31.
- Mike Buob and Kevin Benner, Sogeti, *Transforming enterprise software delivery through agentic AI*, July 2026. [Page](https://labs.sogeti.com/whitepaper-transforming-enterprise-software-delivery-through-agentic-ai/). Short quotes, pages 2, 3, 5 and 7.
- DORA (Google Cloud), *State of AI-assisted Software Development*, 2025, and the *DORA AI Capabilities Model*. [Report](https://dora.dev/research/2025/dora-report/), [capabilities](https://dora.dev/ai/capabilities-model/). Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by Google LLC; quoted and summarized here.
- Martin Janda, *Agentic Software Development: Enterprise Architecture with AI Agents*, version 3.2, October 2026. [Repository](https://github.com/mjanda0815/agentic-publikation). Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); principles summarized and translated from German.

## Related

- [Conductor mode](conductor-mode.md)
- [Bots](bots.md)
- [Fence the agent](../recipes/fence-the-agent.md)
- [Answer from anywhere](../recipes/answer-from-anywhere.md)
- [Trace every agent turn](../recipes/trace-agent-turns.md)
