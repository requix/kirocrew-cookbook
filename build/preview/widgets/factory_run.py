"""One issue down the factory line, as the software factory page sets it up.

content/widgets/factory-run.yaml holds the stages and the steps. load() checks every step against
the stages, and works out, per step, which stages were visited and which were re-entered. The
stage names are the page's own words, not dashboard labels. The JS only renders.
"""
from __future__ import annotations

from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "factory-run"


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "phases", "fence", "fence_label", "steps"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    phases = spec["phases"]
    if not 3 <= len(phases) <= 10 or len(set(phases)) != len(phases):
        raise _err("phases must be 3 to 10 unique stage names")
    fence = spec["fence"]
    if not fence or any(f not in phases for f in fence):
        raise _err("every fence stage must be one of the phases")
    idx = sorted(phases.index(f) for f in fence)
    if idx != list(range(idx[0], idx[-1] + 1)):
        raise _err("fence stages must be next to each other")
    steps_in = spec["steps"]
    if not 3 <= len(steps_in) <= 12:
        raise _err("a run needs 3 to 12 steps")
    if steps_in[-1]["phase"] != phases[-1]:
        raise _err(f"the last step must be {phases[-1]}")

    steps, visits = [], [0] * len(phases)
    for i, st in enumerate(steps_in, start=1):
        if st.get("phase") not in phases:
            raise _err(f"step {i} names unknown phase '{st.get('phase')}'")
        if not st.get("caption") or not st.get("who"):
            raise _err(f"step {i} needs a caption and a who")
        k = phases.index(st["phase"])
        visits[k] += 1
        steps.append({
            "phase": k,
            "who": st["who"],
            "caption": st["caption"],
            "visited": [n > 0 for n in visits],
            "reentered": [n > 1 for n in visits],
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
