from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_public_surface_is_lean() -> None:
    assert not (ROOT / "GATES").exists()
    assert not (ROOT / "SUPERSESSION.md").exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for forbidden in (
        "## Maintainers Only", "Planning a protected case?", "Reviewing future options and boundaries?",
        "FINAL_GITHUB_PUBLIC_RELEASE_PLAN", "DEPLOYMENT_DEP00", "UAT_WEB03",
    ):
        assert forbidden not in readme
    assert len(readme.splitlines()) <= 150

def test_only_current_release_notes_live_at_repository_root() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    observed = sorted(path.name for path in ROOT.glob("RELEASE_NOTES_v*.md"))
    assert observed == [f"RELEASE_NOTES_v{version}.md"]

def test_docs_surface_is_bounded() -> None:
    docs = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "docs").glob("*") if path.is_file())
    assert len(docs) <= 25
    for forbidden in (
        "docs/FINAL_GITHUB_PUBLIC_RELEASE_PLAN.md", "docs/DEPLOYMENT_DEP00.md", "docs/UAT_WEB03.md",
        "docs/M1_CASE_001_PLAYBOOK.md", "docs/PROGRAM_REGISTER.md",
    ):
        assert forbidden not in docs

def test_public_use_routes_remain() -> None:
    for relative in (
        "docs/START_HERE.md", "docs/FIVE_MINUTE_EVALUATION.md", "docs/METHOD.md",
        "docs/EVIDENCE_MODEL.md", "docs/MATERIAL_ASSURANCE_RECORD.md", "docs/DECISION_PASSPORT.md",
        "docs/INTEROPERABILITY.md", "docs/VALIDATION.md", "docs/PUBLIC_BOUNDARY.md",
        "SECURITY.md", "CONTRIBUTING.md", "LICENSE",
    ):
        assert (ROOT / relative).exists(), relative
