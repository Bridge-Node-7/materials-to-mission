from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github/workflows/release.yml"

if not workflow.is_file():
    raise SystemExit("STOP - hosted Release workflow is missing")

text = workflow.read_text(encoding="utf-8")

for required in (
    "gh release create",
    "--draft",
    "git diff --exit-code",
    'notes_file="RELEASE_NOTES.md"',
    'archive="dist/materials-to-mission-${GITHUB_REF_NAME}.zip"',
    'test "$manifest_tag" = "$GITHUB_REF_NAME"',
    'assert data["tag"] == f"v{data',
    "m2m-stable-release-candidate",
    "RELEASE_CANDIDATE_SHA256SUMS",
):
    if required not in text:
        raise SystemExit(f"STOP - hosted Release workflow contract missing: {required}")

if re.search(r'notes_file="RELEASE_NOTES_v\d+\.\d+\.\d+\.md"', text):
    raise SystemExit("STOP - hosted Release workflow uses version-per-release notes filename")

if "dist/materials-to-mission-v0.1.0.zip" in text:
    raise SystemExit("STOP - hosted Release workflow contains hard-coded release identity")

head, jobs = text.split("\njobs:\n", 1)
if "permissions:\n  contents: read" not in head:
    raise SystemExit("STOP - Release workflow must default to read-only contents")

build, publish = jobs.split("\n  publish:\n", 1)
if "contents: write" in build:
    raise SystemExit("STOP - build/validation job must not hold publication authority")
for required in ("contents: read", "actions/upload-artifact@", "Install locked dependencies and validate"):
    if required not in build:
        raise SystemExit(f"STOP - read-only build handoff missing: {required}")

for required in ("actions: read", "contents: write", "actions/download-artifact@", "Verify sealed candidate and tag identity"):
    if required not in publish:
        raise SystemExit(f"STOP - minimal publish handoff missing: {required}")
for prohibited in ("actions/checkout@", "actions/setup-python@", "pip install", "python scripts/"):
    if prohibited in publish:
        raise SystemExit(f"STOP - publish job executes mutable source/toolchain step: {prohibited}")

print("PASS - hosted Release workflow contract")
