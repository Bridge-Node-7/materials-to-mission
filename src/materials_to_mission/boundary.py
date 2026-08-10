from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterator

from .resources import policy_dir


_BOUNDARY_CONFUSABLES = str.maketrans(
    {
        "\u0391": "A", "\u03b1": "a",
        "\u0399": "I", "\u03b9": "i",
        "\u039f": "O", "\u03bf": "o",
        "\u0410": "A", "\u0430": "a",
        "\u0406": "I", "\u0456": "i",
        "\u0412": "B", "\u0432": "b",
        "\u0415": "E", "\u0435": "e",
        "\u041a": "K", "\u043a": "k",
        "\u041c": "M", "\u043c": "m",
        "\u041d": "H", "\u043d": "h",
        "\u041e": "O", "\u043e": "o",
        "\u0420": "P", "\u0440": "p",
        "\u0421": "C", "\u0441": "c",
        "\u0422": "T", "\u0442": "t",
        "\u0425": "X", "\u0445": "x",
    }
)


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
    normalized = unicodedata.normalize("NFKC", str(value)).translate(
        _BOUNDARY_CONFUSABLES
    )
    return re.sub(r"[^a-z0-9]+", "_", normalized.casefold()).strip("_")


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
    normalized_text = unicodedata.normalize("NFKC", text).translate(
        _BOUNDARY_CONFUSABLES
    )
    lower = normalized_text.casefold()
    findings: list[str] = []

    for location, key in _walk(value):
        normalized = _normalized_key(key)
        if normalized in _SECRET_KEY_NAMES:
            findings.append(f"prohibited public key at {location}: {key}")

    for token in policy["prohibited_case_insensitive_tokens"]:
        if token.lower() in lower:
            findings.append(f"prohibited public token: {token}")
    for pattern in policy["prohibited_regexes"]:
        if re.search(pattern, text) or re.search(pattern, normalized_text):
            findings.append(f"prohibited public pattern: {pattern}")

    # Keep output deterministic and avoid duplicate messages when a policy token
    # and a structured key identify the same underlying signal.
    return list(dict.fromkeys(findings))
