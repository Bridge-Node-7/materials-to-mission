from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .boundary import scan_public_boundary
from .resources import schema_dir


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    code: str
    message: str
    path: str = "$"
    severity: str = "ERROR"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    findings: tuple[ValidationFinding, ...]

    @property
    def valid(self) -> bool:
        return not any(item.severity == "ERROR" for item in self.findings)


def _path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def _schema_findings(case: dict[str, Any]) -> list[ValidationFinding]:
    import json

    base = schema_dir()
    schemas = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(base.glob("*.json"))]
    registry = Registry().with_resources((schema["$id"], Resource.from_contents(schema)) for schema in schemas)
    schema = next(item for item in schemas if item["$id"].endswith("/case.schema.json"))
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    return [
        ValidationFinding("SCHEMA", error.message, _path(error.absolute_path))
        for error in sorted(validator.iter_errors(case), key=lambda e: list(e.absolute_path))
    ]


def _semantic_findings(case: dict[str, Any], public: bool) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    charter = case.get("decision_charter", {})
    mar = case.get("material_assurance_record", {})
    passport = case.get("decision_passport", {})

    for field in ("decision_owner", "disposition_authority"):
        value = str(charter.get(field, "")).strip()
        if not value:
            findings.append(ValidationFinding("HUMAN_AUTHORITY", f"{field} must name a human authority", f"$.decision_charter.{field}"))
        if value.lower() in {"ai", "automated system", "algorithm", "model"}:
            findings.append(ValidationFinding("HUMAN_AUTHORITY", f"{field} may not be assigned to automation", f"$.decision_charter.{field}"))

    triggered = [c for c in mar.get("critical_conditions", []) if c.get("triggered")]
    dispositions = {str(mar.get("proposed_disposition", "")), str(passport.get("disposition", ""))}
    if triggered and dispositions.intersection({"ADVANCE", "PARTNER"}):
        findings.append(ValidationFinding("CRITICAL_CONDITION", "triggered critical conditions block ADVANCE and PARTNER", "$.decision_passport.disposition"))

    evidence = mar.get("evidence_records", [])
    posture = passport.get("evidence_posture", {})
    mapping = {"UNKNOWN": "unknown", "CONTRADICTED": "contradicted", "UNSUPPORTED": "unsupported", "EXPIRED": "expired"}
    for item in evidence:
        state = item.get("claim_state")
        bucket = mapping.get(state)
        if not bucket:
            continue
        evidence_id = item.get("evidence_id", "")
        values = posture.get(bucket, [])
        if not any(evidence_id in str(value) for value in values):
            findings.append(ValidationFinding("VISIBLE_UNCERTAINTY", f"{state} evidence {evidence_id} is not visible in Decision Passport posture", f"$.decision_passport.evidence_posture.{bucket}"))

    governing = [w for w in mar.get("weak_links", []) if w.get("governing")]
    if len(governing) != 1:
        findings.append(ValidationFinding("WEAK_LINK", "exactly one governing weak link is required", "$.material_assurance_record.weak_links"))

    if passport.get("decision_owner") != charter.get("decision_owner"):
        findings.append(ValidationFinding("AUTHORITY_MISMATCH", "Decision Passport owner must match Decision Charter owner", "$.decision_passport.decision_owner"))
    if passport.get("disposition_authority") != charter.get("disposition_authority"):
        findings.append(ValidationFinding("AUTHORITY_MISMATCH", "Decision Passport authority must match Decision Charter authority", "$.decision_passport.disposition_authority"))
    if passport.get("disposition") != mar.get("proposed_disposition"):
        findings.append(ValidationFinding("DISPOSITION_MISMATCH", "MAR and Decision Passport dispositions must match", "$.decision_passport.disposition"))

    evidence_ids = {e.get("evidence_id") for e in evidence}
    source_ids = set(case.get("provenance", {}).get("source_record_ids", []))
    if evidence_ids != source_ids:
        findings.append(ValidationFinding("PROVENANCE", "provenance source_record_ids must exactly match MAR evidence IDs", "$.provenance.source_record_ids"))

    if public or case.get("public_safe"):
        if not case.get("synthetic") or case.get("maturity") != "SYNTHETIC_PUBLIC_REFERENCE":
            findings.append(ValidationFinding("PUBLIC_BOUNDARY", "public-safe cases must be synthetic public references", "$"))
        for message in scan_public_boundary(case):
            findings.append(ValidationFinding("PUBLIC_BOUNDARY", message, "$"))
        supplier = str(mar.get("supplier", {}).get("label", "")).lower()
        facility = str(mar.get("facility", {}).get("label", "")).lower()
        if "fictional" not in supplier or "fictional" not in facility:
            findings.append(ValidationFinding("PUBLIC_BOUNDARY", "public supplier and facility labels must be visibly fictional", "$.material_assurance_record"))

    return findings


def validate_case(case: dict[str, Any], *, public: bool = False) -> ValidationResult:
    findings = _schema_findings(case)
    if not findings:
        findings.extend(_semantic_findings(case, public))
    return ValidationResult(tuple(findings))
