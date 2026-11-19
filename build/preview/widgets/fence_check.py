"""Can the agent write here? A read-only folder simulator.

content/widgets/fence-check.yaml holds the folders and list entries. load() works out the verdict
for every combination of choices, following the rules of agent.sandbox_readonly_paths and
agent.sandbox_readonly_exceptions in v0.13.0. The JS only looks the answer up.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path

from . import WidgetError, check_text, read_yaml

NAME = "fence-check"
LABELS = ("folder", "paths", "exceptions", "sandbox")
VERDICTS = ("off", "free", "blocked", "excepted", "skipped_root", "skipped_exception")


def _err(msg: str) -> WidgetError:
    return WidgetError(f"{NAME}.yaml: {msg}")


def _inside(path: str, folder: str) -> bool:
    """True when path is folder itself or below it."""
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def _strictly_inside(path: str, folder: str) -> bool:
    return path != folder and _inside(path, folder)


def decide(target: str, paths: list[str], exceptions: list[str], sandbox: bool, v: dict) -> dict:
    """The verdict for one combination: {text, tone, note}."""
    notes = []
    entries = []
    for p in paths:
        if p == "/" or not p.startswith("/"):
            notes.append(v["skipped_root"].format(entry=p))
        else:
            entries.append(p)
    kept = []
    for e in exceptions:
        if any(_strictly_inside(e, p) for p in entries):
            kept.append(e)
        else:
            notes.append(v["skipped_exception"].format(exception=e))
    note = " ".join(notes)
    if not sandbox:
        return {"text": v["off"], "tone": "info", "note": note}
    covering = [p for p in entries if _inside(target, p)]
    if not covering:
        return {"text": v["free"], "tone": "ok", "note": note}
    entry = max(covering, key=len)
    for e in kept:
        if _inside(target, e) and _strictly_inside(e, entry):
            return {"text": v["excepted"].format(exception=e, entry=entry), "tone": "ok", "note": note}
    return {"text": v["blocked"].format(entry=entry), "tone": "stop", "note": note}


def _mask(items: list[str], chosen) -> int:
    return sum(1 << i for i, x in enumerate(items) if x in set(chosen))


def load(project: Path) -> dict:
    spec = read_yaml(project, NAME)
    for key in ("title", "labels", "targets", "paths", "exceptions", "start", "verdicts"):
        if key not in spec:
            raise _err(f"missing '{key}'")
    labels, v = spec["labels"], spec["verdicts"]
    if set(labels) != set(LABELS):
        raise _err(f"labels must be exactly {list(LABELS)}")
    if set(v) != set(VERDICTS):
        raise _err(f"verdicts must be exactly {list(VERDICTS)}")
    targets, paths, excs = spec["targets"], spec["paths"], spec["exceptions"]
    for group, items in (("targets", targets), ("paths", paths), ("exceptions", excs)):
        if not items or len(set(items)) != len(items):
            raise _err(f"'{group}' must be a non-empty list without repeats")
        if len(items) > 6:
            raise _err(f"'{group}' has more than 6 entries; keep the card calm")
        for x in items:
            if not isinstance(x, str) or not x.startswith("/"):
                raise _err(f"'{group}' entry {x!r} must be an absolute path")
    start = spec["start"]
    if start.get("target") not in targets:
        raise _err("start.target must be one of the targets")
    for group, items in (("paths", paths), ("exceptions", excs)):
        for x in start.get(group) or []:
            if x not in items:
                raise _err(f"start.{group} names unknown entry {x!r}")

    cases = {}
    for t, pm, em, sb in product(range(len(targets)), range(1 << len(paths)), range(1 << len(excs)), (0, 1)):
        chosen_p = [p for i, p in enumerate(paths) if pm >> i & 1]
        chosen_e = [e for i, e in enumerate(excs) if em >> i & 1]
        cases[f"{t}:{pm}:{em}:{sb}"] = decide(targets[t], chosen_p, chosen_e, bool(sb), v)

    data = {
        "title": spec["title"],
        "labels": labels,
        "targets": targets,
        "paths": paths,
        "exceptions": excs,
        "start": {
            "target": targets.index(start["target"]),
            "paths": _mask(paths, start.get("paths") or []),
            "exceptions": _mask(excs, start.get("exceptions") or []),
            "sandbox": bool(start.get("sandbox", True)),
        },
        "cases": cases,
    }
    check_text(NAME, {k: data[k] for k in ("title", "labels")})
    check_text(NAME, v)
    return data


def markdown(data: dict) -> str:
    paths = data["paths"]
    real = [i for i, p in enumerate(paths) if p != "/"]
    pm = sum(1 << i for i in real)
    em = (1 << len(data["exceptions"])) - 1
    rows = [f"**{data['title']}**", "",
            f"With {', '.join(paths[i] for i in real)} read-only and the exceptions "
            f"{', '.join(data['exceptions'])}:", "",
            "| Agent writes to | Result |", "| --- | --- |"]
    for t, target in enumerate(data["targets"]):
        rows.append(f"| `{target}` | {data['cases'][f'{t}:{pm}:{em}:1']['text']} |")
    return "\n".join(rows)
