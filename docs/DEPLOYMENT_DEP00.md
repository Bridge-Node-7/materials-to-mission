# DEP-00 Production Deployment

**Result:** PASS  
**Hosting:** GitHub Pages  
**Build type:** GitHub Actions workflow  
**Public URL:** https://bridgenode7.com/materials-to-mission/  
**Initial verified deployment commit:** `5fd0390c5060fdef5da55210170c8b738fb24aad`  
**Initial Pages run:** `31371350106`  
**HTTPS:** verified and enforced  
**Public maturity:** M0  
**Release at deployment:** `v0.2.0`

## Deployment Contract

Production is generated only by `python scripts/build_web.py`. The browser remains derived,
read-only, and non-authoritative. Python semantic validation remains authoritative.

Every third-party Action is pinned to an exact commit SHA. The deployment workflow runs the
complete repository validation gate, verifies an unchanged tracked worktree, builds the exact
deterministic five-file browser payload, verifies `WEB_MANIFEST.sha256`, and deploys through
the `github-pages` environment.

## Public Provenance Readback

DEP-00 verifies `index.html`, `styles.css`, `app.js`, `data/ga001.json`, and
`WEB_MANIFEST.sha256` byte-for-byte against a fresh deterministic build from the exact
accepted deployment commit. HTTPS is verified directly, then HTTP-to-HTTPS enforcement is
enabled and observed before closeout.

GA-001 remains `GA-001` version `1.0.0`; the public view contract remains `0.3.0`;
consequential decision authority remains human.

## Preserved Boundaries

DEP-00 does not change canonical v0.1.0 schema authority, validation-profile semantics,
M0 maturity, GA-001 meaning, or the human-decision boundary. It does not create a real
operational Case 001, introduce telemetry/backend write-back, create `v0.3.0`, or alter
BridgeNode7.com site-repository routing.
