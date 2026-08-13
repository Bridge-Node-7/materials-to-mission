from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_v061_truth_separates_configured_current_source_from_admitted_runtime():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    assert facts['version']=='0.6.1'
    assert facts['browser_uat_configured_profile_count']==14
    assert facts['browser_uat_current_source_expected_result_profile_count']==14
    assert facts['browser_uat_profile_count']==13
    admitted=facts['latest_source_admitted_automated_browser_attestation']
    assert admitted['release']=='v0.6.0' and admitted['commit']=='65837cc816da7407fe14fb3ec33a1b7d062443a6' and admitted['status']=='PASS' and admitted['result_profile_count']==13
    assert facts['human_real_device_uat_attestation']=='NOT_ATTESTED'
    assert facts['human_assistive_technology_uat_attestation']=='NOT_ATTESTED'
    assert 'required-before-release' not in facts['browser_uat_status']

def test_v061_production_truth_separates_source_and_external_runtime_authority():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    assert facts['production_deployment_readback']=='SOURCE_ADMITTED_V060_EXTERNAL_PASS'
    admitted=facts['latest_source_admitted_production_attestation']
    assert admitted['release']=='v0.6.0' and admitted['commit']=='65837cc816da7407fe14fb3ec33a1b7d062443a6' and admitted['status']=='PASS'
    assert facts['production_source_stored_historical_baseline']['release']=='v0.5.0'
    assert 'rather than CI writeback' in facts['current_source_line_external_attestation_policy']

def test_v061_website_integration_truth_is_current():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    assert facts['website_release']=='v1.2.1'
    assert 'website release `v1.2.1`' in (ROOT/'docs/CURRENT_STATE.md').read_text(encoding='utf-8')

def test_v061_programmatic_scroll_honors_reduced_motion():
    source=(ROOT/'web/app.js').read_text(encoding='utf-8')
    assert 'matchMedia("(prefers-reduced-motion: reduce)")' in source
    assert source.count('behavior:preferredScrollBehavior()')==2
    assert 'behavior:"smooth"' not in source

def test_v061_material_system_controls_have_unique_accessible_names():
    source=(ROOT/'scripts/build_web.py').read_text(encoding='utf-8')
    assert 'aria-label="Open detail: {esc(form["name"])}"' in source
    browser=(ROOT/'scripts/browser_uat_v060.py').read_text(encoding='utf-8')
    assert 'assert_material_system_accessible_names' in browser
    assert 'buttons.count()==10' in browser
    assert 'len(set(labels))==10' in browser

def test_v061_browser_contract_adds_behavioral_reduced_motion_profile():
    source=(ROOT/'scripts/browser_uat_v060.py').read_text(encoding='utf-8')
    assert "'reduced-motion-programmatic-scroll'" in source
    assert 'expected_profiles=len(VIEWPORTS)+7' in source
    assert '__m2mScrollBehaviors' in source
    assert 'context.add_init_script("() => {' not in source
    assert 'context.add_init_script("window.__m2mScrollBehaviors = [];' in source
    assert 'page.wait_for_function("Array.isArray(window.__m2mScrollBehaviors)")' in source
    assert "set(behaviors)=={'auto'}" in source

def test_v061_public_identity_and_boundaries_remain_bounded():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    notes=(ROOT/'RELEASE_NOTES_v0.6.1.md').read_text(encoding='utf-8')
    state=(ROOT/'docs/CURRENT_STATE.md').read_text(encoding='utf-8')
    assert 'Explore the 60-mineral Materials-to-Mission Atlas' in readme
    assert 'Explore the 60-mineral Strategic Constellation' not in readme
    assert 'This source line is version `0.6.1`.' in state
    for token in ('Frozen GA-001 v1.0.0','YIG remains an engineered material system','M0 maturity','human consequential authority'):
        assert token in notes
