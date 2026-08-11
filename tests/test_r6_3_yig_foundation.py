from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "public-snapshots/materials-field/MF-001"
YIG = ROOT / "public-snapshots/material-systems/YIG-001"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_yig_and_ggg_are_public_engineered_systems_not_official_minerals() -> None:
    atlas = load(FIELD / "atlas.json")
    forms = load(FIELD / "public-forms.json")["forms"]
    mineral_names = {m["name"] for m in atlas["materials"]}
    form_by = {f["id"]: f for f in forms}
    assert "Yttrium Iron Garnet" not in mineral_names
    assert "Gadolinium Gallium Garnet" not in mineral_names
    assert form_by["yig"]["kind"] == "engineered-material-system"
    assert form_by["yig"]["formula"] == "Y3Fe5O12"
    assert form_by["yig"]["primary_example"] is True
    assert {r["mineral"] for r in form_by["ggg"]["relationships"]} == {"Gadolinium","Gallium"}

def test_yig_pathway_is_bounded_and_has_horizon() -> None:
    pathway = load(YIG / "pathway.json")
    assert pathway["official_critical_mineral"] is False
    assert pathway["human_authority_required"] is True
    ids = {s["id"] for s in pathway["stages"]}
    assert pathway["evidence_horizon"]["first_unresolved_stage_id"] in ids
    assert any("room-temperature" in s["summary"].lower() for s in pathway["stages"])
    assert "scalable room-temperature quantum computing" in pathway["no_claims"]

def test_yig_sources_are_public_primary_sources() -> None:
    register = load(FIELD / "source-register.json")
    by = {s["source_id"]:s for s in register["sources"]}
    for sid in (
        "USGS-Y-2026","APS-YIG-LPE-2020","APS-YIG-RT-HYBRID-2024",
        "NATURE-YIG-GGG-DEVICE-2025","NATURE-YIG-SUBSTRATE-2026"
    ):
        assert sid in by
        assert by[sid]["url"].startswith("https://")
    assert by["USGS-Y-2026"]["authority_class"] == "official-government-primary"
    assert by["APS-YIG-RT-HYBRID-2024"]["authority_class"] == "peer-reviewed-primary"

def test_r63_interaction_contracts_are_in_source() -> None:
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    assert "enableConstellationKeyboard()" in js
    assert 'node.tabIndex = on ? 0 : -1' in js
    assert "directionalNeighbor" in js
    assert 'if (!hash.startsWith("#material-") && !hash.startsWith("#form-") && sheet.open)' in js
    assert 'href="#yig-pathway"' in js
    assert 'related-parent' in js
    assert 'form-mode' in js
