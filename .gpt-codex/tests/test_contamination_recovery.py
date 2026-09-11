import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_context_binding():
    path = ROOT / "scripts" / "context_binding.py"
    if not path.is_file():
        raise AssertionError("context_binding.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("context_binding_recovery_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ContaminationRecoveryTests(unittest.TestCase):
    def test_chat_only_contamination_recovers_logical_context_without_rollback(self):
        cb = load_context_binding()
        result = cb.recover_contamination("CHAT_ONLY_CONTAMINATION")
        self.assertEqual(result["status"], "CONTEXT_CONTAMINATION_DETECTED")
        self.assertEqual(result["recovery"], "LAST_VALID_PROJECT_CONTEXT")
        self.assertFalse(result["audit_required"])
        self.assertFalse(result["destructive_rollback"])

    def test_repository_mutation_possible_requires_read_only_audit(self):
        cb = load_context_binding()
        result = cb.recover_contamination("REPOSITORY_MUTATION_POSSIBLE")
        self.assertTrue(result["audit_required"])
        self.assertEqual(result["audit_mode"], "READ_ONLY_CONTAMINATION_AUDIT")
        self.assertFalse(result["destructive_rollback"])

    def test_clean_baseline_returns_to_trusted_context(self):
        cb = load_context_binding()
        result = cb.recover_contamination("REPOSITORY_MUTATION_POSSIBLE", baseline_confirmed=True)
        self.assertEqual(result["recovery"], "LAST_VALID_PROJECT_CONTEXT")
        self.assertTrue(result["baseline_confirmed"])


if __name__ == "__main__":
    unittest.main()
