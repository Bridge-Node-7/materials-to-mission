from __future__ import annotations

import json
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from materials_to_mission.resources import schema_dir
from materials_to_mission.validator import validate_case


def registry_and_schema(name: str):
    schemas = [json.loads(path.read_text()) for path in sorted(schema_dir().glob("*.json"))]
    registry = Registry().with_resources((schema["$id"], Resource.from_contents(schema)) for schema in schemas)
    schema = next(item for item in schemas if item["$id"].endswith(f"/{name}"))
    return registry, schema


def test_case_template_is_valid(root):
    case = json.loads((root / "templates/case.template.json").read_text())
    assert validate_case(case, public=True).valid


def test_mar_template_is_schema_valid(root):
    record = json.loads((root / "templates/material-assurance-record.template.json").read_text())
    registry, schema = registry_and_schema("material-assurance-record.schema.json")
    errors = list(Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).iter_errors(record))
    assert errors == []


def test_charter_template_is_schema_valid(root):
    record = json.loads((root / "templates/decision-charter.template.json").read_text())
    registry, schema = registry_and_schema("decision-charter.schema.json")
    errors = list(Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).iter_errors(record))
    assert errors == []


def test_passport_template_is_schema_valid(root):
    record = json.loads((root / "templates/decision-passport.template.json").read_text())
    registry, schema = registry_and_schema("decision-passport.schema.json")
    errors = list(Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).iter_errors(record))
    assert errors == []
