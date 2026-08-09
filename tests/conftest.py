from __future__ import annotations

import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def example_case() -> dict:
    return json.loads((ROOT / "examples/synthetic-critical-material-pathway/case.json").read_text(encoding="utf-8"))


@pytest.fixture
def root() -> Path:
    return ROOT
