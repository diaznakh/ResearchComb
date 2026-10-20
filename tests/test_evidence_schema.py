"""Validate fixture evidence.json files against the Draft 2020-12 schema."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "skills/researchcomb/references/evidence.schema.json"
FIXTURE_EVIDENCE = sorted(ROOT.glob("tests/fixtures/**/evidence.json"))
DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"


class SchemaError(ValueError):
    """A JSON Schema validation failure with a JSON Pointer path."""


def _is_type(instance, name):
    if name == "null":
        return instance is None
    if name == "boolean":
        return isinstance(instance, bool)
    if name == "object":
        return isinstance(instance, dict)
    if name == "array":
        return isinstance(instance, list)
    if name == "string":
        return isinstance(instance, str)
    if name == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if name == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    raise SchemaError(f"unsupported type name {name!r}")


def _resolve_ref(ref, root):
    if not ref.startswith("#/"):
        raise SchemaError(f"unsupported $ref {ref}")
    node = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolved $ref {ref}")
        node = node[part]
    return node


def _ok(instance, schema, root):
    try:
        validate(instance, schema, root)
    except SchemaError:
        return False
    return True


def validate(instance, schema, root=None, path="$"):
    """Validate instance against a subset of JSON Schema Draft 2020-12."""
    if schema is True:
        return
    if schema is False:
        raise SchemaError(f"{path}: boolean schema false")
    if not isinstance(schema, dict):
        raise SchemaError(f"{path}: schema must be an object or boolean")
    if root is None:
        root = schema
    if "$ref" in schema:
        validate(instance, _resolve_ref(schema["$ref"], root), root, path)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, name) for name in names):
            raise SchemaError(f"{path}: expected type {schema['type']!r}, got {type(instance).__name__}")
    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: {instance!r} is not in enum {schema['enum']!r}")
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            validate(instance, subschema, root, path)
    if "anyOf" in schema:
        if not any(_ok(instance, subschema, root) for subschema in schema["anyOf"]):
            raise SchemaError(f"{path}: anyOf matched no alternative")
    if "oneOf" in schema:
        matches = sum(_ok(instance, subschema, root) for subschema in schema["oneOf"])
        if matches != 1:
            raise SchemaError(f"{path}: oneOf matched {matches} alternatives")
    if "if" in schema:
        if _ok(instance, schema["if"], root):
            if "then" in schema:
                validate(instance, schema["then"], root, path)
        elif "else" in schema:
            validate(instance, schema["else"], root, path)
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                raise SchemaError(f"{path}: missing required property {key!r}")
        extras = set(instance)
        for key, subschema in schema.get("properties", {}).items():
            extras.discard(key)
            if key in instance:
                validate(instance[key], subschema, root, f"{path}/{key}")
        additional = schema.get("additionalProperties", True)
        if additional is False and extras:
            raise SchemaError(f"{path}: unexpected properties {sorted(extras)}")
        if isinstance(additional, (dict, bool)) and additional is not True:
            for key in extras:
                validate(instance[key], additional, root, f"{path}/{key}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaError(f"{path}: expected at least {schema['minItems']} items")
        if "items" in schema:
            for index, item in enumerate(instance):
                validate(item, schema["items"], root, f"{path}/{index}")
    if isinstance(instance, str) and "minLength" in schema and len(instance) < schema["minLength"]:
        raise SchemaError(f"{path}: string shorter than {schema['minLength']}")
    if _is_type(instance, "number") and "minimum" in schema and instance < schema["minimum"]:
        raise SchemaError(f"{path}: {instance} is below minimum {schema['minimum']}")


class EvidenceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text())

    def test_schema_declares_draft_2020_12(self):
        self.assertEqual(self.schema["$schema"], DRAFT_2020_12)
        self.assertEqual(self.schema["type"], "object")
        self.assertEqual(self.schema["required"], ["question", "sources", "claims"])

    def test_every_fixture_evidence_json_matches_schema(self):
        self.assertTrue(FIXTURE_EVIDENCE, "expected at least one tests/fixtures/**/evidence.json")
        for path in FIXTURE_EVIDENCE:
            with self.subTest(path=str(path.relative_to(ROOT))):
                record = json.loads(path.read_text())
                validate(record, self.schema)

    def test_check_results_fixture_shape_matches_schema(self):
        record = {
            "question": "Test a claim",
            "sources": [{
                "id": "S1", "title": "Fixture", "authors": [], "year": None,
                "url": "fixture.md", "doi": None, "access": "excerpt",
                "identity_status": "provided", "link_status": "not_checked",
            }],
            "claims": [{
                "id": "C1", "text": "Claim", "status": "supported",
                "evidence": [{"source_id": "S1", "location": "section 1", "observation": "Evidence"}],
                "note": "Checked against the supplied excerpt",
            }],
        }
        validate(record, self.schema)

    def test_schema_rejects_values_already_invalid_in_check_code(self):
        record = json.loads((ROOT / "tests/fixtures/workflows/evidence.json").read_text())
        record["sources"][0]["access"] = "snippet"
        with self.assertRaises(SchemaError):
            validate(record, self.schema)
        del record["question"]
        record["sources"][0]["access"] = "excerpt"
        with self.assertRaises(SchemaError):
            validate(record, self.schema)

    def test_assessed_claim_requires_evidence_item(self):
        record = {
            "question": "q",
            "sources": [{
                "id": "S1", "title": "T", "authors": None, "year": None,
                "url": None, "doi": None, "access": "metadata",
                "identity_status": "unverified", "link_status": "not_checked",
            }],
            "claims": [{
                "id": "C1", "text": "Claim", "status": "supported",
                "evidence": [], "note": "",
            }],
        }
        with self.assertRaises(SchemaError):
            validate(record, self.schema)
        record["claims"][0]["status"] = "unverified"
        validate(record, self.schema)

    def test_unavailable_search_needs_reason_and_fallback(self):
        record = {
            "question": "q",
            "sources": [],
            "claims": [],
            "searches": [{
                "source": "Crossref",
                "direct": {"outcome": "unavailable", "reason": "Host only offers web search"},
                "fallback": {"query": "example site:search.crossref.org", "outcome": "relevant results found"},
            }],
        }
        validate(record, self.schema)
        record["searches"][0]["direct"]["url"] = "https://search.crossref.org/"
        with self.assertRaises(SchemaError):
            validate(record, self.schema)
        record["searches"][0]["direct"] = {"outcome": "unavailable", "reason": "Host only offers web search"}
        del record["searches"][0]["fallback"]
        with self.assertRaises(SchemaError):
            validate(record, self.schema)


if __name__ == "__main__":
    unittest.main()
