"""Data for the "Dashboard map" page: map.yaml + the pinned UI index and UI text.

Every zone names a part of the drawn dashboard. This module checks each one
exists (in KiroCrew's UI index, or as one of the drawing's own x.* parts),
fills the Customize and Settings tabs with the descriptions the dashboard
itself shows, and works out which screen each zone lives on.

The drawing takes no clicks: the reader picks a part from the list beside it,
and the drawing highlights that part.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

import where_is

esc = html.escape

# Parts of the drawing the UI index does not list (kc-drawing.js draws them with these ids).
DRAWN = {"x.history-nav", "x.status", "x.feedback", "x.apps-group", "x.session-row", "x.transcript",
         "x.message-box", "x.optimize", "x.agent-selector", "x.project-pill", "x.side-panel"}
# Description keys for Customize tabs, by UI-index id (website/src/pages/CapabilitiesPage.tsx).
CUSTOMIZE_TEXT = {
    "tab.capabilities.crews": "crews", "tab.capabilities.templates": "templates", "tab.capabilities.skills": "skills",
    "tab.capabilities.mcp": "connections", "tab.capabilities.knowledge": "knowledge", "tab.capabilities.prompts": "prompts",
    "tab.capabilities.steering": "steering", "tab.capabilities.hooks": "hooks", "tab.capabilities.workflows": "workflows",
}
# Placeholders the dashboard fills at runtime, filled the way a default install does.
FILL = {"{{registry}}": "packages", "{{productName}}": "KiroCrew"}


class MapError(Exception):
    pass


def _fill(text: str | None) -> str | None:
    if text:
        for k, v in FILL.items():
            text = text.replace(k, v)
    return text


def _screen(idx: where_is.Index, at: str) -> str | None:
    """The page a zone lives on. None means the top bar or the rail: visible on every page."""
    if at.startswith(("page.", "shell.")) or at in ("x.history-nav", "x.status", "x.feedback", "x.apps-group"):
        return None
    if at.startswith("x."):
        return "page.chat"
    parents = idx.placement(at)["parent_ids"]
    return parents[0] if parents and parents[0].startswith("page.") else "page.chat"


def load(project: Path, docs_by_slug: dict[str, dict], finder: dict | None) -> dict:
    idx = where_is.load_index(project)
    text = json.loads((project / "build" / "data" / "ui-text.json").read_text(encoding="utf-8"))
    strings = text["strings"]
    spec = yaml.safe_load((project / "content" / "find" / "map.yaml").read_text(encoding="utf-8"))
    task_ids = {t["id"] for t in (finder or {}).get("tasks", [])}
    groups, seen = [], set()

    for g in spec["groups"]:
        zones = []
        if g.get("auto") == "customize":
            for _, ids in where_is.CUSTOMIZE:
                for at in ids:
                    key = CUSTOMIZE_TEXT[at]
                    zones.append({"at": at, "name": idx.label(at),
                                  "text": _fill(strings.get(f"pages.capabilitiesPage.{key}_description")),
                                  "state": {"sidetab": at}})
        elif g.get("auto") == "settings":
            for _, keys in where_is.SETTINGS:
                for key in keys:
                    at = f"settings.tab.{key}"
                    if at not in idx.locs or at in where_is.PREVIEW_TABS:
                        continue
                    camel = key.split("-")[0] + "".join(p.capitalize() for p in key.split("-")[1:])
                    desc = _fill(strings.get(f"settings.tabs.{camel}.description")
                                 or (strings.get("privacyDisclosure.settingsDescription") if key == "privacy" else None))
                    zones.append({"at": at, "name": idx.label(at), "text": desc, "state": {"sidetab": at}})
        else:
            for z in g["zones"]:
                at = z["at"]
                if at not in idx.locs and at not in DRAWN:
                    raise MapError(f"map.yaml: '{at}' is neither in the pinned UI index nor a drawn x.* part")
                if z.get("task") and z["task"] not in task_ids:
                    raise MapError(f"map.yaml: zone '{at}' links to unknown Where-is task '{z['task']}'")
                see_slug, _, see_hash = (z.get("see") or "").partition("#")
                if see_slug and see_slug not in docs_by_slug:
                    raise MapError(f"map.yaml: zone '{at}' links to unknown cookbook page '{see_slug}'")
                zones.append({"at": at, "name": z["name"], "text": z["text"], "task": z.get("task"),
                              "state": z.get("state") or {},
                              "see": {"slug": see_slug, "hash": see_hash,
                                      "title": docs_by_slug[see_slug]["meta"]["title"]} if see_slug else None})
        for z in zones:
            if z["at"] in seen:
                raise MapError(f"map.yaml: '{z['at']}' is listed twice")
            seen.add(z["at"])
            z["screen"] = _screen(idx, z["at"])
            z["path"] = idx.path(z["at"]) if z["at"] in idx.locs else None
        groups.append({"group": g["group"], "zones": zones})

    for at in spec.get("tour") or []:
        if at not in seen:
            raise MapError(f"map.yaml: tour stop '{at}' is not a zone")
    labels = {z["at"]: z["name"] for g in groups for z in g["zones"]}
    used = {at for at in seen if at in idx.locs}
    return {"version": idx.version, "text_commit": text["source_commit"], "groups": groups,
            "tour": spec.get("tour") or [], "drawing": where_is.drawing_data(idx, used, labels)}


def fallback_table(data: dict) -> str:
    rows = []
    for g in data["groups"]:
        rows.append(f'<tr class="wi-table__group"><th colspan="2" scope="rowgroup">{esc(g["group"])}</th></tr>')
        for z in g["zones"]:
            rows.append(f'<tr><th scope="row"><a href="#zone={esc(z["at"])}">{esc(z["name"])}</a></th>'
                        f'<td>{esc(z["text"] or "")}</td></tr>')
    return ('<div class="vc-table-wrap"><table class="wi-table"><thead><tr><th scope="col">Part</th>'
            '<th scope="col">What it is for</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


def markdown_table(data: dict) -> str:
    out = []
    for g in data["groups"]:
        out += ["", f"### {g['group']}", "", "| Part | What it is for |", "|---|---|"]
        out += [f"| {z['name']} | {z['text'] or ''} |" for z in g["zones"]]
    return "\n".join(out).strip() + "\n"


def widget_html(data: dict, rel: str) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<div class="wi dm is-empty" data-dash-map>
<noscript><p class="wi-noscript">The interactive map needs JavaScript. Every part is described in the table below.</p></noscript>
<div class="wi-finder">
<p class="vc-label">Parts of the dashboard</p>
<div class="dm-tour"><button type="button" class="vc-btn vc-btn--primary vc-btn--sm" id="dm-tour">Take the 1-minute tour</button></div>
<div class="wi-list" id="dm-list"></div>
</div>
<div class="wi-stage">
<div class="wi-answer" id="dm-info"></div>
<div class="dm-tourbox"></div>
<div class="dm-screens" id="dm-screens"></div>
<div class="wi-frame" aria-hidden="true"><div class="wi-canvas" id="dm-canvas"></div></div>
<p class="wi-caption">A simplified drawing of the KiroCrew {esc(data["version"])} dashboard. It only shows where things are; nothing in it is clickable. Labels come from KiroCrew's own UI index; order and spacing on your screen can differ.</p>
</div>
<script type="application/json" id="dm-data">{payload}</script>
</div>
<link rel="stylesheet" href="{rel}assets/where-is.css">
<script type="module" src="{rel}assets/dashboard-map.js"></script>
"""
