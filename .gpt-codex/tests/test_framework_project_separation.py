import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from context_binding import evaluate_project_identity, load_project_identity


VALID_CONTEXT_ID = "11111111-1111-4111-8111-111111111111"
FOREIGN_CONTEXT_ID = "22222222-2222-4222-8222-222222222222"


def valid_control() -> dict[str, object]:
    return {
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": "PRJ-001",
        "project_context_id": VALID_CONTEXT_ID,
        "project_name": "Example Project",
        "github": {
            "repository_id": "123",
            "repository_full_name": "owner/repo",
            "default_branch": "main",
        },
        "governance_profile": "STANDARD",
        "framework": {
            "adopted_version": "2.5.0",
            "last_evaluated_version": "2.5.0",
            "evaluation_result": "NO_ACTION",
        },
        "roots": {
            "project_role": "AUTHORITATIVE",
            "framework_role": "ADVISORY",
            "framework_kernel_access": "READ_ONLY",
            "framework_builtins_access": "READ_ONLY",
            "harvest_namespace": "PRJ-001",
        },
        "extensions": {
            "skills": [],
            "guardrails": [
                {"id": "cross-project-context-binding", "source": "builtin", "version": "1.0.0", "enabled": True},
                {"id": "github-repository-binding", "source": "builtin", "version": "1.0.0", "enabled": True},
            ],
            "fitness": [],
        },
        "permissions": {"production_access": "DENY", "destructive_operations": "APPROVAL_REQUIRED", "framework_kernel_write": "DENY", "framework_builtin_write": "DENY", "harvest_own_namespace_write": "ALLOW", "harvest_other_namespace_write": "DENY"},
        "complexity": {"default_decision": "DO_NOT_ADD", "reuse_before_extension": True, "degrade_before_extend": True, "generalize_after_repetition": True},
    }


class ProjectIdentityTests(unittest.TestCase):
    def test_valid_control_contains_current_required_keys(self):
        control = valid_control()
        self.assertTrue({"kernel_version", "schema_version", "project_id", "governance_profile", "framework", "roots", "extensions", "permissions", "complexity"}.issubset(control))
        self.assertEqual(set(control["github"]), {"repository_id", "repository_full_name", "default_branch"})
        self.assertEqual(set(control["roots"]), {"project_role", "framework_role", "framework_kernel_access", "framework_builtins_access", "harvest_namespace"})
        self.assertEqual(set(control["extensions"]), {"skills", "guardrails", "fitness"})

    def test_identity_precedence_ignores_project_name_and_framework_version(self):
        control = valid_control()
        control["project_name"] = "Wrong display name"
        control["framework"]["last_evaluated_version"] = "9.9.9"
        decision = evaluate_project_identity(control, expected_project_id="PRJ-001", expected_project_context_id=VALID_CONTEXT_ID, expected_repository_id="123")
        self.assertEqual(decision.decision, "ALLOW")
        self.assertTrue(decision.identity_match)
        self.assertFalse(decision.current_project_mutation)
        self.assertFalse(decision.action_executable)

    def test_malformed_control_identity_returns_project_identity_invalid(self):
        control = valid_control()
        control["project_context_id"] = "not-a-uuid"
        decision = evaluate_project_identity(control)
        self.assertEqual(decision.reason, "PROJECT_IDENTITY_INVALID")
        self.assertTrue(decision.hard_stop)

    def test_same_name_different_context_returns_cross_project_context_mismatch(self):
        decision = evaluate_project_identity(valid_control(), expected_project_context_id=FOREIGN_CONTEXT_ID)
        self.assertEqual(decision.reason, "CROSS_PROJECT_CONTEXT_MISMATCH")

    def test_matching_project_context_is_positively_accepted(self):
        decision = evaluate_project_identity(valid_control(), expected_project_context_id=VALID_CONTEXT_ID)
        self.assertEqual(decision.decision, "ALLOW")
        self.assertFalse(decision.action_executable)

    def test_framework_root_is_never_project_authority(self):
        identity = load_project_identity(valid_control(), framework_root=Path("framework"))
        self.assertEqual(identity.framework_role, "ADVISORY")
        self.assertFalse(identity.management)


if __name__ == "__main__":
    unittest.main()
