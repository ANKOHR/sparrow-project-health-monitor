# Sparrow Project Health Monitor

Sparrow returns time to small business owners through tools that perform explicit operational checks. This Python CLI flags projects whose entered facts already indicate missed expectations. It does not forecast delivery, discover facts, estimate completion, or measure savings.

## Hypothesis and acceptance

A deterministic CLI can reliably identify explicitly overdue, over-budget and blocked projects. Acceptance: on 200 labelled synthetic records, all 160 planted flagged projects are found with zero false positives, all counts and integer money totals match independent hand calculations, and the full demo takes under five seconds. This validates rule implementation on planted facts, not real-world predictive accuracy or buyer demand.

## Quickstart (CPU only, local files)

Python 3.10 or newer and setuptools are required. No runtime dependencies. Installation can be done offline with available setuptools:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
sphm fixtures --out demo
sphm run --input demo
sphm report --format md
python -m pytest -q
```

POSIX shells can join the three demo commands with `&&`; Windows PowerShell users can run them on separate lines. No commands in this project call the network. pytest is a development dependency and must already be installed for offline testing.

If `sphm` is outside PATH, use `python -m sparrow_project_health_monitor.cli` in place of `sphm`, or add the installer-reported Scripts directory to PATH.

A ready five-record input is included at `examples/tiny/projects.json`: run `sphm run --input examples/tiny`.

For a tiny example, copy `demo/tiny.json.example` to `tiny/projects.json` after creating the `tiny` directory, then run `sphm run --input tiny`. It contains five explicitly written rule combinations. The generator emits 200 records for the acceptance demo.

## Input format

The input directory contains `projects.json`, a UTF-8 JSON envelope. Only this named file is parsed. `expectations.json` is separate test evidence and is never used to compute reports. Unsupported formats are not parsed. A nonempty directory without projects.json yields MissingInput; an empty directory produces a zero report.

```json
{
  "_comment": "SYNTHETIC illustrative example",
  "synthetic": true,
  "projects": [
    {
      "id": "example-1",
      "name": "Illustrative refurbishment",
      "synthetic": true,
      "as_of": "2026-09-30",
      "start_date": "2026-09-01",
      "due_date": "2026-09-29",
      "budget_cents": 10000,
      "spent_cents": 12000,
      "progress_percent": 50,
      "blocked": true
    }
  ]
}
```

Every field shown is required. Unknown fields are rejected. IDs are unique; IDs and names accept Unicode and Windows path text, with 1 to 10000 characters and some non-whitespace content. Money is nonnegative integer cents, at most 10^15, in a single currency chosen by the caller; currency conversion and mixed currencies are unsupported. Progress is integer 0 through 100; booleans must be actual booleans, not integers. Dates must use canonical YYYY-MM-DD. Start must be no later than as_of, and due must be no earlier than start. Future due dates are valid. Future starts relative to as_of are rejected. The CLI never compares to the machine clock, so historic or future snapshots are reproducible.

The envelope synthetic flag must equal whether every record is synthetic, including true for an empty list. Mixed files use false at envelope level and retain per-record labels. For Henry's manually entered real data, use false on those records and an accurate comment. Real data and trial results are not shipped or committed. Provenance is caller-declared, not independently authenticated.

## Rules and traceability

- overdue: due_date is strictly earlier than as_of and progress is below 100.
- over_budget: spent_cents is strictly greater than budget_cents, including completed projects.
- blocked: blocked is true and progress is below 100.

A project is flagged if any rule triggers. Reason counts overlap, so their sum need not equal flagged count. Budget and spending totals include all projects, flagged or otherwise. All money calculations use integer cents. Every report includes project IDs, labels, amounts and rule reasons; JSON also includes the full facts, progress, dates and provenance ID lists. Markdown shows each project's status, while JSON supplies all fields for auditing.

## Subcommand catalogue

```text
sphm fixtures --out demo
sphm run --input demo --results results.json
sphm report --results results.json --format json --out report.json
sphm report --results results.json --format md --out report.md
sphm risks --input demo
sphm check --input demo --id P001
```

`fixtures` generates the labelled acceptance set and independent expectations. `run` validates input and atomically writes `.sphm-results.json` by default. `report` recomputes saved records, never trusting saved totals or labels for rule results; rerun after changing source input. `risks` lists flagged projects and `check` explains one project. Their summary totals describe the whole input, while their project lists are filtered. Each command has `--help` and an example. Outputs overwrite explicitly selected files atomically; output parent directories must already exist. Error exit code is 2; success is 0.

## Architecture

```text
fixtures.py -> labelled local JSON + independent expectations
local projects.json -> cli.py validation -> core.py pure rules
core.py results -> atomic saved JSON -> report.py -> Markdown / JSON
pytest -> planted truth, adversarial inputs, determinism, CLI demo
```

## Honesty boundary

Synthetic results are illustrative, not measured business outcomes. Every fixture contains a SYNTHETIC comment field and synthetic: true, including the five-record example and expectations file. JSON has no header comment syntax, so `_comment` is the in-file header comment. Every report carries a provenance banner and per-record labels. The CLI computes only explicit input facts. There is no model, network, GPU workload, random generator, inferred schedule, or risk probability. Enumeration requires no seed. Sorting by ID and fixed serialization make repeat outputs byte-identical. Input em dash characters are rendered as ASCII hyphens to meet the output constraint.

Time saved and money saved are unmeasured and are not reported. Measured demo runtime is only execution performance, not business time saved. A future savings claim requires an actual measured baseline and recorded method. No real trial accuracy or commercial verdict is invented.

## Failure modes and limits

Malformed JSON produces ParseError with file and parser line. UTF-8 and filesystem failures produce ReadError with file and line 1. Schema errors name the source file, offending field and record index where relevant; line 1 denotes document-level validation, not exact token position. Missing paths give MissingInput and a usage hint. Invalid records and duplicate IDs fail the entire run; none are silently dropped. Writes use temporary files in the destination directory and atomic replacement; WriteError leaves no partial report. Existing results remain intact on a failed run, so check exit codes to avoid using stale results.

Flags are only as accurate as entered facts. Undeclared currency mixing, incorrect progress, unreported blockers and unrealistic budgets cannot be detected. No historical prediction calibration has been performed. Large inputs are memory-bound. No claimed real adoption, revenue or savings exist in this build.

## Evidence-based improvement and verdict

After two weeks of Henry's real use, hand-check each project's rule status in a sample and record disagreements / sampled projects as the error rate. Also record runs used and whether a buyer paid or expressed willingness to pay. Keep that real evidence locally outside the shipped repository. If error exceeds 10 percent, identify and fix the top failure cause; if unused, record why and kill. A real trial has not begun, so its dates and results are unmeasured.

Verdict is pending the two-week evidence window. Then record a reason: expand for daily use or revenue, integrate for heavy sibling overlap, commercialise if a buyer would pay as-is, maintain as portfolio evidence otherwise, or kill if unused or unable to meet acceptance. Passing synthetic tests alone does not justify commercialisation. See VERDICT.md for the decision record.
