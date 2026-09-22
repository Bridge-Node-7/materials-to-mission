from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "synthetic-critical-material-pathway" / "case.json"
SCRIPT = ROOT / "scripts" / "export_fma_projection.py"


def _run(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(CASE), "--output-dir", str(output_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_projection_is_deterministic_and_preserves_rich_evidence_semantics():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        first = base / "first"
        second = base / "second"
        r1 = _run(first)
        r2 = _run(second)
        assert r1.returncode == 0, r1.stdout + r1.stderr
        assert r2.returncode == 0, r2.stdout + r2.stderr

        for name in ("assurance-graph.json", "decision-receipt.json", "projection-manifest.json"):
            assert (first / name).read_bytes() == (second / name).read_bytes()

        graph = json.loads((first / "assurance-graph.json").read_text(encoding="utf-8"))
        nodes = {node["id"]: node for node in graph["nodes"]}
        evidence = nodes["E-005"]["m2m_projection"]
        assert evidence["ai_involvement"] == {"used": True, "tasks": ["Comparison"]}
        assert evidence["human_reviewer"] == "Fictional Human Reviewer"
        assert evidence["contradictory_evidence"] == ["CS-A conflicts with CS-B"]
        assert evidence["claim_state"] == "CONTRADICTED"

        decision = json.loads((first / "decision-receipt.json").read_text(encoding="utf-8"))
        assert decision["decision"]["disposition"] == "HOLD"
        assert decision["decision"]["id"] == "DECISION-M2M-SYNTHETIC-001"
        assert "E-004" in decision["basis"]["node_refs"]
        assert "REQ-ORIGIN" in decision["basis"]["node_refs"]

        manifest = json.loads((first / "projection-manifest.json").read_text(encoding="utf-8"))
        assert manifest["projection_is_lossy"] is True
        assert manifest["source"]["sha256"] == hashlib.sha256(CASE.read_bytes()).hexdigest()
        assert "ai_involvement" in manifest["preserved_m2m_evidence_fields"]
        assert "human_reviewer" in manifest["preserved_m2m_evidence_fields"]
        assert "contradictory_evidence" in manifest["preserved_m2m_evidence_fields"]
        assert manifest["target_contracts"] == [
            "https://bridge-node-7.github.io/frontier-mission-assurance/assurance-graph.schema.json",
            "https://bridge-node-7.github.io/frontier-mission-assurance/decision-receipt.schema.json",
        ]
        assert manifest["target_contract_sha256"] == {
            "https://bridge-node-7.github.io/frontier-mission-assurance/assurance-graph.schema.json":
                "28be24c589f7b3e26586af58c4a6f413e9398ca784cac95191a928d85a619f85",
            "https://bridge-node-7.github.io/frontier-mission-assurance/decision-receipt.schema.json":
                "dd19aad0fb1dd2f877e15d04e5d8812e4e2fe0cccb634c513e62f91148056fcf",
        }


def test_public_projection_refuses_non_synthetic_case():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source = root / "case.json"
        source.write_text(
            json.dumps({"case_id": "REAL-001", "synthetic": False, "public_safe": True}),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(source), "--output-dir", str(root / "out")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 2
        assert "requires synthetic=true and public_safe=true" in result.stdout
