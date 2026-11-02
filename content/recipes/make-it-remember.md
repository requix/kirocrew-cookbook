---
title: Make it remember
description: Teach rules and facts, keep tickets out, and fix stale memory before it spreads.
category: Memory
difficulty: beginner
time: 15 min
surfaces: [dashboard, cli]
tags: [memory, lessons]
updated: 2026-10-29
featured: false
prerequisites:
  - Kiro Crew running (see Your first hour)
---

**Problem.** You told the agent something yesterday. Today it forgot. Or worse: it remembered the wrong thing and now repeats a stale fact. Memory is Kiro Crew's headline feature, and it is the one people set up wrong.

This recipe shows what to teach it, how, and what to keep out.

## The one rule

**Memory is not a notepad.** You do not dump everything in. You teach it two kinds of thing:

- **Rules** — "always do X", "never do Y". These change how it behaves forever.
- **Facts** — stable truths about you and your work. Your stack, your conventions, your projects.

Everything else — a ticket number, today's bug, a one-off path — does **not** belong in memory. It ages into noise and makes every future answer worse.

## Two memory tiers

Kiro Crew has two memory stores. Know which one you are in.

| Tier | Who has it | Shared across sessions? |
|---|---|---|
| Global | The default agent and plain sessions | Yes — all plain sessions share it |
| Private | A crew member you create | No — only that member's sessions |

For most people starting out: you are on **Global**. Everything you teach the default agent is shared by every default session. That is usually what you want.

## Steps

### 1. Teach it a rule

Just say it in plain words, with "always" or "never":

```prompt
Always use SSH for git remotes, never HTTPS.
```

The agent saves it as a **lesson** right then. Lessons are the "always/never" kind — they come back in future sessions, even unrelated ones.

### 2. Teach it a fact

Same thing — just tell it:

```prompt
Remember: my main project is the az-pet Terraform modules, and we own the cloud and infra, not the application.
```

It stores this as a fact. Facts come back when the topic is relevant.

### 3. Ask it what it knows

To check, just ask:

```prompt
What do you remember about my git preferences?
```

It reads its memory and tells you. If a rule is wrong or stale, say so and it removes it.

### 4. Fix a wrong memory

```prompt
Forget the rule about using HTTPS for git. The correct rule is SSH only.
```

It drops the bad lesson. Do this the moment you spot drift — stale rules are worse than none.

## Verify

- Start a **new** session. Ask it a question that needs the rule. It should follow the rule without being told again.
- Ask "what do you remember about X". The answer should be right and short — not a pile of old junk.

## Gotchas

- **Do not save tickets or today's bug.** "Fix JIRA-412" is not a rule. It is noise next week. Memory is for things that stay true.
- **A rule and a fact are different.** "Always sign commits" is a rule (behavior). "My repo is at /home/me/app" is a fact. Both are fine; keep them as what they are.
- **Private member memory does not reach the default agent.** If you made a crew member, what you taught *it* stays with *it*. The default agent will not know.
- **Some sessions learn nothing on purpose.** Incognito and temporary sessions keep their transcript for you but save no memory or lessons. Use them when you do *not* want the agent to remember.
- **Say "always/never" to make a rule stick.** Vague phrasing may be stored as a weaker fact. Be blunt: "always", "never", "remember".

## What you learned

Teach rules and facts, not tickets. Check with "what do you remember". Fix drift the moment you see it. Keep memory small and true, and every future session starts smarter.
