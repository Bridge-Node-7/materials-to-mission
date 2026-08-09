
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from .errors import MaterialsToMissionError

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    "__pycache__",
    "htmlcov",
    "*.egg-info",
}
EXCLUDED_FILES = {".coverage"}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def _is_excluded(relative: Path) -> bool:
    return any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in relative.parts)


def _include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if _is_excluded(relative):
        return False
    if path.name in EXCLUDED_FILES or path.suffix in {".pyc", ".pyo"}:
        return False
    if path.is_symlink():
        raise MaterialsToMissionError(
            f"symbolic links are not permitted in a release root: {relative.as_posix()}"
        )
    return path.is_file()


def _archive_mode(relative: Path) -> int:
    return 0o755 if relative.suffix == ".sh" else 0o644


def _validate_output_location(root: Path, output: Path) -> None:
    try:
        relative_parent = output.parent.relative_to(root)
    except ValueError:
        return
    if not relative_parent.parts:
        raise MaterialsToMissionError(
            "the package output directory cannot be the repository root; "
            "use dist, build, or a directory outside the release root"
        )
    first = relative_parent.parts[0]
    if first not in EXCLUDED_DIRS and not first.endswith(".egg-info"):
        raise MaterialsToMissionError(
            "an output directory inside the repository must be excluded from the archive; "
            "use dist, build, or a directory outside the release root"
        )


def build_deterministic_zip(root: str | Path, output: str | Path) -> Path:
    root_path = Path(root).resolve()
    output_path = Path(output).resolve()
    _validate_output_location(root_path, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path
        for path in root_path.rglob("*")
        if _include(path, root_path) and path.resolve() != output_path
    )
    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            relative = path.relative_to(root_path).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = _archive_mode(Path(relative)) << 16
            archive.writestr(info, path.read_bytes())
    return output_path


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
