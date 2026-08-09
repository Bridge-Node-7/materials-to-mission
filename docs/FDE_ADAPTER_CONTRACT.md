# Frontier Decision Engine Adapter Contract

## Status

Deferred until the canonical Materials-to-Mission v0.1.0 release is public and verified.

## Authority

Materials-to-Mission owns the canonical M2M schemas and versions. Frontier Decision Engine
owns its application, generic decision model, and presentation behavior.

## Minimum Adapter Declaration

```json
{
  "profile_id": "materials-to-mission",
  "status": "experimental",
  "schema_authority": {
    "repository": "Bridge-Node-7/materials-to-mission",
    "release": "v0.1.0",
    "schema_version": "0.1.0",
    "manifest_sha256": "<released manifest hash>"
  }
}
```

## Required Tests

- Exact supported contract version
- Import validation
- Missing, contradictory, expired, revoked, and superseded evidence
- Human-authority preservation
- Export or round-trip behavior where supported
- No duplicate canonical schema copies
- Public synthetic data only
