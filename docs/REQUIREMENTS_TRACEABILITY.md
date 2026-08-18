# Requirements Traceability

| Requirement | Implementation | Validation |
|---|---|---|
| Human decision owner required | Decision Charter and Decision Passport schemas; semantic validator | `test_missing_human_owner_fails`, `test_automation_cannot_own_decision` |
| Critical conditions cannot be averaged away | MAR schema and semantic validator | `test_triggered_critical_condition_blocks_advance` |
| Unknown evidence remains visible | Evidence schema, Decision Passport posture, semantic validator | `test_unknown_evidence_must_be_visible` |
| Contradictory evidence remains visible | Evidence schema and synthetic reference | Public example validation and passport rendering |
| Exactly one governing weak link | MAR schema and semantic validator | `test_exactly_one_governing_weak_link`, `test_no_governing_weak_link_fails` |
| Authority remains consistent | Semantic validator | `test_owner_mismatch_fails` |
| Dispositions remain consistent | Semantic validator | `test_disposition_must_match` |
| Evidence provenance is complete | Case provenance and semantic validator | `test_provenance_must_match_evidence_ids` |
| Public examples are synthetic | Case schema, public validator, boundary scanner | `test_public_case_must_be_synthetic` |
| Protected tokens are rejected | Public-boundary policy and scanner | `test_public_boundary_rejects_protected_token` |
| Input is bounded | Safe JSON reader | `test_read_json_rejects_oversize`, `test_read_json_rejects_deep_input` |
| Decision Passport is deterministic | Markdown renderer | `test_report_is_deterministic` |
| Release archive is deterministic | Release builder | `test_deterministic_release` |
| Transient content is excluded | Release builder | `test_release_excludes_transient_directories` |
| Actions are immutable | Complete local gate | Full-SHA pin check |
| Public release is review-gated | GitHub workflows and release validation | Bash syntax and hosted CI after publication |

## v0.1.1 assurance-hardening traceability

The maintenance candidate adds semantic checks that the M0 schemas alone cannot express:

- consequential owners and disposition authorities may not be automation identities;
- MAR and Passport dispositions must be allowed by the Decision Charter;
- evidence and critical-condition visibility use exact leading identifiers;
- `PARTIALLY_SUPPORTED` evidence remains visible in the Passport `unknown` posture;
- requirement links resolve to Charter requirements or acceptance criteria;
- evidence issue dates may not be later than access dates;
- one evidence identifier may not occupy incompatible posture buckets;
- the Passport decision identifier equals the case identifier;
- secret-like structured keys are scanned in addition to serialized values;
- excessive JSON nesting returns a controlled operational error;
- ignored local-environment symlinks are distinguished from tracked or release-path symlinks.

These checks remain public-method validation. They do not establish material qualification,
compliance, source ownership, laboratory validity, production capacity, or mission authorization.

## v0.1.2 validation traceability

- Automation-only authority aliases are normalized and rejected; clearly named humans in
  AI, model-risk, and automation roles remain valid declarations.
- Decision Charter requirements and acceptance criteria share one unique identifier
  namespace.
- `VALIDATION_REPORT.md` derives its version from `VERSION`, which must agree with
  `pyproject.toml`.
- Direct renderer misuse returns a controlled toolkit exception; the CLI continues to
  validate before rendering.
- `scripts/evaluate_public_method.py` exercises the existing public CLI and confirms one
  intentional fail-closed fixture.
- These controls validate declarations and repository behavior. They do not authenticate a
  legal identity or establish qualification, compliance, production readiness, adoption,
  or operational authorization.
