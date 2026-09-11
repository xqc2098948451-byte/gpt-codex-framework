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


if __name__ == "__main__":
    unittest.main()
