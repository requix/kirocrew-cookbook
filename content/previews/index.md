---
title: Preview Features
description: Features you can turn on early. They may change before they go GA.
category: Previews
difficulty: beginner
time: 5 min
surfaces: [dashboard]
tags: [previews, feature-previews, beta]
updated: 2026-11-08
featured: false
---

Preview features are finished enough to use but not yet stable. They ship off by default, and you turn each one on in **Settings → Developer → Feature Previews**. Expect changes between releases — the UI, the behavior, and sometimes the whole approach can shift before a feature goes GA.

## What's in preview now

| Feature | What it does | Since |
|---------|--------------|-------|
| [Ultra Mode](ultra-mode.md) | A chat that hands tasks to worker chats, with a Board tab to see what's running | 0.12.0 |
| [Session Environments](session-environments.md) | Run a session in a Coder, Fly.io or boxd workspace instead of the gateway machine | 0.12.0 |
| Shared Crew | Share the gateway over Tailscale with teammates | 0.12.0 |
| Remote dispatch | Let Ultra Mode run tasks on machines connected via Remote Crew | 0.12.0 |

## How to turn one on

1. Open **Settings → Developer → Feature Previews**.
2. Find the feature and turn on its switch.
3. The change takes effect immediately — no restart.

Some previews need more than a switch. Session Environments, for example, also needs `KIROCREW_DEV_MODE` set in the gateway's environment and an account with a supported workspace provider.

## What "preview" means

- **It works.** The feature is not a stub. You can use it for real work.
- **It may change.** The team can rename things, move controls, change defaults, or rethink the design between releases.
- **Feedback matters.** The preview period is when the team wants to hear what's awkward, missing, or broken. Use the **Request a Feature** button in the top bar.
- **It will graduate or be dropped.** A preview either becomes GA (and the switch goes away) or is removed. Nothing stays in preview forever.

## See also

- [What's new in 0.12](../start/whats-new-0.12.md) — the release that added most of these previews
