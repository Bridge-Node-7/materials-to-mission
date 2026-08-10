# Validation Profiles

Validation profiles version semantic acceptance behavior independently from the immutable
v0.1.0 JSON Schema authority.

## `m0-baseline-0.1.0`

Historical compatibility profile for the semantic behavior shipped with the original
v0.1.0 public method. Its compatibility corpus begins with the exact v0.1.0 synthetic
public reference case stored under `tests/fixtures/historical/`. The profile also preserves
the original v0.1.0 public-boundary scanner/policy behavior for historical evaluation.

This profile exists for explicit historical evaluation. It is not the default for new
records.

## `m0-strict-0.2.0`

Released strengthened M0 profile for the Consumer & Contract Integrity line. Its released
accept/reject behavior remains available for explicit compatibility evaluation.

## `m0-strict-0.4.0`

Default M0 strict profile for v0.4.0. It preserves the `m0-strict-0.2.0` semantic rules and
adds explicit ERROR-level rejection for the additional automation-authority aliases
`Scoring Engine`, `Rules Engine`, and `Inference Service`.

## Behavioral immutability

Released validation profiles are behavioral contracts. A released profile does not silently
gain a new ERROR-level semantic requirement, changed rejection criterion, or severity
promotion. Those changes require a new validation-profile identifier.

## CLI

```bash
m2m validate case.json --public --profile m0-strict-0.4.0
m2m validate strict-compatibility.json --public --profile m0-strict-0.2.0
m2m validate historical.json --public --profile m0-baseline-0.1.0
```

If `--profile` is omitted, the documented default is `m0-strict-0.4.0`.
Machine-readable validation output states the actual profile and toolkit version used.

## Authority boundary

A validation profile governs automated structural and declared semantic findings. It does
not authorize qualification, certification, compliance, acquisition, operational action,
or the final human disposition.
