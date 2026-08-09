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
| Public release is review-gated | GitHub workflows and operator gates | Bash syntax and hosted CI after publication |
