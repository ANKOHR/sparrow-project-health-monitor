"""Local file CLI. No network, model calls, or estimated savings."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import InputError, analyze
from .fixtures import generate
from .report import render, safe_text


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"ParseError {path} line {exc.lineno}: {exc.msg}") from None
    except (OSError, UnicodeError) as exc:
        raise InputError(f"ReadError {path} line 1: {exc}") from None


def load(directory):
    root = Path(directory)
    if not root.is_dir():
        raise InputError(f"MissingInput {root}: use --input with an existing directory containing projects.json")
    path = root / "projects.json"
    if not path.exists():
        if any(root.iterdir()):
            raise InputError(f"MissingInput {path}: expected projects.json; only JSON project input is supported")
        return []
    data = read_json(path)
    if not isinstance(data, dict) or set(data) != {"_comment", "synthetic", "projects"}:
        raise InputError(f"SchemaError {path} line 1: fields must be _comment, synthetic, projects")
    if type(data["synthetic"]) is not bool or not isinstance(data["projects"], list) or not isinstance(data["_comment"], str):
        raise InputError(f"SchemaError {path} line 1: invalid synthetic, _comment or projects field")
    try:
        result = analyze(data["projects"])
    except InputError as exc:
        raise InputError(f"{path} line 1: {exc}") from None
    if data["synthetic"] != all(r["synthetic"] for r in data["projects"]):
        raise InputError(f"SchemaError {path} line 1: synthetic envelope must equal all record labels")
    return data["projects"]


def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         prefix=".sphm-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError {path}: {exc}") from None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def parser():
    p = argparse.ArgumentParser(description="Compute project expectation flags from explicit local inputs.")
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fixtures", help="Generate 200 labelled synthetic projects", epilog="Example: sphm fixtures --out demo")
    f.add_argument("--out", required=True)
    r = sub.add_parser("run", help="Compute and save project signals", epilog="Example: sphm run --input demo")
    r.add_argument("--input", required=True)
    r.add_argument("--results", default=".sphm-results.json")
    report = sub.add_parser("report", help="Render saved results with provenance", epilog="Example: sphm report --format md")
    report.add_argument("--format", choices=("md", "json"), default="md")
    report.add_argument("--results", default=".sphm-results.json")
    report.add_argument("--out")
    for command, help_text in (("risks", "List projects triggering expectation rules"), ("check", "Explain one project's rules")):
        d = sub.add_parser(command, help=help_text, epilog=f"Example: sphm {command} --input demo" + (" --id P001" if command == "check" else ""))
        d.add_argument("--input", required=True)
        if command == "check":
            d.add_argument("--id", required=True)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 synthetic illustrative projects; no measured savings.")
        elif args.command == "report":
            saved = read_json(Path(args.results))
            if not isinstance(saved, dict) or not isinstance(saved.get("projects"), list):
                raise InputError(f"SchemaError {args.results} line 1: missing projects")
            # Recompute from explicit saved records rather than trusting stored totals.
            if any(not isinstance(r, dict) for r in saved["projects"]):
                raise InputError(f"SchemaError {args.results} line 1: projects must contain objects")
            records = [{k: v for k, v in r.items() if k not in ("flagged", "reasons")} for r in saved["projects"]]
            output = render(analyze(records), args.format)
            if args.out:
                atomic_write(args.out, output)
            else:
                sys.stdout.write(output)
        else:
            result = analyze(load(args.input))
            if args.command == "run":
                atomic_write(args.results, render(result, "json"))
                print(f"Computed {result['totals']['projects']} projects, {result['totals']['flagged']} flagged. Input-declared provenance saved; signals are not predictions.")
            else:
                if args.command == "risks":
                    result["projects"] = [r for r in result["projects"] if r["flagged"]]
                else:
                    result["projects"] = [r for r in result["projects"] if r["id"] == args.id]
                    if not result["projects"]:
                        raise InputError(f"MissingProject: id {args.id!r} not found")
                sys.stdout.write(render(result, "md"))
        return 0
    except (InputError, OSError) as exc:
        print(safe_text(str(exc)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
