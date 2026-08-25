from __future__ import annotations

import copy
import importlib.util
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mpi_ux_v020_build", ROOT / "scripts" / "build_web.py"
)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def built_html(tmp_path: Path) -> str:
    output = BUILD.build(tmp_path / "web")
    return (output / "index.html").read_text(encoding="utf-8")


def test_v020_atlas_first_journey_and_visual_discovery(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    assert '<h1 id="atlas-title">Materials-to-Mission Atlas</h1>' in html
    assert "PATHWAY PREVIEWS" in html
    assert "See how far the evidence carries." in html
    assert "Two reviewed public examples. Reviewed does not mean qualified." in html
    assert html.count('class="selected-pathway-signal"') == 2
    assert html.count('class="selected-pathways-legend"') == 1
    assert html.count('class="selected-pathway-preview-meta"') == 2
    assert "Mission Pathway Intelligence · M0 Public Method" not in html
    assert 'class="mpi-hero"' not in html
    assert 'id="pathway-explanation"' not in html
    ids = (
        'id="atlas"',
        'id="selected-pathways"',
        'id="trace"',
        'id="yig-pathway"',
        'id="forms"',
        'id="sources"',
    )
    assert [html.index(value) for value in ids] == sorted(html.index(value) for value in ids)


def test_v020_preserves_identity_classification_and_human_boundary(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    assert html.count("CRITICAL MINERAL · REVIEWED PATHWAY") == 2
    assert html.count("ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT") == 2
    assert "Gallium · GA-001" not in html  # Existing identity layout remains source-derived.
    assert 'data-pathway="gallium"' in html and 'data-pathway="yig"' in html
    assert html.count("Human decision authority remains required.") >= 3
    assert "Reviewed does not mean qualified." in html
    assert "M0 identifies the experimental public evidence method used here. It does not indicate readiness, qualification, certification, or acquisition approval." in html


def test_v020_pathway_previews_are_build_time_and_non_authoritative(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    assert html.count('class="signal-horizon"') == 2
    assert "Gallium (Ga)" in html
    assert "Qualified domestic primary recovery at mission-relevant scale" in html
    assert "Critical Materials" in html
    assert "Qualified Material Stack" in html
    assert html.count("Experimental public evidence method") == 2
    assert "M0 experimental public method" not in html
    assert "Public evidence is continuous through Gallium; qualified domestic primary recovery remains unresolved." in html
    assert "Public evidence is continuous through critical materials; a qualified material stack remains unresolved." in html
    assert 'href="#ga-pathway">View Gallium pathway' in html
    assert 'href="#yig-pathway">View YIG pathway' in html
    assert 'class="selected-pathways-secondary"' not in html
    visible = re.sub(r"<[^>]+>", " ", html).lower()
    assert "pathway score" not in visible
    assert "confidence percentage" not in visible
    assert "Human decision authority remains required." in html


def test_v020_yig_first_use_and_spoken_flow_precede_method_detail(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    yig_html = html[html.index('<section id="yig-pathway"'):]
    intro_cues = (
        "Yttrium Iron Garnet (YIG)",
        "What it is",
        "Why it matters",
        'id="yig-overview"',
        'id="yig-trace"',
        'id="yig-boundary"',
    )
    assert [yig_html.index(cue) for cue in intro_cues] == sorted(yig_html.index(cue) for cue in intro_cues)
    boundary_html = yig_html[yig_html.index('id="yig-boundary"'):]
    boundary_cues = (
        "What We Know",
        "Supported evidence",
        "What We Don't Know",
        "Evidence Horizon",
        "First unresolved link",
        'id="yig-mpi-title">What evidence establishes',
    )
    assert [boundary_html.index(cue) for cue in boundary_cues] == sorted(
        boundary_html.index(cue) for cue in boundary_cues
    )
    assert 'aria-label="Chemical formula for yttrium iron garnet: Y three F E five O twelve"' in html
    assert "Gadolinium gallium garnet (GGG)" in html
    assert "yttrium scandium gallium aluminum garnet (YSGAG)" in html


def test_v020_pathway_journeys_are_visual_ordered_and_route_scoped(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    assert html.count('class="pathway-ribbon"') == 2
    assert html.count("Supported evidence") >= 3
    assert html.count("First unresolved link") >= 3
    assert html.count("Later-stage context") >= 3
    assert [html.index(cue) for cue in (
        'id="ga-pathway"', 'id="ga-overview"', 'id="trace"',
        'id="examine"', 'id="decision"', 'id="ga-systems"', 'id="ga-sources"',
    )] == sorted(html.index(cue) for cue in (
        'id="ga-pathway"', 'id="ga-overview"', 'id="trace"',
        'id="examine"', 'id="decision"', 'id="ga-systems"', 'id="ga-sources"',
    ))
    assert [html.index(cue) for cue in (
        'id="yig-pathway"', 'id="yig-overview"', 'id="yig-trace"',
        'id="yig-boundary"', 'id="yig-next-proof"', 'id="yig-systems"', 'id="yig-sources"',
    )] == sorted(html.index(cue) for cue in (
        'id="yig-pathway"', 'id="yig-overview"', 'id="yig-trace"',
        'id="yig-boundary"', 'id="yig-next-proof"', 'id="yig-systems"', 'id="yig-sources"',
    ))
    assert 'data-pathway-routes="ga"' in html
    assert 'data-pathway-only="yig" href="#yig-sources"' in html
    assert '<h2 id="forms-title">Connected Material Systems</h2>' in html
    assert '<h2 id="sources-title">Evidence & Sources</h2>' in html
    assert html.count('>Explore the Pathway Overview <span aria-hidden="true">→</span></a>') == 2
    assert html.count('>Trace to Mission <span aria-hidden="true">→</span></a>') == 2
    assert '>Review the Evidence Boundary' not in html
    assert html.count('>Explore Connected Material Systems') == 2
    assert html.count('>Review Evidence & Sources') == 2
    assert html.count('>Consider Next Proof') == 2
    assert 'class="sources-next' not in html
    assert html.count('>Next Proof</h2>') == 2
    assert html.count('What would need to be established next?') == 2
    boundary_copy = (
        "This map organizes public evidence and unresolved questions. It does not approve, "
        "qualify, or certify a pathway. Decisions requiring judgment remain with responsible "
        "people and organizations."
    )
    assert html.count(f"<p>{boundary_copy}</p>") == 2
    assert '<h3>Support Next Proof</h3>' in html
    assert '"support"' in (ROOT / "public-snapshots/gallium/GA-001/public-view.json").read_text(encoding="utf-8")
    assert '<strong>Fabrication path for a specific program</strong>' in html
    assert '<strong>Use-specific validation evidence</strong>' in html
    assert '<strong>Program acquisition access</strong>' in html
    assert '<strong>Program-specific fabrication path</strong>' not in html


def test_v020_pathways_share_presentation_rhythm_without_forcing_stage_parity(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    css = (tmp_path / "web" / "styles.css").read_text(encoding="utf-8")
    assert html.count('class="pathway-glance"') == 2
    assert html.count('class="pathway-next"') == 4
    assert '.trace-node,.yig-stage{border-radius:14px' in css
    assert '.trace-node.horizon,.yig-stage.horizon{box-shadow:none}' in css
    assert '.contextual-depth.section{padding-top:56px;padding-bottom:56px}' in css
    assert html.count('class="examine-grid evidence-findings"') == 2
    assert html.count('class="state supported">Supported evidence</span>') == 2
    assert html.count('class="state unknown">Unknown</span>') == 2
    assert html.count('<h3>What We Know</h3>') == 2
    assert html.count("<h3>What We Don't Know</h3>") == 2
    assert html.count('<small>Evidence Horizon</small><strong>First unresolved link</strong>') == 2
    for boundary_id in ('id="examine"', 'id="yig-boundary"'):
        boundary_html = html[html.index(boundary_id):]
        cues = (
            "What We Know",
            'class="state supported">Supported evidence',
            "What We Don't Know",
            "Evidence Horizon",
            "First unresolved link",
            "Human decision boundary",
        )
        assert [boundary_html.index(cue) for cue in cues] == sorted(
            boundary_html.index(cue) for cue in cues
        )


def test_v020_trace_rails_share_semantics_without_changing_governed_stages(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    css = (tmp_path / "web" / "styles.css").read_text(encoding="utf-8")
    payload = BUILD.project()
    expected_ga = [stage["id"] for stage in payload["mpi"]["ga001"]["stages"]]
    expected_yig = [stage["id"] for stage in payload["mpi"]["yig001"]["stages"]]
    rendered_ga = re.findall(
        r'<li class="pathway-stage trace-node [^"]+" data-stage-id="([^"]+)"', html
    )
    rendered_yig = re.findall(
        r'<li class="pathway-stage yig-stage [^"]+" data-stage-id="([^"]+)"', html
    )
    assert rendered_ga == expected_ga
    assert rendered_yig == expected_yig
    assert len(rendered_ga) == 10
    assert len(rendered_yig) == 8
    assert html.count("pathway-trace-sequence") >= 2
    assert html.count('tabindex="0"') >= 2
    assert '<ol class="trace-list pathway-trace-sequence"' in html
    assert '<ol id="yig-stages" class="yig-stage-grid pathway-trace-sequence"' in html
    assert "grid-auto-flow:column" in css
    assert "overflow-x:auto" in css
    assert "grid-auto-flow:row" in css


def test_v020_shared_presentation_state_adapter_preserves_raw_evidence(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    payload = BUILD.project()
    stages = payload["mpi"]["ga001"]["stages"] + payload["mpi"]["yig001"]["stages"]
    rendered = re.findall(
        r'data-stage-id="([^"]+)" data-raw-evidence-state="([^"]+)" '
        r'data-continuity="([^"]+)" data-presentation-state="([^"]+)"',
        html,
    )
    expected = [
        (
            stage["id"],
            stage["state"],
            stage["continuity"],
            BUILD.presentation_state_label(stage).lower().replace(" ", "-"),
        )
        for stage in stages
    ]
    assert rendered == expected
    assert html.count('class="pathway-stage ') == 18
    assert html.count('class="pathway-stage-state">Supported evidence</small>') == 2
    assert html.count('class="pathway-stage-state">First unresolved link</small>') == 2
    assert html.count('class="pathway-stage-state">Later-stage context</small>') == 6
    assert html.count('class="pathway-stage-state">Unresolved question</small>') == 8
    assert 'data-stage-id="ga-required-form" data-raw-evidence-state="supported"' in html
    assert 'data-stage-id="yig-growth" data-raw-evidence-state="supported-context"' in html
    with pytest.raises(SystemExit, match="unsupported evidence state and continuity"):
        BUILD.presentation_state_label({"continuity": "continuous", "state": "unknown"})


def test_v020_evidence_boundaries_share_shell_and_keep_optional_governed_regions(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    assert html.count('class="evidence-boundary-shell"') == 2
    assert html.count('class="evidence-boundary-head"') == 2
    assert html.count('class="boundary-governed-region"') == 2
    assert 'aria-label="Gallium governed evidence details"' in html
    assert 'Reviewed Gallium claim register' in html
    assert 'aria-label="YIG governed research context"' in html
    assert html.count('Reviewed YIG claim register') == 0
    assert html.count('<h3>What We Know</h3>') == 2
    assert html.count("<h3>What We Don't Know</h3>") == 2


def test_v020_route_scope_uses_only_explicit_governed_relationships(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    payload = BUILD.project()
    field_ids = {source["source_id"] for source in payload["sources"]}
    gallium = next(item for item in payload["atlas"]["materials"] if item["id"] == "gallium")
    expected_ga_sources = set(gallium["source_ids"]) & field_ids
    yig = next(item for item in payload["forms"] if item["id"] == "yig")
    expected_yig_sources = set(yig.get("source_ids", []))
    pathway = payload["yig001"]
    for collection in (
        "critical_mineral_dependencies", "substrate_context", "stages",
        "public_applications", "frontier_research_context",
    ):
        for item in pathway.get(collection, []):
            expected_yig_sources.update(item.get("source_ids", []))
            expected_yig_sources.update(item.get("context_source_ids", []))
    routed_sources = {
        match.group(2): set(match.group(1).split())
        for match in re.finditer(
            r'class="source-card" data-pathway-routes="([^"]*)"><span class="source-id">([^<]+)',
            html,
        )
    }
    assert {source_id for source_id, routes in routed_sources.items() if "ga" in routes} == expected_ga_sources
    assert {source_id for source_id, routes in routed_sources.items() if "yig" in routes} == expected_yig_sources
    routed_forms = {
        match.group(1): set(match.group(2).split())
        for match in re.finditer(
            r'id="form-([^"]+)" class="form-card[^"]*" data-pathway-routes="([^"]*)"',
            html,
        )
    }
    expected_ga_forms = {
        item["id"] for item in payload["forms"]
        if any(link["mineral"] == "Gallium" for link in item["relationships"])
    }
    expected_yig_symbols = {"YIG"} | {item["name"] for item in pathway["substrate_context"]}
    expected_yig_forms = {item["id"] for item in payload["forms"] if item["symbol"] in expected_yig_symbols}
    assert {form_id for form_id, routes in routed_forms.items() if "ga" in routes} == expected_ga_forms
    assert {form_id for form_id, routes in routed_forms.items() if "yig" in routes} == expected_yig_forms


def test_v020_pathway_preview_copy_fails_closed_when_governed_view_changes() -> None:
    payload = copy.deepcopy(BUILD.project())
    payload["mpi"]["ga001"]["horizon"]["label"] = "Unsupported replacement"
    template = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    with pytest.raises(SystemExit, match="GA-001 pathway preview copy is unsupported"):
        BUILD.render(template, payload)


def test_v020_public_boundary_and_static_runtime(tmp_path: Path) -> None:
    html = built_html(tmp_path)
    visible = re.sub(r"<[^>]+>", " ", html).lower()
    for forbidden in (
        "confidence percentage",
        "pathway score",
        "top-ranked",
        "customer-specific",
        "private intelligence",
        "automated approval",
    ):
        assert forbidden not in visible
    js = (ROOT / "web" / "app.js").read_text(encoding="utf-8").lower()
    for forbidden in (
        "fetch(", "xmlhttprequest", "websocket", "localstorage",
        "sessionstorage", "indexeddb", "analytics", "telemetry",
    ):
        assert forbidden not in js


def test_v020_source_and_pages_boundaries_are_unchanged(tmp_path: Path) -> None:
    output = BUILD.build(tmp_path / "web")
    observed = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert observed == {
        "index.html", "styles.css", "app.js", "data/ga001.json",
        "WEB_MANIFEST.sha256",
    }
    assert (output / "app.js").read_bytes() == (ROOT / "web" / "app.js").read_bytes()
