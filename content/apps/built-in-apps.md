---
title: "A tour of the built-in apps"
description: What each of the 24 apps that ship with KiroCrew does, what it needs, and which to turn on first.
category: Apps
difficulty: beginner
time: 15 min
surfaces: [dashboard, cli]
tags: [apps, app-store, built-in, setup, getting-started]
updated: 2026-10-30
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
---

KiroCrew ships with 24 apps. An app adds something to your surface: a dashboard page, extra MCP tools, skills, a cron or two, sometimes a specialist agent. Most arrive installed but switched off, so the store is a menu you opt into rather than a pile of pages you have to clear away. This page walks the whole set grouped by the job it does, tells you what each one needs before it is any use, and names a few worth turning on first. For what an app _is_ under the hood, see [What apps are](./what-apps-are.md); to build one, see [Build your own app](./build-your-own-app.md).

Two things to read off every table. **On by default** means the app is live the moment KiroCrew starts; everything else you enable yourself. The **Needs** column is the real cost of turning it on — a CLI on the host, a cloud account, the desktop build, a compiler — pulled from each app's manifest. An app with no entry there runs with nothing but the gateway itself.

Only two apps are on out of the box: **Task Runner** and **Command Bar**. Every other app in this tour starts disabled.

## Everyday dashboard tools

These are the low-friction ones: no accounts, mostly read-only, useful from the first session.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Command Bar** | `command-bar` | Replaces Cmd+K / Ctrl+K quick-search with a command launcher: type a command instead of a query. While it is on, searching knowledge, skills and prompts from that surface is off — disable it to get that back. | — | Yes |
| **Task Runner** | `projects` | Hand over a multi-step job and let it run unattended. Describe the work, paste a spec, or upload YAML; generate a plan to review first or start straight away. Pause, resume, retry or stop a run on its own page. | — | Yes |
| **Files** | `file-explorer` | Browse and read files on the gateway host without leaving the dashboard — tabs, a tree with inline git status, folder search, rendered markdown. Read-only by design and confined to your home dir, the temp dir, and `/home`, `/opt`, `/workplace` on Linux and macOS. | — (git and ripgrep only add optional status and search) | No |
| **Notes** | `md-notebook` | A markdown notebook backed by a git repo, so notes are versioned and portable. Clone a GitHub repo as a vault or attach an existing folder (an Obsidian vault works) without a second copy. Wikilinks, backlinks, full-text search, one-step sync; optionally index the vault into Knowledge. | git; a private GitHub clone needs a PAT or authenticated `gh` | No |
| **Create Folders From Project** | `project-scaffolder` | Point it at a project directory and it works out the sub-projects inside, then creates a matching sidebar folder for each. The scan is read-only, so you tick what you want before anything is created and existing folders are never duplicated. | — | No |

## Code and pull-request work

The engineer's shelf. All of these reach a forge, so most want an authenticated provider CLI on the **gateway host** — the machine running KiroCrew, not your laptop, if those differ.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Code Review Sage** | `code-review-sage` | Deep-reviews GitHub pull requests and ranks the changed files by blast radius into a Focus Report. Each PR gets its own isolated agent session, and nothing is posted to the PR unless you publish it or turn on auto-posting. Learns your repo's real standards from shipped fixes and past comments. | Authenticated `gh` CLI on the gateway host; network | No |
| **Issue Radar** | `issue-radar` | Triage GitHub issues, GitLab issues and Azure DevOps work items with AI-suggested labels and per-item notes, kept in a local ledger so nothing is re-investigated. Can act on a PR in place — approve, request changes, merge, close, re-run CI — pinned to the commit you were shown, and only with triage/push access. | An authenticated CLI for the provider you connect: `gh`, `glab`, or `az`; network | No |
| **Spec Builder** | `spec-builder` | Spec-driven development inside KiroCrew: turn a feature idea into Requirements → Design → Tasks with an embedded agent, review the markdown in-app, approve each stage, then hand the plan to an autonomous build session. Can open a fresh worktree for the work. | — (a project folder; optionally a git worktree) | No |
| **Design Tweak** | `design-tweak` | Visually select elements in your live app preview and turn them into scoped, source-mapped edit requests for the agent — Figma-style comments, but for code. Load a local web project, start its dev server, switch to Edit mode. | A local web project with a dev server | No |
| **Design Critique** | `design-critique` | A design critique you can run before asking a colleague. Give it a screenshot, a multi-screen flow, a Figma file, a repo or a running URL; it finds the screens, measures contrast and hit-targets from the rendered page, and reports findings tied to named heuristics (Nielsen, WCAG, Gestalt, Fitts). | Downloads a headless browser into a home-dir cache on first use; a private GitHub source may need `gh auth login` | No |

## Planning and long-running work

Work you set up once and let run — campaigns, autonomous cycles, orchestrated phases.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Research Lab** | `auto-research` | Runs multi-cycle research campaigns that keep working after you leave. Expands one broad question into a tree of sub-questions, sends agents to investigate each, and streams findings live. Attended mode pauses for a decision; unattended runs straight through. Export the report to Knowledge or an artifact. | Network | No |
| **Auto-Improvement** | `auto-improvement` | Measures a GitHub repo before it changes it: designs a calibrated metric, proves the metric against a known win, then runs keep-or-revert cycles where each candidate fix lands in an isolated worktree, gated by the repo's tests. Survivors are drafted as PRs you review — draft-only, never merged for you. | git and an authenticated `gh` CLI on the gateway host; network | No |
| **Workflows** | `workflows` | Author, run and watch dynamic workflows: sandboxed Python scripts, usually written for you from a plain-English goal, that drive several agents through ordered phases. A script is validated before anything executes, then the page streams each phase. Hidden from the store (see below). | — (packaged installs ship no example scripts) | No (hidden) |

## Cloud and ops

The on-call and infrastructure shelf. These touch live accounts, so each has its own confirmation gates.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **AWS Control** | `aws-control` | Your AWS accounts in plain language: a health light per account with reconnect guidance, plus an S3-backed cloud drive — files, a cloud artifact library, backups — with time-boxed share links. Nothing is public unless you say so, and every paid service confirms per account before it can bill you. | AWS credentials configured on the host; network | No |
| **Ops Mission Control** | `ops-mission-control` | An autonomous ops first responder. Watches alarms, pages and monitors; claims what fires; investigates with real context; proposes a fix — and keeps what it learns in a local ledger so the second occurrence is faster. Read-only by default; write actions are opt-in per signal pattern and audited. | Network; optionally the `aws` and `gh` CLIs; a provider (CloudWatch, PagerDuty, Datadog, incident.io, GitHub Issues); Slack output reuses an existing connection | No |
| **Dev Fleet** | `dev-fleet` | A control panel for working on KiroCrew itself: lists every feature worktree with PR state, commit count and disk usage, and brings any up as an isolated preview pod on its own port and data dir. Note that enabling it lets agent sessions start and stop pods, so worktree code runs outside the agent's sandbox, as you. Built for people developing KiroCrew, not everyday use. | Authenticated `gh` for PR actions; pods need systemd `--user` (Linux) or launchd (macOS); terminal access | No |

## Research, docs and media

Making things — papers, decks, meeting notes.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Papyrus** | `papyrus` | A LaTeX paper editor with live PDF preview and an AI co-author. Split-pane editor, compile on save, clickable error list, clone-commit-push from the toolbar. The co-author panel is a real KiroCrew chat scoped to the paper. Never runs the compiler with shell escape. | A TeX compiler — `pdflatex` or `tectonic` on PATH, or one click installs a managed Tectonic into Papyrus's own folder; git for clones; network | No |
| **PPTX Maker** | `pptx-maker` | Describe the deck in chat and get a real `.pptx`. An agent interviews you, writes a brief, outline and art direction, then composes every slide — rendered as animated SVG in a live preview as they build. Reusable styles and `.pptx` templates re-skin the same content. | Fetches a pinned engine on first use; network; optionally `soffice` (LibreOffice) and `pdftoppm` for broader previews | No |
| **Meetings** | `meetings` | An AI meeting assistant. Transcribes a live meeting through KiroCrew's own speech-to-text, keeps structured notes and a diagram, extracts action items, and lets you review them before filing. Ships a local task ledger and an iCalendar reader. | Browser microphone access; network; optionally an iCalendar path/URL | No |
| **Personal Shopper** | `personal-shopper` | A personal advisor that researches real stores and helps solve a problem that may or may not end in a purchase. It has no way to reach a cart or checkout — it researches only the stores you name and flags that prices come from public pages. | Network | No |

## Multi-agent

Several agents working one problem together, in the open.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Channels** | `channels` | A shared room where role-assigned agents work a problem together in one readable transcript. There is no private agent-to-agent messaging, and you stay the approver for anything that changes state. Hidden from the store (see below). | — | No (hidden) |

## Companions and fun

Ambient and desktop-companion apps. Two of these need the KiroCrew **Desktop** build to float a window on your screen.

| App | id | What it does | Needs | On by default |
|---|---|---|---|---|
| **Crew Companion** | `crew-companion` | A desktop companion that paces your day: break nudges on an interval you choose, plain-language reminders, a short breathing exercise, and a heads-up when a session finishes, fails, or needs your OK. | KiroCrew Desktop; network | No |
| **Mochi** | `mochi` | A desktop pet that floats on your screen — chats through its own panel, watches pages and feeds, plans its own day around your schedule, and taps you only when something changed. The autonomous core runs in-process, no second app. | KiroCrew Desktop; schedule-aware planning needs a connected calendar MCP tool | No |
| **Agent Worlds** | `agent-worlds` | Turns your running agents into characters in an animated pixel-art scene, so a glance tells you how busy KiroCrew is. Themed scenes, pop-out for a second monitor. Purely a visualization — it never changes what agents do. | — | No |

## Hidden apps

Two built-ins are hidden: **Workflows** (`workflows`) and **Channels** (`channels`). The manifest flags them `hidden: true`, so they do not show up in **Discover** or **Library** until they are enabled. Enable them from the command line by name:

```bash
kirocrew app enable workflows
kirocrew app enable channels
```

Once enabled, each adds its dashboard page (**Workflows**, **Channels**) like any other app.

## Where to start

If you write code daily, four apps earn their place fast:

- **Command Bar** — already on; learn Cmd+K / Ctrl+K and you stop hunting through menus.
- **Files** — read and search the gateway host from the dashboard, zero setup, read-only so it can't break anything.
- **Code Review Sage** — if you live in GitHub PRs, the Focus Report puts the risky files first; it only needs `gh` authenticated on the host.
- **Spec Builder** — turns a half-formed feature idea into reviewable Requirements → Design → Tasks before you write a line, no external account needed.

## Apps that are not built in

The 24 above ship inside KiroCrew. Beyond them is an **official registry** plus community apps, published separately and installed from **Discover**. A few registry entries are listed in KiroCrew's own `app-registry.json`, for example `launchdarkly`, `todo-ledger` and `todo-txt`, each pointing at a GitHub repo. To add an organization's own registry, use **Manage app sources** on **Discover**.

Registry apps install from a repository. `kirocrew app info file-review` on a machine with **File Review** installed shows it:

```text
source:     registry:file-review
origin:     registry
sourceUrl:  https://github.com/jief123/file-review
```

That is the shape of every non-built-in app from a registry: a name that resolves to a GitHub repo, cloned on install.

The difference that matters is trust. A built-in ships inside the KiroCrew package and runs **like core code** — the trust-boundary comment in `module_loader.py` says exactly that, and `builtin_app_names()` marks these names as first-party. A third-party app's Python executes in-process with full gateway privileges, so it runs only after you grant trust at **Settings → Security → Third-party apps** (the `agent.apps_allow_third_party` and per-app `agent.apps_trusted` settings). Built-in apps skip that gate entirely; installed and community apps do not.

## Turning an app on and off

Two ways, same effect. In the dashboard, open **Library** for installed apps (built-ins are always installed) and turn the app on or off there; **Discover** is the store for apps you do not have yet. From the command line:

```bash
kirocrew app list
kirocrew app enable code-review-sage
kirocrew app disable code-review-sage
kirocrew app info issue-radar
```

Use the app's **id** (the kebab-case name in the tables above), not its display name — `kirocrew app enable projects`, not `Task Runner`.

## Gotchas

- **Enabled is not configured.** Most apps need a step after you flip them on — connect a repo, authenticate a CLI, point at a folder. The app page tells you; the switch alone rarely does anything.
- **"The host" means the gateway host.** `gh`, `glab`, `az`, `pdflatex` and AWS credentials all have to be on the machine running KiroCrew. If that is a remote box, authenticating on your laptop does nothing for the app.
- **Two apps need the Desktop build.** Crew Companion and Mochi declare `requiresDesktopApp`; in a browser-only setup their window has nowhere to float.
- **Command Bar takes over Cmd+K.** While it is enabled you lose the old quick-search over knowledge, skills and prompts from that surface. Disable it if you want that back.
- **Dev Fleet widens the agent's reach.** Enabling it lets agent sessions start and stop pods, which runs worktree code outside the sandbox as you. Leave it off unless you are developing KiroCrew itself.
- **id ≠ display name.** The store shows **Task Runner**, **Notes**, **Files**, **AWS Control**; the manifest names are `projects`, `md-notebook`, `file-explorer`, `aws-control`. The CLI wants the manifest name.
