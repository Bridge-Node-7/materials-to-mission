# Repository Architecture

```text
materials-to-mission/
├── schemas/                 Public versioned JSON Schemas
├── templates/               Valid starter records
├── examples/                Synthetic reference and adversarial fixtures
├── src/materials_to_mission Python CLI, validation, rendering, and packaging
├── tests/                   Unit, integration, semantic, and release tests
├── policy/                  Public-boundary rules
├── scripts/                 Complete local gate and release construction
├── docs/                    Method, evidence, security, governance, and limits
├── .github/                 CI, CodeQL, release, issues, and dependency updates
└── GATES/                   Separated preflight, create, metadata, and release operators
```

## Trust Boundaries

- JSON Schema checks declared structure.
- Semantic validation checks cross-record rules.
- Public-boundary scanning identifies known prohibited patterns.
- Human review determines truth, applicability, and disposition.
- Release automation proves artifact identity and tested behavior.

## Runtime Boundary

Core commands operate locally and do not make network requests. Network access
is used only by package installation and GitHub-hosted release operations.
