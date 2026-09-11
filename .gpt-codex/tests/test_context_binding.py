import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VALID_ID = "11111111-1111-4111-8111-111111111111"
FOREIGN_ID = "22222222-2222-4222-8222-222222222222"


def load_context_binding():
    path = SCRIPTS / "context_binding.py"
    if not path.is_file():
        raise AssertionError("context_binding.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("context_binding_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def migrated_control(guardrails=None):
    return {
        "project_context_id": VALID_ID,
        "project_name": "Example Project",
        "framework": {"adopted_version": "2.1.0"},
        "extensions": {"guardrails": guardrails if guardrails is not None else [
            {"id": "cross-project-context-binding", "source": "builtin", "version": "1.0.0", "enabled": True}
        ]},
    }


class ContextBindingTests(unittest.TestCase):
    def test_same_project_instruction_allows_even_when_framework_version_differs(self):
        cb = load_context_binding()
        decision = cb.evaluate_instruction(
            {
                "instruction_type": "WORK_UNIT",
                "target_project_context_id": VALID_ID,
                "target_project_name": "Example Project",
                "framework_version": "2.0.3",
                "expected_state_revision": 4,
            },
            local_context_id=VALID_ID,
            current_state_revision=4,
            project_control=migrated_control(),
        )
        self.assertEqual(decision.decision, "ALLOW")
        self.assertTrue(decision.identity_match)

    def test_different_project_instruction_is_denied_without_mutation(self):
        cb = load_context_binding()
        decision = cb.evaluate_instruction(
            {"instruction_type": "WORK_UNIT", "target_project_context_id": FOREIGN_ID},
            local_context_id=VALID_ID,
            current_state_revision=4,
            project_control=migrated_control(),
        )
        self.assertEqual(decision.decision, "DENY")
        self.assertEqual(decision.reason, "CROSS_PROJECT_INSTRUCTION_MISMATCH")
        self.assertFalse(decision.current_project_mutation)
        self.assertFalse(decision.action_executable)

    def test_same_name_different_id_is_denied(self):
        cb = load_context_binding()
        decision = cb.evaluate_instruction(
            {"instruction_type": "WORK_UNIT", "target_project_context_id": FOREIGN_ID, "target_project_name": "Example Project"},
            local_context_id=VALID_ID,
            current_state_revision=4,
            project_control=migrated_control(),
        )
        self.assertEqual(decision.decision, "DENY")

    def test_stale_instruction_is_reconciliation_not_cross_project(self):
        cb = load_context_binding()
        decision = cb.evaluate_instruction(
            {"instruction_type": "WORK_UNIT", "target_project_context_id": VALID_ID, "expected_state_revision": 3},
            local_context_id=VALID_ID,
            current_state_revision=4,
            project_control=migrated_control(),
        )
        self.assertEqual(decision.decision, "RECONCILIATION_REQUIRED")
        self.assertEqual(decision.reason, "STALE_INSTRUCTION")
        self.assertTrue(decision.identity_match)
        self.assertFalse(decision.action_executable)

    def test_malformed_or_missing_target_fails_closed(self):
        cb = load_context_binding()
        for envelope in ({"instruction_type": "WORK_UNIT"}, {"target_project_context_id": "not-an-id"}):
            with self.subTest(envelope=envelope):
                decision = cb.evaluate_instruction(
                    envelope,
                    local_context_id=VALID_ID,
                    current_state_revision=4,
                    project_control=migrated_control(),
                )
                self.assertEqual(decision.decision, "DENY")
                self.assertFalse(decision.current_project_mutation)

    def test_missing_active_context_and_foreign_return_are_denied(self):
        cb = load_context_binding()
        unbound = cb.evaluate_return(
            {"source_project_context_id": VALID_ID, "status": "PASS", "next_gpt_action": "do work"},
            active_context_id=None,
            project_control=migrated_control(),
        )
        self.assertEqual(unbound.reason, "ACTIVE_PROJECT_CONTEXT_UNBOUND")
        foreign = cb.evaluate_return(
            {"source_project_context_id": FOREIGN_ID, "status": "PASS", "next_gpt_action": "do work"},
            active_context_id=VALID_ID,
            project_control=migrated_control(),
        )
        self.assertEqual(foreign.decision, "DENY")
        self.assertEqual(foreign.reason, "CROSS_PROJECT_CONTEXT_MISMATCH")
        self.assertFalse(foreign.action_executable)

    def test_explicit_foreign_analysis_has_no_current_authority(self):
        cb = load_context_binding()
        decision = cb.evaluate_return(
            {"source_project_context_id": FOREIGN_ID, "status": "PASS", "next_gpt_action": "do work"},
            active_context_id=VALID_ID,
            analysis_only=True,
            project_control=migrated_control(),
        )
        self.assertEqual(decision.decision, "ANALYSIS_ONLY")
        self.assertEqual(decision.authority, "NONE")
        self.assertFalse(decision.current_project_mutation)
        self.assertFalse(decision.action_executable)

    def test_required_guardrail_is_single_control_source_and_optional_builtins_remain_optional(self):
        cb = load_context_binding()
        allowed = cb.required_guardrail_allows(
            {**migrated_control(), "extensions": {"guardrails": [
                {"id": "cross-project-context-binding", "source": "builtin", "version": "1.0.0", "enabled": True}
            ]}},
            "instruction",
        )
        self.assertEqual(allowed.decision, "ALLOW")
        missing = cb.required_guardrail_allows(migrated_control(guardrails=[]), "instruction")
        self.assertEqual(missing.decision, "DENY")
        disabled = cb.required_guardrail_allows(
            migrated_control(guardrails=[{"id": "cross-project-context-binding", "source": "builtin", "version": "1.0.0", "enabled": False}]),
            "return",
        )
        self.assertEqual(disabled.decision, "DENY")
        optional_only = cb.required_guardrail_allows(
            {**migrated_control(), "extensions": {"guardrails": [
                {"id": "cross-project-context-binding", "source": "builtin", "version": "1.0.0", "enabled": True},
                {"id": "optional-extra", "source": "builtin", "version": "1.0.0", "enabled": False},
            ]}},
            "instruction",
        )
        self.assertEqual(optional_only.decision, "ALLOW")


if __name__ == "__main__":
    unittest.main()
