# Supersession Record

All earlier RC1, RC2, RC3, RC4, publication, FDE-profile, CSA, and historical operator
packages remain preserved as engineering evidence but are superseded by the current
Materials-to-Mission repository and release line.

```text
SUPERSEDED
PRESERVE AS EVIDENCE
DO NOT EXECUTE
```

## Current Authority

- Dedicated standalone `Bridge-Node-7/materials-to-mission` repository
- MIT license
- Immutable `v0.1.0` public method and canonical schema baseline
- Immutable `v0.1.2` current M0 authority and traceability closeout release
- M0 experimental public method may exist before Case 001
- M1 and later claims remain evidence-gated
- Version-tag-bound canonical schema identifiers
- Public-write gates excluded from public source
- Hosted Release workflow as the sole GitHub Release creator
- One completed external **View Public Method** link on the website Materials page
- Frontier Decision Engine release prerequisite complete; implementation deferred pending
  real Case 001 evidence and repeated user need
- No separate competing public Critical Supply Chain Assurance repository

## Historical Package Rule

Earlier packages remain evidence only. Do not execute, mix, retag, or use them as current
source authority. Historical plans may explain how the repository was formed, but current
state is governed by the live repository, signed releases, `PROJECT_FACTS.json`,
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), and reviewed closeout evidence.

## Cross-Platform Validation Evidence

The current evidence contract remains strict and reproducible across supported hosts:
all runnable tests must pass, local combined coverage must remain at or above 95 percent,
and only the three documented symlink-unavailable tests may skip on hosts that cannot create
symbolic links.
