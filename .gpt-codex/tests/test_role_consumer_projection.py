import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from consumer_projection import audit_projection_paths, load_projection_manifest


class RoleConsumerProjectionTests(unittest.TestCase):
    def test_generic_role_protocol_assets_are_consumer_required(self):
        manifest = load_projection_manifest(ROOT)
        for relative in (
            ".gpt-codex/schemas/instruction-envelope.schema.json",
            ".gpt-codex/schemas/result-envelope.schema.json",
            ".gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json",
            ".gpt-codex/project-template/RESULT_ENVELOPE.template.json",
            ".gpt-codex/scripts/role_communication.py",
            ".gpt-codex/scripts/instruction_envelope.py",
            ".gpt-codex/scripts/result_return.py",
            ".gpt-codex/scripts/validate_project.py",
        ):
            with self.subTest(relative=relative):
                self.assertEqual(manifest["paths"].get(relative), "CONSUMER_REQUIRED")

    def test_role_protocol_development_tests_remain_management_only(self):
        manifest = load_projection_manifest(ROOT)
        for relative in (
            ".gpt-codex/tests/test_role_consumer_projection.py",
            ".gpt-codex/tests/test_stage_review_routing.py",
            ".gpt-codex/tests/test_review_history.py",
            ".gpt-codex/tests/test_role_routing_docs.py",
        ):
            with self.subTest(relative=relative):
                self.assertEqual(manifest["paths"].get(relative), "MANAGEMENT_ONLY")

    def test_current_projection_has_no_unknown_or_missing_role_protocol_paths(self):
        audit = audit_projection_paths(ROOT, load_projection_manifest(ROOT))
        self.assertEqual(audit["unknown_paths"], [])
        self.assertEqual(audit["missing_required_paths"], [])
        self.assertEqual(audit["invalid_classifications"], [])


if __name__ == "__main__":
    unittest.main()
