from __future__ import annotations

from dataclasses import dataclass

BASELINE_PROFILE_ID = "m0-baseline-0.1.0"
STRICT_PROFILE_ID = "m0-strict-0.2.0"
STRICT_V040_PROFILE_ID = "m0-strict-0.4.0"
DEFAULT_VALIDATION_PROFILE = STRICT_V040_PROFILE_ID

@dataclass(frozen=True, slots=True)
class ValidationProfile:
    profile_id: str
    description: str
    schema_authority: str = "v0.1.0"

_PROFILES = {
    BASELINE_PROFILE_ID: ValidationProfile(
        profile_id=BASELINE_PROFILE_ID,
        description=(
            "Historical v0.1.0 semantic acceptance behavior for explicit "
            "compatibility evaluation."
        ),
    ),
    STRICT_PROFILE_ID: ValidationProfile(
        profile_id=STRICT_PROFILE_ID,
        description=(
            "Released strengthened M0 semantic validation for the Consumer & "
            "Contract Integrity release line."
        ),
    ),
    STRICT_V040_PROFILE_ID: ValidationProfile(
        profile_id=STRICT_V040_PROFILE_ID,
        description=(
            "M0 strict profile adding explicitly versioned automation-authority "
            "alias rejection while preserving released profile behavior."
        ),
    ),
}

VALIDATION_PROFILE_IDS = tuple(_PROFILES)

def get_validation_profile(profile_id: str) -> ValidationProfile:
    try:
        return _PROFILES[profile_id]
    except KeyError:
        raise ValueError(f"unknown validation profile: {profile_id}") from None
