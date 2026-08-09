from __future__ import annotations

import copy
import json

from materials_to_mission.validator import validate_case


def codes(result):
    return {item.code for item in result.findings}


def test_valid_public_example(example_case):
    result = validate_case(example_case, public=True)
    assert result.valid, result.findings


def test_missing_human_owner_fails(root):
    case = json.loads((root / "examples/invalid/missing-human-owner.json").read_text())
    result = validate_case(case, public=True)
    assert not result.valid
    assert "SCHEMA" in codes(result)


def test_triggered_critical_condition_blocks_advance(root):
    case = json.loads((root / "examples/invalid/triggered-critical-advance.json").read_text())
    result = validate_case(case, public=True)
    assert not result.valid
    assert "CRITICAL_CONDITION" in codes(result)


def test_unknown_evidence_must_be_visible(root):
    case = json.loads((root / "examples/invalid/hidden-unknown.json").read_text())
    result = validate_case(case, public=True)
    assert not result.valid
    assert "VISIBLE_UNCERTAINTY" in codes(result)


def test_public_boundary_rejects_protected_token(root):
    case = json.loads((root / "examples/invalid/protected-public-token.json").read_text())
    result = validate_case(case, public=True)
    assert not result.valid
    assert "PUBLIC_BOUNDARY" in codes(result)


def test_schema_missing_required_fails(root):
    case = json.loads((root / "examples/invalid/schema-missing-required.json").read_text())
    result = validate_case(case, public=True)
    assert not result.valid
    assert "SCHEMA" in codes(result)


def test_owner_mismatch_fails(example_case):
    case = copy.deepcopy(example_case)
    case["decision_passport"]["decision_owner"] = "Different Human"
    result = validate_case(case, public=True)
    assert "AUTHORITY_MISMATCH" in codes(result)


def test_provenance_must_match_evidence_ids(example_case):
    case = copy.deepcopy(example_case)
    case["provenance"]["source_record_ids"].pop()
    result = validate_case(case, public=True)
    assert "PROVENANCE" in codes(result)


def test_exactly_one_governing_weak_link(example_case):
    case = copy.deepcopy(example_case)
    case["material_assurance_record"]["weak_links"].append({"weak_link_id": "WL-002", "statement": "Second", "governing": True})
    result = validate_case(case, public=True)
    assert "WEAK_LINK" in codes(result)
