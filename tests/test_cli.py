import json
import time
import pytest
from sparrow_project_health_monitor.cli import main
from sparrow_project_health_monitor.fixtures import generate


def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start = time.perf_counter()
    assert main(["fixtures", "--out", "demo"]) == 0
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--format", "md"]) == 0
    assert "Data provenance" in capsys.readouterr().out
    assert time.perf_counter() - start < 5


def test_empty_input_renders_without_traceback(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(tmp_path)
    assert main(["run", "--input", str(empty)]) == 0
    assert main(["report", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out.split("\n", 1)[1])["totals"]["projects"] == 0


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "projects.json").write_text('{\n invalid')
    assert main(["run", "--input", str(tmp_path)]) == 2
    assert "projects.json line 2" in capsys.readouterr().err


def test_determinism_byte_identical(tmp_path, monkeypatch):
    generate(tmp_path / "demo")
    monkeypatch.chdir(tmp_path)
    for n in (1, 2):
        assert main(["run", "--input", "demo", "--results", f"r{n}.json"]) == 0
        assert main(["report", "--results", f"r{n}.json", "--out", f"r{n}.md"]) == 0
    assert (tmp_path / "r1.json").read_bytes() == (tmp_path / "r2.json").read_bytes()
    assert (tmp_path / "r1.md").read_bytes() == (tmp_path / "r2.md").read_bytes()


def test_cli_smoke_all_subcommands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for command in ("fixtures", "run", "report", "risks", "check"):
        with pytest.raises(SystemExit) as exc:
            main([command, "--help"])
        assert exc.value.code == 0
    generate(tmp_path / "demo")
    assert main(["risks", "--input", "demo"]) == 0
    assert main(["check", "--input", "demo", "--id", "P001"]) == 0


def test_missing_input(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "absent")]) == 2
    assert "MissingInput" in capsys.readouterr().err


def test_report_write_failure_no_partial(tmp_path, monkeypatch, capsys):
    generate(tmp_path / "demo")
    monkeypatch.chdir(tmp_path)
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--out", "absent/report.md"]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert [p.name for p in tmp_path.glob(".sphm-*")] == [".sphm-results.json"]


def test_malformed_saved_report(tmp_path, capsys):
    p = tmp_path / "result.json"
    p.write_text('{"projects": [null]}')
    assert main(["report", "--results", str(p)]) == 2
    assert "SchemaError" in capsys.readouterr().err
