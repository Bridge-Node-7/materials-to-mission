from pathlib import Path

from materials_to_mission.cli import main


def test_cli_validate(root, capsys):
    code = main(["validate", str(root / "examples/synthetic-critical-material-pathway/case.json"), "--public"])
    assert code == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_render(root, tmp_path):
    output = tmp_path / "passport.md"
    code = main(["render", str(root / "examples/synthetic-critical-material-pathway/case.json"), "--output", str(output)])
    assert code == 0
    assert output.exists()
    assert "Decision Passport" in output.read_text()


def test_cli_invalid_returns_two(root):
    code = main(["validate", str(root / "examples/invalid/triggered-critical-advance.json"), "--public"])
    assert code == 2
