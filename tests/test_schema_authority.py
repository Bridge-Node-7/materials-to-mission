import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'https://raw.githubusercontent.com/Bridge-Node-7/materials-to-mission/v0.1.0/schemas/'

def test_all_public_schemas_use_canonical_versioned_authority():
    for path in sorted((ROOT / "schemas").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["$id"] == PREFIX + path.name


def test_interface_manifest_pins_authority_semantics():
    interfaces = json.loads((ROOT / "INTERFACES.json").read_text(encoding="utf-8"))
    assert interfaces["format"] == "bn7.interfaces/0.1"
    assert interfaces["system"] == "materials-to-mission"
    assert interfaces["provides"][0]["authority"] == "PRODUCER_OWNED_PORTABLE_CONTRACT"
    assert all(
        item["authority"] == "PINNED_PORTABLE_VALIDATION_CONTRACT"
        for item in interfaces["accepts"]
    )
