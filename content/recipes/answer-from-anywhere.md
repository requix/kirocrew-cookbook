---
title: Answer from anywhere
description: Answer a waiting approval or question from the sidebar, a chat app DM or a quieter dashboard, without opening the session.
category: Recipes
difficulty: intermediate
time: 15 min
surfaces: [dashboard]
tags: [notifications, approvals, slack, telegram, discord, webex, feishu, sidebar]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - For the chat app part, at least one chat app (Slack, Discord, Telegram, Webex or Feishu) already connected to your Kiro Crew
---

**Problem.** A session stops and waits for you. It wants approval for a tool call, or it asked a question and cannot continue without an answer. If you are in another session, or away from the dashboard, that session sits idle until you notice. This recipe sets up three ways to answer without going back to it: a quick reply card in the sidebar, a copy of the notification in your own chat app DM, and quieter sounds so you can leave the dashboard open all day.

## Steps

### 1. Answer from the sidebar

Rest the pointer on a session that waits on you, or select it and press the right arrow key. A card opens next to it. It shows:

- a **Recap** of what the session was doing,
- **Needs you**, with every pending approval and question in full, each tagged **Approval**, **Question**, **Form** or **Reply**,
- a reply box with the placeholder "Reply to this session…".

For an approval, click **Approve** or **Deny**. The card says what that means: "Approve lets the agent do this once. Deny skips it." Approve is a one-time grant for that call. For a plain reply, type in the box and press Enter. Shift+Enter starts a new line, and Esc closes the card.

A few cases behave differently:

- If the agent is still in the middle of a step, the card says "Queued. Sends when the agent finishes its current step."
- Typing into the box does not answer an approval. The card says "Replies go to the chat. Use Approve or Deny above."
- A session that a conductor runs shows "Decide this on the conductor's approval card." Use that card instead. See [Conductor mode](../concepts/conductor-mode.md).
- If someone else answered first, you get "Approved elsewhere" or "Denied elsewhere", and a late reply is not sent.
- Some asks cannot be answered from the card. It then says "Open the session in the list to answer."

If the card gets in your way, turn it off in **Settings → Chat → Sessions**. The switch is **Quick Reply Card on Hover**, and it is on by default.

### 2. Send the notification to your own DM

Go to **Settings → Notifications** and open **Sources**. Each row is a notification source. The row for approvals is described as "When an agent is stopped until you approve a tool it wants to use." The same page has rows for other sources, such as bot messages, app updates and chat errors.

Under a row you see **Deliver to** and a checkbox for each chat app. The row offers only apps that are connected right now. If you pick an app that later disconnects, it stays checked and reads "(unavailable)", so your choice is not lost.

The supported apps are Slack, Discord, Telegram, Webex, WeCom and Feishu. Tick the ones you want for that source. The note arrives in your own DM with the bot, not in a channel. Kiro Crew only sends it when it can tell which single person owns that DM.

Once at least one app is ticked, a priority menu appears. Its options are:

| Option | What reaches your DM |
|---|---|
| **Critical only** | Only critical notes. This is the default for a new route. |
| **Default and critical** | Critical and default priority. |
| **Every priority** | Everything, including passive notes. |

Approvals are critical by default, so **Critical only** is enough for them. Keep it that way on the busier sources, otherwise your DM turns into a second notification feed.

Unticking every app removes the route and resets the priority menu with it.

Feishu needs one extra condition. Notes go only while exactly one `open_id` is in `allowed_open_ids`, because that is how the gateway knows the DM is yours.

Try it below. Pick a note, its priority and where it may go, and see where it lands.

```widget note-router
```

### 3. Mute sounds when you need quiet

On the same **Notifications** page, the sound section has a **Mute sounds** menu. It silences notification sounds for a while and then turns them back on by itself. Notifications still arrive, so the sidebar card and your DM keep working. Pick **For 1 hour**, **For 2 hours**, or the last choice, which reads "Until" followed by a time (the morning). While it is active the menu reads "Muted until" followed by the time, and **Off** ends it early.

This is separate from muting a source in **Sources**. A muted source "stays in history but never badges, sounds, or banners".

### 4. Optional preview: answer approvals in the chat app

Step 2 alone carries the notes that Kiro Crew already sends. A tool approval is not one of them by default. To get one, turn on a preview.

> **Preview.** This feature is off by default and may change. It lives under **Settings → Developer → Feature Previews**.

Turn on **Send pending approvals to chat apps**. Then, when a tool approval opens, Kiro Crew sends a note about it to the chat apps your approvals source delivers to. The dashboard bell does not ring for it. Make sure the approvals row from step 2 has an app ticked, or there is nowhere for the note to go.

How you answer depends on the app:

- **Slack:** the note has **Approve** and **Deny** buttons.
- **Telegram, Discord and Webex:** reply to the note with `approve` or `deny`. Only that exact word works, and only for that one request. A reply cannot grant a whole session.
- **Feishu:** you get the note, but you answer in the dashboard.

A single-choice question card gets one button per option in Slack. On Telegram, Discord and Webex you reply with the number of the option.

Only you can answer. The sender has to be the owner of that DM, and a reply from anyone else changes nothing. If the request was already answered or has expired, the bot says so.

The hint under the switch in the dashboard still says the note "has no buttons yet". The 0.13.0 release notes and the bridge code describe the buttons and reply answers above, so treat that hint as out of date. If you do not see buttons in Slack, answer from the dashboard and check the app's connection in step 2.

### 5. Verify it worked

1. Start a session that needs approval, then switch to a different session.
2. Check that the waiting session shows the quick reply card when you rest on it, and that **Approve** answers it.
3. If you set up a DM route, repeat the test with the dashboard closed and check that the note arrives in your chat app at your chosen priority.
4. If you turned on the preview, answer the approval from Slack or from a reply, and check that the session continues.

## What can go wrong

**Problem:** The card never opens.

**Fix:** Check that **Quick Reply Card on Hover** is on under **Settings → Chat → Sessions**. The card only appears for a session that is waiting on you, so a session that is merely running shows nothing.

**Problem:** **Deliver to** is missing from a row.

**Fix:** The row shows only apps that are connected and that the notification bridge can deliver to. Connect the chat app first, then come back.

**Problem:** You ticked an app and nothing arrives.

**Fix:** Look at the priority menu. With **Critical only**, a default or passive note stays in the dashboard. Raise it for that row, or change the source's own priority.

**Problem:** Approvals reach your DM only after you turn on the preview, and you expected them earlier.

**Fix:** That is the intended behavior. Without **Send pending approvals to chat apps**, a waiting tool approval is not sent to chat apps.
