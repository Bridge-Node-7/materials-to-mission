# Maintainers Only

These local gates validate the canonical source and verify the separation between the
public repository and the separately generated publication kit. They perform no GitHub
read or write.

- `00_VALIDATE_CANONICAL_SOURCE.sh` creates an isolated environment, preserves logs, and
  runs the complete non-mutating repository gate.
- `01_VERIFY_PUBLICATION_KIT_BOUNDARY.sh` verifies that public-write gates, exact Git
  identity, and operator credentials are not bundled into the public source.

Public users do not need this directory to validate cases or render Decision Passports.
Public-write gates exist only in a separately reviewed publication kit.
