from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from materials_to_mission.release import build_deterministic_zip, sha256  # noqa: E402

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
archive = dist / f"materials-to-mission-v{version}.zip"
build_deterministic_zip(ROOT, archive)
digest = sha256(archive)
sidecar = dist / "SHA256SUMS"
sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


mode = os.environ.get("M2M_RELEASE_MODE", "source")
if mode not in {"source", "candidate"}:
    raise SystemExit(f"STOP - unsupported M2M_RELEASE_MODE: {mode}")

commit = os.environ.get("GITHUB_SHA") or git_value("rev-parse", "HEAD")
tag = os.environ.get("GITHUB_REF_NAME")
tree = git_value("show", "-s", "--format=%T", commit or "HEAD") if commit else None
commit_timestamp = git_value("show", "-s", "--format=%cI", commit or "HEAD") if commit else None

if mode == "candidate":
    expected_tag = f"v{version}"
    if not commit or not tree or not commit_timestamp or tag != expected_tag:
        raise SystemExit(
            "STOP - candidate release manifest requires exact commit, tree, and tag "
            f"{expected_tag}"
        )

manifest = {
    "name": "materials-to-mission",
    "version": version,
    "mode": mode,
    "git_bound": mode == "candidate",
    "tag": tag,
    "commit": commit,
    "tree": tree,
    "archive": archive.name,
    "sha256": digest,
    "license": "MIT",
    "schema_authority": "https://raw.githubusercontent.com/Bridge-Node-7/materials-to-mission/v0.1.0/schemas/",
    "maturity": "M0 experimental public method",
    "synthetic_public_reference_only": True,
    "real_case_001_claimed": False,
    "human_decision_authority_required": True,
    "bootstrap_commit_timestamp": commit_timestamp if mode == "candidate" else None,
}
(dist / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"PASS - {archive}")
print(f"SHA-256 {digest}")
print(f"MODE {mode}")
