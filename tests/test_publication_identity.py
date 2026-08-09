from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_publication_kit", ROOT / "scripts/check_publication_kit.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


COMMIT = "a" * 40
TREE = "b" * 40
PREVIOUS = "c" * 40
TIMESTAMP = "2026-08-09T01:30:00Z"


def identity() -> dict[str, object]:
    return {
        "repository": "Bridge-Node-7/materials-to-mission",
        "version": "v0.1.0",
        "source_archive_sha256": "d" * 64,
        "git_bundle_sha256": "e" * 64,
        "commit": COMMIT,
        "tree": TREE,
        "bootstrap_commit_timestamp": TIMESTAMP,
        "predecessor_commit": PREVIOUS,
    }


def manifest() -> dict[str, object]:
    return {
        "version": "0.1.0",
        "tag": "v0.1.0",
        "commit": COMMIT,
        "tree": TREE,
        "sha256": "d" * 64,
        "bootstrap_commit_timestamp": TIMESTAMP,
    }


def env() -> dict[str, str]:
    return {
        "FULL_REPO": "Bridge-Node-7/materials-to-mission",
        "TAG": "v0.1.0",
        "APPROVED_COMMIT": COMMIT,
        "APPROVED_TREE": TREE,
        "BUNDLE_SHA256": "e" * 64,
        "EXPECTED_SOURCE_ARCHIVE_SHA256": "d" * 64,
    }


def test_publication_identity_accepts_coherent_metadata() -> None:
    MODULE.validate_identity_metadata(identity(), manifest(), env())


def test_publication_identity_rejects_same_predecessor() -> None:
    candidate = identity()
    candidate["predecessor_commit"] = COMMIT
    with pytest.raises(SystemExit, match="predecessor_commit must differ"):
        MODULE.validate_identity_metadata(candidate, manifest(), env())


def test_publication_identity_rejects_timestamp_mismatch() -> None:
    release = manifest()
    release["bootstrap_commit_timestamp"] = "2026-08-09T01:31:00Z"
    with pytest.raises(SystemExit, match="bootstrap timestamp mismatch"):
        MODULE.validate_identity_metadata(identity(), release, env())


def test_publication_identity_rejects_environment_mismatch() -> None:
    candidate_env = env()
    candidate_env["APPROVED_COMMIT"] = PREVIOUS
    with pytest.raises(SystemExit, match="release-candidate.env mismatch"):
        MODULE.validate_identity_metadata(identity(), manifest(), candidate_env)


def test_complete_manifest_rejects_unlisted_file(tmp_path: Path) -> None:
    (tmp_path / "listed.txt").write_text("listed\n", encoding="utf-8")
    (tmp_path / "unlisted.txt").write_text("unlisted\n", encoding="utf-8")
    digest = MODULE.sha256(tmp_path / "listed.txt")
    (tmp_path / "KIT_SHA256SUMS").write_text(
        f"{digest}  listed.txt\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="manifest coverage mismatch"):
        MODULE.verify_manifest(tmp_path, "KIT_SHA256SUMS", require_complete=True)
