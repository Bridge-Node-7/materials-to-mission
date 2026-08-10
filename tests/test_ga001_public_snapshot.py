from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public-snapshots" / "gallium" / "GA-001"


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_ga001_identity_and_scope() -> None:
    snapshot = load("snapshot.json")
    assert snapshot["snapshot_id"] == "GA-001"
    assert snapshot["snapshot_version"] == "1.0.0"
    assert snapshot["snapshot_kind"] == "public-source-evidence-snapshot"
    assert snapshot["material"] == {"name": "Gallium", "symbol": "Ga", "atomic_number": 31}
    assert snapshot["public_maturity"] == "M0"
    assert snapshot["real_case_001"] is False
    assert snapshot["human_authority_required"] is True


def test_ga001_sources_are_official_and_bounded() -> None:
    register = load("source-register.json")
    allowed = {"www.usgs.gov", "www.energy.gov"}
    ids = set()
    for source in register["sources"]:
        host = urlparse(source["url"]).hostname
        assert host in allowed
        assert source["authority"] == "official-government"
        ids.add(source["source_id"])
    assert ids == {
        "USGS-GA-STATS",
        "USGS-CRITICAL-2025",
        "DOE-TRACE-GA-2026",
        "DOE-TRACE-GA-2025",
    }


def test_ga001_rights_are_metadata_and_paraphrase_only() -> None:
    rights = load("rights.json")
    assert rights["rights_posture"] == "metadata-and-original-paraphrase-only"
    assert rights["source_files_redistributed"] is False
    assert rights["source_images_redistributed"] is False
    assert rights["long_source_quotes_redistributed"] is False
    assert rights["blanket_public_domain_assertion"] is False
    assert rights["approved_for_public_repository"] is True


def test_ga001_view_validates_against_derived_public_view_contract() -> None:
    schema = json.loads(
        (ROOT / "view-contracts" / "public-view.schema.json").read_text(encoding="utf-8")
    )
    view = load("public-view.json")
    Draft202012Validator(schema).validate(view)
    assert view["decision_authority"] == "human"
    assert view["source_kind"] == "public-source-snapshot"
    states = {node["kind"]: node["state"] for node in view["trace_nodes"]}
    assert states["qualification"] == "unknown"
    assert states["acquisition-access"] == "unknown"
    assert states["mission"] == "unknown"


def test_ga001_preserves_public_boundary() -> None:
    snapshot = load("snapshot.json")
    claims = " ".join(item["claim"] for item in snapshot["claims"]).lower()
    assert "qualified domestic production capacity" not in claims
    assert "mission-ready" not in claims
    assert snapshot["not_in_scope"]
