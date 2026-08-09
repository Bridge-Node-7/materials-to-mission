from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas", ROOT / "src/materials_to_mission/resources/schemas"),
    (ROOT / "policy", ROOT / "src/materials_to_mission/resources/policy"),
]


def expected_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for source_dir, target_dir in PAIRS:
        for source in sorted(source_dir.glob("*.json")):
            files.append((source, target_dir / source.name))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if packaged resources differ from canonical files")
    args = parser.parse_args()

    mismatches: list[str] = []
    for source, target in expected_files():
        if args.check:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                mismatches.append(target.relative_to(ROOT).as_posix())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    if args.check and mismatches:
        raise SystemExit(
            "STOP - packaged resources are stale: " + ", ".join(mismatches) +
            "; run `python scripts/check_repo.py --update-evidence`, review the diff, and rerun"
        )
    print("PASS - packaged resources match canonical files" if args.check else "PASS - resources synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
