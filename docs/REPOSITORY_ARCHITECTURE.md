# Repository Architecture

```text
materials-to-mission/
├── schemas/                 Immutable canonical public JSON Schema authority
├── view-contracts/          Derived, versioned, non-authoritative presentation contracts
├── templates/               Valid starter records
├── examples/                Synthetic reference and adversarial fixtures
├── src/materials_to_mission Python CLI, validation, rendering, and packaging
├── tests/                   Unit, integration, semantic, release, and view-contract tests
├── policy/                  Public-boundary rules
├── scripts/                 Complete local gate and release construction
├── docs/                    Method, evidence, security, governance, UX, and limits
├── .github/                 CI, CodeQL, release, issues, and dependency updates
└── GATES/                   Separated preflight, create, metadata, and release operators
```

## Trust Boundaries

- JSON Schema checks declared canonical record structure.
- Semantic validation checks cross-record rules.
- Validation profiles version semantic behavior without rewriting historical schema
  authority.
- Public-boundary scanning identifies known prohibited patterns.
- Human review determines truth, applicability, and consequential disposition.
- View contracts control derived presentation structure only.
- Release automation proves artifact identity and tested behavior.

## Presentation Boundary

The v0.3 public visual layer is derived, read-only, and non-authoritative. It may consume
validated records, synthetic examples, and separately controlled public-source snapshots.
It must not mutate canonical records or become a second semantic engine.

## Runtime Boundary

Core commands operate locally and do not make network requests. Network access is used
only by package installation and GitHub-hosted release operations. The initial public
browser experience must not require accounts, telemetry, a hosted backend, or remote
persistence.
