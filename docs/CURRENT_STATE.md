# Current State

**As of August 9, 2026**

Materials-to-Mission remains an **M0 experimental public method baseline**. The public
`v0.1.0` release is immutable and remains the latest released version. The repository
does not claim M1 real workflow proof, material or supplier qualification, certification,
commercial validation, government adoption, or mission authorization.

## Released Baseline

The immutable `v0.1.0` release provides the public method, six canonical schemas,
synthetic examples, validation tooling, deterministic packaging, governance records, and
explicit public/private boundaries.

## Current Main Branch

Main includes unreleased assurance and portability maintenance after `v0.1.0`:

- stricter evidence, requirement, decision-identity, and critical-condition validation;
- conservative handling of partially supported evidence;
- structured public-boundary key scanning;
- neutral authoring templates;
- controlled deeply nested JSON failure behavior;
- host-independent manifest hashing for UTF-8 text;
- regression coverage for Linux and Windows behavior.

The merged maintenance work passed the complete local repository gate, the hosted Ubuntu
and Windows Python 3.11 and 3.13 matrix, and CodeQL. These results support maintenance
readiness only. They do not establish M1.

## Release Status

The maintenance changes are documented under Unreleased in `CHANGELOG.md`. No `v0.1.1`
tag or release has been created. Release authorization, exact-head verification, asset
readback, and public closeout remain separate gates.

## M1 Status

M1 is **not achieved**. No approved real Case 001, private case evidence package,
independent case review, human disposition, measured outcome, or authorized sanitized
case study is present in this public repository.

See [`M1_READINESS.md`](M1_READINESS.md) for the evidence required before an M1 claim.

## Website and Integration Status

This repository does not modify the Bridge Node 7 website. Minimal website linkage remains
a separate repository change governed by [`WEBSITE_INTEGRATION.md`](WEBSITE_INTEGRATION.md).

Frontier Decision Engine integration also remains deferred until a separately reviewed
thin adapter is justified by released contracts and case evidence.
