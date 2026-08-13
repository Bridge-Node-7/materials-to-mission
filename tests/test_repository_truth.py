from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_release_identity_axes_align() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", citation)
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert project["project"]["version"] == version
    assert facts["version"] == version
    assert match and match.group(1) == version
    assert facts["release_artifact"] == f"materials-to-mission-v{version}.zip"
    assert facts["release_notes"] == f"RELEASE_NOTES_v{version}.md"

def test_public_maturity_and_human_authority_remain_bounded() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["current_public_maturity"] == "M0"
    assert facts["real_case_count"] == 0
    assert facts["m1_real_workflow_proof_claimed"] is False
    assert facts["human_decision_authority_required"] is True
    assert facts["real_world_qualification_claimed"] is False

def test_external_release_authority_remains_durable() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["public_release_status"] == "governed-by-verified-tag-and-immutable-github-release"
    assert facts["release_publication_authority"] == "GitHub verified signed tags and immutable Releases"

def test_unevidenced_human_uat_is_not_promoted() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["browser_uat_status"] == "v0.6.0-browser-gate-required-before-release; A1-A9 automated closeout plus browser contract; human-device-AT not separately attested"
    assert facts["browser_uat_profile_count"] == 0
    assert facts["browser_uat_configured_profile_count"] == 12
    for key in (
        "browser_uat_accessibility", "browser_uat_narrow_320", "browser_uat_performance",
        "browser_uat_primary", "browser_uat_reduced_motion", "browser_uat_security",
        "browser_uat_zoom_200_reflow",
    ):
        assert facts[key] == "OPEN"

def test_visual_baseline_identity_is_preserved() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["visual_experience_baseline_version"] == "0.5.0"
    assert facts["visual_experience_candidate_version"] == "0.6.0"
    assert facts["visual_experience_candidate_status"] == "release-gated-field-focus-proof"
    assert facts["visual_experience_status"] == "production-validated-r6-3-3-baseline"
    assert facts["production_deployment_readback"] == "PASS_V050_EXACT_PUBLIC_BYTES"

def test_public_safe_scope_is_machine_unambiguous() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["public_safe_examples_only"] is True
    assert facts["public_safe_examples_scope"] == "examples-directory-only"
    assert facts["public_source_snapshots_authorized"] is True
    assert facts["restricted_case_data_present"] is False
    assert facts["browser_uat_required_for_current_m0_gate"] is True


def test_codeql_covers_python_and_browser_javascript() -> None:
    workflow = (ROOT / ".github/workflows/codeql.yml").read_text(encoding="utf-8")
    assert "language: [python, javascript-typescript]" in workflow
    assert "languages: ${{ matrix.language }}" in workflow


def test_pages_requires_post_deploy_anonymous_readback() -> None:
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert "verify-production:" in workflow
    assert "needs: deploy" in workflow
    assert "scripts/verify_production.py" in workflow
    assert "https://bridgenode7.com/materials-to-mission/" in workflow
