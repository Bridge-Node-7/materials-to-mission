# Versioning

Materials-to-Mission separates software release identity from canonical data-contract and semantic-validation identities.

## Five version axes

1. **Schema version** identifies the canonical structural record contract.
2. **Validation profile** identifies semantic rules and finding severities.
3. **Toolkit version** identifies the released Python implementation.
4. **View-contract version** identifies a derived public presentation contract.
5. **Application version** identifies a deployed browser experience.

These identities must not be silently conflated.

## Canonical schema authority

The existing `v0.1.0` schema identifiers remain immutable. Validation profiles do not add a required field to those schemas.

## Validation-profile compatibility

Released validation profiles are behavioral contracts with explicit compatibility corpora. A patch may repair an implementation defect only when the released profile's declared accept/reject behavior remains intact. A new ERROR-level semantic requirement, changed rejection criterion, or severity promotion to ERROR requires a new validation-profile identifier.

Historical records must be evaluated under an explicit compatible profile rather than silently reinterpreted under newer semantic rules.

Current profiles:

- `m0-baseline-0.1.0` — historical v0.1.0 semantic compatibility.
- `m0-strict-0.2.0` — strengthened M0 semantic validation.

The toolkit default is `m0-strict-0.2.0` and the applied profile is surfaced in machine-readable validation output and checked-in validation evidence.

## Toolkit releases

Toolkit releases follow Semantic Versioning within the experimental `0.x` line. During `0.x`, a minor release may introduce a new backward-compatible capability or an explicitly versioned compatibility mechanism.

Toolkit version advancement does not establish M1 or any real-world qualification, certification, compliance, production, or operational conclusion.
