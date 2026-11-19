---
title: "Conductor mode: a chat that runs a crew"
description: How conductor mode hands tasks to worker chats, what the Board shows, and when a regular chat fits better.
category: Concepts
difficulty: beginner
time: 10 min
surfaces: [dashboard]
tags: [conductor-mode, ultra-mode, crew-mode, conductor, workers, board]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - A dashboard chat session
---

A regular chat is one agent working through your request one step after another. That is fine for a question or a small fix. When a request splits into several pieces that could run side by side, one agent ends up carrying all of them in a single context, and you wait for each piece in turn.

Conductor mode changes who does the work. The chat you type into becomes a conductor, and the conductor hands each task to its own worker chat. It shipped as the Ultra Mode preview in 0.12.0 and became generally available in 0.13.0 under its new name. If you see Ultra Mode or Crew Mode in older notes, it is the same thing.

## Turn it on

There is nothing to enable. A new chat's composer has a **Conductor mode** switch, and an ongoing plain chat has it to the right of the permission button. The old preview switch under **Settings > Developer > Feature Previews** is gone, and a value saved from it is ignored.

- **On a new chat**, you can turn the switch off again any time before your first message.
- **On an ongoing chat**, the switch goes one way. The chat stays in conductor mode, so start a new chat if you want a regular conversation again.

To start every new chat in conductor mode, turn on **Settings > Chat > Sessions > Start New Chats in conductor mode**. It is off by default, and it does not apply to Incognito or Temporary chats or to chats on another agent.

The LTS edition does not offer conductor mode. There, the conductor templates are ordinary agents in the agent picker.

## How it works

The chat runs on a conductor, a specialised agent called `kirocrew-conductor`. To run a different conductor, set `agent.crew_mode_agent`. The conductor does not do the leaf work itself. It keeps a goal and a list of items, and for each item it opens a separate worker chat and hands the task over. The chat keeps its memory and history after the switch.

```widget conductor-run
```

Each worker is a normal agent with your default toolset plus the two tools it needs to report back. It has its own context, so one task's logs and file reads do not crowd out another's. When a worker says it is done, the conductor checks the claim against acceptance criteria instead of trusting the worker's own summary.

Since 0.13.0 the conductor also checks its own work:

- It plans from the goal first and tests the plan before any worker starts.
- It takes sensible defaults instead of stopping to ask you about small choices.
- On every patrol it checks each worker's new work for drift, and re-plans only the item that went wrong.
- Once an hour it looks at every open item.
- It sends messages to its own workers and closes them without an approval prompt.

The worker chats are kept out of your folders, so your session list does not fill up with them. History still lists them if you need to find one.

Once the chat has its first message it is locked to the conductor. Switching it to another agent is refused. Start a new chat to work with a different agent.

## The Board tab

The side panel of a conductor mode chat has a **Board** tab. Read it top to bottom:

- **Recap:** how many items are done out of the total, and who is waiting, stuck or quiet.
- **Needs you:** approvals and questions only you can answer. You can reply from here.
- **Milestones:** every item with its state. A worker that has gone quiet is marked **Stalled**.

Check **Needs you** first. A worker waiting on an approval does not move until you answer, and the rest of the crew carries on without it, so the wait can go unnoticed.

The Workers tree folds under each lead and names the machine each worker runs on. The chat itself says when a run is done or stopped.

To stop everything at once, press **Pause all** on the Board. It stops every running worker, sub-teams included, and no new workers start while the crew is paused. Steps that were in progress run again when you press **Resume all**. The pause holds across a gateway restart.

In the Sessions list the chat appears as a crew card, and the **Conductor mode** filter finds these chats.

## When to use it

Use conductor mode when the request splits into pieces that can run independently, such as reviewing several files against the same checklist, investigating a handful of unrelated failures, or preparing a change across separate parts of a repo. It also fits work you expect to leave running while you do something else.

Use a regular chat when the task is a single thread. A question, a one-file fix, a refactor where each step depends on the last, or a conversation where you want to steer every move gains nothing from a conductor. It also adds overhead: more chats and more tokens, because each worker starts with its own context.

If you are unsure, start regular. You can turn an ongoing chat into a conductor mode chat later when the work turns out to be wider than you thought.

## Verify

1. Open a new chat. The **Conductor mode** switch should be in the composer.
2. Turn it on and send a request with two or three independent tasks.
3. Open the side panel and check that the Board lists the items under **Milestones**.
4. Press **Pause all**, confirm the workers stop, then press **Resume all**.
5. Leave the chat for a few minutes, then return and read the **Recap** on the Board.

## Gotchas

- **The conversion is one way.** An ongoing chat that becomes a conductor mode chat stays one.
- **Needs you does not push itself at you.** A blocked worker waits quietly, so check the Board when you return.
- **Pause is not cancel.** A step that was cut off by the pause runs again from the start on resume.
- **More workers cost more.** Each worker has its own context and its own model usage.

For how the agents behind this fit together, see [How the pieces fit](how-it-fits.md). For approvals that can put a worker into **Needs you**, see [security](security.md).
