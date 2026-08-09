# Design Decisions

## DD-001: Standalone Public Repository

Materials-to-Mission is implemented as a focused standalone public repository.
The repository owns its method, public schemas, reference implementation,
synthetic examples, validation gates, and release lifecycle.

## DD-002: Synthetic Public Baseline

The public repository contains synthetic examples only. Real cases remain under
separate contractual, legal, security, privacy, and intellectual-property
controls.

## DD-003: Manual Record Before Automation

The public contracts model the Decision Charter, Material Assurance Record, and
Decision Passport. Automation validates and renders those records but does not
replace evidence collection, independent review, or human disposition.

## DD-004: Human Authority

Every consequential case names a human decision owner and a human disposition
authority. AI and scoring systems may not occupy either role.

## DD-005: Noncompensating Critical Conditions

A triggered critical condition blocks advancement or partnership until the
condition is resolved and the record is reassessed. Favorable evidence elsewhere
may not average the failure away.

## DD-006: Visible Uncertainty

Unknown, contradicted, unsupported, and expired evidence must remain visible in
the Decision Passport.

## DD-007: Public and Protected Separation

The repository excludes real suppliers, customers, laboratories, facilities,
samples, lots, prices, capacities, vulnerabilities, patent-sensitive methods,
and restricted information.

## DD-008: No Certification Claim

Repository validation proves only specified software and record behaviors. It
does not qualify a material or supplier, certify compliance, authorize a
mission, or prove commercial value.

## DD-009: Interoperability Without Conflation

Future integrations may exchange records with Frontier Decision Engine,
Frontier Intelligence Workflows, and Quantum Readiness, but domain-specific
scoring and authority boundaries remain separate.


## DD-010: M0 Public Method Before Case 001

The newest explicit program decision authorizes a dedicated public repository now.
The repository may publish an M0 experimental method baseline before a real Case 001
because it contains synthetic records only and makes no M1 workflow-proof, qualification,
customer, laboratory, or commercial claim.

Manual proof before software abstraction remains binding for M1 and later maturity claims.
The public M0 baseline must not be represented as real-world validation.

## DD-011: Canonical Schema Authority

`Bridge-Node-7/materials-to-mission` is the single public authority for Materials-to-Mission
schemas and contract versions. Frontier Decision Engine may consume or adapt released
contracts but may not redefine or independently version the same M2M artifacts.

## DD-012: Immutable v0.1.0 Schema Identifiers

The initial canonical schema identifiers use immutable, version-tag-bound raw GitHub URLs:

`https://raw.githubusercontent.com/Bridge-Node-7/materials-to-mission/v0.1.0/schemas/`

A branded schema domain may be introduced later only with a documented stability,
redirect, and compatibility policy.

## DD-013: Minimal Website Integration

The first website integration is one restrained external repository link on the existing
Materials page, plus validator coverage. No new website route or sitemap entry is required
for the initial repository release.

## DD-014: FDE as Consumer

The first FDE integration is a thin, version-declared adapter to a released M2M contract.
FDE remains general decision infrastructure and does not become a second M2M schema authority.
