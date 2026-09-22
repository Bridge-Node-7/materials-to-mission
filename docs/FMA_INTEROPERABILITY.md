# Frontier Mission Assurance interoperability

Materials-to-Mission owns the full materials/source/process/requirement/evidence/decision semantics of an M2M case. Frontier Mission Assurance (FMA) is a thinner portable assurance layer. This integration deliberately connects the two without forcing them into one ontology.

## Contract

The deterministic adapter is:

```text
python scripts/export_fma_projection.py \
  examples/synthetic-critical-material-pathway/case.json \
  --output-dir build/fma-projection
```

It emits:

- `assurance-graph.json` — an FMA Assurance Graph v1 projection;
- `decision-receipt.json` — an FMA Decision Receipt v1 projected from the M2M proposed disposition;
- `projection-manifest.json` — source digest, adapter identity, target schema identifiers, preserved semantics, non-claims, and output digests.

The source M2M case remains authoritative.

## Why the projection is deliberately loss-aware

A portable contract should not erase useful domain intelligence. M2M evidence records therefore retain the following richer source fields inside each projected FMA evidence node's `m2m_projection` extension:

- `basis`
- `claim_state`
- `confidence`
- `applicability`
- `requirement_links`
- `claim_links`
- `contradictory_evidence`
- `limitations`
- `classification`
- `ai_involvement`
- `human_reviewer`

The projection manifest explicitly declares `projection_is_lossy: true`. Consumers that need full M2M meaning must use the source case bound by SHA-256 rather than reconstructing M2M from the FMA projection.

## Stable FMA contract identities

The adapter targets the public FMA contracts:

- `https://bridge-node-7.github.io/frontier-mission-assurance/assurance-graph.schema.json`
- `https://bridge-node-7.github.io/frontier-mission-assurance/decision-receipt.schema.json`

The manifest also records the Research Receipt identifier for ecosystem discoverability, but this adapter does not manufacture a research execution receipt when no experiment was executed.

## Contract-first native proof

M2M native CI validates the projection locally against exact pinned copies of the producer-owned FMA Assurance Graph v1 and Decision Receipt v1 schemas. `INTERFACES.json` records their stable identifiers and raw SHA-256 values independently from any FMA application version.

The projection exporter fails closed if a pinned schema digest or identifier changes, validates both projected artifacts under the exact portable contracts, and records the contract digests in `projection-manifest.json`.

This proves deterministic transformation and portable-contract conformance without downloading or repinning an FMA application merely because its release number changed.

Current-product M2M → FMA interoperability is a separate estate-level conformance question. It should be recorded in a BN7 compatibility receipt for the exact tested implementation commits/releases rather than making ordinary M2M CI depend on a historical FMA wheel.

The adapter does not manufacture a Research Receipt v3 unless an actual research execution exists.

## Assurance boundary

A successful adapter run proves deterministic transformation and contract compatibility for the declared synthetic case. It does **not** establish source credibility, material qualification, supplier approval, compliance, scientific truth, mission readiness, or decision authorization.

Public examples must remain synthetic and public-safe. Real program evidence belongs in an access-controlled environment appropriate to its classification and handling requirements.
