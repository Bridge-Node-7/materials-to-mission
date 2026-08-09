from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
errors: list[str] = []
for path in sorted(ROOT.rglob("*.md")):
    if any(part in {".git", ".venv", "dist", "build"} for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if clean and not (path.parent / clean).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)} -> {target}")
if errors:
    print("STOP - broken relative Markdown links")
    print("\n".join(errors))
    raise SystemExit(1)
print("PASS - Markdown relative links")
