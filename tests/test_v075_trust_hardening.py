from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v075_pages_permissions_are_least_privilege():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    head, deploy = workflow.split("  deploy:\n", 1)
    assert "pages: write" not in head
    assert "id-token: write" not in head
    deploy_block = deploy.split("  verify-production:\n", 1)[0]
    assert "pages: write" in deploy_block
    assert "id-token: write" in deploy_block
    verify_block = deploy.split("  verify-production:\n", 1)[1]
    assert "pages: write" not in verify_block
    assert "id-token: write" not in verify_block


def test_v075_public_policy_has_no_dead_synthetic_marker_field():
    policy = json.loads((ROOT / "policy/public-boundary-policy.json").read_text(encoding="utf-8"))
    assert "required_synthetic_markers" not in policy


def test_v075_unicode_confusables_are_version_pinned():
    data = json.loads((ROOT / "policy/unicode-confusables-17.0.0.json").read_text(encoding="utf-8"))
    assert data["unicode_version"] == "17.0.0"
    assert data["source"].endswith("/17.0.0/security/confusables.txt")
    assert len(data["source_sha256"]) == 64
    assert len(data["mapping"]) >= 5000


def test_v075_release_identity_is_singular_in_source():
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.7.5"
    facts = json.loads((ROOT / "PROJECT_FACTS.json").read_text(encoding="utf-8"))
    assert facts["version"] == facts["source_version"] == "0.7.5"
    assert facts["immediate_prior_immutable_release"]["tag"] == "v0.7.4"
    assert facts["maintenance_v075"]["public_product_behavior_changed"] is False

def test_v075_confusables_loader_rejects_wrong_version(tmp_path, monkeypatch):
    import json
    import pytest
    import materials_to_mission.boundary as boundary

    policy = tmp_path / "policy"
    policy.mkdir()
    (policy / "unicode-confusables-17.0.0.json").write_text(
        json.dumps({"unicode_version": "16.0.0", "mapping": {}}),
        encoding="utf-8",
    )

    boundary._confusable_mapping.cache_clear()
    monkeypatch.setattr(boundary, "policy_dir", lambda: policy)
    try:
        with pytest.raises(ValueError, match="unexpected Unicode confusables data version"):
            boundary._confusable_mapping()
    finally:
        boundary._confusable_mapping.cache_clear()


def test_v075_confusables_loader_rejects_non_mapping_payload(tmp_path, monkeypatch):
    import json
    import pytest
    import materials_to_mission.boundary as boundary

    policy = tmp_path / "policy"
    policy.mkdir()
    (policy / "unicode-confusables-17.0.0.json").write_text(
        json.dumps({"unicode_version": "17.0.0", "mapping": []}),
        encoding="utf-8",
    )

    boundary._confusable_mapping.cache_clear()
    monkeypatch.setattr(boundary, "policy_dir", lambda: policy)
    try:
        with pytest.raises(ValueError, match="invalid Unicode confusables mapping"):
            boundary._confusable_mapping()
    finally:
        boundary._confusable_mapping.cache_clear()
