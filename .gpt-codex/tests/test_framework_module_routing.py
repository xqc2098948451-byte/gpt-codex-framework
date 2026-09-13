import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".gpt-codex" / "framework-modules" / "REGISTRY.json"


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


INITIAL_MODULE_IDS = [
    "framework-core",
    "identity-context",
    "role-communication",
    "navigation-continuity",
    "git-continuity",
    "release-projection",
    "framework-validation",
]


class FrameworkModuleRoutingTests(unittest.TestCase):
    def test_registry_has_exact_initial_module_ids(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["authority"], "FRAMEWORK_MODULE_REGISTRY")
        self.assertEqual(
            [entry["module_id"] for entry in registry["modules"]],
            INITIAL_MODULE_IDS,
        )
        self.assertTrue(all(entry["status"] == "ACTIVE" for entry in registry["modules"]))

    def test_each_registered_descriptor_has_exact_identity_and_fields(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for entry in registry["modules"]:
            descriptor = json.loads((ROOT / entry["descriptor"]).read_text(encoding="utf-8"))
            self.assertEqual(descriptor["MODULE_ID"], entry["module_id"])
            self.assertEqual(set(descriptor), MODULE_FIELDS)


if __name__ == "__main__":
    unittest.main()
