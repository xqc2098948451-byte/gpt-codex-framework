import sys
from copy import deepcopy
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from context_binding import evaluate_instruction, evaluate_return
from framework_feedback import framework_feedback_authorizes_mutation, validate_framework_evolution_boundary


class MultiProjectGithubIsolationTests(unittest.TestCase):
    def test_project_a_feedback_cannot_authorize_or_propagate_to_project_b(self):
        project_a = {"project_id": "PRJ-A", "project_context_id": "11111111-1111-4111-8111-111111111111",
                     "github": {"repository_id": "repo-a"}, "framework": {"adopted_version": "2.5.0"},
                     "governance_profile": "STANDARD",
                     "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"}}
        project_b = {"project_id": "PRJ-B", "project_context_id": "22222222-2222-4222-8222-222222222222",
                     "github": {"repository_id": "repo-b"}, "framework": {"adopted_version": "2.4.0"},
                     "governance_profile": "STANDARD"}
        feedback = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                    "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        original_b = deepcopy(project_b)

        self.assertEqual(validate_framework_evolution_boundary(project_a, feedback), [])
        self.assertFalse(framework_feedback_authorizes_mutation(project_a, feedback))
        self.assertEqual(project_b, original_b)

    def test_same_context_wrong_repository_denies_instruction(self):
        envelope = {"target_project_context_id": "11111111-1111-4111-8111-111111111111", "target_github_repository_id": "repo-b"}
        control = {"project_context_id": envelope["target_project_context_id"], "github": {"repository_id": "repo-a", "repository_full_name": "o/a", "default_branch": "main"}}
        decision = evaluate_instruction(envelope, envelope["target_project_context_id"], 0, project_control=control, local_repository_id="repo-a")
        self.assertEqual(decision.decision, "DENY")

    def test_wrong_context_same_repository_denies_return(self):
        envelope = {"source_project_context_id": "22222222-2222-4222-8222-222222222222", "source_github_repository_id": "repo-a"}
        control = {"project_context_id": "11111111-1111-4111-8111-111111111111", "github": {"repository_id": "repo-a", "repository_full_name": "o/a", "default_branch": "main"}}
        decision = evaluate_return(envelope, control["project_context_id"], 0, project_control=control, local_repository_id="repo-a")
        self.assertEqual(decision.decision, "DENY")


if __name__ == "__main__":
    unittest.main()
