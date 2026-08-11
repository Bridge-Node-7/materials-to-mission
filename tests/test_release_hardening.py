from __future__ import annotations

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


def test_manifest_hash_is_line_ending_independent(tmp_path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_manifest_line_endings", ROOT / "scripts/build_manifest.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    cr = tmp_path / "cr.txt"
    lf.write_bytes(b"alpha\nbeta\n")
    crlf.write_bytes(b"alpha\r\nbeta\r\n")
    cr.write_bytes(b"alpha\rbeta\r")

    expected = module.manifest_digest(lf)
    assert module.manifest_digest(crlf) == expected
    assert module.manifest_digest(cr) == expected


def test_manifest_hash_preserves_binary_bytes(tmp_path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_manifest_binary", ROOT / "scripts/build_manifest.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    binary = tmp_path / "fixture.bin"
    raw = b"\x00alpha\r\nbeta\xff"
    binary.write_bytes(raw)

    assert module.canonical_file_bytes(binary) == raw
    assert module.manifest_digest(binary) == module.hashlib.sha256(raw).hexdigest()


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

def test_release_archive_uses_canonical_host_independent_metadata(tmp_path: Path) -> None:
    from materials_to_mission.release import (
        CANONICAL_COMPRESSION,
        CANONICAL_CREATE_SYSTEM,
        CANONICAL_ZIP_VERSION,
        FIXED_TIME,
        build_deterministic_zip,
    )
    import zipfile

    root = tmp_path / "root"
    root.mkdir()
    (root / "README.md").write_text("example\n", encoding="utf-8")

    archive = build_deterministic_zip(root, tmp_path / "release.zip")
    with zipfile.ZipFile(archive) as handle:
        info = handle.getinfo("README.md")
        assert info.create_system == CANONICAL_CREATE_SYSTEM
        assert info.create_version == CANONICAL_ZIP_VERSION
        assert info.extract_version == CANONICAL_ZIP_VERSION
        assert info.date_time == FIXED_TIME
        assert info.compress_type == CANONICAL_COMPRESSION == zipfile.ZIP_STORED
        assert info.extra == b""
        assert info.comment == b""


def test_release_archive_ignores_windows_zipinfo_defaults(
    tmp_path: Path, monkeypatch
) -> None:
    import materials_to_mission.release as release

    root = tmp_path / "root"
    root.mkdir()
    (root / "README.md").write_text("example\n", encoding="utf-8")

    baseline = release.build_deterministic_zip(root, tmp_path / "baseline.zip")
    original_zip_info = release.zipfile.ZipInfo

    class WindowsDefaultZipInfo(original_zip_info):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.create_system = 0

    monkeypatch.setattr(release.zipfile, "ZipInfo", WindowsDefaultZipInfo)
    simulated_windows = release.build_deterministic_zip(
        root, tmp_path / "simulated-windows.zip"
    )

    assert baseline.read_bytes() == simulated_windows.read_bytes()


def test_generated_release_evidence_writers_force_lf_bytes(tmp_path: Path) -> None:
    import importlib.util

    cases = [
        (
            "check_repo_lf_writer",
            ROOT / "scripts/check_repo.py",
            "_write_utf8_lf(report_path, report)",
        ),
        (
            "build_manifest_lf_writer",
            ROOT / "scripts/build_manifest.py",
            "_write_utf8_lf(OUTPUT, expected)",
        ),
    ]

    for module_name, script_path, expected_call in cases:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        target = tmp_path / f"{module_name}.txt"
        module._write_utf8_lf(target, "alpha\r\nbeta\r\n")

        assert target.read_bytes() == b"alpha\nbeta\n"
        assert expected_call in script_path.read_text(encoding="utf-8")
