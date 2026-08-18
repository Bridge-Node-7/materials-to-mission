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
):
    if required not in text:
        raise SystemExit(f"STOP - hosted Release workflow contract missing: {required}")

if re.search(r'notes_file="RELEASE_NOTES_v\d+\.\d+\.\d+\.md"', text):
    raise SystemExit("STOP - hosted Release workflow uses version-per-release notes filename")

if "dist/materials-to-mission-v0.1.0.zip" in text:
    raise SystemExit("STOP - hosted Release workflow contains hard-coded release identity")

print("PASS - hosted Release workflow contract")
