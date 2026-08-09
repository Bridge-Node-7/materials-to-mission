from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import InputFileError


MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_NESTING_DEPTH = 64


def _exceeds_depth(value: Any) -> bool:
    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > MAX_NESTING_DEPTH:
            return True
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return False


def read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        size = p.stat().st_size
    except OSError as exc:
        raise InputFileError(f"cannot stat input: {p}: {exc}") from exc
    if size > MAX_INPUT_BYTES:
        raise InputFileError(f"input exceeds {MAX_INPUT_BYTES} bytes: {p}")

    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw)
    except RecursionError as exc:
        raise InputFileError(
            f"input exceeds maximum nesting depth {MAX_NESTING_DEPTH}: {p}"
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputFileError(f"cannot read JSON input: {p}: {exc}") from exc

    if not isinstance(data, dict):
        raise InputFileError("top-level JSON value must be an object")
    if _exceeds_depth(data):
        raise InputFileError(
            f"input exceeds maximum nesting depth {MAX_NESTING_DEPTH}"
        )
    return data


def write_text(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")
