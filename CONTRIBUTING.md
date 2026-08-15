# Contributing

Contributions should improve the public method, schemas, validation logic,
synthetic examples, documentation, accessibility, security, or release
integrity.

## Before Opening a Pull Request

1. Confirm that the change contains no protected or restricted information.
2. Add tests for expected and failure behavior.
3. Refresh evidence with `python scripts/check_repo.py --update-evidence` when tests or tracked behavior change.
4. Review the evidence diff, then run `python scripts/check_repo.py` and require a non-mutating PASS.
5. Update documentation and changelog when public behavior changes.
6. Explain evidence, compatibility, limitations, and public-boundary impact.

If a version-identity test reports installed metadata that differs from
`VERSION`, the editable installation is stale. Reinstall the current checkout
in the active environment (for example, `python -m pip install --no-build-isolation -e .`)
and rerun the gate; do not weaken the identity assertion.

Do not submit real supplier, customer, laboratory, sample, lot, price, capacity,
vulnerability, patent-sensitive, classified, controlled, or confidential data.
All consequential decisions remain human-owned.
