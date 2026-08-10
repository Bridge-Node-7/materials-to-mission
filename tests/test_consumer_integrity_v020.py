from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import tomllib

import pytest

from materials_to_mission import __version__
from materials_to_mission.boundary import scan_public_boundary
from materials_to_mission.cli import main
from materials_to_mission.validation_evidence import render_validation_report
from materials_to_mission.validation_profiles import (
    BASELINE_PROFILE_ID,
    DEFAULT_VALIDATION_PROFILE,
    STRICT_PROFILE_ID,
    get_validation_profile,
)
from materials_to_mission.validator import validate_case


def finding_codes(result) -> set[str]:
    return {item.code for item in result.findings}


def historical_case(root: Path) -> dict:
    return json.loads((root / "tests/fixtures/historical/v0.1.0-reference-case.json").read_text(encoding="utf-8"))


def test_profile_identifiers_are_frozen() -> None:
    assert BASELINE_PROFILE_ID == "m0-baseline-0.1.0"
    assert STRICT_PROFILE_ID == "m0-strict-0.2.0"
    assert DEFAULT_VALIDATION_PROFILE == STRICT_PROFILE_ID
    assert get_validation_profile(BASELINE_PROFILE_ID).schema_authority == "v0.1.0"
    assert get_validation_profile(STRICT_PROFILE_ID).schema_authority == "v0.1.0"
    with pytest.raises(ValueError, match="unknown validation profile"):
        get_validation_profile("not-a-profile")


def test_v010_reference_validates_under_historical_profile(root: Path) -> None:
    result = validate_case(historical_case(root), public=True, profile=BASELINE_PROFILE_ID)
    assert result.valid, result.findings
    assert result.validation_profile == BASELINE_PROFILE_ID


def test_v010_reference_has_explicit_strict_profile_result(root: Path) -> None:
    result = validate_case(historical_case(root), public=True, profile=STRICT_PROFILE_ID)
    assert not result.valid
    assert "VISIBLE_UNCERTAINTY" in finding_codes(result)


def test_current_reference_validates_under_strict_profile(example_case: dict) -> None:
    result = validate_case(example_case, public=True, profile=STRICT_PROFILE_ID)
    assert result.valid, result.findings


def test_historical_boundary_behavior_is_not_silently_hardened(root: Path) -> None:
    case = historical_case(root)
    case["title"] += " CUI"
    baseline = validate_case(case, public=True, profile=BASELINE_PROFILE_ID)
    strict = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
    assert "PUBLIC_BOUNDARY" not in finding_codes(baseline)
    assert "PUBLIC_BOUNDARY" in finding_codes(strict)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("automation", "HUMAN_AUTHORITY"),
        ("critical", "CRITICAL_CONDITION"),
        ("weak_link", "WEAK_LINK"),
        ("owner_mismatch", "AUTHORITY_MISMATCH"),
        ("disposition", "DISPOSITION_MISMATCH"),
        ("provenance", "PROVENANCE"),
        ("public_label", "PUBLIC_BOUNDARY"),
    ],
)
def test_baseline_profile_preserves_original_semantic_rules(example_case: dict, mutation: str, expected: str) -> None:
    case = copy.deepcopy(example_case)
    if mutation == "automation":
        case["decision_charter"]["decision_owner"] = "AI"
        case["decision_passport"]["decision_owner"] = "AI"
    elif mutation == "critical":
        case["material_assurance_record"]["proposed_disposition"] = "ADVANCE"
        case["decision_passport"]["disposition"] = "ADVANCE"
    elif mutation == "weak_link":
        case["material_assurance_record"]["weak_links"][0]["governing"] = False
    elif mutation == "owner_mismatch":
        case["decision_passport"]["decision_owner"] = "Different Human"
    elif mutation == "disposition":
        case["decision_passport"]["disposition"] = "STOP"
    elif mutation == "provenance":
        case["provenance"]["source_record_ids"].pop()
    elif mutation == "public_label":
        case["material_assurance_record"]["supplier"]["label"] = "Actual Supplier"
    result = validate_case(case, public=True, profile=BASELINE_PROFILE_ID)
    assert expected in finding_codes(result)


def test_named_human_automation_phrase_is_visible_as_ambiguity(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    label = "AI Manager Jane Smith"
    case["decision_charter"]["decision_owner"] = label
    case["decision_passport"]["decision_owner"] = label
    result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
    ambiguity = [item for item in result.findings if item.code == "AUTHORITY_AMBIGUITY"]
    assert result.valid
    assert ambiguity
    assert all(item.severity == "WARNING" for item in ambiguity)
    assert "HUMAN_AUTHORITY" not in finding_codes(result)


@pytest.mark.parametrize("alias", ["Α.Ι.", "А.І."])
def test_cross_script_ai_confusables_are_rejected(example_case: dict, alias: str) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["decision_owner"] = alias
    case["decision_passport"]["decision_owner"] = alias
    result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
    assert "HUMAN_AUTHORITY" in finding_codes(result)


def test_synthetic_state_is_coherent_in_reverse_direction(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    case["synthetic"] = False
    case["public_safe"] = False
    result = validate_case(case, public=False, profile=STRICT_PROFILE_ID)
    assert "SYNTHETIC_STATE" in finding_codes(result)


@pytest.mark.parametrize("value", ["ITAR", "CUI", "export-controlled technical data", "clаssified"])
def test_high_value_boundary_signals_are_detected(value: str) -> None:
    assert scan_public_boundary({"note": value})


@pytest.mark.parametrize(
    ("name", "expected_code"),
    [
        ("missing-human-owner.json", "SCHEMA"),
        ("hidden-unknown.json", "VISIBLE_UNCERTAINTY"),
        ("protected-public-token.json", "PUBLIC_BOUNDARY"),
        ("schema-missing-required.json", "SCHEMA"),
        ("triggered-critical-advance.json", "CRITICAL_CONDITION"),
    ],
)
def test_teaching_fixtures_are_surgical(root: Path, name: str, expected_code: str) -> None:
    case = json.loads((root / "examples/invalid" / name).read_text(encoding="utf-8"))
    result = validate_case(case, public=True, profile=STRICT_PROFILE_ID)
    assert not result.valid
    assert finding_codes(result) == {expected_code}
    assert len(result.findings) == 1


def test_cli_json_exposes_profile_and_toolkit_identity(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main([
        "validate",
        str(root / "examples/synthetic-critical-material-pathway/case.json"),
        "--public",
        "--json",
        "--profile",
        STRICT_PROFILE_ID,
    ])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["valid"] is True
    assert payload["validation_profile"] == STRICT_PROFILE_ID
    assert payload["toolkit_version"] == __version__
    assert payload["schema_version"] == "0.1.0"


def test_cli_usage_errors_are_input_errors() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["not-a-command"])
    assert exc.value.code == 3


def test_guided_evaluator_has_truthful_install_preflight(root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    path = root / "scripts/evaluate_public_method.py"
    spec = importlib.util.spec_from_file_location("m2m_guided_evaluator_v020", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "toolkit_available", lambda: False)
    code = module.main()
    output = capsys.readouterr().out
    assert code == 1
    assert "toolkit is not installed" in output
    assert "synthetic reference did not validate" not in output


def test_consumer_lock_contains_exact_build_backend(root: Path) -> None:
    runtime = (root / "requirements.lock").read_text(encoding="utf-8")
    dev = (root / "requirements-dev.lock").read_text(encoding="utf-8")
    assert "setuptools==82.0.1" in runtime
    assert dev.count("setuptools==82.0.1") == 0
    assert "-r requirements.lock" in dev


def test_hosted_ci_contains_documented_consumer_journey(root: Path) -> None:
    workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert 'python-version: "3.12"' in workflow
    assert "python -m venv .consumer-venv" in workflow
    assert "python -m pip install -r requirements.lock" in workflow
    assert "--no-build-isolation -e ." in workflow
    assert "python scripts/evaluate_public_method.py" in workflow


def test_version_identity_is_singular(root: Path) -> None:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    facts = json.loads((root / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    citation_version = re.search(r"(?m)^version:\s*([^\s]+)\s*$", citation)
    assert version == "0.3.0"
    assert __version__ == version
    assert pyproject["project"]["version"] == version
    assert facts["version"] == version
    assert citation_version
    assert citation_version.group(1) == version


def test_validation_report_exposes_profile() -> None:
    report = render_validation_report(1, "0.2.0", STRICT_PROFILE_ID)
    assert f"**Validation profile:** {STRICT_PROFILE_ID}" in report
