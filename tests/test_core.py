import pytest
from sparrow_project_health_monitor.core import analyze, InputError
from sparrow_project_health_monitor.fixtures import fixture_records


@pytest.mark.parametrize("field,value", [("spent_cents", -1), ("budget_cents", True),
    ("progress_percent", 101), ("start_date", "2027-01-01"), ("due_date", "invalid"),
    ("name", "x" * 10001), ("blocked", 1), ("spent_cents", 10**16)])
def test_rejects_adversarial_values(field, value):
    records = fixture_records(1)
    records[0][field] = value
    with pytest.raises(InputError, match=field):
        analyze(records)


def test_duplicate_ids():
    r = fixture_records(1)
    with pytest.raises(InputError, match="duplicate id"):
        analyze(r + r)


def test_handles_unicode_and_long_inputs():
    r = fixture_records(1)
    r[0]["name"] = "你好 café C:\\Users\\henry " + "x" * 9000
    assert analyze(r)["projects"][0]["name"] == r[0]["name"]


def test_boundaries_completed_and_future_due():
    r = fixture_records(5)
    r[4]["progress_percent"] = 100
    assert analyze(r)["projects"][4]["reasons"] == ["over_budget"]
    r[1]["due_date"] = r[1]["as_of"]
    assert not analyze(r)["projects"][1]["flagged"]


def test_schema_drift():
    r = fixture_records(1)
    r[0]["estimate"] = 1
    with pytest.raises(InputError, match="estimate"):
        analyze(r)
