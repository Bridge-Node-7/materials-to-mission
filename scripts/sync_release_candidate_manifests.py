"""Align VERSION/PROJECT_FACTS, strip pre-tag CHANGELOG compare URLs, refresh file manifest."""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
COMPARE_HEADING_RE = re.compile(
    r"(^## \[\d+\.\d+\.\d+\])\(https://github\.com/[^\s)]+/compare/[^\s)]+\)( \(\d{4}-\d{2}-\d{2}\))",
    re.MULTILINE,
)
def main() -> int:
    root = Path(".").resolve()
    version = str(json.loads((root / ".release-please-manifest.json").read_text(encoding="utf-8")).get(".", "")).strip()
    if not VERSION_RE.fullmatch(version):
        print(f"FAIL: invalid manifest version {version!r}", file=sys.stderr); return 1
    vp = root / "VERSION"
    if vp.read_text(encoding="utf-8").strip() != version:
        vp.write_text(version + "\n", encoding="utf-8", newline="\n")
        print(f"PASS: aligned VERSION to {version}")
    else:
        print(f"PASS: VERSION already {version}")
    pf = root / "PROJECT_FACTS.json"
    if pf.exists():
        data = json.loads(pf.read_text(encoding="utf-8"))
        changed = False
        for k in ("version", "source_version"):
            if k in data and data[k] != version:
                data[k] = version; changed = True
        if "release_artifact" in data:
            na = re.sub(r"v\d+\.\d+\.\d+", f"v{version}", str(data["release_artifact"]))
            if na != data["release_artifact"]:
                data["release_artifact"] = na; changed = True
        if changed:
            pf.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
            print("PASS: aligned PROJECT_FACTS.json")
    cl = root / "CHANGELOG.md"
    text = cl.read_text(encoding="utf-8")
    rewritten, n = COMPARE_HEADING_RE.subn(r"\1\2", text, count=1)
    if n:
        cl.write_text(rewritten, encoding="utf-8", newline="\n")
        print("PASS: stripped pre-tag CHANGELOG compare URL")
    else:
        print("PASS: CHANGELOG compare heading already plain or absent")
    state = root / "docs/CURRENT_STATE.md"
    if state.is_file():
        text = state.read_text(encoding="utf-8")
        updated = re.sub(
            r"Current source version: \*\*\d+\.\d+\.\d+\*\*",
            f"Current source version: **{version}**",
            text,
            count=1,
        )
        updated = re.sub(
            r"`VERSION` identifies source line `\d+\.\d+\.\d+`",
            f"`VERSION` identifies source line `{version}`",
            updated,
            count=1,
        )
        if updated != text:
            state.write_text(updated, encoding="utf-8", newline="\n")
            print(f"PASS: aligned docs/CURRENT_STATE.md to {version}")
        else:
            print(f"PASS: docs/CURRENT_STATE.md already {version}")

    r = subprocess.run([sys.executable, "scripts/sync_resources.py"], cwd=root)
    if r.returncode != 0: return r.returncode
    r = subprocess.run([sys.executable, "scripts/build_manifest.py"], cwd=root)
    if r.returncode != 0: return r.returncode
    print("PASS: refreshed resources and file manifest")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
