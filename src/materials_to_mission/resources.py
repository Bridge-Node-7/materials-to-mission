from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def schema_dir() -> Path:
    return Path(str(files("materials_to_mission").joinpath("resources/schemas")))


def policy_dir() -> Path:
    return Path(str(files("materials_to_mission").joinpath("resources/policy")))
