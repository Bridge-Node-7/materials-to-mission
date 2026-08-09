from __future__ import annotations

import json
from pathlib import Path

from materials_to_mission.cli import main


def test_cli_validate_json(root, capsys):
    code = main(["validate", str(root / "examples/synthetic-critical-material-pathway/case.json"), "--public", "--json"])
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["valid"] is True


def test_cli_render_stdout(root, capsys):
    code = main(["render", str(root / "examples/synthetic-critical-material-pathway/case.json")])
    assert code == 0
    assert "Decision Passport" in capsys.readouterr().out


def test_cli_render_rejects_invalid(root, capsys):
    code = main(["render", str(root / "examples/invalid/triggered-critical-advance.json")])
    assert code == 2
    assert "CRITICAL_CONDITION" in capsys.readouterr().err


def test_cli_scan_clean(root, capsys):
    code = main(["scan", str(root / "examples/synthetic-critical-material-pathway/case.json")])
    assert code == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_scan_bad_json_output(root, capsys):
    code = main(["scan", str(root / "examples/invalid/protected-public-token.json"), "--json"])
    output = json.loads(capsys.readouterr().out)
    assert code == 2
    assert output["clean"] is False


def test_cli_package(root, tmp_path, capsys):
    code = main(["package", "--root", str(root), "--output-dir", str(tmp_path)])
    assert code == 0
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    archive = tmp_path / f"materials-to-mission-v{version}.zip"
    checksum = tmp_path / f"materials-to-mission-v{version}.zip.sha256"
    assert archive.exists()
    assert checksum.exists()
    assert "SHA-256" in capsys.readouterr().out


def test_cli_schema_dir(capsys):
    code = main(["schema-dir"])
    assert code == 0
    assert "schemas" in capsys.readouterr().out


def test_cli_missing_input_returns_three(capsys):
    code = main(["validate", "does-not-exist.json"])
    assert code == 3
    assert "STOP" in capsys.readouterr().err



def test_cli_invalid_json_is_machine_readable(root, capsys):
    code = main(["validate", str(root / "examples/invalid/missing-human-owner.json"), "--public", "--json"])
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert code == 2
    assert output["valid"] is False
    assert output["findings"]
    assert captured.err == ""


def test_cli_help_has_examples_and_exit_codes(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    output = capsys.readouterr().out
    assert "examples:" in output
    assert "exit codes:" in output
    assert "m2m validate" in output



def test_cli_package_rejects_repository_root_output(tmp_path, capsys):
    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    code = main(["package", "--root", str(root), "--output-dir", str(root)])
    captured = capsys.readouterr()
    assert code == 3
    assert "cannot be the repository root" in captured.err
    assert not (root / "materials-to-mission-v0.1.0.zip").exists()


def test_cli_package_rejects_symlink_without_traceback(tmp_path, capsys):
    import os
    import pytest

    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    try:
        os.symlink("/etc/hosts", root / "leak.txt")
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable in this environment")
    code = main(["package", "--root", str(root), "--output-dir", str(tmp_path / "out")])
    captured = capsys.readouterr()
    assert code == 3
    assert captured.out == ""
    assert "symbolic links are not permitted" in captured.err
    assert "Traceback" not in captured.err
