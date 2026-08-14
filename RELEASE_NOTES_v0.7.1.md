# Materials-to-Mission v0.7.1 — Foundation Hardening

## Purpose

v0.7.1 hardens the Materials-to-Mission foundation without increasing evidence claims or changing the accepted Atlas experience.

## Foundation

- Selected Pathways are rendered deterministically at build time from schema-validated controlled metadata.
- Gallium and Yttrium Iron Garnet (YIG) remain the same two reviewed public examples.
- Selected Pathways remain discoverable without requiring JavaScript.
- Browser UAT infrastructure uses version-neutral workflow, script, and artifact names.
- Local preview and automated Browser UAT use the repository-owned HTTP/1.1 preview server.
- Repository and release truth distinguish immediate-prior immutable `v0.7.0`, the historical foundation baseline, and the `v0.7.1` source/release line.
- GitHub Actions checkout credentials use least-persistence behavior where appropriate.
- Pages production-attestation reporting is corrected without weakening fail-closed production verification.

## Assurance

- Deterministic build and complete repository gate: **PASS**.
- Automated test suite: **PASS across the hosted Linux/Windows CI matrix. Only the three documented symlink-unavailable cases may skip on environments that do not support them.**
- Combined statement and branch coverage: **95 percent**.
- Browser UAT: **PASS — 14 profiles, including seven 42-contract viewports**.
- Keyboard/focus, forced colors, reduced motion, mobile/touch, 320px layout, 200-percent reflow, no-JavaScript behavior, CSP/navigation, public boundaries, links, manifest integrity, and reproducibility: **PASS**.

Human mobile visual UAT and human assistive-technology UAT are not separately attested.

## Boundaries

- Frozen GA-001 v1.0.0, MF-001, and YIG-001 evidence is unchanged.
- YIG remains an engineered material system, not a USGS critical mineral.
- M0 remains M0.
- No M1 capability is claimed.
- Unknown remains non-favorable and Evidence Horizon remains explicit.
- Human consequential authority remains required and explicit.
- No qualification, certification, legal-compliance, acquisition-approval, mission-readiness, production-capacity, assured-supply, supplier-validation, customer-validation, government-endorsement, or autonomous consequential-authority claim is made.
