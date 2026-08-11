# Changelog

All notable changes are documented here.

## Unreleased

### v0.5.0 candidate — Precision Evidence Experience
- Add the complete USGS 2025 critical-mineral field as a Strategic Constellation.
- Derive Application Lenses and coordinates from controlled DOE application data.
- Generate visible public HTML from one validated projection with a no-JavaScript fallback.
- Preserve Gallium GA-001 as the only released reviewed pathway in this candidate.
- Add public deep links, form search, precision Index, responsive detail behavior, and Evidence Horizon semantics.
- Harden source authority, HTTPS/domain, ID/state, relationship, and lineage validation.
- Preserve M0, no-score behavior, human consequential authority, and public/private boundaries.

## [0.4.0] - 2026-08-10

### Corrected
- Restored `m0-strict-0.2.0` to its released accept/reject behavior for the automation-owner aliases introduced during v0.3.1 maintenance.
- Added `m0-strict-0.4.0` as the explicitly versioned profile carrying rejection for `Scoring Engine`, `Rules Engine`, and `Inference Service`.
- Made `m0-strict-0.4.0` the default profile for new validation while preserving explicit historical evaluation under earlier profiles.

### Preserved
- Immutable v0.3.1 release history and public browser experience.
- Canonical v0.1.0 schemas.
- `m0-baseline-0.1.0` behavior and released `m0-strict-0.2.0` behavior.
- Frozen GA-001 v1.0.0 evidence and public-view contract 0.3.0.
- M0 maturity, no-score behavior, and human consequential authority.

## [0.3.1] - 2026-08-10

### Corrected
- Reconciled README public-boundary truth and website-integration record truth.
- Added narrow automation-owner alias guards for Scoring Engine, Rules Engine, and Inference Service.
- Added explicit deterministic local-browser preview guidance.
- Tightened Trace wording so public use context is not presented as a program-specific requirement.

### Refined
- Clarified public-snapshot, public-evidence-state, and snapshot-toolkit microcopy.
- Preserved compact journey navigation and a vertical Trace on narrow screens.
- Increased the dialog close target and added deliberate View Public Method / Back to Materials completion routes.

### Preserved
- Immutable v0.3.0 history.
- Canonical v0.1.0 schemas and existing validation-profile identifiers.
- Frozen GA-001 v1.0.0 snapshot/source/rights evidence.
- Public-view contract 0.3.0, M0 maturity, no-score behavior, and human consequential authority.

## [0.3.0] - 2026-08-10
### Added

- Derived, read-only Materials-to-Mission browser with the seven-stage Golden Journey.
- Frozen GA-001 v1.0.0 Gallium public-source evidence snapshot and source-support view.
- Versioned public view contract 0.3.0 and controlled Explore/Examine presentation tokens.
- Exact GitHub Pages deployment workflow with full-SHA-pinned Actions.

### Verified

- Observed desktop, mobile, 320px, reduced-motion, and 200%-zoom-equivalent browser UAT.
- Accessibility, privacy, security, performance, deterministic build, and exact public-byte readback.
- Corrected Examine-accent contrast, implicit favicon request, and reduced-motion skip-link focus visibility.
- HTTPS production deployment with human consequential authority preserved.

### Maturity

- Public maturity remains M0.
- Canonical v0.1.0 schema identifiers remain unchanged.
- Validation profiles remain `m0-baseline-0.1.0` and `m0-strict-0.2.0`.
- GA-001 is a public-source evidence snapshot, not a real operational Case 001.
- No M1, qualification, certification, compliance, acquisition, production, or autonomous-decision claim is made.

## [0.2.0] - 2026-08-10 (candidate)

### Added

- Explicit validation-profile identity independent from immutable v0.1.0 schema identity.
- Historical `m0-baseline-0.1.0` compatibility behavior, including the original v0.1.0 public-boundary behavior.
- Default `m0-strict-0.2.0` strengthened M0 behavior.
- Machine-readable validation output carrying toolkit and validation-profile identity.
- Dedicated Python 3.12 consumer-path CI using the documented public install.
- Historical released-reference regression coverage.

### Fixed

- Include the exact setuptools build backend in the public consumer/bootstrap lock.
- Distinguish toolkit-not-installed failures from case-validation failures in the guided evaluator.
- Derive CLI/package version identity from installed package metadata with a source-tree fallback.
- Isolate invalid teaching fixtures to their intended failure.
- Surface ambiguous named-human plus automation authority declarations for review.
- Detect demonstrated Greek/Cyrillic confusable automation and protected-content forms.
- Enforce synthetic public-reference state coherently in both directions.
- Add high-value ITAR, CUI, and export-controlled public-boundary patterns.
- Force generated validation-report and repository-manifest bytes to LF so release archives reproduce identically across Windows and POSIX checkouts.

### Compatibility erratum

The v0.1.1 and v0.1.2 lines preserved the immutable v0.1.0 **structural schema identifiers**, but they also strengthened ERROR-level semantic validation. Therefore the earlier phrase "all existing public data contracts" was broader than the demonstrated behavior.

Candidate 0.2.0 resolves that ambiguity by keeping schema authority unchanged while versioning semantic acceptance behavior explicitly through validation profiles.

### Maturity

- Public maturity remains M0.
- No real Case 001 is published.
- No M1, qualification, certification, compliance, acquisition, production, commercial-readiness, or operational-authorization claim is made.
- No browser application or Gallium public snapshot is included.

## [0.1.2] - 2026-08-09

### Fixed

- Harden human-authority declarations against demonstrated automation-only aliases while
  preserving clearly named humans in AI, model-risk, and automation roles.
- Reject duplicate Decision Charter requirement identifiers across requirements and
  acceptance criteria.
- Derive validation-report release identity from the reviewed project version.
- Normalize generated validation evidence to prevent trailing-whitespace drift.
- Return a controlled package error for direct rendering of an unvalidated record.

### Added

- Guided one-command public evaluation with calm fail-closed output.
- Focused scope, M1 Case 001, readiness-state, and private-case template guidance.
- Deterministic exact-diff protected-content verification before the corrective merge.

### Documentation

- Reconcile current-state records with the `v0.1.2` release line.
- Preserve the immutable `v0.1.0` schema baseline and `v0.1.1` maintenance lineage.
- Keep M1, qualification, certification, adoption, and operational-authorization
  non-claims explicit.

### Validation

- 118 collected tests with all runnable tests passing.
- 97 percent combined statement and branch coverage.
- Hosted Ubuntu and Windows Python 3.11 and 3.13 checks.
- CodeQL analysis.
- Deterministic packaging, exact five-asset release verification, and archive-to-tree
  equality.

## [0.1.1] - 2026-08-09

### Added

- Exact evidence, requirement, critical-condition, and decision-identity validation.
- Conservative visibility treatment for partially supported evidence.
- Structured public-boundary key scanning and controlled deeply nested JSON failures.
- Neutral schema-valid authoring templates and assurance regression coverage.
- Dated current-state and M1-readiness records with machine-readable M0 non-claims.
- Generic signed-tag release automation and a dedicated v0.1.1 release record.

### Changed

- Directly declare the imported `referencing` runtime dependency.
- Permit symlinks only inside untracked Git-ignored local or generated paths while
  preserving tracked, unignored, and release-package symlink rejection.
- Canonicalize repository-manifest hashing and release-archive identity across Windows
  and Linux.
- Clarify that tests, documentation, schemas, and generated artifacts do not establish M1.
- Preserve the immutable v0.1.0 schema authority and all existing public data contracts.

### Validation

- Complete repository-native validation with a strict 95 percent coverage floor.
- Hosted Ubuntu and Windows Python 3.11 and 3.13 checks.
- CodeQL analysis.
- Deterministic packaging and exact five-asset release verification.

## [0.1.0] - 2026-08-08

### Added

- Public Materials-to-Mission method and evidence boundaries.
- Decision Charter, Material Assurance Record, Evidence Record, and Decision Passport schemas.
- Synthetic critical-material pathway reference case.
- Command-line validation, report generation, public-boundary scanning, and deterministic packaging.
- Adversarial fixtures for missing authority, hidden uncertainty, critical-condition violations, and protected-content leakage.
- Cross-platform continuous integration, CodeQL analysis, release automation, security policy, governance, and contribution guidance.

### Limitations

- No real supplier, customer, laboratory, sample, lot, price, capacity, vulnerability, or mission data.
- No certification, qualification, compliance, government adoption, production capacity, or commercial-validation claim.
- No stable cross-case product maturity is claimed.


### Convergence Hardening

- Finalized the v0.1.0 public license as MIT.
- Assigned immutable v0.1.0 schema identifiers.
- Added maturity, threat-model, website-integration, FDE-adapter, and supersession records.
- Updated GitHub Action pins.
- Made CI and local validation consume exact dependency locks.
- Split repository creation, metadata, and release authorization gates.
- Made validation reporting record exact combined coverage.


### Reliability and release hardening

- Corrected invalid `--json` validation output for slots-based findings.
- Added CLI failure-path, help, release-mode, and gate-contract regression tests.
- Added progressive onboarding, audience paths, and a five-minute evaluation.
- Updated setup-python to v7.0.0 and CodeQL Action to v4.37.6 using full commit pins.
- Separated source-maintainer gates from generated public-write gates.
- Added isolated-environment validation, exact-404 target checks, workflow-ID readback,
  partial-creation evidence, release-asset attestation, exact allowlists, and archive-to-tree closeout.
- Preserved MIT, the M0 public-method boundary, canonical standalone schemas, minimal website
  linkage, and FDE as a later consumer.

### Final Public-Release Hardening

- Aligned the configured coverage threshold with the 95 percent repository gate.
- Made packaged-resource validation fail closed without rewriting tracked files.
- Added generated-state cleanup before every complete validation run.
- Preserved canonical-source validation evidence on failure.
- Renamed the second source gate to describe its publication-kit boundary function.
- Added a separate publication-kit contract validator and regression coverage.
- Clarified source, publication-kit, hosted Release, and recovery responsibilities.
- Added a concise record-relationship diagram for first-time readers.

### Final Packaging Safety Closeout

- Rejected symbolic links in included package paths to prevent out-of-tree file capture.
- Rejected repository-root and other nonexcluded internal package destinations.
- Preserved deterministic packaging through excluded `dist/`, excluded `build/`, or external outputs.
- Added CLI and release regression tests for symlink, output-location, and repeat-build behavior.
- Corrected the website follow-on kit to match the actual v1.1.2 repository, which has no root `VERSION` file.

### Publication Identity Integrity Closeout

- Added strict candidate timestamp, predecessor, release-manifest, and environment consistency checks.
- Required complete publication-kit manifest coverage and rejected symbolic links or unlisted files.
- Verified bundle author and committer timestamps against the candidate identity.
- Added regression tests for contradictory predecessor metadata, timestamp drift, environment drift, and manifest gaps.

### Cross-Platform Validation Evidence Closeout

- Made the checked-in validation report host-independent while preserving the strict 95 percent local coverage floor.
- Required all runnable tests to pass on every operator machine.
- Permitted only the three documented symlink-unavailable skips on hosts that cannot create symbolic links.
- Added JUnit evidence parsing and regression tests for allowed and unexpected skips.
- Preserved canonical Linux symlink coverage while allowing Windows Gate 00 to reproduce the approved evidence contract.
