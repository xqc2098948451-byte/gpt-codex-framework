import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from git_continuity import classify_review_sync, review_routing_for_stage


class StageReviewRoutingTests(unittest.TestCase):
    def test_design_and_plan_require_remote_visibility_and_gpt_review(self):
        for stage in ("DESIGN", "PLAN"):
            with self.subTest(stage=stage):
                routing = review_routing_for_stage(stage)
                self.assertEqual(routing["remote_review_visibility"], "REQUIRED")
                self.assertEqual(routing["gpt_review"], "REQUIRED")
                self.assertEqual(routing["reviewer_role"], "GPT_REVIEWER")

    def test_implementation_uses_codex_reviewer_and_optional_remote_visibility(self):
        routing = review_routing_for_stage("IMPLEMENTATION")
        self.assertEqual(routing["remote_review_visibility"], "OPTIONAL")
        self.assertEqual(routing["technical_review"], "CODEX_REVIEWER")

    def test_remote_trigger_is_preserved_as_review_reason(self):
        routing = review_routing_for_stage("IMPLEMENTATION", "FINAL_ACCEPTANCE")
        self.assertEqual(routing["remote_trigger"], "FINAL_ACCEPTANCE")

    def test_unknown_stage_and_trigger_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_REVIEW_STAGE"):
            review_routing_for_stage("RELEASE")
        with self.assertRaisesRegex(ValueError, "INVALID_REMOTE_TRIGGER"):
            review_routing_for_stage("IMPLEMENTATION", "")

    def test_missing_or_incomplete_sync_evidence_is_pending(self):
        pending_cases = (
            ("NOT_ATTEMPTED", "NOT_ATTEMPTED", None),
            ("FAILED", "UNAVAILABLE", None),
            ("SUCCEEDED", "INCOMPLETE", None),
            ("SUCCEEDED", "UNAVAILABLE", None),
        )
        for push_status, verification, remote_head in pending_cases:
            with self.subTest(push_status=push_status, verification=verification):
                self.assertEqual(
                    classify_review_sync("DESIGN", push_status, verification, remote_head, "b" * 40),
                    "LOCAL_COMPLETE / SYNC_PENDING",
                )

    def test_conflicting_sync_facts_require_reconciliation(self):
        cases = (
            ("SUCCEEDED", "VERIFIED", "c" * 40),
            ("SUCCEEDED", "DIVERGED", "b" * 40),
            ("SUCCEEDED", "STALE_STATE_REVISION", "b" * 40),
            ("SUCCEEDED", "IDENTITY_CONFLICT", "b" * 40),
        )
        for push_status, verification, remote_head in cases:
            with self.subTest(verification=verification):
                self.assertEqual(
                    classify_review_sync("PLAN", push_status, verification, remote_head, "b" * 40),
                    "RECONCILIATION_REQUIRED",
                )

    def test_verified_matching_sync_is_synced(self):
        self.assertEqual(
            classify_review_sync("PLAN", "SUCCEEDED", "VERIFIED", "b" * 40, "b" * 40),
            "SYNCED",
        )


if __name__ == "__main__":
    unittest.main()
