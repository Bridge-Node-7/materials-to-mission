from __future__ import annotations

import copy

from materials_to_mission.validator import validate_case


def codes(result):
    return {item.code for item in result.findings}


def test_automation_cannot_own_decision(example_case):
    case = copy.deepcopy(example_case)
    case["decision_charter"]["decision_owner"] = "AI"
    case["decision_passport"]["decision_owner"] = "AI"
    result = validate_case(case, public=True)
    assert "HUMAN_AUTHORITY" in codes(result)


def test_public_case_must_be_synthetic(example_case):
    case = copy.deepcopy(example_case)
    case["synthetic"] = False
    result = validate_case(case, public=True)
    assert "PUBLIC_BOUNDARY" in codes(result)


def test_disposition_must_match(example_case):
    case = copy.deepcopy(example_case)
    case["decision_passport"]["disposition"] = "STOP"
    result = validate_case(case, public=True)
    assert "DISPOSITION_MISMATCH" in codes(result)


def test_public_labels_must_be_fictional(example_case):
    case = copy.deepcopy(example_case)
    case["material_assurance_record"]["supplier"]["label"] = "Example Supplier"
    result = validate_case(case, public=True)
    assert "PUBLIC_BOUNDARY" in codes(result)


def test_no_governing_weak_link_fails(example_case):
    case = copy.deepcopy(example_case)
    case["material_assurance_record"]["weak_links"][0]["governing"] = False
    result = validate_case(case, public=True)
    assert "WEAK_LINK" in codes(result)


def test_unsupported_evidence_must_be_visible(example_case):
    case = copy.deepcopy(example_case)
    case["material_assurance_record"]["evidence_records"][0]["claim_state"] = "UNSUPPORTED"
    result = validate_case(case, public=True)
    assert "VISIBLE_UNCERTAINTY" in codes(result)
