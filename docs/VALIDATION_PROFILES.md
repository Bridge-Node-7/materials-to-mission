# Validation Profiles

Validation profiles version semantic acceptance behavior independently from the immutable v0.1.0 JSON Schema authority.

## `m0-baseline-0.1.0`

Historical compatibility profile for the semantic behavior shipped with the original v0.1.0 public method. Its compatibility corpus begins with the exact v0.1.0 synthetic public reference case stored under `tests/fixtures/historical/`. The profile also preserves the original v0.1.0 public-boundary scanner/policy behavior for historical evaluation.

This profile exists for explicit historical evaluation. It is not the default for new records.

## `m0-strict-0.2.0`

Default strengthened M0 profile for the Consumer & Contract Integrity release. It retains the strengthened semantic checks introduced after v0.1.0 and the bounded hardening accepted for this release.

## Behavioral immutability

Once released, a profile does not silently gain new ERROR-level requirements. New ERROR semantics or severity promotions require a new profile identifier.

## CLI

```bash
m2m validate case.json --public --profile m0-strict-0.2.0
m2m validate historical.json --public --profile m0-baseline-0.1.0
```

If `--profile` is omitted, the documented default is `m0-strict-0.2.0`. Machine-readable validation output states the actual profile and toolkit version used.

## Authority boundary

A validation profile governs automated structural and declared semantic findings. It does not authorize qualification, certification, compliance, acquisition, operational action, or the final human disposition.
