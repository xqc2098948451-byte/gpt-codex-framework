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

    def test_feedback_evidence_refs_are_immutable_and_validated(self):
        feedback = FrameworkFeedback("p", "r", "s", "PASS", True, ("result:1",))
        self.assertIsInstance(feedback.evidence_refs, tuple)
        with self.assertRaises((AttributeError, TypeError)):
            feedback.evidence_refs += ("result:2",)
        with self.assertRaises(AttributeError):
            feedback.evidence_refs.append("result:2")
        base = {"problem": "p", "reason": "r", "local_solution": "s", "result": "PASS",
                "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        for refs in ([], [""], ["   "], [123], ["result:1", ""], "result:1", None):
            with self.subTest(refs=refs):
                self.assertEqual(validate_framework_feedback({**base, "evidence_refs": refs}), ["FRAMEWORK_FEEDBACK_INVALID"])

    def test_policy_and_counter_negatives_and_validator_reuse(self):
        import framework_feedback
        import validate_project
        self.assertIs(validate_project.validate_execution_policy, framework_feedback.validate_execution_policy)
        for key, value in (("strategy_profile_id", ""), ("task_splitting", "OTHER"),
                           ("instruction_policy", "OTHER"), ("result_return_policy", "OTHER"),
                           ("review_policy", "OTHER")):
            with self.subTest(key=key):
                policy = dict(POLICY); policy[key] = value
                self.assertEqual(validate_execution_policy(policy), ["EXECUTION_POLICY_INVALID"])
        for record in ({"codex_retries": -1}, {"codex_retries": True}, {"review_rounds": -1}):
            with self.subTest(record=record):
                with self.assertRaisesRegex(ValueError, "PROCESS_REVIEW_INVALID"):
                    build_process_review([record], "PROJECT_PROFILE_001")

if __name__ == "__main__":
    unittest.main()
