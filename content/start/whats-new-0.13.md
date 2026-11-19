---
title: What's new in 0.13
description: A quick scan of what changed in Kiro Crew 0.13, with links to the pages that cover each piece.
category: Start
difficulty: beginner
time: 6 min
surfaces: [dashboard, cli]
tags: [release, upgrade, whats-new]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
---

**Problem.** You upgraded to 0.13 and some settings moved, some defaults changed, and a few things you used to turn on are just there. You want to know which ones matter for you.

Scan the list below and follow the links for the parts you use. The full list is in the release notes, which now live under **Settings → About**.

## Generally available

### Conductor mode
Conductor mode, called Ultra Mode in 0.12, left Feature Previews and needs nothing turned on. A new chat's composer offers the switch, and an ongoing chat offers it to the right of the permission button. Its chats run on the `kirocrew-conductor` agent unless `agent.crew_mode_agent` names another. If you want every new chat to start in it, turn on **Settings → Chat → Sessions → Start New Chats in conductor mode** (off by default).

The conductor now plans from the goal, tests the plan before it starts, and checks each worker's new work for drift on every patrol. On the Board, Pause all stops every running worker, sub-teams included, until Resume all.

See [Conductor mode: a chat that runs a crew](../concepts/conductor-mode.md).

### Answer from anywhere
A session that waits on you no longer needs a trip into the chat. Rest the pointer on it in the sidebar, or press the right arrow key, and a card opens with its recap, every approval and question in full, and a quick reply box. **Settings → Chat → Sessions → Quick Reply Card on Hover** turns the hover behavior off.

Under **Settings → Notifications → Sources**, each source row also gains Deliver to, which sends its notes to your own Slack, Discord, Telegram, Webex or Feishu DM while that channel is connected. Only critical notes go by default, unless you lower the floor.

See the [answer from anywhere recipe](../recipes/answer-from-anywhere.md).

### Updates you can see coming
When a newer version is announced, **Settings → About** shows an Upcoming update block with its version, expected date and highlights. About also holds the release notes that used to have their own Releases page. In the desktop app it adds Restart gateway, which restarts the local gateway without updating.

### Chat that works your way
- Cmd+Shift+T (Ctrl+Shift+T, or Alt+Shift+T in a browser tab) reopens the session you closed last.
- `/fork <prompt>` continues in a copy of the conversation. A reply's More menu adds Fork with another model.
- **Settings → Chat → Composer → Optimize Before Sending** rewrites your message on Send and leaves it for you to check.
- **Settings → Chat → Transcript → Preferred Reply Language** sets the language of replies. Code, commits and pull request text keep the project's language.
- A usage limit error card says when the limit resets and offers Continue automatically after that time.

### Files and Git panels
The side panel's Files tab now opens on Edited, the files this chat created or changed, newest first, each with Show changes. Browse walks the project folder. The Git panel adds Branch changes, which shows everything the branch changed since its base.

### Connections and MCP servers
**Settings → Connections** now holds every provider card, and the six Google products share one Google entry and one OAuth app. MCP servers moved to their own MCP Servers tab under Customize, next to Skills. Each tool in a server's tool list gains an Always allow toggle, so one MCP tool can stop asking for approval without trusting the whole server.

See [Connect Google Workspace](../recipes/connect-google-workspace.md).

### Settings → Advanced
**Settings → Advanced** lists every config key. A setting with no control of its own can be changed there without editing `config.json`. Keys about the sandbox, approvals, sign-in and channels show read only.

### Bots choose their harness
The Agent harness row on a Bot's profile left preview. It lists only the harnesses Bots can run on here, and Inherited follows **Settings → Agent Harness**. See [Bots](../concepts/bots.md).

### Slack code channels
With `slack.code_channels` on, a code channel on a git repository runs in its own worktree with a diff view and a context bar. The Slack panel in Settings gains Reconnect, which applies new tokens without a gateway restart.

See the [Slack code channels recipe](../recipes/slack-code-channels.md).

## Safety and control

### Outside edits to config wait for review
On a Linux host with the sandbox, a change to `config.json`, `config.local.json`, `denied_commands.json` or `computer_use.json` that Kiro Crew did not write no longer applies by itself. A bell note leads to a card in **Settings → Security** that lists each changed key to Apply or Discard. A gateway without the dashboard uses `kirocrew config pending apply` or `kirocrew config pending discard`.

### Read-only folders
`agent.sandbox_readonly_paths` lists folders the sandboxed agent may read but never write. `agent.sandbox_readonly_exceptions` keeps chosen folders inside them writable. The OS sandbox enforces both on Linux and macOS.

See the [fence the agent recipe](../recipes/fence-the-agent.md) and [Security](../concepts/security.md).

### Traces
Set `telemetry.traces_enabled` (off by default) to record one trace per agent turn. A trace holds the model, tokens and tool calls, but never their text. `kirocrew trace show` prints one turn as a waterfall from the local span files.

See the [trace agent turns recipe](../recipes/trace-agent-turns.md).

## Usage data is now on by default

Local usage metrics are recorded on this machine within disk caps. They cover how long things take and how often features are used, and they hold no prompts, files or credentials. The public build also sends a reviewed list of product metrics to Kiro telemetry, but only after the first-run Privacy chapter or a terminal notice has named it.

To turn it off, use any one of these:

- **Settings → Privacy**
- `kirocrew telemetry disable`
- `telemetry.enabled: false` in your config
- the environment variable `KIROCREW_TELEMETRY=0` or `DO_NOT_TRACK=1`

## Previews

These are behind **Settings → Developer → Feature Previews**. Turn one on when you want to try it, and expect rough edges. For how previews work, see [Previews](../previews/index.md).

- **Kiro Cloud Sessions.** A KAS chat runs in its own cloud sandbox. This one also needs `KIROCREW_DEV_MODE`, and its profiles live under **Settings → Session Environments**.
- **Agent Harness for worker chats.** A main chat starts each worker chat on another harness such as Claude or Codex.
- **GitHub sign-in by Kiro Crew.** Kiro Crew holds the sign-in itself for GitHub and other connections.
- **Secrets vault redesign.** Settings → Secrets becomes a list with a detail pane that also holds logins and notes.

## After you upgrade

Run `kirocrew doctor` to check your install. Then open [Your first hour](first-hour.md) for a fresh walkthrough, or [How it fits together](../concepts/how-it-fits.md) for the big picture.
