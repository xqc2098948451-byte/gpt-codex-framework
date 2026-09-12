import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HandoffNavigationContractTests(unittest.TestCase):
    def test_handoff_preserves_derived_navigation_and_resume_boundaries(self):
        handoff = (ROOT / "builtins" / "skills" / "handoff" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        manifest = json.loads(
            (ROOT / "builtins" / "skills" / "handoff" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )

        for hint in (
            "MAP_ROUTE",
            "MAP_MODULES",
            "MAP_STALE_MODULES",
            "MAP_MISSING",
            "RESUME_MODE",
            "RESUME_CHECKPOINT_REVISION",
            "RESUME_ANCHOR_SHA",
            "HOT_MODULES",
            "HOT_FILES",
            "CONTEXT_INVALIDATED",
            "NEXT_REQUIRED_READS",
        ):
            self.assertIn(hint, handoff)

        self.assertIn("derived routing context only", handoff)
        self.assertIn("must not override", handoff)
        for authority in (
            "CONTROL",
            "STATE",
            "Work Unit",
            "Result",
            "Evidence",
            "source/tests",
            "Git/GitHub",
        ):
            self.assertIn(authority, handoff)

        self.assertEqual(manifest["kernel_version"], "2.0.0")
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["version"], "1.2.0")
        self.assertEqual(manifest["permissions"], {
            "project_read": "ALLOW",
            "project_write": "DENY",
        })


if __name__ == "__main__":
    unittest.main()
