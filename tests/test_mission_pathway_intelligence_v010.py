from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mpi_v010_build", ROOT / "scripts" / "build_web.py"
)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def payload():
    return BUILD.project()


def test_mpi_derivation_preserves_ga_and_yig_authority() -> None:
    data = payload()
    ga = data["mpi"]["ga001"]
    yig = data["mpi"]["yig001"]

    assert ga["identity"] == {
        "record_id": "GA-001",
        "record_version": "1.0.0",
        "subject_name": "Gallium",
        "symbol": "Ga",
        "type_label": "CRITICAL MINERAL · REVIEWED PATHWAY",
        "maturity": "M0",
    }
    assert ga["supported_labels"] == ["Gallium (Ga)"]
    assert ga["horizon"]["stage_id"] == "ga-processing"
    assert ga["constraint"]["status"] == "not-established"
    assert ga["stages"][2]["continuity"] == "post-horizon-context"

    assert yig["identity"]["record_id"] == "YIG-001"
    assert yig["identity"]["type_label"] == (
        "ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT"
    )
    assert yig["identity"]["maturity"] == "M0"
    assert yig["supported_labels"] == ["Critical Materials"]
    assert yig["horizon"]["stage_id"] == "yig-qualified-stack"
    assert yig["constraint"]["status"] == "not-established"
    assert [stage["display_state"] for stage in yig["stages"][2:5]] == [
        "context",
        "context",
        "context",
    ]


def test_mpi_build_uses_existing_pages_boundary_and_semantic_html(tmp_path: Path) -> None:
    output = BUILD.build(tmp_path / "web")
    observed = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert observed == {
        "index.html",
        "styles.css",
        "app.js",
        "data/ga001.json",
        "WEB_MANIFEST.sha256",
    }

    html = (output / "index.html").read_text(encoding="utf-8")
    assert html.count('class="mpi-summary"') == 2
    assert 'data-mpi-record="GA-001"' in html
    assert 'data-mpi-record="YIG-001"' in html
    assert "CRITICAL MINERAL · REVIEWED PATHWAY · GA-001 v1.0.0 · M0" in html
    assert "ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT · YIG-001 v1.0.0 · M0" in html
    assert 'data-mpi-output="governing-constraint"' not in html
    assert "No canonical governing constraint is established" not in html
    assert "Supported, supported context, and unknown remain separate." in html
    assert "pathway score" not in html.lower()
    assert "confidence percentage" not in html.lower()
    assert "R6:GA_MPI" not in html


def test_hidden_ga_gap_stops_continuity_without_hiding_later_context() -> None:
    data = payload()
    selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "GA-001"
    )
    material = next(
        item for item in data["atlas"]["materials"] if item["id"] == "gallium"
    )
    view = deepcopy(data["ga001"]["view"])
    view["trace_nodes"][0]["state"] = "unknown"
    derived = BUILD.derive_ga_mpi_view(
        selected,
        material,
        view,
        data["ga001"]["snapshot"],
        data["ga001"]["sources"],
    )
    assert derived["horizon"]["stage_id"] == "ga-material"
    assert derived["supported_labels"] == []
    assert all(
        stage["continuity"] == "post-horizon-context"
        for stage in derived["stages"][1:]
    )


def test_yig_rejects_unsupported_continuity_before_declared_horizon() -> None:
    data = payload()
    selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "YIG-001"
    )
    form = next(item for item in data["forms"] if item["id"] == "yig")
    pathway = deepcopy(data["yig001"])
    pathway["stages"][0]["state"] = "supported-context"
    source_by = {source["source_id"]: source for source in data["sources"]}
    with pytest.raises(SystemExit, match="unsupported YIG MPI continuity"):
        BUILD.derive_yig_mpi_view(selected, form, pathway, source_by)


def test_mpi_rejects_missing_ga_and_yig_provenance() -> None:
    data = payload()
    ga_selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "GA-001"
    )
    gallium = next(
        item for item in data["atlas"]["materials"] if item["id"] == "gallium"
    )
    ga_snapshot = deepcopy(data["ga001"]["snapshot"])
    ga_snapshot["claims"][0]["source_ids"] = ["PRIVATE-SOURCE"]
    with pytest.raises(SystemExit, match="claim provenance is unresolved"):
        BUILD.derive_ga_mpi_view(
            ga_selected,
            gallium,
            data["ga001"]["view"],
            ga_snapshot,
            data["ga001"]["sources"],
        )

    yig_selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "YIG-001"
    )
    form = next(item for item in data["forms"] if item["id"] == "yig")
    pathway = deepcopy(data["yig001"])
    pathway["stages"][0]["source_ids"] = ["PRIVATE-SOURCE"]
    source_by = {source["source_id"]: source for source in data["sources"]}
    with pytest.raises(SystemExit, match="stage provenance is unresolved"):
        BUILD.derive_yig_mpi_view(yig_selected, form, pathway, source_by)


def test_mpi_rejects_invalid_horizon_and_multiple_governing_constraints() -> None:
    data = payload()
    selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "YIG-001"
    )
    form = next(item for item in data["forms"] if item["id"] == "yig")
    pathway = deepcopy(data["yig001"])
    pathway["evidence_horizon"]["first_unresolved_stage_id"] = "yig-inputs"
    source_by = {source["source_id"]: source for source in data["sources"]}
    with pytest.raises(SystemExit, match="Evidence Horizon is invalid"):
        BUILD.derive_yig_mpi_view(selected, form, pathway, source_by)

    with pytest.raises(SystemExit, match="multiple governing constraints"):
        BUILD.derive_governing_constraint(
            [
                {"weak_link_id": "WL-1", "statement": "One", "governing": True},
                {"weak_link_id": "WL-2", "statement": "Two", "governing": True},
            ]
        )


def test_mpi_missing_fields_fail_closed() -> None:
    data = payload()
    ga_selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "GA-001"
    )
    gallium = next(
        item for item in data["atlas"]["materials"] if item["id"] == "gallium"
    )
    ga_view = deepcopy(data["ga001"]["view"])
    del ga_view["trace_nodes"]
    with pytest.raises(SystemExit, match="pathway stages are missing"):
        BUILD.derive_ga_mpi_view(
            ga_selected,
            gallium,
            ga_view,
            data["ga001"]["snapshot"],
            data["ga001"]["sources"],
        )

    yig_selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "YIG-001"
    )
    form = next(item for item in data["forms"] if item["id"] == "yig")
    pathway = deepcopy(data["yig001"])
    del pathway["evidence_horizon"]
    source_by = {source["source_id"]: source for source in data["sources"]}
    with pytest.raises(SystemExit, match="stages or horizon are missing"):
        BUILD.derive_yig_mpi_view(yig_selected, form, pathway, source_by)

    mpi = deepcopy(data["mpi"]["ga001"])
    mpi["supported_labels"] = []
    html = BUILD.mpi_summary_html(
        mpi,
        title_id="missing-segment-title",
        links=(("Evidence status", "#examine"),),
    )
    assert "Continuous supported segment not established" in html


def test_mpi_ignores_unapproved_customer_context_and_rejects_scoring_copy() -> None:
    data = payload()
    selected = deepcopy(
        next(
            item for item in data["selected_pathways"]
            if item["record_id"] == "GA-001"
        )
    )
    selected["customer_context"] = "Undisclosed Customer Alpha"
    gallium = next(
        item for item in data["atlas"]["materials"] if item["id"] == "gallium"
    )
    derived = BUILD.derive_ga_mpi_view(
        selected,
        gallium,
        data["ga001"]["view"],
        data["ga001"]["snapshot"],
        data["ga001"]["sources"],
    )
    html = BUILD.mpi_summary_html(
        derived,
        title_id="test-title",
        links=(("Evidence status", "#examine"),),
    )
    assert "Undisclosed Customer Alpha" not in html

    for text in (
        "pathway score 91",
        "82% pathway confidence",
        "top-ranked material",
    ):
        with pytest.raises(SystemExit, match="scoring or ranking language"):
            BUILD._validate_mpi_copy(text)


def test_mpi_rejects_automated_authority_and_preserves_absent_constraint() -> None:
    data = payload()
    selected = next(
        item for item in data["selected_pathways"] if item["record_id"] == "GA-001"
    )
    gallium = next(
        item for item in data["atlas"]["materials"] if item["id"] == "gallium"
    )
    view = deepcopy(data["ga001"]["view"])
    view["decision_authority"] = "automated system"
    with pytest.raises(SystemExit, match="human authority changed"):
        BUILD.derive_ga_mpi_view(
            selected,
            gallium,
            view,
            data["ga001"]["snapshot"],
            data["ga001"]["sources"],
        )

    constraint = BUILD.derive_governing_constraint([])
    assert constraint == {
        "status": "not-established",
        "statement": BUILD.MPI_NO_CONSTRAINT,
    }
