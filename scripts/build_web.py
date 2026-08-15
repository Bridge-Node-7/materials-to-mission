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

    nodes = view["trace_nodes"]
    unique(nodes, "id", "trace node ID")
    for node in nodes:
        if node.get("state") not in ALLOWED_STATES:
            raise SystemExit("STOP - invalid trace state")
    if not any(node["state"] == "unknown" for node in nodes):
        raise SystemExit("STOP - Evidence Horizon missing")
    return claim_by, ga_source_by


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
        '<a class="detail-action" href="#trace" data-depth="trace">Reviewed pathway available →</a>'
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
    selected_pathways = payload["selected_pathways"]

    orientation_by_source = {
        "gallium": (
            '<span class="pathway-orientation"><strong>New here? Start with Gallium.</strong> '
            'An official critical mineral can still have an unresolved pathway.</span>'
        ),
        "yig": (
            '<span class="pathway-orientation"><strong>Explore deeper:</strong> YIG shows how an engineered material system '
            'adds substrate, processing, characterization, and validation questions.</span>'
        ),
    }
    selected_pathway_rows = "".join(
        '<article class="selected-pathway-row" data-pathway="' + esc(item["source_id"]) + '">'
        f'<span class="selected-pathway-symbol{" selected-pathway-symbol-wide" if len(item["symbol"]) > 2 else ""}" aria-hidden="true">{esc(item["symbol"])}</span>'
        '<div class="selected-pathway-identity">'
        f'<span class="selected-pathway-type">{esc(item["type_label"])}</span><h3>{esc(item["name"])}</h3></div>'
        f'<p>{esc(item["summary"])}{orientation_by_source[item["source_id"]]}</p><a href="{esc(item["href"])}">{esc(item["action_label"])} <span aria-hidden="true">→</span></a>'
        '</article>'
        for item in selected_pathways
    )
    selected_pathways_html = (
        '<section id="selected-pathways" class="selected-pathways" aria-labelledby="selectedPathwaysTitle">'
        '<header class="selected-pathways-head"><p class="selected-pathways-kicker">GO DEEPER</p>'
        '<h2 id="selectedPathwaysTitle">Selected pathways</h2>'
        f'<p>{len(selected_pathways)} public examples currently shared with deeper reviewed context. Reviewed does not mean qualified.</p></header>'
        f'<div class="selected-pathway-list">{selected_pathway_rows}</div>'
        '<nav class="selected-pathways-secondary" aria-label="Additional Materials-to-Mission depth">'
        '<a href="#forms">Browse material systems <span aria-hidden="true">→</span></a>'
        '<a href="#sources">Evidence &amp; sources <span aria-hidden="true">→</span></a></nav></section>'
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

    first_unknown = next(
        index for index, node in enumerate(view["trace_nodes"])
        if node["state"] == "unknown"
    )
    trace_nodes = []
    for index, node in enumerate(view["trace_nodes"]):
        zone = "connected" if index < first_unknown else ("horizon" if index == first_unknown else "island")
        trace_nodes.append(
            f'<li class="trace-node {zone} state-{esc(node["state"])}">'
            f'<span class="trace-num">{index + 1:02d}</span><div>'
            f'<small>{esc(node["kind"].replace("-", " "))}</small>'
            f'<strong>{esc(node["label"])}</strong>'
            f'<em>{esc(node["state"].title())}</em></div></li>'
        )

    supported = "".join(
        f'<li>{esc(item["text"])}</li>'
        for item in snapshot["bounded_interpretations"]
        if item["state"] == "supported"
    )
    unknown = "".join(
        f'<li>{esc(item["text"])}</li>'
        for item in snapshot["bounded_interpretations"]
        if item["state"] == "unknown"
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

    action_copy = {
        "monitor": "Keep the evidence state visible and reassess when material conditions change.",
        "validate": "Target the first unresolved link with a defined proof request before advancing the pathway.",
        "support": "Direct bounded support toward evidence or capability that closes a named pathway gap without implying qualification.",
    }
    actions = "".join(
        f'<article class="action-card"><span>{index + 1:02d}</span>'
        f'<h3>{esc(action.title())}</h3>'
        f'<p>{esc(action_copy.get(action, "Human review required before any consequential action."))}</p>'
        '<small>Evidence-supported option · human decision required</small></article>'
        for index, action in enumerate(view["action_options"])
    )

    material_id_by_name = {material["name"]: material["id"] for material in atlas["materials"]}
    form_cards = []
    ordered_forms = sorted(forms, key=lambda form: (0 if form.get("primary_example") else 1, form["name"]))
    for form in ordered_forms:
        relationships = "".join(
            f'<a href="#material-{esc(material_id_by_name[rel["mineral"]])}">'
            f'{esc(rel["mineral"])}</a>'
            for rel in form["relationships"]
        )
        primary = '<span class="primary-badge">Primary example</span>' if form.get("primary_example") else ""
        review = form.get("review", {}).get("label", "Public Context")
        form_cards.append(
            f'<article id="form-{esc(form["id"])}" class="form-card{" primary-system" if form.get("primary_example") else ""}">'
            f'<span class="form-symbol">{esc(form["symbol"])}</span><div>'
            f'{primary}<h3>{esc(form["name"])}</h3><p>{esc(form["context"])}</p>'
            f'<small class="form-state">{esc(review)}</small>'
            '<span class="detail-label">Related critical minerals</span>'
            f'<div class="relationship-links">{relationships}'
            f'<button type="button" class="js-only" data-form-id="{esc(form["id"])}" aria-label="Open detail: {esc(form["name"])}">Open detail</button>'
            '</div></div></article>'
        )

    yig_horizon_id = yig_pathway["evidence_horizon"]["first_unresolved_stage_id"]
    horizon_seen = False
    yig_stage_cards = []
    for index, stage in enumerate(yig_pathway["stages"]):
        if stage["id"] == yig_horizon_id:
            zone = "horizon"
            horizon_seen = True
        elif horizon_seen:
            zone = "island"
        else:
            zone = "connected"
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
        basis = (
            f'<p class="stage-basis"><strong>Evidence basis:</strong> {esc(stage["evidence_basis"])}</p>'
            if stage.get("evidence_basis") else ""
        )
        yig_stage_cards.append(
            f'<article class="yig-stage {zone} state-{esc(stage["state"])}">'
            f'<span class="yig-stage-num">{index + 1:02d}</span>'
            f'<div><small>{esc(stage["state"].replace("-", " "))}</small>'
            f'<h3>{esc(stage["stage"])}</h3><p>{esc(stage["summary"])}</p>{basis}'
            f'<div class="yig-source-links">{source_links}{context_links}</div></div></article>'
        )

    yig_dependencies = "".join(
        f'<span>{esc(item["mineral"])}<small>{esc(item["role"])}</small></span>'
        for item in yig_pathway["critical_mineral_dependencies"]
    )
    yig_next = "".join(f'<li>{esc(item)}</li>' for item in yig_pathway["next_proof"])
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
    yig_pathway_html = (
        '<div class="yig-identity">'
        '<span class="yig-mark">YIG</span><div><p class="eyebrow">PRIMARY ENGINEERED MATERIAL-SYSTEM EXAMPLE</p>'
        f'<h2>{esc(yig_pathway["material_system"])} · Y₃Fe₅O₁₂</h2>'
        f'<p>{esc(yig_pathway["public_summary"])}</p></div></div>'
        '<div class="yig-dependencies"><span class="detail-label">Critical-Mineral Dependencies Across Common YIG Stacks</span>'
        '<p class="dependency-note">Yttrium is the YIG critical-mineral constituent. Gadolinium, Gallium, Scandium, and Aluminum enter through common or emerging garnet substrate systems shown in this public pathway.</p>'
        f'<div>{yig_dependencies}</div></div>'
        f'<div class="yig-stage-grid">{"".join(yig_stage_cards)}</div>'
        f'<div class="frontier-context-grid">{frontier_context}</div>'
        '<div class="yig-proof-horizon"><span aria-hidden="true"></span><div>'
        f'<strong>{esc(yig_pathway["evidence_horizon"]["label"])}</strong>'
        f'<p>{esc(yig_pathway["evidence_horizon"]["meaning"])}</p></div></div>'
        '<div class="yig-next-proof"><p class="eyebrow">NEXT PROOF</p><h3>What would have to be established next?</h3>'
        f'<ol>{yig_next}</ol></div>'
    )

    source_cards = "".join(
        '<article class="source-card">'
        f'<span class="source-id">{esc(source["source_id"])}</span>'
        f'<h3>{esc(source["title"])}</h3>'
        f'<p>{esc(source["publisher"])}</p>'
        f'<small>{esc(source.get("source_date") or "Current page")} · verified {esc(source["verified_at"])}</small>'
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
        '<p>Explore its applications, related material systems, public sources, and reviewed pathways where available.</p></div>'
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
        "<!-- R6:TRACE -->": "".join(trace_nodes),
        "<!-- R6:SUPPORTED -->": supported,
        "<!-- R6:UNKNOWN -->": unknown,
        "<!-- R6:SUPPORT -->": "".join(support_items),
        "<!-- R6:GA_CLAIMS -->": ga_claim_items,
        "<!-- R6:ACTIONS -->": actions,
        "<!-- R6:FORMS -->": "".join(form_cards),
        "<!-- R6:YIG_PATHWAY -->": yig_pathway_html,
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
