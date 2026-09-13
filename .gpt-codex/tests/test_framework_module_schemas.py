import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / ".gpt-codex" / "schemas"


MODULE_FIELDS = frozenset(
    {
        "MODULE_ID",
        "VERSION",
        "PURPOSE",
        "RESPONSIBILITIES",
        "NON_RESPONSIBILITIES",
        "OWNED_ASSETS",
        "ENTRY_POINTS",
        "INPUTS",
        "OUTPUTS",
        "DEPENDS_ON",
        "USED_BY",
        "INVARIANTS",
        "PERMISSIONS",
        "CHANGE_RISK",
        "REQUIRED_TESTS",
        "RELATED_MODULES",
    }
)


def load_schema(name: str) -> dict[str, object]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


class FrameworkModuleSchemaTests(unittest.TestCase):
    def test_registry_schema_freezes_authority_and_status(self):
        schema = load_schema("framework-module-registry.schema.json")
        self.assertEqual(schema["$id"], "gpt-codex/framework-module-registry-v1")
        self.assertEqual(schema["properties"]["schema_version"], {"const": 1})
        self.assertEqual(
            schema["properties"]["authority"],
            {"const": "FRAMEWORK_MODULE_REGISTRY"},
        )
        self.assertEqual(
            schema["properties"]["modules"]["items"]["properties"]["status"]["enum"],
            ["ACTIVE", "INACTIVE"],
        )

    def test_module_schema_has_exact_descriptor_fields(self):
        schema = load_schema("framework-module.schema.json")
        self.assertEqual(set(schema["required"]), MODULE_FIELDS)
        self.assertEqual(set(schema["properties"]), MODULE_FIELDS)
        self.assertTrue(schema["additionalProperties"] is False)

    def test_owned_asset_schema_is_exact_two_field_object(self):
        owned = load_schema("framework-module.schema.json")["properties"]["OWNED_ASSETS"]
        item = owned["items"]
        self.assertEqual(set(item["properties"]), {"type", "value"})
        self.assertEqual(item["required"], ["type", "value"])
        self.assertFalse(item["additionalProperties"])
        self.assertEqual(
            item["properties"]["type"]["enum"],
            ["EXACT_PATH", "PATH_PREFIX", "LOGICAL_ASSET"],
        )


if __name__ == "__main__":
    unittest.main()
