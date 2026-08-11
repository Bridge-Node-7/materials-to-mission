from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github/workflows/release.yml"

if not workflow.is_file():
    raise SystemExit("STOP - hosted Release workflow is missing")

text = workflow.read_text(encoding="utf-8")

for required in (
    "gh release create",
    "--draft",
    "git diff --exit-code",
    'notes_file="RELEASE_NOTES_${GITHUB_REF_NAME}.md"',
    'archive="dist/materials-to-mission-${GITHUB_REF_NAME}.zip"',
    'test "$manifest_tag" = "$GITHUB_REF_NAME"',
    'assert data["tag"] == f"v{data',
):
    if required not in text:
        raise SystemExit(f"STOP - hosted Release workflow contract missing: {required}")

for forbidden in (
    "RELEASE_NOTES_v0.1.0.md",
    "dist/materials-to-mission-v0.1.0.zip",
):
    if forbidden in text:
        raise SystemExit(f"STOP - hosted Release workflow contains hard-coded release identity: {forbidden}")

print("PASS - hosted Release workflow contract")
