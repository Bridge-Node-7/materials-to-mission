from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from materials_to_mission.validation_profiles import (
    DEFAULT_VALIDATION_PROFILE,
    STRICT_PROFILE_ID,
)


ROOT = Path(__file__).resolve().parents[1]
GA_ROOT = ROOT / "public-snapshots" / "gallium" / "GA-001"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _built_html(tmp_path: Path) -> str:
    output = tmp_path / "web"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_web.py"), "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    return (output / "index.html").read_text(encoding="utf-8")


def test_public_language_and_evidence_boundaries(tmp_path: Path) -> None:
    html = _built_html(tmp_path)
    assert "M0 Public Method" not in html
    assert "M0 identifies" not in html
    assert "BN7-specific precursor" not in html
    assert "mission-specific precursor form" in html
    assert "GA-001 historical snapshot profile" in html
    assert STRICT_PROFILE_ID in html
    assert "Reviewed does not mean qualified." in html
    assert "Human decision authority remains required." in html
    assert "does not indicate readiness, qualification, certification, or acquisition approval" in html


def test_profile_identities_defaults_and_ga001_history_are_immutable() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    view = json.loads((GA_ROOT / "public-view.json").read_text(encoding="utf-8"))

    assert DEFAULT_VALIDATION_PROFILE == facts["validation_profile_default"] == "m0-strict-0.4.0"
    assert {"m0-baseline-0.1.0", "m0-strict-0.2.0", "m0-strict-0.4.0"} <= set(
        facts["validation_profiles"]
    )
    assert view["validation_profile"] == STRICT_PROFILE_ID == "m0-strict-0.2.0"
    assert _sha256(GA_ROOT / "snapshot.json") == "6e100f9e1c3bac48fa93ee7b0838c117e8e67313fa0540f918058eec7ea0e968"
    assert _sha256(GA_ROOT / "public-view.json") == "31bdbf1a074e1f838205eab16c32ee02b8e3ee1a75899d0e476db0ce9fdf8676"
