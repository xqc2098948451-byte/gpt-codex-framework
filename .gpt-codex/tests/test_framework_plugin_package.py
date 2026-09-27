import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "plugins/gpt-codex-framework"


class FrameworkPluginPackageTests(unittest.TestCase):
    def test_portable_manifest_is_skills_only(self):
        manifest = json.loads((PACKAGE / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "gpt-codex-framework")
        self.assertIn("version", manifest)
        self.assertIn("description", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("capabilities", manifest)
        self.assertFalse((PACKAGE / "mcp.json").exists())
        self.assertFalse((PACKAGE / ".codex-plugin/plugin.json").exists())

    def test_one_governance_skill_explains_dual_path_and_authority(self):
        skills = list((PACKAGE / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 1)
        skill = skills[0].read_text(encoding="utf-8")
        self.assertIn("load_continuity_resume", skill)
        self.assertIn("build_repository_handoff", skill)
        self.assertIn("build_project_handoff", skill)
        self.assertIn("RECONCILIATION_REQUIRED", skill)
        self.assertIn("DURABLE_AUTHORITY_MAY_HAVE_CHANGED", skill)
        self.assertNotIn("next_authorized_action", skill)


if __name__ == "__main__":
    unittest.main()
