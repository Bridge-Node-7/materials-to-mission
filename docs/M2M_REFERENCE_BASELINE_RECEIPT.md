# Materials-to-Mission Reference Baseline Receipt

Generated:
Thu Aug 20 08:42:36 UTC 2026

## Repository

Path:
/c/Users/Lucky777/Documents/GitHub/materials-to-mission

Branch:
m2m/reference-baseline-completion

Commit:
f141a85cee9615a57582855e677450af7584cfd4

Remote:
https://github.com/Bridge-Node-7/materials-to-mission.git

## Version

0.7.4

## Repository Structure

```
.
./.editorconfig
./.git
./.gitattributes
./.github
./.github/CODEOWNERS
./.github/ISSUE_TEMPLATE
./.github/dependabot.yml
./.github/pull_request_template.md
./.github/workflows
./.gitignore
./.python-version
./CHANGELOG.md
./CITATION.cff
./CODE_OF_CONDUCT.md
./CONTRIBUTING.md
./LICENSE
./Makefile
./NOTICE
./PROJECT_FACTS.json
./README.md
./RELEASE_NOTES.md
./REPO_FILE_MANIFEST.sha256
./SCHEMA_CATALOG.json
./SECURITY.md
./VALIDATION_REPORT.md
./VERSION
./VERSIONING.md
./docs
./docs/AI_PROVENANCE.md
./docs/CURRENT_STATE.md
./docs/DECISION_CHARTER.md
./docs/DECISION_PASSPORT.md
./docs/ENGINEERED_MATERIAL_SYSTEMS_CONTRACT.md
./docs/EVIDENCE_MODEL.md
./docs/FIVE_MINUTE_EVALUATION.md
./docs/INTEROPERABILITY.md
./docs/M2M_REFERENCE_BASELINE_RECEIPT.md
./docs/MAINTENANCE.md
./docs/MATERIAL_ASSURANCE_RECORD.md
./docs/MATURITY_AND_PROOF.md
./docs/METHOD.md
./docs/PUBLIC_BOUNDARY.md
./docs/QUALIFICATION_AND_READINESS_STATES.md
./docs/REQUIREMENTS_TRACEABILITY.md
./docs/SCOPE_COVERAGE.md
./docs/SECURITY_MODEL.md
./docs/START_HERE.md
./docs/THREAT_MODEL.md
./docs/V0_3_DESIGN_TOKENS.json
./docs/VALIDATION.md
./docs/VALIDATION_PROFILES.md
./examples
./examples/invalid
./examples/synthetic-critical-material-pathway
./policy
./policy/public-boundary-policy.json
./public-snapshots
./public-snapshots/gallium
./public-snapshots/material-systems
./public-snapshots/materials-field
./pyproject.toml
./requirements-browser.lock
./requirements-dev.txt
./requirements.txt
./schemas
./schemas/case.schema.json
./schemas/common.schema.json
./schemas/decision-charter.schema.json
./schemas/decision-passport.schema.json
./schemas/evidence-record.schema.json
./schemas/material-assurance-record.schema.json
./scripts
./scripts/browser_uat.py
./scripts/build_manifest.py
./scripts/build_release.py
./scripts/build_web.py
./scripts/check_gate_contracts.py
./scripts/check_links.py
./scripts/check_repo.py
./scripts/evaluate_public_method.py
./scripts/generate_atlas_layout.py
./scripts/serve_preview.py
./scripts/sync_resources.py
./scripts/verify_production.py
./src
./src/materials_to_mission
./templates
./templates/README.md
./templates/case.template.json
./templates/decision-charter.template.json
./templates/decision-passport.template.json
./templates/material-assurance-record.template.json
./tests
./tests/conftest.py
./tests/fixtures
./tests/test_assurance_hardening.py
./tests/test_boundary.py
./tests/test_cli.py
./tests/test_cli_more.py
./tests/test_consumer_integrity_v020.py
./tests/test_evaluate_public_method.py
./tests/test_foundation_hardening.py
./tests/test_ga001_public_snapshot.py
./tests/test_gate_contracts.py
./tests/test_io.py
./tests/test_materials_atlas_r6.py
./tests/test_materials_atlas_r6_adversarial.py
./tests/test_profile_compatibility_v040.py
./tests/test_public_surface.py
./tests/test_public_visual_contract.py
./tests/test_r6_2_visual_contract.py
./tests/test_r6_3_1_final_precision.py
./tests/test_r6_3_2_semantic_parity.py
./tests/test_r6_3_3_release_reproducibility.py
./tests/test_r6_3_yig_foundation.py
./tests/test_release.py
./tests/test_release_hardening.py
./tests/test_report.py
./tests/test_repository_truth.py
./tests/test_resources.py
./tests/test_schema_authority.py
./tests/test_semantic_more.py
./tests/test_templates.py
./tests/test_uxf_v031.py
./tests/test_v060_ux_contract.py
./tests/test_v061_truth_accessibility.py
./tests/test_v070_selected_pathways_release.py
./tests/test_v072_corrective_maintenance.py
./tests/test_v073_clarity_orientation.py
./tests/test_validation.py
./tests/test_validation_evidence.py
./tests/test_web_golden_journey.py
./view-contracts
./view-contracts/public-view.schema.json
./web
./web/README.md
./web/app.js
./web/index.html
./web/selected-pathways.json
./web/selected-pathways.schema.json
./web/styles.css
```

## Validation Files

./.git/hooks/push-to-checkout.sample
./.github/workflows/browser-uat.yml
./docs/FIVE_MINUTE_EVALUATION.md
./scripts/browser_uat.py
./scripts/check_gate_contracts.py
./scripts/check_links.py
./scripts/check_repo.py
./scripts/evaluate_public_method.py
./tests/conftest.py
./tests/test_assurance_hardening.py
./tests/test_boundary.py
./tests/test_cli.py
./tests/test_cli_more.py
./tests/test_consumer_integrity_v020.py
./tests/test_evaluate_public_method.py
./tests/test_foundation_hardening.py
./tests/test_ga001_public_snapshot.py
./tests/test_gate_contracts.py
./tests/test_io.py
./tests/test_materials_atlas_r6.py
./tests/test_materials_atlas_r6_adversarial.py
./tests/test_profile_compatibility_v040.py
./tests/test_public_surface.py
./tests/test_public_visual_contract.py
./tests/test_r6_2_visual_contract.py
./tests/test_r6_3_1_final_precision.py
./tests/test_r6_3_2_semantic_parity.py
./tests/test_r6_3_3_release_reproducibility.py
./tests/test_r6_3_yig_foundation.py
./tests/test_release.py
./tests/test_release_hardening.py
./tests/test_report.py
./tests/test_repository_truth.py
./tests/test_resources.py
./tests/test_schema_authority.py
./tests/test_semantic_more.py
./tests/test_templates.py
./tests/test_uxf_v031.py
./tests/test_v060_ux_contract.py
./tests/test_v061_truth_accessibility.py
./tests/test_v070_selected_pathways_release.py
./tests/test_v072_corrective_maintenance.py
./tests/test_v073_clarity_orientation.py
./tests/test_validation.py
./tests/test_validation_evidence.py
./tests/test_web_golden_journey.py

## Python Files

./scripts/browser_uat.py
./scripts/build_manifest.py
./scripts/build_release.py
./scripts/build_web.py
./scripts/check_gate_contracts.py
./scripts/check_links.py
./scripts/check_repo.py
./scripts/evaluate_public_method.py
./scripts/generate_atlas_layout.py
./scripts/serve_preview.py
./scripts/sync_resources.py
./scripts/verify_production.py
./src/materials_to_mission/__init__.py
./src/materials_to_mission/__main__.py
./src/materials_to_mission/boundary.py
./src/materials_to_mission/cli.py
./src/materials_to_mission/errors.py
./src/materials_to_mission/io.py
./src/materials_to_mission/release.py
./src/materials_to_mission/report.py
./src/materials_to_mission/resources.py
./src/materials_to_mission/validation_evidence.py
./src/materials_to_mission/validation_profiles.py
./src/materials_to_mission/validator.py
./tests/conftest.py
./tests/test_assurance_hardening.py
./tests/test_boundary.py
./tests/test_cli.py
./tests/test_cli_more.py
./tests/test_consumer_integrity_v020.py
./tests/test_evaluate_public_method.py
./tests/test_foundation_hardening.py
./tests/test_ga001_public_snapshot.py
./tests/test_gate_contracts.py
./tests/test_io.py
./tests/test_materials_atlas_r6.py
./tests/test_materials_atlas_r6_adversarial.py
./tests/test_profile_compatibility_v040.py
./tests/test_public_surface.py
./tests/test_public_visual_contract.py
./tests/test_r6_2_visual_contract.py
./tests/test_r6_3_1_final_precision.py
./tests/test_r6_3_2_semantic_parity.py
./tests/test_r6_3_3_release_reproducibility.py
./tests/test_r6_3_yig_foundation.py
./tests/test_release.py
./tests/test_release_hardening.py
./tests/test_report.py
./tests/test_repository_truth.py
./tests/test_resources.py
./tests/test_schema_authority.py
./tests/test_semantic_more.py
./tests/test_templates.py
./tests/test_uxf_v031.py
./tests/test_v060_ux_contract.py
./tests/test_v061_truth_accessibility.py
./tests/test_v070_selected_pathways_release.py
./tests/test_v072_corrective_maintenance.py
./tests/test_v073_clarity_orientation.py
./tests/test_validation.py
./tests/test_validation_evidence.py
./tests/test_web_golden_journey.py

## Example Directories

./examples

## Baseline Rules

Historical validation remains immutable.

Future changes preserve:

- evidence traceability
- provenance
- lineage
- reproducibility
- human decision authority
- public/private boundaries

