# Threat Model

## Scope

This threat model covers the public Materials-to-Mission repository, its schemas,
CLI, synthetic fixtures, validation tooling, release automation, and contribution
paths. Use repository inputs that are approved for the intended environment.

## Security properties

- Integrity of canonical schemas and version identifiers
- Human decision authority
- Approved-release surface integrity
- Deterministic release identity
- Synthetic-fixture authenticity
- Validation and release evidence
- Repository and release signing authority

## Primary Threats

### Unintended Publication

A contribution may include material that is not approved for the repository's
distribution context.

**Controls:** release-surface validation, scanner, synthetic fixtures, contribution
guidance, human review, and a fail-closed release gate.

### Authority Substitution

Software or AI may be presented as the final qualification, compliance, approval, or risk
authority.

**Controls:** required human owner, required human disposition, non-qualification language,
adversarial tests, visible limitations.

### Schema Drift or Split Authority

A second repository may publish incompatible copies of M2M schemas under the same artifact
names.

**Controls:** canonical authority declaration, immutable version URLs, adapter-only FDE
integration, compatibility tests.

### Evidence Laundering

Reported, assumed, inferred, expired, unsupported, or contradictory evidence may be
presented as tested or supported.

**Machine-checked controls:** declared evidence-state consistency, visible contradictions, semantic validation, and noncompensating critical conditions.

**Human-owned controls:** factual truth of evidence, source interpretation, sufficiency, and material significance. Automation can verify declared structure and consistency; it cannot certify that the underlying evidence is true or sufficient.


### Archive Path and Symlink Substitution

A release root may contain a symbolic link to protected files outside the reviewed tree, or a
package output may be written into an included directory and then absorbed into a later archive.

**Controls:** reject symbolic links in included release paths, ignore only explicitly excluded
transient directories, reject nonexcluded internal output directories, normalize archive modes,
and regression-test repeat packaging.

### Release Substitution

A release may be created from a different tree than the reviewed source.

**Controls:** exact commit and tree records, deterministic archive, SHA-256 manifests,
hosted-check review for the exact SHA, signed tag, public readback.

### Dependency or Action Compromise

A mutable dependency or GitHub Action may change after review.

**Controls:** full-SHA Action pins, exact dependency locks, CodeQL, Dependabot,
least-privilege workflow permissions.

### Resource Exhaustion or Malformed Input

Oversized, deeply nested, or malformed JSON may exhaust resources or bypass validation.

**Controls:** bounded parsing, schema limits, explicit validation, no network access in
core commands, test fixtures.

## Residual Risks

- Public repositories cannot prevent all misuse or misinterpretation.
- License selection does not resolve third-party patent or data rights.
- Synthetic validation cannot establish scientific or commercial validity.
- Human review quality remains dependent on reviewer competence and authority.
