from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .resources import policy_dir


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def scan_public_boundary(value: Any, policy_path: str | Path | None = None) -> list[str]:
    path = Path(policy_path) if policy_path else policy_dir() / "public-boundary-policy.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    text = _serialize(value)
    lower = text.lower()
    findings: list[str] = []
    for token in policy["prohibited_case_insensitive_tokens"]:
        if token.lower() in lower:
            findings.append(f"prohibited public token: {token}")
    for pattern in policy["prohibited_regexes"]:
        if re.search(pattern, text):
            findings.append(f"prohibited public pattern: {pattern}")
    return findings
