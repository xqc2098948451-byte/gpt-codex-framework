import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from framework_feedback import (  # noqa: E402
    FrameworkFeedback, ProcessReview, build_process_review,
    validate_execution_policy, validate_framework_feedback,
)


POLICY = {
    "strategy_profile_id": "PROJECT_PROFILE_001",
    "gpt_orchestrator_strategy": "MINIMAL_CLOSED_LOOP",
    "codex_implementer_strategy": "MINIMAL_DIFF_TDD",
    "codex_reviewer_strategy": "CONTRACT_FIRST",
    "task_splitting": "PROJECT_DETERMINED",
    "review_policy": "RISK_OR_MILESTONE",
    "instruction_policy": "REFERENCE_FIRST",
    "result_return_policy": "DURABLE_REF_FIRST",
}


class FrameworkFeedbackTests(unittest.TestCase):
    def test_valid_fixed_execution_policy_is_accepted(self):
        self.assertEqual(validate_execution_policy(POLICY), [])
        self.assertEqual(validate_execution_policy(None), [])

    def test_process_review_aggregates_observable_counters_and_unknown_usage(self):
        review = build_process_review(
            [{"codex_tasks": 2, "codex_retries": 1, "project_result": "PASS"},
             {"review_rounds": 1, "handoffs": 1}],
            "PROJECT_PROFILE_001",
        )
        self.assertIsInstance(review, ProcessReview)
        self.assertEqual((review.codex_tasks, review.codex_retries, review.review_rounds, review.handoffs), (2, 1, 1, 1))
        self.assertEqual(review.project_result, "PASS")
        self.assertEqual(review.usage, "UNKNOWN")

    def test_feedback_is_evidence_only_and_rejects_authority(self):
        record = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                  "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        self.assertEqual(validate_framework_feedback(record), [])
        self.assertIsInstance(FrameworkFeedback(**record), FrameworkFeedback)
        for key in ("authorized_actions", "framework_mutation", "policy_update", "release_authority", "adoption_authority"):
            with self.subTest(key=key):
                self.assertEqual(validate_framework_feedback({**record, key: True}), ["FRAMEWORK_FEEDBACK_INVALID"])


if __name__ == "__main__":
    unittest.main()
