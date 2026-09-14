import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from framework_module_routing import classify_changed_assets, load_registry  # noqa: E402


def load_module():
    path = SCRIPTS / "execution_telemetry.py"
    spec = importlib.util.spec_from_file_location("execution_telemetry_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExecutionTelemetryTaskOneTests(unittest.TestCase):
    def test_framework_core_owns_telemetry_paths_and_vocabulary_is_closed(self):
        module = load_module()
        assets = [
            ".gpt-codex/scripts/execution_telemetry.py",
            ".gpt-codex/tests/test_execution_telemetry.py",
        ]
        owners = classify_changed_assets(ROOT, load_registry(ROOT), assets)
        self.assertEqual(owners[assets[0]], ("framework-core",))
        self.assertEqual(owners[assets[1]], ("framework-core",))
        self.assertEqual(module.TELEMETRY_CLASSIFICATION, "DERIVED_OBSERVATION_ONLY")
        self.assertEqual(module.EVENT_CLASSES, frozenset({
            "INSTRUCTION_ISSUED", "SLOT_ASSIGNED", "SLOT_REASSIGNED",
            "EXECUTION_STARTED", "EXECUTION_COMPLETED", "EXECUTION_BLOCKED",
            "REVIEW_REQUESTED", "REVIEW_RESULT", "FINDING_CREATED",
            "REMEDIATION_AUTHORIZED", "RE_REVIEW_RESULT",
            "REMOTE_EVIDENCE_OBSERVED", "PUBLICATION_BOUNDARY_TRANSITION",
        }))


if __name__ == "__main__":
    unittest.main()
