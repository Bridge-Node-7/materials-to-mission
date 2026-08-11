# Materials-to-Mission Public Experience

The public page is generated from controlled repository inputs.

Build locally:

```text
python scripts/build_web.py --output build/web-preview
python -m http.server 8000 --directory build/web-preview
```

The generated Pages artifact remains exactly:

- `index.html`
- `styles.css`
- `app.js`
- `data/ga001.json`
- `WEB_MANIFEST.sha256`

The base HTML contains the semantic journey before JavaScript. JavaScript progressively enhances the Strategic Constellation, search, Application Lenses, deep links, desktop/mobile detail, and view switching.

The browser is derived, read-only, and non-authoritative. It does not mutate canonical evidence or replace Python semantic validation.
