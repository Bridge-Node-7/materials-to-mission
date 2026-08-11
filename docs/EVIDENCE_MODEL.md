# Evidence Model

## Evidence Basis

- `OBSERVED`: directly observed and recorded
- `TESTED`: produced through a defined test or measurement
- `DOCUMENTED`: contained in an identifiable document or record
- `REPORTED`: asserted by a source but not independently confirmed
- `INFERRED`: derived analytically from other records
- `ASSUMED`: used temporarily and explicitly as an assumption

## Claim State

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `CONTRADICTED`
- `UNSUPPORTED`
- `UNKNOWN`
- `NOT_APPLICABLE`
- `EXPIRED`

Basis and claim state are separate. A documented claim may still be
contradicted, unsupported, or expired.

## Required Provenance

Every material evidence item records an identifier, source, locator, version,
dates, basis, claim state, confidence, applicability, limitations, linked
requirements, contradictory evidence, public or protected classification, AI
involvement, and human reviewer.

## Evidence Discipline

- Completion of a field does not establish truth.
- Contradictions remain visible.
- Unknown is not equivalent to favorable.
- Expired evidence remains preserved but is not treated as current.
- AI summaries link to underlying sources and remain reviewable.

## Critical Distinctions

- `UNKNOWN` and `CONTRADICTED` remain distinct evidence states.
- Claim support is not pathway assessment.
- Evidence-supported action is not human decision.
- No composite readiness score is used; critical conditions do not average away.
