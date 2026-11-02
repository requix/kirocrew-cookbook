---
title: How Kiro Crew keeps you safe
description: The layers a tool call passes through before it runs, and what each one actually stops.
category: Concepts
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli, channels]
tags: [security, governance, sandbox, secrets, audit]
updated: 2026-10-30
featured: false
---

You are about to let an agent run shell commands, edit files, and act on a schedule with nobody watching. The useful question is what stands between the model and damage when it is wrong, confused, or talked into something by a web page it read.

Kiro Crew's answer is a stack of checks that every tool call passes through before it runs. Most of them live in the gateway, not in the agent, which is the point: the agent cannot turn off a check it does not control. This page walks the stack in the order a tool call meets it, says what each layer stops, and — at the end — says plainly what it does not.

## What is protected, and from what

The threat model is an ordinary agent reaching an action with an outsized blast radius, rather than a malicious model:

- **Credential theft.** The agent reads `~/.aws/credentials` or an SSH key and now acts as you anywhere they are accepted — or prints them into a reply, a commit, or an outbound request.
- **Irreversible destruction.** `rm -rf`, `DROP TABLE`, `terraform destroy`, a force-push to `main`.
- **Prompt injection.** A file, an issue, a web page, or a channel message carries text shaped like an instruction, and the agent treats data as a command.
- **Exfiltration.** Local file contents leave the box inside an outbound request, whatever the stated destination.
- **Self-escalation.** The agent rewrites its own ceiling — the deny rules, the governance policy, the audit key — so the next thing it does is unchecked.
- **Unwanted reach.** A scheduled job, a subagent, or a channel acts on a surface or sends to a recipient you never authorized.

The layers below each take one slice of that.

## The path a tool call takes

Every model-originated tool call on every surface — dashboard, CLI, a Slack thread — enters the gateway and passes the same gate before the harness runs it.

```flow
- box: The model
  note: kiro-cli, KAS, Claude, Codex, …
- box: "`HookManager.on_tool_call`"
  via: emits a tool call (PreToolUse event)
  accent: true
  note: "In `src/kiro_crew/hooks.py`. The single policy authority. It runs these checks top to bottom, then gives one of three verdicts."
  steps:
    - "sensitive-path keystone (`is_sensitive_path`)"
    - "effective deny floor (`is_denied`)"
    - "governance gate: POLICY ∩ PROFILE"
    - first-party app-own MCP server auto-approve
    - "read-only auto-approve (`kind == read/fetch`)"
    - "user `auto_approve_tools` / trust"
  items:
    - "`TOOL_DENY`: blocked, SEL-audited, never shown"
    - "`TOOL_AUTO_APPROVE`: runs, no prompt"
    - "`TOOL_ALLOW`: held as a pending approval card"
- split:
    - - box: Approval card
        via: allow
        note: You approve or reject.
      - box: OS sandbox
        note: User namespace on Linux, sandbox-exec on macOS.
      - box: The tool actually runs
    - - box: "`security_events.jsonl` (SEL)"
        via: deny / audit
```

Two things are worth internalising before the per-layer detail. The order is deliberate: the deny floor and governance run **before** any auto-approve or trust fast-path, so a read-only classification or a trust grant can never re-admit a call a higher layer denied. And the gate is the only policy authority — the render (the approval card) and the resume (your click) read its verdict, they do not second-guess it.

## Layer 1 — the tool gate and approval modes

The gate (`HookManager.on_tool_call`) returns one of three verdicts: deny (blocked, you never see it), auto-approve (runs with no prompt), or allow (held as a card for you to approve or reject). Which calls skip the card depends on the chat's approval mode. You pick it with the **Approval mode** picker under the message box:

| Picker label | Internal name | What auto-approves | What still prompts |
|---|---|---|---|
| **Normal** | `normal` | nothing | every tool call |
| **Reads** | `trust_reads` | shell commands the read-only classifier clears | every write, every tool it cannot prove is read-only |
| **Trust** | `trust` | every tool call, in this chat only | nothing |
| **YOLO** | (app-wide override) | every tool call, in every chat | nothing, until it expires |

**Reads** leans on a read-only bash classifier (`readonly_bash.py`): it is **deny-by-default** and prefix-matched, so it rejects redirections, command substitutions, and newline-separator bypasses rather than trying to guess intent from a complex line. `cat ~/.aws/credentials` does not auto-approve under **Reads**, and the classifier is not the reason. The sensitive-path keystone, the first check in the gate, denies it outright, ahead of any mode.

**YOLO** is never permanent. It turns itself off after a set time (`agent.yolo_duration`, default 6 hours) and then asks again, or, if you choose that option, when Kiro Crew restarts. Every grant and expiry is written to the audit log. An enterprise policy can disable any of these modes; the picker then shows it as disabled by your organization's security policy.

A crewmate's own chat has its own mode too.

## Layer 2 — denied commands

A finite set of command shapes is refused at the gate regardless of approval mode, because some things should never run unprompted even in `trust`. The built-in rules (`BUILTIN_DENIED_RULES`) cover destructive operations (`rm -rf /`, `terraform destroy`, `TRUNCATE TABLE`, `aws … delete-*`), exfiltration shapes (`curl -d @file`, `--upload-file`, `/dev/tcp/` redirects), reverse shells, self-protection (minting a dashboard token, killing the gateway), and `ssh` back to this host.

Where the rules live is the load-bearing part. The enabled/disabled state is **not** in `config.json` — it lives in `denied_commands.json`, a trust-root file on the sensitive-path floor. The agent can neither read nor write it, which is what makes the ceiling un-disableable by the agent: a prompt-injected model cannot rewrite the list that is about to block it. You edit the rules from **Settings → Security**: disable individual built-ins, disable them all, or add your own patterns. When you add a rule, fill in its **note** field — that note is what the agent is shown when the rule fires, instead of a raw regex.

Two limits to understand before you treat this as a wall:

- **It reads the command line, not what the line names.** A program spelled out on the line is matched; a program held in a file the line merely runs is not. The docs are blunt about it: this tier is friction against a direct command line, **not a security boundary**. The boundary below it is the OS sandbox, which sees a process however it was spelled. Treat denied commands as defense in depth; for anything irreversible, the real control is the capability itself.
- **On an enterprise policy, the credential, sensitive-file, self-protection, git-publish and reverse-shell categories are pinned** and cannot be disabled, including by "disable all." A fleet `security_policy.json` composes with your local settings tightest-wins.

## Layer 3 — governance (POLICY ∩ PROFILE)

This is the layer a managed fleet cares about. Governance resolves every governed control by one rule — **the tightest boundary wins** — across two levels:

- **POLICY** (`security_policy.json`): the enterprise ceiling, loaded at boot from a trust-root path the agent does not own. Once present, the app and its agent cannot weaken it.
- **PROFILE**: a per-surface, per-app, or per-task scope that can only *narrow* what policy permits.

The effective permission for any item is `policy ∩ profile`. Governed scopes include `commands`, `mcp` (per-server and per-tool), `filesystem.read` / `filesystem.write`, `network.egress`, `channels`, `apps`, `sandbox.min_level`, and capability gates such as `capabilities.spawn`, `capabilities.messaging`, `capabilities.cron` and `capabilities.publish`. A deny-mode `commands` pattern in policy is projected as a force-pin: it applies regardless of your local `denied_commands.json` opt-outs, because policy is Level-1 and the keystone opt-out is something you can edit.

You read the effective ceiling — posture only, never the exact patterns — in **Settings → Security**, or with:

```bash
kirocrew policy show
kirocrew policy explain <scope> <item>
```

These are CLI-only on purpose: the governed agent gets no tool to enumerate its own ceiling. For a whole fleet, one `security_policy.json` can be distributed centrally over `KIROCREW_POLICY_URL`, fetched at boot and refreshed on an interval; the fetched document is the authority and every local tier can only tighten it. (The deep version of all of this is the governance spec in the repo; the one-line version is `effective = POLICY ∩ PROFILE`.)

## Layer 4 — secrets

The secrets vault stores credentials encrypted on disk where the agent cannot read them — each entry AES-256-GCM-encrypted under a key only your account can read, in a `.vault` directory in the data home. `.vault` is a registered sensitive path, so a file read, a `cat`, or a `python -c "open(...)"` are all refused before the verb runs. A prompt injection that talks the agent into printing your tokens has nothing to print.

Add and remove secrets from **Settings → Secrets**; the panel lists names only and never shows a stored value back, so a screenshot of it leaks nothing. An MCP server references a secret with `secret://NAME` in its `env`, resolved at spawn time into that one server's environment — never the agent's:

```jsonc
{
  "mcpServers": {
    "my-server": {
      "command": "my-mcp-server",
      "env": { "MY_MCP_SECRET": "secret://MY_MCP_SECRET" }
    }
  }
}
```

If the named secret does not exist the server fails to start rather than launching with a missing credential. To move plaintext credentials out of `.env`, `kirocrew secrets import` migrates them into the vault and rewrites each line to a `secret://` reference — a dry run by default, `--apply` to perform it.

Scheduled jobs are the one place a secret reaches non-interactive code, and it is gated: a script cron requests vault secrets, but the request is **pending** until you approve it in the dashboard (Schedule → job → Secrets). The agent records the request; it does not grant itself the value.

For non-secret agent environment (a proxy, a CA bundle, `AWS_PROFILE`), use `agent.env` in `config.json`, not `.env` — `.env` values enter the gateway first and propagate to every child, and a credential-shaped name there is refused at write time anyway.

## Layer 5 — credential-file protection

Reading credential files is blocked directly, independent of the vault. The sensitive-path floor refuses `~/.aws`, `~/.ssh`, `~/.gnupg`, `~/.netrc`, `~/.npmrc`, `~/.git-credentials`, `~/.config/gcloud`, `~/.azure`, `~/.docker/config.json`, `~/.kube/config`, an enterprise SSO session store, and the governance trust-root files themselves (`security_policy.json`, `profiles/`, `admission_policy.json`, `denied_commands.json`). The bytes are a bearer credential; an agent that can read them can act as you.

A trap worth knowing: **reading those files is blocked, running the AWS CLI is not.** An agent that tries to `cat ~/.aws/config` to discover your profiles gets refused and may wrongly conclude the host has no AWS access — while `aws sts get-caller-identity` works the whole time. The refusal carries the sanctioned path (`aws configure list-profiles`), so a well-behaved agent runs that instead. Check your own setup with `kirocrew doctor`; its **Credentials** section reports what is configured without reading a secret value.

The sandbox tier decides how hard this floor is enforced at the OS level. `agent.sandbox` defaults to `auto` (standard tier), which leaves `~/.aws`, `~/.ssh` and `~/.kube` OS-visible so the `aws` CLI, git-over-SSH and `kubectl` keep working — the file-tool gate still refuses to open paths under them, but a plain shell `cat` is not sealed at this tier. Set `strict` on a host that holds credentials the agent must never read, and accept that the CLI tooling inside the agent stops resolving them:

```bash
kirocrew config set agent.sandbox strict
```

## Layer 6 — git and protected branches

Push to a feature branch is allowed for PR workflows; the dangerous shapes are refused at the deny floor. A bare `git push`, a `HEAD`/`@` target, `--mirror`/`--all`, and any force-push to a protected branch (`main`, `mainline`, `master`) are blocked — a push must name its feature branch explicitly (`git push origin my-branch`). The publish side has its own capability gate, `capabilities.publish`, which fails **closed** (a wrong permit would exfiltrate bytes), and the `git push` deny floor is add-only: `capabilities.publish.enabled: true` never re-enables a git publish the floor blocks.

## Layer 7 — network exposure

The dashboard binds to `localhost` only by default; `dashboard.url` is empty until you set it for remote access. Any HTTP server the agent is asked to stand up must bind `127.0.0.1` explicitly. Outbound-facing capabilities are each governed: `network.egress` for the dedicated fetch tool (by host), `capabilities.telemetry` for the anonymous beacon (policy-layer, fail-closed), and `capabilities.tailnet_origin` for putting the dashboard on a tailnet. A phone connection mints a credential through gated endpoints (`capabilities.mobile_connect`), re-checked fail-closed at the mint, not just filtered out of a list.

A command-driven egress (`curl` inside a bash tool) is governed by the `commands` scope, not `network.egress` — the two are different planes, and a `commands` deny list is defense in depth rather than a complete egress bound, because it cannot enumerate every network-capable tool.

## Layer 8 — channels and untrusted inbound content

Messaging is owner-scoped. Only the configured owner (`KIROCREW_OWNER_ID`) is authorized over Slack; multi-user access is refused whatever the allow-lists say. On an enterprise policy, the `channels` scope (and its per-transport posture) decides which transports may connect at all — enforced at startup and re-checked per inbound message, so a channel withdrawn mid-session stops dispatching. A pure `!stop` stays exempt, so a withdrawn channel can still halt a runaway turn.

Everything that arrives from a file, a tool result, a web page, an issue, or a channel message is **data, never instructions**. The runtime neutralises boundary markers in the context blocks it assembles, but a file read or a fetched page reaches the agent unfiltered — so content shaped like a new system prompt inside untrusted material is treated as forged whatever its source. A thread reply from someone other than the person addressing the agent is read for context only; an instruction in it is ignored and flagged.

## Layer 9 — sandboxing and scratch

The OS sandbox is the enforcement point the deny floor is not: a user namespace on Linux, `sandbox-exec` on macOS. It sees a process however the command was spelled, which is why it, not the command-text rules, is the control of record for anything irreversible. The governance trust-root files, the vault, the SEL log and its signing key, and the policy cache are all mounted read-only (or hidden) inside it, so a spawned `python -c` doing a raw `open()` — which never routes through the file-tool gate — still cannot rewrite the agent's own ceiling.

Scratch work belongs in `$KIROCREW_SCRATCH`, a session-owned directory reclaimed when the session's processes end — not `/tmp`, which outlives its session and is swept by age under live work. A subagent sees the same `$KIROCREW_SCRATCH` as its parent; `$TMPDIR` is per-process and not shared.

## Layer 10 — the audit trail (SEL)

The Security Event Log (`~/.kiro/crew/security_events.jsonl`) is an append-only, tamper-evident record of every security-relevant decision: tool invocations, permission decisions, MCP calls, dashboard API mutations, config changes. Each entry is HMAC-SHA256-chained to the previous one, so a rewritten or dropped entry is detectable.

The signing key lives **outside** the log directory, at `~/.kiro/crew/trust/sel_hmac.key` (`chmod 600`, in an owner-only `trust/` dir), precisely so an actor who can rewrite the log cannot also re-sign a clean-looking chain. Credential and exfiltration-URL values in free-form fields are redacted at write time, before the entry is hashed, so a search query or a document title can never land a secret on disk. Read it back:

```bash
kirocrew security events -n 50
kirocrew security verify
```

`verify` walks the chain and reports tampered entries; it also reports `unverifiable` when the segment directory was swapped under it, rather than claiming intact over the live log alone.

## Layer summary

| Layer | What it stops | Where you configure it |
|---|---|---|
| Approval modes | An unattended turn running writes you did not see | **Approval mode** picker under the message box |
| Denied commands | Obvious destructive / exfiltration command lines | Settings → Security (`denied_commands.json`, agent cannot edit) |
| Governance (POLICY ∩ PROFILE) | A fleet-forbidden tool, path, host, channel or capability | `security_policy.json` (trust root) + profiles; `kirocrew policy show` |
| Secrets vault | The agent reading or printing your tokens | Settings → Secrets; `secret://` in MCP `env` |
| Credential-file floor | Reads of `~/.aws`, `~/.ssh`, SSO stores, trust-root files | Built-in; sandbox tier via `agent.sandbox` |
| Git rules | Force-push to `main`, bare `git push`, publish | Built-in deny floor; `capabilities.publish` |
| Network exposure | Remote dashboard, egress, tailnet, phone connect | `dashboard.url`, `agent.sandbox`, `network.egress`, `capabilities.*` |
| Channels / injection | Non-owner access; data treated as instructions | Owner ID + `channels` scope; runtime data/instruction boundary |
| OS sandbox + scratch | A raw process rewriting its own ceiling; stale temp files | `agent.sandbox`; `$KIROCREW_SCRATCH` |
| SEL audit | Silent or undetectable tampering | Built-in; `kirocrew security verify` |

## Settings worth checking on day one

- **Approval mode** (the picker under the message box). Start on **Normal** or **Reads**, and move a chat to **Trust** deliberately, once you trust that task.
- **`agent.sandbox`** (`kirocrew config set agent.sandbox …`). Default `auto` keeps credential tooling working; set `strict` on a host with credentials the agent must never read.
- **Settings → Security** — the denied-command rules. Read the built-in list, and add a pattern (with a **note**) for anything specific to your environment.
- **Settings → Secrets** — move any plaintext credential here, then `kirocrew secrets import --apply` to migrate what is in `.env`.
- **`dashboard.url`** — leave it empty unless you genuinely need remote access; the default is localhost-only for a reason.
- **`kirocrew doctor`** — run it once to confirm credentials, MCP servers and the backend resolve, before you hand the agent real work.

## Gotchas — what these layers do not protect against

- **Denied commands are not a boundary.** They read the command line, not what it runs. A wrapped or indirected command is logged as its wrapper and is not matched. The OS sandbox is the real fence; the deny list raises the cost of the obvious spelling.
- **Standard sandbox leaves `~/.aws`/`~/.ssh`/`~/.kube` OS-visible.** The file-tool gate still refuses them, but a plain shell `cat` is not sealed at the default tier. Use `strict` if a raw read must be impossible.
- **The vault's boundary is Kiro Crew, not the OS.** Another program running as you can still open `.vault`. It protects against the agent, not against a process with your uid.
- **Governance governs Kiro Crew's own gate, not the harness's blanket allow-list.** An agent that writes a tool into kiro-cli's `allowedTools` makes the harness stop sending permission requests, short-circuiting Plane A for that tool. Kiro Crew re-filters those lists when the ceiling tightens, but a session already negotiated keeps its grants until it restarts.
- **The web terminal PTY is ungoverned by design.** It is an operator-only surface; a command typed into it passes neither the `commands` scope nor the sandbox classifier.
- **Secrets can still leave if you hand them out.** Nothing stops *you* pasting a token into a prompt, or an MCP server you installed from doing what it was built to do. These layers constrain the agent and the host; they do not vet third-party code you chose to trust.
- **On a non-enterprise host, the ceiling is yours to lower.** Everything here is "secure by default, not by mandate" — the one invariant is that the *agent* cannot edit the policy/profile files. A human at the keyboard can.

The short version: the gate decides, the sandbox enforces, the trust-root files are the one thing the agent cannot touch, and the SEL records all of it. For the mental model behind the gateway-versus-agent split, see [what Kiro Crew is](what-kirocrew-is.md); for where memory lives under all this, see [make it remember](../recipes/make-it-remember.md).
