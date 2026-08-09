from __future__ import annotations

from typing import Any


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None recorded"


def render_decision_passport(case: dict[str, Any]) -> str:
    passport = case["decision_passport"]
    charter = case["decision_charter"]
    posture = passport["evidence_posture"]
    critical = passport["critical_conditions"]
    options = passport["options"]
    lines = [
        f"# {case['title']}: Decision Passport",
        "",
        f"**Case:** `{case['case_id']}`  ",
        f"**Disposition:** `{passport['disposition']}`  ",
        f"**Decision owner:** {passport['decision_owner']}  ",
        f"**Disposition authority:** {passport['disposition_authority']}  ",
        f"**Decision deadline:** {charter['decision_deadline']}",
        "",
        "## Decision",
        "",
        charter["decision_statement"],
        "",
        "## Mission Consequence",
        "",
        passport["mission_consequence"],
        "",
        "## Evidence Posture",
        "",
        "### Supported",
        "",
        _bullets(posture["supported"]),
        "",
        "### Unknown",
        "",
        _bullets(posture["unknown"]),
        "",
        "### Contradicted",
        "",
        _bullets(posture["contradicted"]),
        "",
        "### Unsupported",
        "",
        _bullets(posture["unsupported"]),
        "",
        "### Expired",
        "",
        _bullets(posture["expired"]),
        "",
        "## Governing Weak Link",
        "",
        passport["weak_link"],
        "",
        "## Critical Conditions",
        "",
        _bullets(critical),
        "",
        "## Options",
        "",
    ]
    for item in options:
        lines.extend([f"### {item['label']}", "", item["tradeoff"], ""])
    lines.extend([
        "## Recommendation",
        "",
        passport["recommendation"],
        "",
        "## Next Action",
        "",
        passport["next_action"],
        "",
        "## Acceptance Criteria",
        "",
        _bullets(passport["acceptance_criteria"]),
        "",
        "## Proof Requirements",
        "",
        _bullets(passport["proof_requirements"]),
        "",
        "## Success Signal",
        "",
        passport["success_signal"],
        "",
        "## Stop Rule",
        "",
        passport["stop_rule"],
        "",
        "## Reassessment Trigger",
        "",
        passport["reassessment_trigger"],
        "",
        "## Limitations",
        "",
        _bullets(passport["limitations"]),
        "",
        "---",
        "",
        "This record is decision support, not certification, qualification, legal advice, operational authorization, or a guarantee of performance.",
        "",
    ])
    return "\n".join(lines)
