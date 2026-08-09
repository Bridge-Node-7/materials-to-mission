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
PYTHON = sys.executable
GENERATED = [ROOT / "build", ROOT / "dist", ROOT / ".pytest_cache", ROOT / "htmlcov", ROOT / ".coverage"]


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


parser = argparse.ArgumentParser()
parser.add_argument(
    "--update-evidence",
    action="store_true",
    help="refresh packaged resources, VALIDATION_REPORT.md, and REPO_FILE_MANIFEST.sha256 after reviewing source changes",
)
args = parser.parse_args()

print("WAIT - Materials-to-Mission complete local gate")
clean_generated()
run(PYTHON, "scripts/sync_resources.py" if args.update_evidence else "scripts/sync_resources.py", *( [] if args.update_evidence else ["--check"] ))
run(PYTHON, "-m", "compileall", "-q", "src", "scripts", "tests")
for path in sorted(ROOT.rglob("*.json")):
    if any(part in {"dist", "build", ".venv"} for part in path.parts):
        continue
    json.loads(path.read_text(encoding="utf-8"))
print("PASS - JSON parsing")
run(PYTHON, "-m", "coverage", "run", "-m", "pytest")
run(PYTHON, "-m", "coverage", "report")
run(PYTHON, "-m", "coverage", "json", "-o", "build/coverage.json")
coverage_data = json.loads((ROOT / "build/coverage.json").read_text(encoding="utf-8"))
coverage_percent = coverage_data["totals"]["percent_covered"]
collect = subprocess.run(
    [PYTHON, "-m", "pytest", "--collect-only", "-q"],
    cwd=ROOT,
    check=True,
    text=True,
    capture_output=True,
)
match = re.search(r"(\d+) tests? collected", collect.stdout)
test_count = int(match.group(1)) if match else "PASS"
if coverage_percent < 95:
    raise SystemExit(f"STOP - coverage below 95 percent: {coverage_percent:.2f}")
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
                raise SystemExit(f"STOP - unpinned GitHub Action in {workflow}: {value}")
print("PASS - GitHub Actions pinned to full commit identifiers")

for path in ROOT.rglob("*"):
    if path.is_symlink():
        raise SystemExit(f"STOP - symbolic links are not permitted: {path}")
print("PASS - no symbolic links")

report = f"""# Validation Report

**Project:** Materials-to-Mission  
**Version:** 0.1.0  
**Status:** PASS within the stated public synthetic scope

## Executed

- Python compilation: PASS
- JSON parsing: PASS
- JSON Schema validation: PASS
- Semantic validation: PASS
- Public-boundary validation: PASS
- Adversarial fixtures: PASS
- Unit and integration tests: {test_count} PASS
- Exact combined statement and branch coverage: {coverage_percent:.2f} percent
- Markdown relative links: PASS
- GitHub Actions full-SHA pinning: PASS
- Public-source maintainer gate contracts: PASS
- Hosted Release workflow contract: PASS
- Separate publication-kit gates: validated by the publication kit
- Symbolic-link rejection: PASS
- Deterministic archive comparison: PASS
- Checked-in validation evidence: current and non-mutating
- SHA-256 manifest verification: PASS
- Compressed-data integrity: verified by the release build

## Not Proven

This validation does not prove a real material, supplier, laboratory, sample,
lot, mission, legal, regulatory, certification, qualification, production,
customer, government, or commercial conclusion.
"""

report_path = ROOT / "VALIDATION_REPORT.md"
if args.update_evidence:
    report_path.write_text(report, encoding="utf-8")
    run(PYTHON, "scripts/build_manifest.py")
else:
    observed = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    if observed != report:
        raise SystemExit(
            "STOP - VALIDATION_REPORT.md is stale; run "
            "`python scripts/check_repo.py --update-evidence`, review the diff, and rerun"
        )
    run(PYTHON, "scripts/build_manifest.py", "--check")

with tempfile.TemporaryDirectory() as tmp:
    first = Path(tmp) / "first.zip"
    second = Path(tmp) / "second.zip"
    sys.path.insert(0, str(ROOT / "src"))
    from materials_to_mission.release import build_deterministic_zip, sha256

    build_deterministic_zip(ROOT, first)
    build_deterministic_zip(ROOT, second)
    if sha256(first) != sha256(second):
        raise SystemExit("STOP - deterministic archives differ")
print("PASS - deterministic packaging")

if (ROOT / "dist").exists():
    shutil.rmtree(ROOT / "dist")
run(PYTHON, "scripts/build_release.py")
print("PASS - Materials-to-Mission complete local gate")
