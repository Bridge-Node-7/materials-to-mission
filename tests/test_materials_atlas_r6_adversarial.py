from __future__ import annotations
import importlib.util
import json
import shutil
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r6build", ROOT / "scripts/build_web.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def copy_field(tmp_path: Path) -> Path:
    target = tmp_path / "MF-001"
    shutil.copytree(MODULE.FIELD, target)
    return target

def test_rejects_unapproved_source_authority(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "source-register.json"
    data = json.loads(path.read_text())
    data["sources"][0]["authority_class"] = "uncontrolled"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()

def test_rejects_non_https_source(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "source-register.json"
    data = json.loads(path.read_text())
    data["sources"][0]["url"] = "http://www.usgs.gov/example"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()

def test_rejects_arbitrary_https_host(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "source-register.json"
    data = json.loads(path.read_text())
    data["sources"][0]["url"] = "https://example.com/"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()

def test_rejects_duplicate_material_id(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "atlas.json"
    data = json.loads(path.read_text())
    data["materials"][1]["id"] = data["materials"][0]["id"]
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()

def test_rejects_undefined_lens_row(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "atlas.json"
    data = json.loads(path.read_text())
    next(iter(data["lenses"].values()))["doe_rows"].append("not-a-row")
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()

def test_rejects_future_verification_timestamp(monkeypatch, tmp_path: Path) -> None:
    field = copy_field(tmp_path)
    path = field / "source-register.json"
    data = json.loads(path.read_text())
    data["sources"][0]["verified_at"] = "2099-01-01T00:00:00Z"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(MODULE, "FIELD", field)
    with pytest.raises(SystemExit):
        MODULE.project()
