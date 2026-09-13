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
        self.assertEqual(project_map_schema["properties"]["authority"], {"const": "DERIVED_NAVIGATION_INDEX"})
        self.assertEqual(module_map_schema["properties"]["authority"], {"const": "DERIVED_NAVIGATION_INDEX"})
        self.assertEqual(project_map_template["authority"], "DERIVED_NAVIGATION_INDEX")
        self.assertEqual(module_map_template["authority"], "DERIVED_NAVIGATION_INDEX")
        self.assertEqual(resume_template["authority"], "DERIVED_CACHE")

        for template in (project_map_template, module_map_template):
            self.assertNotIn("state", template)
            self.assertNotIn("state_revision", template)
        self.assertIn("hot_modules", resume_template["working_set"])

    def test_resume_contract_places_approved_context_and_working_set_fields_correctly(self):
        resume_schema = json.loads(
            (ROOT / "schemas" / "resume.schema.json").read_text(encoding="utf-8")
        )
        resume_template = json.loads(
            (ROOT / "project-template" / "continuity" / "RESUME.template.json").read_text(
                encoding="utf-8"
            )
        )

        for field in ("context_sources", "objective", "decision", "blocker", "verification"):
            self.assertIn(field, resume_schema["required"])
            self.assertIn(field, resume_schema["properties"])
            self.assertIn(field, resume_template)
        self.assertEqual(len(resume_schema["required"]), len(set(resume_schema["required"])))

        working_set_fields = {
            "hot_modules",
            "hot_files",
            "next_required_reads",
            "invalidated_context",
        }
        self.assertTrue(working_set_fields.issubset(resume_schema["properties"]["working_set"]["required"]))
        self.assertTrue(working_set_fields.issubset(resume_template["working_set"]))
        self.assertNotIn("next_required_reads", resume_schema["properties"])
        self.assertNotIn("invalidated_context", resume_schema["properties"])
        self.assertNotIn("next_required_reads", resume_template)
        self.assertNotIn("invalidated_context", resume_template)
        self.assertNotIn("checkpoint", resume_schema["properties"])
        self.assertNotIn("checkpoint", resume_template)

    def test_module_map_preserves_file_roles_and_project_map_uses_root_relative_loader_path(self):
        module_map_schema = json.loads(
            (ROOT / "schemas" / "module-map.schema.json").read_text(encoding="utf-8")
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

        key_file_schema = module_map_schema["properties"]["key_files"]["items"]
        self.assertEqual(key_file_schema["type"], "object")
        self.assertTrue({"path", "role"}.issubset(key_file_schema["required"]))
        self.assertEqual(
            module_map_template["key_files"],
            [{"path": "src/example/index.ext", "role": "Replace with this file's verified role."}],
        )
        self.assertEqual(
            project_map_template["modules"][0]["module_map"],
            ".gpt-codex/navigation/modules/MODULE_MAP.example-module.json",
        )


if __name__ == "__main__":
    unittest.main()
