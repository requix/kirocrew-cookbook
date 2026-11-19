---
title: Fence the agent
description: Make folders read-only for the agent, review config edits made outside Kiro Crew, and set how strict the deny rules are.
category: Recipes
difficulty: intermediate
time: 20 min
surfaces: [dashboard, cli]
tags: [security, sandbox, governance, deny-rules, config]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - Linux or macOS for the read-only folders. The pending-edit review applies to a Linux host with the sandbox.
---

**Problem.** The agent runs with write access to far more of your disk than it needs. A mounted Windows drive, a folder of finished work or a shared archive is somewhere you want it to read and never change. At the same time, a settings file that confines the agent should not be something a stray script can quietly rewrite. This recipe covers the knobs 0.13.0 gives you for both, plus two switches that decide how firm the command deny rules and the write guard are.

For how the layers fit together, read [How Kiro Crew keeps you safe](../concepts/security.md) first. This page only sets values.

## Steps

### 1. Make a folder read-only

Two keys in `config.json` control this. Both are lists of absolute paths and both are empty by default, which changes nothing.

- `agent.sandbox_readonly_paths` (shown as **Sandbox Read-Only Paths**): folders the sandboxed agent may read and never write. A leading `~` is expanded.
- `agent.sandbox_readonly_exceptions` (shown as **Sandbox Read-Only Exceptions**): folders strictly inside one of those entries that stay writable.

The OS sandbox enforces them. On Linux that is a read-only bind mount in the namespace, WSL2 included. On macOS it is a write deny in the Seatbelt profile. A filesystem mounted below an entry becomes read-only too.

You can set a list from the CLI. The value goes in as base64 JSON, which keeps the quoting out of your shell:

```bash
kirocrew config set agent.sandbox_readonly_paths --value-base64=WyIvc3J2L2FyY2hpdmUiXQ==
kirocrew config set agent.sandbox_readonly_exceptions --value-base64=WyIvc3J2L2FyY2hpdmUvc2NyYXRjaCJd
```

That makes `/srv/archive` read-only and keeps `/srv/archive/scratch` writable. Swap in your own paths.

The change applies to sessions started after you make it. A chat that is already running keeps the sandbox it started with.

Some entries are skipped, each with a SECURITY warning in the log:

- A path that does not exist, is relative, or is `/`.
- A path that holds `/run/user/<uid>` or `/dev/shm`, where the Linux sandbox builds its masks.
- An exception that is not strictly inside an entry, or that would re-open a Kiro Crew mask or seal.

Kiro Crew's own masks and seals go on top of your list and always win, so a read-only entry can never expose a hidden path. In the other direction, making the project directory, the Kiro Crew data home or the agent's own state directories read-only breaks the agent there. Leave those out.

The fence only exists where Kiro Crew applies its own sandbox. It is not enforced when `agent.sandbox` is `off`, when a macOS spawn is delegated to kiro-cli's internal sandbox, or on Windows, which logs a SECURITY warning instead.

### 2. Know what happens when someone edits a settings file by hand

On a Linux host with the sandbox, a change to one of these four files that Kiro Crew did not write no longer applies by itself:

- `config.json`
- `config.local.json`
- `denied_commands.json`
- `computer_use.json`

The file keeps loading as the last version Kiro Crew saved. Ordinary saves to it are refused until you decide, and the refusal tells you to review the change in **Settings → Security**. A bell note and a dot in Settings point you there.

Open **Settings → Security**. The card is titled "`<file>` was changed outside Kiro Crew" and lists each changed key, for example "Changed `agent.sandbox` from … to …". Values of secrets show as "(value hidden)". Risky keys carry a hint, such as "Turns off the process sandbox." You then pick:

- **Apply** starts using the edit. A confirmation dialog repeats the security changes first. For an edit that turns the sandbox off, the button reads **Apply and turn off the sandbox**.
- **Discard** overwrites the file with the version Kiro Crew last saved. The outside edit is lost.

If the edited file is not valid JSON, you can only discard it. If the file was deleted, discard puts it back.

A gateway running without the dashboard has no card, so use the CLI from your own terminal:

```bash
kirocrew config pending
kirocrew config pending apply config.json <signature>
kirocrew config pending discard config.json <signature>
```

The first command lists each held file with what changed and prints the exact apply and discard lines, signature included. The signature names the version you were shown, so an edit made after you looked cannot ride your decision. Both commands refuse to run inside the agent sandbox. The agent cannot approve its own edits.

This is why step 1 matters on a Linux host. If you edit `config.json` in a text editor instead of using `kirocrew config set` or the dashboard, your fence waits for your own approval too.

### 3. Decide whether a deny rule can be overridden

When the command deny list refuses a shell command in a dashboard chat you are driving, Kiro Crew shows a card instead of a plain refusal. You can allow the command once or for the session, or reject it.

`agent.deny_override` (shown as **Deny Rule Override Card**) turns that card on and off. It is on by default. Set it to `false` and every such refusal is final: no card, no wait for an answer. Overrides you granted earlier stop applying while it is off, and apply again if you turn it back on, until that session ends. It is read on each request, so no restart is needed.

```bash
kirocrew config set agent.deny_override false
```

Turn it off on a machine where nobody sits at the dashboard to judge a card, or where you want the deny list to mean exactly what it says.

### 4. Keep the batch write guard on

`hooks.batch_write_guard` (shown as **Batch write guard**) is on by default in 0.13.0. It refuses a write sent in the same parallel tool batch as a read, but only when the write quotes an id or value the agent has not seen yet. That catches a guessed commit sha or issue number written before the read that would have returned it. A write beside a read that quotes nothing unseen goes through.

The guard is a discipline control, not a security control. The security floor runs first and is unchanged. `hooks.batch_write_guard_commands` (**Batch write guard commands**) is an empty list where you can add write-command prefixes the guard should treat as writes, such as `myctl apply`. It has no effect unless the guard is on.

You can still turn the guard off by setting `hooks.batch_write_guard` to `false` in `config.json`. The rest of this recipe assumes you leave it on.

### 5. Check the result

Open **Settings → Advanced**, titled "All settings". It lists every config key. Keys about the sandbox and approvals show as **Read only**, and the row says why. `agent.deny_override` and `hooks.batch_write_guard` both carry the reason "Read only: it decides what the agent may run, or do without asking you." The page shows them but does not change them.

For the two switches that do have a control, open **Settings → Security** and look at **Safety switches**. It holds the toggles for `mcp.protect_kiro_permission_rules` and `mcp.honour_auto_approve`.

Then test the fence from a new chat:

```prompt
Try to create a file called fence-test.txt inside /srv/archive, then try the same inside /srv/archive/scratch. Tell me which one worked and what error you got.
```

The first write should fail with a read-only filesystem error on Linux. The second should succeed.

## What can go wrong

**Problem:** You set `agent.sandbox_readonly_paths` and the agent can still write there.

**Fix:** Check that the entry is an absolute path that exists, and that the session started after your change. Then check `agent.sandbox`. With it `off`, or on a macOS spawn delegated to kiro-cli's internal sandbox, the list is not enforced. Look in the log for a SECURITY warning that names the skipped entry.

**Problem:** The agent breaks after you made a large folder read-only.

**Fix:** The folder probably holds the project directory, the Kiro Crew data home or the agent's own state directories. Narrow the entry, or add the writable part to `agent.sandbox_readonly_exceptions`.

**Problem:** A save in Settings is refused and says to review the change in **Settings → Security**.

**Fix:** A settings file was edited outside Kiro Crew and is waiting for review. Apply or discard it on the card, or run `kirocrew config pending` from your own terminal.

**Problem:** `kirocrew config pending apply` says the file is not held at that version.

**Fix:** The file changed again after you listed it. Run `kirocrew config pending` for the current signature and retry.
