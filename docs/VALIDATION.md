# Validation

## Local Gate

```bash
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/check_repo.py
```

The default gate is non-mutating. It fails if `VALIDATION_REPORT.md` or
`REPO_FILE_MANIFEST.sha256` is stale.

After a reviewed source or test change, refresh the checked-in evidence once:

```bash
python scripts/check_repo.py --update-evidence
git diff -- VALIDATION_REPORT.md REPO_FILE_MANIFEST.sha256
python scripts/check_repo.py
```

Commit the refreshed evidence only after reviewing the diff.

The gate performs:

- Python compilation
- Schema synchronization
- JSON parsing and JSON Schema validation
- Semantic validation
- Public-boundary scanning
- Adversarial fixture checks
- Unit and integration tests
- Coverage threshold
- Markdown-link checks
- Source/release gate-contract checks
- Checked-in evidence verification
- Cross-platform deterministic release build
- Included-path symbolic-link rejection
- Package-output location validation
- SHA-256 manifest verification
- Clean-tree enforcement in hosted workflows

A passing gate proves only the behaviors tested. It does not prove real-world
material, supplier, laboratory, mission, legal, or commercial conclusions.
