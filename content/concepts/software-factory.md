---
title: Kiro Crew as a software factory
description: The parts of a software factory, from orders in to shipping, and the Kiro Crew feature that plays each one.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, channels, cli]
tags: [software-factory, issue-radar, conductor-mode, work-ledger, worktree, pipeline, automation]
updated: 2026-11-20
featured: true
prerequisites:
  - Kiro Crew 0.13.0 or later
  - A git repository the agent may work on
---

"Software factory" is a name people give to a setup where issues go in at one end and pull requests come out at the other, with agents doing most of the steps between. Kiro Crew has no feature with that name. It has the parts, though, and they map onto a factory quite well: something takes orders, something plans, workers sit at separate benches, someone checks the output, and there is a button that stops the line.

This page walks through those parts one at a time. Each section names the factory idea, the Kiro Crew feature that plays it, and draws how the pieces connect. Click a part below to jump to it.

```widget factory-map
```

## 1. Orders come in

A factory needs a way to receive orders. In Kiro Crew, work can arrive four ways, and you can use more than one:

- **Issue Radar** is an app that reads your GitHub, GitLab or Azure DevOps items, suggests labels and keeps a local findings ledger. It is the natural front door when your backlog already lives in an issue tracker.
- **Slack code channels** give each coding task its own Slack channel. The channel is one Kiro Crew session, and on a git project it works in its own worktree. See [Slack code channels](../recipes/slack-code-channels.md).
- **Inbound webhooks** let another system start a turn. A CI runner or a ticket system POSTs to `/api/hooks/agent`, the gateway runs one agent turn in a short-lived session, and the answer goes to your notifications. The endpoint is supported, while its dashboard page sits behind the **Webhooks** switch under **Settings > Developer > Feature Previews**.
- **Cron jobs** start work on a schedule, such as "every morning, check the new issues". See [Schedule real work](../recipes/schedule-real-work.md).

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

## 2. Planning turns an order into work

A raw issue is rarely ready to build. Someone has to decide what "fixed" looks like and how to split the job. Kiro Crew has two planners for this.

**Spec Builder** is a built-in app for spec-driven work. A feature idea becomes Requirements, then Design, then Tasks, and the tasks feed an execution session. Use it when a request is vague and you want to read the plan before any code changes.

**Conductor mode** plans from a goal. The conductor keeps the goal and a list of items, and hands each item to its own worker chat. A piece of work qualifies as an item only when it is independent of the other items, has a completion condition you can name up front, and runs long enough that you would want to watch it. With fewer than two such items, one plain session is the better shape. See [Conductor mode](conductor-mode.md).

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

## 3. Work orders say what done means

On a factory floor, a work order travels with the part. In Kiro Crew that order is an item in the **work ledger**, the shared record between a conductor and its workers. The conductor writes the item's title and its acceptance condition. The worker writes back a status, a short summary, pointers to what it made and, when it opened one, a pull request number.

The conductor learns what happened by reading those fields, not by reading the worker's transcript. A transcript grows without limit and can carry instructions; a ledger field is plain data. A session that owns a ledger has **Crew board** in its session actions menu, which shows the items read-only: what needs your decision first, then open work, then finished items.

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

## 4. The line moves items through fixed steps

Issue Radar runs one fixed pipeline for every repository: Scan, Triage, Dispatch, Implement, Verify and Cleanup. A repository can set how long a claim lasts, which label a crew applies when it needs a person, and its commit trailer. It cannot add steps of its own, which keeps every repository's board readable the same way.

Inside the pipeline, each crew work item gets a lane on the **Item lanes** board. The lane runs through the phase columns below. Press Play to follow one issue, including a CI failure that sends it back to Implement.

```widget factory-run
```

The board draws state with shapes. A `#N` chip names the item's open pull request. An arc under the lane means the item went back to a phase, and a stub off the lane is an exit: skipped, yielded, handed back, preempted, or waiting on a human reply. The Pipeline tab works with GitHub only, while Item lanes works on every forge.

## 5. Workbenches keep workers apart

Two workers at one bench get in each other's way. In Kiro Crew each worker is its own chat with its own context, so one task's logs and file reads do not crowd out another's. For code, the bench is a **git worktree**: a separate checkout of the same repository on its own branch. A Slack code channel, for example, cuts a worktree on a branch named `slack/<slug>-<hash>`.

There are also limits on how many workers run at once. On the Item lanes board, Implement and Addressing review sit inside a fence: those phases hold a worktree with uncommitted changes, so at most one item per crew is in them at a time. A bot has a **Workers at once** setting on its profile that caps how many workers it runs together. See [Bots](bots.md).

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

## 6. Quality control checks every claim

When a worker reports `done`, the item stays open. The conductor runs an acceptance check against the item's own condition and records a verdict: `pass`, `fail` or `pending`. A `pending` item waits up to 24 hours before the conductor decides whether to keep waiting or drop it. Only a `pass` closes the item as done.

Two more checkers fit here. A **monitor loop** keeps one conversation checking a pull request or a CI run on a schedule, and only speaks up when something changes. **Code Review Sage** is a built-in app that deep-reviews a GitHub pull request and tells you which changes deserve your attention.

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

## 7. Safety fences and the stop button

A factory keeps people's hands out of the machines and has a cord anyone can pull. Kiro Crew has both:

- **Tool approvals** stop a worker before a risky tool call until someone approves it. An approval is a one-time grant for that call.
- **Read-only folders** (`agent.sandbox_readonly_paths`) let the agent read a folder and never write it. See [Fence the agent](../recipes/fence-the-agent.md).
- **Needs you** on the conductor's Board lists every worker waiting on your answer. You can answer from the sidebar card or a chat app DM, as [Answer from anywhere](../recipes/answer-from-anywhere.md) shows.
- **Pause all** on the Board stops every running worker, and no new workers start until you press **Resume all**. The pause holds across a gateway restart.
- In Issue Radar, a crew that needs a person applies the repository's human label instead of guessing.

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

## 8. Shipping ends at a pull request

What leaves this factory is a pull request. The worker records its number on the item, the Item lanes board shows it as a `#N` chip, and once CI and review are done the item sits in **AWAIT MRG** until someone merges.

I keep that merge with a person. Everything before it can run without me, but the merge is where code reaches the main branch, and I want one human decision there. When you hand merges to an agent anyway, do it on a repository where a bad merge is cheap to revert.

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

## 9. Gauges show where work piles up

A factory manager watches the line, not each worker. Issue Radar's **Pipeline** dashboard does that job. For each of the six steps it shows what is sitting there now (**In step**), what moved through recently (**Recent**) and the total so far (**Total**). Click a step to see its items and the agent sessions each one opened, with turns, tokens, credits and cost where the server reports them. It is the only place the cost per issue shows up.

The Item lanes tab adds **In flight**, **Editing**, **Escalations** and **Longest wait**, and flags any item that has sat in one phase for over an hour. For a single turn, [traces](../recipes/trace-agent-turns.md) show where the time went: model calls, tool calls and approval waits.

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

## 10. Getting better every run

A good factory fixes the cause of a defect, not only the defect. In Kiro Crew, a correction you give with "always" or "never" becomes a **lesson**, which comes back in later sessions, so the same mistake does not need the same correction twice. See [Make it remember](../recipes/make-it-remember.md).

For the code itself, the **Auto-Improvement** app measures a GitHub repository before it changes anything, then runs improvement cycles where each change is kept or reverted against that measurement.

```flow
- box: A run goes wrong
- box: You correct it
- box: Lesson
  accent: true
  note: Comes back in later sessions
- box: Next run starts smarter
```

## Pick a size

You do not need every part on day one. These are three sizes I would start from:

| Size | Parts | Fits |
|---|---|---|
| Small | A task runner spec run with `kirocrew run`, with an allowlist of the tools it may use | One batch of issues you start by hand |
| Medium | A conductor mode chat, one worker per item, the Board and Pause all | A day of parallel work you watch |
| Large | Issue Radar crews on the repository, the Pipeline dashboard and a human merge | A live backlog that keeps moving |

## Related

- [Conductor mode](conductor-mode.md)
- [Bots](bots.md)
- [Slack code channels](../recipes/slack-code-channels.md)
- [Fence the agent](../recipes/fence-the-agent.md)
- [Answer from anywhere](../recipes/answer-from-anywhere.md)
- [Trace every agent turn](../recipes/trace-agent-turns.md)
