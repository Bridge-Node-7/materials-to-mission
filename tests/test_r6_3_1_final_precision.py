from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_selected_mineral_hitbox_does_not_expand() -> None:
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    selected=css.split(".mineral.selected{",1)[1].split("}",1)[0]
    assert "width:" not in selected
    assert "height:" not in selected
    assert ".mineral.selected:before" in css
    assert "pointer-events:none" in css.split(".mineral.selected:before",1)[1].split("}",1)[0]

def test_index_cta_uses_real_view_transition() -> None:
    html=(ROOT/"web/index.html").read_text(encoding="utf-8")
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    assert 'id="openIndexCta"' in html
    assert 'function setAtlasView(mode' in js
    assert 'openIndexCta.addEventListener("click"' in js
    assert 'setAtlasView("index", {focus:true, scroll:true})' in js

def test_no_js_enhancement_controls_are_authoritatively_hidden() -> None:
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert "html:not(.js-ready) .js-only{display:none!important}" in css
    assert ".js-ready .view-row.js-only{display:flex}" in css

def test_search_uses_material_system_ontology() -> None:
    html=(ROOT/"web/index.html").read_text(encoding="utf-8")
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    assert "Search minerals or material systems" in html
    assert "Engineered Material System" in js
    assert "Engineered Substrate" in js
    assert "Public engineered form" not in js

def test_yig_public_wording_is_precise() -> None:
    builder=(ROOT/"scripts/build_web.py").read_text(encoding="utf-8")
    assert "Critical-Mineral Dependencies Across Common YIG Stacks" in builder
    assert "Yttrium is the YIG critical-mineral constituent" in builder
    assert "Y₃Fe₅O₁₂" in builder

def test_meaningful_copy_and_source_targets_have_release_floor() -> None:
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert ".yig-stage p," in css
    assert "font-size:12px" in css
    assert "min-height:30px" in css
