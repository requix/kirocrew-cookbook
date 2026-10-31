---
title: What KiroCrew apps are
description: What a KiroCrew app is, what it can add, how it installs and gets trusted, and how agents use it.
category: Apps
difficulty: intermediate
time: 14 min
surfaces: [dashboard, cli]
tags: [apps, app-store, permissions, trust, manifest]
updated: 2026-10-30
featured: false
prerequisites:
  - KiroCrew running (see Your first hour)
  - Comfortable with the dashboard sidebar and the kirocrew CLI
---

Your KiroCrew surface is not fixed. The pages in the sidebar, the agents in the picker, the skills on disk, the MCP tools an agent can call, the jobs on the schedule — a chunk of all that comes from apps, and it changes when you enable or disable one. If a tool you expected is missing, or a page appeared you did not add, an app is usually the reason. This page explains what an app is, what it can bring, how it installs and gets trusted, and how an agent reaches into one.

## What an app is

An app is a folder with an `app.json` manifest at its root. The manifest declares the app's identity (`name`, `version`, `displayName`, `description`) and then, optionally, every resource and capability the app contributes. KiroCrew reads the manifest to decide what the app adds and what it is allowed to do. Nothing about an app is magic: it is data in a JSON file plus the files that data points at.

The `name` is a kebab-case identifier and becomes a directory name, so it is checked hard at install — it cannot be `system`, `library`, `registry` and a few other reserved segments, and it cannot be a Windows device stem like `con` or `nul`.

## What an app can add

Every item below is a field in the [manifest reference](https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md). An app may declare any subset.

| Contribution | Manifest field | What it adds |
|---|---|---|
| Dashboard pages | `ui.pages` | Routed pages with a sidebar entry |
| Side-panel tabs | `contributes.panelTabs` | Body-owning tabs in the chat side panel (up to 8) |
| Session controls | `contributes.sessionControls` | A per-chat chip in the composer bar (at most 2 per app) |
| Command Bar rows | `contributes.commands` | Rows that seed a session with a prompt |
| File-menu rows | `contributes.fileMenuItems` | Rows in the file-editor, tree, and folder menus |
| Agents | `agents` | Agent JSON files registered under the app's namespace |
| Skills | `skills` | Skill directories registered on enable |
| MCP servers / tools | `mcpServers` | An MCP server whose tools merge into allowed agents |
| Scheduled jobs | `crons` | Cron jobs registered on enable, removed on disable |
| A backend | `backend` | A process (`entryPoint`) or in-gateway hooks (`backend.hooks`) |
| Notification channels | `notifications.channels` | Up to 8 app-owned bell channels |
| Artifact publish target | `publishProvider` | One destination in the artifact publishing UI |
| Host-surface overlay | `ui.overlays` | Replaces a host surface like quick-search — **builtin apps only** |

Two of these have real caps worth remembering: at most 2 session controls per app, and the dashboard renders at most 2 across all apps, so with three contributing apps a declared control can be absent. `ui.overlays` is validated for any manifest but only a builtin can claim a slot; an installed app that declares one is refused at install.

What an app contributes is not fixed at build time either. A contributed command needs no page, no bundle and no backend — a manifest plus the skill its prompt names is the whole app.

## Where apps come from

- **Built in.** 24 apps ship inside the KiroCrew package. Almost all are off until you turn them on; **Command Bar** and **Task Runner** are the two on from a fresh install.
- **The official store.** The **Discover** page (`/apps`) reads the published catalog at `apps.crew.kiro.dev`, cached for an hour. When the fetch fails it falls back to a small seed list bundled in your build.
- **An external registry.** Open **Manage app sources** on **Discover** to add an organization's own registry.
- **A local path.** `kirocrew app install /path/to/my-app` installs a directory you built. Local-path installs skip the `onInstall` build hook, so build first.
- **A plugin package.** `kirocrew app import` converts a manifest-declared plugin package into an app directory. Conversion only reads JSON and copies files — no code in the package runs during the import.

## The lifecycle

```bash
kirocrew app list                    # installed apps and their status
kirocrew app info meetings           # one app's details
kirocrew app enable meetings
kirocrew app disable meetings
kirocrew app install /path/to/app    # a local app directory
kirocrew app uninstall my-app        # keeps app data
```

The states run install → trust → enable → update → disable → uninstall.

**Enable** is the activation gate. A disabled app contributes no pages, no agents, no skills, no crons and no backend process. **Disable** reverses all of that but keeps the app's data directory.

**Update** happens when the catalog version is newer than yours. The **Updates** worklist (`/apps/-/updates`) collects every pending update with **Update All**, and each Library tile keeps its own Update button. A registry update re-runs the `onInstall` hook, so write that hook to be idempotent.

**Uninstall** applies to apps you installed; a builtin cannot be uninstalled, only disabled. Uninstall keeps the app's data by default and removes its trust grant. Pass `--purge-data` on the CLI to delete the data too, which is not reversible. `kirocrew app install` on an app that is already installed is refused with `already installed`, and the CLI has no update command, so to load a new version from a local path you uninstall and install again.

## Trust and permissions

Enabling an app runs its code in the gateway's own process. App Python is imported into the gateway; there is no process-level sandbox around app code, and the manifest's `permissions` block gates the SDK tool surface handed to the app, not its imports, filesystem or network use. So the honest rule is the plain one: only enable apps you trust.

KiroCrew makes the boundary explicit instead of hiding it. The decision lives in one place — `apps/execution.py` — and it defaults to deny.

- **Builtin apps are trusted like core.** Anything loaded from outside the package is third-party.
- **Third-party execution is deny-by-default.** `agent.apps_allow_third_party` defaults to `false`, so enabling a third-party app is refused, and so are its hooks, backend, install scripts and `openCommand`, until you grant trust. In the dashboard the refusal becomes a consent dialog that names what the app receives; confirming it trusts that app alone (`agent.apps_trusted`) and retries.
- **Turning trust off revokes it.** The app's tracked backend process is stopped — at the moment you change the setting, at the next gateway start, and by a periodic liveness check that re-reads the policy.

To trust every third-party app at once, turn on **Trust every third-party app** in **Settings → Security → Third-party apps**. That writes `agent.apps_allow_third_party`. The per-app consent dialog is the narrower choice.

The `permissions` block itself:

| Field | Grants |
|---|---|
| `api` | Allowed API path prefixes |
| `events` | Allowed WebSocket event types |
| `mcpTools` | The app's own agents may call these managed tools |
| `storage` | App-scoped key-value storage |
| `cron` | May create cron jobs at runtime; **required** when `crons` is non-empty |
| `memory` | `""` (none), `"app-scoped"`, or `"shared"` |
| `network` | May make outbound HTTP calls |
| `sessionApproval` | May message, approve/deny tool requests and change approval mode on existing local user sessions |
| `spawn` | May start a background agent through the host's subagent manager |
| `jobs` | May run durable background work through `ctx.job` |

Most of these are advisory for in-process app code today — the validator functions are not wired into the install or runtime path. The ones actually enforced are the narrow ones: a non-empty `mcpTools` scopes the app's **own** agents (every undeclared host-managed tool is written to that agent's exclude list), `spawn` gates whether `ctx.spawn` exists at all, `cron` is required whenever `crons` is present, and `sessionApproval` is enforced for app-token calls into user sessions and shown in the consent dialog. Treat the rest as a declaration you read before enabling, not a cage around the code. Full in-process enforcement is still an open RFC.

## How agents use apps

An enabled app reaches your agents in three ways.

- **Its agents.** Each one is written to `~/.kiro/agents/<app>--<agent>.json`, but you call it by the `name` inside the file. It shows up in the chat's agent selector, and `/agent <name>` or `kirocrew chat --agent <name>` switches to it.
- **Its skills.** Each skill is linked to `~/.kiro/crew/skills/<app>/<skill>/`. The default agent sees the whole skill catalog. A custom agent, including an app's own agent, sees only the skills mapped to it with a `skill://` entry in its `resources`.
- **Its MCP tools.** The servers in the app's `mcpServers` are merged into the app's own agents, and a non-empty `mcpTools` limits which of KiroCrew's managed tools those agents get.

An app backend sits behind the gateway at `/apps/<name>/api/`. The app routes need dashboard or app login, so a bare `curl` to them is refused. When an agent says an app's tool is missing, the usual cause is that the app is not installed or not enabled. Check `kirocrew app list` before you debug anything else.

## Apps vs skills vs crewmates vs MCP servers

These overlap, so here is when to reach for each.

| You want to… | Use | Why |
|---|---|---|
| Add a page, a backend, agents, crons and skills as one installable unit | **App** | An app is the only thing that bundles all of these behind one manifest and one enable switch |
| Teach the agent a repeatable procedure it reads and follows | **Skill** | A markdown file on disk; no process, no page, agent-creatable |
| Give one job its own isolated memory and standing conversation | **Crewmate** | A named agent with its own memory store; set up in the dashboard, not by the agent |
| Expose an external system's tools to agents | **MCP server** | A tool surface; an app can bundle one, but a plain MCP server is just the tools |

An app can bundle a skill, an agent and an MCP server, so the question is rarely "app or skill" — it is whether you need the whole bundle behind one install, or just the one piece.

## Where apps live on disk

An installed app's files are copied to `~/.kiro/crew/apps/<app-name>/`, and its data lives in `data/` inside that folder, with key-value storage under `data/kv/`. KiroCrew runs that copy, not the folder you installed from. Built-in apps run from inside the KiroCrew package. The trust settings live in `config.json` under `agent.apps_trusted` and `agent.apps_allow_third_party`.

## What an app cannot do

- It cannot run its code until it is both enabled and, if third-party, trusted.
- It cannot claim a host overlay slot (like quick-search) unless it is a builtin.
- A command it contributes cannot name a host agent — only one of the app's own agents — so app-authored prompt text cannot borrow a broader agent's tool reach.
- It cannot use a reserved name, traverse outside its own root with resource paths, or forge builtin provenance through its installed metadata.
- It cannot create a crewmate on its own; `proposeCrewmate` is a switched-off preview, and even when live each proposal is an owner change card the owner presses.

## Gotchas

- **Enable checks trust first.** An app that is not built in is refused with `blocked by execution policy` until you trust it, even an app that ships no code. In the dashboard the refusal becomes a consent dialog; confirming it trusts that one app.
- **A missing app tool usually means "not enabled."** Confirm with `kirocrew app list`, then enable it from **Library**. Do not swap the tool call for a `curl`; the route refuses it.
- **Disable and uninstall both keep data; only `--purge-data` deletes it.** Uninstall also removes the app's trust grant, so a reinstall asks for trust again.
- **A cron shipped disabled resets to paused after a disable → re-enable cycle.** Disabling an app deletes its registered crons and re-enabling re-registers them from the manifest, so a job that shipped with `"enabled": false` and was later resumed goes back to paused and must be resumed again.
- **The store shelf can be short.** When the catalog fetch fails, Discover falls back to a bundled seed list; your installed apps in Library are unaffected.

For the catalog of what ships, see [built-in apps](./built-in-apps.md). To write your own, see [build your own app](./build-your-own-app.md). The trust boundary is part of the wider [security](../concepts/security.md) model; crewmates are covered in [crewmates](../concepts/crewmates.md); and teaching the agent a standalone procedure is [teach it a skill](../recipes/teach-it-a-skill.md).
