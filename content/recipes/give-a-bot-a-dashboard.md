---
title: Give a bot a dashboard
description: Set up a custom dashboard so your bot shows where its work stands in one glance.
category: Automation
difficulty: intermediate
time: 15 min
surfaces: [dashboard]
tags: [bots, crewmates, dashboard, goals]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew running (see Your first hour)
  - A bot with a goal set (see Design your first bot)
---

**Problem.** Your bot works. It triages issues, watches builds, reviews PRs. But to see what it has done, you scroll its chat transcript. What is in flight? What is blocked? What needs you? The answers are in there, buried in messages.

A dashboard is one page that answers those questions without a scroll. The bot writes it and keeps it current. You open the tab, see the state, and move on.

## What the dashboard shows

A bot's Dashboard tab is not a static report. It is a live view over the bot's work:

| Block | What it answers |
|---|---|
| Headline | How many tasks are in flight, what the bot spent, how many need you |
| Status cards | In flight, accepted, credits spent, needs attention |
| Trend lines | Credits per hour, tasks accepted over time |
| Needs you | One card per item — blocked tasks, open questions, decisions waiting |
| Work tree | Every workstream and task, with progress and cost on each row |

The bot fills these from its work ledger and its own notes. When it finishes a task, the dashboard updates. When something blocks, it shows up in the "needs you" section.

## Steps

### 1. Make sure the bot has a goal and milestones

The dashboard offer only comes after your bot has a goal and at least one milestone. If you skipped those:

```prompt
Let's set a goal for this bot.
```

The bot proposes a goal card. Press it. Then it proposes milestones. Press those too. The dashboard offer comes next.

### 2. Accept the dashboard offer

After milestones are confirmed, the bot offers to write a dashboard page with `offer_dashboard_page`. You see a card in the chat:

> Would you like me to create a Dashboard page around this goal?

Press the card. The bot writes the page and it goes live on the bot's Dashboard tab.

If you already dismissed this card, the bot does not offer again by default. You can ask it directly:

```prompt
Build me a dashboard page for this work.
```

### 3. Check the Dashboard tab

Open the bot on the Bots page. Switch from Chat to the **Dashboard** tab. You should see:

- The headline summary
- Cards for status and spend
- The needs-you section (empty if nothing is blocked)
- The work tree (populated as tasks run)

If the page is blank, the bot has not run any tasks yet. Give it something to do and check back.

### 4. Let the bot update it

The bot updates its dashboard using `dashboard_write`. This happens automatically when:

- A task completes or changes state
- Something gets blocked
- The bot records a milestone reading
- The heartbeat wakes and the bot does work

You do not need to ask the bot to refresh the page. It keeps it current.

### 5. Customize what it shows (optional)

If you want a different layout or different data:

```prompt
Add a section showing the last 5 completed tasks with their duration.
```

The bot adjusts the page. What it can show depends on what it tracks — the work ledger, milestone readings, and any notes the bot writes itself.

## How the bot writes to the dashboard

The dashboard is a template filled from folds in the bot's crew log. That means:

- **No model call to read it.** The page renders from stored data, not from asking the model.
- **Agentic values are marked.** When the bot writes something itself (a verdict, a note, a priority), the page shows it is the bot's own claim, not a recorded fact.
- **The bot cannot fake the numbers.** Credits, task counts, and durations come from the log. The bot fills the qualitative parts — the verdict, the blocked-item notes — and those are labeled.

The tools involved:

- `dashboard_write` — writes a value into the page (a verdict, a note, a field)
- `dashboard_save` — saves the page layout, creating a new version
- `dashboard_preview` — previews before saving

## The verdict line

At the top of the dashboard is a one-line verdict. The bot writes this to summarize the state:

- **on_track** — work is moving, nothing blocked
- **needs_you** — something is waiting on your input
- **blocked** — the bot is stuck
- **no_word** — the fold has advanced since the verdict was written, so the page shows the last known state with a note

This is the one value that can go stale. If the bot dies mid-run or misses a heartbeat, the page downgrades to `no_word` automatically. You never see a confident "on track" for a bot that is actually dead.

## Verify

- The Dashboard tab shows real data — at least the summary cards.
- Run a task and watch the dashboard update.
- Block something deliberately (ask the bot a question it cannot answer without you). It should show in the needs-you section.
- Check that the verdict line reflects reality.

## Gotchas

- **No dashboard without a goal.** The offer only comes after goals and milestones are set. If you skip those, there is nothing to build the page around.
- **The offer comes once.** If you dismiss the card, the bot does not offer again automatically. Ask directly if you change your mind.
- **Agentic values are the bot's opinion.** The verdict, the notes, the priorities — these are what the bot thinks, not what the log records. The page marks them so you know the difference.
- **A blank page means no work yet.** The dashboard draws from the work ledger. No tasks, no data. Run something first.
- **The dashboard is per-bot.** Each bot gets its own page. There is no cross-bot rollup.

## What you learned

A dashboard shows where a bot's work stands without scrolling the transcript. The bot offers to build it after you set goals and milestones. It updates automatically as work happens. The verdict line and notes are the bot's own claims; the numbers come from the log. Check the Dashboard tab to see the state in one glance.
