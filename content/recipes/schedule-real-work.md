---
title: Schedule real work
description: Build a cron job you would actually keep, test it once, and make it speak only on a real signal.
category: Automation
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [cron, schedules, notifications]
updated: 2026-10-29
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
---

**Problem.** Some work should happen without you. A morning check. A nightly scan. A weekly report. You do not want to remember to run it, and you do not want to sit and watch it.

That is a **cron job**: a task KiroCrew runs on a schedule, on its own.

## Steps

### 1. Ask for it in plain words

You do not write cron syntax. You say when and what:

```prompt
Every weekday at 8am, check my main repo for open PRs that have no review yet, and send me a summary.
```

KiroCrew creates the job. It picks the schedule from your words ("every weekday at 8am").

### 2. Say where the result goes

By default a scheduled result shows up as a dashboard notification. You can send it to a channel instead:

```prompt
Post the result to my Slack DM.
```

### 3. Smoke-test it now

Do not wait until tomorrow morning to find out it is broken. Trigger it once:

```prompt
Run that scheduled job now so I can see the output.
```

Check the result. Fix the wording if the output is not what you want.

### 4. List and manage your jobs

```prompt
List my scheduled jobs.
Pause the PR-check job.
Change it to run at 9am instead of 8am.
```

You can pause, resume, re-time, or remove any job by asking.

## Pick the right kind of job

Two kinds, and the difference matters for cost and reliability.

| Kind | Use for | Why |
|---|---|---|
| **Conversational** | Reminders, summaries, anything that should remember past runs | Keeps context between runs |
| **Lightweight poll** | Checkers, scanners, digests that just report a fact | Cheap, no memory carried, fresh each run |

If your job just checks something and reports — "is the build green?", "any new tickets?" — ask for the **lightweight** kind. Say so:

```prompt
Make it a lightweight polling job — no need to remember past runs.
```

That keeps it cheap and stops it dragging old context into every wake.

## A job worth keeping

A good first cron is one you would actually miss. Examples that earn their place:

- **PR babysitter.** Every 2 hours, check your open PR for new review comments; ping you only if there are any.
- **Morning digest.** Weekdays at 8am, summarize overnight activity on your repos.
- **Cost watch.** Daily, read one cloud bill figure and alert only if it crossed a line.

Notice the pattern: **report only when there is something to report.** A job that pings you every run with "nothing happened" gets muted in a week.

## Verify

- Trigger the job once by hand (step 3). You should get the output you expected.
- List your jobs. The schedule and target should read right.
- Wait for one real fire. It should arrive where you said, on time.

## Gotchas

- **Say the timezone for clock times.** "8am" is ambiguous across zones. Name yours ("8am Berlin time") so it fires when you mean.
- **"List my jobs" shows this session's jobs.** A job you made in another session or on the dashboard may not show here. That does not mean it is gone — check the Schedule page in the dashboard.
- **Noisy jobs die.** If it pings you every run with nothing, you will mute it. Build it to speak only on a real signal.
- **Smoke-test before you trust it.** A silent broken job is worse than no job. Trigger it once, right after you make it.

## What you learned

Describe the schedule in words; KiroCrew builds the job. Send the result where you want it. Pick lightweight for pure checkers. Trigger once to prove it. And make it report only when it matters.
