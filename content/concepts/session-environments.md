---
title: "Session Environments: run a session in a cloud workspace"
description: Run a chat session in a Coder, Fly.io Sprites or boxd workspace, with a remote Files panel, Git panel and terminal.
category: Concepts
difficulty: intermediate
time: 10 min
surfaces: [dashboard]
tags: [session-environments, remote, coder, sprites, boxd, preview]
updated: 2026-11-08
featured: false
prerequisites:
  - Kiro Crew 0.12.0 or later
  - A dashboard chat session
  - An account with Coder, Fly.io Sprites or boxd
---

A session normally works on the machine that runs the gateway. That is fine for a laptop project. It gets awkward when the code, the build tools and the credentials live in a cloud development environment, because you end up copying files back and forth or running the gateway inside the workspace.

Session Environments, a preview in 0.12.0, lets a chat session use a remote workspace as its environment. You pick the workspace in the composer, and the session's files, git state and shell come from that workspace.

## Turn it on

Session Environments is a Feature Preview, so it is off by default. Two things have to be true:

1. Turn it on under **Settings > Developer > Feature Previews**.
2. Start the gateway with `KIROCREW_DEV_MODE` set. Without it, the developer-only features stay off, even if the preview toggle is on.

## Connect a provider

Open **Settings > Session Environments** and connect a provider. Three are supported:

- Coder
- Fly.io Sprites
- boxd

Each connected workspace becomes something you can pick as an environment.

## What changes in the chat

- **Environment chip.** The composer shows a chip with the environment the session uses. Use it to choose a connected workspace for the session.
- **Remote Files panel.** The Files panel lists the files in the remote workspace, not on the gateway host.
- **Git panel.** The Git panel shows the branch and changes of the repository in the workspace.
- **Terminal.** The terminal opens a shell in the workspace.

Because all three read from the same workspace, what you see in Files, Git and the terminal agrees with what the session works on.

## When to use it

Use it when your development environment already lives in the cloud: a Coder workspace your team provisions, a Fly.io Sprite you keep for a project, or a boxd workspace with its tools preinstalled. The session works next to the code and the toolchain, and you do not sync a checkout to the gateway host.

If your project is on the same machine as the gateway, you do not need it.

## Verify

1. Confirm the preview toggle is on and the gateway was started with `KIROCREW_DEV_MODE` set.
2. Connect a provider under **Settings > Session Environments**.
3. In a new chat, pick the workspace from the environment chip in the composer.
4. Open the Files panel and check that it lists the workspace's files. Open the terminal and run `pwd` to confirm it is the remote shell.

## Gotchas

- **Nothing shows up without `KIROCREW_DEV_MODE`.** The preview toggle alone is not enough. Check the gateway's environment first when the settings page or the chip is missing.
- **It is a preview.** Behavior and settings can change between releases.
- **Credentials belong to the provider.** Connect the workspace under Session Environments rather than pasting provider tokens into a chat.

For how approvals work around commands run in a session, see [security](security.md). For how the pieces of Kiro Crew fit together, see [how-it-fits](how-it-fits.md).
