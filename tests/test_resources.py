from pathlib import Path

from materials_to_mission.resources import policy_dir, schema_dir


def test_packaged_schemas_match_public_schemas(root):
    for public in sorted((root / "schemas").glob("*.json")):
        packaged = schema_dir() / public.name
        assert packaged.read_bytes() == public.read_bytes()


def test_packaged_policy_matches_public_policy(root):
    for public in sorted((root / "policy").glob("*.json")):
        packaged = policy_dir() / public.name
        assert packaged.read_bytes() == public.read_bytes()
