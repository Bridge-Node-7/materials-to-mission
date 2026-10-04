# Schedule Exposure and Common-Cause Dependency

Materials-to-Mission should make physical dependency risk visible in the dimensions that materially affect a mission decision.

Cost alone is often insufficient. A low-cost component may control schedule because it is difficult to qualify, concentrated in one facility, dependent on a unique process, or supported by suppliers that appear independent while sharing the same upstream source.

This guidance defines two bounded human-facing views:

- Schedule Exposure
- Common-Cause Dependency

Neither view qualifies a supplier, certifies capacity, predicts delivery with certainty, or replaces the Material Assurance Record.

## Schedule Exposure

Schedule Exposure answers:

> Which material, component, process, supplier, facility, or qualification dependency may materially move the mission schedule?

A useful view may include:

- dependency identity;
- mission or system relationship;
- authoritative source references;
- stated lead time;
- lead-time evidence date;
- qualification duration;
- test-capacity dependency;
- inventory or buffer state when authorized;
- substitute state;
- latest responsible action;
- downstream milestone;
- uncertainty;
- accountable owner;
- reopen condition.

Unsupported values should remain absent or unknown.

## Schedule evidence

A schedule statement is evidence only for what its source establishes.

Examples include:

- supplier-quoted lead time;
- historical observed lead time;
- contractual milestone;
- internal planning target;
- manufacturing-cycle estimate;
- qualification-duration estimate;
- logistics estimate.

These should remain distinguishable.

A planning date must not silently become a supplier commitment.

A supplier statement must not silently become verified capacity.

## Schedule Receipt pattern

Where a schedule claim materially controls a decision, preserve a bounded receipt containing:

- schedule claim;
- source;
- source date or observed time;
- target or milestone date;
- dependency;
- assumptions;
- evidence freshness;
- current validity;
- invalidation trigger;
- affected decision.

This is a documentation pattern, not a new portable contract.

Repeated operational use should prove whether a future versioned contract is justified.

## Latest responsible action

A useful decision surface may show the latest point at which an action may be taken without knowingly violating a declared schedule assumption.

That date must remain traceable to its assumptions.

It is not a guarantee.

When uncertainty is high, expose the range or unresolved state instead of manufacturing precision.

## Common-Cause Dependency

Common-Cause Dependency answers:

> Which apparently independent supply paths may fail together because they share an upstream dependency?

Relevant relationships may include:

- common parent company;
- common manufacturing facility;
- common sub-tier supplier;
- common raw-material source;
- common process;
- common qualification facility;
- common piece of unique equipment;
- common logistics corridor;
- common geography;
- common energy or utility dependency;
- common regulatory exposure.

Apparent supplier count must not be treated as independent resilience when hidden dependencies are shared.

## Independence rule

Five suppliers do not necessarily represent five independent sources.

Two manufacturers using the same critical sub-tier may form one practical failure domain.

Three geographically separate suppliers may still depend on one process chemistry or qualification facility.

The view should expose declared dependency structure rather than calculate an opaque diversification score.

## Qualification boundary

Alternative availability and alternative qualification are different states.

A substitute may exist commercially while remaining unusable for the mission because:

- technical requirements are not met;
- testing is incomplete;
- process changes require requalification;
- integration evidence is missing;
- customer approval is required;
- schedule is insufficient.

The method should keep these states separate.

## Mission consequence

Schedule and common-cause views should connect only to declared mission consequences.

Useful questions include:

- Which milestone is affected?
- What capability depends on the item?
- What is the first unresolved link?
- Which alternative is genuinely qualified?
- What evidence would retire the uncertainty?
- What action remains reversible?
- What happens if no action is taken?

No risk score is required to answer these questions.

## Relationship to the Material Assurance Record

The Material Assurance Record remains authoritative for the bounded material pathway.

Schedule Exposure and Common-Cause Dependency are projections from governed data.

They must not create competing supplier, facility, qualification, or evidence records.

## Relationship to Mission Graph

Where a physical dependency materially affects a cross-system decision, Mission Graph may consume the declared relationship through an approved interface or bounded case process.

Mission Graph may then expose shared failure domains or prepare a human-owned ProofRequest.

The upstream Materials-to-Mission record remains authoritative for its domain semantics.

## Customer and supplier handling

Real customer, supplier, facility, price, inventory, and contract information may be sensitive.

Public examples must remain synthetic or explicitly public-safe.

Repository visibility is not handling authorization.

## Success criterion

The views succeed when a decision owner may understand which physical dependency threatens schedule or creates hidden common-cause exposure without mistaking the projection for supplier qualification, guaranteed delivery, or automated decision authority.
