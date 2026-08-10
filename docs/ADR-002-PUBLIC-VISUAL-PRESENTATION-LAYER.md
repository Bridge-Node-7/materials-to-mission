# ADR-002: Public Visual Presentation Layer

**Status:** Accepted for the v0.3.0 visual-experience line

## Context

Materials-to-Mission is an M0 experimental public method. Its semantic authority remains
the Python validation implementation operating against the immutable v0.1.0 canonical
schema authority and an explicit validation profile. A browser experience may make the
method easier to understand, but it must not become a second source of semantic truth.

## Decision

The public visual layer is a **derived, read-only, non-authoritative presentation layer**.

It may:

- render evidence and pathway state already supported by controlled source data;
- explain what is claimed, supported, unresolved, contradicted, expired, revoked, or
  superseded;
- show trace relationships from material through mission dependence;
- expose supporting evidence and the rules used to derive a presentation state;
- present evidence-supported next-action options without deciding for the user.

It must not:

- mutate canonical records;
- duplicate or replace Python semantic validation;
- create a second schema authority;
- convert missing evidence into favorable status;
- collapse critical conditions into a compensating composite score;
- approve, qualify, certify, waive, terminate, or close a consequential decision;
- require accounts, telemetry, a hosted backend, or remote persistence for the initial
  public experience.

## Interaction Grammar

The visual grammar is:

**FIELD → FOCUS → PROOF**

- **FIELD** establishes the system context and visible pathway.
- **FOCUS** narrows attention to one material, dependency, constraint, or decision.
- **PROOF** reveals the evidence, provenance, validation profile, limitations, and human
  authority needed to understand the displayed state.

## Experience Modes

The initial experience uses two complementary modes:

- **Explore:** deep-midnight field for possibility, structure, and pathway orientation.
- **Examine:** warm-mineral-ivory field for evidence, consequence, and decision review.

The visual experience becomes more beautiful as evidence becomes more explicit, never as
claims become more dramatic.

## Version Axes

The public experience keeps these version axes distinct:

1. canonical schema version;
2. validation-profile version;
3. toolkit/software version;
4. public view-contract version;
5. application/presentation version.

The initial public view contract is `0.3.0`. It is not a replacement for the v0.1.0
canonical schemas.

## Consequences

The browser may evolve rapidly without changing canonical data contracts. Semantic changes
remain evidence-gated and profile-versioned. Human authority remains explicit at every
consequential disposition.
