# Start Here

Materials-to-Mission supports one bounded question:

> Does the available evidence justify a defined next action for a specific material,
> source, process, component, or mission dependency?

## The Seven-Step Method

1. Define the decision and human authority in a Decision Charter.
2. Record requirements and noncompensating critical conditions.
3. Collect source-linked evidence without hiding unknowns or contradictions.
4. Build the Material Assurance Record.
5. Generate the Decision Passport.
6. Obtain independent review where the decision is consequential.
7. Record the human disposition, action, outcome, and reassessment trigger.

Use the synthetic example only to learn the structure. It is not evidence for a real
material, source, supplier, laboratory, or mission.

## Choose a Path

### Evaluate the Method

1. Read [`FIVE_MINUTE_EVALUATION.md`](FIVE_MINUTE_EVALUATION.md).
2. Open the synthetic case in `examples/synthetic-critical-material-pathway/`.
3. Render its Decision Passport and inspect the intentional failure fixtures.

### Integrate the Schemas

1. Read the root `SCHEMA_CATALOG.json`.
2. Review [`INTEROPERABILITY.md`](INTEROPERABILITY.md).
3. Preserve the canonical `v0.1.0` schema identifiers and human-authority fields.
4. Read [`VALIDATION_PROFILES.md`](VALIDATION_PROFILES.md) before depending on semantic accept/reject behavior.

### Understand Current Maturity

1. Read [`CURRENT_STATE.md`](CURRENT_STATE.md).
2. Read [`MATURITY_AND_PROOF.md`](MATURITY_AND_PROOF.md).
3. Use [`M1_READINESS.md`](M1_READINESS.md) before proposing any real Case 001.

Documentation readiness does not establish M1.

### Maintain the Repository

1. Read [`VALIDATION.md`](VALIDATION.md).
2. Run `python scripts/check_repo.py`.
3. Review [`RELEASE_PROCESS.md`](RELEASE_PROCESS.md) before changing release behavior.

### Review the Public Boundary

1. Read [`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md).
2. Read [`PRIVATE_CASE_BOUNDARY.md`](PRIVATE_CASE_BOUNDARY.md).
3. Run `m2m scan <record.json> --json` before proposing any public fixture.
