# Materials-to-Mission v0.1.0

Initial public reference baseline.

## Included

- Versioned Decision Charter, Evidence Record, Material Assurance Record, Decision Passport, and Case schemas
- Deterministic CLI validation and Markdown rendering
- Synthetic critical-material pathway reference case
- Adversarial negative fixtures
- Public-boundary scanner
- Cross-platform CI, CodeQL, signed-tag release workflow, deterministic archive, and checksums
- Complete method, evidence, security, governance, limitations, and release documentation

## Not Claimed

No real-world qualification, certification, compliance, production capacity,
customer adoption, government endorsement, operational authorization, or
commercial readiness is claimed.


## Convergence Decisions

- Dedicated repository is the canonical Materials-to-Mission schema authority.
- MIT is the v0.1.0 public license; the patent and private-information boundaries remain explicit.
- Canonical schema identifiers are immutable and version-tag-bound.
- M0 experimental method publication is separate from M1 Case 001 proof.
- FDE integration is adapter-based and deferred until after the canonical release.
- Initial website integration is a minimal external link, not a new route.


## Reliability and release integrity

- Corrected invalid `--json` validation output for slots-based findings.
- Added CLI failure-path, help, release-mode, and gate-contract regression tests.
- Added progressive onboarding, audience paths, and a five-minute evaluation.
- Updated setup-python to v7.0.0 and CodeQL Action to v4.37.6 using full commit pins.
- Separated source-maintainer gates from generated public-write gates.
- Added isolated-environment validation, exact-404 target checks, workflow-ID readback,
  partial-creation evidence, release-asset attestation, exact allowlists, and archive-to-tree closeout.
- Preserved MIT, the M0 public-method boundary, canonical standalone schemas, minimal website
  linkage, and FDE as a later consumer.

## Final packaging safety

- Included package paths reject symbolic links instead of following them.
- Package output must be placed in excluded `dist/`, excluded `build/`, or outside the release root.
- Regression tests protect deterministic repeat builds and controlled CLI failures.

## Publication identity integrity

- Candidate metadata, release manifest, environment file, Git bundle, and bootstrap timestamp must agree.
- Publication-kit manifests must cover every shipped file exactly.
- Contradictory predecessor or timestamp-correction records fail closed.

## Cross-platform validation evidence

- The checked-in validation report is now reproducible across supported hosts.
- Every operator environment must pass all runnable tests and the 95 percent combined coverage floor.
- Only the three documented symlink-unavailable cases may skip where the operating system cannot create symbolic links.
