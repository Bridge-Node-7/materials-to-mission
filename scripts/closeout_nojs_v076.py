from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "0.7.5"
NEW = "0.7.6"


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


# Progressive enhancement boundary: static evidence remains usable without JavaScript.
index = ROOT / "web/index.html"
html = index.read_text(encoding="utf-8")
if 'id="no-js-boundary"' not in html:
    marker = "<main>\n"
    fallback = '''<main>\n<noscript>\n  <section id="no-js-boundary" class="no-js-notice" aria-labelledby="no-js-title">\n    <p class="eyebrow">STATIC EVIDENCE MODE</p>\n    <h2 id="no-js-title">Interactive map controls are unavailable.</h2>\n    <p>The Materials-to-Mission evidence record remains available without JavaScript. Continue with the complete static Mineral List, reviewed pathways, claim register, and source-linked evidence below.</p>\n    <p><a href="#indexPanel">Continue to the static Mineral List</a> · <a href="#sources">Review evidence &amp; sources</a></p>\n  </section>\n</noscript>\n'''
    if marker not in html:
        raise SystemExit("<main> insertion point not found")
    html = html.replace(marker, fallback, 1)
index.write_text(html, encoding="utf-8", newline="\n")

styles = ROOT / "web/styles.css"
css = styles.read_text(encoding="utf-8")
block = '''\n/* v0.7.6 progressive-enhancement boundary */\n.no-js-notice{max-width:1180px;margin:0 auto;padding:1rem 1.25rem 1.25rem;border-bottom:1px solid rgba(241,200,107,.28);background:rgba(10,19,36,.92)}\n.no-js-notice h2{margin:.2rem 0 .55rem;font-size:clamp(1.35rem,2.7vw,2rem)}\n.no-js-notice p{max-width:78ch;margin:.45rem 0;color:var(--muted,#b8c2d1);line-height:1.55}\n.no-js-notice a{color:var(--gold,#f1c86b)}\nhtml:not(.js-ready) #constellationPanel{display:none!important}\nhtml:not(.js-ready) #indexPanel{display:block!important}\n'''
if "/* v0.7.6 progressive-enhancement boundary */" not in css:
    css = css.rstrip() + block + "\n"
styles.write_text(css, encoding="utf-8", newline="\n")

# Release identity: bounded accessibility/progressive-enhancement maintenance release.
(ROOT / "VERSION").write_text(NEW + "\n", encoding="utf-8", newline="\n")
replace_once("pyproject.toml", f'version = "{OLD}"', f'version = "{NEW}"')
replace_once("CITATION.cff", f"version: {OLD}", f"version: {NEW}")

facts_path = ROOT / "PROJECT_FACTS.json"
facts = json.loads(facts_path.read_text(encoding="utf-8"))
facts["version"] = NEW
facts["source_version"] = NEW
facts["release_artifact"] = f"materials-to-mission-v{NEW}.zip"
facts["maintenance_v076"] = {
    "scope": "NO_JAVASCRIPT_PROGRESSIVE_ENHANCEMENT_BOUNDARY_ONLY",
    "static_evidence_mode": True,
    "static_index_forced_visible_without_javascript": True,
    "interactive_constellation_hidden_without_javascript": True,
    "evidence_model_changed": False,
    "gallium_evidence_changed": False,
    "yig_evidence_changed": False,
    "schema_or_pathway_changed": False,
    "human_decision_authority_changed": False,
}
facts_path.write_text(json.dumps(facts, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")

# Current-facing release documents move forward; historical records remain intact.
for rel in ("docs/CURRENT_STATE.md", "VALIDATION_REPORT.md"):
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    if OLD in text:
        p.write_text(text.replace(OLD, NEW), encoding="utf-8", newline="\n")

release_notes = ROOT / "RELEASE_NOTES.md"
release_notes.write_text('''# Materials-to-Mission v0.7.6 - Trust Hardening\n\n## Purpose\n\nv0.7.6 is a bounded accessibility and resilience maintenance release. It makes the no-JavaScript operating boundary explicit and preserves a useful static evidence path without changing the underlying evidence, schemas, pathways, or human decision authority.\n\n## Improved\n\n- Added an explicit no-JavaScript static evidence notice.\n- Forced the complete static Mineral List visible when JavaScript is unavailable.\n- Hid the interactive constellation when it cannot function, avoiding a misleading inert control surface.\n- Preserved direct access to reviewed pathways, claim registers, and source-linked evidence.\n\n## Preserved\n\n- M0 remains M0; no M1 capability is claimed.\n- Frozen GA-001 v1.0.0, MF-001, and YIG-001 evidence meaning is unchanged.\n- YIG remains an engineered material system, not a USGS critical mineral.\n- Unknown remains non-favorable and Evidence Horizon remains explicit.\n- Human consequential authority remains required.\n- No supplier, customer, government, investment, acquisition, readiness, certification, or operational qualification claim is added.\n\n## Validation\n\nThe complete repository gate, deterministic packaging, required CI/CodeQL/Browser UAT checks, and production readback remain authoritative.\n''', encoding="utf-8", newline="\n")

changelog = ROOT / "CHANGELOG.md"
text = changelog.read_text(encoding="utf-8")
old = "## Unreleased\n\nNo changes recorded after v0.7.5.\n\n## [0.7.5] - 2026-08-22\n"
new = """## Unreleased\n\nNo changes recorded after v0.7.6.\n\n## [0.7.6] - 2026-09-13\n\n### Improved\n- Added an explicit no-JavaScript static evidence mode and direct route to the complete Mineral List and sources.\n- Forced the static index visible and the interactive constellation hidden when JavaScript is unavailable.\n- Added regression coverage for the progressive-enhancement boundary.\n\n### Preserved\n- Existing evidence, schemas, qualification boundaries, selected pathways, maturity semantics, and human consequential authority.\n\n## [0.7.5] - 2026-08-22\n"""
if old not in text:
    raise SystemExit("unexpected changelog header")
changelog.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

# Existing release-contract tests intentionally track the active source version even
# when their filenames preserve the release in which the invariant was introduced.
for rel in (
    "tests/test_foundation_hardening.py",
    "tests/test_v061_truth_accessibility.py",
    "tests/test_v070_selected_pathways_release.py",
    "tests/test_v073_clarity_orientation.py",
    "tests/test_v075_trust_hardening.py",
):
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    if OLD in text:
        p.write_text(text.replace(OLD, NEW), encoding="utf-8", newline="\n")

# Dedicated regression for the graceful no-JavaScript path.
test = ROOT / "tests/test_v076_nojs_boundary.py"
test.write_text('''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\n\ndef test_no_javascript_boundary_is_explicit_and_evidence_preserving() -> None:\n    html = (ROOT / "web/index.html").read_text(encoding="utf-8")\n    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")\n    assert '<noscript>' in html\n    assert 'id="no-js-boundary"' in html\n    assert 'Continue to the static Mineral List' in html\n    assert 'Review evidence &amp; sources' in html\n    assert 'JavaScript is required' not in html\n    assert html.count('<h1') == 1\n    assert 'html:not(.js-ready) #constellationPanel{display:none!important}' in css\n    assert 'html:not(.js-ready) #indexPanel{display:block!important}' in css\n\n\ndef test_v076_release_identity_and_truth_boundaries() -> None:\n    import json\n    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))\n    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.7.6"\n    assert facts["version"] == facts["source_version"] == "0.7.6"\n    assert facts["maintenance_v076"]["evidence_model_changed"] is False\n    assert facts["maintenance_v076"]["schema_or_pathway_changed"] is False\n    assert facts["maintenance_v076"]["human_decision_authority_changed"] is False\n''', encoding="utf-8", newline="\n")
