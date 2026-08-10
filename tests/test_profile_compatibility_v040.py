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
    return json.loads(
        (ROOT / "examples/synthetic-critical-material-pathway/case.json").read_text(
            encoding="utf-8"
        )
    )


def test_v040_is_current_toolkit_identity() -> None:
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.4.0"
    assert DEFAULT_VALIDATION_PROFILE == STRICT_V040_PROFILE_ID


def test_strict_020_acceptance_surface_is_preserved_for_new_aliases() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = copy.deepcopy(_case())
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
        assert "HUMAN_AUTHORITY" not in {f.code for f in result.findings}


def test_strict_040_adds_versioned_alias_rejection() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = copy.deepcopy(_case())
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_V040_PROFILE_ID)
        assert not result.valid
        assert any(f.code == "HUMAN_AUTHORITY" for f in result.findings)
