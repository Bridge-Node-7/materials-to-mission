from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_release_workflow_contract() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_gate_contracts.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS - hosted Release workflow contract" in result.stdout
