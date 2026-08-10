# Interoperability

Materials-to-Mission is designed to exchange synthetic decision records with
other evidence-governed tools while retaining its own schema authority.

Potential integrations include Frontier Decision Engine for decision
presentation, Frontier Intelligence Workflows for generic evidence and release
integrity, and Quantum Readiness for a separate domain-specific reference case.

Integration must preserve evidence classes, unknown states, critical conditions,
human authority, version identity, public boundaries, and provenance. Domain
scoring models must not be silently merged.

Validation consumers must preserve the distinction between structural schema identity and semantic validation-profile identity. Canonical records remain bound to the immutable v0.1.0 schemas, while semantic acceptance is evaluated under an explicit profile such as `m0-baseline-0.1.0` or `m0-strict-0.2.0`. A consumer must not infer a validation profile solely from `schema_version`.
