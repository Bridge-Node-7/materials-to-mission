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
