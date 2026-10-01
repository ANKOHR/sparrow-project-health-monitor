import json
from sparrow_project_health_monitor.fixtures import generate
from sparrow_project_health_monitor.cli import load
from sparrow_project_health_monitor.core import analyze


def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    for path in tmp_path.iterdir():
        data = json.loads(path.read_text())
        assert data["synthetic"] is True
        assert "SYNTHETIC" in data["_comment"]
        assert all(r["synthetic"] for r in data.get("projects", []))


def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path)
    expected = json.loads((tmp_path / "expectations.json").read_text())
    actual = analyze(load(tmp_path))
    assert actual["totals"] == expected["totals"]
    assert actual["reason_counts"] == expected["reason_counts"]
    assert [r["id"] for r in actual["projects"] if r["flagged"]] == expected["flagged_ids"]


def test_corrupted_input_changes_report(tmp_path):
    generate(tmp_path)
    path = tmp_path / "projects.json"
    data = json.loads(path.read_text())
    data["projects"][0]["spent_cents"] = 20000
    path.write_text(json.dumps(data))
    assert analyze(load(tmp_path))["totals"]["flagged"] == 161


def test_corrupted_ground_truth_detected(tmp_path):
    generate(tmp_path)
    path = tmp_path / "expectations.json"
    data = json.loads(path.read_text())
    data["totals"]["flagged"] = 0
    path.write_text(json.dumps(data))
    assert analyze(load(tmp_path))["totals"] != json.loads(path.read_text())["totals"]
