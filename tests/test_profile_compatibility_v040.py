from __future__ import annotations
import copy
import json
from pathlib import Path
from materials_to_mission.validation_profiles import (
    DEFAULT_VALIDATION_PROFILE,
    STRICT_PROFILE_ID,
    STRICT_V040_PROFILE_ID,
)
from materials_to_mission.validator import validate_case

ROOT = Path(__file__).resolve().parents[1]

def _case() -> dict:
    return json.loads((ROOT / "examples/synthetic-critical-material-pathway/case.json").read_text(encoding="utf-8"))

def test_default_validation_profile_identity_remains_v040() -> None:
    facts = json.loads(
        (ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8")
    )
    assert DEFAULT_VALIDATION_PROFILE == STRICT_V040_PROFILE_ID
    assert facts["validation_profile_default"] == STRICT_V040_PROFILE_ID

def test_strict_020_acceptance_surface_is_preserved_for_new_aliases() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = copy.deepcopy(_case())
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
        assert "HUMAN_AUTHORITY" not in {finding.code for finding in result.findings}

def test_strict_040_alias_rejection_remains_preserved() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = copy.deepcopy(_case())
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_V040_PROFILE_ID)
        assert not result.valid
        assert any(finding.code == "HUMAN_AUTHORITY" for finding in result.findings)
