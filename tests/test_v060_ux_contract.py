from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_v060_field_focus_proof_contract(tmp_path: Path) -> None:
    out=tmp_path/'web'; subprocess.run([sys.executable,str(ROOT/'scripts'/'build_web.py'),'--output',str(out)],cwd=ROOT,check=True)
    html=(out/'index.html').read_text(encoding='utf-8'); js=(out/'app.js').read_text(encoding='utf-8')
    assert '<h1 id="atlas-title">Materials-to-Mission Atlas</h1>' in html
    assert '<title>Materials-to-Mission Atlas | Bridge Node 7</title>' in html
    assert 'aria-label="Filter by application"' in html
    assert '>Map</button>' in html and '>List</button>' in html
    assert 'class="map-toolbar js-only"' in html
    assert html.count('class="mineral')==60
    assert 'let selectedId = null;' in js and 'aria-activedescendant' in js
    assert 'GA-001 snapshot validation profile' in html
    assert html.count('class="ga-claim"')==7
    assert html.count('class="ga-source-card"')==4
    assert 'Materials Field Sources' in html and 'GA-001 Reviewed Sources' in html
    assert 'Position shows application connection, not ranking.' in html
    assert 'Claim scope:' not in html
    assert 'Supports: GA-' in html
    assert '#ga-source-' in js and 'popstate' in js
    assert 'id="showNextProof"' in html and 'What would change this?' in html
    assert 'trace-next' in js and 'showNextProof' in js

def test_v060_ga001_provenance_and_distinct_source_identity() -> None:
    ga=json.loads((ROOT/'public-snapshots/gallium/GA-001/source-register.json').read_text(encoding='utf-8'))
    field_path=ROOT/'public-snapshots/materials-field/MF-001/source-register.json'
    if not field_path.exists(): field_path=ROOT/'public-snapshots/materials-field/source-register.json'
    field=json.loads(field_path.read_text(encoding='utf-8'))
    ga_by={s['source_id']:s for s in ga['sources']}; field_by={s['source_id']:s for s in field['sources']}
    assert ga_by['USGS-CRITICAL-2025']['source_date']=='2025-11-14'
    assert field_by['USGS-CM-2025']['source_date']=='2025-11-06'
    assert 'USGS-CRITICAL-2025' != 'USGS-CM-2025'

def test_v060_evidence_invariants() -> None:
    snap=json.loads((ROOT/'public-snapshots/gallium/GA-001/snapshot.json').read_text(encoding='utf-8'))
    view=json.loads((ROOT/'public-snapshots/gallium/GA-001/public-view.json').read_text(encoding='utf-8'))
    assert snap['snapshot_id']=='GA-001' and snap['snapshot_version']=='1.0.0'
    assert len(snap['claims'])==7 and all(c['support_state']=='supported' for c in snap['claims'])
    assert snap['human_authority_required'] is True and view['validation_profile']=='m0-strict-0.2.0'
    first=next(n for n in view['trace_nodes'] if n['state']=='unknown')
    assert first['label']=='Qualified domestic primary recovery at mission-relevant scale'

def test_v060_release_and_browser_dependency_contract() -> None:
    browser_lock=(ROOT/'requirements-browser.lock').read_text(encoding='utf-8')
    browser_workflow=(ROOT/'.github/workflows/browser-uat.yml').read_text(encoding='utf-8')
    release_workflow=(ROOT/'.github/workflows/release.yml').read_text(encoding='utf-8')
    assert '-r requirements-dev.lock' in browser_lock
    assert 'playwright==1.55.0' in browser_lock
    assert 'pip install -r requirements-browser.lock' in browser_workflow
    assert 'pip install playwright' not in browser_workflow
    assert 'FIELD → FOCUS → PROOF' in release_workflow


def test_v060_mobile_deep_links_restore_visible_detail() -> None:
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    assert 'if (hash.startsWith("#material-")) { const id=hash.slice(10); if (byId[id]) { selectMaterial(id,{pushHash:false,openSheet:true}); return; } }' in js
    assert 'if (hash.startsWith("#form-")) { const id=hash.slice(6); if (formById[id]) { selectForm(id,{pushHash:false,openSheet:true}); return; } }' in js
    assert 'if (hash === "#gallium") { selectMaterial("gallium",{pushHash:false,openSheet:true}); return; }' in js

def test_v060_focus_uat_uses_keyboard_not_programmatic_focus() -> None:
    uat=(ROOT/"scripts/browser_uat_v060.py").read_text(encoding="utf-8")
    assert "def tab_to_selector(page,selector,steps=160):" in uat
    assert "tab_to_selector(page,'.mineral')" in uat
    assert "style['focusVisible']" in uat
    assert "page.locator('.mineral').first.focus()" not in uat
    assert 'page.locator(\'.mineral[data-id="gallium"]\').focus()' not in uat

def test_v060_search_input_has_visible_keyboard_focus() -> None:
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert ":focus-visible{outline:3px solid var(--gold2);outline-offset:3px}" in css
    assert ".searchbox input{width:100%;border:0;outline:0;" in css
    assert ".searchbox input:focus-visible{outline:3px solid var(--gold2);outline-offset:3px}" in css

def test_v060_selected_material_has_noncolor_geometry() -> None:
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert "a.mineral.selected{border-width:2px;transform:translate(-50%,-50%) scale(1.18)}" in css
    assert ".mineral.selected span{font:14px Georgia,serif;font-weight:700}" in css
    uat=(ROOT/"scripts/browser_uat_v060.py").read_text(encoding="utf-8")
    assert "grayscale-noncolor-state" in uat
    assert "aria-current" in uat
    assert "borderWidth" in uat and "transform" in uat and "fontSize" in uat

def test_v060_mineral_node_element_matches_structural_selector() -> None:
    build=(ROOT/"scripts/build_web.py").read_text(encoding="utf-8")
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert "f'<a class=\"mineral" in build
    assert "a.mineral.selected{border-width:2px;transform:translate(-50%,-50%) scale(1.18)}" in css
    assert "button.mineral.selected{" not in css

def test_v060_grayscale_uat_eliminates_transition_race() -> None:
    uat=(ROOT/"scripts/browser_uat_v060.py").read_text(encoding="utf-8")
    assert "# Grayscale / non-color selected state\n        context=browser.new_context(viewport={'width':1280,'height':720},reduced_motion='reduce');" in uat
    assert "DOMMatrixReadOnly(getComputedStyle(ga).transform)" in uat
    assert "Math.abs(a.a-b.a)>.15" in uat
    assert "timeout=3000" in uat
