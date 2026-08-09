from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

EXPECTED_GATES = {
    "00_READ_ONLY_PERSONAL_ACCOUNT_PREFLIGHT.sh",
    "01_CREATE_REPOSITORY_AND_PUSH_EXACT_MAIN.sh",
    "02_HOSTED_CI_AND_CODEQL_READBACK.sh",
    "03_CONFIGURE_METADATA_SECURITY_AND_RULESET.sh",
    "04_PUSH_SIGNED_V0.1.0_TAG.sh",
    "05_RELEASE_READBACK_AND_CLOSEOUT.sh",
}
REQUIRED_FILES = {
    "CANDIDATE_IDENTITY.json",
    "release-candidate.env",
    "release-manifest.json",
    "materials-to-mission-v0.1.0.zip",
    "materials-to-mission-v0.1.0.gitbundle",
    "REPO_FILE_MANIFEST.sha256",
    "VALIDATION_REPORT.md",
    "SHA256SUMS",
    "KIT_SHA256SUMS",
    "README_FIRST.md",
    "SUPERSESSION.md",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, *needles: str) -> None:
    missing = [item for item in needles if item not in text]
    if missing:
        raise SystemExit("STOP - publication gate contract missing: " + ", ".join(missing))


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise SystemExit(f"STOP - malformed release-candidate.env line: {line}")
        key, value = stripped.split("=", 1)
        if not key or key in values:
            raise SystemExit(f"STOP - invalid or duplicate release-candidate.env key: {key}")
        values[key] = value
    return values


def parse_timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SystemExit(f"STOP - {label} is missing")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"STOP - {label} is not valid ISO-8601: {value}") from exc
    if parsed.tzinfo is None:
        raise SystemExit(f"STOP - {label} must include a timezone: {value}")
    return value


def verify_manifest(root: Path, manifest_name: str, *, require_complete: bool = False) -> set[str]:
    manifest = root / manifest_name
    if not manifest.is_file():
        raise SystemExit(f"STOP - publication kit missing manifest: {manifest_name}")
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"STOP - malformed manifest line in {manifest_name}: {line}") from exc
        if relative in entries:
            raise SystemExit(f"STOP - duplicate manifest member: {relative}")
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"STOP - manifest member missing or unsafe: {relative}")
        observed = sha256(path)
        if observed != expected:
            raise SystemExit(
                f"STOP - manifest mismatch for {relative}: expected {expected}, observed {observed}"
            )
        entries[relative] = expected
    if require_complete:
        observed_files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.name != manifest_name
        }
        if set(entries) != observed_files:
            missing = sorted(observed_files - set(entries))
            extra = sorted(set(entries) - observed_files)
            raise SystemExit(
                "STOP - publication-kit manifest coverage mismatch: "
                f"missing={missing}, extra={extra}"
            )
    return set(entries)


def validate_identity_metadata(
    identity: dict[str, object],
    manifest: dict[str, object],
    env: dict[str, str],
) -> None:
    required = (
        "repository",
        "version",
        "source_archive_sha256",
        "git_bundle_sha256",
        "commit",
        "tree",
        "bootstrap_commit_timestamp",
    )
    for key in required:
        if not identity.get(key):
            raise SystemExit(f"STOP - candidate identity missing {key}")

    commit = str(identity["commit"])
    tree = str(identity["tree"])
    if not HEX40.fullmatch(commit) or not HEX40.fullmatch(tree):
        raise SystemExit("STOP - candidate identity commit or tree is not a 40-character Git ID")

    timestamp = parse_timestamp(identity["bootstrap_commit_timestamp"], "bootstrap commit timestamp")
    if manifest.get("bootstrap_commit_timestamp") != timestamp:
        raise SystemExit("STOP - release manifest bootstrap timestamp mismatch")

    expected_version = str(identity["version"]).removeprefix("v")
    if manifest.get("version") != expected_version:
        raise SystemExit("STOP - release manifest version mismatch")
    if manifest.get("tag") != identity["version"]:
        raise SystemExit("STOP - release manifest tag mismatch")
    if manifest.get("commit") != commit or manifest.get("tree") != tree:
        raise SystemExit("STOP - release manifest Git identity mismatch")
    if manifest.get("sha256") != identity["source_archive_sha256"]:
        raise SystemExit("STOP - release manifest source identity mismatch")

    predecessor = identity.get("predecessor_commit")
    if predecessor is not None:
        if not isinstance(predecessor, str) or not HEX40.fullmatch(predecessor):
            raise SystemExit("STOP - predecessor_commit is not a 40-character Git ID")
        if predecessor == commit:
            raise SystemExit("STOP - predecessor_commit must differ from the approved commit")

    timestamp_correction = identity.get("timestamp_correction")
    if timestamp_correction is not None:
        if not isinstance(timestamp_correction, dict):
            raise SystemExit("STOP - timestamp_correction must be an object")
        previous = timestamp_correction.get("previous_commit")
        if not isinstance(previous, str) or not HEX40.fullmatch(previous):
            raise SystemExit("STOP - timestamp_correction.previous_commit is invalid")
        if previous == commit:
            raise SystemExit(
                "STOP - timestamp_correction.previous_commit must differ from the approved commit"
            )

    expected_env = {
        "FULL_REPO": str(identity["repository"]),
        "TAG": str(identity["version"]),
        "APPROVED_COMMIT": commit,
        "APPROVED_TREE": tree,
        "BUNDLE_SHA256": str(identity["git_bundle_sha256"]),
        "EXPECTED_SOURCE_ARCHIVE_SHA256": str(identity["source_archive_sha256"]),
    }
    for key, expected in expected_env.items():
        if env.get(key) != expected:
            raise SystemExit(
                f"STOP - release-candidate.env mismatch for {key}: "
                f"expected {expected}, observed {env.get(key)}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kit", type=Path, help="extracted publication-kit directory")
    args = parser.parse_args(argv)
    root = args.kit.resolve()
    if not root.is_dir():
        raise SystemExit(f"STOP - publication kit is not a directory: {root}")

    for path in root.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"STOP - publication kit contains a symbolic link: {path.relative_to(root)}")

    gates = root / "GATES"
    observed = {path.name for path in gates.glob("*.sh")} if gates.is_dir() else set()
    if observed != EXPECTED_GATES:
        raise SystemExit(
            f"STOP - publication gate set mismatch: expected {sorted(EXPECTED_GATES)}, "
            f"observed {sorted(observed)}"
        )

    missing = sorted(name for name in REQUIRED_FILES if not (root / name).is_file())
    if missing:
        raise SystemExit("STOP - publication kit missing files: " + ", ".join(missing))

    verify_manifest(root, "KIT_SHA256SUMS", require_complete=True)

    identity = json.loads((root / "CANDIDATE_IDENTITY.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
    env = parse_env(root / "release-candidate.env")
    validate_identity_metadata(identity, manifest, env)

    source = root / "materials-to-mission-v0.1.0.zip"
    bundle = root / "materials-to-mission-v0.1.0.gitbundle"
    if sha256(source) != identity["source_archive_sha256"]:
        raise SystemExit("STOP - source archive does not match candidate identity")
    if sha256(bundle) != identity["git_bundle_sha256"]:
        raise SystemExit("STOP - Git bundle does not match candidate identity")

    texts = {name: (gates / name).read_text(encoding="utf-8") for name in EXPECTED_GATES}
    joined = "\n".join(texts.values())
    if "gh release create" in joined:
        raise SystemExit("STOP - publication gates must not compete with the hosted Release workflow")

    require(
        texts["00_READ_ONLY_PERSONAL_ACCOUNT_PREFLIGHT.sh"],
        "owner type", "HTTP", "404", "verify-tag", "archive-to-tree",
        "gh release verify --help", "gh release verify-asset --help",
        "BN7_M2M_GATE00_MARKER",
    )
    require(
        texts["01_CREATE_REPOSITORY_AND_PUSH_EXACT_MAIN.sh"],
        "gh repo create", "bundle verify", "repository may now exist", "Do not delete",
        "bundle-check",
    )
    require(
        texts["02_HOSTED_CI_AND_CODEQL_READBACK.sh"],
        ".github/workflows/ci.yml", ".github/workflows/codeql.yml", "head_sha",
    )
    require(
        texts["03_CONFIGURE_METADATA_SECURITY_AND_RULESET.sh"],
        "private-vulnerability-reporting", "immutable-releases", "branches/main/protection",
    )
    require(
        texts["04_PUSH_SIGNED_V0.1.0_TAG.sh"],
        "tag-work", "tag -s", "verify-tag", "push origin", "immutable releases are not enabled",
    )
    require(
        texts["05_RELEASE_READBACK_AND_CLOSEOUT.sh"],
        "gh release verify", "gh release verify-asset", "archive-to-tree", "schemas/",
    )

    for path in sorted(gates.glob("*.sh")):
        result = run("bash", "-n", str(path))
        if result.returncode:
            raise SystemExit(f"STOP - Bash syntax failed for {path.name}: {result.stderr}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        verify_repo = tmp_root / "bundle-check"
        clone = tmp_root / "clone"
        verify_repo.mkdir()
        result = run("git", "-C", str(verify_repo), "init", "-q")
        if result.returncode:
            raise SystemExit("STOP - could not initialize bundle verification repository")
        result = run("git", "-C", str(verify_repo), "bundle", "verify", str(bundle))
        if result.returncode:
            raise SystemExit("STOP - Git bundle verification failed: " + result.stderr.strip())
        result = run("git", "clone", "-q", "-b", "main", str(bundle), str(clone))
        if result.returncode:
            raise SystemExit("STOP - Git bundle clone failed: " + result.stderr.strip())
        commit = run("git", "-C", str(clone), "rev-parse", "HEAD")
        tree = run("git", "-C", str(clone), "show", "-s", "--format=%T", "HEAD")
        author_time = run("git", "-C", str(clone), "show", "-s", "--format=%aI", "HEAD")
        committer_time = run("git", "-C", str(clone), "show", "-s", "--format=%cI", "HEAD")
        status = run("git", "-C", str(clone), "status", "--porcelain")
        if commit.stdout.strip() != identity["commit"]:
            raise SystemExit("STOP - bundle commit does not match candidate identity")
        if tree.stdout.strip() != identity["tree"]:
            raise SystemExit("STOP - bundle tree does not match candidate identity")
        expected_time = identity["bootstrap_commit_timestamp"]
        if author_time.stdout.strip() != expected_time or committer_time.stdout.strip() != expected_time:
            raise SystemExit("STOP - bundle commit timestamp does not match candidate identity")
        if status.stdout.strip():
            raise SystemExit("STOP - bundle clone is not clean")

    print(
        "PASS - publication kit manifests, metadata, environment, bundle, gates, "
        "safety contracts, Bash syntax, and clean clone"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
