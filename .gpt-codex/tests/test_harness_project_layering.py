import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_project import validate_harness_root_separation  # noqa: E402


class HarnessProjectLayeringTests(unittest.TestCase):
    def test_default_semantic_roots_are_disjoint(self):
        control = json.loads(
            (ROOT / ".gpt-codex/project-template/CONTROL.template.json").read_text(encoding="utf-8")
        )
        self.assertEqual(control["roots"]["harness_root"], ".harness")
        self.assertEqual(control["roots"]["product_roots"], ["app"])
        self.assertEqual(control["roots"]["deploy_roots"], ["ops"])
        self.assertIn(".harness", control["roots"]["production_excludes"])
        self.assertEqual(validate_harness_root_separation(control), [])

    def test_harness_cannot_be_product_or_deploy_root(self):
        control = {
            "roots": {
                "harness_root": ".harness",
                "product_roots": [".harness"],
                "deploy_roots": ["ops"],
                "production_excludes": [".harness"],
            }
        }
        self.assertEqual(
            validate_harness_root_separation(control),
            ["HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP"],
        )

    def test_harness_must_be_excluded_from_production(self):
        control = {
            "roots": {
                "harness_root": ".harness",
                "product_roots": ["app"],
                "deploy_roots": ["ops"],
                "production_excludes": [],
            }
        }
        self.assertEqual(
            validate_harness_root_separation(control),
            ["HARNESS_PRODUCTION_EXCLUSION_REQUIRED"],
        )

    def test_minimal_harness_templates_exist(self):
        harness = ROOT / ".gpt-codex/project-template/.harness"
        self.assertEqual(
            {path.name for path in harness.glob("*.template.md")},
            {
                "RULES.template.md",
                "STATE.template.md",
                "REASONING.template.md",
                "FEEDBACK.template.md",
            },
        )


if __name__ == "__main__":
    unittest.main()
