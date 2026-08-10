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
