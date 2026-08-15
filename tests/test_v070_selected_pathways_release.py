from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_v070_historical_selected_pathways_release_contract():
    changelog=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    assert '## [0.7.0] - 2026-08-13' in changelog
    assert 'exactly two bounded public deeper examples: Gallium and YIG' in changelog
    assert 'Frozen GA-001, MF-001, and YIG-001 evidence is unchanged' in changelog

def test_v070_truth_and_uat_scope():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    registry=json.loads((ROOT/'web/selected-pathways.json').read_text(encoding='utf-8'))
    assert facts['immediate_prior_immutable_release']['tag']=='v0.7.1'
    assert facts['immediate_prior_immutable_release']['verified_signed_tag_target']=='2699783e1404fd1e6b01ae81451c29ecf9fcef27'
    assert facts['historical_v070_selected_pathways_release_matrix']=='72_SCENARIO_CONFIGURATIONS_X_72_ACCEPTANCE_PROBES_EXTERNAL_GATE'
    assert facts['selected_pathways_public_example_count']==len(registry['pathways'])
    assert facts['selected_pathways_public_examples']==['Gallium','Yttrium Iron Garnet (YIG)']
    assert facts['selected_pathways_gallium_status']=='CRITICAL_MINERAL_REVIEWED_PATHWAY'
    assert facts['selected_pathways_yig_status']=='ENGINEERED_MATERIAL_SYSTEM_REVIEWED_CONTEXT'
    assert facts['selected_pathways_human_desktop_visual_uat']=='PASS_USER_REVIEW_2026-08-13'
    assert facts['selected_pathways_human_mobile_visual_uat']=='NOT_SEPARATELY_ATTESTED'
    assert facts['selected_pathways_human_assistive_technology_uat']=='NOT_ATTESTED'

def test_v070_release_boundaries_are_explicit():
    facts=json.loads((ROOT/'PROJECT_FACTS.json').read_text(encoding='utf-8'))
    notes=(ROOT/facts['release_notes']).read_text(encoding='utf-8')
    state=(ROOT/'docs/CURRENT_STATE.md').read_text(encoding='utf-8')
    assert 'does not add or upgrade underlying evidence' in state
    assert 'YIG remains an engineered material system, not a USGS critical mineral' in notes
    for token in ('M0 remains M0','No M1','Human consequential authority remains required','Unknown remains non-favorable'):
        assert token.lower() in notes.lower()

def test_v070_browser_uat_respects_progressive_disclosure_before_trace():
    source=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    assert "if not action.first.is_visible():" in source
    assert "ancestor::details[1]" in source
    assert "drawer.locator('summary').click()" in source
    assert "action.first.wait_for(state='visible')" in source
    assert "action.first.click(); page.locator('#trace.is-revealed').wait_for()" in source

def test_v070_browser_uat_respects_progressive_disclosure_before_yig():
    source=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    assert "if not yig.is_visible():" in source
    assert "drawer=yig.locator('xpath=ancestor::details[1]')" in source
    assert "drawer.locator('summary').click()" in source
    assert "yig.wait_for(state='visible')" in source
    assert "yig.click(); record(checks,'39-yig-not-critical-mineral'" in source

def test_v070_browser_uat_respects_progressive_disclosure_before_parent_return():
    source=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    assert "if not parent.is_visible():" in source
    assert "drawer=parent.locator('xpath=ancestor::details[1]')" in source
    assert "drawer.locator('summary').click()" in source
    assert "parent.wait_for(state='visible')" in source
    assert "parent.click(); record(checks,'41-parent-return-restores-yttrium'" in source

def test_v070_special_trace_profile_respects_progressive_disclosure():
    import ast

    source=(ROOT/'scripts/browser_uat.py').read_text(encoding='utf-8')
    tree=ast.parse(source)

    assignments=[]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id=='special_trace' for t in node.targets):
            continue
        value=node.value
        if not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr=='locator'
            and value.args
            and isinstance(value.args[0], ast.Constant)
            and isinstance(value.args[0].value, str)
        ):
            continue
        assignments.append(value.args[0].value)

    assert assignments == ['#desktopDetail [data-depth="trace"]']

    def rooted_call(node, method):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == method
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == 'special_trace'
        )

    assert any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and rooted_call(node.test.operand, 'is_visible')
        for node in ast.walk(tree)
    )

    assert any(
        rooted_call(node, 'wait_for')
        and any(
            kw.arg == 'state'
            and isinstance(kw.value, ast.Constant)
            and kw.value.value == 'visible'
            for kw in node.keywords
        )
        for node in ast.walk(tree)
    )

    assert any(rooted_call(node, 'click') for node in ast.walk(tree))

    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == 'click'
        and isinstance(node.func.value, ast.Call)
        and isinstance(node.func.value.func, ast.Attribute)
        and node.func.value.func.attr == 'locator'
        and node.func.value.args
        and isinstance(node.func.value.args[0], ast.Constant)
        and node.func.value.args[0].value == '#desktopDetail [data-depth="trace"]'
        for node in ast.walk(tree)
    )
