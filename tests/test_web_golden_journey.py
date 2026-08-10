from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_golden_journey_source_has_required_landmarks() -> None:
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    required = [
        'id="arrival"',
        'id="atlas"',
        'id="gallium"',
        'id="trace"',
        'id="support"',
        'id="examine"',
        'id="decision"',
        "See the pathway.",
        "Verify the constraint.",
        "Direct the next move.",
        "Human decision authority remains required.",
    ]
    for marker in required:
        assert marker in html


def test_browser_is_read_only_and_has_no_external_runtime_dependency() -> None:
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8").lower()
    js = (ROOT / "web" / "app.js").read_text(encoding="utf-8").lower()

    assert "<form" in html  # dialog uses method=dialog only
    assert 'method="dialog"' in html
    assert "fetch(data_url" in js
    assert "post(" not in js
    assert "put(" not in js
    assert "delete(" not in js
    assert "localstorage" not in js
    assert "sessionstorage" not in js
    assert "analytics" not in html + js
    assert "telemetry" not in html + js
    assert "cdn." not in html
    assert "https://fonts" not in html


def test_skip_link_remains_immediate_under_reduced_motion() -> None:
    css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")
    block = css.split(".skip-link {", 1)[1].split("}", 1)[0]
    assert "transition: none;" in block
    assert ".skip-link:focus { transform: translateY(0); }" in css


def test_browser_declares_no_network_favicon() -> None:
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert '<link rel="icon" href="data:,">' in html
    assert 'href="/favicon.ico"' not in html
    assert 'href="./favicon.ico"' not in html


def test_browser_preserves_no_score_and_human_authority_boundary() -> None:
    combined = "\n".join(
        (ROOT / "web" / name).read_text(encoding="utf-8")
        for name in ("index.html", "styles.css", "app.js")
    ).lower()

    assert "readiness score" not in combined
    assert "not a readiness determination" in combined
    assert "does not approve, qualify, certify, waive, terminate, or close" in combined
    assert "human decision required" in combined
    assert "risk gauge" not in combined
    assert "readiness percentage" not in combined


def test_accessibility_and_reduced_motion_contract() -> None:
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

    assert 'class="skip-link"' in html
    assert ":focus-visible" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "@media (max-width: 560px)" in css
    assert 'aria-label="Gallium trace to mission pathway"' in html


def test_web_build_is_deterministic_and_binds_frozen_ga001(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    for output in (first, second):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_web.py"), "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

    def digest_tree(root: Path) -> dict[str, str]:
        return {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(p for p in root.rglob("*") if p.is_file())
        }

    assert digest_tree(first) == digest_tree(second)

    payload = json.loads((first / "data" / "ga001.json").read_text(encoding="utf-8"))
    assert payload["snapshot"]["snapshot_id"] == "GA-001"
    assert payload["snapshot"]["snapshot_version"] == "1.0.0"
    assert payload["snapshot"]["real_case_001"] is False
    assert payload["view"]["view_contract_version"] == "0.3.0"
    assert payload["view"]["decision_authority"] == "human"
    assert payload["rights"]["rights_posture"] == "metadata-and-original-paraphrase-only"


def test_controlled_examine_accent_meets_contrast_floor() -> None:
    def channel(value: int) -> float:
        x = value / 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    def luminance(value: str) -> float:
        value = value.lstrip("#")
        r, g, b = (int(value[i:i+2], 16) for i in (0, 2, 4))
        return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

    def contrast_ratio(fg: str, bg: str) -> float:
        a, b = luminance(fg), luminance(bg)
        return (max(a, b) + 0.05) / (min(a, b) + 0.05)

    tokens = json.loads(
        (ROOT / "docs" / "V0_3_DESIGN_TOKENS.json").read_text(encoding="utf-8")
    )
    accent = tokens["modes"]["examine"]["accent"]
    field = tokens["modes"]["examine"]["field"]
    css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

    assert accent == "#825F31"
    assert "--examine-accent: #825F31;" in css
    assert contrast_ratio(accent, field) >= 4.5

def test_trace_preserves_unknown_nodes() -> None:
    view = json.loads(
        (
            ROOT
            / "public-snapshots"
            / "gallium"
            / "GA-001"
            / "public-view.json"
        ).read_text(encoding="utf-8")
    )
    states = {item["kind"]: item["state"] for item in view["trace_nodes"]}
    assert states["qualification"] == "unknown"
    assert states["acquisition-access"] == "unknown"
    assert states["mission"] == "unknown"
