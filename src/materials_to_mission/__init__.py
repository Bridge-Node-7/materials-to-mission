"""Materials-to-Mission public reference toolkit."""

from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path

try:
    __version__ = distribution_version("materials-to-mission")
except PackageNotFoundError:  # source-tree fallback before installation
    __version__ = (
        Path(__file__).resolve().parents[2] / "VERSION"
    ).read_text(encoding="utf-8").strip()

from .validator import ValidationFinding, ValidationResult, validate_case

__all__ = [
    "ValidationFinding",
    "ValidationResult",
    "validate_case",
    "__version__",
]
