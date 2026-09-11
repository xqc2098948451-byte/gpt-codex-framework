import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContinuityContractSchemaTests(unittest.TestCase):
    def test_control_template_has_exactly_three_durable_github_fields(self):
        template = json.loads((ROOT / "project-template" / "CONTROL.template.json").read_text(encoding="utf-8"))
        self.assertEqual(set(template["github"]), {"repository_id", "repository_full_name", "default_branch"})
        self.assertNotIn("remote_name", template["github"])

    def test_state_template_has_continuity_facts(self):
        template = json.loads((ROOT / "project-template" / "STATE.template.json").read_text(encoding="utf-8"))
        self.assertEqual(set(template["continuity"]), {
            "current_remote_ref", "latest_verified_remote_sha", "latest_synced_state_revision",
            "last_verified_result_ref", "sync_status",
        })

    def test_schema_floors_and_result_namespace_are_preserved(self):
        control = json.loads((ROOT / "schemas" / "control.schema.json").read_text(encoding="utf-8"))
        state = json.loads((ROOT / "schemas" / "state.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(control["properties"]["kernel_version"]["const"], "2.0.0")
        self.assertEqual(state["properties"]["schema_version"]["const"], 1)
        self.assertTrue((ROOT / "project-template" / "evidence" / "results" / ".gitkeep").exists())


if __name__ == "__main__":
    unittest.main()
