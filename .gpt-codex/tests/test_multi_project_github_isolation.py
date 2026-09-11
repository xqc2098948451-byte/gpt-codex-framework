import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from context_binding import evaluate_instruction, evaluate_return


class MultiProjectGithubIsolationTests(unittest.TestCase):
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
