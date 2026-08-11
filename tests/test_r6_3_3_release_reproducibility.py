from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
FIELD=ROOT/"public-snapshots/materials-field/MF-001"
YIG=ROOT/"public-snapshots/material-systems/YIG-001"

def test_live_region_announcement_is_synchronous() -> None:
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    block=js.split("function announce(message)",1)[1].split("}",1)[0]
    assert "requestAnimationFrame" not in block
    assert "experienceStatus.textContent = message" in block

def test_unknown_yig_stages_separate_absence_basis_from_context_sources() -> None:
    data=json.loads((YIG/"pathway.json").read_text(encoding="utf-8"))
    unknown=[stage for stage in data["stages"] if stage["state"]=="unknown"]
    assert unknown
    for stage in unknown:
        assert stage.get("source_ids",[]) == []
        assert stage.get("evidence_basis")
    qualified=next(s for s in unknown if s["id"]=="yig-qualified-stack")
    assert qualified["context_source_ids"] == ["USGS-Y-2026"]

def test_room_temperature_magnon_josephson_context_is_bounded() -> None:
    data=json.loads((YIG/"pathway.json").read_text(encoding="utf-8"))
    register=json.loads((FIELD/"source-register.json").read_text(encoding="utf-8"))
    ids={s["source_id"] for s in register["sources"]}
    assert "APS-YIG-MAGNON-JOSEPHSON-2021" in ids
    ctx=data["frontier_research_context"][0]
    assert "Josephson oscillations" in ctx["summary"]
    assert "not validation of any specific proposed device architecture" in ctx["summary"]
    assert ctx["source_ids"] == ["APS-YIG-MAGNON-JOSEPHSON-2021"]

def test_yig_unknown_semantics_are_fail_closed_in_builder() -> None:
    builder=(ROOT/"scripts/build_web.py").read_text(encoding="utf-8")
    assert "unknown YIG stage must not cite a source as proof of absence" in builder
    assert "unknown YIG stage requires explicit reviewed-corpus evidence basis" in builder
