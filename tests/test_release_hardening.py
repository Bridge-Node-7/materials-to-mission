from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_packaged_resources_check_is_non_mutating() -> None:
    before = {
        p.relative_to(ROOT).as_posix(): p.read_bytes()
        for p in (ROOT / "src/materials_to_mission/resources").rglob("*.json")
    }
    subprocess.run([sys.executable, "scripts/sync_resources.py", "--check"], cwd=ROOT, check=True)
    after = {
        p.relative_to(ROOT).as_posix(): p.read_bytes()
        for p in (ROOT / "src/materials_to_mission/resources").rglob("*.json")
    }
    assert before == after


def test_publication_kit_validator_rejects_missing_gate_set(tmp_path: Path) -> None:
    required = [
        "materials-to-mission-v0.1.0.zip",
        "materials-to-mission-v0.1.0.gitbundle",
        "REPO_FILE_MANIFEST.sha256",
        "VALIDATION_REPORT.md",
        "SHA256SUMS",
        "release-candidate.env",
    ]
    for name in required:
        (tmp_path / name).write_text("fixture\n", encoding="utf-8")
    (tmp_path / "CANDIDATE_IDENTITY.json").write_text(json.dumps({
        "repository": "Bridge-Node-7/materials-to-mission",
        "version": "v0.1.0",
        "source_archive_sha256": "a",
        "git_bundle_sha256": "b",
        "commit": "c",
        "tree": "d",
    }), encoding="utf-8")
    (tmp_path / "GATES").mkdir()
    result = subprocess.run(
        [sys.executable, "scripts/check_publication_kit.py", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "gate set mismatch" in result.stdout + result.stderr


def test_manifest_sort_key_is_posix_relative_and_case_sensitive() -> None:
    import importlib.util
    from pathlib import PureWindowsPath

    spec = importlib.util.spec_from_file_location(
        "build_manifest", ROOT / "scripts/build_manifest.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    root = PureWindowsPath("C:/repo")
    paths = [
        root / ".github/dependabot.yml",
        root / ".github/ISSUE_TEMPLATE/bug.yml",
    ]
    ordered = sorted(paths, key=lambda path: module.canonical_relative(path, root))
    assert [module.canonical_relative(path, root) for path in ordered] == [
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/dependabot.yml",
    ]


def test_release_archive_member_order_uses_posix_paths(tmp_path: Path) -> None:
    from materials_to_mission.release import build_deterministic_zip
    import zipfile

    root = tmp_path / "root"
    (root / ".github/ISSUE_TEMPLATE").mkdir(parents=True)
    (root / ".github/ISSUE_TEMPLATE/bug.yml").write_text("bug\n", encoding="utf-8")
    (root / ".github/dependabot.yml").write_text("deps\n", encoding="utf-8")

    archive = build_deterministic_zip(root, tmp_path / "release.zip")
    with zipfile.ZipFile(archive) as handle:
        assert handle.namelist() == [
            ".github/ISSUE_TEMPLATE/bug.yml",
            ".github/dependabot.yml",
        ]
