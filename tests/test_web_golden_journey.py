from __future__ import annotations
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_strategic_constellation_is_first_public_experience() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert "Materials-to-Mission Atlas" in html
    assert "Explore critical minerals, their application connections, and reviewed pathways where public evidence is available." in html
    assert 'id="atlas"' in html
    assert 'id="trace"' in html
    assert 'id="examine"' in html
    assert 'id="decision"' in html
    assert 'id="forms"' in html
    assert 'id="sources"' in html
    assert 'id="ga-pathway"' in html
    assert 'href="#ga-pathway">Follow the pathway →</a>' in html
    assert "02 · FOCUS" not in html
    assert "03 · FOLLOW" not in html
    assert "Beyond the Evidence Map" in html
    assert "Explore how evidence, uncertainty, and human judgment shape strategic choices." in html
    assert ">Explore the Decision Experience</a>" in html
    assert ">Strategic Partnership</a>" in html
    assert "See the field.<br>" not in html

def test_browser_is_static_read_only_progressive_enhancement() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8").lower()
    js = (ROOT / "web/app.js").read_text(encoding="utf-8").lower()
    for forbidden in ("fetch(", "xmlhttprequest", "websocket", "localstorage", "sessionstorage", "indexeddb"):
        assert forbidden not in js
    assert "analytics" not in html + js
    assert "telemetry" not in html + js
    assert "https://fonts" not in html
    assert 'type="application/json"' in html

def test_no_javascript_baseline_is_semantic() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert 'id="indexPanel"' in html
    assert 'class="atlas-tools js-only"' in html
    assert 'class="lensbar js-only"' in html
    assert "JavaScript is required" not in html

def test_accessibility_and_reduced_motion_contract() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    js = (ROOT / "web/app.js").read_text(encoding="utf-8")
    assert 'class="skip-link"' in html
    assert 'href="#atlas-title">Skip to Materials Atlas</a>' in html
    assert html.count("<h1") == 1
    assert '<h1 id="atlas-title">Materials-to-Mission Atlas</h1>' in html
    assert ':focus-visible' in css
    assert '[hidden]{display:none!important}' in css.replace(" ", "")
    assert 'prefers-reduced-motion:reduce' in css.replace(" ", "")
    assert '<dialog id="materialSheet" class="material-sheet" aria-label="Material detail">' in html
    assert 'aria-labelledby="sheetTitle"' not in html
    assert 'sheet.setAttribute("aria-labelledby", title.id)' in js
    assert "sheet.showModal()" in js
    assert "sheet.show()" not in js
    assert 'role="combobox"' in html
    assert 'aria-controls="searchResults"' in html
    assert 'viewport-fit=cover' in html
    assert '<span id="ga-pathway" class="pathway-entry-anchor" aria-hidden="true"></span>' in html

def test_mobile_default_does_not_auto_open_material_sheet() -> None:
    js = (ROOT / "web/app.js").read_text(encoding="utf-8")
    assert 'let selectedId = null' in js
    assert 'selectMaterial("gallium", {pushHash:false, openSheet:false})' not in js
    assert 'openSheet && matchMedia("(max-width:1160px)").matches' in js

    assert 'centerMaterialInViewport(material.id)' in js


def test_rare_earth_convention_is_precise_and_orientation_only() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert "The Atlas 15-count follows the controlled USGS commodity grouping used here; scandium remains separately listed." in html
    assert html.count("Rare-earth convention.") == 1

def test_typography_floor() -> None:
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", css)]
    assert sizes and min(sizes) >= 10

def test_web_build_is_deterministic_and_keeps_current_pages_shape(tmp_path: Path) -> None:
    trees = []
    outputs = []
    for name in ("a", "b"):
        out = tmp_path / name
        subprocess.run([sys.executable, str(ROOT / "scripts/build_web.py"), "--output", str(out)], cwd=ROOT, check=True)
        observed = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
        assert observed == {"index.html", "styles.css", "app.js", "data/ga001.json", "WEB_MANIFEST.sha256"}
        trees.append({rel: hashlib.sha256((out / rel).read_bytes()).hexdigest() for rel in observed})
        outputs.append(out)
    assert trees[0] == trees[1]
    built = (outputs[0] / "index.html").read_text(encoding="utf-8")
    assert built.count('class="mineral') == 60
    assert "Evidence Horizon" in built
    assert "Reviewed Pathway" in built
    assert "<!-- R6:" not in built


def test_search_and_svg_dynamic_paths_avoid_innerhtml() -> None:
    js = (ROOT / "web/app.js").read_text(encoding="utf-8")
    assert "results.innerHTML" not in js
    assert "results.replaceChildren" in js
    assert 'document.createElement("button")' in js
    assert "svg.innerHTML" not in js
    assert "svg.replaceChildren()" in js
