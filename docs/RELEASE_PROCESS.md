# Release Process

## Public Source Repository

The public source contains only local maintainer controls:

1. Validate the canonical source in an isolated environment while preserving logs.
2. Verify that exact Git identity and GitHub write gates remain outside the public source.
3. Validate a separately generated publication kit through `scripts/check_publication_kit.py`.

The public repository does not contain executable GitHub write gates.

## Publication Kit

A separately generated and reviewed publication kit contains the exact source archive,
prebuilt reviewed commit, Git tree, complete Git bundle, checksums, V&V evidence, and six
separately authorized gates:

1. Read-only personal-account preflight
2. Create the public repository and push exact `main`
3. Read back hosted CI and CodeQL by exact workflow identity
4. Configure metadata, security, immutable releases, and future branch protection
5. Push one verified signed `v0.1.0` tag
6. Verify hosted release, exact assets, attestations, checksums, archive-to-tree equality,
   canonical schema URLs, and signed-out public access

The hosted `Release` workflow is the sole GitHub Release creator.

## Evidence Update

When intentional source changes affect checked-in validation evidence:

```bash
python scripts/check_repo.py --update-evidence
git diff -- VALIDATION_REPORT.md REPO_FILE_MANIFEST.sha256 src/materials_to_mission/resources/
python scripts/check_repo.py
```

Review every changed evidence file before committing.

## Recovery Rule

If repository creation succeeds but push fails, do not delete the repository and do not
rerun blindly. Preserve the evidence directory, inspect the remote state, and resume only
through a reviewed recovery gate.
