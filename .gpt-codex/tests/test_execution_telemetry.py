import importlib.util
import sys
import unittest
from datetime import datetime, timezone
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
    sys.modules[spec.name] = module
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


NOW = datetime(2026, 9, 14, tzinfo=timezone.utc)


def valid_payload(**overrides):
    payload = {
        "event_class": "EXECUTION_COMPLETED",
        "work_unit_id": "WU-1",
        "slot_id": "NONE",
        "role": "CODEX_IMPLEMENTER",
        "state_revision": 3,
        "project_context_id": "ctx-1",
        "branch_ref": "feature/example",
        "base_sha": "a" * 40,
        "head_sha": "b" * 40,
        "result_status": "PASS",
        "review_gate": "IMPLEMENTATION",
        "evidence_refs": ["result:1"],
        "source": "result-envelope",
        "provenance": {
            "classification": "DERIVED",
            "source_channel": "result-envelope",
            "source_record_refs": ["result:1"],
            "observed_state_revision": 3,
            "observed_head_sha": "b" * 40,
            "redaction_actions": [],
            "completeness": "COMPLETE",
        },
        "result_id": "result-1",
    }
    payload.update(overrides)
    return payload


class ExecutionTelemetryTaskTwoTests(unittest.TestCase):
    def test_normalization_creates_immutable_derived_event_and_deterministic_key(self):
        module = load_module()
        raw = valid_payload()
        event = module.normalize_event(raw, collector_id="collector", collector_version="1.0", timestamp=NOW)
        self.assertEqual(event.provenance.classification, "DERIVED")
        self.assertIsInstance(event.evidence_refs, tuple)
        self.assertIsInstance(event.provenance.source_record_refs, tuple)
        self.assertEqual(event.logical_key, module.logical_idempotency_key(event))
        self.assertEqual(module.correlation_ref_for(event), "result-1")
        raw["provenance"]["source_record_refs"].append("result:2")
        self.assertEqual(event.provenance.source_record_refs, ("result:1",))

    def test_normalization_rejects_authority_and_sensitive_fields_but_allows_status(self):
        module = load_module()
        event = module.normalize_event(valid_payload(result_status="PASS"), collector_id="collector", collector_version="1.0", timestamp=NOW)
        self.assertEqual(event.result_status, "PASS")
        for key, error in (("authority_claim", "PROHIBITED_AUTHORITY_CLAIM"), ("raw_prompt", "UNSAFE_TELEMETRY_CONTENT")):
            with self.subTest(key=key), self.assertRaisesRegex(module.TelemetryValidationError, error):
                module.normalize_event(valid_payload(**{key: "value"}), collector_id="collector", collector_version="1.0", timestamp=NOW)


if __name__ == "__main__":
    unittest.main()
