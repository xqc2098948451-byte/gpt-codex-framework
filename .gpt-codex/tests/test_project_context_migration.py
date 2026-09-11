import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALID_ID = "11111111-1111-4111-8111-111111111111"
CHALLENGE = "challenge-opaque-001"


def load_context_binding():
    path = ROOT / "scripts" / "context_binding.py"
    if not path.is_file():
        raise AssertionError("context_binding.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("context_binding_migration_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProjectContextMigrationTests(unittest.TestCase):
    def test_legacy_bootstrap_requires_matching_project_id(self):
        cb = load_context_binding()
        local = {"project_id": "LEGACY-001"}
        allowed = cb.evaluate_bootstrap(
            {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP", "bootstrap_target_project_id": "LEGACY-001"},
            local,
        )
        self.assertIn(allowed.decision, {"ALLOW", "BOOTSTRAP_REQUIRED"})
        mismatch = cb.evaluate_bootstrap(
            {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP", "bootstrap_target_project_id": "FOREIGN-001"},
            local,
        )
        self.assertEqual(mismatch.decision, "DENY")
        self.assertEqual(mismatch.reason, "CROSS_PROJECT_BOOTSTRAP_MISMATCH")
        self.assertFalse(mismatch.current_project_mutation)

    def test_first_uninitialized_bootstrap_is_read_only_challenge(self):
        cb = load_context_binding()
        first = cb.evaluate_bootstrap(
            {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP"},
            local_control=None,
        )
        self.assertEqual(first.decision, "BOOTSTRAP_REQUIRED")
        self.assertEqual(first.reason, "BOOTSTRAP_CHALLENGE_REQUIRED")
        self.assertFalse(first.current_project_mutation)
        challenge = cb.create_bootstrap_challenge({"project_name_hint": "New Project"}, challenge_factory=lambda: CHALLENGE)
        self.assertEqual(challenge["bootstrap_challenge_id"], CHALLENGE)

    def test_exact_challenge_allows_identity_only_and_consumption_blocks_replay(self):
        cb = load_context_binding()
        pending = {"bootstrap_challenge_id": CHALLENGE, "consumed": False}
        allowed = cb.verify_bootstrap_challenge(
            {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP", "bootstrap_challenge_id": CHALLENGE, "task_body": "business"},
            pending,
        )
        self.assertEqual(allowed.decision, "ALLOW")
        self.assertTrue(allowed.hard_stop)
        self.assertFalse(allowed.business_execution)
        self.assertTrue(pending["consumed"])
        replay = cb.verify_bootstrap_challenge(
            {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP", "bootstrap_challenge_id": CHALLENGE},
            pending,
        )
        self.assertEqual(replay.decision, "DENY")
        self.assertEqual(replay.reason, "BOOTSTRAP_CHALLENGE_REPLAY")

    def test_wrong_or_stale_challenge_is_denied_without_mutation(self):
        cb = load_context_binding()
        for received in ("foreign-challenge", "stale-challenge"):
            with self.subTest(received=received):
                pending = {"bootstrap_challenge_id": CHALLENGE, "consumed": False, "stale": received == "stale-challenge"}
                result = cb.verify_bootstrap_challenge(
                    {"instruction_type": "PROJECT_CONTEXT_BOOTSTRAP", "bootstrap_challenge_id": received},
                    pending,
                )
                self.assertEqual(result.decision, "DENY")
                self.assertFalse(result.current_project_mutation)

    def test_bootstrap_is_idempotent_and_does_not_regenerate_identity(self):
        cb = load_context_binding()
        control = {"project_name": "Example Project", "project_context_id": VALID_ID}
        self.assertEqual(cb.bootstrap_project_context(control, "Example Project")["project_context_id"], VALID_ID)
        generated = cb.bootstrap_project_context({"project_name": "Example Project"}, "Example Project", id_factory=lambda: VALID_ID)
        self.assertEqual(generated["project_context_id"], VALID_ID)


if __name__ == "__main__":
    unittest.main()
