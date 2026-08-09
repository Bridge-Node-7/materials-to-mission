from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import unicodedata
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
    schemas = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(base.glob("*.json"))
    ]
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    schema = next(
        item for item in schemas if item["$id"].endswith("/case.schema.json")
    )
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    return [
        ValidationFinding("SCHEMA", error.message, _path(error.absolute_path))
        for error in sorted(
            validator.iter_errors(case),
            key=lambda error: list(error.absolute_path),
        )
    ]


_AUTOMATION_TERM = re.compile(
    r"\b(?:ai|artificial intelligence|automated|automation|algorithm(?:ic)?|"
    r"machine(?: learning)?|bot|chatbot|large language model|llm|chatgpt|"
    r"gpt(?:\s+\d+(?:\.\d+)?)?|claude|autonomous(?: agent)?|"
    r"decision engine|system selected agent|agent|model)\b",
    re.IGNORECASE,
)
_NAMED_HUMAN_WITH_ROLE = re.compile(
    r"\b(?i:manager|lead|director|officer|owner|authority|reviewer|engineer|"
    r"analyst|counsel|scientist|researcher|coordinator|administrator|architect|"
    r"supervisor|chair|chief|head|specialist)\s+"
    r"(?:(?i:dr|mr|ms|mx)\.?\s+)?"
    r"[A-Z][A-Za-z'’\-]+\s+[A-Z][A-Za-z'’\-]+\b"
)
_EVIDENCE_ID = re.compile(r"^(E-[0-9]{3,})(?=$|[:\s])")
_CONDITION_ID = re.compile(r"^(CC-[A-Z0-9-]+)(?=$|[:\s])")


def _normalize_authority(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = re.sub(r"(?i)\ba[\W_]*i\b", "ai", normalized)
    normalized = re.sub(r"[-_/]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip().casefold()


def _looks_automated_authority(value: str) -> bool:
    normalized = _normalize_authority(value)
    if not _AUTOMATION_TERM.search(normalized):
        return False
    return _NAMED_HUMAN_WITH_ROLE.search(value) is None


def _leading_identifier(value: Any, pattern: re.Pattern[str]) -> str | None:
    match = pattern.match(str(value).strip())
    return match.group(1) if match else None


def _identifier_set(values: Any, pattern: re.Pattern[str]) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {
        identifier
        for value in values
        if (identifier := _leading_identifier(value, pattern)) is not None
    }


def _parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _semantic_findings(
    case: dict[str, Any],
    public: bool,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    charter = case.get("decision_charter", {})
    mar = case.get("material_assurance_record", {})
    passport = case.get("decision_passport", {})

    for field in ("decision_owner", "disposition_authority"):
        value = str(charter.get(field, "")).strip()
        path = f"$.decision_charter.{field}"
        if not value:
            findings.append(
                ValidationFinding(
                    "HUMAN_AUTHORITY",
                    f"{field} must name a human authority",
                    path,
                )
            )
        elif _looks_automated_authority(value):
            findings.append(
                ValidationFinding(
                    "HUMAN_AUTHORITY",
                    f"{field} may not be assigned to automation",
                    path,
                )
            )

    allowed_dispositions = {
        str(value)
        for value in charter.get("allowed_dispositions", [])
        if str(value)
    }
    for value, path in (
        (
            str(mar.get("proposed_disposition", "")),
            "$.material_assurance_record.proposed_disposition",
        ),
        (
            str(passport.get("disposition", "")),
            "$.decision_passport.disposition",
        ),
    ):
        if value and value not in allowed_dispositions:
            findings.append(
                ValidationFinding(
                    "DISPOSITION_NOT_ALLOWED",
                    f"disposition {value} is not allowed by the Decision Charter",
                    path,
                )
            )

    triggered = [
        condition
        for condition in mar.get("critical_conditions", [])
        if condition.get("triggered")
    ]
    dispositions = {
        str(mar.get("proposed_disposition", "")),
        str(passport.get("disposition", "")),
    }
    if triggered and dispositions.intersection({"ADVANCE", "PARTNER"}):
        findings.append(
            ValidationFinding(
                "CRITICAL_CONDITION",
                "triggered critical conditions block ADVANCE and PARTNER",
                "$.decision_passport.disposition",
            )
        )

    visible_condition_ids = _identifier_set(
        passport.get("critical_conditions", []),
        _CONDITION_ID,
    )
    for condition in triggered:
        condition_id = str(condition.get("condition_id", ""))
        if condition_id and condition_id not in visible_condition_ids:
            findings.append(
                ValidationFinding(
                    "CRITICAL_CONDITION_VISIBILITY",
                    f"triggered critical condition {condition_id} is not visible "
                    "by exact identifier in the Decision Passport",
                    "$.decision_passport.critical_conditions",
                )
            )

    evidence = mar.get("evidence_records", [])
    posture = passport.get("evidence_posture", {})
    mapping = {
        "UNKNOWN": "unknown",
        "PARTIALLY_SUPPORTED": "unknown",
        "CONTRADICTED": "contradicted",
        "UNSUPPORTED": "unsupported",
        "EXPIRED": "expired",
    }

    posture_ids = {
        bucket: _identifier_set(values, _EVIDENCE_ID)
        for bucket, values in posture.items()
    }

    seen_buckets: dict[str, set[str]] = {}
    for bucket, identifiers in posture_ids.items():
        for identifier in identifiers:
            seen_buckets.setdefault(identifier, set()).add(bucket)
    for evidence_id, buckets in sorted(seen_buckets.items()):
        if len(buckets) > 1:
            findings.append(
                ValidationFinding(
                    "POSTURE_CONFLICT",
                    f"evidence {evidence_id} appears in incompatible posture "
                    f"buckets: {', '.join(sorted(buckets))}",
                    "$.decision_passport.evidence_posture",
                )
            )

    requirement_id_values = [
        str(item.get("requirement_id", ""))
        for collection in (
            charter.get("requirements", []),
            charter.get("acceptance_criteria", []),
        )
        for item in collection
        if str(item.get("requirement_id", ""))
    ]
    duplicate_requirement_ids = sorted(
        identifier
        for identifier, count in Counter(requirement_id_values).items()
        if count > 1
    )
    for identifier in duplicate_requirement_ids:
        findings.append(
            ValidationFinding(
                "DUPLICATE_REQUIREMENT_ID",
                f"Decision Charter requirement identifier {identifier} is duplicated",
                "$.decision_charter",
            )
        )
    requirement_ids = set(requirement_id_values)

    for index, item in enumerate(evidence):
        state = item.get("claim_state")
        bucket = mapping.get(state)
        evidence_id = str(item.get("evidence_id", ""))

        if bucket and evidence_id not in posture_ids.get(bucket, set()):
            findings.append(
                ValidationFinding(
                    "VISIBLE_UNCERTAINTY",
                    f"{state} evidence {evidence_id} is not visible by exact "
                    "identifier in Decision Passport posture",
                    f"$.decision_passport.evidence_posture.{bucket}",
                )
            )

        for link_index, requirement_id in enumerate(
            item.get("requirement_links", [])
        ):
            if str(requirement_id) not in requirement_ids:
                findings.append(
                    ValidationFinding(
                        "REQUIREMENT_LINK",
                        f"requirement link {requirement_id} does not resolve to "
                        "a Decision Charter requirement or acceptance criterion",
                        "$.material_assurance_record.evidence_records"
                        f"[{index}].requirement_links[{link_index}]",
                    )
                )

        issued = _parse_date(item.get("date_issued"))
        accessed = _parse_date(item.get("date_accessed"))
        if issued is not None and accessed is not None and issued > accessed:
            findings.append(
                ValidationFinding(
                    "EVIDENCE_DATE_ORDER",
                    f"evidence {evidence_id} date_issued must not be later than "
                    "date_accessed",
                    "$.material_assurance_record.evidence_records"
                    f"[{index}].date_accessed",
                )
            )

    governing = [
        weak_link
        for weak_link in mar.get("weak_links", [])
        if weak_link.get("governing")
    ]
    if len(governing) != 1:
        findings.append(
            ValidationFinding(
                "WEAK_LINK",
                "exactly one governing weak link is required",
                "$.material_assurance_record.weak_links",
            )
        )

    if passport.get("decision_owner") != charter.get("decision_owner"):
        findings.append(
            ValidationFinding(
                "AUTHORITY_MISMATCH",
                "Decision Passport owner must match Decision Charter owner",
                "$.decision_passport.decision_owner",
            )
        )
    if passport.get("disposition_authority") != charter.get(
        "disposition_authority"
    ):
        findings.append(
            ValidationFinding(
                "AUTHORITY_MISMATCH",
                "Decision Passport authority must match Decision Charter authority",
                "$.decision_passport.disposition_authority",
            )
        )
    if passport.get("disposition") != mar.get("proposed_disposition"):
        findings.append(
            ValidationFinding(
                "DISPOSITION_MISMATCH",
                "MAR and Decision Passport dispositions must match",
                "$.decision_passport.disposition",
            )
        )
    if passport.get("decision_id") != case.get("case_id"):
        findings.append(
            ValidationFinding(
                "DECISION_IDENTITY",
                "Decision Passport decision_id must equal the top-level case_id",
                "$.decision_passport.decision_id",
            )
        )

    evidence_ids = {item.get("evidence_id") for item in evidence}
    source_ids = set(case.get("provenance", {}).get("source_record_ids", []))
    if evidence_ids != source_ids:
        findings.append(
            ValidationFinding(
                "PROVENANCE",
                "provenance source_record_ids must exactly match MAR evidence IDs",
                "$.provenance.source_record_ids",
            )
        )

    if public or case.get("public_safe"):
        if not case.get("synthetic") or (
            case.get("maturity") != "SYNTHETIC_PUBLIC_REFERENCE"
        ):
            findings.append(
                ValidationFinding(
                    "PUBLIC_BOUNDARY",
                    "public-safe cases must be synthetic public references",
                    "$",
                )
            )
        for message in scan_public_boundary(case):
            findings.append(
                ValidationFinding("PUBLIC_BOUNDARY", message, "$")
            )
        supplier = str(mar.get("supplier", {}).get("label", "")).lower()
        facility = str(mar.get("facility", {}).get("label", "")).lower()
        if "fictional" not in supplier or "fictional" not in facility:
            findings.append(
                ValidationFinding(
                    "PUBLIC_BOUNDARY",
                    "public supplier and facility labels must be visibly fictional",
                    "$.material_assurance_record",
                )
            )

    return findings


def validate_case(
    case: dict[str, Any],
    *,
    public: bool = False,
) -> ValidationResult:
    findings = _schema_findings(case)
    if not findings:
        findings.extend(_semantic_findings(case, public))
    return ValidationResult(tuple(findings))
