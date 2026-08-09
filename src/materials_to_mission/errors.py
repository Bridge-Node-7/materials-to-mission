class MaterialsToMissionError(Exception):
    """Base exception for controlled toolkit failures."""


class InputFileError(MaterialsToMissionError):
    """Raised when an input file cannot be read safely."""
