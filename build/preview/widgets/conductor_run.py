"""A conductor mode run, step by step.

content/widgets/conductor-run.yaml holds the steps and the node states. load() checks that every
step names known nodes and states, then derives what the Board shows (Needs you, Milestones,
Recap) from the worker states, following the rules of the v0.13.0 dashboard. The JS only renders.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from . import WidgetError

# Board wording confirmed in the v0.13.0 UI strings (en.manual.json, conductor_mode_*).
CONFIRMED_LABELS = {
    "board": "Board",
    "recap": "Recap",
    "needs_you": "Needs you",
    "milestones": "Milestones",
    "paused": "Paused",
    "pause_all": "Pause all",
    "resume_all": "Resume all",
    "recap_empty": "The crew has not reported yet.",
    "needs_you_none": "Nothing needs you right now.",
    "milestones_none": "No milestones yet.",
}
# Row labels in the Milestones list that the UI strings confirm.
CONFIRMED_BOARD_ROWS = {"", "Not started", "In progress", "Waiting on your approval above", "Paused", "Done", "Stalled"}
CONTROLS = {"pause_all", "resume_all"}
FORBIDDEN = ("·", "→", "->")


def _err(msg: str) -> WidgetError:
    return WidgetError(f"conductor-run.yaml: {msg}")


def recap(workers: list[dict]) -> str:
    """The Recap line, built the way the Board builds it (recap_head, recap_waiting, recap_running)."""
    listed = [w for w in workers if w["state"] != "absent"]
    if not listed:
        return CONFIRMED_LABELS["recap_empty"]
    done = sum(w["state"] == "done" for w in listed)
    head = f"{done} of {len(listed)} done"
    waiting = [w["name"] for w in listed if w["state"] == "waiting"]
    running = sum(w["state"] in ("working", "drifting") for w in listed)
    if len(waiting) == 1:
        return f"{head}; {waiting[0]} is waiting on you."
    if waiting:
        return f"{head}; {', '.join(waiting)} are waiting on you."
    if running:
        return f"{head}; {running} running."
    return f"{head}."


def load(project: Path) -> dict:
    path = Path(project) / "content" / "widgets" / "conductor-run.yaml"
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise _err(f"cannot read: {exc}") from exc
    if not isinstance(spec, dict):
        raise _err("must be a mapping")
    for key in ("title", "labels", "conductor", "workers", "worker_states", "steps"):
        if key not in spec:
            raise _err(f"missing '{key}'")

    labels = spec["labels"]
    for key, text in labels.items():
        if key not in CONFIRMED_LABELS:
            raise _err(f"unknown label '{key}'")
        if text != CONFIRMED_LABELS[key]:
            raise _err(f"label '{key}' must read '{CONFIRMED_LABELS[key]}' (the v0.13.0 Board wording), not '{text}'")
    missing = set(CONFIRMED_LABELS) - set(labels)
    if missing:
        raise _err(f"missing labels {sorted(missing)}")

    cstates = spec["conductor"].get("states") or {}
    if not cstates:
        raise _err("conductor has no states")
    wstates = spec["worker_states"]
    if "absent" not in wstates:
        raise _err("worker_states needs 'absent'")
    for sid, s in wstates.items():
        if s["board"] not in CONFIRMED_BOARD_ROWS:
            raise _err(f"worker state '{sid}': Board label '{s['board']}' is not in the v0.13.0 strings")

    workers = spec["workers"]
    ids = [w["id"] for w in workers]
    if len(set(ids)) != len(ids) or not ids:
        raise _err("worker ids must be unique and not empty")
    if not 3 <= len(ids) <= 4:
        raise _err("show three or four workers")
    names = {w["id"]: w["name"] for w in workers}

    steps_in = spec["steps"]
    if not 2 <= len(steps_in) <= 9:
        raise _err("a run needs between 2 and 9 steps")

    steps = []
    for i, st in enumerate(steps_in, start=1):
        where = f"step {i}"
        if not st.get("caption"):
            raise _err(f"{where} has no caption")
        if st["conductor"] not in cstates:
            raise _err(f"{where} names unknown conductor state '{st['conductor']}'")
        wmap = st.get("workers") or {}
        for wid in wmap:
            if wid not in names:
                raise _err(f"{where} names unknown worker '{wid}'")
        if set(wmap) != set(ids):
            raise _err(f"{where} must give a state for every worker")
        for wid, s in wmap.items():
            if s not in wstates:
                raise _err(f"{where} gives worker '{wid}' unknown state '{s}'")
        control = st.get("control")
        if control is not None and control not in CONTROLS:
            raise _err(f"{where} has unknown control '{control}'")
        cells = [{"id": w["id"], "name": w["name"], "task": w["task"], "state": wmap[w["id"]],
                  "label": wstates[wmap[w["id"]]]["node"], "board": wstates[wmap[w["id"]]]["board"]}
                 for w in workers]
        listed = [c for c in cells if c["state"] != "absent"]
        steps.append({
            "caption": st["caption"],
            "conductor": {"state": st["conductor"], "label": cstates[st["conductor"]]["label"]},
            "workers": cells,
            "needs_you": [c["name"] for c in cells if c["state"] == "waiting"],
            "milestones": f"{sum(c['state'] == 'done' for c in listed)} of {len(listed)}" if listed else "",
            "recap": recap(cells),
            "paused": bool(st.get("crew_paused")),
            "control": labels[control] if control else "",
        })

    data = {
        "title": spec["title"],
        "labels": labels,
        "conductor": {"name": spec["conductor"]["name"]},
        "steps": steps,
    }
    _check_text(data)
    return data


def _check_text(node) -> None:
    if isinstance(node, str):
        for bad in FORBIDDEN:
            if bad in node:
                raise _err(f"visible text must not contain '{bad}': {node!r}")
    elif isinstance(node, dict):
        for v in node.values():
            _check_text(v)
    elif isinstance(node, list):
        for v in node:
            _check_text(v)


def markdown(data: dict) -> str:
    rows = ["**" + data["title"] + "**", "", "| Step | What happens | Recap on the Board |", "| --- | --- | --- |"]
    for i, s in enumerate(data["steps"], start=1):
        rows.append(f"| {i} | {s['caption']} | {s['recap']} |")
    return "\n".join(rows)
