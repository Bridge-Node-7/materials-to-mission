from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def test_ga001_claims_are_server_rendered() -> None:
    out=ROOT/"build"/"r632-test"
    subprocess.run([sys.executable,str(ROOT/"scripts/build_web.py"),"--output",str(out)],cwd=ROOT,check=True)
    html=(out/"index.html").read_text(encoding="utf-8")
    assert html.count('class="ga-claim"') == 7
    for index in range(1,8):
        assert f"GA-C{index:02d}" in html

def test_no_js_semantic_claim_register_is_in_template_contract() -> None:
    html=(ROOT/"web/index.html").read_text(encoding="utf-8")
    builder=(ROOT/"scripts/build_web.py").read_text(encoding="utf-8")
    assert 'class="claim-register"' in html
    assert "<!-- R6:GA_CLAIMS -->" in html
    assert '"<!-- R6:GA_CLAIMS -->": ga_claim_items' in builder

def test_assistive_status_channel_is_present() -> None:
    html=(ROOT/"web/index.html").read_text(encoding="utf-8")
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    css=(ROOT/"web/styles.css").read_text(encoding="utf-8")
    assert 'id="experienceStatus"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'function announce(message)' in js
    assert ".sr-only" in css

def test_public_overlay_does_not_define_package_integrity_manifest() -> None:
    assert not (ROOT/"PUBLIC_OVERLAY_MANIFEST.sha256").exists()
