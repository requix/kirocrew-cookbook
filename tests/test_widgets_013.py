"""Tests for the fence-check, note-router and trace-waterfall widgets."""
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build" / "preview"))

import widgets  # noqa: E402
from widgets import fence_check, note_router, trace_waterfall  # noqa: E402


def copy(tmp_path, name):
    (tmp_path / "content" / "widgets").mkdir(parents=True)
    shutil.copy(ROOT / "content" / "widgets" / f"{name}.yaml", tmp_path / "content" / "widgets")
    return tmp_path


def edit(project, name, old, new):
    p = project / "content" / "widgets" / f"{name}.yaml"
    text = p.read_text()
    assert old in text
    p.write_text(text.replace(old, new, 1))


# fence-check

V = fence_check.load(ROOT)


def case(target, paths, excs, sandbox=True):
    t = V["targets"].index(target)
    pm = sum(1 << V["paths"].index(p) for p in paths)
    em = sum(1 << V["exceptions"].index(e) for e in excs)
    return V["cases"][f"{t}:{pm}:{em}:{int(sandbox)}"]


def test_fence_blocked_and_free():
    assert case("/srv/archive/report.pdf", ["/srv/archive"], [])["tone"] == "stop"
    assert case("/home/me/project/app.py", ["/srv/archive"], [])["tone"] == "ok"


def test_fence_exception_reopens_only_inside():
    c = case("/srv/archive/scratch/notes.txt", ["/srv/archive"], ["/srv/archive/scratch"])
    assert c["tone"] == "ok" and "exception" in c["text"]
    assert case("/srv/archive/report.pdf", ["/srv/archive"], ["/srv/archive/scratch"])["tone"] == "stop"


def test_fence_exception_needs_its_entry():
    c = case("/srv/archive/scratch/notes.txt", [], ["/srv/archive/scratch"])
    assert c["tone"] == "ok" and "skipped" in c["note"]


def test_fence_root_is_skipped():
    c = case("/home/me/project/app.py", ["/"], [])
    assert c["tone"] == "ok" and "skipped" in c["note"]


def test_fence_sandbox_off_enforces_nothing():
    assert "not enforced" in case("/srv/archive/report.pdf", ["/srv/archive"], [], sandbox=False)["text"]


def test_fence_every_combination_present():
    assert len(V["cases"]) == len(V["targets"]) * 2 ** len(V["paths"]) * 2 ** len(V["exceptions"]) * 2


def test_fence_rejects_relative_target(tmp_path):
    p = copy(tmp_path, "fence-check")
    edit(p, "fence-check", "  - /mnt/c/Users/me/todo.txt", "  - mnt/c/todo.txt")
    with pytest.raises(widgets.WidgetError, match="absolute"):
        fence_check.load(p)


# note-router

N = note_router.load(ROOT)


def route(kind, prio, menu, apps, preview):
    k = [x["label"] for x in N["kinds"]].index(kind)
    am = sum(1 << [a["label"] for a in N["apps"]].index(a) for a in apps)
    return N["cases"][f"{k}:{N['priorities'].index(prio)}:{N['routes'].index(menu)}:{am}:{int(preview)}"]


def test_router_approval_needs_preview_for_dm():
    off = route("Tool approval", "Critical", "Critical only", ["Slack"], False)
    on = route("Tool approval", "Critical", "Critical only", ["Slack"], True)
    assert off["card"] and off["dm"] == []
    assert on["dm"] == ["slack"] and "Approve" in on["answers"]["slack"]


def test_router_priority_menu_filters():
    assert route("Chat error", "Default", "Critical only", ["Telegram"], False)["dm"] == []
    assert route("Chat error", "Default", "Default and critical", ["Telegram"], False)["dm"] == ["telegram"]
    assert route("Chat error", "Passive", "Every priority", ["Telegram"], False)["dm"] == ["telegram"]


def test_router_no_apps():
    c = route("Chat error", "Critical", "Every priority", [], True)
    assert c["dm"] == [] and not c["card"]


def test_router_rejects_unconfirmed_menu_label(tmp_path):
    p = copy(tmp_path, "note-router")
    edit(p, "note-router", "label: Every priority", "label: Everything")
    with pytest.raises(widgets.WidgetError, match="priority menu"):
        note_router.load(p)


# trace-waterfall

def test_trace_loads_and_draws():
    d = trace_waterfall.load(ROOT)
    assert d["spans"][0]["width"] == 100
    assert any(s["slow"] for s in d["spans"])
    assert "Never recorded" in trace_waterfall.markdown(d)


def test_trace_rejects_attribute_off_allowlist(tmp_path):
    p = copy(tmp_path, "trace-waterfall")
    edit(p, "trace-waterfall", "kirocrew.approval.outcome: approved", "kirocrew.approval.command: rm")
    with pytest.raises(widgets.WidgetError, match="allowlist"):
        trace_waterfall.load(p)


def test_trace_rejects_unknown_span_name(tmp_path):
    p = copy(tmp_path, "trace-waterfall")
    edit(p, "trace-waterfall", "name: kirocrew.compaction", "name: kirocrew.nap")
    with pytest.raises(widgets.WidgetError, match="span name"):
        trace_waterfall.load(p)


def test_markdown_for_all():
    for mod in (fence_check, note_router, trace_waterfall):
        assert mod.markdown(mod.load(ROOT)).strip()
