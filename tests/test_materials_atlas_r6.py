from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "public-snapshots/materials-field/MF-001"

def load(name: str) -> dict:
    return json.loads((FIELD / name).read_text(encoding="utf-8"))

def test_exact_public_field_and_review_scope() -> None:
    atlas = load("atlas.json")
    assert len(atlas["materials"]) == 60
    assert len({material["name"] for material in atlas["materials"]}) == 60
    assert sum(1 for material in atlas["materials"] if material["rare_earth"]) == 15
    reviewed = [material for material in atlas["materials"] if material["review"]["code"] == "reviewed-pathway"]
    assert [(material["name"], material["review"]["snapshot_id"]) for material in reviewed] == [("Gallium", "GA-001")]

def test_lenses_are_bn7_presentation_not_official_taxonomy() -> None:
    atlas = load("atlas.json")
    assert atlas["layout"]["authority"] == "BN7 presentation ontology"
    assert atlas["layout"]["source_id"] == "DOE-CMM-APPLICATIONS"
    assert len(atlas["lenses"]) == 6

def test_public_form_relationships_resolve() -> None:
    atlas = load("atlas.json")
    forms = load("public-forms.json")["forms"]
    names = {material["name"] for material in atlas["materials"]}
    assert all(rel["mineral"] in names for form in forms for rel in form["relationships"])
    assert len({form["id"] for form in forms}) == len(forms)

def test_layout_generator_is_shipped_and_reproducible() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_atlas_layout import coordinate_digest
    atlas = load("atlas.json")
    apps = load("doe-application-map.json")
    first = coordinate_digest(atlas, apps)
    second = coordinate_digest(atlas, apps)
    assert first == second
    assert len(first) == 64

def test_public_source_register_has_explicit_utc_verification() -> None:
    register = load("source-register.json")
    assert all(source["verified_at"].endswith("Z") and "T" in source["verified_at"] for source in register["sources"])
    assert all(source["url"].startswith("https://") for source in register["sources"])
