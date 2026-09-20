from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_javascript_boundary_is_explicit_and_evidence_preserving() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    assert '<noscript>' in html
    assert 'id="no-js-boundary"' in html
    assert 'Continue to the static Mineral List' in html
    assert 'Review evidence &amp; sources' in html
    assert 'JavaScript is required' not in html
    assert html.count('<h1') == 1
    assert 'html:not(.js-ready) #constellationPanel{display:none!important}' in css
    assert 'html:not(.js-ready) #indexPanel{display:block!important}' in css


def test_v076_release_identity_and_truth_boundaries() -> None:
    import json
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.7.6"
    assert facts["version"] == facts["source_version"] == "0.7.6"
    assert facts["current_public_maturity"] == "M0"
    assert facts["human_decision_authority_required"] is True
