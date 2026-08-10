from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from materials_to_mission.validation_profiles import (
    STRICT_PROFILE_ID,
    STRICT_V040_PROFILE_ID,
)
from materials_to_mission.validator import validate_case

ROOT = Path(__file__).resolve().parents[1]


def _case() -> dict:
    return json.loads((ROOT / "examples/synthetic-critical-material-pathway/case.json").read_text(encoding="utf-8"))


def test_v031_release_record_is_preserved() -> None:
    assert (ROOT / "RELEASE_NOTES_v0.3.1.md").is_file()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.3.1] - 2026-08-10" in changelog


def test_v031_aliases_do_not_rewrite_released_strict_020_behavior() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = _case()
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
        assert "HUMAN_AUTHORITY" not in {item.code for item in result.findings}, (
            alias,
            result.findings,
        )


def test_v040_aliases_fail_closed_under_new_strict_profile() -> None:
    for alias in ("Scoring Engine", "Rules Engine", "Inference Service"):
        case = _case()
        case["decision_charter"]["decision_owner"] = alias
        case["decision_passport"]["decision_owner"] = alias
        result = validate_case(case, public=True, profile=STRICT_V040_PROFILE_ID)
        assert not result.valid
        assert any(
            item.code == "HUMAN_AUTHORITY"
            and item.path == "$.decision_charter.decision_owner"
            for item in result.findings
        ), (alias, result.findings)


def test_ga001_display_wording_is_bounded() -> None:
    view = json.loads((ROOT / "public-snapshots/gallium/GA-001/public-view.json").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in view["trace_nodes"]}
    assert nodes["ga-required-form"]["label"] == "Observed U.S. use forms · GaAs / GaN / GaP wafers"
    assert nodes["ga-system"]["label"] == "Semiconductor-sector use context"
    assert view["toolkit_version"] == "0.2.0"
    assert view["view_contract_version"] == "0.3.0"


def test_browser_completion_and_local_preview_contract() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    preview = (ROOT / "web/README.md").read_text(encoding="utf-8")
    assert "Public snapshot available" in html
    assert "Public evidence state" in html
    assert "Follow every stage. Unknown stays unknown." in html
    assert "Open any displayed claim" in html
    assert "Snapshot toolkit" in html
    assert "View Public Method" in html
    assert "Back to Materials" in html
    assert "width: 46px;" in css and "height: 46px;" in css
    mobile = css.split("@media (max-width: 900px)", 1)[1]
    assert "min-width: 0;" in mobile
    assert "display: flex;" in mobile
    assert "scripts/build_web.py --output build/web-preview" in preview
    assert "http.server 8000 --directory build/web-preview" in preview
