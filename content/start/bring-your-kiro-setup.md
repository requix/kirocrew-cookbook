---
title: Bring your Kiro setup
description: What KiroCrew reuses from your Kiro CLI/IDE config, what changes, and what to check.
category: Getting started
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [agents, steering, skills, mcp, hooks, migration]
updated: 2026-10-30
prerequisites:
  - KiroCrew running (see Your first hour)
  - An existing ~/.kiro with your agents, steering, skills, or MCP servers
---

You already have a `~/.kiro` tree: steering files, a few custom agents, skills, MCP servers, maybe some hooks. KiroCrew runs on top of `kiro-cli`, not instead of it, so most of that tree carries over untouched. The parts that behave differently are worth knowing before you wonder why a skill you rely on is not loading.

The short version: KiroCrew starts `kiro-cli` in ACP mode and drives it, so by default kiro-cli's engine, your login and your agent files do the work. What changes is that a new chat runs KiroCrew's own `kirocrew` agent with its own prompt, and skills follow a different root than the kiro-cli default.

## What carries over

| Thing | Picked up? | Where it lives | Note |
|---|---|---|---|
| Login | Yes | `kiro-cli login` | Used as is. On the default harness you can instead sign in from **Settings → Agent Harness**. |
| Global steering | Yes | `~/.kiro/steering/**/*.md` | Loaded for every session, as in the terminal. |
| Project steering | Yes, with a project | `<project>/.kiro/steering/**/*.md` | Needs a project bound to the chat. |
| Custom agents (JSON) | Yes | `~/.kiro/agents/*.json`, `<project>/.kiro/agents/*.json` | Switch with the agent chip or `/agent <name>`. |
| Custom agents (Markdown) | Yes on KAS, no on kiro-cli | same | kiro-cli loads JSON only. |
| MCP servers (global) | Yes | `~/.kiro/settings/mcp.json` | Merged into the `kirocrew` agent; file never modified. |
| MCP servers (agent) | Yes | a spec's `mcpServers` | A custom agent keeps its own. |
| Your skills | **No, not by default** | `~/.kiro/skills/` | The default agent reads `~/.kiro/crew/skills/`. Add your path in Settings. |
| Hooks | Partly | the Hooks tab, or `agent.kiro_hooks` in config | Five of kiro-cli's events map through; the IDE's extra triggers are stored, not fired. |
| Prompts | Yes | `~/.kiro/prompts`, `<project>/.kiro/prompts` | Mention with `@<name>` in the composer. |

The rest of this page is the detail behind each row, and the gotchas you only hit once you depend on something.

## Steering

Nothing to move. kiro-cli loads both steering roots itself: the global `~/.kiro/steering/**/*.md` for every session, and `<project>/.kiro/steering/**/*.md` because the session subprocess runs with the chat slot's project directory as its working directory. A workspace steering file therefore needs a project bound to the chat — set it with the project button in the message box, or start the chat in a sidebar folder that has a linked project. With no project, the Steering files tab offers only the global root and a workspace document is refused with `steering_workspace_unavailable`.

Inclusion modes are Kiro's format, not KiroCrew's: `inclusion` is one of `always`, `fileMatch`, `manual`, `auto` (absent or misspelled reads as `always`), and `fileMatchPattern` is a glob that only means anything beside `inclusion: fileMatch`. KiroCrew reports and edits the declaration but does not decide delivery from it — what a mode causes is the harness's behavior, it differs from the Kiro IDE, and it has changed between releases. The one row every measurement agrees on is `manual`: there is no way to pull a `manual` document into a turn over ACP. Treat a steering file as reliably reaching a session when it declares `always` (or declares nothing) and lives in a root that session loads.

One asymmetry to know about: on the Claude Code backend, which does not read an agent spec's `resources` array, the gateway loads the global root explicitly (`_load_steering_resources` in `src/kiro_crew/context_assembly/agent_spec.py` globs `file://.kiro/steering/**/*.md` against `$HOME`) — but only the global root, not the workspace one.

Steering sits ahead of memory in context assembly: steering resources are injected before thread history, before memory, before lessons, and an earlier layer outranks a later one. Where a steering file and a stored memory disagree, the steering file is the one the agent follows.

## Custom agents

Your agents in `~/.kiro/agents/*.json` and a project's `.kiro/agents/*.json` are listed and runnable. Switch a chat to one with the agent chip under the message box or `/agent <name>`; a project agent needs the chat to have that project as its folder. A name no agent answers to is refused rather than silently running the default.

### Running on your own agent instead of `kirocrew`

A new chat runs KiroCrew's own `kirocrew` agent, not kiro-cli's `kiro_default`. That is the main reason the same request can get a different answer than it would in `kiro-cli chat`: `kirocrew` has a different system prompt, and KiroCrew adds context to every turn (memory, learned corrections, the skill catalog, dashboard reply rules). To work on a CLI-style agent instead:

- **Your own agent, per chat.** Pick it with the agent chip or `/agent <name>`. A JSON agent runs on both Kiro harnesses.
- **kiro-cli's built-in `kiro_default`.** `/agent kiro_default` works only when the harness is **Kiro CLI**: choose it under **Settings → Agent Harness**, or run `kirocrew config set agent.acp_backend kiro`. The default harness (KAS, kiro-cli's v3 engine) does not offer kiro-cli's built-ins, so use your own agent there.
- **Default for all new chats.** Open **Customize → Custom agents** and set it in **New sessions use**. This writes `agent.default_agent`.

You can also pin an agent per cron job (at creation time) and per crew member.

Even on your own agent, KiroCrew still adds memory, learned corrections and the dashboard reply rules. A custom agent in `~/.kiro/agents/` can set `"includeCrewContext": false` to drop KiroCrew's block of dashboard rules and its dashboard-tool reminders, though some reply-format guidance still rides each turn.

### What KiroCrew adds to or overrides in the prompt

KiroCrew's own managed default spec (`~/.kiro/agents/kirocrew.json`) does **not** point `prompt` at a file. It carries a short native-prompt stub, and KiroCrew injects the resolved operating contract itself on session start, so the persona reaches every backend exactly once. A custom or forked agent that sets its own `prompt` keeps it — the stub is the managed default's value only. Your own agent's prompt is loaded and appended as the `[AGENT SYSTEM PROMPT]` block, on every harness, with no backend condition.

The agent spec is a large surface and most of its fields behave differently per harness. If you are porting a spec that relies on per-tool restrictions, hooks, or `resources`, read [agent-spec-fields.md](https://github.com/kirodotdev/KiroCrew/blob/main/src/kiro_crew/docs/agent-spec-fields.md) in the repo — the per-field table is the authority, and the degradations on non-kiro-cli backends are predictable but not obvious (a `@server/tool` ref narrows to one tool on kiro-cli and mounts the whole server everywhere else, for example).

### Markdown vs JSON agents

A markdown agent (YAML frontmatter plus a prompt body) is the form kiro-cli v3 (KAS) and Kiro IDE read. It is listed in pickers and runs on KAS, but it does **not** run on the `kiro` (kiro-cli) backend: kiro-cli loads JSON only, and a markdown-only agent is refused at session start with a message naming the file. Switch `agent.acp_backend` to `kas`, or add a JSON spec, to run it there.

`<name>.json` and `<name>.md` side by side is the same agent twice. In KiroCrew the JSON wins and the markdown is not read (the gateway log warns which file is shadowed); kiro-cli v3's own loader resolves the pair the other way. Keep one file per name to get the same agent everywhere.

## Skills

This is the row most likely to surprise you. The default `kirocrew` agent reads skills from `~/.kiro/crew/skills/`, **not** `~/.kiro/skills/`. Your terminal skills in `~/.kiro/skills/` are not read by the default agent until you tell KiroCrew where they are.

Skill sources and precedence, highest first:

1. `~/.kiro/crew/skills/` — KiroCrew's global skills.
2. `skills.extra_paths` — read-only extra directories; a global skill wins on a duplicate name.
3. `<active-project>/.kiro/skills/` — loaded last, only when project skills are enabled and you have granted that exact project directory trust.

To use your existing `~/.kiro/skills` with the default agent, add it under **Settings → Skills → Extra skill paths** (one path per line), or from a terminal:

```bash
kirocrew config set skills.extra_paths '["/home/me/.kiro/skills"]'
```

A custom agent on the Kiro CLI harness still inherits `~/.kiro/skills` as it does in the terminal. The split is really about the default agent and the KAS native-launch view, where KiroCrew supplies the skill directory itself (`~/.kiro/skills` and the workspace's `.kiro/skills`) and serves it through `skill_search`.

A skill is any directory holding a `SKILL.md`. The frontmatter that matters: `always: true` injects the whole body every session, `triggers` is a comma-separated phrase list, and `repo_scope` restricts a skill to a project tree. `SKILL.md` must be UTF-8; a UTF-16 file (PowerShell's default redirect) is skipped with a log warning.

## MCP servers

KiroCrew never writes to your provider globals. `~/.kiro/settings/mcp.json` is user-owned: KiroCrew reads it and merges it into the per-agent file it fully owns, `~/.kiro/agents/kirocrew.json`, at render time. That keeps KiroCrew-scoped tools out of every interactive kiro-cli and Kiro IDE session you run outside KiroCrew.

Three config files are in play:

| File | Owner | Read by |
|---|---|---|
| `~/.kiro/agents/kirocrew.json` | KiroCrew gateway | kiro-cli, as the `kirocrew` agent |
| `~/.kiro/settings/mcp.json` | You | every kiro-cli agent; merged into KiroCrew's agent file |
| `~/.kiro/crew/mcp.json` | You, via the dashboard MCP panel | KiroCrew gateway only |

KiroCrew's own managed servers (`kirocrew-core`, `kirocrew-cron`, and the others) sit **beside** yours in the generated agent file. They are refreshed on every rebuild, their `command`/`args` rewritten from the live `kirocrew` binary. A custom agent keeps its own `mcpServers`; on the Kiro CLI harness it also loads `~/.kiro/settings/mcp.json` unless it sets `"includeMcpJson": false`.

Two things to know:

- **`includeMcpJson` is pinned `false` on every agent KiroCrew manages.** The gateway already merged the global into the agent file, so the agent file is the superset. With `true`, kiro-cli would merge the global a second time and a stale path there could shadow the fresh one the gateway resolved. A crew's fork of a custom template gets the same pin, so a server a fork reached only through the global `mcp.json` is not loaded for it — list it in the fork's own `mcpServers` instead.
- **If `kirocrew-core` / `kirocrew-cron` show up in your provider global, that is leftover state from an older install.** Clean it from the dashboard MCP panel or run `kirocrew setup`.

Reference tokens as `${ENV_VAR}` in a server entry, never a literal value. On the KAS wire, `headers` are withheld from every entry and `env` is filtered per key, because those routinely hold credentials.

Manage all of this from **Customize → Connections**. Changes there do not restart sessions by default; scope changes take effect at the next session spawn, or use Apply & Restart to drain the warm pool.

## Hooks

Chat lifecycle hooks live on the **Hooks** tab (`~/.kiro/crew/hooks.json`) and fire on five events: `AgentSpawn`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`. `PreToolUse` is the only event whose exit code decides anything, and only where the gateway is the one approving the call: exit 0 allows, exit 2 denies (stderr goes to the model), anything else resolves to deny. Where kiro-cli already approved the call, the hook is informational.

If you keep kiro-cli hooks that should survive `kirocrew update`, put them in `agent.kiro_hooks` in `~/.kiro/crew/config.json`:

```json
{"agent": {"kiro_hooks": {"preToolUse": [{"matcher": "*", "command": "/path/to/hook.sh"}]}}}
```

This field also accepts the array of hook documents a kiro-agent profile uses, so a spec written for either tool loads. Twelve triggers are accepted in any spelling, but only five map onto kiro-cli's own events (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart` → `agentSpawn`, `Stop`). A hook on the other seven triggers — the file and task triggers the Kiro IDE uses — stays in your config and is not installed. An `action` of type `agent` has no kiro-cli slot either.

A hook does not inherit the gateway's environment. It gets an allowlisted slice (`PATH`, home, temp, locale, TLS trust, `KIROCREW_HOME`), so a command that works in your terminal can fail as a hook when something like `VIRTUAL_ENV`, `PYTHONPATH` or `AWS_PROFILE` is not forwarded. Set what you need inside the command, or use absolute paths.

## Settings and config

Everything KiroCrew remembers lives in `~/.kiro/crew/config.json`, created on the first `kirocrew gateway` run. Most keys are editable from the Settings pages; the full set is in the config schema, rendered under **Developer → Config**.

```bash
kirocrew config get agent.acp_backend     # which harness
kirocrew config get skills.extra_paths     # where your skills come from
kirocrew config defaults                   # values holding a superseded default
```

Your terminal `kiro-cli` config is separate. KiroCrew's config is about the gateway: the harness, memory, schedules, channels, sandbox. One key worth setting early is `agent.acp_backend` if you want a specific harness (`kas` is the default, `kiro` is kiro-cli).

## Kiro IDE specifics

Project `.kiro/` folders are shared with the IDE in the parts kiro-cli reads directly: project steering (`<project>/.kiro/steering`) and project agents (`<project>/.kiro/agents`) are the same files the IDE and kiro-cli use. Markdown agents are the form "kiro-cli v3 (KAS) and Kiro IDE read", so an agent authored for the IDE loads on KAS here. The IDE's agent drop-down also lists KiroCrew's internal `kirocrew-skill-view-...` agents: those are managed views KiroCrew writes into `~/.kiro/agents/` so kiro-cli can resolve a `--agent` name, pruned when their session ends; picking one in the IDE is harmless but pointless (it is the named agent minus its `skill://` resources). The repo does not document anything else IDE-specific (specs, for instance), so treat other IDE features as outside what KiroCrew reuses.

## Steps: move into KiroCrew in 15 minutes

Verify each piece is actually seen before you trust it.

### 1. Confirm the harness

```bash
kirocrew config get agent.acp_backend
```

Empty or `kas` is the default (KAS); `kiro` is kiro-cli. Pick `kiro` if you need kiro-cli's built-in agents such as `kiro_default`. Stay on `kas` if you have markdown-only agents, because kiro-cli loads JSON specs only.

### 2. Confirm a steering file loaded

Start a chat with your project as its folder and ask it something your steering answers:

```prompt
What are the steering rules you're currently following for this project?
```

If a project rule is missing, the chat has no project bound — set it with the project button in the message box.

### 3. Point the default agent at your skills

The default agent reads `~/.kiro/crew/skills/`, not `~/.kiro/skills/`. Add your path:

```bash
kirocrew config set skills.extra_paths '["/home/me/.kiro/skills"]'
```

Then confirm a specific skill is in scope:

```prompt
Search your skills for "<name of one of my skills>" and tell me where it loaded from.
```

### 4. Confirm your MCP servers merged

Open **Customize → Connections** and check the MCP panel: the servers from your `~/.kiro/settings/mcp.json` should be listed beside KiroCrew's own. A red "0 tools" row on a server that works in your terminal is usually a probe limitation on a host with no OS sandbox, not a broken server — the error text says so.

### 5. Run your own agent

Switch one chat to a custom agent and confirm the switch:

```prompt
/agent my-reviewer
```

A name no agent answers to is refused, so a clean switch means the spec loaded.

### 6. Carry over the hooks that matter

Move any `kiro-cli` hooks you want to keep into `agent.kiro_hooks` (config) or the Hooks tab, remembering that only five triggers reach kiro-cli and that a hook runs with a stripped environment. Test each one from the Hooks tab before you rely on it.

## Gotchas

- **Your skills do not load until you add the path.** The default agent reads `~/.kiro/crew/skills/`, so `~/.kiro/skills/` is invisible to it until you add it under Extra skill paths. This is the single most common "my setup isn't here" surprise.
- **A markdown-only agent won't run on kiro-cli.** kiro-cli loads JSON specs only. Use the KAS backend, or add a JSON spec. A `.json` beside a `.md` of the same name shadows the markdown entirely.
- **A forked agent loses a server it only had through the global `mcp.json`.** Forks pin `includeMcpJson: false` on every refresh, so list the server in the fork's own `mcpServers`.
- **Project steering needs a project bound to the chat.** Without one, the chat works in KiroCrew's own workspace and your workspace steering never loads.
- **A hook's environment is not your shell's.** `VIRTUAL_ENV`, `PYTHONPATH`, `JAVA_HOME`, `AWS_PROFILE` and the like are not forwarded; set them inside the command.
- **The default chat runs `kirocrew`, not `kiro_default`.** Different prompt, plus injected memory and rules. If you want CLI-identical behavior, switch the agent, and on kiro-cli's built-ins switch the harness to `kiro` first.
- **Steering outranks memory.** A steering rule wins over a stored memory where they conflict, so do not teach a lesson that only duplicates a steering file.
