from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from materials_to_mission.boundary import scan_public_boundary
from materials_to_mission.cli import main
from materials_to_mission.validator import validate_case


def codes(case: dict) -> set[str]:
    return {item.code for item in validate_case(case, public=True).findings}


@pytest.mark.parametrize(
    "alias",
    [
        "AI System",
        "Automated Decision Engine",
        "Algorithmic Agent",
        "Model Operator",
    ],
)
def test_automation_aliases_cannot_own_decisions(
    example_case: dict,
    alias: str,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["decision_owner"] = alias
    case["decision_passport"]["decision_owner"] = alias
    assert "HUMAN_AUTHORITY" in codes(case)


def test_human_authority_remains_valid(example_case: dict) -> None:
    assert "HUMAN_AUTHORITY" not in codes(copy.deepcopy(example_case))


def test_disposition_must_be_allowed_by_charter(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["allowed_dispositions"] = ["HOLD", "STOP"]
    case["material_assurance_record"]["proposed_disposition"] = "VALIDATE"
    case["decision_passport"]["disposition"] = "VALIDATE"
    assert "DISPOSITION_NOT_ALLOWED" in codes(case)


def test_uncertainty_requires_exact_evidence_identifier(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["evidence_posture"]["unknown"] = [
        "Narrative reassurance that mentions E-004 without an exact identity link."
    ]
    assert "VISIBLE_UNCERTAINTY" in codes(case)


def test_similar_evidence_identifier_does_not_match(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["evidence_posture"]["unknown"] = [
        "E-004-EXTRA: a different identifier"
    ]
    assert "VISIBLE_UNCERTAINTY" in codes(case)


def test_partially_supported_evidence_must_remain_visible(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["evidence_posture"]["unknown"] = [
        value
        for value in case["decision_passport"]["evidence_posture"]["unknown"]
        if not value.startswith("E-002")
    ]
    assert "VISIBLE_UNCERTAINTY" in codes(case)


def test_requirement_links_must_resolve(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    case["material_assurance_record"]["evidence_records"][0][
        "requirement_links"
    ] = ["REQ-NOT-DEFINED"]
    assert "REQUIREMENT_LINK" in codes(case)


def test_evidence_date_order_is_enforced(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    evidence = case["material_assurance_record"]["evidence_records"][0]
    evidence["date_issued"] = "2026-08-09"
    evidence["date_accessed"] = "2026-08-08"
    assert "EVIDENCE_DATE_ORDER" in codes(case)


def test_evidence_cannot_occupy_incompatible_posture_buckets(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["evidence_posture"]["contradicted"].append(
        "E-004: duplicate incompatible posture"
    )
    assert "POSTURE_CONFLICT" in codes(case)


def empty_policy(tmp_path: Path) -> Path:
    path = tmp_path / "policy.json"
    path.write_text(
        json.dumps(
            {
                "prohibited_case_insensitive_tokens": [],
                "prohibited_regexes": [],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_secret_like_json_key_is_detected(tmp_path: Path) -> None:
    findings = scan_public_boundary(
        {"nested": {"api_key": "synthetic-placeholder"}},
        empty_policy(tmp_path),
    )
    assert any("prohibited public key" in item for item in findings)


def test_benign_key_is_not_misclassified(tmp_path: Path) -> None:
    assert (
        scan_public_boundary(
            {"api_version": "1", "tokenization": "none"},
            empty_policy(tmp_path),
        )
        == []
    )


def test_deep_json_returns_controlled_cli_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "deep.json"
    path.write_text('{"x":' * 1400 + "0" + "}" * 1400, encoding="utf-8")
    result = main(["validate", str(path), "--json"])
    captured = capsys.readouterr()
    assert result == 3
    assert "STOP -" in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_triggered_condition_requires_exact_passport_identity(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["critical_conditions"] = [
        "The origin condition remains important."
    ]
    assert "CRITICAL_CONDITION_VISIBILITY" in codes(case)


def test_passport_decision_id_must_equal_case_id(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    case["decision_passport"]["decision_id"] = "M2M-UNRELATED-DECISION"
    assert "DECISION_IDENTITY" in codes(case)


def test_referencing_is_a_direct_runtime_dependency(root: Path) -> None:
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    dependencies = pyproject.split("dependencies = [", 1)[1].split("]", 1)[0]
    assert '"referencing>=0.37,<1"' in dependencies


def test_templates_are_distinct_neutral_authoring_records(root: Path) -> None:
    template = json.loads(
        (root / "templates/case.template.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (
            root
            / "examples/synthetic-critical-material-pathway/case.json"
        ).read_text(encoding="utf-8")
    )
    mar_template = json.loads(
        (
            root / "templates/material-assurance-record.template.json"
        ).read_text(encoding="utf-8")
    )

    assert template != example
    assert template["case_id"] == "M2M-TEMPLATE-001"
    assert "Template" in template["title"]
    assert template["material_assurance_record"] == mar_template
    assert validate_case(template, public=True).valid


def test_symlink_policy_allows_only_untracked_ignored_paths(
    root: Path,
) -> None:
    module_path = root / "scripts/check_repo.py"
    spec = importlib.util.spec_from_file_location(
        "m2m_check_repo",
        module_path,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.symlink_is_permitted(tracked=False, ignored=True)
    assert not module.symlink_is_permitted(tracked=True, ignored=True)
    assert not module.symlink_is_permitted(tracked=False, ignored=False)

@pytest.mark.parametrize(
    "alias",
    [
        "ChatGPT",
        "GPT-4",
        "LLM",
        "A.I.",
        "Claude",
        "autonomous agent",
        "our AI",
        "system-selected agent",
    ],
)
def test_gate13_automation_only_authorities_are_rejected(
    example_case: dict,
    alias: str,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["decision_owner"] = alias
    case["decision_passport"]["decision_owner"] = alias
    assert "HUMAN_AUTHORITY" in codes(case)


@pytest.mark.parametrize(
    "label",
    [
        "AI Program Manager Maya Chen",
        "Model Risk Lead Jordan Lee",
        "Automation Assurance Director Priya Shah",
    ],
)
def test_gate13_named_humans_in_automation_roles_are_allowed(
    example_case: dict,
    label: str,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["decision_owner"] = label
    case["decision_passport"]["decision_owner"] = label
    assert "HUMAN_AUTHORITY" not in codes(case)


def test_duplicate_requirement_ids_are_rejected(example_case: dict) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["requirements"].append(
        copy.deepcopy(case["decision_charter"]["requirements"][0])
    )
    assert "DUPLICATE_REQUIREMENT_ID" in codes(case)


def test_duplicate_acceptance_criterion_ids_are_rejected(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["acceptance_criteria"].append(
        copy.deepcopy(case["decision_charter"]["acceptance_criteria"][0])
    )
    assert "DUPLICATE_REQUIREMENT_ID" in codes(case)


def test_requirement_and_acceptance_ids_share_one_namespace(
    example_case: dict,
) -> None:
    case = copy.deepcopy(example_case)
    case["decision_charter"]["acceptance_criteria"][0]["requirement_id"] = (
        case["decision_charter"]["requirements"][0]["requirement_id"]
    )
    assert "DUPLICATE_REQUIREMENT_ID" in codes(case)
