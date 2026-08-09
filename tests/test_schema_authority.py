import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'https://raw.githubusercontent.com/Bridge-Node-7/materials-to-mission/v0.1.0/schemas/'

def test_all_public_schemas_use_canonical_versioned_authority():
    for path in sorted((ROOT / "schemas").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["$id"] == PREFIX + path.name
