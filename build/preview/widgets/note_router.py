"""Where does this note go? A notification routing simulator.

content/widgets/note-router.yaml holds the note kinds, priorities, the priority menu and the chat
apps. load() works out where each combination lands, following the 0.13.0 rules for the quick reply
card, Deliver to routes and the "Send pending approvals to chat apps" preview. The JS only looks up.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "note-router"
LABELS = ("kind", "priority", "route", "apps", "preview")
VERDICTS = ("card_only", "card_and_dm", "dm", "filtered", "no_apps")
# Wording confirmed in the v0.13.0 Notifications settings.
CONFIRMED_ROUTES = {"Critical only", "Default and critical", "Every priority"}
CONFIRMED_PREVIEW = "Send pending approvals to chat apps"


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def decide(kind: dict, priority: str, route: dict, apps: list[dict], preview: bool, v: dict) -> dict:
    """Where one note lands: {text, tone, card, dm: [app ids], answers: {app id: how}}."""
    card = bool(kind["asks"])
    if not apps:
        reason = v["no_apps"]
    elif kind["asks"] and not preview:
        reason = v["card_only"]
    elif priority not in route["passes"]:
        reason = v["filtered"].format(priority=priority)
    else:
        reason = None
    if reason:
        return {"text": reason, "tone": "info" if card else "stop", "card": card, "dm": [], "answers": {}}
    names = _join([a["label"] for a in apps])
    text = v["card_and_dm" if card else "dm"].format(apps=names)
    answers = {a["id"]: a["answer"] for a in apps} if kind["asks"] else {}
    return {"text": text, "tone": "ok", "card": card, "dm": [a["id"] for a in apps], "answers": answers}


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "labels", "kinds", "priorities", "routes", "apps", "start", "places", "verdicts"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    labels, v = spec["labels"], spec["verdicts"]
    if set(labels) != set(LABELS):
        raise _err(f"labels must be exactly {list(LABELS)}")
    if labels["preview"] != CONFIRMED_PREVIEW:
        raise _err(f"labels.preview must read '{CONFIRMED_PREVIEW}' (the v0.13.0 switch)")
    if set(v) != set(VERDICTS):
        raise _err(f"verdicts must be exactly {list(VERDICTS)}")
    prio_ids = [p["id"] for p in spec["priorities"]]
    kinds, routes, apps = spec["kinds"], spec["routes"], spec["apps"]
    for group, items in (("kinds", kinds), ("priorities", spec["priorities"]), ("routes", routes), ("apps", apps)):
        ids = [x["id"] for x in items]
        if not ids or len(set(ids)) != len(ids):
            raise _err(f"'{group}' ids must be unique and not empty")
    if len(apps) > 4:
        raise _err("show at most four apps")
    for k in kinds:
        if k["priority"] not in prio_ids:
            raise _err(f"kind '{k['id']}' has unknown priority '{k['priority']}'")
    for r in routes:
        if r["label"] not in CONFIRMED_ROUTES:
            raise _err(f"route label '{r['label']}' is not in the v0.13.0 priority menu")
        for p in r["passes"]:
            if p not in prio_ids:
                raise _err(f"route '{r['id']}' passes unknown priority '{p}'")
    start = spec["start"]
    if start.get("kind") not in [k["id"] for k in kinds]:
        raise _err("start.kind must be one of the kinds")
    if start.get("route") not in [r["id"] for r in routes]:
        raise _err("start.route must be one of the routes")
    for a in start.get("apps") or []:
        if a not in [x["id"] for x in apps]:
            raise _err(f"start.apps names unknown app '{a}'")

    cases = {}
    for k, p, r, am, pv in product(range(len(kinds)), range(len(prio_ids)), range(len(routes)),
                                   range(1 << len(apps)), (0, 1)):
        chosen = [a for i, a in enumerate(apps) if am >> i & 1]
        cases[f"{k}:{p}:{r}:{am}:{pv}"] = decide(kinds[k], prio_ids[p], routes[r], chosen, bool(pv), v)

    kind_index = [k["id"] for k in kinds].index(start["kind"])
    data = {
        "title": spec["title"],
        "labels": labels,
        "places": spec["places"],
        "kinds": [{"label": k["label"], "priority": prio_ids.index(k["priority"])} for k in kinds],
        "priorities": [p["label"] for p in spec["priorities"]],
        "routes": [r["label"] for r in routes],
        "apps": [{"id": a["id"], "label": a["label"]} for a in apps],
        "start": {
            "kind": kind_index,
            "priority": prio_ids.index(kinds[kind_index]["priority"]),
            "route": [r["id"] for r in routes].index(start["route"]),
            "apps": sum(1 << i for i, a in enumerate(apps) if a["id"] in (start.get("apps") or [])),
            "preview": bool(start.get("preview")),
        },
        "cases": cases,
    }
    check_text(NAME, {k: data[k] for k in ("title", "labels", "places", "kinds", "priorities", "routes", "apps")})
    check_text(NAME, v)
    return data


def markdown(data: dict) -> str:
    allapps = (1 << len(data["apps"])) - 1
    rows = [f"**{data['title']}**", "",
            f"Every app ticked, priority menu at {data['routes'][0]}, each note at its usual priority:", "",
            f"| The note | Preview off | Preview on |", "| --- | --- | --- |"]
    for k, kind in enumerate(data["kinds"]):
        off = data["cases"][f"{k}:{kind['priority']}:0:{allapps}:0"]["text"]
        on = data["cases"][f"{k}:{kind['priority']}:0:{allapps}:1"]["text"]
        rows.append(f"| {kind['label']} | {off} | {on} |")
    return "\n".join(rows)
