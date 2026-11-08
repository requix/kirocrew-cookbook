---
title: "Ultra Mode: a chat that runs a crew"
description: How the Ultra Mode preview hands tasks to worker chats, what the Board shows, and when a regular chat fits better.
category: Concepts
difficulty: beginner
time: 10 min
surfaces: [dashboard]
tags: [ultra-mode, crew-mode, conductor, workers, board, preview]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later
  - A dashboard chat session
---

A regular chat is one agent working through your request one step after another. That is fine for a question or a small fix. When a request splits into several pieces that could run side by side, one agent ends up carrying all of them in a single context, and you wait for each piece in turn.

Ultra Mode, shipped as a preview in 0.12.0, changes who does the work. The chat you type into becomes a conductor, and the conductor hands each task to its own worker chat. The docs also call this Crew Mode; Ultra Mode is the name on the preview switch.

## Turn it on

Ultra Mode is off by default. Open **Settings > Developer > Feature Previews** and switch on **Ultra Mode**. The switch is per device and is kept in the browser you set it in, so another browser or machine needs its own.

Once it is on, you will see an **Ultra Mode** chip in two places:

- on a new chat, in the composer
- on an ongoing plain chat, to the right of the permission button

On an ongoing chat, the chip turns that chat into an Ultra Mode chat. This goes one way. You cannot turn the chat back into a plain one, so start a new chat if you want a regular conversation again.

## How it works

The chat runs on a conductor, which is a specialised agent (`kirocrew-conductor`). It does not do the leaf work itself. It keeps a goal and a list of items, and for each item it opens a separate worker chat and hands the task over. The chat keeps its memory and history after the switch.

Each worker is a normal agent with your default toolset plus the two tools it needs to report back. It has its own context, so one task's logs and file reads do not crowd out another's. When a worker reports that it is done, the conductor checks the claim against acceptance criteria instead of trusting the worker's own summary.

The worker chats are kept out of your folders, so your session list does not fill up with them. History still lists them if you need to find one.

Once the chat has its first message it is locked to the conductor. Switching it to another agent is refused. Start a new chat to work with a different agent.

## The Board tab

With Ultra Mode on, the side panel for that chat shows the crew by status. The groups that matter most:

- **Needs you:** a worker is blocked on a decision, a permission or an answer only you can give.
- **Stalled:** a worker has gone quiet and may need a nudge or a look at its transcript.
- **Running:** workers that are making progress and need nothing from you.

Check **Needs you** first. A worker waiting on an approval does not move until you answer, and the rest of the crew carries on without it, so the wait can go unnoticed. Everything under **Running** can be left alone.

In the Sessions list the chat appears as a crew card, and there is a **Crew Mode** filter to find these chats.

## Coming back to it

Ultra Mode is meant for work that takes a while, so you will often leave and return. When you come back, the conductor posts a catch-up message that says what finished, what is still running and what is waiting on you. Read it before you open the Board. It usually tells you which workers to look at.

## When to use it

Use Ultra Mode when the request splits into pieces that can run independently, such as reviewing several files against the same checklist, investigating a handful of unrelated failures, or preparing a change across separate parts of a repo. It also fits work you expect to leave running while you do something else.

Use a regular chat when the task is a single thread. A question, a one-file fix, a refactor where each step depends on the last, or a conversation where you want to steer every move gains nothing from a conductor, and it adds overhead: more chats and more tokens, because each worker starts with its own context.

If you are unsure, start regular. You can turn an ongoing chat into an Ultra Mode chat later when the work turns out to be wider than you thought.

## Verify

1. Turn on **Ultra Mode** under **Settings > Developer > Feature Previews**.
2. Open a new chat. The **Ultra Mode** chip should be in the composer.
3. Send a request with two or three independent tasks.
4. Open the side panel and check that the Board lists workers under their statuses.
5. Leave the chat for a few minutes, then return and read the catch-up message.

## Gotchas

- **It is a preview.** Names and layout may change between releases. The switch is hidden until you turn it on.
- **The switch is per browser.** Turning it on in one browser does not turn it on in another.
- **The conversion is one way.** An ongoing chat that becomes an Ultra Mode chat stays one.
- **Needs you does not push itself at you.** A blocked worker waits quietly, so check the Board when you return.
- **More workers cost more.** Each worker has its own context and its own model usage.

For how the agents behind this fit together, see [how-it-fits](how-it-fits.md). For approvals that can put a worker into **Needs you**, see [security](security.md).
