import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class GitContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.available = importlib.util.find_spec("git_continuity") is not None

    def test_continuity_module_exists(self):
        self.assertTrue(self.available, "continuity decision core is required")

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_new_work_requires_clean_synced(self):
        from git_continuity import SyncSnapshot, evaluate_new_work_preflight

        clean = SyncSnapshot("a", "a", "refs/heads/main", False, 0, 0, False)
        offline = SyncSnapshot("a", None, "refs/heads/main", False, 0, 0, False)
        self.assertTrue(evaluate_new_work_preflight(clean, "a", "refs/heads/main", "a", 1, 1).mutation_allowed)
        self.assertFalse(evaluate_new_work_preflight(offline, "a", "refs/heads/main", "a", 1, 1).mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_active_authorized_work_can_degrade_but_cannot_pass_or_start_new_unit(self):
        from git_continuity import evaluate_active_work_degraded_continuation

        decision = evaluate_active_work_degraded_continuation(True, True, True, False, False)
        self.assertTrue(decision.mutation_allowed)
        self.assertFalse(decision.publish_allowed)
        self.assertEqual(decision.decision, "LOCAL_COMPLETE")
        self.assertFalse(evaluate_active_work_degraded_continuation(True, True, True, False, True).mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_publish_gate_requires_live_remote_verification(self):
        from github_repository_binding import BindingDecision
        from git_continuity import SyncDecision, evaluate_publish_gate

        binding = BindingDecision("ALLOW", "OK", True, True)
        sync = SyncDecision("CLEAN_SYNCED", "OK", True, True)
        self.assertEqual(evaluate_publish_gate(binding, sync, "SUCCEEDED", "VERIFIED", True).decision, "SYNCED")
        self.assertNotEqual(evaluate_publish_gate(binding, sync, "SUCCEEDED", "UNAVAILABLE", True).decision, "SYNCED")

    def test_review_revision_requires_descendant_of_formal_review(self):
        from git_continuity import validate_review_revision

        self.assertEqual(validate_review_revision(None, "b" * 40, lambda _old, _new: False), [])
        self.assertEqual(validate_review_revision("a" * 40, "b" * 40, lambda _old, _new: True), [])
        errors = validate_review_revision("a" * 40, "b" * 40, lambda _old, _new: False)
        self.assertIn("RECONCILIATION_REQUIRED", errors)
        self.assertIn("REVIEWED_REVISION_NOT_ANCESTOR", errors)

    def test_review_revision_rejects_invalid_sha_inputs(self):
        from git_continuity import validate_review_revision

        for previous, candidate in (("bad", "b" * 40), (None, "bad"), ("a" * 40, None)):
            with self.subTest(previous=previous, candidate=candidate):
                errors = validate_review_revision(previous, candidate, lambda _old, _new: True)
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn("REVIEWED_REVISION_INVALID", errors)

    def test_review_history_operations_are_append_only_after_design_plan_review(self):
        from git_continuity import validate_review_history_operation

        for stage in ("DESIGN", "PLAN"):
            for operation in ("EDIT", "COMMIT", "FAST_FORWARD_PUSH", "VERIFY_REMOTE"):
                with self.subTest(stage=stage, operation=operation):
                    self.assertEqual(validate_review_history_operation(stage, operation), [])
            for operation in (
                "AMEND", "REBASE", "RESET_REVIEWED", "FORCE_PUSH", "FORCE_WITH_LEASE",
                "REPLACE_BRANCH", "DELETE_BRANCH", "MERGE_MAIN", "TAG", "RELEASE", "PUBLISH",
            ):
                with self.subTest(stage=stage, operation=operation):
                    errors = validate_review_history_operation(stage, operation)
                    self.assertIn("ROLE_AUTHORITY_CONFLICT", errors)
                    self.assertIn("REVIEW_HISTORY_REWRITE_FORBIDDEN", errors)

        self.assertEqual(validate_review_history_operation("IMPLEMENTATION", "AMEND"), [])

    def test_worktree_cleanup_is_evidence_gated_and_fail_closed(self):
        from git_continuity import evaluate_worktree_cleanup

        self.assertEqual(evaluate_worktree_cleanup(False, True, True, False), "CLEAN")
        for facts in (
            (True, True, True, False),
            (False, False, True, False),
            (False, True, False, False),
            (False, True, True, True),
        ):
            with self.subTest(facts=facts):
                self.assertEqual(evaluate_worktree_cleanup(*facts), "KEEP")
        for position in range(4):
            facts = [False, True, True, False]
            facts[position] = None
            with self.subTest(unknown_position=position):
                self.assertEqual(evaluate_worktree_cleanup(*facts), "KEEP")


if __name__ == "__main__":
    unittest.main()
