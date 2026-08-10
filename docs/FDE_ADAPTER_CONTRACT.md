# Frontier Decision Engine Adapter Contract

## Status

```text
CANONICAL RELEASE PREREQUISITE: COMPLETE
ADAPTER ASSESSMENT:             ELIGIBLE
IMPLEMENTATION:                 DEFERRED
BLOCKING EVIDENCE:              REAL CASE 001, STABLE MAPPING NEED, REPEATED USER NEED
```

The immutable `v0.1.0` release remains the canonical schema authority. Version `v0.1.1`
is the first M0 assurance-maintenance release, and `v0.1.2` is the current authority and
traceability closeout release. Public release availability alone does not justify adapter
implementation.

## Authority

Materials-to-Mission owns the canonical M2M schemas and versions. Frontier Decision Engine
owns its application, generic decision model, and presentation behavior.

A future adapter must consume a declared released contract. It must not copy, fork, or
silently reinterpret the canonical schemas.

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

## Required Evidence Before Implementation

- approved real Case 001 demonstrates a recurring browser or decision-workflow need;
- mapping requirements are stable enough to test;
- intended users confirm the adapter would improve a consequential workflow;
- public and protected data boundaries are defined;
- the adapter remains smaller and safer than duplicating the method.

## Required Tests

- Exact supported contract version
- Import validation
- Missing, contradictory, expired, revoked, and superseded evidence
- Human-authority preservation
- Export or round-trip behavior where supported
- No duplicate canonical schema copies
- Public synthetic data only
- Fail-closed handling of incompatible or undeclared records
