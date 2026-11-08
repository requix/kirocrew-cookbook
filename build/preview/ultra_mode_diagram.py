"""Ultra Mode conductor/worker diagram.

ultra-mode-diagram.yaml holds the drawing (nodes, links, animation steps).
This widget shows how a request flows through the conductor to workers
and back, with animated steps the user can navigate.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

esc = html.escape


class UltraModeError(Exception):
    pass


def load(project: Path) -> dict:
    spec = yaml.safe_load((project / "content" / "concepts" / "ultra-mode-diagram.yaml").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in spec["nodes"]}
    w, h = spec["canvas"]

    # Build links
    links = []
    for a, b, text in spec["links"]:
        if a not in nodes or b not in nodes:
            raise UltraModeError(f"ultra-mode-diagram.yaml: link {a}>{b} names an unknown node")
        links.append({"id": f"{a}>{b}", "from": a, "to": b, "label": text})
    link_ids = {l["id"] for l in links}

    # Validate steps reference valid nodes/links
    all_ids = set(nodes) | link_ids
    for i, step in enumerate(spec["steps"], start=1):
        for item in step.get("show", []):
            if item not in all_ids:
                raise UltraModeError(f"ultra-mode-diagram.yaml: step {i} names unknown '{item}'")

    # Figure out which step first shows each node/link
    first_step: dict[str, int] = {}
    for i, step in enumerate(spec["steps"], start=1):
        for item in step.get("show", []):
            first_step.setdefault(item, i)

    # Validate all nodes/links are shown by some step
    missing = all_ids - set(first_step)
    if missing:
        raise UltraModeError(f"ultra-mode-diagram.yaml: never shown by any step: {sorted(missing)}")

    # Build output nodes with positions and step info
    out_nodes = []
    styles = spec.get("styles", {})
    for n in spec["nodes"]:
        x, y = n["at"]
        nw, nh = n.get("size", [140, 52])
        if x < 0 or y < 0 or x + nw > w or y + nh > h:
            raise UltraModeError(f"ultra-mode-diagram.yaml: node '{n['id']}' does not fit the {w}x{h} canvas")
        style = styles.get(n.get("style", ""), {})
        out_nodes.append({
            "id": n["id"],
            "name": n["name"],
            "sub": n.get("sub") or "",
            "x": x, "y": y, "w": nw, "h": nh,
            "step": first_step[n["id"]],
            "style": n.get("style", ""),
        })

    return {
        "w": w, "h": h,
        "nodes": out_nodes,
        "links": [{**l, "step": first_step[l["id"]]} for l in links],
        "steps": [{"show": s.get("show", []), "note": s.get("note", "")} for s in spec["steps"]],
        "styles": styles,
    }


def widget_html(data: dict, rel: str) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    step_notes = "".join(
        f'<li class="um-step" data-step="{i+1}">'
        f'<button type="button" class="um-step__btn">'
        f'<span class="um-step__num">{i+1}</span>'
        f'<span class="um-step__note">{esc(s["note"])}</span>'
        f'</button></li>'
        for i, s in enumerate(data["steps"])
    )
    return f"""<div class="um" data-ultra-mode>
<div class="um-frame"><div class="um-canvas" role="group" aria-label="Ultra Mode conductor and worker diagram"></div></div>
<div class="um-controls">
<ol class="um-steps" aria-label="Animation steps">{step_notes}</ol>
<div class="um-bar">
<button type="button" class="vc-btn vc-btn--ghost vc-btn--sm um-prev" aria-label="Previous step">← Prev</button>
<button type="button" class="vc-btn vc-btn--ghost vc-btn--sm um-next" aria-label="Next step">Next →</button>
<button type="button" class="vc-btn vc-btn--ghost vc-btn--sm um-play" data-playing="false">▶ Play</button>
</div>
</div>
<script type="application/json" data-um-data>{payload}</script>
</div>
<link rel="stylesheet" href="{rel}assets/ultra-mode-diagram.css">
<script type="module" src="{rel}assets/ultra-mode-diagram.js"></script>
"""
