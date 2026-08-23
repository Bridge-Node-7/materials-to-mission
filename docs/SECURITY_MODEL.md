# Security Model

The public toolkit is designed for synthetic and public-safe records.

Security controls include bounded JSON parsing, schema validation, semantic
rules, public-boundary scanning, no network access in core commands,
deterministic output, least-privilege GitHub workflows, pinned Actions, CodeQL,
and private vulnerability reporting.

The repository is not approved storage for controlled, confidential,
export-controlled, procurement-sensitive, personally identifiable, or
patent-sensitive information.

Repository and release manifests establish byte consistency. Verified signed tags and immutable GitHub Releases establish release authenticity; a manifest alone is not an authenticity proof. The public-boundary scanner is a repository guardrail, not a substitute for credential revocation or dedicated secret scanning.
