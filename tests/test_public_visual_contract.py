from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_public_view_contract_is_derived_and_human_authority() -> None:
    schema = load_json("view-contracts/public-view.schema.json")
    assert schema["$id"] == "urn:bn7:m2m:view-contract:public-view:0.3.0"
    assert schema["properties"]["view_contract_version"]["const"] == "0.3.0"
    assert schema["properties"]["decision_authority"]["const"] == "human"
    assert "public-source-snapshot" in schema["properties"]["source_kind"]["enum"]


def test_visual_tokens_include_accessibility_and_reduced_motion() -> None:
    tokens = load_json("docs/V0_3_DESIGN_TOKENS.json")
    assert tokens["version"] == "0.3.0"
    assert tokens["accessibility"]["keyboard"] is True
    assert tokens["accessibility"]["color_only_meaning"] is False
    assert tokens["accessibility"]["reduced_motion"] is True
    assert tokens["motion_ms"]["reduced_max"] <= 80


def test_project_facts_keep_m0_and_canonical_schema_authority() -> None:
    facts = load_json("PROJECT_FACTS.json")
    assert facts["version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert facts["current_public_maturity"] == "M0"
    assert facts["schema_authority"].endswith("/v0.1.0/schemas/")
    assert facts["public_view_semantic_authority"] is False
    assert facts["browser_writeback_authorized"] is False
    assert facts["gallium_public_snapshot_status"] == "frozen-ga-001-v1.0.0"
    assert facts["m1_real_workflow_proof_claimed"] is False


def test_evidence_model_preserves_key_distinctions() -> None:
    model = (ROOT / "docs/EVIDENCE_MODEL.md").read_text(encoding="utf-8")
    assert "`UNKNOWN` and `CONTRADICTED` remain distinct evidence states." in model
    assert "Claim support is not pathway assessment." in model
    assert "Evidence-supported action is not human decision." in model
    assert "No composite readiness score" in model
