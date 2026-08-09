from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "REPO_FILE_MANIFEST.sha256"
EXCLUDED = {".git", ".venv", "venv", "dist", "build", ".pytest_cache", "__pycache__", "htmlcov"}


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if path == OUTPUT or any(part in EXCLUDED or part.endswith(".egg-info") for part in rel.parts):
        return False
    return path.is_file() and path.name != ".coverage" and path.suffix not in {".pyc", ".pyo"}


def expected_text() -> str:
    lines = []
    for path in sorted(p for p in ROOT.rglob("*") if include(p)):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
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

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"PASS - wrote {OUTPUT.name} with {len(expected.splitlines())} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
