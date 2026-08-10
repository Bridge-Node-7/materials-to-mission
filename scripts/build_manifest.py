from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "REPO_FILE_MANIFEST.sha256"
EXCLUDED = {".git", ".venv", "venv", "dist", "build", ".pytest_cache", "__pycache__", "htmlcov"}


def _write_utf8_lf(path: Path, text: str) -> None:
    path.write_bytes(
        text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    )


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if path == OUTPUT or any(part in EXCLUDED or part.endswith(".egg-info") for part in rel.parts):
        return False
    return path.is_file() and path.name != ".coverage" and path.suffix not in {".pyc", ".pyo"}


def canonical_relative(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def canonical_file_bytes(path: Path) -> bytes:
    # Normalize UTF-8 text to LF while preserving exact binary bytes.
    raw = path.read_bytes()
    if b"\x00" in raw:
        return raw
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def manifest_digest(path: Path) -> str:
    return hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def expected_text() -> str:
    lines = []
    paths = (p for p in ROOT.rglob("*") if include(p))
    for path in sorted(paths, key=canonical_relative):
        digest = manifest_digest(path)
        lines.append(f"{digest}  {canonical_relative(path)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the checked-in manifest is stale")
    args = parser.parse_args()

    expected = expected_text()
    if args.check:
        observed = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if observed != expected:
            raise SystemExit(
                "STOP - REPO_FILE_MANIFEST.sha256 is stale; run "
                "`python scripts/check_repo.py --update-evidence`, review the diff, and rerun"
            )
        print(f"PASS - {OUTPUT.name} matches {len(expected.splitlines())} entries")
        return 0

    _write_utf8_lf(OUTPUT, expected)
    print(f"PASS - wrote {OUTPUT.name} with {len(expected.splitlines())} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
