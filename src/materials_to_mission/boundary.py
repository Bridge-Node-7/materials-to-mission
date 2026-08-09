from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

from .resources import policy_dir


_SECRET_KEY_NAMES = {
    "api_key",
    "apikey",
    "access_key",
    "access_token",
    "auth_token",
    "authorization_token",
    "client_secret",
    "credential",
    "credentials",
    "password",
    "passwd",
    "private_key",
    "secret",
    "secret_key",
    "token",
}


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def _walk(value: Any, path: str = "$") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            yield child, key
            yield from _walk(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def scan_public_boundary(
    value: Any,
    policy_path: str | Path | None = None,
) -> list[str]:
    path = (
        Path(policy_path)
        if policy_path
        else policy_dir() / "public-boundary-policy.json"
    )
    policy = json.loads(path.read_text(encoding="utf-8"))
    text = _serialize(value)
    lower = text.lower()
    findings: list[str] = []

    for location, key in _walk(value):
        normalized = _normalized_key(key)
        if normalized in _SECRET_KEY_NAMES:
            findings.append(f"prohibited public key at {location}: {key}")

    for token in policy["prohibited_case_insensitive_tokens"]:
        if token.lower() in lower:
            findings.append(f"prohibited public token: {token}")
    for pattern in policy["prohibited_regexes"]:
        if re.search(pattern, text):
            findings.append(f"prohibited public pattern: {pattern}")

    # Keep output deterministic and avoid duplicate messages when a policy token
    # and a structured key identify the same underlying signal.
    return list(dict.fromkeys(findings))
