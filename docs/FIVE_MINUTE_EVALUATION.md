# Five-Minute Evaluation

This path gives a first-time evaluator one visible success and one visible fail-closed result.

**Prerequisite:** complete the installation steps in the root README. The five-minute path begins after installation.

## 1. Open the Synthetic Case

Review:

`examples/synthetic-critical-material-pathway/case.json`

Notice the supported, unknown, contradictory, and critical evidence states. Everything is
fictional and public-safe.

## 2. Validate It

```bash
m2m validate examples/synthetic-critical-material-pathway/case.json --public --profile m0-strict-0.2.0
```

Expected:

```text
PASS - case is structurally and semantically valid
```

## 3. Render the Decision Passport

```bash
m2m render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md --profile m0-strict-0.2.0
```

Open `build/decision-passport.md`. Locate the governing weak link, human authority,
disposition, stop rule, and reassessment trigger.

## 4. Inspect a Deliberate Failure

```bash
m2m validate examples/invalid/missing-human-owner.json --public --json --profile m0-strict-0.2.0
```

Expected:

- exit code `2`;
- valid JSON findings;
- a visible required-human-owner schema failure;
- no Python traceback.

## 5. Change One Evidence State

Copy the synthetic case, change one evidence claim state, and run validation again. Confirm
that unknown or contradictory evidence remains visible and that a triggered critical
condition cannot be averaged away.

## What Success Means

You have confirmed that the public method can preserve evidence state, block unsupported
progression, and produce a concise human-facing artifact. You have not qualified a real
material or supplier.
