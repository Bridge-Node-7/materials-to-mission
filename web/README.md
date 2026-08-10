# Local browser preview

Do not open `web/index.html` directly from the source tree. The controlled browser payload
includes generated `data/ga001.json`, so preview the deterministic build:

```bash
python scripts/build_web.py --output build/web-preview
python -m http.server 8000 --directory build/web-preview
```

Then open `http://127.0.0.1:8000/`.

The browser remains derived, read-only, and non-authoritative. Python semantic validation
remains authoritative. No fallback source-data path is used.
