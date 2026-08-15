from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def build_html(tmp_path: Path) -> str:
    output = tmp_path / "web"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_web.py"), "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    return (output / "index.html").read_text(encoding="utf-8")


def test_v073_first_use_orientation_is_exact_and_bounded(tmp_path: Path) -> None:
    html = build_html(tmp_path)
    assert html.count("Start with one material. Follow the pathway. Stop where evidence stops. See what should be proven next.") == 1
    assert html.count("Supported facts stay supported. Unknowns stay visible.") >= 1
    assert html.count("Reviewed does not mean qualified.") == 1
    text = re.sub(r"<[^>]+>", "", html)
    assert text.count("M0 is a public evidence method. It is not qualification, certification, acquisition approval, or mission readiness.") == 1
    for step in ("Choose", "Follow", "Understand", "Move"):
        assert f"<strong>{step}</strong>" in html


def test_v073_pathway_cues_preserve_exact_two_examples(tmp_path: Path) -> None:
    html = build_html(tmp_path)
    assert html.count('class="selected-pathway-row"') == 2
    assert html.count("New here? Start with Gallium.") == 1
    assert "An official critical mineral can still have an unresolved pathway." in html
    assert html.count("Explore deeper:</strong> YIG shows how an engineered material system adds substrate, processing, characterization, and validation questions.") == 1


def test_v073_truth_preserves_human_and_evidence_boundaries() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["version"] == facts["source_version"] == "0.7.3"
    assert facts["current_public_maturity"] == "M0"
    assert facts["human_decision_authority_required"] is True
    assert facts["human_first_time_comprehension_uat_attestation"] == "NOT_ATTESTED"
    assert facts["clarity_orientation_v073"]["scope"] == "FIRST_USE_COPY_AND_PROGRESSIVE_ORIENTATION_ONLY"
    assert facts["clarity_orientation_v073"]["dependency_security"] == "PASS_NO_CHANGE"
    assert facts["clarity_orientation_v073"]["first_time_human_comprehension_uat"] == "NOT_ATTESTED"
    assert facts["clarity_orientation_v073"]["anti_framing"] == "KNOWN_HOSTING_LAYER_LIMITATION"


def test_v073_release_concept_uses_exact_ascii_hyphen() -> None:
    title = (ROOT / "RELEASE_NOTES_v0.7.3.md").read_text(encoding="utf-8").splitlines()[0]
    assert title == "# Materials-to-Mission v0.7.3 - Clarity and Orientation"
