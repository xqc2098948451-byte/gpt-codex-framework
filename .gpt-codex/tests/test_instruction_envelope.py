import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VALID_ID = "11111111-1111-4111-8111-111111111111"


def load_instruction_envelope():
    path = SCRIPTS / "instruction_envelope.py"
    if not path.is_file():
        raise AssertionError("instruction_envelope.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("instruction_envelope_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionEnvelopeTests(unittest.TestCase):
    def test_instruction_schema_and_template_exist_with_context_contract(self):
        schema_path = ROOT / "schemas" / "instruction-envelope.schema.json"
        template_path = ROOT / "project-template" / "INSTRUCTION_ENVELOPE.template.json"
        self.assertTrue(schema_path.is_file())
        self.assertTrue(template_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        template = json.loads(template_path.read_text(encoding="utf-8"))
        for key in (
            "instruction_id",
            "instruction_type",
            "target_project_context_id",
            "target_project_name",
            "expected_state_revision",
            "framework_version",
        ):
            self.assertIn(key, schema["properties"])
            self.assertIn(key, template)

    def test_builder_generates_all_required_fields_without_manual_identity(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.1.0",
        )
        for key in (
            "instruction_id",
            "instruction_type",
            "target_project_context_id",
            "target_project_name",
            "expected_state_revision",
            "framework_version",
        ):
            self.assertIn(key, envelope)
        self.assertNotEqual(envelope["instruction_id"], "NONE")

    def test_instruction_is_one_copyable_block_with_envelope_first(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.1.0",
        )
        rendered = ie.render_codex_instruction(
            envelope,
            "Run the authorized task body.",
            {"execution_strategy": "串行", "approval": "需要 GPT 判断"},
        )
        self.assertTrue(rendered.startswith("INSTRUCTION_ID:"))
        self.assertLess(rendered.index("INSTRUCTION_ID:"), rendered.index("Run the authorized task body."))
        self.assertIn("TARGET_PROJECT_CONTEXT_ID: " + VALID_ID, rendered)
        self.assertEqual(rendered.count("Run the authorized task body."), 1)

    def test_legacy_bootstrap_carries_target_project_id(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="Example Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_target_project_id="LEGACY-001",
        )
        self.assertEqual(envelope["bootstrap_target_project_id"], "LEGACY-001")

    def test_challenge_bound_bootstrap_carries_exact_challenge(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="New Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_challenge_id="challenge-opaque-001",
        )
        self.assertEqual(envelope["bootstrap_challenge_id"], "challenge-opaque-001")

    def test_normal_instruction_requires_target_and_challenge_bootstrap_is_identity_only(self):
        ie = load_instruction_envelope()
        with self.assertRaises(ValueError):
            ie.build_instruction_envelope(
                instruction_type="WORK_UNIT",
                target_project_context_id=None,
                target_project_name="Example Project",
                expected_state_revision=7,
                framework_version="2.1.0",
            )
        challenge = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="New Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_challenge_id="challenge-opaque-001",
            bootstrap_phase="CHALLENGE_BOUND",
        )
        with self.assertRaises(ValueError):
            ie.render_codex_instruction(
                challenge,
                "run business task",
                {"execution_strategy": "串行", "approval": "需要 GPT 判断"},
            )


if __name__ == "__main__":
    unittest.main()
