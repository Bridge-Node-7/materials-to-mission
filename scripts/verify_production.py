from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_manifest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in (root / "WEB_MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        result[relative] = expected
    if not result:
        raise ValueError("empty WEB_MANIFEST.sha256")
    return result


def fetch_bytes(url: str, timeout_seconds: int) -> bytes:
    request = Request(url, headers={"User-Agent": "BN7-M2M-production-readback/1"})
    with urlopen(request, timeout=timeout_seconds) as response:
        if response.status != 200:
            raise RuntimeError(f"unexpected HTTP status {response.status}: {url}")
        return response.read()


def observe(expected_dir: Path, base_url: str, timeout_seconds: int, token: str) -> tuple[bool, dict]:
    expected = read_manifest(expected_dir)
    files: dict[str, dict] = {}
    passed = True
    for relative, expected_hash in expected.items():
        url = base_url.rstrip("/") + "/" + relative + "?bn7_readback=" + token
        observed_hash = digest(fetch_bytes(url, timeout_seconds))
        match = observed_hash == expected_hash
        passed = passed and match
        files[relative] = {"expected_sha256": expected_hash, "observed_sha256": observed_hash, "match": match}
    return passed, files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-dir", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-sha", default="")
    parser.add_argument("--attempts", type=int, default=12)
    parser.add_argument("--delay-seconds", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    args = parser.parse_args()
    record = {"schema_version": "1.0.0", "production_url": args.base_url, "expected_commit": args.github_sha, "status": "FAIL", "attempts": []}
    for attempt in range(1, args.attempts + 1):
        token = f"{args.github_sha}-{attempt}-{int(time.time())}"
        try:
            passed, files = observe(args.expected_dir, args.base_url, args.timeout_seconds, token)
            entry = {"attempt": attempt, "observed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "files": files}
        except Exception as exc:
            passed = False
            entry = {"attempt": attempt, "observed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "error": f"{type(exc).__name__}: {exc}"}
        record["attempts"].append(entry)
        if passed:
            record["status"] = "PASS"
            break
        if attempt < args.attempts:
            time.sleep(args.delay_seconds)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
