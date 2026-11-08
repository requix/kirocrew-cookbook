---
title: Design your first bot
description: Pick a responsibility, set boundaries, and build one bot that earns its place.
category: Automation
difficulty: intermediate
time: 20 min
surfaces: [dashboard]
tags: [bots, crewmates, goals, delegation]
updated: 2026-11-08
featured: true
prerequisites:
  - Kiro Crew running (see Your first hour)
  - You understand what a bot is (see Bots in Concepts)
---

**Problem.** You have been running sessions in parallel. One refactors code, another chases a flaky test, a third drafts a migration plan. You come back and each one needs context you have to rebuild — where it stopped, what it decided, what still needs you. The more sessions you run, the more time you spend shepherding context between them.

A bot changes this. Instead of tracking sessions one by one, you hand off a whole responsibility. The bot owns the work, keeps its own notes, and brings back what matters.

This recipe walks through the design: what makes a good first bot, how to scope it, and how to set it up so it runs without constant steering.

## Pick a responsibility, not a task

A bot is not a one-shot task runner. It is a standing identity that accumulates memory around a job. Pick something that:

- **Repeats.** Not "fix this bug" but "triage incoming issues."
- **Carries context.** Decisions build on each other — a convention you settled, a dependency you ruled out, a pattern that worked.
- **Can run while you are away.** The bot should be able to move work forward between your messages.

Bad first bots:

- "Help me with this PR" — too narrow, no recurring context.
- "Do everything on my backlog" — too broad, no clear boundary.
- "Research new libraries" — no end state, no way to measure progress.

Good first bots:

| Bot | What it owns | Why it works |
|---|---|---|
| Issue triage | Reads new issues, labels them, flags duplicates, drafts repro steps for bugs | Repeats daily, learns your labeling conventions, has clear outputs |
| Build health | Checks CI every 30 minutes, sorts new failures from known flakes, surfaces what needs you | Repeats on a schedule, learns which failures are noise, stays out of your way when green |
| Code review | Checks each PR against decisions you made before — your error-handling pattern, dependencies you ruled out | Carries context across reviews, applies your standards consistently |
| Release readiness | Owns the checklist before each release — tests, notes, sign-off | Clear scope, measurable done state, repeats each cycle |

## Set boundaries first

Before you create the bot, write down:

1. **What it receives.** Where does work come from? A ticket queue, a PR list, a Slack channel?
2. **What it may do.** Comment on issues? Label them? Close them? Merge PRs? Less is better to start.
3. **What a useful handoff looks like.** When it brings something to you, what should be included?
4. **When it should ask.** What decisions must wait for you?

Start narrow. A triage bot that can only label and comment is safer than one that closes issues on its own. You can expand permissions later, one at a time, by approving the bot's capability requests.

## Steps

### 1. Create the bot

Open the Bots page in the dashboard. Press **Create your first Bot** or **New Bot** from the Add menu.

Give it a name that says what it does — `issue-triage`, not `helper-1`.

### 2. Set triggers

In Advanced settings, add trigger phrases that route work to this bot:

```text
new issue, incoming ticket, triage, label this, duplicate check
```

Triggers are how other agents know to hand work to this bot. Keep them specific to the job.

### 3. Give it a goal

When you create the bot, it opens its chat and asks what you want it to do. Tell it plainly:

```prompt
You triage incoming issues on the kirodotdev/KiroCrew repo. For each new issue:
- Label it (bug, feature, question, docs)
- Check if it duplicates an existing issue
- For bugs, draft reproduction steps
- For anything unclear, flag it for me

You can comment and label. You cannot close issues or assign them.
```

The bot proposes this as a goal card. Press it. Now the goal is recorded and the bot will refer back to it.

### 4. Set milestones

After the goal is set, the bot proposes milestones — measurable readings that show progress. For a triage bot:

- Issues triaged this week: target 20
- Duplicates caught: target 5
- Unlabeled issues in queue: target 0

Review what it proposes. Adjust if the targets do not fit your volume. Press the card to confirm.

### 5. Turn on the heartbeat

On the bot's Goals tab, find the check-ins section. Turn on **Heartbeat** and pick an interval:

- 30 minutes for a bot that should catch things fast (build health)
- 1 hour for most triage work
- 2–4 hours for slower queues

The heartbeat wakes the bot on schedule. It checks for new work, moves what it can, and only writes in the chat when something needs you.

### 6. Do a trial run

Send the bot a test:

```prompt
Triage the last 5 open issues on kirodotdev/KiroCrew.
```

Watch what it does. Check:

- Did it label correctly?
- Did it catch an obvious duplicate?
- Did it ask before doing anything outside its scope?

If something is wrong, correct it now. The correction becomes a lesson the bot keeps.

## What happens next

Once the bot is running:

- **It works while you are away.** The heartbeat moves things forward on schedule.
- **It learns from corrections.** Tell it "that was not a duplicate" and it adjusts its judgment.
- **It reports only what matters.** Quiet work lands on the Dashboard tab. Blocked work or questions come to the chat.
- **You check the Dashboard tab, not the transcript.** The tab shows what is in flight, what is done, and what needs you.

After a few cycles, tune it:

- Raise or lower the heartbeat interval based on volume.
- Add permissions if it needs them — each one is a card you approve.
- Adjust the goal or milestones as your process changes.

## Gotchas

- **Start with one bot.** Get one working well before you add a second. Two bots with overlapping triggers confuse routing.
- **Less permission is safer.** A bot that can only comment and label cannot break anything. Add merge rights only after it earns trust.
- **Correct mistakes immediately.** A bot that learns a wrong pattern spreads that pattern. Say what was wrong and what to do instead, right when you see it.
- **The heartbeat costs credits.** Each wake is a model turn. If the bot has nothing to do, it calls `nothing_to_do` and the wake is cheap. If it works every wake, you pay for it.
- **Triggers need overlap with your vocabulary.** If you say "look at this ticket" but the triggers only have "issue", routing misses. Add the words you actually use.

## What you learned

Pick a responsibility that repeats and carries context. Set boundaries before you create the bot. Give it a goal and milestones so it knows what success looks like. Turn on the heartbeat so it works between your messages. Correct mistakes early. Check the Dashboard tab to see where things stand.

One bot that handles triage well is worth more than five that each need constant steering.
