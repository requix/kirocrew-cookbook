---
title: Slack code channels
description: Give each coding task its own Slack channel and git worktree, then pick its agent and approval mode.
category: Recipes
difficulty: intermediate
time: 20 min
surfaces: [dashboard, channels]
tags: [slack, code-channels, worktree, approval-mode, agents]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - Slack already connected to Kiro Crew
  - A git repository on the machine that runs Kiro Crew
---

**Problem.** A coding task in a shared DM thread gets buried. You lose the branch name, the state of the pull request and what the agent changed. A code channel gives each task its own Slack channel. The channel is one Kiro Crew session, and it works in its own git worktree, so two tasks on the same repository do not step on each other's files.

This recipe turns the feature on, sets sensible defaults, and covers the controls you use once a channel exists. It assumes Slack is connected already. If it is not, finish that first with the [Slack integration doc](https://github.com/kirodotdev/KiroCrew/blob/v0.13.0/src/kiro_crew/docs/slack-integration.md).

## What you get

With `slack.code_channels` on, the agent can open a code channel for a coding task. Slack is rolling code channels out gradually, so your workspace may not have them yet.

- **One worktree per channel.** If the session's project is a git repository, Kiro Crew cuts a worktree on a branch named `slack/<slug>-<hash>` from the repository's default branch and points the session at it. A project that is not a repository gets no worktree and no error.
- **A diff tab.** The channel's Code tab shows what changed in the worktree. It is refreshed at the end of each turn, and only when it changed.
- **A context bar.** It shows the repo, the branch, the pull request and its CI state when they exist. The agent can add its own items after those.
- **A dashboard badge.** The channel's session in the dashboard carries a **Slack code channel** badge that opens the channel in Slack. Messages in the channel and in the dashboard session are one conversation.

## Steps

### 1. Turn on Code channels

Open **Settings → Messaging Channels → Slack** and find the **Slack Code** section. Switch on **Code channels**. It is off by default and applies without a restart. In config terms this is `slack.code_channels`.

The switch adds five scopes to the generated app manifest: `code_channels:manage`, `chat:write.customize`, `canvases:write`, `channels:write.invites` and `groups:write.invites`. Slack grants scopes only when the app is installed, so the switch does nothing until your installed app has them. Until then Slack works as before, and the page says why under the switch.

### 2. Update your Slack app

The **Update your Slack app** panel in the same section compares the scopes your installed app holds with what the switches need. It reads one of **Up to date**, **Needs update**, **Workspace not enabled**, **Cannot check yet** and a few token states. If it reads **Needs update**:

1. Copy the manifest from the panel. `kirocrew manifest` prints the same text.
2. Open your app's App Manifest page in Slack (the panel links it), replace the YAML and select **Save Changes**.
3. Reinstall the app when Slack asks.
4. Select **Check again**. The status should read **Up to date**.

If the status reads **Workspace not enabled**, the app is fine. A Slack workspace admin has to enable code channels, and then you select **Check again**.

### 3. Set the defaults

Under **New code channels start with**, you can set a default folder, agent, model, reasoning effort and approval mode. Anything you leave empty falls through to the folder's setting, then to the agent Slack already uses. A preview below the fields shows what a new code channel will run with.

If you set nothing, a top-level **Code channels** folder is created the first time it is needed, with `kirocrew-conductor` as its default agent. A code channel with no defaults runs the conductor. The agent list offers every agent a chat can run, minus the background-only ones (`kirocrew-lite`, `kirocrew-guest`, `kirocrew-heartbeat`).

The approval mode has three values. They are stored as `ask`, `trust_reads` and `trust` in `slack.code_channel_defaults.approval_mode`, and the page labels them **Normal**, **Reads** and **Trust**.

| Mode | What runs without asking |
|---|---|
| Normal | Look-ups such as file reads, web searches and read-only shell commands. Everything else waits for approval. |
| Reads | The same, plus searches of memory, past chats, skills and the knowledge library. |
| Trust | Every tool. |

Trust means anyone allowed to talk to the bot in the channel drives an agent whose tools run unprompted, and sessions it starts inherit that. Slack access is owner-only, so that is you in practice, but pick Trust on purpose.

### 4. Open a code channel

Ask the agent for one in a message to the bot.

```prompt
Open a code channel for fixing the flaky retry test in my payments repo.
```

The channel gets a kickoff message. Two controls on it matter:

- **An agent picker**, preselected with the agent the session runs.
- **An Approval mode menu**, shown to the channel's owner.

Both change the session that is already running, so you do not need to reopen the channel.

### 5. Change agent or approval mode later

In the channel, use the slash command you set up for the app (`kirocrew` by default):

```text
/kirocrew agent
/kirocrew agent <name>
/kirocrew approval normal
/kirocrew approval reads
/kirocrew approval trust
```

A bare `/kirocrew agent` lists the agents you can choose. Only the owner can change either setting. An agent switch never interrupts a running turn. If one is running, the switch is refused and you try again after it ends. A tool-approval card in the channel also has a **Trust this channel** button that approves that call and moves the channel to Trust.

A channel answers three more commands: `/summarize`, `/wrap-up` and, when the repository has a GitHub remote and `gh` is signed in, `/create-pr`. `/wrap-up` posts a summary with an **Archive channel** button that only a person can press.

### 6. Optional: let the channel start helper agents

In the **Slack Code** section, switch on **Let code channels start helper agents** (`slack.code_channel_dispatch`). It is off by default and needs **Code channels** on as well.

With it on, the channel's own session can start worker sessions and follow their status. Workers are filed in the channel's folder and work with the channel's approval mode, never a wider one. They ask before changing files unless the channel is on Trust. This only applies to turns you started yourself, and only one level deep.

## Resume after a gateway restart

A channel's binding survives a restart, so your next message still reaches the same session. Work that was mid-turn is picked up automatically, once. The channel shows one message:

- **I resumed where I left off**, with a **Stop** button. It stops the work the restart resumed.
- **Kiro Crew restarted while I was working.**, with a **Resume** button, when the turn could not be resumed on its own. For example, it had already restarted once. Only you can press it.

A turn is resumed automatically only once. A turn that takes the gateway down cannot loop.

## Reconnect in the Slack panel

Tokens and the owner ID you save in the Slack panel apply when you click **Reconnect**, with no gateway restart. A changed owner ID, or a token for a different workspace, is refused there and still needs a restart.
## Verify

- **Update your Slack app** reads **Up to date**.
- A new code channel shows a context bar with the repo and branch, and its Code tab shows a diff after the agent edits a file.
- The session in the dashboard carries the **Slack code channel** badge.
- `/kirocrew approval reads` in the channel is answered with the new mode, and the kickoff menu shows **Reads**.

## Gotchas

- **Nothing happens after turning the switch on.** The installed app is missing the scopes, or Slack has not enabled code channels for the workspace. Read the status in **Update your Slack app**.
- **No diff tab and no branch.** The session's project is not a git repository, or git refused to open it. The channel still works without a worktree.
- **`/create-pr` is missing.** The repository has no GitHub remote Kiro Crew may reach, or `gh` is not signed in.
- **The agent switch is refused.** A turn is running. Wait for it to finish, or stop it.
- **A setting disappeared.** A folder or agent deleted after you saved it is flagged on the page and skipped. The other defaults still apply.

## What you learned

`slack.code_channels` gives each coding task a channel with its own worktree, diff tab and context bar. The defaults card sets the folder, agent and approval mode for new channels, `/kirocrew agent` and `/kirocrew approval` change them afterwards, and **Let code channels start helper agents** is a separate switch. A restart resumes interrupted work by itself, and **Reconnect** applies new Slack tokens without one.
