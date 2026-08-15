# Materials-to-Mission v0.7.2 — Corrective Maintenance

## Purpose

v0.7.2 closes bounded accessibility and assurance findings without changing evidence, maturity, pathways, or the accepted Atlas experience.

## Verified fixes

- Narrow-screen material and material-system details use native modal dialog semantics.
- The dialog has a valid static fallback name and gains a specific title association only after detail content exists.
- Modal focus navigation cannot reach background controls, Escape and the explicit close control close the dialog, and focus returns to the originating Atlas control.
- The orientation layer explains that the Atlas 15-count follows the controlled USGS commodity grouping and lists scandium separately.
- Contributor guidance identifies stale editable-install metadata and directs reinstalling the current checkout without weakening version identity.

## Verified assurance

- Complete repository gate, deterministic build, deterministic packaging, and hosted Linux/Windows CI matrix: **PASS**.
- Combined statement and branch coverage: **at least 95 percent**.
- Browser UAT: **PASS — 14 profiles, including seven existing 42-contract viewports**.
- Frozen GA-001 v1.0.0, MF-001, and YIG-001 evidence is unchanged.
- YIG remains an engineered material system, not a USGS critical mineral.

## Accepted and deferred informational items

- Dense Atlas nodes retain the documented 24px target-size floor; the List view remains the larger-row alternative. No usability regression justified redesign.
- GitHub Pages did not expose response-level CSP or X-Frame-Options during the bounded anonymous check. Meta-delivered CSP cannot enforce `frame-ancestors`; any hosting-layer change requires separate external governance.
- Human physical-device mobile UAT and human assistive-technology UAT remain not separately attested.

## Boundaries

- Exactly two Selected Pathways remain: Gallium and YIG.
- This corrective release does not add or upgrade underlying evidence.
- M0 remains M0; no M1 capability is claimed.
- Unknown remains non-favorable and Evidence Horizon remains explicit.
- Human consequential authority remains required and explicit.
- No evidence, qualification, certification, acquisition-approval, mission-readiness, production-capacity, supplier, customer, government, or autonomous consequential-authority claim is added.
