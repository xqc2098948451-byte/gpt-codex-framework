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
            "PROJECT_MAP",
            "MODULE_MAP",
            "RESUME",
            "MAP_HIT",
            "MAP_PARTIAL",
            "MAP_MISS",
            "MAP_MISSING",
            "FAST_RESUME",
            "DELTA_RESUME",
            "COLD_RESUME",
            "Git delta",
        ):
            self.assertIn(hint, handoff)

        self.assertIn("DERIVED_NAVIGATION_INDEX", handoff)
        self.assertIn("DERIVED_CACHE", handoff)
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
