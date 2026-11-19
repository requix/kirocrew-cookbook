"""Tests for the conductor-run widget: YAML validation and the derived Board text."""
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build" / "preview"))

import widgets  # noqa: E402
from widgets import conductor_run  # noqa: E402

YAML = ROOT / "content" / "widgets" / "conductor-run.yaml"


@pytest.fixture
def project(tmp_path):
    (tmp_path / "content" / "widgets").mkdir(parents=True)
    shutil.copy(YAML, tmp_path / "content" / "widgets" / "conductor-run.yaml")
    return tmp_path


def edit(project, old, new, count=1):
    p = project / "content" / "widgets" / "conductor-run.yaml"
    text = p.read_text()
    assert old in text
    p.write_text(text.replace(old, new, count))


def test_real_yaml_loads():
    data = conductor_run.load(ROOT)
    assert len(data["steps"]) == 7
    assert len(data["steps"][0]["workers"]) == 4


def test_rejects_unknown_worker_state(project):
    edit(project, "w1: working", "w1: flying")
    with pytest.raises(widgets.WidgetError, match="unknown state"):
        conductor_run.load(project)


def test_rejects_unknown_conductor_state(project):
    edit(project, "conductor: planning", "conductor: dreaming")
    with pytest.raises(widgets.WidgetError, match="unknown conductor state"):
        conductor_run.load(project)


def test_rejects_unknown_worker_and_missing_worker(project):
    edit(project, "{ w1: absent, w2: absent, w3: absent, w4: absent }", "{ w1: absent, w2: absent, w3: absent, w9: absent }")
    with pytest.raises(widgets.WidgetError, match="unknown worker"):
        conductor_run.load(project)


def test_rejects_unconfirmed_board_label(project):
    edit(project, "milestones: Milestones", "milestones: Goals")
    with pytest.raises(widgets.WidgetError, match="Board wording"):
        conductor_run.load(project)


def test_rejects_middle_dot(project):
    edit(project, "It dispatches workers, one chat per item.", "It dispatches workers · one chat per item.")
    with pytest.raises(widgets.WidgetError, match="must not contain"):
        conductor_run.load(project)


def test_recap_and_board_per_step():
    s = conductor_run.load(ROOT)["steps"]
    assert s[0]["recap"] == "The crew has not reported yet."
    assert s[0]["milestones"] == ""
    assert s[1]["recap"] == "0 of 4 done; 4 running."
    assert s[2]["recap"] == "1 of 4 done; Worker 3 is waiting on you."
    assert s[2]["needs_you"] == ["Worker 3"]
    assert s[3]["recap"] == "1 of 4 done; Worker 3 is waiting on you."
    assert s[4]["paused"] and s[4]["control"] == "Pause all"
    assert [w["state"] for w in s[4]["workers"]] == ["done", "paused", "waiting", "paused"]
    assert s[5]["control"] == "Resume all" and not s[5]["paused"]
    assert s[6]["recap"] == "4 of 4 done."
    assert s[6]["milestones"] == "4 of 4"
    assert s[6]["needs_you"] == []


def test_markdown_not_empty():
    md = conductor_run.markdown(conductor_run.load(ROOT))
    assert "4 of 4 done." in md and md.strip()
