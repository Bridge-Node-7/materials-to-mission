from __future__ import annotations
import json
from pathlib import Path
from materials_to_mission.validation_profiles import STRICT_PROFILE_ID, STRICT_V040_PROFILE_ID
from materials_to_mission.validator import validate_case

ROOT = Path(__file__).resolve().parents[1]

def _case() -> dict:
    return json.loads((ROOT / "examples/synthetic-critical-material-pathway/case.json").read_text(encoding="utf-8"))

def test_v031_release_history_is_preserved_in_changelog() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.3.1] - 2026-08-10" in changelog
    assert "Immutable v0.3.1 release history" in changelog

def test_released_profile_behavior_remains_preserved() -> None:
    case = _case()
    case["decision_charter"]["decision_owner"] = "Scoring Engine"
    case["decision_passport"]["decision_owner"] = "Scoring Engine"
    assert "HUMAN_AUTHORITY" not in {x.code for x in validate_case(case, public=True, profile=STRICT_PROFILE_ID).findings}
    assert any(x.code == "HUMAN_AUTHORITY" for x in validate_case(case, public=True, profile=STRICT_V040_PROFILE_ID).findings)

def test_ga001_wording_and_versions_remain_frozen() -> None:
    view = json.loads((ROOT / "public-snapshots/gallium/GA-001/public-view.json").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in view["trace_nodes"]}
    assert nodes["ga-required-form"]["label"] == "Observed U.S. use forms · GaAs / GaN / GaP wafers"
    assert nodes["ga-system"]["label"] == "Semiconductor-sector use context"
    assert view["toolkit_version"] == "0.2.0"
    assert view["view_contract_version"] == "0.3.0"

def test_v050_precision_experience_contract() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    assert "Strategic Constellation" in html
    assert "Evidence Horizon" in html
    assert "Evidence informs." in html
    assert "View Public Method" in html
    assert "Back to Materials" in html
    assert "width:44px" in css.replace(" ", "")
    assert "min-width:820px" in css.replace(" ", "")
