"""Pure deterministic rules. Risk flags are input-derived signals, not predictions."""
from datetime import date


class InputError(ValueError):
    """A named input or schema error suitable for CLI display."""


FIELDS = {"id", "name", "synthetic", "as_of", "start_date", "due_date",
          "budget_cents", "spent_cents", "progress_percent", "blocked"}


def validate(records):
    seen = set()
    for index, record in enumerate(records, 1):
        prefix = f"SchemaError record {index}"
        if not isinstance(record, dict):
            raise InputError(f"{prefix}: expected object")
        missing, extra = FIELDS - record.keys(), record.keys() - FIELDS
        if missing or extra:
            raise InputError(f"{prefix}: missing fields {sorted(missing)}, unknown fields {sorted(extra)}")
        for field in ("id", "name"):
            if not isinstance(record[field], str) or not record[field].strip() or len(record[field]) > 10000:
                raise InputError(f"{prefix}: {field} must be nonempty text of at most 10000 characters")
        if record["id"] in seen:
            raise InputError(f"{prefix}: duplicate id {record['id']!r}")
        seen.add(record["id"])
        for field in ("synthetic", "blocked"):
            if type(record[field]) is not bool:
                raise InputError(f"{prefix}: {field} must be boolean")
        for field in ("budget_cents", "spent_cents", "progress_percent"):
            value = record[field]
            maximum = 100 if field == "progress_percent" else 10**15
            if type(value) is not int or not 0 <= value <= maximum:
                raise InputError(f"{prefix}: {field} must be an integer in 0..{maximum}")
        for field in ("as_of", "start_date", "due_date"):
            try:
                value = record[field]
                if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                    raise ValueError()
            except (ValueError, TypeError):
                raise InputError(f"{prefix}: {field} must be YYYY-MM-DD") from None
        if record["start_date"] > record["as_of"]:
            raise InputError(f"{prefix}: start_date cannot be after as_of")
        if record["due_date"] < record["start_date"]:
            raise InputError(f"{prefix}: due_date cannot precede start_date")
    return records


def assess(record):
    reasons = []
    if record["progress_percent"] < 100 and record["due_date"] < record["as_of"]:
        reasons.append("overdue")
    if record["spent_cents"] > record["budget_cents"]:
        reasons.append("over_budget")
    if record["blocked"] and record["progress_percent"] < 100:
        reasons.append("blocked")
    return {**record, "flagged": bool(reasons), "reasons": reasons}


def analyze(records):
    validate(records)
    projects = [assess(r) for r in sorted(records, key=lambda r: r["id"])]
    return {"schema_version": 1,
            "provenance": {"synthetic_records": sum(r["synthetic"] for r in records),
                           "real_records": sum(not r["synthetic"] for r in records),
                           "synthetic_ids": [r["id"] for r in projects if r["synthetic"]],
                           "real_ids": [r["id"] for r in projects if not r["synthetic"]]},
            "totals": {"projects": len(records), "flagged": sum(r["flagged"] for r in projects),
                       "budget_cents": sum(r["budget_cents"] for r in records),
                       "spent_cents": sum(r["spent_cents"] for r in records)},
            "reason_counts": {k: sum(k in r["reasons"] for r in projects)
                              for k in ("overdue", "over_budget", "blocked")},
            "projects": projects}
