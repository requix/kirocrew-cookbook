---
title: Install Kiro Crew step by step
description: Prerequisites, the one-line installer, the gateway, and how to keep it running on Linux, macOS and Windows.
category: Getting started
difficulty: beginner
time: 15 min
surfaces: [cli, dashboard]
tags: [install, gateway, service, doctor, windows]
updated: 2026-10-30
featured: true
prerequisites:
  - A terminal and a browser on the machine that will run Kiro Crew
  - Permission to install software for your own user (no admin needed on the common paths)
---

Kiro Crew runs on your own machine. It is a gateway process that drives `kiro-cli` and adds memory, schedules, subagents and a safety gate on top. This page is the full install: every prerequisite, what the installer actually does, where it writes, and how to keep the gateway alive after you close the terminal.

If you only want to get to a first working task fast, [Your first hour](first-hour.md) is the short version. This page is the one to keep open when something does not install cleanly, or when you are setting up a server you will not be sitting in front of.

## Supported systems

Kiro Crew runs on macOS, Linux and Windows. The install paths differ by platform.

| Platform | Install paths | Notes |
|---|---|---|
| Linux | one-line installer, `.deb` / `.rpm` desktop package, AppImage, Docker, source | The one-line installer is the recommended path. |
| macOS | one-line installer, DMG desktop app, source | `kirocrew service install` sets up a per-user LaunchAgent. |
| Windows | signed desktop installer (`.exe`), source | No one-line installer and no OS-level service; see [How Windows differs](#how-windows-differs). |

### How Windows differs

Windows is natively supported, but three things work differently from macOS and Linux, and they are worth knowing before you start:

- **No one-line `cli.sh` installer.** You install the signed desktop `.exe` or do a Python source install. The source build driver is `.\make.ps1` (the Windows counterpart of the Makefile), and the gateway launches as `.\.venv\Scripts\python.exe -m kiro_crew gateway`.
- **No `kirocrew service install` backend.** `kirocrew service install` prints that service management is supported only on systemd and launchd. A gateway you start by hand stops when you sign out or close its window.
- **No OS-level agent sandbox.** On Linux and macOS, agent subprocesses run inside a namespace or Seatbelt sandbox. Windows has no such backend. The default KAS chat harness runs unconfined; scripts, hooks, MCP probes and other spawned tools also run unconfined under the platform default. Credential environment variables are still scrubbed and every spawn is audited, but the OS is not confining the agent. To push chat into a real sandbox, pick the **Kiro CLI** harness in Settings → Agent Harness. To refuse the unconfined spawns instead, declare `agent.sandbox_allow_unsandboxed_exec: false` in `config.json`.

The rest of this page shows the Linux/macOS path first and calls out the Windows equivalent where it matters.

## Prerequisites

The prebuilt artifacts bundle their own Python, so for the common install you need almost nothing on the host beyond `kiro-cli`.

| Requirement | Needed for | Floor |
|---|---|---|
| `kiro-cli` | Driving the model (the default agent backend) | Required, on your `PATH` |
| Python | Only the source install, or `--system-python` | `>= 3.12` |
| Node.js + npm | Only building the dashboard from source | `>= 22.12` (Node 24 LTS recommended) |

Node is only needed to *build* the dashboard. The prebuilt wheel, the macOS DMG, the Linux AppImage and the `.deb` / `.rpm` packages all ship the dashboard already bundled, so with one of those you need neither Node nor a compiler.

The one-line installer provisions its own Python by default (a SHA-256-pinned `uv` downloads a python-build-standalone CPython 3.12 under `~/.kiro/crew-python`). So on the recommended Linux path you do not install Python yourself either. Pass `--system-python` if you would rather run on a system Python 3.12+.

Embeddings need no setup step. On first gateway start, the embedding model (about 610 MB) downloads in the background over HTTPS, verified against a pinned sha256, and lands under `~/.kiro/crew/models/`. Until it arrives, memory search falls back to keyword search and switches to semantic search on its own with no restart.

### Install and log in to kiro-cli

`kiro-cli` is the one hard prerequisite. Kiro Crew drives it over the Agent Client Protocol; without it, chat sessions cannot run. The repo does not ship a `kiro-cli` installer of its own — install it from the official page and then log in:

Install `kiro-cli` from [kiro.dev/cli](https://kiro.dev/cli/), put its binary on your `PATH`, then:

```bash
kiro-cli login
```

Installing and logging in are two separate states. `kirocrew doctor` reports the binary and the login on separate lines, so check both. On the first dashboard launch, if `kiro-cli` is missing or signed out, the **Set up Kiro** page detects it, shows copyable install commands for your platform and the login command to run yourself, and offers a **Use other coding agents** picker. Kiro Crew does not run the install or the login for you.

## Steps

### 1. Run the one-line installer (Linux and macOS)

This fetches a signed, sha256-verified `kirocrew` wheel from the release CDN. No clone, no npm, no local build:

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
```

`stable` is the default channel. To track a faster lane or pin an exact release:

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --channel insider
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --version 0.6.0
```

What the installer does, under the hood:

- **Verifies before it installs.** `--version` resolves an immutable per-version signed manifest, and the installer checks the wheel's digest against it. There is no checksum-only fallback; a mismatch fails closed. The minimum pinnable release is `0.1.2`.
- **Picks an install layout.** It uses `pipx` when `pipx` is on your `PATH`. Otherwise it creates a managed venv *beside* the data home at `~/.kiro/crew-venv` (override with `KIROCREW_VENV`) and symlinks `~/.local/bin/kirocrew` at it. The venv is deliberately not nested inside `~/.kiro/crew`, so no whole-home cleanup can delete the live interpreter.
- **Provisions its own Python.** A SHA-256-pinned `uv` installs a python-build-standalone CPython 3.12 into `~/.kiro/crew-python`. An installed `uv` already on `PATH` is never executed, because `PATH` commonly leads with agent-writable directories.
- **Installs dependencies from prebuilt wheels only** (`pip --only-binary=:all:`), so no C compiler or `-dev` headers are needed. On a host where no dependency publishes a runnable wheel, it stops before any build and names the platform and packages.
- **Records the channel** to `~/.kiro/crew/channel`, and prints the next step when it finishes.

Updates to a managed venv build each new version as its own tree beside it (`crew-venv-<version>`, about 350 MiB) and switch the `crew-venv-current` link to it, keeping the current and previous trees for rollback.

On Windows there is no `cli.sh`. Install the signed desktop `.exe` from `https://download.crew.kiro.dev/desktop/stable/latest/KiroCrew-Setup.exe`, or do a source build with `.\make.ps1 build`. See the [Windows install guide](https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md) for the current signing and source-install detail.

### 2. Point it at a backend and verify

If you have not already, install and log in to `kiro-cli` (see [above](#install-and-log-in-to-kiro-cli)). Then run first-time setup:

```bash
kirocrew setup
```

This interactive wizard detects `kiro-cli` on your `PATH`, installs the agent config to `~/.kiro/agents/kirocrew.json`, and walks through the workspace directory, timezone and dashboard URL. It configures no messaging channels — the dashboard and CLI need none. A few flags narrow it:

| Flag | Effect |
|---|---|
| `--agent-only` | Install the agent config and stop, skipping workspace and credential prompts |
| `--clean` | Rebuild the agent config from defaults instead of merging your existing MCP servers and tools forward |
| `--slack` | Run the guided Slack credential setup (opt-in) |

`kirocrew setup --agent-only --clean` rebuilds the agent config from scratch and touches nothing else. That is the fix for a broken or stale MCP configuration, because without `--clean` the existing file is used as the base.

From a source checkout, every subcommand runs as `PYTHONPATH=src python -m kiro_crew <subcommand>` in place of `kirocrew`.

### 3. Start the gateway

```bash
kirocrew gateway
```

This starts the full server: the web dashboard, listeners for every configured messaging channel, the cron scheduler, the heartbeat and the update checker. The dashboard listens on `http://localhost:5476`. Leave this terminal open — closing it stops the gateway. [Step 5](#5-keep-the-gateway-running) replaces this with a supervised service.

If port 5476 is taken (often by a second gateway), bind an OS-assigned port:

```bash
kirocrew gateway --port auto
```

`KIROCREW_PORT` sets the port through the environment; `--port` on the CLI overrides it.

### 4. Open the dashboard and finish Set up Kiro

In a browser on the same machine:

```text
http://localhost:5476
```

On first launch, if `kiro-cli` is missing or not logged in, you land on the **Set up Kiro** page. It shows the exact install and sign-in commands for your platform. Run them yourself, then reload — the page re-checks on its own (on Windows, a `kiro-cli` installed while the gateway is running is picked up by the next automatic check, with no restart).

Once the page's read-only `kiro-cli whoami` probe succeeds, the dashboard opens. This is also where you confirm the backend is wired up before you send any real work.

### 5. Keep the gateway running

A foreground `kirocrew gateway` dies when you close the terminal. For anything always-on — channel bots, cron jobs, background tasks — install it as a service:

```bash
kirocrew service install    # systemd unit on Linux, launchd LaunchAgent on macOS
kirocrew service status
kirocrew service uninstall
```

The service survives an SSH disconnect, restarts on crash, and starts on boot. Two platform details matter:

- **Linux.** The installer writes `/etc/systemd/system/kirocrew.service` and prompts for `sudo` once for the unit file; the gateway itself runs as your own non-root user (it refuses to install a `User=root` service). Enable linger so your user manager keeps running after logout, or agent runtimes die at your last logout:

  ```bash
  sudo loginctl enable-linger <user>
  ```

- **macOS.** The service is a per-user LaunchAgent, so on a Mac the gateway starts when you log in, not at boot. On a headless Mac with automatic login off, nothing answers on the port until someone logs in at the machine itself.

Tail the service output with `kirocrew logs -f`.

To set the service port (a system service inherits none of your shell environment), bake it in at install time: `KIROCREW_PORT=5477 kirocrew service install`. To change it later, edit `/etc/kirocrew/kirocrew.env` and `sudo systemctl restart kirocrew`.

On Windows, `kirocrew service install` has no backend and prints that service management is systemd/launchd only. Run the gateway in a terminal (or through the desktop app, which is a window around the same gateway), and reach the dashboard from a browser. The desktop app can start and stop its gateway with the app; the CLI path does not auto-start at boot.

## Verify

Run the doctor:

```bash
kirocrew doctor
```

`doctor` walks your setup section by section: the resolved platform edition, the `kiro-cli` binary and login state, the project directory, the agent config and its MCP entries, the sandbox, services and channels, the gateway status, and the embedding runtime and model. Where a check fails it prints a specific fix command, and it repairs missing MCP entries where it can. It is the first stop for any "it won't start" problem.

You are installed when all of these hold:

- `kirocrew doctor` reports no problems, and shows `kiro-cli` both installed and logged in.
- The dashboard loads at `http://localhost:5476`.
- A first real task comes back with an answer, not an error — that part is [Your first hour](first-hour.md).

To collect everything for a bug report in one file (credentials redacted):

```bash
kirocrew doctor --bundle
```

## Updating

```bash
kirocrew update
kirocrew restart     # restart the gateway onto the new version
```

For a managed-venv install, `update` builds the new version as its own tree and switches the `crew-venv-current` link. For a source checkout it updates the checkout and rebuilds it. Clicking **Update Available** in the dashboard topbar runs the same path. The signed desktop apps update themselves through the app's own updater.

If `kirocrew restart` reports the replacement gateway did not become ready in time, a slow host can need longer than the default 60 seconds — set `KIROCREW_RESTART_READY_TIMEOUT` (clamped to 15–180 seconds) for the shell running the restart, then run `kirocrew logs -f` to watch the new gateway start.

## Uninstalling

Uninstalling removes the binary and runtime but **preserves your data home** (`~/.kiro/crew`) — config, credentials, memory, sessions and the audit chain stay intact, so a reinstall picks up where you left off. Stop the gateway and remove the service first:

```bash
kirocrew stop
kirocrew service uninstall
```

Then remove the binary by install method:

| Install method | Remove with |
|---|---|
| `cli.sh` via pipx | `pipx uninstall kirocrew` |
| `cli.sh` via managed venv | `rm ~/.local/bin/kirocrew` and the `~/.kiro/crew-venv*` trees (exact script in the [install guide](https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md)) |
| pip / pip wheel | `pip uninstall kirocrew` |
| Linux `.deb` / `.rpm` | `sudo apt remove kirocrew` / `sudo dnf remove kirocrew` |
| macOS DMG | Quit, then drag `KiroCrew.app` from `/Applications` to the Trash |
| Linux AppImage | Delete the AppImage file |
| Windows | Settings → Apps → Installed apps → Kiro Crew → Uninstall |

To also remove all user data — config, credentials, session history, memory and the model cache — back up first, because it is irreversible, then delete the data home:

```bash
cp -a "${KIROCREW_HOME:-$HOME/.kiro/crew}" ~/kirocrew-backup \
  && rm -rf "${KIROCREW_HOME:-$HOME/.kiro/crew}"
```

Store that backup outside the data home and somewhere the agent cannot reach — it holds your `.env` credentials and signing keys, with none of the live home's path protections.

## Alternatives: Docker and remote

For an always-on server or NAS, the gateway ships as a public multi-arch image on GHCR (`ghcr.io/kirodotdev/kirocrew:stable`):

```bash
docker run -d --name kirocrew \
  -p 127.0.0.1:5476:5476 \
  -v kirocrew-home:/home/kirocrew \
  ghcr.io/kirodotdev/kirocrew:stable
```

Two one-time steps follow: `docker exec -it kirocrew kiro-cli login` to authenticate the agent runtime, then `docker exec kirocrew kirocrew token --ttl 2h` to mint a dashboard login link (boot-time links in `docker logs` usually expire before you read them). The `-p 127.0.0.1:5476:5476` mapping keeps the port host-local. Inside the container the gateway binds all interfaces (`KIROCREW_BIND=0.0.0.0`) because a loopback bind would be unreachable from the host — the dashboard still requires a token regardless.

The Docker sandbox has its own wrinkles: on first run the entrypoint probes whether the inner user-namespace sandbox works under the runtime's seccomp/AppArmor policy, and if no backend works, agent execution stays fail-closed until you either permit user namespaces (the repo ships `docker/seccomp/kirocrew-seccomp.json`) or restart with `-e KIROCREW_ALLOW_UNSANDBOXED=1`. The [Docker guide](https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker.md) has the full matrix, including Kubernetes and WSL2.

For reaching a gateway on a remote host or from a phone, see the [remote and mobile guide](https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-and-mobile.md). It is outside the scope of this page.

## Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `kiro-cli not found in PATH` | `kiro-cli` is not installed or not on `PATH` | Install it from [kiro.dev/cli](https://kiro.dev/cli/), open a new shell, retry |
| `AcpTimeoutError: ACP prompt timed out` | `kiro-cli` missing, not logged in, or a stale MCP config eating the init window | Check `kiro-cli login`; rebuild the agent config with `kirocrew setup --agent-only --clean` |
| Dashboard won't load | The gateway is not running, or the port is taken | Start `kirocrew gateway`; if 5476 is busy, `kirocrew gateway --port auto` |
| Dashboard asks for sign-in but `kiro-cli` is authenticated with an API key | The `KIRO_API_KEY` is only in your shell, not the gateway's environment | Add it to `~/.kiro/crew/.env` (chmod 600 first), then `kirocrew restart` |
| `sandbox: unshare(NEWNS) failed: errno 1` on Ubuntu 23.10+ | AppArmor restricts unprivileged user namespaces | `kirocrew service install` adds and loads the `kirocrew-userns` profile; for an AppImage, `kirocrew sandbox install-profile --path <AppImage>` |
| Memory or knowledge search returns nothing | The embedding model is still downloading | Check the Vector Memory section of `kirocrew doctor`; it falls back to keyword search until the model lands, then switches over with no restart |
| macOS: a command runs in Terminal but not inside the app | A GUI `.app` inherits launchd's minimal `PATH`, not your shell's | `launchctl setenv PATH "$PATH"`, then fully quit (Cmd+Q) and relaunch the app |
| macOS headless: gateway down after reboot until someone logs in | The service is a per-user LaunchAgent; its `gui/<uid>` domain exists only after a login at the Mac | Turn on automatic login, or log in once per reboot |
| Windows: `ModuleNotFoundError: No module named 'fcntl'` | You installed a build that predates the Windows port | Update to a current build |
| Windows: "Python was not found" (Microsoft Store) | A bare `python` resolved the Store alias stub | Install a real CPython 3.12 and put it ahead of the stub on `PATH` |
| Enterprise (work) account: MCP tools absent, every server reports healthy | kiro-cli connects only to registry-marked servers in MCP registry mode | `kirocrew config set agent.mcp_registry_mode true`, `kirocrew restart`, and have an admin add the servers to the registry |

When in doubt, run `kirocrew doctor` first — it checks the whole chain end to end and prints a fix command for anything it finds.
