"""Data for the "Where is…?" page: tasks.yaml + KiroCrew's pinned UI index.

Every task names a control by its UI-index id. This module turns that into the
click path (page → tab → section → control), the "needs first" notes, and the
lists the drawn dashboard needs. An id the index no longer has is an error, so
the build stops instead of shipping a wrong answer.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

esc = html.escape

# Rail order and groups, as the dashboard draws them (website/src/surfaces/surfaceData.ts).
RAIL = {
    "main": ["page.chat", "page.members", "page.schedule", "page.artifacts"],
    "apps": ["page.apps", "page.apps-library", "page.projects"],
    "bottom": ["shell.terminal", "page.capabilities", "page.settings"],
}
# Customize tabs and their groups (website/src/pages/CapabilitiesPage.tsx).
CUSTOMIZE = [
    ("Agent", ["tab.capabilities.crews", "tab.capabilities.templates", "tab.capabilities.skills", "tab.capabilities.mcp"]),
    ("Knowledge & instructions", ["tab.capabilities.knowledge", "tab.capabilities.prompts", "tab.capabilities.steering"]),
    ("Automation", ["tab.capabilities.hooks", "tab.capabilities.workflows"]),
]
# Settings tabs and their groups (website/src/pages/SettingsPage.tsx); tabs the pinned index lacks are skipped.
SETTINGS = [
    ("", ["overview", "imports"]),
    ("Preferences", ["agent", "chat", "display", "voice", "notifications", "shortcuts", "skills"]),
    ("", ["channels"]),
    ("System", ["browser", "computer-use", "webhooks", "instances", "privacy", "security", "connections", "secrets", "developer"]),
    ("", ["releases", "about"]),
]
# Sub-section order inside Settings tabs (website/src/pages/settings/*Panel.tsx); the index lists them A-Z.
SUB_ORDER = {
    "chat": ["transcript", "composer", "sessions", "sidepanel", "models", "aboutyou", "discovery", "advanced"],
    "display": ["view", "zoom", "terminal", "theme", "sidebar"],
    "notifications": ["sources", "alerts", "sound", "percategory", "custom"],
    "security": ["posture", "approval", "rules", "tailnet", "apps", "registries", "redaction", "layers", "governance", "docs"],
    "channels": ["slack", "discord", "telegram", "webex", "wecom", "feishu", "teams", "weixin", "imessage", "whatsapp"],
}
# Settings tabs that exist only behind a preview switch: drawn only for a task that needs them.
PREVIEW_TABS = {"settings.tab.webhooks"}
SHORT = {
    "chat.session-title": "Chat title",
    "chat.model-picker": "Model, under the message box",
    "chat.memory-mode": "Memory mode, above the message box",
    "composer.approval-mode": "Approval mode (Normal)",
    "composer.voice": "Microphone",
    "members.roster-list": "Pick a mate in the list",
    "shell.search": "Search bar (Cmd+K / Ctrl+K)",
}
# Conditions the drawing can show as a click of their own: (drawn element, step label).
CONDITION_STEPS = {"job_open": ("x.job-row", "Pick the job in the list")}
# Things that must be opened first and that the drawing can show as a click.
CLICKABLE_REVEALS = {"chat.side-panel-open"}
# Conditions every reader of this page meets, or that only add noise.
QUIET_CONDITIONS = {"mouse_input", "full_dashboard", "session_open", "has_open_sessions", "pointer_on_session_row",
                    "search_bar_unclaimed"}
# The drawn chat screen has these; anything else in the chat surface is drawn generically.
CHAT_DRAWN = {
    "chat.new-session", "sessions.create-menu", "sessions.list-menu", "sessions.list", "sessions.row-menu",
    "sessions.row-duplicate", "sessions.row-close", "chat.older-sessions", "chat.session-title",
    "chat.side-panel-open", "chat.side-panel.add", "composer.add-menu", "chat.model-picker",
    "composer.approval-mode", "composer.automation", "composer.context-usage", "composer.voice",
    "composer.send", "composer.attach-files", "chat.memory-mode",
}
MENUS = {"composer.add-menu", "sessions.create-menu", "sessions.list-menu", "sessions.row-menu", "chat.side-panel.add",
         "composer.automation", "members.add-menu", "members.switcher", "apps.sources"}


class WhereIsError(Exception):
    pass


# Why a task is on the page at all: the reasons a control is hard to find (see tasks.yaml).
WHY = {
    "menu": "Behind a menu",
    "state": "Shows only sometimes",
    "preview": "Needs a switch first",
    "name": "Has another name",
    "deep": "Deep in Settings or Customize",
}


class Index:
    def __init__(self, path: Path):
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.version = raw["kirocrew_version"]
        self.labels = raw["labels"]
        self.conditions = raw["conditions"]
        self.locs = {loc["id"]: loc for loc in raw["locations"]}
        self.children: dict[str, list[str]] = {}
        for loc in raw["locations"]:
            p = self.placement(loc["id"])
            parent = p["parent_ids"][-1] if p["parent_ids"] else None
            if parent:
                self.children.setdefault(parent, []).append(loc["id"])

    def placement(self, loc_id: str) -> dict:
        """The desktop placement: the one without a mobile-only viewport rule."""
        ps = self.locs[loc_id]["placements"]
        for p in ps:
            if not any(r["kind"] == "viewport" and r.get("value") == "mobile" for r in p["requires"]):
                return p
        return ps[0]

    def label(self, loc_id: str) -> str:
        if loc_id in SHORT:
            return SHORT[loc_id]
        loc = self.locs[loc_id]
        text = self.labels.get(loc.get("label_key", ""), "")
        if not text:
            raise WhereIsError(f"{loc_id}: no English label in the pinned index")
        return text

    def description(self, loc_id: str) -> str | None:
        loc = self.locs[loc_id]
        return self.labels.get(loc["label_key"]) if loc.get("label_kind") == "description" else None

    def path(self, loc_id: str) -> str:
        return " → ".join(self.label(i) for i in [*self.placement(loc_id)["parent_ids"], loc_id])


def area_of(loc_id: str, idx: Index) -> str:
    """Which part of the drawn dashboard a control sits in."""
    loc = idx.locs.get(loc_id, {})
    if loc_id.startswith("page."):
        return "rail"
    if loc_id in ("shell.search", "shell.focus-mode", "shell.notifications"):
        return "header"
    if loc_id == "shell.terminal":
        return "rail"
    if loc_id.startswith(("tab.capabilities.", "settings.tab.")):
        return "sidetab"
    if loc_id.startswith("settings.sub."):
        return "subnav"
    if loc.get("kind") == "setting":
        return "row"
    if loc_id in MENUS:
        return "menubutton"
    parent = (idx.placement(loc_id)["parent_ids"] or [None])[-1] if loc else None
    if parent in MENUS:
        return "menuitem"
    if loc_id in CHAT_DRAWN:
        return "chat"
    if loc.get("kind") == "tab":
        return "contenttab"
    if loc.get("kind") == "list":
        return "list"
    return "content"


def resolve_at(task: dict, idx: Index, by_target: dict[str, str]) -> dict:
    target = task["at"]
    if target not in idx.locs:
        raise WhereIsError(f"task '{task['id']}': '{target}' is not in the pinned UI index (KiroCrew {idx.version})")
    p = idx.placement(target)
    chain = [*p["parent_ids"], target]
    needs: list[dict] = []
    extra: list[tuple[str, str]] = []
    for r in p["requires"]:
        if r["kind"] == "preview_flag":
            flag = r["location"]
            needs.append({"text": f"Turn on the preview first: {idx.path(flag)}", "task": by_target.get(flag)})
        elif r["kind"] == "shown_by":
            if r["location"] in CLICKABLE_REVEALS:
                chain.insert(chain.index(target) if target in chain else len(chain) - 1, r["location"])
            elif r["location"] not in ("chat.sessions-sidebar-toggle", "composer.expand"):
                needs.append({"text": f"If you cannot see it, open {idx.label(r['location'])} first"})
        elif r["kind"] == "condition" and r["id"] in CONDITION_STEPS:
            extra.append(CONDITION_STEPS[r["id"]])
        elif r["kind"] == "condition" and r["id"] not in QUIET_CONDITIONS:
            text = idx.conditions.get(r["id"])
            if text:
                needs.append({"text": f"Shows only when {text}"})
        elif r["kind"] == "viewport" and r.get("value") == "mobile":
            needs.append({"text": "Phone screens only"})
    # Keep reveal steps in click order: page first, then the reveal, then the rest.
    if any(c in CLICKABLE_REVEALS for c in chain):
        rev = [c for c in chain if c in CLICKABLE_REVEALS]
        rest = [c for c in chain if c not in CLICKABLE_REVEALS]
        chain = rest[:1] + rev + rest[1:]
    steps = [{"loc": c, "label": idx.label(c), "area": area_of(c, idx)} for c in chain]
    for loc, text in extra:
        steps.insert(len(steps) - 1, {"loc": loc, "label": text, "area": "content"})
    terms = list(task.get("terms") or []) + list(idx.locs[target].get("terms") or [])
    return {"surface": p["surface_id"], "steps": steps, "needs": needs, "terms": terms,
            "detail": idx.description(target), "source": f"KiroCrew {idx.version} UI index: {target}"}


def resolve_manual(task: dict, idx: Index) -> dict:
    m = task["manual"]
    for s in m["steps"]:
        if s["draw"].startswith(("page.", "shell.")) and s["draw"] not in idx.locs:
            raise WhereIsError(f"task '{task['id']}': '{s['draw']}' is not in the pinned UI index")
    steps = [{"loc": s["draw"], "label": s["label"], "area": "rail" if s["draw"].startswith("page.") else "chat"}
             for s in m["steps"]]
    return {"surface": m["screen"], "steps": steps, "needs": [], "terms": list(task.get("terms") or []),
            "detail": None, "source": m["source"]}


def load(project: Path, docs_by_slug: dict[str, dict]) -> dict:
    idx = load_index(project)
    groups = yaml.safe_load((project / "content" / "find" / "tasks.yaml").read_text(encoding="utf-8"))
    flat = [(g["group"], t) for g in groups for t in g["tasks"]]
    ids = [t["id"] for _, t in flat]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise WhereIsError(f"tasks.yaml: duplicate ids {sorted(dupes)}")
    by_target = {t["at"]: t["id"] for _, t in flat if "at" in t}
    tasks = []
    for group, t in flat:
        if ("at" in t) == ("manual" in t):
            raise WhereIsError(f"task '{t['id']}': give exactly one of 'at' or 'manual'")
        if t.get("why") not in WHY:
            raise WhereIsError(f"task '{t['id']}': why must be one of {sorted(WHY)} (see the top of tasks.yaml)")
        r = resolve_at(t, idx, by_target) if "at" in t else resolve_manual(t, idx)
        see = None
        if t.get("see"):
            if t["see"] not in docs_by_slug:
                raise WhereIsError(f"task '{t['id']}': see '{t['see']}' is not a cookbook page")
            see = {"slug": t["see"], "title": docs_by_slug[t["see"]]["meta"]["title"]}
        tasks.append({"id": t["id"], "group": group, "task": t["task"], "why": WHY[t["why"]], "note": t.get("note"),
                      "see": see, **r})

    used = {s["loc"] for t in tasks for s in t["steps"]}
    labels = {s["loc"]: s["label"] for t in tasks for s in t["steps"]}
    return {"version": idx.version, "tasks": tasks, "drawing": drawing_data(idx, used, labels)}


def load_index(project: Path) -> Index:
    return Index(project / "build" / "data" / "ui-index.json")


def drawing_data(idx: Index, used: set[str], labels: dict[str, str] | None = None) -> dict:
    """What the drawn dashboard needs: rail, tab lists, and the siblings around every control in `used`."""
    containers = {(idx.placement(u)["parent_ids"] or [None])[-1] for u in used if u in idx.locs} | used
    children = {}
    for c in containers:
        if c in idx.children:
            kids = [k for k in idx.children[c] if not k.startswith(("settings.sub.", "settings.tab.", "tab."))
                    or c.startswith("settings.tab.") or c.startswith("page.")]
            children[c] = [{"loc": k, "label": idx.label(k), "kind": idx.locs[k]["kind"]} for k in kids]
    lab = lambda i: {"loc": i, "label": idx.label(i)}

    def sub_rank(tab: str, sub: str) -> tuple[int, str]:
        key, name = tab.removeprefix("settings.tab."), sub.rsplit(".", 1)[-1]
        order = SUB_ORDER.get(key, [])
        return (order.index(name) if name in order else len(order), sub)

    every = {u: idx.label(u) for u in used if u in idx.locs}
    every.update(labels or {})
    for kids in children.values():
        every.update({k["loc"]: k["label"] for k in kids})
    return {
        "rail": {k: [lab(i) for i in v] for k, v in RAIL.items()},
        "customize": [{"group": g, "tabs": [lab(i) for i in ids_ if i in idx.locs]} for g, ids_ in CUSTOMIZE],
        "settings": [{"group": g, "tabs": [{**lab(f"settings.tab.{k}"), "preview": f"settings.tab.{k}" in PREVIEW_TABS}
                                           for k in keys if f"settings.tab.{k}" in idx.locs]}
                     for g, keys in SETTINGS],
        "subnav": {t: [lab(k) for k in sorted((k for k in idx.children.get(t, []) if k.startswith("settings.sub.")),
                                              key=lambda k, t=t: sub_rank(t, k))]
                   for t in idx.locs if t.startswith("settings.tab.")},
        "children": children,
        "pages": {i: idx.label(i) for i in idx.locs if i.startswith("page.")},
        "labels": every,
    }


def path_text(t: dict) -> str:
    return " → ".join(s["label"] for s in t["steps"])


def fallback_table(data: dict, rel: str) -> str:
    """The whole list as a plain table: works without JavaScript, prints, and feeds search."""
    rows, last = [], None
    for t in data["tasks"]:
        if t["group"] != last:
            rows.append(f'<tr class="wi-table__group"><th colspan="4" scope="rowgroup">{esc(t["group"])}</th></tr>')
            last = t["group"]
        needs = "<br>".join(esc(n["text"]) for n in t["needs"]) or "—"
        rows.append(f'<tr id="t-{esc(t["id"])}"><th scope="row"><a href="#task={esc(t["id"])}">{esc(t["task"])}</a></th>'
                    f"<td>{esc(path_text(t))}</td><td>{esc(t['why'])}</td><td>{needs}</td></tr>")
    return ('<div class="vc-table-wrap"><table class="wi-table"><thead><tr><th scope="col">You want to</th>'
            '<th scope="col">Click</th><th scope="col">Why it hides</th><th scope="col">Needs first</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def markdown_table(data: dict) -> str:
    out, last = [], None
    for t in data["tasks"]:
        if t["group"] != last:
            out += ["", f"### {t['group']}", "", "| You want to | Click | Why it hides | Needs first |", "|---|---|---|---|"]
            last = t["group"]
        needs = "; ".join(n["text"] for n in t["needs"]) or "-"
        out.append(f"| {t['task']} | {path_text(t)} | {t['why']} | {needs} |")
    return "\n".join(out).strip() + "\n"


def widget_html(data: dict, rel: str) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<div class="wi" data-where-is>
<noscript><p class="wi-noscript">The animated finder needs JavaScript. Every answer is in the table below.</p></noscript>
<div class="wi-finder">
<label class="vc-label" for="wi-q">What do you want to do?</label>
<div class="wi-search"><input id="wi-q" type="search" autocomplete="off" placeholder="Try: working directory, skills, YOLO" aria-describedby="wi-count"></div>
<p class="wi-count" id="wi-count" aria-live="polite"></p>
<div class="wi-list" id="wi-list"></div>
</div>
<div class="wi-stage">
<div class="wi-answer" id="wi-answer"><p class="wi-hint">Pick a task. A pointer shows every click on a drawn dashboard.</p></div>
<div class="wi-frame" aria-hidden="true"><div class="wi-canvas" id="wi-canvas"></div></div>
<p class="wi-caption">A simplified drawing of the KiroCrew {esc(data["version"])} dashboard. Labels come from KiroCrew's own UI index; order and spacing on your screen can differ.</p>
</div>
<script type="application/json" id="wi-data">{payload}</script>
</div>
<link rel="stylesheet" href="{rel}assets/where-is.css">
<script type="module" src="{rel}assets/where-is.js"></script>
"""
