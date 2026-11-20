---
title: Kiro Crew as a software factory
description: What recent papers say an AI software factory needs, and which Kiro Crew feature plays each part.
category: Concepts
difficulty: intermediate
time: 20 min
surfaces: [dashboard, channels, cli]
tags: [software-factory, agentic-coding, conductor-mode, work-ledger, worktree, pipeline, governance]
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

Work can reach Kiro Crew four ways, and you can combine them:

- **Issue Radar** is an app that reads your GitHub, GitLab or Azure DevOps items, suggests labels and keeps a local findings ledger.
- **Slack code channels** give each coding task its own Slack channel and, on a git project, its own worktree. See [Slack code channels](../recipes/slack-code-channels.md).
- **Inbound webhooks** let another system start a turn. A CI runner or ticket system POSTs to `/api/hooks/agent`, the gateway runs one turn in a short-lived session, and the answer goes to your notifications. The dashboard page for it sits behind the **Webhooks** switch under **Settings > Developer > Feature Previews**.
- **Cron jobs** start work on a schedule. See [Schedule real work](../recipes/schedule-real-work.md).

```flow
- split:
    - - box: Issue tracker
        note: Issue Radar
    - - box: Slack channel
        note: Code channel
    - - box: Another system
        note: Inbound webhook
    - - box: The clock
        note: Cron job
- box: A Kiro Crew session
  via: each one starts
  accent: true
```

> **What the papers say.** Sogeti's agents start with "product discovery" that frames the problem and its success criteria before anyone builds. DORA lists a user-centric focus among the seven capabilities that decide whether AI helps a team. An order that arrives without a clear outcome is the first place a factory goes wrong.


## 2. Planning turns an order into work

**Spec Builder** is a built-in app for spec-driven work: a feature idea becomes Requirements, then Design, then Tasks, and the tasks feed an execution session. **Conductor mode** plans from a goal instead. The conductor keeps the goal and a list of items, and hands each item to its own worker chat. An item qualifies only when it is independent of the others, has a completion condition you can name up front, and runs long enough to be worth watching. With fewer than two such items, one plain session is the better shape. See [Conductor mode](conductor-mode.md).

```flow
- box: Feature idea or goal
- split:
    - - box: Spec Builder
        steps: [Requirements, Design, Tasks]
    - - box: Conductor
        note: Splits the goal into items
  via: pick a planner
- box: Work that a worker can pick up
  accent: true
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

Issue Radar runs one fixed pipeline for every repository: Scan, Triage, Dispatch, Implement, Verify and Cleanup. A repository can set how long a claim lasts, which label a crew applies when it needs a person, and its commit trailer. It cannot add steps of its own.

Each crew work item gets a lane on the **Item lanes** board. Press Play to follow one issue through the phase columns, including a CI failure that sends it back to Implement.

```widget factory-run
```

A `#N` chip names the item's open pull request. An arc under the lane means the item went back to a phase, and a stub off the lane is an exit: skipped, yielded, handed back, preempted, or waiting on a human reply. The Pipeline tab works with GitHub only, while Item lanes works on every forge.

> **What the papers say.** DORA counts platform engineering among the seven AI capabilities: a platform gives agents "automated, secure pathways" instead of one-off scripts. Sogeti wants agents to operate "within a governed SDLC". A fixed line that every repository shares is that kind of pathway.


## 5. Workbenches keep workers apart

Each worker is its own chat with its own context. For code, its bench is a **git worktree**: a separate checkout of the same repository on its own branch. On the Item lanes board, Implement and Addressing review sit inside a fence because they hold a worktree with uncommitted changes, and at most one item per crew is in them at a time. A bot has a **Workers at once** setting that caps how many workers it runs together. See [Bots](bots.md).

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

When a worker reports `done`, the item stays open. The conductor runs an acceptance check against the item's own condition and records `pass`, `fail` or `pending`. Only `pass` closes it. Two more checkers fit here: a **monitor loop** keeps one conversation watching a pull request or CI run, and **Code Review Sage** deep-reviews a GitHub pull request and points at the changes that deserve your attention.

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
- **Pause all** on the Board stops every running worker until **Resume all**, and the pause holds across a gateway restart.
- In Issue Radar, a crew that needs a person applies the repository's human label.

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

What leaves this factory is a pull request. The worker records its number on the item, the Item lanes board shows it as a `#N` chip, and once CI and review are done the item waits in **AWAIT MRG** for a merge.

I keep that merge with a person. Everything before it can run without me, but the merge is where code reaches the main branch, and I want one human decision there.

```flow
- box: Pull request opened
  note: "Shown as a #N chip on the lane"
- box: CI and review
- box: AWAIT MRG
  accent: true
  note: Waits for a merge
- box: You merge
- box: RESOLVED
```

> **What the papers say.** DORA lists working in small batches and version control among its AI capabilities, because faster change needs a safety net. Sogeti describes reintegration "in stages rather than as a single disruptive merge," with an orchestrator that tracks merge readiness. In Sogeti's role table the reviewer stays human.


## 9. Gauges show where work piles up

Issue Radar's **Pipeline** dashboard shows, for each step, what is sitting there now (**In step**), what moved through recently (**Recent**) and the total so far (**Total**). Click a step to see its items and each agent session's turns, tokens, credits and cost where the server reports them. It is the only place the cost per issue shows up. The **Item lanes** tab adds **In flight**, **Editing**, **Escalations** and **Longest wait**, and flags any item stuck in one phase for over an hour. For one turn, [traces](../recipes/trace-agent-turns.md) show where the time went.

```flow
- box: Pipeline tab
  accent: true
  items:
    - In step, Recent, Total per step
    - Cost per issue
- box: Item lanes tab
  items:
    - In flight, Editing, Escalations, Longest wait
    - Items stuck over an hour are flagged
- box: Traces
  note: One turn, drawn as a waterfall
```

> **What the papers say.** If AI amplifies what is already there, as DORA finds, you need to see what is there before you speed it up. Anthropic's report notes that engineers "fully delegate" only 0 to 20 percent of tasks even while using AI in about 60 percent of their work, so the gauges that matter show where people still spend their time.


## 10. Getting better every run

A correction you give with "always" or "never" becomes a **lesson** that comes back in later sessions. See [Make it remember](../recipes/make-it-remember.md). For the code itself, the **Auto-Improvement** app measures a GitHub repository before it changes anything, then keeps or reverts each change against that measurement.

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
| Small | A task runner spec run with `kirocrew run`, with an allowlist of the tools it may use | One batch of issues you start by hand |
| Medium | A conductor mode chat, one worker per item, the Board and Pause all | A day of parallel work you watch |
| Large | Issue Radar crews on the repository, the Pipeline dashboard and a human merge | A live backlog that keeps moving |

## Sources

- Anthropic, *2026 Agentic Coding Trends Report*, January 2026. [PDF](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf). Short quotes, pages 3, 8, 10 and 17.
- OpenAI, *A practical guide to building agents*, April 2025. [PDF](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). Short quotes, pages 16, 25, 27 and 31.
- Mike Buob and Kevin Benner, Sogeti, *Transforming enterprise software delivery through agentic AI*, July 2026. [Page](https://labs.sogeti.com/whitepaper-transforming-enterprise-software-delivery-through-agentic-ai/). Short quotes, pages 2, 3, 5 and 7.
- DORA (Google Cloud), *State of AI-assisted Software Development*, 2025, and the *DORA AI Capabilities Model*. [Report](https://dora.dev/research/2025/dora-report/), [capabilities](https://dora.dev/ai/capabilities-model/). Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by Google LLC; quoted and summarized here.
- Martin Janda, *Agentic Software Development: Enterprise Architecture with AI Agents*, version 3.2, October 2026. [Repository](https://github.com/mjanda0815/agentic-publikation). Licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); principles summarized and translated from German.

## Related

- [Conductor mode](conductor-mode.md)
- [Bots](bots.md)
- [Slack code channels](../recipes/slack-code-channels.md)
- [Fence the agent](../recipes/fence-the-agent.md)
- [Answer from anywhere](../recipes/answer-from-anywhere.md)
- [Trace every agent turn](../recipes/trace-agent-turns.md)
