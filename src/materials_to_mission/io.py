from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import InputFileError

MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_NESTING_DEPTH = 64


def _depth(value: Any, current: int = 0) -> int:
    if current > MAX_NESTING_DEPTH:
        return current
    if isinstance(value, dict):
        return max([current] + [_depth(v, current + 1) for v in value.values()])
    if isinstance(value, list):
        return max([current] + [_depth(v, current + 1) for v in value])
    return current


def read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        size = p.stat().st_size
    except OSError as exc:
        raise InputFileError(f"cannot stat input: {p}: {exc}") from exc
    if size > MAX_INPUT_BYTES:
        raise InputFileError(f"input exceeds {MAX_INPUT_BYTES} bytes: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputFileError(f"cannot read JSON input: {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputFileError("top-level JSON value must be an object")
    if _depth(data) > MAX_NESTING_DEPTH:
        raise InputFileError(f"input exceeds maximum nesting depth {MAX_NESTING_DEPTH}")
    return data


def write_text(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")
