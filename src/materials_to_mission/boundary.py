from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
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
_SECRET_KEY_COMPONENTS = {
    "token",
    "password",
    "passwd",
    "secret",
    "credential",
    "credentials",
}
_KEY_QUALIFIERS = {
    "api",
    "access",
    "auth",
    "client",
    "encryption",
    "private",
    "secret",
    "signing",
    "ssh",
}
_SECRET_VALUE_PATTERNS = (
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,255}\b")),
    ("github-fine-grained-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,255}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,255}\b")),
)


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


@lru_cache(maxsize=1)
def _confusable_mapping() -> dict[str, str]:
    path = policy_dir() / "unicode-confusables-17.0.0.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("unicode_version") != "17.0.0":
        raise ValueError("unexpected Unicode confusables data version")
    mapping = data.get("mapping")
    if not isinstance(mapping, dict):
        raise ValueError("invalid Unicode confusables mapping")
    return {str(key): str(value) for key, value in mapping.items()}


def _security_skeleton(value: str) -> str:
    text = unicodedata.normalize("NFD", str(value))
    mapping = _confusable_mapping()
    mapped = "".join(mapping.get(char, char) for char in text)
    return unicodedata.normalize("NFD", mapped)


def _normalized_key(value: Any) -> str:
    normalized = _security_skeleton(str(value)).casefold()
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def _secret_like_key(normalized: str) -> bool:
    if normalized in _SECRET_KEY_NAMES:
        return True
    parts = {part for part in normalized.split("_") if part}
    if parts & _SECRET_KEY_COMPONENTS:
        return True
    return "key" in parts and bool(parts & _KEY_QUALIFIERS)


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
    skeleton = _security_skeleton(text)
    lower = skeleton.casefold()
    findings: list[str] = []

    for location, key in _walk(value):
        normalized = _normalized_key(key)
        if _secret_like_key(normalized):
            findings.append(f"prohibited public key at {location}: {key}")

    for token in policy["prohibited_case_insensitive_tokens"]:
        token_skeleton = _security_skeleton(token).casefold()
        if token_skeleton in lower:
            findings.append(f"prohibited public token: {token}")
    for pattern in policy["prohibited_regexes"]:
        if re.search(pattern, text) or re.search(pattern, skeleton):
            findings.append(f"prohibited public pattern: {pattern}")
    for label, pattern in _SECRET_VALUE_PATTERNS:
        if pattern.search(text) or pattern.search(skeleton):
            findings.append(f"prohibited credential-shaped public value: {label}")

    # Keep output deterministic and avoid duplicate messages when more than one
    # guardrail identifies the same underlying signal.
    return list(dict.fromkeys(findings))
