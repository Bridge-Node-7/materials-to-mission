from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from materials_to_mission.validation_evidence import (  # noqa: E402
    COVERAGE_FLOOR_PERCENT,
    parse_pytest_junit,
    render_validation_report,
    validate_pytest_summary,
)


PYTHON = sys.executable
GENERATED = [
    ROOT / "build",
    ROOT / "dist",
    ROOT / ".pytest_cache",
    ROOT / "htmlcov",
    ROOT / ".coverage",
]


def run(*args: str) -> None:
    print("WORKING -", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def clean_generated() -> None:
    for path in GENERATED:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
    for path in ROOT.rglob("*.py[co]"):
        path.unlink(missing_ok=True)
    print("PASS - generated state cleaned")


def symlink_is_permitted(*, tracked: bool, ignored: bool) -> bool:
    """Permit only untracked symlinks inside Git-ignored local/generated paths."""
    return ignored and not tracked


def _git_path_state(path: Path) -> tuple[bool, bool]:
    relative = path.relative_to(ROOT).as_posix()
    tracked = (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )
    ignored = (
        subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", "--", relative],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )
    return tracked, ignored


def check_symlinks() -> None:
    ignored_local = 0
    for path in ROOT.rglob("*"):
        if not path.is_symlink():
            continue
        tracked, ignored = _git_path_state(path)
        if not symlink_is_permitted(tracked=tracked, ignored=ignored):
            raise SystemExit(
                "STOP - symbolic links are permitted only in untracked, "
                f"Git-ignored local/generated paths: {path}"
            )
        ignored_local += 1
    print(
        "PASS - no tracked or unignored symbolic links"
        f"; ignored local symlinks observed: {ignored_local}"
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument(
        "--update-evidence",
        action="store_true",
        help=(
            "refresh packaged resources, VALIDATION_REPORT.md, and "
            "REPO_FILE_MANIFEST.sha256 after reviewing source changes"
        ),
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    print("WAIT - Materials-to-Mission complete local gate")
    clean_generated()
    run(
        PYTHON,
        "scripts/sync_resources.py",
        *([] if args.update_evidence else ["--check"]),
    )
    run(PYTHON, "-m", "compileall", "-q", "src", "scripts", "tests")

    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {"dist", "build", ".venv"} for part in path.parts):
            continue
        json.loads(path.read_text(encoding="utf-8"))
    print("PASS - JSON parsing")

    run(
        PYTHON,
        "-m",
        "coverage",
        "run",
        "-m",
        "pytest",
        "--junitxml=build/pytest-junit.xml",
    )
    run(PYTHON, "-m", "coverage", "report")
    run(PYTHON, "-m", "coverage", "json", "-o", "build/coverage.json")

    coverage_data = json.loads(
        (ROOT / "build/coverage.json").read_text(encoding="utf-8")
    )
    coverage_percent = coverage_data["totals"]["percent_covered"]
    if coverage_percent < COVERAGE_FLOOR_PERCENT:
        raise SystemExit(
            f"STOP - coverage below {COVERAGE_FLOOR_PERCENT:.0f} percent: "
            f"{coverage_percent:.2f}"
        )

    try:
        pytest_summary = parse_pytest_junit(ROOT / "build/pytest-junit.xml")
        validate_pytest_summary(pytest_summary)
    except ValueError as exc:
        raise SystemExit(f"STOP - pytest evidence is invalid: {exc}") from exc
    test_count = pytest_summary.tests

    run(PYTHON, "scripts/check_links.py")
    run(PYTHON, "scripts/check_gate_contracts.py")
    run(
        PYTHON,
        "-m",
        "materials_to_mission",
        "validate",
        "examples/synthetic-critical-material-pathway/case.json",
        "--public",
    )

    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        for line in workflow.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("uses:"):
                value = stripped.split("uses:", 1)[1].strip().split()[0]
                if not re.search(r"@[0-9a-f]{40}$", value):
                    raise SystemExit(
                        f"STOP - unpinned GitHub Action in {workflow}: {value}"
                    )
    print("PASS - GitHub Actions pinned to full commit identifiers")

    check_symlinks()

    report = render_validation_report(test_count)
    report_path = ROOT / "VALIDATION_REPORT.md"
    if args.update_evidence:
        report_path.write_text(report, encoding="utf-8")
        run(PYTHON, "scripts/build_manifest.py")
    else:
        observed = (
            report_path.read_text(encoding="utf-8")
            if report_path.exists()
            else ""
        )
        if observed != report:
            raise SystemExit(
                "STOP - VALIDATION_REPORT.md is stale; run "
                "`python scripts/check_repo.py --update-evidence`, "
                "review the diff, and rerun"
            )
        run(PYTHON, "scripts/build_manifest.py", "--check")

    with tempfile.TemporaryDirectory() as tmp:
        first = Path(tmp) / "first.zip"
        second = Path(tmp) / "second.zip"
        sys.path.insert(0, str(ROOT / "src"))
        from materials_to_mission.release import (  # noqa: PLC0415
            build_deterministic_zip,
            sha256,
        )

        build_deterministic_zip(ROOT, first)
        build_deterministic_zip(ROOT, second)
        if sha256(first) != sha256(second):
            raise SystemExit("STOP - deterministic archives differ")
    print("PASS - deterministic packaging")

    if (ROOT / "dist").exists():
        shutil.rmtree(ROOT / "dist")
    run(PYTHON, "scripts/build_release.py")
    print("PASS - Materials-to-Mission complete local gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
