from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_identity_axes_align() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    facts = json.loads(
        (ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8")
    )
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", citation)

    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert pyproject["project"]["version"] == version
    assert facts["version"] == version
    assert match
    assert match.group(1) == version


def test_active_truth_records_remove_candidate_era_release_state() -> None:
    paths = [
        ROOT / "PROJECT_FACTS.json",
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "docs/CURRENT_STATE.md",
        ROOT / "docs/PROGRAM_REGISTER.md",
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in paths
    )

    forbidden = [
        "candidate-v0.5.0-not-released",
        "R6_CANDIDATE_OPEN_NOT_RELEASED",
        "preserved-v0.4.0-production-candidate-v0.5.0-not-deployed",
        "`v0.5.0` is the Precision Evidence Experience candidate",
        "Current release:        v0.4.0",
        "Version `v0.4.0` is the",
    ]

    for value in forbidden:
        assert value not in combined


def test_publication_authority_is_external_and_durable() -> None:
    facts = json.loads(
        (ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8")
    )
    current = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    register = (
        ROOT / "docs/PROGRAM_REGISTER.md"
    ).read_text(encoding="utf-8")

    assert facts["public_release_status"] == (
        "governed-by-verified-tag-and-immutable-github-release"
    )
    assert facts["release_publication_authority"] == (
        "GitHub verified signed tags and immutable Releases"
    )
    assert "External publication identity is not self-declared" in current
    assert "Release authority:" in register


def test_v050_visual_baseline_is_preserved_as_history() -> None:
    facts = json.loads(
        (ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8")
    )

    assert facts["visual_experience_baseline_version"] == "0.5.0"
    assert "visual_experience_candidate_version" not in facts
    assert facts["visual_experience_status"] == (
        "production-validated-r6-3-3-baseline"
    )
    assert facts["production_deployment_readback"] == (
        "PASS_V050_EXACT_PUBLIC_BYTES"
    )


def test_unevidenced_human_uat_is_not_promoted_to_pass() -> None:
    facts = json.loads(
        (ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8")
    )

    assert facts["browser_uat_status"] == (
        "automated-browser-validated-human-device-uat-not-recorded"
    )
    assert facts["browser_uat_profile_count"] == 0

    for key in (
        "browser_uat_accessibility",
        "browser_uat_narrow_320",
        "browser_uat_performance",
        "browser_uat_primary",
        "browser_uat_reduced_motion",
        "browser_uat_security",
        "browser_uat_zoom_200_reflow",
    ):
        assert facts[key] == "OPEN"
