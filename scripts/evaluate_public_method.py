from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = "examples/synthetic-critical-material-pathway/case.json"
INVALID = "examples/invalid/missing-human-owner.json"
OUTPUT = "build/guided-decision-passport.md"
PROFILE = "m0-strict-0.2.0"

def toolkit_available() -> bool:
    return importlib.util.find_spec("materials_to_mission") is not None

def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "materials_to_mission", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

def stop(label: str, result: subprocess.CompletedProcess[str] | None = None) -> int:
    print(f"STOP - {label}")
    if result is not None:
        if result.stdout:
            print(result.stdout.rstrip(), file=sys.stderr)
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
    return 1

def main() -> int:
    print("WAIT - Materials-to-Mission guided public evaluation")
    if not toolkit_available():
        print("STOP - toolkit is not installed in this environment")
        print("NEXT - complete the documented install and rerun.")
        return 1
    print("PASS - TOOLKIT AVAILABLE")
    print("WORKING - validate the synthetic public reference")
    valid = run_cli("validate", REFERENCE, "--public", "--profile", PROFILE)
    if valid.returncode != 0:
        return stop("synthetic reference did not validate", valid)
    print("PASS - SYNTHETIC CASE VALID")
    print("WORKING - render the Decision Passport")
    rendered = run_cli("render", REFERENCE, "--output", OUTPUT, "--profile", PROFILE)
    if rendered.returncode != 0:
        return stop("Decision Passport was not written", rendered)
    print("PASS - DECISION PASSPORT WRITTEN")
    print("WORKING - confirm one intentional fail-closed example")
    invalid = run_cli("validate", INVALID, "--public", "--json", "--profile", PROFILE)
    try:
        payload = json.loads(invalid.stdout)
    except json.JSONDecodeError:
        return stop("invalid fixture did not return JSON findings", invalid)
    if invalid.returncode != 2 or payload.get("valid") is not False:
        return stop("invalid fixture did not fail closed with exit code 2", invalid)
    if payload.get("validation_profile") != PROFILE:
        return stop("invalid fixture did not report the explicit validation profile", invalid)
    print("PASS - FAIL-CLOSED EXAMPLE CONFIRMED")
    print(f"NEXT - OPEN {OUTPUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
