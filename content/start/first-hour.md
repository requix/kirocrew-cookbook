---
title: Your first hour
description: Install Kiro Crew, open the dashboard and get one real task done.
category: Getting started
difficulty: beginner
time: 60 min
surfaces: [dashboard, cli]
tags: [install, dashboard, doctor]
updated: 2026-10-29
featured: true
prerequisites:
  - Linux or macOS (Windows has its own install guide)
  - kiro-cli installed and on your PATH
  - A Kiro login that works in kiro-cli
---

**Problem.** You installed nothing yet, or you installed it and the dashboard is a wall of panels. You want one real task done, fast.

This gets you from zero to a first useful result.

## Steps

### 1. Log in to kiro-cli

Kiro Crew drives `kiro-cli`. No `kiro-cli`, no agent. Make sure it is logged in:

```bash
kiro-cli login
```

You do not need to install Python. The installer in the next step brings its own Python 3.12.

### 2. Install Kiro Crew

One line. It fetches a signed, verified build. No clone, no npm.

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
```

This puts `kirocrew` on your `PATH`. Then run the first-time setup once. It installs the agent config and asks for your workspace folder, timezone and dashboard URL:

```bash
kirocrew setup
```

For every install option, Windows, and what the installer writes where, see [Install Kiro Crew step by step](install.md).

### 3. Start the gateway

```bash
kirocrew gateway
```

The gateway is the one process that runs everything. Leave it running.

### 4. Open the dashboard

In your browser:

```text
http://localhost:5476
```

If `kiro-cli` is missing or not logged in, the first run shows a **Set up Kiro** page. It gives you the exact commands to fix it. Run them, then reload.

### 5. Send one real task

Do not test it with "hello". Give it something true and small from your own work. Example:

```prompt
Read package.json in this project and list every dependency that is a major version behind.
```

Watch it read the file and answer. That is the loop: you ask, it uses tools, it answers.

### 6. Point it at your project

A dashboard session works in one directory. To aim it at your repo, tell it in chat:

```prompt
Work in /home/me/projects/my-app from now on.
```

Now its file search, edits and commands default to that repo.

## Verify

You are set up when all three are true:

- `kirocrew doctor` shows no problems.
- The dashboard loads at `localhost:5476`.
- Your first task came back with a real answer, not an error.

```bash
kirocrew doctor
```

`doctor` walks through your setup section by section: the `kiro-cli` binary and login, config, MCP servers, memory and connectivity. It is your first stop for any "it won't start" problem.

## Gotchas

- **`kiro-cli not found in PATH`.** The binary is not installed or not on `PATH`. Install it, open a new shell, try again.
- **Dashboard won't load.** The gateway is not running. Start `kirocrew gateway` and keep that terminal open.
- **It answers but can't see your files.** It is working in the wrong directory. Tell it which folder to work in (step 6).
- **Port 5476 is taken.** Something else already listens there, often a second gateway. Start with `kirocrew gateway --port auto` to take a free port, or set `KIROCREW_PORT`.

## What you learned

Log in → install → gateway → dashboard → first task → point at a project. That is the whole first hour. Everything else builds on this.
