import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "role_communication.py"
    if not path.is_file():
        raise AssertionError("role_communication.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("role_communication_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoleCommunicationTaxonomyTests(unittest.TestCase):
    def test_roles_are_exactly_the_approved_protocol_roles(self):
        module = load_module()
        self.assertEqual(
            module.ROLES,
            frozenset(
                {
                    "GPT_ORCHESTRATOR",
                    "GPT_REVIEWER",
                    "CODEX_IMPLEMENTER",
                    "CODEX_REVIEWER",
                    "USER_APPROVER",
                    "USER_LOCAL",
                    "INFORMATION_ONLY",
                }
            ),
        )
        self.assertNotIn("GPT_USER", module.ROLES)
        self.assertNotIn("PLAN_TASK", module.ROLES)
        self.assertNotIn("AGENT", module.ROLES)
        self.assertNotIn("FRESH_REVIEWER", module.ROLES)

    def test_instruction_and_result_types_are_disjoint(self):
        module = load_module()
        self.assertTrue(module.INSTRUCTION_TYPES)
        self.assertTrue(module.RESULT_MESSAGE_TYPES)
        self.assertTrue(module.INSTRUCTION_TYPES.isdisjoint(module.RESULT_MESSAGE_TYPES))
        self.assertIn("EXECUTION_INSTRUCTION", module.INSTRUCTION_TYPES)
        self.assertIn("REVIEW_REQUEST", module.INSTRUCTION_TYPES)
        self.assertIn("FIX_INSTRUCTION", module.INSTRUCTION_TYPES)
        self.assertIn("PROJECT_CONTEXT_BOOTSTRAP", module.INSTRUCTION_TYPES)
        self.assertIn("REVIEW_RESULT", module.RESULT_MESSAGE_TYPES)
        self.assertIn("REVIEW_FINDING", module.RESULT_MESSAGE_TYPES)
        self.assertIn("IMPLEMENTATION_RESULT", module.RESULT_MESSAGE_TYPES)

    def test_type_validators_are_side_specific(self):
        module = load_module()
        self.assertEqual(module.validate_instruction_type("FIX_INSTRUCTION"), [])
        self.assertEqual(module.validate_result_message_type("REVIEW_FINDING"), [])
        self.assertIn("RESULT_TYPE_NOT_ALLOWED_AS_INSTRUCTION", module.validate_instruction_type("REVIEW_RESULT"))
        self.assertIn("INSTRUCTION_TYPE_NOT_ALLOWED_AS_RESULT", module.validate_result_message_type("FIX_INSTRUCTION"))
        self.assertEqual(module.validate_instruction_type("WORK_UNIT"), [])
        self.assertIn("UNKNOWN_INSTRUCTION_TYPE", module.validate_instruction_type("UNREGISTERED"))

    def test_executor_validation_rejects_missing_plural_compound_and_unknown_values(self):
        module = load_module()
        self.assertIn("EXECUTOR_REQUIRED", module.validate_executor_role(None))
        self.assertIn("EXECUTOR_MUST_BE_SCALAR", module.validate_executor_role(["CODEX_IMPLEMENTER", "CODEX_REVIEWER"]))
        self.assertIn("EXECUTOR_MUST_BE_SCALAR", module.validate_executor_role("CODEX_IMPLEMENTER,CODEX_REVIEWER"))
        self.assertIn("UNKNOWN_EXECUTOR_ROLE", module.validate_executor_role("AGENT"))
        self.assertEqual(module.validate_executor_role("CODEX_IMPLEMENTER"), [])

    def test_legacy_instruction_aliases_are_explicit_and_fail_closed(self):
        module = load_module()
        self.assertEqual(module.validate_instruction_type("IMPLEMENTATION"), [])
        self.assertEqual(module.validate_instruction_type("WORK_UNIT"), [])
        self.assertIn("UNKNOWN_INSTRUCTION_TYPE", module.validate_instruction_type("CODEX_REVIEWER_RESULT"))

    def test_action_authority_rejects_unknown_overlap_and_role_violations(self):
        module = load_module()
        self.assertEqual(
            module.validate_action_authority(
                "CODEX_REVIEWER",
                ["READ", "TEST", "VALIDATE", "REPORT"],
                ["MUTATE_APPROVED_SCOPE"],
            ),
            [],
        )
        self.assertIn(
            "ACTION_NOT_ALLOWED_FOR_ROLE",
            module.validate_action_authority("CODEX_REVIEWER", ["MUTATE_APPROVED_SCOPE"], []),
        )
        self.assertIn(
            "UNKNOWN_ACTION",
            module.validate_action_authority("CODEX_IMPLEMENTER", ["UNREGISTERED_ACTION"], []),
        )
        self.assertIn(
            "ACTION_IN_AUTHORIZED_AND_FORBIDDEN",
            module.validate_action_authority("CODEX_IMPLEMENTER", ["READ"], ["READ"]),
        )

    def test_action_authority_rejects_non_array_shapes(self):
        module = load_module()
        self.assertIn(
            "INVALID_ACTIONS_SHAPE",
            module.validate_action_authority("CODEX_IMPLEMENTER", "READ", []),
        )
        self.assertIn(
            "INVALID_ACTIONS_SHAPE",
            module.validate_action_authority("CODEX_IMPLEMENTER", 7, []),
        )

    def test_legacy_codex_route_requires_bounded_structured_context(self):
        module = load_module()
        resolver = getattr(module, "resolve_legacy_codex_route", None)
        self.assertIsNotNone(resolver, "legacy [CODEX] resolver is not implemented")
        self.assertEqual(
            resolver("[CODEX]", "IMPLEMENTATION"),
            "CODEX_IMPLEMENTER",
        )
        self.assertEqual(
            resolver("[CODEX]", "REVIEW"),
            "CODEX_REVIEWER",
        )
        for marker, context, error in (
            ("[CODEX]", None, "LEGACY_ROUTE_CONTEXT_REQUIRED"),
            ("[CODEX]", ["IMPLEMENTATION", "REVIEW"], "LEGACY_ROUTE_AMBIGUOUS"),
            ("[UNKNOWN]", "IMPLEMENTATION", "UNKNOWN_LEGACY_ROUTE_MARKER"),
        ):
            with self.subTest(marker=marker, context=context):
                with self.assertRaisesRegex(ValueError, error):
                    resolver(marker, context)
        self.assertIn(
            "UNKNOWN_ACTION",
            module.validate_action_authority("CODEX_IMPLEMENTER", [["READ"]], []),
        )


if __name__ == "__main__":
    unittest.main()
