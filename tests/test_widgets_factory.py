"""Tests for the factory-map and factory-run widgets on the software factory page."""
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build" / "preview"))

import widgets  # noqa: E402
from widgets import factory_map, factory_run  # noqa: E402


def copy(tmp_path, name, with_page=False):
    (tmp_path / "content" / "widgets").mkdir(parents=True)
    shutil.copy(ROOT / "content" / "widgets" / f"{name}.yaml", tmp_path / "content" / "widgets")
    if with_page:
        (tmp_path / "content" / "concepts").mkdir(parents=True)
        shutil.copy(ROOT / "content" / "concepts" / "software-factory.md", tmp_path / "content" / "concepts")
    return tmp_path


def edit(project, name, old, new):
    p = project / "content" / "widgets" / f"{name}.yaml"
    text = p.read_text()
    assert old in text
    p.write_text(text.replace(old, new, 1))


def test_map_loads_every_station_into_a_zone():
    d = factory_map.load(ROOT)
    placed = sorted(i for z in d["zones"] for i in z["stations"])
    assert placed == list(range(len(d["stations"])))


def test_map_anchors_are_real_headings():
    html = (ROOT / "build" / "preview" / "dist" / "concepts" / "software-factory.html")
    d = factory_map.load(ROOT)
    if html.exists():
        text = html.read_text()
        for s in d["stations"]:
            assert f'id="{s["anchor"]}"' in text


def test_map_rejects_missing_anchor(tmp_path):
    p = copy(tmp_path, "factory-map", with_page=True)
    edit(p, "factory-map", "anchor: 1-orders-come-in", "anchor: 1-orders-go-out")
    with pytest.raises(widgets.WidgetError, match="not a heading"):
        factory_map.load(p)


def test_map_rejects_unknown_zone(tmp_path):
    p = copy(tmp_path, "factory-map")
    edit(p, "factory-map", "zone: back", "zone: basement")
    with pytest.raises(widgets.WidgetError, match="unknown zone"):
        factory_map.load(p)


def test_run_tracks_visits_and_reentry():
    d = factory_run.load(ROOT)
    implement = d["phases"].index("IMPLEMENT")
    last = d["steps"][-1]
    assert all(last["visited"])
    assert last["reentered"][implement]
    assert last["pr"] == "#87"
    assert d["steps"][0]["pr"] == ""


def test_run_rejects_unconfirmed_phase(tmp_path):
    p = copy(tmp_path, "factory-run")
    edit(p, "factory-run", "  - phase: CLAIMED", "  - phase: GRABBED")
    with pytest.raises(widgets.WidgetError, match="unknown phase"):
        factory_run.load(p)


def test_run_rejects_changed_columns(tmp_path):
    p = copy(tmp_path, "factory-run")
    edit(p, "factory-run", "AWAIT MRG, RESOLVED]", "MERGED, RESOLVED]")
    with pytest.raises(widgets.WidgetError, match="Item lanes columns"):
        factory_run.load(p)


def test_markdown_versions():
    assert "Orders in" in factory_map.markdown(factory_map.load(ROOT))
    assert "AWAIT CI" in factory_run.markdown(factory_run.load(ROOT))


def test_map_every_station_has_papers_and_a_lab_result():
    d = factory_map.load(ROOT)
    for s in d["stations"]:
        assert s["papers"]
        assert s["tested"]["label"] in factory_map.STATUSES.values()
        assert s["tested"]["note"]


def test_map_rejects_unknown_paper(tmp_path):
    p = copy(tmp_path, "factory-map")
    edit(p, "factory-map", "papers: [dora]", "papers: [gartner]")
    with pytest.raises(widgets.WidgetError, match="unknown paper"):
        factory_map.load(p)


def test_map_rejects_unknown_lab_status(tmp_path):
    p = copy(tmp_path, "factory-map")
    edit(p, "factory-map", "status: none, note: \"Not tested.\"", "status: maybe, note: \"Not tested.\"")
    with pytest.raises(widgets.WidgetError, match="tested needs a status"):
        factory_map.load(p)
