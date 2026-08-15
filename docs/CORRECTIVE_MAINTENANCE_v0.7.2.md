# v0.7.2 Corrective Maintenance Record

**Observation date:** 2026-08-14 local project context

## Closed findings

- **A-01 — PASS:** narrow-screen mineral and material-system details use native modal dialog semantics, native focus containment, Escape/explicit close behavior, and focus restoration.
- **A-02 — PASS:** the static dialog has `aria-label="Material detail"`; `aria-labelledby="sheetTitle"` is applied only after the unique title exists.
- **D-04 — PASS:** the orientation layer explains the controlled USGS 15-count convention and separately listed scandium without changing the dataset or primary stats.
- **P-05 — PASS:** contributor and assertion diagnostics direct operators to reinstall a stale editable checkout without weakening version identity.

## Informational disposition

- **U-03 — ACCEPTED / NO CHANGE:** dense Atlas nodes retain the documented 24px AA floor, and List view provides substantially larger rows. No empirical regression justified enlarging all 60 nodes.

## Hosting-layer observation

- **S-01 — VERIFIED HOSTING-LAYER LIMITATION / EXTERNAL GOVERNANCE DECISION REQUIRED.**
- Anonymous production response: `200 OK`; `Server: GitHub.com`; `Via: 1.1 varnish`.
- `Content-Security-Policy` response header: absent.
- `X-Frame-Options` response header: absent.
- The application retains a restrictive meta-delivered CSP, but `frame-ancestors` is ignored in meta CSP and therefore cannot remediate framing.
- The public M0 browser has no accounts, write-back, consequential approval action, authenticated privileged state, backend, database, or telemetry.
- DNS, proxy, CDN, or hosting architecture changes remain outside this maintenance gate and require separate authorization.

## Human-only assurance

Human physical-device mobile UAT and human assistive-technology UAT remain not separately attested.

## Dependency review

An ephemeral `pip-audit` 2.10.1 scan reviewed `requirements.lock`, `requirements-dev.lock`, and `requirements-browser.lock` on 2026-08-14. No high or critical finding was reported. Two development/build findings were inspected: `setuptools` 82.0.1 (`GHSA-h35f-9h28-mq5c`, medium, fixed in 83.0.0) and `pytest` 9.0.2 (`GHSA-6w46-j5rx-g56g`, medium, fixed in 9.0.3). Neither package is a browser runtime resource; the pytest finding concerns UNIX temporary-directory handling and remains relevant to the test supply chain. Dependency changes are outside this bounded maintenance candidate and should be handled as a separately reviewed lockfile update.

## External evidence URL sweep

Bounded anonymous GET requests followed redirects for all 15 controlled source records on 2026-08-14. Controlled URLs were not rewritten. Every final URL remained in its expected source domain family.

| Snapshot | Source ID | Status | Redirects | Content type / disposition |
| --- | --- | ---: | ---: | --- |
| MF-001 | USGS-CM-2025 | 403 | 0 | `text/html`; automated access denied, unresolved |
| MF-001 | DOE-CMM-APPLICATIONS | 200 | 0 | `text/html` |
| MF-001 | DOE-TRACE-GA-2026 | 200 | 0 | `text/html` |
| MF-001 | DFARS-252.225-7052 | 200 | 0 | `text/html` |
| MF-001 | GA-001 | 200 | 0 | `text/html` |
| MF-001 | USGS-Y-2026 | 200 | 0 | `application/pdf` |
| MF-001 | APS-YIG-LPE-2020 | 403 | 0 | `text/html`; automated access denied, unresolved |
| MF-001 | APS-YIG-RT-HYBRID-2024 | 403 | 0 | `text/html`; automated access denied, unresolved |
| MF-001 | NATURE-YIG-GGG-DEVICE-2025 | 200 | 3 | `text/html`; same-domain cookie-support redirect |
| MF-001 | NATURE-YIG-SUBSTRATE-2026 | 200 | 3 | `text/html`; same-domain cookie-support redirect |
| MF-001 | APS-YIG-MAGNON-JOSEPHSON-2021 | 403 | 0 | `text/html`; automated access denied, unresolved |
| GA-001 | USGS-GA-STATS | 403 | 0 | `text/html`; automated access denied, unresolved |
| GA-001 | USGS-CRITICAL-2025 | 403 | 0 | `text/html`; automated access denied, unresolved |
| GA-001 | DOE-TRACE-GA-2026 | 200 | 0 | `text/html` |
| GA-001 | DOE-TRACE-GA-2025 | 200 | 0 | `text/html` |

The six HTTP 403 responses are recorded as unresolved automated-access results, not evidence-content changes. The two Nature records completed same-domain redirects caused by cookie handling. No material domain-family change was observed.

## Performance smoke

The deterministic local build and complete Browser UAT reported no console or page errors and completed every navigation/interaction contract without timeout. Static HTML contains no third-party runtime script or stylesheet reference. Relative to the v0.7.1 source baseline, `web/index.html` increased from 15,381 to 15,551 bytes (+170), `web/app.js` increased from 30,661 to 31,411 bytes (+750), and `web/styles.css` remained 41,707 bytes. This bounded smoke found no pathological resource growth or material interaction regression; it is not a universal performance certification.
