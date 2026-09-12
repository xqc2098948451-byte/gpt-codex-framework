import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NavigationSchemaTests(unittest.TestCase):
    def test_navigation_and_resume_assets_preserve_derived_authority_contracts(self):
        project_map_schema = json.loads(
            (ROOT / "schemas" / "project-map.schema.json").read_text(encoding="utf-8")
        )
        module_map_schema = json.loads(
            (ROOT / "schemas" / "module-map.schema.json").read_text(encoding="utf-8")
        )
        resume_schema = json.loads(
            (ROOT / "schemas" / "resume.schema.json").read_text(encoding="utf-8")
        )
        project_map_template = json.loads(
            (ROOT / "project-template" / "navigation" / "PROJECT_MAP.template.json").read_text(
                encoding="utf-8"
            )
        )
        module_map_template = json.loads(
            (ROOT / "project-template" / "navigation" / "modules" / "MODULE_MAP.template.json").read_text(
                encoding="utf-8"
            )
        )
        resume_template = json.loads(
            (ROOT / "project-template" / "continuity" / "RESUME.template.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(project_map_schema["$id"], "gpt-codex/project-map-v1")
        self.assertEqual(module_map_schema["$id"], "gpt-codex/module-map-v1")
        self.assertEqual(resume_schema["$id"], "gpt-codex/resume-v1")
        self.assertEqual(
            project_map_schema["properties"]["authority"]["const"], "DERIVED_NAVIGATION_INDEX"
        )
        self.assertEqual(
            module_map_schema["properties"]["authority"]["const"], "DERIVED_NAVIGATION_INDEX"
        )
        self.assertEqual(resume_schema["properties"]["authority"]["const"], "DERIVED_CACHE")
        self.assertIn("hot_modules", resume_schema["properties"]["working_set"]["properties"])

        for template in (project_map_template, module_map_template):
            self.assertNotIn("state", template)
            self.assertNotIn("state_revision", template)
        self.assertIn("hot_modules", resume_template["working_set"])


if __name__ == "__main__":
    unittest.main()
