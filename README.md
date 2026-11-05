# Materials-to-Mission

**Evidence-backed materials decisions · Deterministic validation · Human-owned conclusions**

Materials-to-Mission traces a material or component dependency from source evidence to a defined human decision—keeping uncertainty visible and stopping a continuous evidence path at the first unresolved link.

[Live experience](https://bridgenode7.com/materials-to-mission/) · [Five-minute evaluation](docs/FIVE_MINUTE_EVALUATION.md) · [Method](docs/METHOD.md) · [Validation](VALIDATION_REPORT.md) · [Latest release](https://github.com/Bridge-Node-7/materials-to-mission/releases/latest) · [Partner](https://bridgenode7.com/partner/)

## Role

The materials and physical-dependency domain implementation within [Bridge Node 7’s Frontier Assurance Architecture](https://github.com/Bridge-Node-7/Bridge-Node-7/blob/main/docs/FRONTIER_ASSURANCE_ARCHITECTURE.md). It owns the Material Assurance Record and domain methodology. Accountable human decisions remain human-owned.

## Method

Critical-material and advanced-material decisions often fail because evidence, assumptions, unknowns, requirements, alternatives, and decision authority are scattered.

Materials-to-Mission makes that chain inspectable:

`Signal → Source → Evidence → Requirement → Material → Origin → Process → Supplier → Facility → Component → System → Mission → Risk → Weak Link → Alternative → Qualification Evidence State → Mitigation → Human Decision → Action → Outcome → Proof → Reassessment`

Later supported facts may remain useful context; they do not silently repair an earlier evidence gap.

## What you can do

- Explore the Materials-to-Mission Atlas and engineered-material systems
- Inspect Gallium GA-001 as a bounded reviewed public-source pathway
- Examine YIG as bounded public research context
- Validate synthetic or public-safe records against explicit evidence rules
- Keep unknown, unsupported, expired, and contradictory evidence visible
- Generate a Decision Passport from the complete evidence-bearing record
- Preserve a named human owner for every consequential disposition

## Try it in five minutes

Requires Python 3.11+ (`python3`). Keep the virtualenv outside the clone.

```bash
python3 -m venv ../m2m-venv
source ../m2m-venv/bin/activate        # Windows Git Bash: source ../m2m-venv/Scripts/activate
python3 -m pip install -r requirements.txt
python3 -m pip install --no-deps --no-build-isolation -e .
python3 scripts/evaluate_public_method.py
```

Expected result:

```text
PASS - SYNTHETIC CASE VALID
PASS - DECISION PASSPORT WRITTEN
PASS - FAIL-CLOSED EXAMPLE CONFIRMED
NEXT - OPEN build/guided-decision-passport.md
```

Direct CLI:

```bash
m2m validate examples/synthetic-critical-material-pathway/case.json --public
m2m render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md
m2m validate examples/invalid/missing-human-owner.json --public --json
```

## Evidence model

The complete evidence lineage lives in the **Material Assurance Record**. The **Decision Passport** is the human-facing decision artifact derived from it.

Automation validates structure, declared evidence state, boundaries, and deterministic behavior.

## Public demonstrations

**GA-001** — reviewed public-source Gallium evidence snapshot. Supply-policy context is maintained separately in [Current State](docs/CURRENT_STATE.md) so new public facts do not silently rewrite the GA-001 review basis.

**YIG-001** — bounded Reviewed Public Context connecting scientific evidence to a material-system pathway while leaving unresolved qualification and supply links explicit.

Checked-in validation state: [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md).

## Assurance boundary

Truth certification, supplier or material qualification, acquisition approval, and consequential judgment remain with accountable human processes. Public examples are evaluation material.

## Release

`main` is the current reviewed source. Distribution identity lives on Releases and in CHANGELOG.

## Reference

- [Start Here](docs/START_HERE.md) · [Method](docs/METHOD.md) · [Evidence Model](docs/EVIDENCE_MODEL.md)
- [Material Assurance Record](docs/MATERIAL_ASSURANCE_RECORD.md) · [Decision Passport](docs/DECISION_PASSPORT.md)
- [Qualification and Readiness States](docs/QUALIFICATION_AND_READINESS_STATES.md)
- [Interoperability](docs/INTEROPERABILITY.md) · [Validation](docs/VALIDATION.md) · [Scope](docs/SCOPE.md)
- [Schema Catalog](SCHEMA_CATALOG.json) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

MIT licensed. Built and maintained by [Bridge Node 7](https://bridgenode7.com/).
