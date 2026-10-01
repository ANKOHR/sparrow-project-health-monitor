"""Synthetic illustrative projects, deterministic enumeration; no random seed needed."""
import json
from pathlib import Path


def fixture_records(count=200):
    records = []
    for i in range(count):
        kind = i % 5
        records.append(dict(id=f"P{i:03d}", name=f"Synthetic project {i}", synthetic=True,
                            as_of="2026-09-30", start_date="2026-09-01",
                            due_date="2026-09-29" if kind in (1, 4) else "2026-10-15",
                            budget_cents=10000, spent_cents=12000 if kind in (2, 4) else 5000,
                            progress_percent=50, blocked=kind in (3, 4)))
    return records


def generate(out):
    directory = Path(out)
    directory.mkdir(parents=True, exist_ok=True)
    records = fixture_records()
    (directory / "projects.json").write_text(json.dumps({"_comment": "SYNTHETIC fixture, illustrative only",
        "synthetic": True, "projects": records}, indent=2) + "\n", encoding="utf-8")
    # Hand calculation: 40 groups of five, four flagged per group, two of each reason.
    expected = {"_comment": "SYNTHETIC hand-computed expectations, not engine output", "synthetic": True,
                "totals": {"projects": 200, "flagged": 160, "budget_cents": 2000000, "spent_cents": 1560000},
                "reason_counts": {"overdue": 80, "over_budget": 80, "blocked": 80},
                "flagged_ids": [f"P{i:03d}" for i in range(200) if i % 5 != 0]}
    (directory / "expectations.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    (directory / "tiny.json.example").write_text(json.dumps({"_comment": "SYNTHETIC five-record example; rename to projects.json in a separate directory",
        "synthetic": True, "projects": records[:5]}, indent=2) + "\n", encoding="utf-8")
