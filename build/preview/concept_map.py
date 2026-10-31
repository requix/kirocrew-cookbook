"""Data for the "How the pieces fit" concept map.

concept-map.yaml holds the drawing (nodes, links) and what each step adds.
The step TEXT is the page itself: every "### N. Title" section of
how-it-fits.md is one step. So the words live in one place, the page reads
fine without JavaScript, and the build fails when the two drift apart.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import yaml

esc = html.escape
STEP_RE = re.compile(r"^### (\d+)\. ", re.M)


class ConceptMapError(Exception):
    pass


def load(project: Path, page_body: str) -> dict:
    spec = yaml.safe_load((project / "content" / "concepts" / "concept-map.yaml").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in spec["nodes"]}
    container = spec["container"]
    ids = set(nodes) | {container["id"]}
    links = []
    for a, b, text in spec["links"]:
        if a not in nodes or b not in nodes:
            raise ConceptMapError(f"concept-map.yaml: link {a}>{b} names an unknown node")
        links.append({"id": f"{a}>{b}", "from": a, "to": b, "label": text})
    link_ids = {l["id"] for l in links}

    numbers = [int(n) for n in STEP_RE.findall(page_body)]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ConceptMapError(f"how-it-fits.md: step headings must be ### 1. … ### N. in order, found {numbers}")
    if len(numbers) != len(spec["steps"]):
        raise ConceptMapError(f"how-it-fits.md has {len(numbers)} numbered steps, concept-map.yaml has {len(spec['steps'])}")

    first_step: dict[str, int] = {}
    for i, step in enumerate(spec["steps"], start=1):
        for item in step.get("show", []) + step.get("mark", []):
            if item not in ids and item not in link_ids:
                raise ConceptMapError(f"concept-map.yaml: step {i} names unknown '{item}'")
        for item in step.get("show", []):
            first_step.setdefault(item, i)
    missing = (ids | link_ids) - set(first_step)
    if missing:
        raise ConceptMapError(f"concept-map.yaml: never shown by any step: {sorted(missing)}")

    w, h = spec["canvas"]
    out_nodes = []
    for n in spec["nodes"]:
        x, y = n["at"]
        nw, nh = n.get("size", [140, 52])
        if x < 0 or y < 0 or x + nw > w or y + nh > h:
            raise ConceptMapError(f"concept-map.yaml: node '{n['id']}' does not fit the {w}x{h} canvas")
        out_nodes.append({"id": n["id"], "name": n["name"], "sub": n.get("sub") or "", "x": x, "y": y, "w": nw, "h": nh,
                          "step": first_step[n["id"]]})
    _check_layout({"w": w, "h": h, "at": {n["id"]: [n["x"], n["y"], n["w"], n["h"]] for n in out_nodes}}, links)
    return {
        "w": w, "h": h,
        "container": {**container, "step": first_step[container["id"]]},
        "nodes": out_nodes,
        "links": [{**l, "step": first_step[l["id"]]} for l in links],
        "steps": [{"show": s.get("show", []), "mark": s.get("mark", [])} for s in spec["steps"]],
    }


def _check_layout(layout: dict, links: list) -> None:
    """No two nodes overlap, and no arrow runs through a box it does not join."""
    at = layout["at"]
    ids = list(at)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (ax, ay, aw, ah), (bx, by, bw, bh) = at[a], at[b]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                raise ConceptMapError(f"concept-map.yaml: nodes '{a}' and '{b}' overlap")
    centre = lambda r: (r[0] + r[2] / 2, r[1] + r[3] / 2)
    for l in links:
        (x1, y1), (x2, y2) = centre(at[l["from"]]), centre(at[l["to"]])
        steps = max(1, int(max(abs(x2 - x1), abs(y2 - y1)) / 2))
        for nid, (x, y, nw, nh) in at.items():
            if nid in (l["from"], l["to"]):
                continue
            for k in range(steps + 1):
                px, py = x1 + (x2 - x1) * k / steps, y1 + (y2 - y1) * k / steps
                if x + 2 < px < x + nw - 2 and y + 2 < py < y + nh - 2:
                    raise ConceptMapError(f"concept-map.yaml: the arrow {l['id']} runs through '{nid}'")


def widget_html(data: dict, rel: str) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<div class="cm" data-concept-map>
<div class="cm-text" data-cm-text></div>
<div class="cm-side">
<div class="cm-sticky">
<ol class="cm-chips" aria-label="Steps"></ol>
<div class="cm-frame"><div class="cm-canvas" role="group" aria-label="Diagram of how the pieces fit"></div></div>
<div class="cm-bar"><button type="button" class="vc-btn vc-btn--ghost vc-btn--sm" data-cm-all aria-pressed="false">Show the whole picture</button>
<span class="cm-hint">Scroll the steps, or click a box to jump to it.</span></div>
</div>
</div>
<script type="application/json" data-cm-data>{payload}</script>
</div>
<link rel="stylesheet" href="{rel}assets/concept-map.css">
<script type="module" src="{rel}assets/concept-map.js"></script>
"""
