---
title: What's new in 0.12
description: A quick scan of what changed in Kiro Crew 0.12, with links to the pages that cover each piece.
category: Getting started
difficulty: beginner
time: 5 min
surfaces: [dashboard, cli]
tags: [release, upgrade, whats-new]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later
---

**Problem.** You upgraded to 0.12 and the dashboard looks different. You want to know what moved and what is new.

Scan the list below and follow the links for the parts you use.

## Generally available

### Bots
Bots no longer sit behind a preview switch. Each Bot now has a work ledger that records what it is doing and what it tried, so it can pick up after a restart. A Bot can work in its own git worktree, and you can export a Bot and import it on another machine.

See Bots: agents with their own job and Design your first Bot.

### Live browser with takeover
The agent's browser appears in your chat while it works. When a page needs a sign-in or a CAPTCHA, you take over, finish the step and hand it back. The agent never types your password.

See Browser: watch the agent work a page and Let it browse.

### More harnesses
Kiro CLI is no longer the only harness. Strands and Copilot CLI are available, and each Bot can pick its own.

See [What Kiro Crew actually is](../concepts/what-kirocrew-is.md).

### New connections
Google Workspace (Gmail, Drive, Calendar, Sheets, Docs, Slides) and Bedrock Knowledge Bases connect from the dashboard.

See Connect Google Workspace and Add a Bedrock knowledge base.

### Sidebar
You can pin sessions, resume them where you left off, and give them colors, which makes a long list easier to scan.

### Push notifications when closed
Notifications reach you even when the dashboard tab is closed.

### Apps in chat
Apps are available from the + menu in the composer and from message actions. See [What apps are](../apps/what-apps-are.md).

### Lighter and faster
The dashboard and gateway are lighter and start faster.

## Previews

These are behind Feature Previews in Settings. Turn one on when you want to try it, and expect rough edges.

- **Ultra Mode.** An opt-in mode for demanding tasks.
- **Session Environments.** Give a session its own environment.
- **Shared Crew.** Work on a crew together with other people.

## After you upgrade

Run `kirocrew doctor` to check your install. Then open [Your first hour](first-hour.md) if you want a fresh walkthrough, or [How it fits together](../concepts/how-it-fits.md) for the big picture.
