from pathlib import Path
import os
import zipfile

import pytest

from materials_to_mission.errors import MaterialsToMissionError
from materials_to_mission.release import _archive_mode, _include, build_deterministic_zip, sha256


def test_deterministic_release(root, tmp_path):
    first = build_deterministic_zip(root, tmp_path / "first.zip")
    second = build_deterministic_zip(root, tmp_path / "second.zip")
    assert sha256(first) == sha256(second)


def test_release_excludes_transient_directories(root, tmp_path):
    archive = build_deterministic_zip(root, tmp_path / "release.zip")
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    assert not any("/.git/" in f"/{name}" for name in names)
    assert not any("/__pycache__/" in f"/{name}" for name in names)
    assert not any(name.startswith("dist/") for name in names)



def test_source_release_manifest_is_explicitly_unbound(root, tmp_path):
    import json
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["M2M_RELEASE_MODE"] = "source"
    subprocess.run([sys.executable, "scripts/build_release.py"], cwd=root, env=env, check=True)
    manifest = json.loads((root / "dist/release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "source"
    assert manifest["git_bound"] is False


def test_candidate_manifest_fails_without_exact_identity(root):
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["M2M_RELEASE_MODE"] = "candidate"
    env.pop("GITHUB_SHA", None)
    env.pop("GITHUB_REF_NAME", None)
    result = subprocess.run([sys.executable, "scripts/build_release.py"], cwd=root, env=env, check=False, text=True, capture_output=True)
    assert result.returncode != 0
    assert "requires exact commit, tree, and tag" in result.stdout + result.stderr


def test_archive_modes_are_platform_independent():
    assert _archive_mode(Path("operator.sh")) == 0o755
    assert _archive_mode(Path("README.md")) == 0o644


def test_archive_records_normalized_modes(tmp_path):
    fixture = tmp_path / "root"
    fixture.mkdir()
    (fixture / "operator.sh").write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
    (fixture / "README.md").write_text("example\n", encoding="utf-8")
    archive = tmp_path / "modes.zip"
    build_deterministic_zip(fixture, archive)
    with zipfile.ZipFile(archive) as handle:
        shell_mode = (handle.getinfo("operator.sh").external_attr >> 16) & 0o777
        readme_mode = (handle.getinfo("README.md").external_attr >> 16) & 0o777
    assert shell_mode == 0o755
    assert readme_mode == 0o644

def test_release_excludes_coverage_file(tmp_path):
    coverage_file = tmp_path / ".coverage"
    coverage_file.write_bytes(b"transient")
    assert _include(coverage_file, tmp_path) is False



def test_release_rejects_public_symlink(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    link = root / "leak.txt"
    try:
        os.symlink("/etc/hosts", link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable in this environment")
    with pytest.raises(MaterialsToMissionError, match="symbolic links are not permitted"):
        build_deterministic_zip(root, tmp_path / "release.zip")


def test_release_ignores_symlink_inside_excluded_directory(tmp_path):
    root = tmp_path / "root"
    excluded = root / ".venv"
    excluded.mkdir(parents=True)
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    link = excluded / "ignored-link"
    try:
        os.symlink("/etc/hosts", link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable in this environment")
    archive = build_deterministic_zip(root, tmp_path / "release.zip")
    with zipfile.ZipFile(archive) as handle:
        assert not any(name.startswith(".venv/") for name in handle.namelist())


def test_release_rejects_output_in_repository_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    with pytest.raises(MaterialsToMissionError, match="cannot be the repository root"):
        build_deterministic_zip(root, root / "release.zip")


def test_release_rejects_nonexcluded_internal_output_directory(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    with pytest.raises(MaterialsToMissionError, match="must be excluded"):
        build_deterministic_zip(root, root / "artifacts/release.zip")


def test_release_allows_dist_and_external_output(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (root / "README.md").write_text("example\n", encoding="utf-8")
    internal = build_deterministic_zip(root, root / "dist/release.zip")
    external = build_deterministic_zip(root, tmp_path / "external/release.zip")
    assert sha256(internal) == sha256(external)
