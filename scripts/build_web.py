from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
GA001 = ROOT / "public-snapshots/gallium/GA-001"
FIELD = ROOT / "public-snapshots/materials-field/MF-001"
YIG001 = ROOT / "public-snapshots/material-systems/YIG-001"
SELECTED_PATHWAYS = WEB / "selected-pathways.json"
SELECTED_PATHWAYS_SCHEMA = WEB / "selected-pathways.schema.json"

sys.path.insert(0, str(ROOT / "scripts"))
from generate_atlas_layout import derive_positions, coordinate_digest  # noqa: E402

USGS_SET = {
    "Aluminum","Antimony","Arsenic","Barite","Beryllium","Bismuth","Boron","Cerium","Cesium",
    "Chromium","Cobalt","Copper","Dysprosium","Erbium","Europium","Fluorspar","Gadolinium",
    "Gallium","Germanium","Graphite","Hafnium","Holmium","Indium","Iridium","Lanthanum","Lead",
    "Lithium","Lutetium","Magnesium","Manganese","Metallurgical Coal","Neodymium","Nickel",
    "Niobium","Palladium","Phosphate","Platinum","Potash","Praseodymium","Rhenium","Rhodium",
    "Rubidium","Ruthenium","Samarium","Scandium","Silicon","Silver","Tantalum","Tellurium",
    "Terbium","Thulium","Tin","Titanium","Tungsten","Uranium","Vanadium","Ytterbium","Yttrium",
    "Zinc","Zirconium",
}
ALLOWED_AUTHORITIES = {"official-government-primary", "bn7-reviewed-public-snapshot", "peer-reviewed-primary"}
ALLOWED_HOSTS = {
    "official-government-primary": {
        "www.usgs.gov","pubs.usgs.gov","www.energy.gov","www.acquisition.gov","acquisition.gov"
    },
    "bn7-reviewed-public-snapshot": {"github.com"},
    "peer-reviewed-primary": {"journals.aps.org", "www.nature.com"},
}
GA_ALLOWED_HOSTS = {"www.usgs.gov", "www.energy.gov"}
ALLOWED_STATES = {"supported", "unknown"}
ALLOWED_REVIEW = {"listed", "reviewed-pathway"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value):
    return html.escape(str(value), quote=True)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def unique(items, key, label):
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        raise SystemExit(f"STOP - duplicate {label}")


def valid_utc_timestamp(value, label):
    if not isinstance(value, str) or "T" not in value or not value.endswith("Z"):
        raise SystemExit(f"STOP - {label} must be an explicit UTC timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit(f"STOP - invalid {label}") from exc
    if dt > datetime.now(timezone.utc).replace(microsecond=0):
        raise SystemExit(f"STOP - {label} is in the future")


def validate_field_sources(register):
    sources = register["sources"]
    unique(sources, "source_id", "source ID")
    by_id = {}
    for source in sources:
        authority = source.get("authority_class")
        if authority not in ALLOWED_AUTHORITIES:
            raise SystemExit("STOP - unapproved source authority")
        parsed = urlparse(source.get("url", ""))
        if parsed.scheme != "https":
            raise SystemExit("STOP - public source must use HTTPS")
        if parsed.hostname not in ALLOWED_HOSTS[authority]:
            raise SystemExit("STOP - source host does not match approved authority")
        valid_utc_timestamp(source.get("verified_at"), f"source verified_at {source['source_id']}")
        by_id[source["source_id"]] = source
    return by_id


def validate_ga(view, snapshot, source_register, rights):
    if snapshot.get("snapshot_id") != "GA-001" or snapshot.get("snapshot_version") != "1.0.0":
        raise SystemExit("STOP - unexpected Gallium snapshot identity")
    if view.get("source_kind") != "public-source-snapshot":
        raise SystemExit("STOP - GA-001 public-view source kind changed")
    if view.get("decision_authority") != "human" or snapshot.get("human_authority_required") is not True:
        raise SystemExit("STOP - human authority changed")
    if rights.get("rights_posture") != "metadata-and-original-paraphrase-only":
        raise SystemExit("STOP - GA-001 rights posture changed")
    if rights.get("approved_for_public_repository") is not True:
        raise SystemExit("STOP - GA-001 public rights approval changed")

    ga_sources = source_register["sources"]
    unique(ga_sources, "source_id", "GA-001 source ID")
    ga_source_by = {}
    for source in ga_sources:
        if source.get("authority") != "official-government":
            raise SystemExit("STOP - GA-001 source authority changed")
        parsed = urlparse(source.get("url", ""))
        if parsed.scheme != "https" or parsed.hostname not in GA_ALLOWED_HOSTS:
            raise SystemExit("STOP - GA-001 source host/scheme changed")
        ga_source_by[source["source_id"]] = source

    claims = snapshot["claims"]
    unique(claims, "claim_id", "GA-001 claim ID")
    claim_by = {claim["claim_id"]: claim for claim in claims}
    for claim in claims:
        if claim.get("support_state") not in ALLOWED_STATES:
            raise SystemExit("STOP - invalid GA-001 claim state")
        source_ids = claim.get("source_ids", [])
        if not source_ids or any(source_id not in ga_source_by for source_id in source_ids):
            raise SystemExit("STOP - unresolved GA-001 claim source")

    support = view["support_items"]
    unique(support, "id", "GA-001 support ID")
    for item in support:
        if item["id"] not in claim_by:
            raise SystemExit("STOP - support item lacks basis claim")
        if item.get("support_state") != claim_by[item["id"]].get("support_state"):
            raise SystemExit("STOP - public support state disagrees with claim")

    interpretations = snapshot["bounded_interpretations"]
    unique(interpretations, "interpretation_id", "GA-001 interpretation ID")
    for interpretation in interpretations:
        if interpretation.get("state") not in ALLOWED_STATES:
            raise SystemExit("STOP - invalid interpretation state")
        basis = interpretation.get("basis_claim_ids", [])
        if not basis or any(claim_id not in claim_by for claim_id in basis):
            raise SystemExit("STOP - interpretation has unresolved basis claim")

    nodes = view.get("trace_nodes")
    if not isinstance(nodes, list) or not nodes:
        raise SystemExit("STOP - GA MPI pathway stages are missing")
    unique(nodes, "id", "trace node ID")
    for node in nodes:
        if node.get("state") not in ALLOWED_STATES:
            raise SystemExit("STOP - invalid trace state")
    if not any(node["state"] == "unknown" for node in nodes):
        raise SystemExit("STOP - Evidence Horizon missing")
    return claim_by, ga_source_by


MPI_HUMAN_BOUNDARY = (
    "Human decision authority remains required. This presentation organizes "
    "public evidence and unresolved proof; it does not approve, qualify, "
    "certify, select, waive, terminate, or close a consequential decision."
)
MPI_NO_CONSTRAINT = (
    "No canonical governing constraint is established in this public record. "
    "The first unresolved link is shown separately as the Evidence Horizon."
)
MPI_ACTION_COPY = {
    "monitor": (
        "Keep the evidence state visible and reassess when material "
        "conditions change."
    ),
    "validate": (
        "Target the first unresolved link with a defined proof request "
        "before advancing the pathway."
    ),
    "support": (
        "Direct bounded support toward evidence or capability that closes "
        "a named pathway gap without implying qualification."
    ),
}
MPI_PROHIBITED_PRESENTATION_PATTERNS = (
    re.compile(r"(?i)\b(?:pathway|readiness|confidence)\s+(?:score|rating)\b"),
    re.compile(r"(?i)\b\d+(?:\.\d+)?%\s+(?:pathway\s+)?confidence\b"),
    re.compile(r"(?i)\btop[- ]ranked\b"),
)


def derive_governing_constraint(weak_links):
    governing = [item for item in weak_links if item.get("governing") is True]
    if len(governing) > 1:
        raise SystemExit("STOP - multiple governing constraints are ambiguous")
    if not governing:
        return {"status": "not-established", "statement": MPI_NO_CONSTRAINT}
    item = governing[0]
    return {
        "status": "explicit",
        "constraint_id": item.get("weak_link_id", ""),
        "statement": item.get("statement", ""),
    }


def _validate_mpi_copy(*values):
    text = " ".join(str(value) for value in values)
    for pattern in MPI_PROHIBITED_PRESENTATION_PATTERNS:
        if pattern.search(text):
            raise SystemExit("STOP - scoring or ranking language in MPI presentation")


def derive_ga_mpi_view(selected, material, view, snapshot, source_register):
    if selected.get("record_id") != "GA-001":
        raise SystemExit("STOP - GA MPI record identity changed")
    if selected.get("type_label") != "CRITICAL MINERAL · REVIEWED PATHWAY":
        raise SystemExit("STOP - GA MPI pathway classification changed")
    if material.get("id") != "gallium" or material.get("name") != "Gallium":
        raise SystemExit("STOP - GA MPI material identity changed")
    if material.get("review", {}).get("snapshot_id") != "GA-001":
        raise SystemExit("STOP - GA MPI review identity changed")
    if snapshot.get("public_maturity") != "M0":
        raise SystemExit("STOP - GA MPI public maturity changed")
    if view.get("decision_authority") != "human":
        raise SystemExit("STOP - GA MPI human authority changed")

    source_ids = {source["source_id"] for source in source_register["sources"]}
    for claim in snapshot["claims"]:
        if not claim.get("source_ids") or any(
            source_id not in source_ids for source_id in claim["source_ids"]
        ):
            raise SystemExit("STOP - GA MPI claim provenance is unresolved")

    nodes = view.get("trace_nodes")
    if not isinstance(nodes, list) or not nodes:
        raise SystemExit("STOP - GA MPI pathway stages are missing")
    first_unknown = next(
        (index for index, node in enumerate(nodes) if node.get("state") == "unknown"),
        None,
    )
    if first_unknown is None:
        raise SystemExit("STOP - GA MPI Evidence Horizon is not established")
    stages = []
    for index, node in enumerate(nodes):
        if index < first_unknown and node.get("state") != "supported":
            raise SystemExit("STOP - unsupported GA MPI continuity before horizon")
        continuity = (
            "continuous"
            if index < first_unknown
            else "horizon" if index == first_unknown else "post-horizon-context"
        )
        stages.append({**node, "display_state": node["state"], "continuity": continuity})

    supported = [
        item for item in snapshot["bounded_interpretations"]
        if item.get("state") == "supported"
    ]
    unknown = [
        item for item in snapshot["bounded_interpretations"]
        if item.get("state") == "unknown"
    ]
    actions = []
    for index, action in enumerate(view["action_options"]):
        if action not in MPI_ACTION_COPY:
            raise SystemExit("STOP - unsupported GA MPI action option")
        actions.append(
            {
                "item_id": f"ga-next-{index + 1}",
                "label": action.title(),
                "statement": MPI_ACTION_COPY[action],
            }
        )

    result = {
        "identity": {
            "record_id": snapshot["snapshot_id"],
            "record_version": snapshot["snapshot_version"],
            "subject_name": material["name"],
            "symbol": material["symbol"],
            "type_label": selected["type_label"],
            "maturity": snapshot["public_maturity"],
        },
        "stages": stages,
        "supported_labels": [stage["label"] for stage in stages if stage["continuity"] == "continuous"],
        "horizon": {
            "status": "established",
            "stage_id": stages[first_unknown]["id"],
            "label": stages[first_unknown]["label"],
        },
        "constraint": derive_governing_constraint([]),
        "posture": {"supported": supported, "context": [], "unknown": unknown},
        "posture_label": "Supported and unknown remain separate.",
        "next_proof": actions,
        "human_boundary": MPI_HUMAN_BOUNDARY,
        "limitations": list(view["limitations"]),
    }
    _validate_mpi_copy(
        result["identity"], result["supported_labels"], result["horizon"],
        result["constraint"], result["posture_label"], result["human_boundary"],
    )
    return result


def derive_yig_mpi_view(selected, form, pathway, source_by):
    if selected.get("record_id") != "YIG-001":
        raise SystemExit("STOP - YIG MPI record identity changed")
    if selected.get("type_label") != "ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT":
        raise SystemExit("STOP - YIG MPI pathway classification changed")
    if form.get("id") != "yig" or form.get("kind") != "engineered-material-system":
        raise SystemExit("STOP - YIG MPI material-system identity changed")
    if pathway.get("official_critical_mineral") is not False:
        raise SystemExit("STOP - YIG MPI may not classify YIG as a critical mineral")
    if pathway.get("public_maturity") != "M0":
        raise SystemExit("STOP - YIG MPI public maturity changed")
    if pathway.get("human_authority_required") is not True:
        raise SystemExit("STOP - YIG MPI human authority changed")

    stages = pathway.get("stages")
    horizon = pathway.get("evidence_horizon")
    if not isinstance(stages, list) or not stages or not isinstance(horizon, dict):
        raise SystemExit("STOP - YIG MPI pathway stages or horizon are missing")
    horizon_id = horizon.get("first_unresolved_stage_id")
    horizon_index = next(
        (index for index, stage in enumerate(stages) if stage.get("id") == horizon_id),
        None,
    )
    if horizon_index is None or stages[horizon_index].get("state") != "unknown":
        raise SystemExit("STOP - YIG MPI Evidence Horizon is invalid")

    normalized = []
    for index, stage in enumerate(stages):
        state = stage.get("state")
        if index < horizon_index and state != "supported":
            raise SystemExit("STOP - unsupported YIG MPI continuity before horizon")
        positive_sources = stage.get("source_ids", [])
        context_sources = stage.get("context_source_ids", [])
        if any(source_id not in source_by for source_id in positive_sources + context_sources):
            raise SystemExit("STOP - YIG MPI stage provenance is unresolved")
        if state in {"supported", "supported-context"} and not positive_sources:
            raise SystemExit("STOP - YIG MPI supported stage lacks positive provenance")
        if state == "unknown" and positive_sources:
            raise SystemExit("STOP - YIG MPI unknown stage cites positive proof")
        continuity = (
            "continuous"
            if index < horizon_index
            else "horizon" if index == horizon_index else "post-horizon-context"
        )
        display_state = "context" if state == "supported-context" else state
        normalized.append(
            {**stage, "display_state": display_state, "continuity": continuity}
        )

    result = {
        "identity": {
            "record_id": pathway["pathway_id"],
            "record_version": pathway["pathway_version"],
            "subject_name": pathway["material_system"],
            "symbol": pathway["symbol"],
            "formula": pathway["formula"],
            "type_label": selected["type_label"],
            "maturity": pathway["public_maturity"],
        },
        "stages": normalized,
        "supported_labels": [stage["stage"] for stage in normalized if stage["continuity"] == "continuous"],
        "horizon": {
            "status": "established",
            "stage_id": horizon_id,
            "label": stages[horizon_index]["stage"],
            "meaning": pathway["evidence_horizon"]["meaning"],
        },
        "constraint": derive_governing_constraint([]),
        "posture": {
            "supported": [stage for stage in normalized if stage["display_state"] == "supported"],
            "context": [stage for stage in normalized if stage["display_state"] == "context"],
            "unknown": [stage for stage in normalized if stage["display_state"] == "unknown"],
        },
        "posture_label": "Supported, supported context, and unknown remain separate.",
        "next_proof": [
            {"item_id": f"yig-next-{index + 1}", "statement": statement}
            for index, statement in enumerate(pathway["next_proof"])
        ],
        "human_boundary": MPI_HUMAN_BOUNDARY,
        "limitations": list(pathway["no_claims"]),
    }
    _validate_mpi_copy(
        result["identity"], result["supported_labels"], result["horizon"],
        result["constraint"], result["posture_label"], result["human_boundary"],
    )
    return result


def mpi_summary_html(mpi, *, title_id, links, heading_level=3):
    if heading_level not in {3, 4}:
        raise ValueError("MPI summary heading level must be 3 or 4")
    identity = mpi["identity"]
    formula = f' · {esc(identity["formula"])}' if identity.get("formula") else ""
    supported = (
        " · ".join(esc(label) for label in mpi["supported_labels"])
        or "Continuous supported segment not established"
    )
    link_html = "".join(
        f'<a href="{esc(href)}">{esc(label)} <span aria-hidden="true">→</span></a>'
        for label, href in links
    )
    constraint_html = ""
    if mpi["constraint"]["status"] == "explicit":
        constraint_html = (
            '<div data-mpi-output="governing-constraint"><dt>Governing constraint</dt>'
            f'<dd><strong>Established</strong><span>{esc(mpi["constraint"]["statement"])}</span></dd></div>'
        )
    heading = f"h{heading_level}"
    rendered = (
        f'<section class="mpi-summary" data-mpi-record="{esc(identity["record_id"])}" '
        f'aria-labelledby="{esc(title_id)}">'
        '<header class="mpi-summary-head"><p class="eyebrow">DERIVED FROM REVIEWED PUBLIC EVIDENCE</p>'
        f'<{heading} id="{esc(title_id)}">What evidence establishes</{heading}>'
        '<p>Existing governed evidence is organized here without a score, rank, or automated decision.</p></header>'
        '<dl class="mpi-summary-grid">'
        '<div data-mpi-output="identity"><dt>Pathway identity</dt>'
        f'<dd><strong>{esc(identity["subject_name"])} ({esc(identity["symbol"])}){formula}</strong>'
        f'<span>{esc(identity["type_label"])} · {esc(identity["record_id"])} v{esc(identity["record_version"])} · {esc(identity["maturity"])}</span></dd></div>'
        '<div data-mpi-output="supported-segment"><dt>Evidence supported through</dt>'
        f'<dd><strong>{supported}</strong><span>Continuous public evidence before the first unresolved link.</span></dd></div>'
        '<div data-mpi-output="evidence-horizon"><dt>Evidence Horizon · First unresolved link</dt>'
        f'<dd><strong>{esc(mpi["horizon"]["label"])}</strong><span>Later context does not reconnect the pathway.</span></dd></div>'
        f'{constraint_html}'
        '<div data-mpi-output="evidence-posture"><dt>Evidence status</dt>'
        f'<dd><strong>{esc(mpi["posture_label"])}</strong><span>Inspect the governed stages, claims, and sources below.</span></dd></div>'
        '</dl>'
        f'<nav class="mpi-summary-links" aria-label="{esc(identity["subject_name"])} pathway evidence">{link_html}</nav>'
        f'<aside class="mpi-human-boundary" aria-label="Human decision boundary" data-mpi-output="human-decision-boundary"><strong>Human decision boundary</strong><p>{esc(mpi["human_boundary"])}</p></aside>'
        '</section>'
    )
    _validate_mpi_copy(rendered)
    return rendered


def evidence_boundary_html(
    *,
    title_id,
    heading_level,
    known_html,
    unknown_html,
    horizon_label,
    horizon_meaning,
    mpi_html,
    optional_governed_html="",
):
    """Render the shared Evidence Boundary shell around governed pathway content."""
    if heading_level not in {2, 3}:
        raise ValueError("Evidence Boundary heading level must be 2 or 3")
    heading = f"h{heading_level}"
    return (
        '<div class="evidence-boundary-shell">'
        '<header class="evidence-boundary-head">'
        f'<div><p class="eyebrow">PATHWAY STEP</p><{heading} id="{esc(title_id)}">Evidence Boundary</{heading}></div>'
        '<p>Supported facts stay supported. Unknowns stay visible.</p></header>'
        '<div class="examine-grid evidence-findings">'
        '<article><h3>What We Know</h3><span class="state supported">Supported evidence</span>'
        f'{known_html}</article>'
        '<article><h3>What We Don\'t Know</h3><span class="state unknown">Unknown</span>'
        f'{unknown_html}</article></div>'
        '<div class="evidence-horizon pathway-boundary-horizon">'
        '<span aria-hidden="true"></span><div><small>Evidence Horizon</small>'
        '<strong>First unresolved link</strong>'
        f'<p><span class="boundary-horizon-label">{esc(horizon_label)}</span>{esc(horizon_meaning)}</p>'
        '</div></div>'
        f'{mpi_html}{optional_governed_html}</div>'
    )


def presentation_stage_label(label):
    """Translate governed labels for display without changing governed records."""
    return {
        "Program-specific fabrication path": "Fabrication path for a specific program",
        "Program-specific validation evidence": "Use-specific validation evidence",
        "Program-specific acquisition access": "Program acquisition access",
    }.get(label, label)


def presentation_action_label(label):
    """Translate governed action values for public display only."""
    return {"Support": "Support Next Proof"}.get(label, label)


def presentation_state_label(stage):
    """Translate raw evidence state plus continuity into the shared public grammar."""
    key = (stage.get("continuity"), stage.get("state"))
    labels = {
        ("continuous", "supported"): "Supported evidence",
        ("horizon", "unknown"): "First unresolved link",
        ("post-horizon-context", "supported"): "Later-stage context",
        ("post-horizon-context", "supported-context"): "Later-stage context",
        ("post-horizon-context", "unknown"): "Unresolved question",
    }
    if key not in labels:
        raise SystemExit(
            "STOP - unsupported evidence state and continuity presentation pair"
        )
    return labels[key]


def pathway_stage_html(
    stage,
    index,
    *,
    title,
    summary=None,
    evidence_basis=None,
    sources_html="",
    variant_class,
):
    """Render one governed stage through the shared pathway presentation grammar."""
    zone = {
        "continuous": "connected",
        "horizon": "horizon",
        "post-horizon-context": "island",
    }[stage["continuity"]]
    presentation_label = presentation_state_label(stage)
    state_key = presentation_label.lower().replace(" ", "-")
    summary_html = (
        f'<p class="pathway-stage-summary">{esc(summary)}</p>' if summary else ""
    )
    basis_html = (
        '<p class="pathway-stage-basis"><strong>Evidence basis:</strong> '
        f'{esc(evidence_basis)}</p>'
        if evidence_basis else ""
    )
    sources = (
        f'<div class="pathway-stage-sources yig-source-links">{sources_html}</div>'
        if sources_html else ""
    )
    return (
        f'<li class="pathway-stage {esc(variant_class)} {zone} state-{esc(stage["state"])}" '
        f'data-stage-id="{esc(stage["id"])}" data-raw-evidence-state="{esc(stage["state"])}" '
        f'data-continuity="{esc(stage["continuity"])}" data-presentation-state="{esc(state_key)}">'
        f'<span class="pathway-stage-number">{index + 1:02d}</span>'
        '<div class="pathway-stage-body">'
        f'<small class="pathway-stage-state">{esc(presentation_label)}</small>'
        f'<strong class="pathway-stage-title">{esc(title)}</strong>'
        f'{summary_html}{basis_html}{sources}</div></li>'
    )


def pathway_ribbon_html(mpi, *, section_id, title_id, trace_href):
    state_labels = {
        "continuous": "Supported evidence",
        "horizon": "First unresolved link",
        "post-horizon-context": "Later-stage context",
    }
    groups = []
    for continuity in ("continuous", "horizon", "post-horizon-context"):
        stage_items = "".join(
            f'<li><strong>{esc(presentation_stage_label(stage.get("label") or stage["stage"]))}</strong></li>'
            for stage in mpi["stages"] if stage["continuity"] == continuity
        )
        if stage_items:
            groups.append(
                f'<li class="ribbon-{esc(continuity)}">'
                f'<span>{esc(state_labels[continuity])}</span>'
                f'<ul>{stage_items}</ul></li>'
            )
    return (
        f'<section id="{esc(section_id)}" class="pathway-glance" aria-labelledby="{esc(title_id)}">'
        f'<header><p class="eyebrow">PATHWAY AT A GLANCE</p><h3 id="{esc(title_id)}">Pathway Overview</h3>'
        '<p>The first unresolved link marks the evidence boundary. Later-stage context remains separate.</p></header>'
        f'<ol class="pathway-ribbon">{"".join(groups)}</ol>'
        f'<a class="pathway-next" href="{esc(trace_href)}">Trace to Mission <span aria-hidden="true">→</span></a>'
        '</section>'
    )


def project():
    atlas = load(FIELD / "atlas.json")
    applications = load(FIELD / "doe-application-map.json")
    forms = load(FIELD / "public-forms.json")["forms"]
    field_sources = load(FIELD / "source-register.json")
    yig_pathway = load(YIG001 / "pathway.json")
    selected_registry = load(SELECTED_PATHWAYS)
    selected_schema = load(SELECTED_PATHWAYS_SCHEMA)
    errors = sorted(Draft202012Validator(selected_schema).iter_errors(selected_registry), key=lambda error: list(error.path))
    if errors:
        raise SystemExit(f"STOP - invalid selected-pathways registry: {errors[0].message}")

    view = load(GA001 / "public-view.json")
    snapshot = load(GA001 / "snapshot.json")
    ga_sources = load(GA001 / "source-register.json")
    rights = load(GA001 / "rights.json")

    field_source_by = validate_field_sources(field_sources)
    validate_ga(view, snapshot, ga_sources, rights)
    valid_utc_timestamp(atlas.get("reviewed_at"), "MF-001 reviewed_at")

    materials = atlas["materials"]
    unique(materials, "id", "material ID")
    unique(materials, "name", "material name")
    unique(materials, "symbol", "material symbol")
    names = {material["name"] for material in materials}
    if names != USGS_SET or len(materials) != 60:
        raise SystemExit("STOP - Atlas is not the exact USGS 2025 60-mineral field")
    if sum(1 for material in materials if material.get("rare_earth")) != 15:
        raise SystemExit("STOP - rare-earth count differs from 15")

    reviewed = []
    for material in materials:
        code = material["review"]["code"]
        if code not in ALLOWED_REVIEW:
            raise SystemExit("STOP - invalid review state")
        if code == "reviewed-pathway":
            reviewed.append(material)
        for context in material.get("context", []):
            if context["source_id"] not in field_source_by:
                raise SystemExit("STOP - unresolved material context source")
    if [(m["name"], m["review"].get("snapshot_id")) for m in reviewed] != [("Gallium", "GA-001")]:
        raise SystemExit("STOP - reviewed-pathway scope differs from released Gallium snapshot")

    rows = applications["rows"]
    for lens in atlas["lenses"].values():
        if any(row_id not in rows for row_id in lens["doe_rows"]):
            raise SystemExit("STOP - lens references undefined DOE row")

    unique(forms, "id", "public form ID")
    unique(forms, "symbol", "public form symbol")
    for form in forms:
        relationships = form.get("relationships", [])
        if not relationships or any(rel["mineral"] not in names for rel in relationships):
            raise SystemExit("STOP - public form relationship unresolved")
        if any(source_id not in field_source_by for source_id in form.get("source_ids", [])):
            raise SystemExit("STOP - public form source unresolved")

    yig = next((form for form in forms if form["id"] == "yig"), None)
    ggg = next((form for form in forms if form["id"] == "ggg"), None)
    if yig is None or ggg is None:
        raise SystemExit("STOP - required YIG/GGG public material-system context missing")
    if yig.get("kind") != "engineered-material-system":
        raise SystemExit("STOP - YIG classification changed")
    if yig.get("formula") != "Y3Fe5O12":
        raise SystemExit("STOP - YIG formula changed")
    if yig.get("primary_example") is not True:
        raise SystemExit("STOP - YIG primary-example contract changed")
    if yig_pathway.get("classification") != "engineered-material-system":
        raise SystemExit("STOP - YIG pathway classification changed")
    if yig_pathway.get("official_critical_mineral") is not False:
        raise SystemExit("STOP - YIG must not be labeled an official critical mineral")
    if yig_pathway.get("human_authority_required") is not True:
        raise SystemExit("STOP - YIG human-authority boundary changed")
    stage_ids = {stage["id"] for stage in yig_pathway["stages"]}
    if yig_pathway["evidence_horizon"]["first_unresolved_stage_id"] not in stage_ids:
        raise SystemExit("STOP - YIG Evidence Horizon does not resolve to a stage")
    for stage in yig_pathway["stages"]:
        if stage["state"] not in {"supported", "supported-context", "unknown"}:
            raise SystemExit("STOP - invalid YIG pathway state")
        source_ids = stage.get("source_ids", [])
        context_source_ids = stage.get("context_source_ids", [])
        if any(source_id not in field_source_by for source_id in source_ids + context_source_ids):
            raise SystemExit("STOP - unresolved YIG pathway source")
        if stage["state"] == "unknown":
            if source_ids:
                raise SystemExit("STOP - unknown YIG stage must not cite a source as proof of absence")
            if not stage.get("evidence_basis"):
                raise SystemExit("STOP - unknown YIG stage requires explicit reviewed-corpus evidence basis")
        elif not source_ids:
            raise SystemExit("STOP - supported YIG context requires positive source lineage")

    for context in yig_pathway.get("frontier_research_context", []):
        if not context.get("source_ids") or any(source_id not in field_source_by for source_id in context["source_ids"]):
            raise SystemExit("STOP - unresolved YIG frontier-research source")

    selected_pathways = []
    selected_ids = set()
    for entry in selected_registry["pathways"]:
        record_id = entry["record_id"]
        if record_id in selected_ids:
            raise SystemExit("STOP - duplicate selected pathway record ID")
        selected_ids.add(record_id)
        item = dict(entry)
        if entry["record_type"] == "critical-mineral-reviewed-pathway":
            material = next((candidate for candidate in reviewed if candidate["id"] == entry["source_id"]), None)
            if material is None or material["review"].get("snapshot_id") != record_id:
                raise SystemExit("STOP - selected critical-mineral pathway does not resolve to reviewed evidence")
            item.update(name=material["name"], symbol=material["symbol"])
        else:
            form = next((candidate for candidate in forms if candidate["id"] == entry["source_id"]), None)
            if form is None or form.get("pathway_id") != record_id:
                raise SystemExit("STOP - selected material-system pathway does not resolve to controlled context")
            if form.get("kind") != "engineered-material-system" or yig_pathway.get("pathway_id") != record_id:
                raise SystemExit("STOP - selected material-system pathway classification changed")
            item.update(name=form["name"], symbol=form["symbol"])
        selected_pathways.append(item)

    ga_selected = next(
        item for item in selected_pathways if item["record_id"] == "GA-001"
    )
    yig_selected = next(
        item for item in selected_pathways if item["record_id"] == "YIG-001"
    )
    ga_mpi = derive_ga_mpi_view(
        ga_selected,
        reviewed[0],
        view,
        snapshot,
        ga_sources,
    )
    yig_mpi = derive_yig_mpi_view(
        yig_selected,
        yig,
        yig_pathway,
        field_source_by,
    )

    positions, exact_rows, lens_members = derive_positions(atlas, applications)
    enriched = []
    for material in materials:
        item = dict(material)
        item["position"] = positions[material["name"]]
        item["doe_rows"] = exact_rows[material["name"]]
        item["lenses"] = lens_members[material["name"]]
        item["lens_labels"] = [atlas["lenses"][lens_id]["short"] for lens_id in item["lenses"]]
        source_ids = [atlas["official_field"]["source_id"]]
        if item["doe_rows"]:
            source_ids.append("DOE-CMM-APPLICATIONS")
        source_ids.extend(context["source_id"] for context in item.get("context", []))
        if item["id"] == "gallium":
            source_ids.extend(["DOE-TRACE-GA-2026", "GA-001"])
        item["source_ids"] = list(dict.fromkeys(source_ids))
        enriched.append(item)

    atlas = dict(atlas)
    atlas["materials"] = enriched
    atlas["layout"] = dict(atlas["layout"])
    atlas["layout"]["coordinate_set_sha256"] = coordinate_digest(atlas, applications)

    return {
        "atlas": atlas,
        "forms": forms,
        "sources": field_sources["sources"],
        "yig001": yig_pathway,
        "mpi": {"ga001": ga_mpi, "yig001": yig_mpi},
        "selected_pathways": selected_pathways,
        "ga001": {
            "view": view,
            "snapshot": snapshot,
            "sources": ga_sources,
            "rights": {"rights_posture": rights["rights_posture"]},
        },
    }


def detail_html(material, forms, sources, sheet=False):
    source_by = {source["source_id"]: source for source in sources}
    related = [
        form for form in forms
        if any(rel["mineral"] == material["name"] for rel in form["relationships"])
    ]
    if material["lens_labels"]:
        chips = "".join(f"<span>{esc(label)}</span>" for label in material["lens_labels"])
    else:
        chips = "<span>No DOE application row mapped in this controlled snapshot.</span>"
    if related:
        form_html = "".join(
            f'<button type="button" class="form-chip" data-form-id="{esc(form["id"])}">'
            f'{esc(form["symbol"])} · {esc(form["name"])}</button>'
            for form in related
        )
    else:
        form_html = "<span>No public material system linked in this release.</span>"
    contexts = "".join(
        f'<span><b>{esc(context["label"])}</b><br>{esc(context["detail"])}</span>'
        for context in material.get("context", [])
    )
    source_html = "".join(
        f'<a href="{esc(source_by[source_id]["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(source_id)} ↗</a>'
        for source_id in material["source_ids"]
        if source_id in source_by
    )
    title_id = ' id="sheetTitle"' if sheet else ""
    rare = "RARE EARTH · " if material["rare_earth"] else ""
    action = (
        '<a class="detail-action" href="#ga-pathway" data-depth="trace">Reviewed pathway available →</a>'
        if material["review"]["code"] == "reviewed-pathway"
        else ""
    )
    context_section = (
        '<section><span class="detail-label">Policy context</span>'
        f'<div class="context-list">{contexts}</div></section>'
        if contexts else ""
    )
    return (
        '<div class="material-detail">'
        '<div class="detail-title">'
        f'<span class="big-symbol">{esc(material["symbol"])}</span>'
        '<div>'
        f'<p class="eyebrow">{rare}USGS 2025</p>'
        f'<h2{title_id}>{esc(material["name"])}</h2>'
        f'<p>{esc(material["official_designation"])}</p>'
        '</div></div>'
        '<section><span class="detail-label">Where it is used</span>'
        f'<div class="chips">{chips}</div></section>'
        '<section><span class="detail-label">Evidence review</span>'
        f'<strong class="review-state review-{esc(material["review"]["code"])}">'
        f'{esc(material["review"]["label"])}</strong></section>'
        f'{context_section}'
        '<section><span class="detail-label">Related Material Systems</span>'
        f'<div class="chips">{form_html}</div></section>'
        '<section><span class="detail-label">Sources & provenance</span>'
        f'<div class="source-links">{source_html}</div></section>'
        f'{action}</div>'
    )


def pathway_trace_html(items_html, *, aria_label, base_class, element_id=None):
    """Render the shared presentation rail without changing governed stage content."""
    id_attribute = f' id="{esc(element_id)}"' if element_id else ""
    return (
        f'<ol{id_attribute} class="{esc(base_class)} pathway-trace-sequence" '
        f'aria-label="{esc(aria_label)}" tabindex="0">{items_html}</ol>'
    )


def render(template, payload):
    atlas = payload["atlas"]
    forms = payload["forms"]
    sources = payload["sources"]
    view = payload["ga001"]["view"]
    snapshot = payload["ga001"]["snapshot"]
    ga_source_register = payload["ga001"]["sources"]
    ga_sources = ga_source_register["sources"]
    ga_source_by = {source["source_id"]: source for source in ga_sources}
    yig_pathway = payload["yig001"]
    ga_mpi = payload["mpi"]["ga001"]
    yig_mpi = payload["mpi"]["yig001"]
    selected_pathways = payload["selected_pathways"]

    mpi_by_record = {
        ga_mpi["identity"]["record_id"]: ga_mpi,
        yig_mpi["identity"]["record_id"]: yig_mpi,
    }
    preview_contracts = {
        "GA-001": {
            "supported_labels": ("Gallium (Ga)",),
            "horizon": "Qualified domestic primary recovery at mission-relevant scale",
            "insight": "Public evidence is continuous through Gallium; qualified domestic primary recovery remains unresolved.",
        },
        "YIG-001": {
            "supported_labels": ("Critical Materials",),
            "horizon": "Qualified Material Stack",
            "insight": "Public evidence is continuous through critical materials; a qualified material stack remains unresolved.",
        },
    }
    for record_id, contract in preview_contracts.items():
        mpi = mpi_by_record.get(record_id)
        if (
            mpi is None
            or tuple(mpi["supported_labels"]) != contract["supported_labels"]
            or mpi["horizon"]["label"] != contract["horizon"]
        ):
            raise SystemExit(f"STOP - {record_id} pathway preview copy is unsupported")
    selected_pathway_rows = "".join(
        '<article class="selected-pathway-row" data-pathway="' + esc(item["source_id"]) + '">'
        '<header class="selected-pathway-preview-head">'
        f'<span class="selected-pathway-symbol{" selected-pathway-symbol-wide" if len(item["symbol"]) > 2 else ""}" aria-hidden="true">{esc(item["symbol"])}</span>'
        '<div class="selected-pathway-identity">'
        f'<span class="selected-pathway-type">{esc(item["type_label"])}</span><h3>{esc(item["name"])}</h3>'
        f'<small>{esc(item["record_id"])} — Experimental public evidence method</small></div></header>'
        '<div class="selected-pathway-signal" aria-hidden="true">'
        + "".join(
            f'<span class="signal-{esc(stage["continuity"])}"></span>'
            for stage in mpi_by_record[item["record_id"]]["stages"]
        )
        + '</div><dl class="selected-pathway-preview-meta">'
        '<div><dt>Evidence supported through</dt><dd>'
        + esc(" · ".join(mpi_by_record[item["record_id"]]["supported_labels"]) or "Not established")
        + '</dd></div><div><dt>Evidence Horizon · First unresolved link</dt><dd>'
        + esc(mpi_by_record[item["record_id"]]["horizon"]["label"])
        + '</dd></div></dl>'
        f'<p class="selected-pathway-insight">{esc(preview_contracts[item["record_id"]]["insight"])}</p>'
        f'<a href="{esc(item["href"])}">{esc(item["action_label"])} <span aria-hidden="true">→</span></a>'
        '</article>'
        for item in selected_pathways
    )
    selected_pathways_html = (
        '<section id="selected-pathways" class="selected-pathways" aria-labelledby="selectedPathwaysTitle">'
        '<header class="selected-pathways-head"><p class="selected-pathways-kicker">PATHWAY PREVIEWS</p>'
        '<h2 id="selectedPathwaysTitle">See how far the evidence carries.</h2>'
        '<p>Two reviewed public examples. Reviewed does not mean qualified.</p></header>'
        '<ul class="selected-pathways-legend" aria-label="Pathway preview legend">'
        '<li class="legend-supported">Supported evidence</li><li class="legend-horizon">First unresolved link</li>'
        '<li class="legend-context">Later-stage context</li></ul>'
        f'<div class="selected-pathway-list">{selected_pathway_rows}</div></section>'
    )

    lens_buttons = "".join(
        f'<button type="button" class="lens" data-lens="{esc(lens_id)}" aria-pressed="false" '
        f'style="--lens-color:{esc(lens["color"])}">{esc(lens["label"])}</button>'
        for lens_id, lens in atlas["lenses"].items()
    )
    zones = "".join(
        f'<div class="zone" data-zone="{esc(lens_id)}" '
        f'style="--zx:{lens["anchor"]["x"]}%;--zy:{lens["anchor"]["y"]}%;--zcolor:{esc(lens["color"])}">'
        f'<i></i><span>{esc(lens["label"])}</span></div>'
        for lens_id, lens in atlas["lenses"].items()
    )
    mineral_nodes = "".join(
        f'<a class="mineral{" rare" if material["rare_earth"] else ""}" '
        f'href="#material-{esc(material["id"])}" data-id="{esc(material["id"])}" '
        f'style="--x:{material["position"]["x"]}%;--y:{material["position"]["y"]}%" '
        f'aria-label="{esc(material["name"])}{", rare earth" if material["rare_earth"] else ""}, USGS 2025 critical mineral"><span>{esc(material["symbol"])}</span></a>'
        for material in atlas["materials"]
    )

    index_rows = []
    for material in atlas["materials"]:
        usage = ", ".join(material["lens_labels"]) or "No DOE application row mapped in this controlled snapshot."
        index_rows.append(
            f'<details id="material-{esc(material["id"])}" class="index-row" data-index-id="{esc(material["id"])}">'
            '<summary>'
            f'<span class="index-symbol">{esc(material["symbol"])}</span>'
            f'<strong>{esc(material["name"])}</strong><span>USGS 2025</span>'
            f'<span>{esc(material["review"]["label"])}</span></summary>'
            '<div>'
            f'<p><b>Where it is used:</b> {esc(usage)}</p>'
            f'<p><b>Source IDs:</b> {esc(", ".join(material["source_ids"]))}</p>'
            '</div></details>'
        )

    trace_nodes = []
    for index, node in enumerate(ga_mpi["stages"]):
        trace_nodes.append(
            pathway_stage_html(
                node,
                index,
                title=presentation_stage_label(node["label"]),
                summary=node["kind"].replace("-", " "),
                variant_class="trace-node",
            )
        )

    supported = "".join(
        f'<li>{esc(item["text"])}</li>'
        for item in ga_mpi["posture"]["supported"]
    )
    unknown = "".join(
        f'<li>{esc(item["text"])}</li>'
        for item in ga_mpi["posture"]["unknown"]
    )

    claim_by = {claim["claim_id"]: claim for claim in snapshot["claims"]}
    def ga_source_ref(source_id):
        if source_id not in ga_source_by:
            raise SystemExit("STOP - unresolved GA-001 claim source during render")
        return (
            f'<a class="ga-source-ref" href="#ga-source-{esc(source_id)}" '
            f'data-ga-source-id="{esc(source_id)}">{esc(source_id)} →</a>'
        )
    ga_claim_items = "".join(
        '<li class="ga-claim">'
        f'<span class="claim-id">{esc(claim["claim_id"])}</span>'
        f'<p>{esc(claim["claim"])}</p>'
        f'<small>{esc(claim["support_state"].title())} · '
        + " ".join(ga_source_ref(source_id) for source_id in claim["source_ids"])
        + '</small></li>'
        for claim in snapshot["claims"]
    )
    support_items = []
    for item in view["support_items"]:
        claim = claim_by[item["id"]]
        support_items.append(
            '<details class="support-item"><summary>'
            f'<strong>{esc(item["id"])} · {esc(item["claim"])}</strong>'
            f'<span class="state {esc(item["support_state"])}">{esc(item["support_state"].title())}</span>'
            '</summary><div class="support-body"><div class="support-meta">'
            f'<div><span>Source label</span><b>{esc(item["source_label"])}</b></div>'
            f'<div><span>Source date</span><b>{esc(item["source_date"] or "Undated")}</b></div>'
            f'<div><span>GA-001 snapshot validation profile</span><b>{esc(view["validation_profile"])}</b></div>'
            '<div><span>Claim source IDs</span><b class="claim-source-links">'
            + " ".join(ga_source_ref(source_id) for source_id in claim["source_ids"])
            + '</b></div>'
            '</div></div></details>'
        )

    actions = "".join(
        f'<article class="action-card"><span>{index + 1:02d}</span>'
        f'<h3>{esc(presentation_action_label(action["label"]))}</h3>'
        f'<p>{esc(action["statement"])}</p>'
        '<small>Evidence-supported option · human decision required</small></article>'
        for index, action in enumerate(ga_mpi["next_proof"])
    )

    material_id_by_name = {material["name"]: material["id"] for material in atlas["materials"]}
    gallium_material = next(material for material in atlas["materials"] if material["id"] == "gallium")
    yig_form = next(form for form in forms if form["id"] == "yig")
    ga_connected_form_ids = {
        form["id"] for form in forms
        if any(relationship["mineral"] == "Gallium" for relationship in form["relationships"])
    }
    yig_connected_symbols = {"YIG"} | {
        context["name"] for context in yig_pathway.get("substrate_context", [])
    }
    yig_connected_form_ids = {
        form["id"] for form in forms if form["symbol"] in yig_connected_symbols
    }
    form_cards = []
    ordered_forms = sorted(forms, key=lambda form: (0 if form.get("primary_example") else 1, form["name"]))
    for form in ordered_forms:
        route_names = " ".join(
            route for route, connected_ids in (
                ("ga", ga_connected_form_ids), ("yig", yig_connected_form_ids)
            ) if form["id"] in connected_ids
        )
        relationships = "".join(
            f'<a href="#material-{esc(material_id_by_name[rel["mineral"]])}">'
            f'{esc(rel["mineral"])}</a>'
            for rel in form["relationships"]
        )
        primary = '<span class="primary-badge">Primary example</span>' if form.get("primary_example") else ""
        review = form.get("review", {}).get("label", "Public Context")
        form_cards.append(
            f'<article id="form-{esc(form["id"])}" class="form-card{" primary-system" if form.get("primary_example") else ""}" '
            f'data-pathway-routes="{esc(route_names)}">'
            f'<span class="form-symbol">{esc(form["symbol"])}</span><div>'
            f'{primary}<h3>{esc(form["name"])}</h3><p>{esc(form["context"])}</p>'
            f'<small class="form-state">{esc(review)}</small>'
            '<span class="detail-label">Related critical minerals</span>'
            f'<div class="relationship-links">{relationships}'
            f'<button type="button" class="js-only" data-form-id="{esc(form["id"])}" aria-label="Open detail: {esc(form["name"])}">Open detail</button>'
            '</div></div></article>'
        )

    yig_stage_cards = []
    for index, stage in enumerate(yig_mpi["stages"]):
        source_links = "".join(
            f'<a href="{esc(next(source["url"] for source in sources if source["source_id"] == source_id))}" '
            f'target="_blank" rel="noopener noreferrer">{esc(source_id)} ↗</a>'
            for source_id in stage.get("source_ids", [])
        )
        context_links = "".join(
            f'<a href="{esc(next(source["url"] for source in sources if source["source_id"] == source_id))}" '
            f'target="_blank" rel="noopener noreferrer">Context · {esc(source_id)} ↗</a>'
            for source_id in stage.get("context_source_ids", [])
        )
        yig_stage_cards.append(
            pathway_stage_html(
                stage,
                index,
                title=stage["stage"],
                summary=stage["summary"],
                evidence_basis=stage.get("evidence_basis"),
                sources_html=source_links + context_links,
                variant_class="yig-stage",
            )
        )

    yig_dependencies = "".join(
        f'<span>{esc(item["mineral"])}<small>{esc(item["role"])}</small></span>'
        for item in yig_pathway["critical_mineral_dependencies"]
    )
    yig_next = "".join(
        f'<li>{esc(item["statement"])}</li>' for item in yig_mpi["next_proof"]
    )
    frontier_context = "".join(
        '<article class="frontier-context-card">'
        f'<span class="detail-label">{esc(item["label"])}</span>'
        f'<p>{esc(item["summary"])}</p>'
        + "".join(
            f'<a href="{esc(next(source["url"] for source in sources if source["source_id"] == source_id))}" '
            f'target="_blank" rel="noopener noreferrer">{esc(source_id)} ↗</a>'
            for source_id in item["source_ids"]
        )
        + '</article>'
        for item in yig_pathway.get("frontier_research_context", [])
    )
    expected_yig_summary = (
        "YIG is a real engineered magnetic garnet used in magnonics and related microwave/spin research. "
        "The public evidence supports technical relevance and multiple laboratory/device demonstrations. "
        "It does not establish a qualified supply chain, repeatable mission-scale manufacturing, "
        "acquisition approval, or mission readiness."
    )
    if yig_pathway.get("public_summary") != expected_yig_summary:
        raise SystemExit("STOP - YIG public orientation copy is unsupported")
    yig_pathway_html = (
        '<div class="yig-identity">'
        '<span class="yig-mark" aria-hidden="true">YIG</span><div><p class="eyebrow">MATERIAL IDENTITY</p>'
        '<h3 aria-label="Chemical formula for yttrium iron garnet: Y three F E five O twelve">Y₃Fe₅O₁₂</h3>'
        '<p>Engineered magnetic material system. Reviewed public context.</p></div></div>'
        '<dl class="yig-orientation yig-orientation-intro" aria-label="Yttrium Iron Garnet introduction">'
        '<div><dt>What it is</dt><dd>YIG is an engineered magnetic material used in magnonics and related microwave and spin research.</dd></div>'
        '<div><dt>Why it matters</dt><dd>YIG shows why an engineered material system cannot be understood from critical-mineral designation alone. Substrate choice, material growth, fabrication, and validation remain distinct parts of the pathway.</dd></div>'
        '</dl>'
        '<a class="pathway-next" href="#yig-overview">Explore the Pathway Overview <span aria-hidden="true">→</span></a>'
        + pathway_ribbon_html(yig_mpi, section_id="yig-overview", title_id="yig-overview-title", trace_href="#yig-trace")
        + '<section id="yig-trace" class="yig-journey-block" aria-labelledby="yig-trace-title">'
        '<header class="journey-block-head"><p class="eyebrow">TRACE</p><h3 id="yig-trace-title">Trace to Mission</h3>'
        '<p>Existing governed relationships show where the public pathway is supported and where continuity stops.</p></header>'
        '<div class="yig-dependencies"><span class="detail-label">Critical-Mineral Dependencies Across Common YIG Stacks</span>'
        '<p class="dependency-note">Yttrium is the YIG critical-mineral constituent. Gadolinium gallium garnet (GGG) and yttrium scandium gallium aluminum garnet (YSGAG) introduce additional critical-mineral dependencies in common or emerging substrate systems.</p>'
        f'<div>{yig_dependencies}</div></div>'
        + pathway_trace_html(
            "".join(yig_stage_cards),
            element_id="yig-stages",
            base_class="yig-stage-grid",
            aria_label="YIG trace to mission pathway",
        )
        + '</section>'
        '<section id="yig-boundary" class="yig-journey-block yig-boundary" aria-labelledby="yig-boundary-title">'
        + evidence_boundary_html(
            title_id="yig-boundary-title",
            heading_level=3,
            known_html=(
                '<p>Public sources support the identified critical-mineral inputs. '
                'Peer-reviewed sources separately document technical relevance and '
                'multiple laboratory and device demonstrations.</p>'
            ),
            unknown_html=(
                '<p>The reviewed public evidence does not establish the required '
                'precursor, purity, processor, substrate lot, and repeatability as one '
                'qualified material stack. It also does not establish mission-scale '
                'manufacturing, acquisition approval, or mission readiness.</p>'
            ),
            horizon_label=yig_mpi["horizon"]["label"],
            horizon_meaning=yig_pathway["evidence_horizon"]["meaning"],
            mpi_html=mpi_summary_html(
                yig_mpi,
                title_id="yig-mpi-title",
                links=(("Consider Next Proof", "#yig-next-proof"),),
                heading_level=4,
            ),
            optional_governed_html=(
                '<div class="boundary-governed-region" '
                'aria-label="YIG governed research context">'
                f'<div class="frontier-context-grid">{frontier_context}</div></div>'
            ),
        )
        + '</section>'
    )

    field_source_ids = {source["source_id"] for source in sources}
    ga_field_source_ids = set(gallium_material["source_ids"]) & field_source_ids
    yig_field_source_ids = set(yig_form.get("source_ids", []))
    for collection_name in (
        "critical_mineral_dependencies", "substrate_context", "stages",
        "public_applications", "frontier_research_context",
    ):
        for item in yig_pathway.get(collection_name, []):
            yig_field_source_ids.update(item.get("source_ids", []))
            yig_field_source_ids.update(item.get("context_source_ids", []))
    source_cards = "".join(
        '<article class="source-card" data-pathway-routes="'
        + esc(" ".join(
            route for route, source_ids in (
                ("ga", ga_field_source_ids), ("yig", yig_field_source_ids)
            ) if source["source_id"] in source_ids
        ))
        + '">'
        f'<span class="source-id">{esc(source["source_id"])}</span>'
        f'<h3>{esc(source["title"])}</h3>'
        f'<p>{esc(source["publisher"])}</p>'
        f'<small>{esc(source.get("source_date") or "Source publication date")} · verified {esc(source["verified_at"])}</small>'
        f'<p>{esc(source["role"])}</p>'
        f'<a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">Open controlled source ↗</a>'
        '</article>'
        for source in sources
    )

    source_claim_ids = {
        source["source_id"]: [
            claim["claim_id"] for claim in snapshot["claims"]
            if source["source_id"] in claim["source_ids"]
        ]
        for source in ga_sources
    }
    ga_source_cards = "".join(
        f'<article id="ga-source-{esc(source["source_id"])}" class="ga-source-card">'
        f'<span class="source-id">{esc(source["source_id"])}</span>'
        f'<h4>{esc(source["title"])}</h4>'
        f'<p>{esc(source["publisher"])}</p>'
        f'<small>{esc(source.get("source_date") or "Undated source page")} · accessed {esc(source["accessed_date"])}</small>'
        f'<p class="source-authority">{esc(source["authority"].replace("-", " "))}</p>'
        f'<p class="source-scope">Supports: {esc(", ".join(source_claim_ids[source["source_id"]]))}</p>'
        f'<a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">View official source ↗</a>'
        '</article>'
        for source in ga_sources
    )
    neutral_detail = (
        '<div class="neutral-detail"><p class="eyebrow">EXPLORE</p><h2>Choose a material</h2>'
        '<p>Explore its applications, connected material systems, public sources, and reviewed pathways where available.</p></div>'
    )
    embedded = json.dumps(
        {"atlas": atlas, "forms": forms, "sources": sources, "yig001": yig_pathway, "ga001": payload["ga001"]},
        separators=(",", ":"), ensure_ascii=False
    ).replace("<", "\u003c")

    replacements = {
        "<!-- R6:LENSES -->": lens_buttons,
        "<!-- R6:ZONES -->": zones,
        "<!-- R6:MINERALS -->": mineral_nodes,
        "<!-- R6:INITIAL_DETAIL -->": neutral_detail,
        "<!-- R6:INDEX -->": "".join(index_rows),
        "<!-- R6:SELECTED_PATHWAYS -->": selected_pathways_html,
        "<!-- R6:GA_RIBBON -->": pathway_ribbon_html(
            ga_mpi,
            section_id="ga-overview",
            title_id="ga-overview-title",
            trace_href="#trace",
        ),
        "<!-- R6:GA_BOUNDARY -->": evidence_boundary_html(
            title_id="examine-title",
            heading_level=2,
            known_html=f"<ul>{supported}</ul>",
            unknown_html=f"<ul>{unknown}</ul>",
            horizon_label=ga_mpi["horizon"]["label"],
            horizon_meaning=(
                "Downstream facts may remain independently supported, but they do not "
                "reconnect the pathway across this unresolved link."
            ),
            mpi_html=mpi_summary_html(
                ga_mpi,
                title_id="ga-mpi-title",
                links=(("Consider Next Proof", "#decision"),),
            ),
        ),
        "<!-- R6:TRACE -->": pathway_trace_html(
            "".join(trace_nodes),
            base_class="trace-list",
            aria_label="Gallium trace to mission pathway",
        ),
        "<!-- R6:SUPPORT -->": "".join(support_items),
        "<!-- R6:GA_CLAIMS -->": ga_claim_items,
        "<!-- R6:ACTIONS -->": actions,
        "<!-- R6:FORMS -->": "".join(form_cards),
        "<!-- R6:YIG_PATHWAY -->": yig_pathway_html,
        "<!-- R6:YIG_NEXT_PROOF -->": f'<ol class="yig-next-proof-list">{yig_next}</ol>',
        "<!-- R6:SOURCES -->": source_cards,
        "<!-- R6:GA_SOURCES -->": ga_source_cards,
        "<!-- R6:DATA -->": embedded,
    }
    rendered = template
    for marker, value in replacements.items():
        if rendered.count(marker) != 1:
            raise SystemExit(f"STOP - template marker invalid: {marker}")
        rendered = rendered.replace(marker, value)
    return rendered


def build(output: Path):
    payload = project()
    template = (WEB / "index.html").read_text(encoding="utf-8")
    rendered = render(template, payload)
    if "<!-- R6:" in rendered:
        raise SystemExit("STOP - unresolved public template marker")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / "data").mkdir()

    write_text(output / "index.html", rendered)
    for name in ("styles.css", "app.js"):
        (output / name).write_bytes((WEB / name).read_bytes())

    ga = payload["ga001"]
    write_text(output / "data/ga001.json", json.dumps(ga, indent=2, sort_keys=True) + "\n")

    rows = []
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        relative = path.relative_to(output).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    write_text(output / "WEB_MANIFEST.sha256", "\n".join(rows) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build/web")
    args = parser.parse_args()
    out = build(args.output.resolve())
    print(f"PASS - deterministic R6 public web build: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
