---
title: Trace every agent turn
description: Turn on OpenTelemetry traces for agent turns, read one as a waterfall from the CLI, and send them to Langfuse or any OTLP collector.
category: Recipes
difficulty: intermediate
time: 15 min
surfaces: [dashboard, cli]
tags: [observability, telemetry, traces, opentelemetry, langfuse]
updated: 2026-11-19
featured: false
prerequisites:
  - Kiro Crew 0.13.0 or later
  - For export only, a collector that accepts OTLP over HTTP
---

**Problem.** An agent turn took four minutes and you do not know where the time went. It might be the model, a slow tool, an approval nobody answered, or a compaction. Logs do not show the shape of a turn. A trace does: one record per turn, with a span for each model call and each tool call, laid out in time.

Kiro Crew 0.13.0 can write those traces. They are off by default, they stay on your machine until you name a collector, and they do not hold your text.

## What a trace holds

One trace per agent turn. Inside it you get:

- the model, and credits and tokens where the backend reports them
- one span per model call
- one span per tool call
- compactions, approval waits and steers that happened during the turn
- for conductor mode and workflows, one trace per round (conductor mode) or per phase (workflow), so a round reads as one waterfall

See [conductor mode](../concepts/conductor-mode.md) for what a round is.

## What a trace never holds

Every attribute on a span comes from a fixed allowlist in the code. Anything not on the list is dropped before it is written. That list does not include:

- prompt or reply text
- tool arguments or tool output
- file paths
- MCP server names or MCP tool names

Session keys name a conversation, so they are not written raw to anything that leaves the host. The export carries a keyed hash of the key instead. The raw key sits under `kirocrew.local.*` attributes, and those are removed from every span before it is sent.

## Steps

### 1. Turn traces on

Traces are controlled by `telemetry.traces_enabled`. It is `false` by default, and while it is off nothing is loaded. It is independent of the metrics switch `telemetry.enabled`, so you can have one without the other.

```bash
kirocrew config set telemetry.traces_enabled true
```

You can also set it in **Settings → Advanced**, which lists every config key. The setting is labelled **Traces Enabled**.

### 2. Run a turn

Start a chat, run a task, anything that makes the agent take a turn. Spans are written to local files under `~/.kiro/crew/traces` as `spans-*.jsonl`. The directory is pruned by the same **Retention (days)** and **Max Total Size (MB)** settings as local metrics (`telemetry.retention_days`, `telemetry.max_total_mb`), and the traces directory gets its own size budget.

### 3. Read one turn as a waterfall

```bash
kirocrew trace show <key>
```

`<key>` can be a turn id, a session key or id, an ACP session id or a trace id. The command prints the most recent trace holding that key as an indented tree. You get a time bar per span, the sub-agents, and a line for each stretch where nothing under a parent was running. Those gaps are usually the answer to "where did the time go".

The command only reads the local files. It needs no running gateway and no OpenTelemetry SDK. It shows span names, timing and the error type, nothing else.

Here is a sample turn drawn the same way. Click a bar to see what that span records.

```widget trace-waterfall
```

### 4. Send traces to a collector (optional)

Local files are enough for step 3. To see traces in Langfuse, CloudWatch or another OTLP backend, set the endpoint to the full OTLP/HTTP traces URL, path included:

```bash
kirocrew config set telemetry.traces_otlp_endpoint https://cloud.langfuse.com/api/public/otel/v1/traces
```

The endpoint is only read while `telemetry.traces_enabled` is on. Some rules to know:

- It must be `https://`, unless the host is loopback (a collector on the same machine).
- It cannot carry `user:password`, a query string or a fragment. A credential goes in a header, see below.
- If you leave it empty, Kiro Crew falls back to the standard `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` and `OTEL_EXPORTER_OTLP_ENDPOINT` environment variables. The config key wins when both exist.
- It obeys the `capabilities.telemetry` `otlp_hosts` policy, and an LTS build ignores it.

### 5. Put the auth header in Settings → Secrets

A collector wants a header such as `Authorization`. Do not put its value in config. Store the whole header value as a secret under **Settings → Secrets**, then point the config at the secret's name.

For Langfuse, the value is `Basic <base64 of public_key:secret_key>`. Save it as a secret named `LANGFUSE_OTLP_AUTH`, then map the header to that name:

```bash
kirocrew config set telemetry.traces_otlp_headers_secret '{"Authorization": "LANGFUSE_OTLP_AUTH"}'
```

The map is header name to secret name. Kiro Crew reads the secret when the exporter is built and never logs the value. These headers go to `telemetry.traces_otlp_endpoint` only. They are never sent to an endpoint that came from the environment.

If you would rather keep the value in an environment variable, `telemetry.traces_otlp_headers_env` does the same with a variable name instead of a secret name.

For an AWS X-Ray endpoint such as `https://xray.us-east-1.amazonaws.com/v1/traces`, the same pattern works with an API key stored as `Bearer <key>`.

### 6. Verify it worked

1. Run a turn.
2. Run `kirocrew trace show <session key>` and check you get a tree back.
3. Open your collector. The turn should appear in the collector. In Langfuse, the model call shows up as a generation with its usage.

## Two related settings

**`kirocrew models`** lists the model names that `--model` accepts and marks the default with `*`. Add `--json` for a script, or pass a name to check it: `kirocrew models claude-sonnet` exits 1 with the closest match if the name is not valid. Handy when a trace shows a model you did not expect.

**`telemetry.plan_alert_pcts`** sends one notification per plan period when your plan's credits cross each percentage you list. There is no settings page for it yet:

```bash
kirocrew config set telemetry.plan_alert_pcts "[50, 80, 100]"
```

The dashboard has to be open, because the reading is taken when the credit pill refreshes.

## What can go wrong

**Problem:** `kirocrew trace show` finds nothing.

**Fix:** Check that `telemetry.traces_enabled` was on before the turn ran. Traces are not recorded after the fact. Then try the trace id instead of a session key.

**Problem:** Local files are written but nothing reaches the collector.

**Fix:** Two causes cover most cases. The endpoint is plain `http://` to a non-loopback host, or its host is blocked by the `otlp_hosts` policy. Or a header cannot be read: a secret name that does not exist, a value that is not a secret name, or an unset environment variable turns export off, with one warning that names the header and never the value.

**Problem:** You want conductor mode turns as separate traces.

**Fix:** The default `telemetry.traces_conductor_mode` is `run`, one trace per round. Set it to `turn` and every turn becomes its own trace, joined by the shared `kirocrew.crew.root` and `kirocrew.work.item_id` attributes.
