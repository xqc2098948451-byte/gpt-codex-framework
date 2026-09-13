import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    path = ROOT / "scripts" / "validate_project.py"
    spec = importlib.util.spec_from_file_location("validate_project_authority_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoleAuthorityTests(unittest.TestCase):
    def instruction(self, **overrides):
        value = {
            "instruction_id": "11111111-1111-4111-8111-111111111111",
            "instruction_type": "EXECUTION_INSTRUCTION",
            "issuer_role": "GPT_ORCHESTRATOR",
            "executor_role": "CODEX_IMPLEMENTER",
            "return_role": "GPT_ORCHESTRATOR",
            "expected_state_revision": 8,
            "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": ["PUBLISH"],
            "target_work_unit": "WU-001",
            "scope_paths": ["docs/approved.md"],
        }
        value.update(overrides)
        return value

    def test_valid_implementer_authority_passes(self):
        validator = load_validator()
        self.assertEqual(
            validator.validate_instruction_authority(
                self.instruction(),
                current_state_revision=8,
                approved_scope={"docs/approved.md"},
            ),
            [],
        )

    def test_unknown_plural_or_allocation_identity_is_invalid_instruction(self):
        validator = load_validator()
        for executor in (None, ["CODEX_IMPLEMENTER", "CODEX_REVIEWER"], "AGENT"):
            with self.subTest(executor=executor):
                errors = validator.validate_instruction_authority(
                    self.instruction(executor_role=executor),
                    current_state_revision=8,
                )
                self.assertTrue(any(code in " ".join(errors) for code in ("EXECUTOR_", "INVALID_INSTRUCTION", "UNKNOWN_EXECUTOR_ROLE")))

    def test_reviewer_mutation_is_denied_as_role_authority_conflict(self):
        validator = load_validator()
        errors = validator.validate_instruction_authority(
            self.instruction(executor_role="CODEX_REVIEWER", authorized_actions=["MUTATE_APPROVED_SCOPE"]),
            current_state_revision=8,
        )
        self.assertIn("ROLE_AUTHORITY_CONFLICT", errors)
        self.assertIn("REVIEWER_MUTATION_DENIED", errors)

    def test_stale_revision_and_scope_expansion_block_continuation(self):
        validator = load_validator()
        stale = validator.validate_instruction_authority(self.instruction(), current_state_revision=9)
        self.assertIn("RECONCILIATION_REQUIRED", stale)
        expanded = validator.validate_instruction_authority(
            self.instruction(scope_paths=["docs/approved.md", "src/forbidden.py"]),
            current_state_revision=8,
            approved_scope={"docs/approved.md"},
        )
        self.assertIn("ROLE_AUTHORITY_CONFLICT", expanded)
        self.assertIn("SCOPE_EXPANSION_DENIED", expanded)

    def test_finding_cannot_be_submitted_as_an_instruction(self):
        validator = load_validator()
        errors = validator.validate_instruction_authority(
            self.instruction(instruction_type="REVIEW_FINDING"),
            current_state_revision=8,
        )
        self.assertIn("INVALID_INSTRUCTION", errors)


if __name__ == "__main__":
    unittest.main()
