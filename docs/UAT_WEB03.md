# WEB-03 Observed Browser UAT

**Result:** PASS  
**Primary browser:** edge 151.0.4129.72  
**Observed profiles:** 6  
**Golden Journey:** 7 / 7 stages  
**Public maturity:** M0  
**Deployment status:** not yet deployed

## Recovery Finding

WEB-03 found three bounded pre-release presentation/accessibility defects before production.
First, the controlled Examine accent `#8A6A3C` measured **4.388:1** against the Examine
field `#F4F0E7`, below the 4.5:1 acceptance threshold; the token and matching CSS variable
were corrected to `#825F31`, which measures **5.086:1**. Second,
server-side request/status tracing proved the browser's implicit `/favicon.ico` request was
the only HTTP 404; the document now declares the explicit no-network favicon `data:,`.
Third, fresh-focus diagnosis proved the skip link was the first keyboard target, while the
global reduced-motion rule unintentionally created an 80ms transform transition on that link,
leaving it offscreen at the instant focus arrived. The skip link now declares `transition:
none`, preserving immediate focus visibility while keeping the wider reduced-motion policy.
No schema, view-contract, GA-001, or semantic-authority change was required.

## Observed Profiles

- `edge_desktop_1440`
- `edge_mobile_390`
- `edge_narrow_320`
- `edge_reduced_motion`
- `edge_zoom_200_equivalent_720`
- `chrome_desktop_1440`

The matrix covers desktop, mobile, 320px narrow layout, reduced motion, and a 200% zoom-
equivalent 720 CSS-pixel reflow profile. When a second installed Chromium-family browser
is available, an additional desktop interoperability pass is included automatically.

## Golden Journey

Arrival → Materials Atlas → Gallium → Trace to Mission → Show Support → Examine →
Decision Room all render and remain interactable.

The observed runtime renders 10 trace nodes, 4 support items, 4 official-source records,
and 3 evidence-supported action options from frozen GA-001 data.

## Accessibility

PASS:

- skip-link is the first keyboard focus target;
- one main landmark and labeled navigation are present;
- heading order remains bounded;
- all buttons have text or accessible labels;
- reduced-motion preference is observed at no more than 80ms transition duration;
- 320px and 200% zoom-equivalent reflow do not create document-level horizontal overflow;
- controlled text/accent contrast pairs meet or exceed 4.5:1;
- human consequential authority is visible in the rendered experience.

## Privacy and Security

PASS:

- runtime requests are local GET requests only;
- no cookies are created;
- local storage and session storage remain empty;
- no service worker is registered;
- no analytics, telemetry, beacon, WebSocket, iframe, `eval`, or dynamic Function path is present;
- no browser write-back path is observed;
- no external runtime dependency is required by the product build.

## Performance

PASS:

- observed local navigation completes under the bounded 5-second UAT threshold;
- runtime resource count remains at or below four resources after the document;
- deterministic runtime build remains below 500 KB.

## Controlled Contrast

- Explore primary: 17.30:1
- Explore secondary: 9.49:1
- Explore accent: 8.46:1
- Examine primary: 14.38:1
- Examine secondary: 5.12:1
- Examine accent: 5.09:1

## Authority Boundary

Observed behavior preserves no readiness score, no automated approval or qualification,
visible unknown states, GA-001 as a public-source snapshot rather than a real operational
Case 001, Python semantic authority, and a derived read-only browser layer.

## Evidence

Machine-readable UAT results and full-page screenshots are sealed in the WEB-03 operator
evidence directory and are not committed to the public source repository.

## Next Gate

**DEP-00 production deployment and exact public provenance readback.**

WEB-03 does not create a release tag or website routing change.
