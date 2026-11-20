"""The software factory map: every factory idea and the Kiro Crew parts that play it.

content/widgets/factory-map.yaml holds the zones and stations. load() checks each station and
that its anchor is a real heading on the host page, so a renamed section breaks the build
instead of leaving a dead link. The JS draws the tiles and the detail card.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "factory-map"
HOST_PAGE = Path("content") / "concepts" / "software-factory.md"


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def _anchors(project: Path) -> set[str]:
    """Heading ids on the host page, made the way build.slugify makes them."""
    try:
        text = (Path(project) / HOST_PAGE).read_text(encoding="utf-8")
    except OSError:
        return set()
    out = set()
    for line in re.findall(r"^#{2,4} (.+)$", text, flags=re.M):
        out.add(re.sub(r"[\s_]+", "-", re.sub(r"[^\w\s-]", "", line.lower()).strip()))
    return out


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "zones", "stations", "start"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    zones = spec["zones"]
    zone_ids = [z["id"] for z in zones]
    if len(set(zone_ids)) != len(zone_ids):
        raise _err("zone ids must be unique")
    stations = spec["stations"]
    ids = [s["id"] for s in stations]
    if len(set(ids)) != len(ids) or not 3 <= len(ids) <= 12:
        raise _err("need 3 to 12 stations with unique ids")
    if spec["start"] not in ids:
        raise _err("'start' must name a station")
    anchors = _anchors(project)
    for s in stations:
        where = f"station '{s['id']}'"
        if s.get("zone") not in zone_ids:
            raise _err(f"{where} has unknown zone '{s.get('zone')}'")
        if not s.get("name") or not s.get("says"):
            raise _err(f"{where} needs a name and a says line")
        feats = s.get("features") or []
        if not 1 <= len(feats) <= 4:
            raise _err(f"{where} needs 1 to 4 features")
        if anchors and s.get("anchor") not in anchors:
            raise _err(f"{where}: anchor '{s.get('anchor')}' is not a heading on {HOST_PAGE.as_posix()}")
    data = {
        "title": spec["title"],
        "zones": [{"id": z["id"], "label": z["label"],
                   "stations": [i for i, s in enumerate(stations) if s["zone"] == z["id"]]} for z in zones],
        "stations": [{"name": s["name"], "features": list(s["features"]), "says": s["says"],
                      "anchor": s["anchor"]} for s in stations],
        "start": ids.index(spec["start"]),
    }
    check_text(NAME, data)
    return data


def markdown(data: dict) -> str:
    rows = [f"**{data['title']}**", "", "| Factory part | Kiro Crew parts |", "| --- | --- |"]
    for s in data["stations"]:
        rows.append(f"| {s['name']} | {', '.join(s['features'])} |")
    return "\n".join(rows)
