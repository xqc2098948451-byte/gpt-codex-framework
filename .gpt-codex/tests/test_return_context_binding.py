import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from result_return import render_gpt_return


class ReturnContextBindingTests(unittest.TestCase):
    def test_return_includes_source_identity_and_framework_version(self):
        rendered = render_gpt_return(
            {
                "return_to_gpt_required": True,
                "status": "PASS",
                "source_project_context_id": "11111111-1111-4111-8111-111111111111",
                "source_project_name": "Example Project",
                "framework_version": "2.1.0",
                "work_unit_id": "WORK-001",
                "state_revision": 3,
            }
        )
        self.assertIn("SOURCE_PROJECT_CONTEXT_ID: 11111111-1111-4111-8111-111111111111", rendered)
        self.assertIn("SOURCE_PROJECT_NAME: Example Project", rendered)
        self.assertIn("FRAMEWORK_VERSION: 2.1.0", rendered)

    def test_missing_identity_is_stable_none(self):
        rendered = render_gpt_return(
            {"return_to_gpt_required": True, "status": "BLOCKED"}
        )
        self.assertIn("SOURCE_PROJECT_CONTEXT_ID: NONE", rendered)
        self.assertIn("SOURCE_PROJECT_NAME: NONE", rendered)
        self.assertIn("FRAMEWORK_VERSION: NONE", rendered)
