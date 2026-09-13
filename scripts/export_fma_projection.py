#!/usr/bin/env python3
"""Project a public-safe Materials-to-Mission case into portable FMA contracts.

The source M2M case remains authoritative. This adapter emits a deliberately
thin, deterministic FMA projection while retaining richer M2M evidence semantics
inside explicit extension fields. It does not certify the source case, replace
human judgment, or collapse the two domain models into one ontology.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ADAPTER_VERSION = "1.0"
FMA_GRAPH_ID = "https://bridge-node-7.github.io/frontier-mission-assurance/assurance-graph.schema.json"
FMA_DECISION_ID = "https://bridge-node-7.github.io/frontier-mission-assurance/decision-receipt.schema.json"
FMA_RESEARCH_ID = "https://bridge-node-7.github.io/frontier-mission-assurance/research-receipt.schema.json"

DISPOSITION_MAP = {
    "ADVANCE": "APPROVE",
    "VALIDATE": "REVISE",
    "PARTNER": "REVISE",
    "HOLD": "HOLD",
    "STOP": "REJECT",
}

CLAIM_STATE_TO_STATUS = {
    "SUPPORTED": "verified",
    "PARTIALLY_SUPPORTED": "active",
    "UNKNOWN": "open",
    "CONTRADICTED": "open",
    "UNSUPPORTED": "open",
    "EXPIRED": "open",
}


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(value))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _decision_id(case_id: str) -> str:
    return f"DECISION-{case_id}"


def project_case(case: dict[str, Any], *, source_path: str, source_sha256: str) -> tuple[dict, dict, dict]:
    if case.get("synthetic") is not True or case.get("public_safe") is not True:
        raise ValueError("FMA public projection requires synthetic=true and public_safe=true")

    case_id = str(case.get("case_id", "")).strip()
    if not case_id:
        raise ValueError("case_id is required")

    charter = _require_mapping(case.get("decision_charter"), "decision_charter")
    mar = _require_mapping(case.get("material_assurance_record"), "material_assurance_record")
    passport = _require_mapping(case.get("decision_passport"), "decision_passport")

    mission = _require_mapping(mar.get("mission"), "material_assurance_record.mission")
    component = _require_mapping(mar.get("component"), "material_assurance_record.component")
    evidence_records = _require_list(mar.get("evidence_records"), "evidence_records")
    risks = _require_list(mar.get("risks", []), "risks")

    requirements: list[dict[str, Any]] = []
    requirements.extend(_require_list(charter.get("requirements", []), "decision_charter.requirements"))
    requirements.extend(
        _require_list(charter.get("acceptance_criteria", []), "decision_charter.acceptance_criteria")
    )

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    mission_id = str(mission.get("mission_id", "")).strip()
    component_id = str(component.get("component_id", "")).strip()
    if not mission_id or not component_id:
        raise ValueError("mission_id and component_id are required")

    nodes.append(
        {
            "id": mission_id,
            "kind": "mission",
            "title": str(mission.get("label") or charter.get("mission") or mission_id),
            "status": "active",
            "criticality": 5,
            "m2m_projection": {
                "outcome": mission.get("outcome"),
                "source_case": case_id,
            },
        }
    )
    nodes.append(
        {
            "id": component_id,
            "kind": "component",
            "title": str(component.get("label") or component_id),
            "status": "active",
            "criticality": 4,
            "m2m_projection": {
                "function": component.get("function"),
                "source_case": case_id,
            },
        }
    )
    edges.append({"from": mission_id, "to": component_id, "relation": "depends_on"})

    requirement_ids: list[str] = []
    for raw in requirements:
        requirement = _require_mapping(raw, "requirement")
        rid = str(requirement.get("requirement_id", "")).strip()
        if not rid:
            raise ValueError("every projected requirement requires requirement_id")
        requirement_ids.append(rid)
        nodes.append(
            {
                "id": rid,
                "kind": "requirement",
                "title": str(requirement.get("statement") or rid),
                "status": "active",
                "criticality": 5 if requirement.get("critical") is True else 3,
                "m2m_projection": {
                    "category": requirement.get("category"),
                    "method": requirement.get("method"),
                    "evidence_required": requirement.get("evidence_required", []),
                    "critical": bool(requirement.get("critical", False)),
                },
            }
        )
        edges.append({"from": component_id, "to": rid, "relation": "requires"})

    evidence_ids: list[str] = []
    for raw in evidence_records:
        evidence = _require_mapping(raw, "evidence_record")
        eid = str(evidence.get("evidence_id", "")).strip()
        if not eid:
            raise ValueError("every projected evidence record requires evidence_id")
        evidence_ids.append(eid)
        claim_state = str(evidence.get("claim_state", "UNKNOWN"))
        nodes.append(
            {
                "id": eid,
                "kind": "evidence",
                "title": str(evidence.get("title") or eid),
                "status": CLAIM_STATE_TO_STATUS.get(claim_state, "open"),
                "source": {
                    "source": evidence.get("source"),
                    "source_type": evidence.get("source_type"),
                    "locator": evidence.get("locator"),
                    "version": evidence.get("version"),
                    "date_issued": evidence.get("date_issued"),
                    "date_accessed": evidence.get("date_accessed"),
                },
                "m2m_projection": {
                    "basis": evidence.get("basis"),
                    "claim_state": claim_state,
                    "confidence": evidence.get("confidence"),
                    "applicability": evidence.get("applicability"),
                    "requirement_links": evidence.get("requirement_links", []),
                    "claim_links": evidence.get("claim_links", []),
                    "contradictory_evidence": evidence.get("contradictory_evidence", []),
                    "limitations": evidence.get("limitations", []),
                    "classification": evidence.get("classification"),
                    "ai_involvement": evidence.get("ai_involvement"),
                    "human_reviewer": evidence.get("human_reviewer"),
                },
            }
        )
        relation = "contradicts" if claim_state == "CONTRADICTED" else "supports"
        for rid in evidence.get("requirement_links", []):
            if rid in requirement_ids:
                edges.append({"from": eid, "to": rid, "relation": relation})

    risk_ids: list[str] = []
    for raw in risks:
        risk = _require_mapping(raw, "risk")
        rid = str(risk.get("risk_id", "")).strip()
        if not rid:
            raise ValueError("every projected risk requires risk_id")
        risk_ids.append(rid)
        nodes.append(
            {
                "id": rid,
                "kind": "risk",
                "title": str(risk.get("statement") or rid),
                "status": "open",
                "criticality": 4,
                "m2m_projection": {
                    "consequence": risk.get("consequence"),
                    "owner_role": risk.get("owner"),
                },
            }
        )

    decision_id = _decision_id(case_id)
    proposed = str(mar.get("proposed_disposition", "HOLD"))
    fma_disposition = DISPOSITION_MAP.get(proposed)
    if fma_disposition is None:
        raise ValueError(f"unsupported M2M disposition for FMA projection: {proposed}")

    nodes.append(
        {
            "id": decision_id,
            "kind": "decision",
            "title": f"Projected M2M disposition for {case_id}",
            "status": "proposed",
            "criticality": 5,
            "m2m_projection": {
                "source_passport_id": passport.get("passport_id"),
                "source_disposition": proposed,
                "decision_owner_role": charter.get("decision_owner"),
                "disposition_authority_role": charter.get("disposition_authority"),
                "weak_link": passport.get("weak_link"),
                "next_action": mar.get("next_action"),
            },
        }
    )
    for rid in requirement_ids + risk_ids:
        edges.append({"from": decision_id, "to": rid, "relation": "depends_on"})

    graph = {
        "graph_version": "1.0",
        "metadata": {
            "title": f"FMA projection of {case_id}",
            "synthetic": True,
            "public_safe": True,
            "adapter": "materials-to-mission/fma-projection",
            "adapter_version": ADAPTER_VERSION,
            "source_case_path": source_path,
            "source_case_sha256": source_sha256,
            "source_schema_version": case.get("schema_version"),
            "fma_contract_ids": {
                "assurance_graph": FMA_GRAPH_ID,
                "decision_receipt": FMA_DECISION_ID,
                "research_receipt": FMA_RESEARCH_ID,
            },
            "projection_policy": "loss-aware; M2M remains authoritative",
        },
        "nodes": nodes,
        "edges": edges,
    }

    basis_refs = [*requirement_ids, *evidence_ids, *risk_ids]
    weak_link = str(passport.get("weak_link") or "M2M source case retains an unresolved weak link.")
    next_action = str(mar.get("next_action") or "Reassess when the source case changes.")
    success_signal = str(mar.get("success_signal") or "Required evidence becomes reviewable.")
    reassessment = str(
        mar.get("reassessment_trigger") or "New evidence or changed assumptions require review."
    )
    decision_receipt = {
        "decision_version": "1.0",
        "decision": {
            "id": decision_id,
            "disposition": fma_disposition,
            "rationale": f"Projected from M2M {proposed}: {weak_link} Next action: {next_action}",
            "reopen_when": [success_signal, reassessment],
        },
        "basis": {"node_refs": basis_refs},
    }

    preserved_evidence_fields = [
        "basis",
        "claim_state",
        "confidence",
        "applicability",
        "requirement_links",
        "claim_links",
        "contradictory_evidence",
        "limitations",
        "classification",
        "ai_involvement",
        "human_reviewer",
    ]
    manifest = {
        "projection_version": "1.0",
        "adapter": "materials-to-mission/fma-projection",
        "adapter_version": ADAPTER_VERSION,
        "source": {
            "repository": "Bridge-Node-7/materials-to-mission",
            "case_id": case_id,
            "path": source_path,
            "sha256": source_sha256,
            "schema_version": case.get("schema_version"),
        },
        "target_contracts": [FMA_GRAPH_ID, FMA_DECISION_ID],
        "authoritative_model": "Materials-to-Mission source case",
        "projection_is_lossy": True,
        "preserved_m2m_evidence_fields": preserved_evidence_fields,
        "non_claims": [
            "The FMA projection does not replace the source M2M case.",
            "Projection validity does not establish source credibility, qualification, mission readiness, or decision authorization.",
            "Human and AI involvement fields are preserved as source-declared provenance, not independently authenticated identity.",
        ],
    }
    return graph, decision_receipt, manifest


def export_projection(case_path: Path, output_dir: Path) -> dict[str, str]:
    source_bytes = case_path.read_bytes()
    try:
        case = json.loads(source_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON case: {exc}") from exc
    case = _require_mapping(case, "case")

    graph, decision, manifest = project_case(
        case,
        source_path=case_path.as_posix(),
        source_sha256=_sha256_bytes(source_bytes),
    )
    graph_path = output_dir / "assurance-graph.json"
    decision_path = output_dir / "decision-receipt.json"
    manifest_path = output_dir / "projection-manifest.json"

    _write_json(graph_path, graph)
    _write_json(decision_path, decision)
    manifest["artifacts"] = {
        "assurance-graph.json": _sha256_bytes(graph_path.read_bytes()),
        "decision-receipt.json": _sha256_bytes(decision_path.read_bytes()),
    }
    _write_json(manifest_path, manifest)
    return {
        "graph": graph_path.as_posix(),
        "decision": decision_path.as_posix(),
        "manifest": manifest_path.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="Public-safe synthetic M2M case JSON")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/fma-projection"),
        help="Directory for deterministic FMA projection artifacts",
    )
    args = parser.parse_args()

    try:
        paths = export_projection(args.case, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 2
    print("PASS: deterministic M2M -> FMA projection written")
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
