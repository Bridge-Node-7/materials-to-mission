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

## Hosted portfolio proof

CI downloads the exact public FMA `v0.5.0` wheel, verifies its published SHA-256 digest before installation, generates the M2M projection, and then runs:

```text
fma validate build/fma-projection/assurance-graph.json
fma decision \
  build/fma-projection/assurance-graph.json \
  build/fma-projection/decision-receipt.json
```

FMA `v0.5.0` is the current hosted interoperability baseline for this adapter. The adapter continues to target the stable Assurance Graph v1 and Decision Receipt v1 contracts; it does not manufacture a Research Receipt v3 unless an actual research execution exists.

That path proves that a real BN7 domain artifact can be projected into FMA contracts and consumed by the independently released FMA package.

## Assurance boundary

A successful adapter run proves deterministic transformation and contract compatibility for the declared synthetic case. It does **not** establish source credibility, material qualification, supplier approval, compliance, scientific truth, mission readiness, or decision authorization.

Public examples must remain synthetic and public-safe. Real program evidence belongs in an access-controlled environment appropriate to its classification and handling requirements.
