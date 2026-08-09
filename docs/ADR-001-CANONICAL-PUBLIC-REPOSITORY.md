# ADR-001: Canonical Materials-to-Mission Public Repository

**Status:** Accepted for v0.1.0  
**Date:** 2026-08-08

## Decision

`Bridge-Node-7/materials-to-mission` is the canonical public authority for the
Materials-to-Mission method, schemas, CLI, validators, synthetic examples, Material
Assurance Record, Decision Passport, compatibility policy, and release lifecycle.

## Consequences

- Frontier Decision Engine may consume an explicitly supported released contract but may
  not independently redefine or version canonical Materials-to-Mission schemas.
- The Bridge Node 7 website remains the institutional narrative and routing layer.
- Real operational cases and protected evidence remain outside public repositories.
- v0.1.0 is M0 experimental public method only and does not establish M1 workflow proof.
- Schema identifiers are immutable and bound to the v0.1.0 Git tag.
- The first website change is a minimal external link, not a new route.
