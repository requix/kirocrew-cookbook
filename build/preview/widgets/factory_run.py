"""One issue down the line, drawn like an Issue Radar item lane.

content/widgets/factory-run.yaml holds the phases and the steps. load() checks every phase name
against the Item lanes columns of v0.13.0 and works out, per step, which phases were visited,
which were re-entered and the pull-request chip. The JS only renders.
"""
from __future__ import annotations

from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "factory-run"
# The Item lanes phase columns in the v0.13.0 Issue Radar Pipeline dashboard, in order.
CONFIRMED_PHASES = ["SELECTED", "CLAIMED", "INVESTIG.", "IMPLEMENT", "AWAIT CI", "ADDR REV", "AWAIT MRG", "RESOLVED"]
CONFIRMED_FENCE = ["IMPLEMENT", "ADDR REV"]


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "phases", "fence", "fence_label", "steps"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    phases = spec["phases"]
    if phases != CONFIRMED_PHASES:
        raise _err(f"phases must be the v0.13.0 Item lanes columns {CONFIRMED_PHASES}")
    if spec["fence"] != CONFIRMED_FENCE:
        raise _err(f"fence must be {CONFIRMED_FENCE}, the phases that hold a dirty worktree")
    steps_in = spec["steps"]
    if not 3 <= len(steps_in) <= 12:
        raise _err("a run needs 3 to 12 steps")
    if steps_in[-1]["phase"] != phases[-1]:
        raise _err(f"the last step must be {phases[-1]}")

    steps, visits, pr = [], [0] * len(phases), None
    for i, st in enumerate(steps_in, start=1):
        if st.get("phase") not in phases:
            raise _err(f"step {i} names unknown phase '{st.get('phase')}'")
        if not st.get("caption") or not st.get("who"):
            raise _err(f"step {i} needs a caption and a who")
        k = phases.index(st["phase"])
        visits[k] += 1
        pr = st.get("pr", pr)
        steps.append({
            "phase": k,
            "who": st["who"],
            "caption": st["caption"],
            "visited": [n > 0 for n in visits],
            "reentered": [n > 1 for n in visits],
            "pr": f"#{pr}" if pr else "",
        })
    data = {
        "title": spec["title"],
        "phases": phases,
        "fence": [phases.index(p) for p in spec["fence"]],
        "fence_label": spec["fence_label"],
        "steps": steps,
    }
    check_text(NAME, {"title": data["title"], "fence_label": data["fence_label"],
                      "steps": [[s["who"], s["caption"]] for s in steps]})
    return data


def markdown(data: dict) -> str:
    rows = [f"**{data['title']}**", "", "| Step | Phase | Who | What happens |", "| --- | --- | --- | --- |"]
    for i, s in enumerate(data["steps"], start=1):
        rows.append(f"| {i} | {data['phases'][s['phase']]} | {s['who']} | {s['caption']} |")
    return "\n".join(rows)
