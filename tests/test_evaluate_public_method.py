from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_guided_public_evaluator() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/evaluate_public_method.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS - SYNTHETIC CASE VALID" in result.stdout
    assert "PASS - DECISION PASSPORT WRITTEN" in result.stdout
    assert "PASS - FAIL-CLOSED EXAMPLE CONFIRMED" in result.stdout
    assert "NEXT - OPEN build/guided-decision-passport.md" in result.stdout
    assert (ROOT / "build/guided-decision-passport.md").is_file()
