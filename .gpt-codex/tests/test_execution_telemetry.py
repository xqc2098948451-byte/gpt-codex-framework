import importlib.util
import sys
import unittest
from dataclasses import fields
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
LATER = datetime(2026, 9, 14, 0, 1, tzinfo=timezone.utc)


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


def low_confidence_fallback_payload(**overrides):
    payload = valid_payload(
        event_class="REMOTE_EVIDENCE_OBSERVED",
        result_id=None,
        authoritative_record_ref=None,
        provenance={
            "classification": "DERIVED",
            "source_channel": "remote-evidence",
            "source_record_refs": [],
            "observed_state_revision": 3,
            "observed_head_sha": "b" * 40,
            "redaction_actions": [],
            "completeness": "LOW_CONFIDENCE",
            "producer_run_id": "run-1",
            "producer_sequence": 0,
        },
    )
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

    def test_slot_id_and_source_are_required_non_empty_strings(self):
        module = load_module()
        for field in ("slot_id", "source"):
            for value in (None, "", 7):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(module.TelemetryValidationError, "MALFORMED_TELEMETRY_EVENT"):
                    module.normalize_event(valid_payload(**{field: value}), collector_id="collector", collector_version="1.0", timestamp=NOW)
        event = module.normalize_event(valid_payload(slot_id="NONE"), collector_id="collector", collector_version="1.0", timestamp=NOW)
        self.assertEqual(event.slot_id, "NONE")

    def test_low_confidence_fallback_requires_complete_producer_identity(self):
        module = load_module()
        fallback = low_confidence_fallback_payload()
        event = module.normalize_event(fallback, collector_id="collector", collector_version="1.0", timestamp=NOW)
        self.assertIsNone(module.correlation_ref_for(event))
        self.assertTrue(event.logical_key)
        for field, value in (("producer_run_id", None), ("producer_sequence", None)):
            invalid = low_confidence_fallback_payload()
            invalid["provenance"] = dict(invalid["provenance"])
            invalid["provenance"][field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(module.TelemetryValidationError, "INVALID_TELEMETRY_PROVENANCE"):
                module.normalize_event(invalid, collector_id="collector", collector_version="1.0", timestamp=NOW)
        for field in ("producer_run_id", "producer_sequence"):
            invalid = low_confidence_fallback_payload()
            invalid["provenance"] = dict(invalid["provenance"])
            invalid["provenance"].pop(field)
            with self.subTest(field=field, value="missing"), self.assertRaisesRegex(module.TelemetryValidationError, "INVALID_TELEMETRY_PROVENANCE"):
                module.normalize_event(invalid, collector_id="collector", collector_version="1.0", timestamp=NOW)
        for value in (-1, "3"):
            invalid = low_confidence_fallback_payload()
            invalid["provenance"] = dict(invalid["provenance"])
            invalid["provenance"]["producer_sequence"] = value
            with self.subTest(sequence=value), self.assertRaisesRegex(module.TelemetryValidationError, "INVALID_TELEMETRY_PROVENANCE"):
                module.normalize_event(invalid, collector_id="collector", collector_version="1.0", timestamp=NOW)


def normalized_event(module, **overrides):
    values = dict(overrides)
    timestamp = values.pop("timestamp", NOW)
    return module.normalize_event(valid_payload(**values), collector_id="collector", collector_version="1.0", timestamp=timestamp)


def normalized_fallback_event(module, **overrides):
    values = dict(overrides)
    timestamp = values.pop("timestamp", NOW)
    return module.normalize_event(low_confidence_fallback_payload(**values), collector_id="collector", collector_version="1.0", timestamp=timestamp)


class ExecutionTelemetryTaskThreeTests(unittest.TestCase):
    def test_collector_deduplicates_retries_and_appends_cross_source_repeat(self):
        module = load_module()
        collector = module.TelemetryCollector()
        first = collector.emit(normalized_event(module))
        retry = collector.emit(normalized_event(module))
        repeat = collector.emit(normalized_event(module, source="remote-evidence-read", timestamp=LATER))
        self.assertEqual(retry.event_id, first.event_id)
        self.assertEqual(repeat.observation_kind, "REPEAT")
        self.assertEqual(repeat.repeats_event_id, first.event_id)
        self.assertEqual(len(collector.events()), 2)

    def test_ordering_precedence_stale_outranks_out_of_order(self):
        module = load_module()
        previous = normalized_event(module, state_revision=3, timestamp=LATER)
        snapshot = module.AuthoritativeSnapshot("ctx-1", 3, None, "result-1", None)
        event = normalized_event(module, state_revision=2, timestamp=NOW)
        self.assertEqual(module.classify_ordering(event, authoritative=snapshot, previous_related_event=previous), "STALE")
        self.assertEqual(module.classify_ordering(event, authoritative=None, previous_related_event=previous), "OUT_OF_ORDER")

    def test_low_confidence_sequence_identity_and_repeat_subject_enable_out_of_order(self):
        module = load_module()
        collector = module.TelemetryCollector()
        first = collector.emit(normalized_event(module, **low_confidence_fallback_payload(
            provenance={**low_confidence_fallback_payload()["provenance"], "producer_sequence": 5},
        )))
        second = collector.emit(normalized_event(module, **low_confidence_fallback_payload(
            provenance={**low_confidence_fallback_payload()["provenance"], "producer_sequence": 3},
        )))
        self.assertNotEqual(first.logical_key, second.logical_key)
        self.assertEqual(module.repeat_subject_key(first), module.repeat_subject_key(second))
        self.assertEqual(second.ordering_status, "OUT_OF_ORDER")

    def test_repeat_lineage_uses_earliest_and_chronology_uses_latest(self):
        module = load_module()
        collector = module.TelemetryCollector()
        first = collector.emit(normalized_event(module, timestamp=NOW))
        second = collector.emit(normalized_event(module, source="remote-evidence-read", timestamp=LATER))
        third = collector.emit(normalized_event(module, source="reviewer-read", timestamp=NOW))
        self.assertEqual(third.repeats_event_id, first.event_id)
        self.assertEqual(third.ordering_status, "LATE")
        self.assertEqual(len(collector.events()), 3)

    def test_snapshot_has_only_result_status_and_compares_matching_result_status(self):
        module = load_module()
        self.assertNotIn("publication_status", {field.name for field in fields(module.AuthoritativeSnapshot)})
        snapshot = module.AuthoritativeSnapshot("ctx-1", 3, None, "result-1", "FAIL")
        event = normalized_event(module, result_status="PASS")
        self.assertEqual(module.classify_ordering(event, authoritative=snapshot, previous_related_event=None), "INCONSISTENT")

    def test_result_status_inconsistency_requires_matching_non_null_correlation(self):
        module = load_module()
        cases = (
            ("both_absent", None, normalized_fallback_event(module, result_status="PASS"), "CURRENT"),
            ("authoritative_absent", None, normalized_event(module, result_id="result-1", result_status="PASS"), "CURRENT"),
            ("event_absent", "result-1", normalized_fallback_event(module, result_status="PASS"), "CURRENT"),
            ("different_non_null", "result-1", normalized_event(module, result_id="result-2", result_status="PASS"), "CURRENT"),
            ("matching_non_null", "result-1", normalized_event(module, result_id="result-1", result_status="PASS"), "INCONSISTENT"),
        )
        for name, correlation_ref, event, expected in cases:
            snapshot = module.AuthoritativeSnapshot("ctx-1", 3, None, correlation_ref, "FAIL")
            with self.subTest(name=name):
                self.assertEqual(module.classify_ordering(event, authoritative=snapshot, previous_related_event=None), expected)

    def test_publication_event_remains_valid_and_out_of_order_outranks_late(self):
        module = load_module()
        publication = normalized_event(module, event_class="PUBLICATION_BOUNDARY_TRANSITION", authoritative_record_ref="publication-1", result_id=None)
        self.assertEqual(publication.event_class, "PUBLICATION_BOUNDARY_TRANSITION")
        previous = normalized_event(module, state_revision=3, timestamp=LATER)
        event = normalized_event(module, state_revision=2, timestamp=NOW)
        self.assertEqual(module.classify_ordering(event, authoritative=None, previous_related_event=previous), "OUT_OF_ORDER")


if __name__ == "__main__":
    unittest.main()
