import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from context_binding import (
    evaluate_project_authority_boundary,
    evaluate_project_identity,
    evaluate_return,
    load_project_identity,
)
from validate_project import (
    evaluate_framework_compatibility,
    validate_evidence_project_binding,
    validate_framework_adoption,
)
from framework_feedback import (  # noqa: E402
    framework_feedback_authorizes_mutation,
    validate_framework_evolution_boundary,
)


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


def complete_result(source_context_id: str, *, repository_id: str = "123", repository_full_name: str | None = "owner/repo") -> dict[str, object]:
    return {"source_project_context_id": source_context_id, "source_github_repository_id": repository_id, "source_github_repository_full_name": repository_full_name, "status": "PASS", "work_unit_id": "WU-001", "state_revision": 6}


class AuthorityAndCompatibilityTests(unittest.TestCase):
    def test_feedback_boundary_preserves_project_authority_and_inputs(self):
        control = valid_control()
        feedback = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                    "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        original_control = deepcopy(control)
        original_feedback = deepcopy(feedback)

        self.assertEqual(validate_framework_evolution_boundary(control, feedback), [])
        self.assertFalse(framework_feedback_authorizes_mutation(control, feedback))
        self.assertEqual(control, original_control)
        self.assertEqual(feedback, original_feedback)
        self.assertEqual(control["framework"]["adopted_version"], "2.5.0")
        self.assertEqual(control["governance_profile"], "STANDARD")

    def test_feedback_boundary_rejects_invalid_project_authority_and_allows_management_import(self):
        feedback = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                    "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        invalid = valid_control()
        invalid["roots"]["framework_role"] = "SELF_MANAGED"
        management = valid_control()
        management["framework_management_only"] = True

        self.assertEqual(validate_framework_evolution_boundary(invalid, feedback), ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"])
        self.assertEqual(validate_framework_evolution_boundary(management, feedback), [])
        self.assertFalse(framework_feedback_authorizes_mutation(management, feedback))

    def test_project_read_is_allowed_but_does_not_authorize_mutation(self):
        decision = evaluate_project_authority_boundary(load_project_identity(valid_control()), source="project", operation="READ")
        self.assertEqual(decision.decision, "ALLOW")
        self.assertFalse(decision.current_project_mutation)
        self.assertFalse(decision.action_executable)

    def test_project_write_requires_separate_authorization(self):
        decision = evaluate_project_authority_boundary(load_project_identity(valid_control()), source="project", operation="WRITE")
        self.assertEqual(decision.reason, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION")
        self.assertFalse(decision.action_executable)

    def test_unknown_framework_operation_fails_closed(self):
        decision = evaluate_project_authority_boundary(load_project_identity(valid_control()), source="framework", operation="DELETE")
        self.assertEqual(decision.reason, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION")

    def test_adopt_is_not_authorized_by_identity_boundary(self):
        decision = evaluate_project_authority_boundary(load_project_identity(valid_control()), source="project", operation="ADOPT")
        self.assertEqual(decision.reason, "FRAMEWORK_ADOPTION_NOT_AUTHORIZED")

    def test_result_matching_repository_id_but_contradictory_full_name_is_denied(self):
        decision = evaluate_return(complete_result(VALID_CONTEXT_ID, repository_full_name="other/repo"), VALID_CONTEXT_ID, 6, project_control=valid_control(), local_repository_id="123")
        self.assertEqual(decision.reason, "GITHUB_REPOSITORY_MISMATCH")

    def test_result_matching_repository_id_with_missing_full_name_is_allowed(self):
        decision = evaluate_return(complete_result(VALID_CONTEXT_ID, repository_full_name=None), VALID_CONTEXT_ID, 6, project_control=valid_control(), local_repository_id="123")
        self.assertEqual(decision.decision, "ALLOW")

    def test_foreign_result_context_returns_cross_project_context_mismatch(self):
        decision = evaluate_return(complete_result(FOREIGN_CONTEXT_ID), VALID_CONTEXT_ID, 6, project_control=valid_control(), local_repository_id="123")
        self.assertEqual(decision.reason, "CROSS_PROJECT_CONTEXT_MISMATCH")

    def test_evidence_project_binding_is_non_authorizing(self):
        self.assertEqual(validate_evidence_project_binding({"project_id": "PRJ-001", "state_revision": 1}, valid_control(), current_state_revision=6), [])
        self.assertEqual(validate_evidence_project_binding({"project_id": "PRJ-FOREIGN", "state_revision": 1}, valid_control(), current_state_revision=6), ["PROJECT_IDENTITY_INVALID"])

    def test_compatibility_evaluation_is_read_only_with_all_classifications(self):
        control = valid_control()
        cases = [
            ({"evaluated_version": "2.5.0", "compatible": True, "reusable": False, "requires_migration": False}, "NO_ACTION"),
            ({"evaluated_version": "2.6.0", "compatible": True, "reusable": True, "requires_migration": False}, "OPTIONAL_REUSE"),
            ({"evaluated_version": "2.6.0", "compatible": True, "reusable": False, "requires_migration": False}, "RECOMMENDED_UPGRADE"),
            ({"evaluated_version": "2.6.0", "compatible": True, "reusable": False, "requires_migration": True}, "REQUIRED_MIGRATION"),
            ({"identity_conflict": True}, "CONFLICT"),
        ]
        for facts, classification in cases:
            with self.subTest(classification=classification):
                result = evaluate_framework_compatibility(control, facts)
                self.assertEqual(result["classification"], classification)
                self.assertFalse(result["mutated"])
                self.assertFalse(result["adoption_authorized"])

    def test_adoption_requires_role_work_unit_and_revision_authority(self):
        instruction = {"target_work_unit": "WU-001", "expected_state_revision": 6, "executor_role": "CODEX_IMPLEMENTER", "authorized_actions": ["MUTATE_APPROVED_SCOPE"], "forbidden_actions": []}
        work_unit = {"project_id": "PRJ-001", "work_unit_id": "WU-001", "state": "AUTHORIZED", "basis_state_revision": 6}
        self.assertEqual(validate_framework_adoption(valid_control(), instruction, work_unit, current_state_revision=6), [])
        instruction["authorized_actions"] = ["READ"]
        self.assertEqual(validate_framework_adoption(valid_control(), instruction, work_unit, current_state_revision=6), ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"])

    def test_durable_historical_result_does_not_require_current_state_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(ROOT, project_root / ".gpt-codex")
            script = project_root / ".gpt-codex" / "scripts" / "validate_project.py"
            result = subprocess.run([sys.executable, str(script), str(project_root)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("STALE_STATE_REVISION", result.stdout)

    def test_live_return_freshness_remains_strict(self):
        envelope = complete_result(VALID_CONTEXT_ID)
        envelope["state_revision"] = 3
        decision = evaluate_return(envelope, VALID_CONTEXT_ID, 6, project_control=valid_control(), local_repository_id="123")
        self.assertEqual(decision.decision, "RECONCILIATION_REQUIRED")
        self.assertEqual(decision.reason, "STALE_STATE_REVISION")


if __name__ == "__main__":
    unittest.main()
