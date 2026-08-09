from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "GATES"
EXPECTED = {
    "00_VALIDATE_CANONICAL_SOURCE.sh",
    "01_VERIFY_PUBLICATION_KIT_BOUNDARY.sh",
}
observed = {p.name for p in GATES.glob("*.sh")}
if observed != EXPECTED:
    raise SystemExit(f"STOP - source gate set mismatch: expected {sorted(EXPECTED)}, observed {sorted(observed)}")

joined = "\n".join((GATES / name).read_text(encoding="utf-8") for name in EXPECTED)
for forbidden in (
    "gh repo create",
    "git push",
    "gh release create",
    "gh repo edit",
    "private-vulnerability-reporting",
    "immutable-releases",
):
    if forbidden in joined:
        raise SystemExit(f"STOP - public mutation pattern found in source-maintainer gates: {forbidden}")

gate0 = (GATES / "00_VALIDATE_CANONICAL_SOURCE.sh").read_text(encoding="utf-8")
for required in ("python3 -m venv", "evidence preserved", "validation.log"):
    if required not in gate0:
        raise SystemExit(f"STOP - source validation gate missing: {required}")

gate1 = (GATES / "01_VERIFY_PUBLICATION_KIT_BOUNDARY.sh").read_text(encoding="utf-8")
for required in ("public source contains local maintainer gates only", "separately reviewed publication kit"):
    if required not in gate1:
        raise SystemExit(f"STOP - publication boundary gate missing: {required}")

validator = ROOT / "scripts/check_publication_kit.py"
if not validator.is_file():
    raise SystemExit("STOP - separate publication-kit validator is missing")

release_workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
if "gh release create" not in release_workflow:
    raise SystemExit("STOP - hosted release workflow is not the sole release creator")
if "--draft" not in release_workflow:
    raise SystemExit("STOP - hosted release workflow must create a draft before publication")
if "git diff --exit-code" not in release_workflow:
    raise SystemExit("STOP - release workflow does not prove validation left the tagged tree unchanged")

for required in (
    'notes_file="RELEASE_NOTES_${GITHUB_REF_NAME}.md"',
    'archive="dist/materials-to-mission-${GITHUB_REF_NAME}.zip"',
    'test "$manifest_tag" = "$GITHUB_REF_NAME"',
    'assert data["tag"] == f"v{data[\'version\']}"',
):
    if required not in release_workflow:
        raise SystemExit(
            f"STOP - release workflow is not version-generic: {required}"
        )
for forbidden in (
    "RELEASE_NOTES_v0.1.0.md",
    "dist/materials-to-mission-v0.1.0.zip",
    "assert data['tag'] == 'v0.1.0'",
):
    if forbidden in release_workflow:
        raise SystemExit(
            f"STOP - release workflow contains a hard-coded release identity: {forbidden}"
        )
print("PASS - public-source maintainer gates and hosted Release workflow contract")
