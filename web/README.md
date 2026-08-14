# Materials-to-Mission Public Experience

The public page is generated from controlled repository inputs.

Build locally:

```text
python scripts/build_web.py --output build/web-preview
python scripts/serve_preview.py --directory build/web-preview --port 8000
```

The generated Pages artifact remains exactly:

- `index.html`
- `styles.css`
- `app.js`
- `data/ga001.json`
- `WEB_MANIFEST.sha256`

The base HTML contains the semantic journey and Selected Pathways index before JavaScript. JavaScript progressively enhances the Atlas, search, Application Lenses, deep links, desktop/mobile detail, and view switching.

The browser is derived, read-only, and non-authoritative. It does not mutate canonical evidence or replace Python semantic validation.
