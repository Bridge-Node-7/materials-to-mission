from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()


def patterns() -> list[re.Pattern[str]]:
    # Build signatures in pieces so this scanner does not contain the complete
    # sensitive path forms it is designed to detect.
    unix_users = "/" + "Users" + "/"
    msys_users = "/c" + unix_users
    home_users = "/" + "home" + "/"
    windows_users = "C:" + "\\" + "Users" + "\\"
    return [
        re.compile(re.escape(msys_users)),
        re.compile(re.escape(unix_users)),
        re.compile(re.escape(home_users)),
        re.compile(re.escape(windows_users), re.IGNORECASE),
    ]


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = (ROOT / raw.decode("utf-8")).resolve()
        if path != SELF and path.is_file():
            paths.append(path)
    return paths


def staged_added_text() -> str:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--no-ext-diff",
            "--unified=0",
            "--",
            ".",
            ":(exclude).githooks/pre-commit",
            ":(exclude)scripts/check_privacy.py",
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    lines: list[str] = []
    for raw in result.stdout.decode("utf-8", errors="replace").splitlines():
        if raw.startswith("+") and not raw.startswith("+++"):
            lines.append(raw[1:])
    return "\n".join(lines)


def find_matches(text: str) -> list[str]:
    return [pattern.pattern for pattern in patterns() if pattern.search(text)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    if args.staged:
        if find_matches(staged_added_text()):
            failures.append("staged additions")
    else:
        for path in tracked_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if find_matches(text):
                failures.append(path.relative_to(ROOT).as_posix())

    if failures:
        print("STOP - absolute machine path detected in: " + ", ".join(failures))
        return 1

    scope = "staged additions" if args.staged else "tracked text files"
    print(f"PASS - privacy path scan ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
