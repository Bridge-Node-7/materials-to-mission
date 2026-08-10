from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
WEB_SOURCE = ROOT / "web"
GA001 = ROOT / "public-snapshots" / "gallium" / "GA-001"

STATIC_FILES = ("index.html", "styles.css", "app.js")


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def build(output: Path) -> Path:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for name in STATIC_FILES:
        source = WEB_SOURCE / name
        target = output / name
        target.write_bytes(source.read_bytes())

    view = json.loads((GA001 / "public-view.json").read_text(encoding="utf-8"))
    snapshot = json.loads((GA001 / "snapshot.json").read_text(encoding="utf-8"))
    sources = json.loads((GA001 / "source-register.json").read_text(encoding="utf-8"))
    rights = json.loads((GA001 / "rights.json").read_text(encoding="utf-8"))

    if snapshot["snapshot_id"] != "GA-001":
        raise SystemExit("STOP - unexpected Gallium snapshot identity")
    if view["source_kind"] != "public-source-snapshot":
        raise SystemExit("STOP - public view is not bound to a public-source snapshot")
    if view["decision_authority"] != "human":
        raise SystemExit("STOP - public view decision authority must remain human")
    if rights["rights_posture"] != "metadata-and-original-paraphrase-only":
        raise SystemExit("STOP - GA-001 rights posture changed")

    payload = {
        "view": view,
        "snapshot": snapshot,
        "sources": sources,
        "rights": {
            "rights_posture": rights["rights_posture"],
            "source_files_redistributed": rights["source_files_redistributed"],
            "source_images_redistributed": rights["source_images_redistributed"],
            "long_source_quotes_redistributed": rights["long_source_quotes_redistributed"],
        },
    }
    _write_utf8_lf(
        output / "data" / "ga001.json",
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
    )

    rows = []
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        rel = path.relative_to(output).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {rel}")
    _write_utf8_lf(output / "WEB_MANIFEST.sha256", "\n".join(rows) + "\n")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "build" / "web",
    )
    args = parser.parse_args()
    result = build(args.output.resolve())
    print(f"PASS - deterministic public web build: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
