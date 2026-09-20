from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_v061_current_browser_validation_scope_is_explicit():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    assert facts['version']==(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    assert facts['browser_uat_configured_profile_count']==14
    assert facts['browser_uat_current_source_expected_result_profile_count']==14
    assert facts['browser_uat_profile_count']==14
    assert facts['human_real_device_uat_attestation']=='NOT_ATTESTED'
    assert facts['human_assistive_technology_uat_attestation']=='NOT_ATTESTED'
    assert facts['browser_uat_contract']=='version-neutral-14-profile-automated-contract-including-seven-42-contract-viewports'

def test_v061_production_truth_uses_external_release_authority():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    assert facts['production_deployment_https_enforced'] is True
    assert facts['production_deployment_url']=='https://bridgenode7.com/materials-to-mission/'
    assert 'GitHub' in facts['publication_authority']

def test_v061_current_state_is_product_facing():
    state=(ROOT/'docs/CURRENT_STATE.md').read_text(encoding='utf-8')
    assert 'Live experience: https://bridgenode7.com/materials-to-mission/' in state
    assert 'historical' not in state.lower()
    assert 'corporate website release' not in state.lower()

def test_v061_programmatic_scroll_honors_reduced_motion():
    source=(ROOT/'web/app.js').read_text(encoding='utf-8')
    assert 'matchMedia("(prefers-reduced-motion: reduce)")' in source
    assert source.count('behavior:preferredScrollBehavior()')==2
    assert 'behavior:"smooth"' not in source

def test_v061_material_system_controls_have_unique_accessible_names():
    source=(ROOT/'scripts/build_web.py').read_text(encoding='utf-8')
    assert 'aria-label="Open detail: {esc(form["name"])}"' in source
    browser=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    assert 'assert_material_system_accessible_names' in browser
    assert 'buttons.count()==10' in browser
    assert 'len(set(labels))==10' in browser

def test_v061_browser_contract_adds_behavioral_reduced_motion_profile():
    source=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    assert "'reduced-motion-programmatic-scroll'" in source
    assert 'expected_profiles=len(VIEWPORTS)+7' in source
    assert '__m2mScrollBehaviors' in source
    assert 'context.add_init_script("() => {' not in source
    assert 'context.add_init_script("window.__m2mScrollBehaviors = [];' in source
    assert 'page.wait_for_function("Array.isArray(window.__m2mScrollBehaviors)")' in source
    assert "set(behaviors)=={'auto'}" in source

def test_v061_public_identity_and_boundaries_remain_bounded():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    notes=(ROOT/facts['release_notes']).read_text(encoding='utf-8')
    state=(ROOT/'docs/CURRENT_STATE.md').read_text(encoding='utf-8')
    assert 'Explore the 60-mineral Materials-to-Mission Atlas' in readme
    assert 'Explore the 60-mineral Strategic Constellation' not in readme
    assert '`VERSION` identifies source line `0.7.6`' in state
    for token in ('Frozen GA-001 v1.0.0','YIG remains an engineered material system','M0','Human consequential authority'):
        assert token.lower() in notes.lower()
