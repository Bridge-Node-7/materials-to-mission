# Materials-to-Mission

**Evidence-backed materials decisions · Deterministic validation · Human-owned conclusions**

Materials-to-Mission is Bridge Node 7's open-source method and toolkit for tracing a material or component dependency from source evidence to a defined human decision.

**[Open the live experience](https://bridgenode7.com/materials-to-mission/)** · **[Run the five-minute evaluation](docs/FIVE_MINUTE_EVALUATION.md)** · **[Read the method](docs/METHOD.md)** · **[See validation evidence](VALIDATION_REPORT.md)**

## Why It Exists

Critical-material and advanced-material decisions often fail because evidence, assumptions, unknowns, requirements, alternatives, and decision authority are scattered across documents and systems.

Materials-to-Mission makes that chain inspectable:

`Signal → Source → Evidence → Requirement → Material → Origin → Process → Supplier → Facility → Component → System → Mission → Risk → Weak Link → Alternative → Qualification Evidence State → Mitigation → Human Decision → Action → Outcome → Proof → Reassessment`

The method keeps uncertainty visible and stops a continuous evidence path at the first unresolved link. Later supported facts may remain useful context, but they do not silently repair an earlier evidence gap.

## What You Can Do

- Explore the 60-mineral Materials-to-Mission Atlas and engineered-material systems.
- Inspect Gallium GA-001 as a bounded reviewed public-source pathway.
- Examine YIG as bounded public research context without turning research into readiness.
- Validate synthetic or public-safe records against explicit evidence rules.
- Keep unknown, unsupported, expired, and contradictory evidence visible.
- Prevent critical conditions from being averaged away.
- Generate a concise Decision Passport from the complete evidence-bearing record.
- Preserve a named human owner for every consequential disposition.

## Try It in Five Minutes

Requires Python 3.11 or newer.

    python -m venv .venv
    source .venv/bin/activate        # Windows Git Bash: source .venv/Scripts/activate
    python -m pip install -r requirements.lock
    python -m pip install --no-deps --no-build-isolation -e .
    python scripts/evaluate_public_method.py

Expected result:

    PASS - SYNTHETIC CASE VALID
    PASS - DECISION PASSPORT WRITTEN
    PASS - FAIL-CLOSED EXAMPLE CONFIRMED
    NEXT - OPEN build/guided-decision-passport.md

Direct CLI use:

    m2m validate examples/synthetic-critical-material-pathway/case.json --public
    m2m render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md
    m2m validate examples/invalid/missing-human-owner.json --public --json

## Evidence Model

The complete evidence lineage lives in the **Material Assurance Record**. The **Decision Passport** is the smaller human-facing decision artifact derived from it.

Automation validates structure, declared evidence state, boundaries, and deterministic behavior. It does not certify truth, qualify a supplier or material, approve acquisition, or replace human judgment.

## Public Demonstrations

**GA-001** is a reviewed public-source Gallium evidence snapshot based on official public sources and original paraphrase. It is not a real operational Case 001 and does not imply qualification, acquisition approval, mission readiness, adoption, or commercial validation.

**YIG-001** is bounded Reviewed Public Context. It demonstrates how scientific evidence may be connected to a material-system pathway while leaving unresolved qualification and supply links explicitly unresolved.

## What Is Proven Here

The repository demonstrates a versioned evidence structure, deterministic validation, fail-closed public boundaries, reproducible packaging, public-source provenance, explicit human decision authority, and a working browser experience.

The current checked-in test, coverage, packaging, and validation state is recorded in [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md).

## What Is Not Claimed

This repository does not establish material or supplier qualification, certification or legal compliance, production capacity or assured supply, laboratory validity outside supplied evidence, acquisition or mission readiness, customer adoption or commercial validation, government endorsement, investment merit, or guaranteed mission performance.

Public maturity remains **M0 experimental public method**.

## Technical Reference

- [Start Here](docs/START_HERE.md)
- [Method](docs/METHOD.md)
- [Evidence Model](docs/EVIDENCE_MODEL.md)
- [Material Assurance Record](docs/MATERIAL_ASSURANCE_RECORD.md)
- [Decision Passport](docs/DECISION_PASSPORT.md)
- [Qualification and Readiness States](docs/QUALIFICATION_AND_READINESS_STATES.md)
- [Interoperability](docs/INTEROPERABILITY.md)
- [Validation](docs/VALIDATION.md)
- [Validation Profiles](docs/VALIDATION_PROFILES.md)
- [Public Boundary](docs/PUBLIC_BOUNDARY.md)
- [AI Provenance](docs/AI_PROVENANCE.md)
- [Schema Catalog](SCHEMA_CATALOG.json)

## Public Boundary

This repository contains material approved for public release. Public examples are synthetic or explicitly identified public-source records.

Use [`SECURITY.md`](SECURITY.md) for private vulnerability reporting.

## Open Source

MIT licensed. Contributions should remain public-safe, evidence-aware, tested, and human-accountable. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

Built and maintained by [Bridge Node 7](https://bridgenode7.com/).
