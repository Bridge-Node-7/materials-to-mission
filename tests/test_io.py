from __future__ import annotations

import json

import pytest

from materials_to_mission import io
from materials_to_mission.errors import InputFileError


def test_read_json_rejects_non_object(tmp_path):
    path = tmp_path / "array.json"
    path.write_text("[]")
    with pytest.raises(InputFileError):
        io.read_json(path)


def test_read_json_rejects_malformed(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{")
    with pytest.raises(InputFileError):
        io.read_json(path)


def test_read_json_rejects_oversize(tmp_path, monkeypatch):
    path = tmp_path / "big.json"
    path.write_text('{"value": "long"}')
    monkeypatch.setattr(io, "MAX_INPUT_BYTES", 1)
    with pytest.raises(InputFileError):
        io.read_json(path)


def test_read_json_rejects_deep_input(tmp_path):
    value = current = {}
    for i in range(io.MAX_NESTING_DEPTH + 2):
        current["next"] = {}
        current = current["next"]
    path = tmp_path / "deep.json"
    path.write_text(json.dumps(value))
    with pytest.raises(InputFileError):
        io.read_json(path)


def test_write_text_creates_parent(tmp_path):
    target = tmp_path / "a" / "b.txt"
    io.write_text(target, "hello\n")
    assert target.read_text() == "hello\n"
