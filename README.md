# Materials-to-Mission

**M0 experimental public method · Synthetic reference cases + reviewed public-source snapshot · Human-owned decisions**

Materials-to-Mission is Bridge Node 7's public-safe method and validation toolkit for
connecting a consequential mission decision to the material, source, process, evidence,
risk, alternatives, human disposition, action, and proof that support it.

The repository is deliberately bounded. It provides versioned data contracts, a deterministic
CLI, synthetic reference cases, adverse fixtures, a complete Material Assurance Record, and
a concise Decision Passport. It does not publish real supplier intelligence, customer
records, laboratory data, patent-sensitive implementation, restricted technical information,
or operational vulnerabilities.

**Live public experience:** [https://bridgenode7.com/materials-to-mission/](https://bridgenode7.com/materials-to-mission/)  
**Five-minute evaluation:** [docs/FIVE_MINUTE_EVALUATION.md](docs/FIVE_MINUTE_EVALUATION.md)

GA-001 v1.0.0 is a reviewed public-source evidence snapshot based on official public sources.
It is **not** a synthetic canonical example and it is **not** a real operational Case 001.
Public-source demonstration does not imply qualification, acquisition approval, mission
readiness, adoption, or M1.

## One Question

> Does the available evidence justify a defined next action for this material, source,
> process, component, or mission dependency?

## Operating Chain

```text
Signal
→ Source
→ Evidence
→ Requirement
→ Material
→ Origin
→ Process
→ Supplier
→ Facility
→ Component
→ System
→ Mission
→ Risk
→ Weak Link
→ Alternative
→ Qualification Evidence State
→ Mitigation
→ Human Decision
→ Action
→ Outcome
→ Proof
→ Reassessment
```

## How the Records Fit

```mermaid
flowchart LR
    DC[Decision Charter] --> ER[Evidence Records]
    ER --> MAR[Material Assurance Record]
    MAR --> DP[Decision Passport]
    DP --> HD[Human Disposition]
    HD --> OR[Outcome and Reassessment]
```

The complete evidence lineage remains in the Material Assurance Record. The Decision
Passport presents the smallest useful human decision view without replacing that lineage.

## Who This Is For

- Independent researchers and builders exploring evidence-backed decisions
- Individual practitioners testing the method with synthetic records
- Technical reviewers evaluating portable schemas and validation behavior
- Small collaborators assessing whether future use is justified

These are evaluation audiences, not claims of adoption.

## What This Repository Proves

- The public record structure is internally consistent.
- Required evidence and decision fields may be validated.
- Unknown, unsupported, expired, and contradictory evidence remain visible.
- Triggered critical conditions cannot be averaged away.
- A consequential disposition requires a named human owner.
- A concise Decision Passport may be generated deterministically.
- A public release package may be built reproducibly.

## What This Repository Does Not Prove

- Material or supplier qualification
- Certification or compliance
- Legal ownership, origin, or foreign-control determinations
- Production capacity
- Laboratory validity outside the supplied synthetic record
- Customer adoption or commercial readiness
- Government endorsement, funding, selection, or authorization
- Investment merit or guaranteed mission performance

## Choose Your Path

**New to the method?** Read [`docs/START_HERE.md`](docs/START_HERE.md).
**Evaluating the toolkit?** Follow the [five-minute evaluation](docs/FIVE_MINUTE_EVALUATION.md).
**Integrating records?** Start with [`SCHEMA_CATALOG.json`](SCHEMA_CATALOG.json) and [`docs/INTEROPERABILITY.md`](docs/INTEROPERABILITY.md).
**Maintaining or releasing?** Use [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) and [`docs/ACTION_PIN_PROVENANCE.md`](docs/ACTION_PIN_PROVENANCE.md).
**Checking current maturity?** Read [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) and [`docs/M1_READINESS.md`](docs/M1_READINESS.md).
**Planning a protected case?** Use [`docs/M1_CASE_001_PLAYBOOK.md`](docs/M1_CASE_001_PLAYBOOK.md) and [`templates/private-case-readiness-checklist.md`](templates/private-case-readiness-checklist.md).
**Reviewing future options and boundaries?** Read [`docs/PROGRAM_REGISTER.md`](docs/PROGRAM_REGISTER.md).

## Evaluate the Method

Create an isolated environment and install the public toolkit:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows Git Bash: source .venv/Scripts/activate
python -m pip install -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
```

The public consumer/bootstrap lock includes the exact build backend required by the documented `--no-build-isolation` installation.

Semantic validation uses an explicit profile. New validation defaults to `m0-strict-0.4.0`. Released `m0-strict-0.2.0` remains available for explicit compatibility evaluation, and historical v0.1.0 compatibility remains available with `--profile m0-baseline-0.1.0`. Machine-readable validation output states the profile and toolkit version actually used.

Validate and render the synthetic reference:

Run the guided five-minute evaluation:

```bash
python scripts/evaluate_public_method.py
```

Expected operator view:

```text
PASS - SYNTHETIC CASE VALID
PASS - DECISION PASSPORT WRITTEN
PASS - FAIL-CLOSED EXAMPLE CONFIRMED
NEXT - OPEN build/guided-decision-passport.md
```

The individual public commands remain available:

```bash
m2m validate examples/synthetic-critical-material-pathway/case.json --public
m2m render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md
```
Inspect one intentional failure:

```bash
m2m validate examples/invalid/missing-human-owner.json --public --json
```

Expected result: valid JSON findings and exit code `2`, with no traceback.

## Develop or Maintain the Repository

```bash
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/check_repo.py
```

Installed commands:

```text
m2m validate   Validate a case and its declared evidence state
m2m render     Render the Decision Passport as Markdown
m2m scan       Scan a JSON record for protected public-boundary tokens
m2m package    Build a deterministic, symlink-rejecting repository archive
m2m schema-dir Print the installed canonical schema directory
```

Packaging safety:

- `m2m package` rejects symbolic links in included paths rather than following them.
- Output must be under excluded `dist/` or `build/`, or outside the release root.
- Repeated packaging is deterministic when the reviewed source is unchanged.

Exit codes:

```text
0  successful result
2  validation or public-boundary finding
3  input, filesystem, or controlled operational error
```

CLI usage errors are treated as input errors and exit `3`.

## Core Artifacts

- `schemas/common.schema.json`
- `schemas/decision-charter.schema.json`
- `schemas/evidence-record.schema.json`
- `schemas/material-assurance-record.schema.json`
- `schemas/decision-passport.schema.json`
- `schemas/case.schema.json`
- `templates/`
- `examples/synthetic-critical-material-pathway/`
- `docs/`
- `docs/VALIDATION_PROFILES.md`

## Decision Artifacts

The **Material Assurance Record** is the complete evidence-bearing record.

The **Decision Passport** is the concise human-facing decision artifact derived from it.

Automation checks structure and declared conditions. **Human authority owns every
consequential conclusion.**

## Public Boundary

Synthetic reference cases remain fictional and synthetic. GA-001 v1.0.0 is separately
identified as a bounded **reviewed public-source evidence snapshot** containing official-source
metadata and original paraphrase. It is not private operational evidence and not a real Case
001.

Public records must not contain real customer names, nonpublic supplier identities, samples,
lots, protected facilities, prices, capacities, vulnerabilities, protected laboratory results,
patent-sensitive methods, classified information, controlled unclassified information,
export-controlled technical data, or other restricted content. See
[`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

## Repository Maturity

`v0.4.0` is the bounded M0 validation-profile compatibility closeout. It preserves the
immutable v0.3.1 public experience, immutable v0.1.0 structural schema authority, released
validation-profile behavior under explicit identifiers, GA-001 v1.0.0 evidence meaning, M0
maturity, and human consequential authority.

The live public experience is
[bridgenode7.com/materials-to-mission/](https://bridgenode7.com/materials-to-mission/).
The repository remains M0 until the real-workflow evidence in
[`docs/M1_READINESS.md`](docs/M1_READINESS.md) is complete. It is not a validated
cross-case commercial product or an authority for certification or qualification.

## Bridge Node 7 Portfolio Fit

- [Bridge Node 7](https://bridgenode7.com/) provides public context and routing.
- **Materials-to-Mission** owns the canonical public method, schemas, validator, synthetic
  reference cases, reviewed public-source snapshots, and derived visual experience.
- [Frontier Decision Engine](https://github.com/Bridge-Node-7/frontier-decision-engine)
  remains generic decision infrastructure and may later consume this contract through a thin adapter.
- Real operational cases and protected evidence remain in controlled private systems.

The separately governed Materials page routes to the live Materials-to-Mission experience.
The application itself provides **View Public Method** access back to this repository.
No additional website release is required for this repository-only maintenance line.

## Security

Do not open a public issue containing sensitive information. Follow [`SECURITY.md`](SECURITY.md)
for private vulnerability reporting.

## License

MIT. The license applies only to content included in this repository. It does not grant
rights to excluded patents, private information, trademarks, or protected operational material.

## Maintainers Only

The `GATES/` directory validates the canonical source and verifies the boundary to a separately
generated exact publication candidate. Public users do not need the release gates to validate or
render cases. Public-write gates exist only in the reviewed publication kit and each requires a
separate authorization.
