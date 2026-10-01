import json
from sparrow_project_health_monitor.core import analyze
from sparrow_project_health_monitor.fixtures import fixture_records
from sparrow_project_health_monitor.report import render


def test_report_matches_ground_truth_exact():
    report = json.loads(render(analyze(fixture_records()), "json"))
    assert report["totals"] == dict(projects=200, flagged=160, budget_cents=2000000, spent_cents=1560000)
    assert report["reason_counts"] == dict(overdue=80, over_budget=80, blocked=80)


def test_report_zero_false_positives():
    report = json.loads(render(analyze(fixture_records()), "json"))
    assert {r["id"] for r in report["projects"] if r["flagged"]} == {f"P{i:03d}" for i in range(200) if i % 5}


def test_report_carries_provenance_banner():
    r = fixture_records(2)
    r[0]["synthetic"] = False
    for format in ("md", "json"):
        output = render(analyze(r), format)
        assert "Data provenance" in output
        assert "Henry" in output
        assert "P000" in output and "P001" in output


def test_hypothetical_figures_labelled():
    for format in ("md", "json"):
        output = render(analyze(fixture_records()), format)
        assert "illustrative" in output
        assert "unmeasured and not reported" in output
        assert "not predictions" in output


def test_no_em_dashes_in_outputs():
    r = fixture_records(1)
    r[0]["name"] = "name" + chr(0x2014)
    for format in ("md", "json"):
        assert chr(0x2014) not in render(analyze(r), format)
