from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v072_corrective_maintenance_truth_is_bounded() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    correction = facts["corrective_maintenance_v072"]
    assert correction["mobile_detail_dialog"] == "NATIVE_MODAL"
    assert correction["accessible_name_lifecycle"] == "STATIC_ARIA_LABEL_THEN_VALID_ARIA_LABELLEDBY"
    assert correction["rare_earth_convention"] == "CONTROLLED_USGS_15_COUNT_SCANDIUM_SEPARATELY_LISTED"
    assert correction["touch_target_disposition"].startswith("ACCEPTED_NO_CHANGE")
    assert correction["anti_framing_disposition"] == (
        "VERIFIED_HOSTING_LAYER_LIMITATION_EXTERNAL_GOVERNANCE_DECISION_REQUIRED"
    )
    assert facts["current_public_maturity"] == "M0"
    assert facts["human_decision_authority_required"] is True


def test_v072_dialog_starts_named_and_opens_modally() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    js = (ROOT / "web/app.js").read_text(encoding="utf-8")
    dialog = html.split('<dialog id="materialSheet"', 1)[1].split(">", 1)[0]
    assert 'aria-label="Material detail"' in dialog
    assert "aria-labelledby" not in dialog
    assert 'sheet.setAttribute("aria-labelledby", title.id)' in js
    assert "function showModalSheet()" in js
    assert "sheet.showModal()" in js
    assert "sheet.show()" not in js
    assert 'sheet.addEventListener("close"' in js
    assert "returnFocus.focus({preventScroll:true})" in js
    assert "if (sheet.open && sheet.contains(link)) sheet.close();" in js


def test_v072_rare_earth_convention_is_explicit_and_exact() -> None:
    atlas = json.loads((ROOT / "public-snapshots/materials-field/MF-001/atlas.json").read_text(encoding="utf-8"))
    rare_earths = {item["name"] for item in atlas["materials"] if item.get("rare_earth") is True}
    assert rare_earths == {
        "Cerium", "Dysprosium", "Erbium", "Europium", "Gadolinium",
        "Holmium", "Lanthanum", "Lutetium", "Neodymium", "Praseodymium",
        "Samarium", "Terbium", "Thulium", "Ytterbium", "Yttrium",
    }
    scandium = next(item for item in atlas["materials"] if item["name"] == "Scandium")
    assert scandium["rare_earth"] is False
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert "Rare-earth convention." in html
    assert "scandium remains separately listed" in html


def test_v072_does_not_claim_ineffective_meta_frame_ancestors() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8").lower()
    assert "frame-ancestors" not in html
    observation = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))[
        "corrective_maintenance_v072"
    ]["anti_framing_observation"]
    assert observation["content_security_policy_header"] == "ABSENT"
    assert observation["x_frame_options_header"] == "ABSENT"
    assert observation["meta_csp_frame_ancestors_effective"] is False


def test_v072_preserves_exactly_two_selected_pathways_and_frozen_records() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "web/selected-pathways.json").read_text(encoding="utf-8"))
    assert len(registry["pathways"]) == facts["selected_pathways_public_example_count"] == 2
    assert {item["record_id"] for item in registry["pathways"]} == {"GA-001", "YIG-001"}
    notes = (ROOT / "RELEASE_NOTES_v0.7.2.md").read_text(encoding="utf-8")
    assert "Frozen GA-001 v1.0.0, MF-001, and YIG-001 evidence is unchanged" in notes
