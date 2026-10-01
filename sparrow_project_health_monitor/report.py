"""Reports label provenance and never claim measured savings or predictive accuracy."""
import json

BANNER = ("Data provenance: synthetic IDs are illustrative fixtures; real IDs are caller-declared "
          "real inputs (Henry's own data only when entered and declared by him). Origin is not independently verified. "
          "Flags are deterministic rule signals, not predictions. Time and money saved are unmeasured and not reported.")


def safe_text(value):
    return str(value).replace(chr(0x2014), "-")


def render(result, format="md"):
    if format == "json":
        return safe_text(json.dumps({"banner": BANNER, **result}, ensure_ascii=False, sort_keys=True, indent=2)) + "\n"
    p = result["provenance"]
    lines = ["# Sparrow Project Health Monitor", "", BANNER, "",
             f"Synthetic records: {p['synthetic_records']}; caller-declared real records: {p['real_records']}", "",
             "## Computed totals", ""]
    lines.extend(f"- {k}: {v}" for k, v in result["totals"].items())
    lines += ["", "## Rule counts (may overlap)", ""]
    lines.extend(f"- {k}: {v}" for k, v in result["reason_counts"].items())
    lines += ["", "## Projects and provenance", ""]
    for r in result["projects"]:
        name = safe_text(r["name"]).replace("\n", " ").replace("\r", " ")
        lines.append(f"- {safe_text(r['id'])}: {name}; {'synthetic' if r['synthetic'] else 'caller-declared real'}; "
                     f"{', '.join(r['reasons']) or 'no rule triggered'}; budget_cents={r['budget_cents']}; spent_cents={r['spent_cents']}")
    return "\n".join(lines) + "\n"
