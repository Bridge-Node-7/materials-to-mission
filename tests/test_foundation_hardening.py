from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_current_durable_source_identity_preserves_foundation_provenance() -> None:
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.7.4"
    assert facts["version"] == facts["source_version"] == "0.7.4"
    assert facts["immediate_prior_immutable_release"] == {
        "tag": "v0.7.3",
        "verified_signed_tag_target": "b63ed45c3d4abb477402f40b264d00d4e0c5bc50",
        "status": "PUBLISHED_IMMUTABLE",
    }
    assert facts["foundation_baseline"]["commit"] == "12e80d232c59e5221747353f963e71aba2df51d4"
    assert facts["foundation_baseline"]["tree"] == "0114df565bd87d8c0b55b0988b3a200970aba8c2"
    assert "GitHub" in facts["publication_authority"]


def test_release_bound_source_does_not_self_declare_mutable_github_state() -> None:
    active_source = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8").lower()
        for relative in ("docs/CURRENT_STATE.md", "PROJECT_FACTS.json", "RELEASE_NOTES.md")
    )
    for volatile in (
        "local release candidate only",
        "no v0.7.4 tag",
        "no github release",
        "latest immutable release is `v0.7.0`",
        "current post-release `main`",
        "tag, github release, and publication not performed",
    ):
        assert volatile not in active_source


def test_selected_pathways_registry_is_valid_and_unique() -> None:
    registry = json.loads((ROOT / "web/selected-pathways.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "web/selected-pathways.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(registry)
    ids = [item["record_id"] for item in registry["pathways"]]
    assert len(ids) == len(set(ids))


def test_current_selected_pathways_are_build_time_and_data_driven(tmp_path: Path) -> None:
    registry = json.loads((ROOT / "web/selected-pathways.json").read_text(encoding="utf-8"))
    out = tmp_path / "web"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_web.py"), "--output", str(out)], cwd=ROOT, check=True)
    html = (out / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    assert html.count('class="selected-pathway-row"') == len(registry["pathways"])
    for pathway in registry["pathways"]:
        assert f'data-pathway="{pathway["source_id"]}"' in html
        assert pathway["record_id"] in {"GA-001", "YIG-001"}
    assert "function buildPathways" not in app
    assert "section.innerHTML" not in app
    assert "CRITICAL MINERAL · REVIEWED PATHWAY" not in app
    assert "ENGINEERED MATERIAL SYSTEM · REVIEWED CONTEXT" not in app
    assert "return document.querySelector('[data-depth=\"legacy-overview\"]');" in app
    assert "while (node && node !== document.body && node !== document.documentElement)" not in app


def test_registry_entries_resolve_to_controlled_records() -> None:
    registry = json.loads((ROOT / "web/selected-pathways.json").read_text(encoding="utf-8"))
    atlas = json.loads((ROOT / "public-snapshots/materials-field/MF-001/atlas.json").read_text(encoding="utf-8"))
    forms = json.loads((ROOT / "public-snapshots/materials-field/MF-001/public-forms.json").read_text(encoding="utf-8"))["forms"]
    material_by_id = {item["id"]: item for item in atlas["materials"]}
    form_by_id = {item["id"]: item for item in forms}
    for pathway in registry["pathways"]:
        if pathway["record_type"] == "critical-mineral-reviewed-pathway":
            assert material_by_id[pathway["source_id"]]["review"]["snapshot_id"] == pathway["record_id"]
        else:
            form = form_by_id[pathway["source_id"]]
            assert form["kind"] == "engineered-material-system"
            assert form["pathway_id"] == pathway["record_id"]


def test_browser_uat_and_preview_transport_are_version_neutral() -> None:
    workflow = (ROOT / ".github/workflows/browser-uat.yml").read_text(encoding="utf-8")
    server = (ROOT / "scripts/serve_preview.py").read_text(encoding="utf-8")
    assert "name: Materials-to-Mission Browser UAT" in workflow
    assert "scripts/browser_uat.py" in workflow
    assert "name: m2m-browser-uat" in workflow
    assert "scripts/serve_preview.py" in workflow
    assert "python -m http.server" not in workflow
    assert 'protocol_version = "HTTP/1.1"' in server
    assert 'default="127.0.0.1"' in server
    uat = (ROOT / "scripts/browser_uat.py").read_text(encoding="utf-8")
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    assert "len(SELECTED_PATHWAYS)" in uat
    assert 'section.querySelectorAll(".selected-pathway-row").length' in app


def test_actions_checkouts_do_not_persist_credentials() -> None:
    for relative in (
        ".github/workflows/browser-uat.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/pages.yml",
        ".github/workflows/release.yml",
    ):
        workflow = (ROOT / relative).read_text(encoding="utf-8")
        assert workflow.count("uses: actions/checkout@") == workflow.count("persist-credentials: false")


def test_pages_summary_fences_are_literal_and_verification_remains_fail_closed() -> None:
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert "printf '%s\\n' '```json'" in workflow
    assert "printf '%s\\n' '```'" in workflow
    assert '"```json"' not in workflow
    verify_step = workflow.split("- name: Verify anonymous production bytes", 1)[1].split("- name: Preserve production attestation", 1)[0]
    assert "set -euo pipefail" in verify_step
    assert "scripts/verify_production.py" in verify_step


def test_release_title_is_derived_from_version_matched_notes_h1() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    notes_h1 = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8").splitlines()[0]
    assert notes_h1 == "# Materials-to-Mission v0.7.4 - Dependency Security and Manifest Visibility"
    assert "release_title=\"$(sed -n '1s/^# //p' \"$notes_file\")\"" in workflow
    assert 'expected_title_prefix="Materials-to-Mission ${GITHUB_REF_NAME}"' in workflow
    assert '"$expected_title_prefix"|"$expected_title_prefix — "*|"$expected_title_prefix - "*)' in workflow
    assert 'echo "Unsupported release title: $release_title" >&2' in workflow
    assert '--title "$release_title"' in workflow
    assert '--title "Materials-to-Mission ${GITHUB_REF_NAME}' not in workflow
