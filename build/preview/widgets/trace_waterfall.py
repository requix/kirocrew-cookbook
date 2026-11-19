"""A sample agent turn drawn as a trace waterfall.

content/widgets/trace-waterfall.yaml holds the spans. load() checks every span name and attribute
key against what the v0.13.0 tracing code writes, so the card cannot show something a real trace
never holds. The JS only draws bars and the details of the clicked one.
"""
from __future__ import annotations

from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "trace-waterfall"

# Span names written by kiro_crew/tracing (turns.py, steps.py) in v0.13.0. Tool spans are
# "execute_tool <name or kind>" and the turn span is "invoke_agent <agent>".
SPAN_NAMES = {"chat", "user.prompt", "turn.complete", "kirocrew.step", "kirocrew.compaction",
              "kirocrew.approval", "kirocrew.steer"}
SPAN_PREFIXES = ("invoke_agent ", "execute_tool ")

# The export allowlist (kiro_crew/tracing/correlation.py) minus the ids and hashes that only
# join spans together. A key not on this list is dropped before a span is written.
ALLOWED_ATTRS = {
    "gen_ai.operation.name", "gen_ai.agent.name", "gen_ai.request.model", "gen_ai.response.model",
    "gen_ai.tool.name", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens",
    "kirocrew.attempt", "kirocrew.tool_kind", "kirocrew.tool.outcome", "kirocrew.stop_reason",
    "kirocrew.usage.credits", "kirocrew.usage.cost_usd", "kirocrew.usage.model_calls",
    "kirocrew.usage.complete", "kirocrew.step.index", "kirocrew.step.derived",
    "kirocrew.compaction.outcome", "kirocrew.steer.mode", "kirocrew.approval.wait_ms",
    "kirocrew.approval.decided_by", "kirocrew.approval.outcome", "kirocrew.queue.wait_ms",
}


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "total", "never", "spans", "start"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    total = spec["total"]
    if not isinstance(total, (int, float)) or total <= 0:
        raise _err("'total' must be a positive number of seconds")
    spans_in = spec["spans"]
    if not 3 <= len(spans_in) <= 12:
        raise _err("show between 3 and 12 spans")
    ids = [s["id"] for s in spans_in]
    if len(set(ids)) != len(ids):
        raise _err("span ids must be unique")
    if spec["start"] not in ids:
        raise _err("'start' must name a span")

    spans = []
    for s in spans_in:
        where = f"span '{s['id']}'"
        name = s.get("name", "")
        if name not in SPAN_NAMES and not name.startswith(SPAN_PREFIXES):
            raise _err(f"{where}: '{name}' is not a span name v0.13.0 writes")
        if not 0 <= s["start"] <= s["end"] <= total:
            raise _err(f"{where}: needs 0 <= start <= end <= total")
        if not s.get("about"):
            raise _err(f"{where} has no 'about'")
        for key in s.get("attrs") or {}:
            if key not in ALLOWED_ATTRS:
                raise _err(f"{where}: attribute '{key}' is not on the v0.13.0 export allowlist")
        spans.append({
            "id": s["id"], "name": name, "about": s["about"], "depth": int(s.get("depth", 1)),
            "slow": bool(s.get("slow")),
            "left": round(100 * s["start"] / total, 3),
            "width": round(100 * (s["end"] - s["start"]) / total, 3),
            "secs": s["end"] - s["start"],
            "attrs": [[k, str(v).lower() if isinstance(v, bool) else str(v)] for k, v in (s.get("attrs") or {}).items()],
        })

    data = {"title": spec["title"], "total": total, "never": spec["never"], "spans": spans,
            "start": ids.index(spec["start"])}
    check_text(NAME, {"title": data["title"], "never": data["never"], "about": [s["about"] for s in spans]})
    return data


def markdown(data: dict) -> str:
    rows = [f"**{data['title']}**", "", "| Span | Seconds | What it records |", "| --- | --- | --- |"]
    for s in data["spans"]:
        attrs = ", ".join(f"`{k}`" for k, _ in s["attrs"]) or "timing only"
        rows.append(f"| `{s['name']}` | {s['secs']:g} | {attrs} |")
    rows += ["", data["never"]]
    return "\n".join(rows)
