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
    assert facts["publication_authority"] == "GitHub verified signed tags, immutable Releases, workflow evidence, and Pages production verification"

def test_unevidenced_human_uat_is_not_promoted() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["browser_uat_contract"] == "version-neutral-14-profile-automated-contract-including-seven-42-contract-viewports"
    assert facts["human_real_device_uat_attestation"] == "NOT_ATTESTED"
    assert facts["human_assistive_technology_uat_attestation"] == "NOT_ATTESTED"
    assert facts["selected_pathways_human_desktop_visual_uat"] == "PASS_USER_REVIEW_2026-08-13"
    assert facts["selected_pathways_human_mobile_visual_uat"] == "NOT_SEPARATELY_ATTESTED"

    admitted = facts["historical_foundation_baseline_browser_attestation"]
    assert admitted["source_identity"] == "v0.7.1-foundation-baseline"
    assert admitted["commit"] == "12e80d232c59e5221747353f963e71aba2df51d4"
    assert admitted["status"] == "PASS"
    assert facts["browser_uat_profile_count"] == admitted["result_profile_count"] == 14
    assert facts["browser_uat_configured_profile_count"] == 14
    assert facts["browser_uat_current_source_expected_result_profile_count"] == 14
    assert facts["browser_uat_reduced_motion_contract"] == "REQUIRED"
    assert facts["browser_uat_performance"] == "NOT_SEPARATELY_ATTESTED"

def test_visual_baseline_identity_is_preserved() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["visual_experience_baseline_version"] == "0.5.0"
    assert facts["source_version"] == facts["version"]
    assert facts["visual_experience_source_status"] == "v0.7.2-corrective-maintenance-external-publication-authority-is-GitHub"
    assert facts["visual_experience_status"] == "field-focus-proof-selected-pathways-progressive-disclosure"
    historical = facts["production_source_stored_historical_baseline"]
    assert historical == {"release": "v0.5.0", "readback": "PASS_V050_EXACT_PUBLIC_BYTES"}
    admitted = facts["historical_foundation_baseline_production_attestation"]
    assert admitted["source_identity"] == "v0.7.1-foundation-baseline"
    assert admitted["status"] == "PASS"
    assert admitted["commit"] == "12e80d232c59e5221747353f963e71aba2df51d4"

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
