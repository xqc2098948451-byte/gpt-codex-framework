import json
from itertools import combinations
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from test_continuity_resume import RepositoryHandoffBindingTests


class FrameworkPluginResumeTests(unittest.TestCase):
    def test_slotless_baseline_needs_no_handoff_bindings(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, _, _ = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_resume(root, "repo-a")
        self.assertEqual(result["status"], "PLUGIN_RESUME_READY")
        self.assertEqual(result["state_revision"], 4)
        self.assertNotIn("result_ref", result)
        self.assertNotIn("next_authorized_action", result)

    def test_partial_bindings_reconcile_without_inference(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, _, _ = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_resume(root, "repo-a", target_work_unit_id="new-work-unit")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_explicit_slotless_bindings_produce_result_handoff(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_resume(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref=work_ref, instruction_locator=locator,
                expected_state_revision=4,
            )
        self.assertEqual(result["status"], "PLUGIN_RESUME_READY")
        self.assertEqual(result["result_ref"], ".gpt-codex/evidence/results/fixture-result.json")
        self.assertNotIn("next_authorized_action", result)


class FrameworkPluginClassificationRegressionTests(unittest.TestCase):
    """Lock the observable P2 adapter contract used by E2 classification."""

    @staticmethod
    def _bindings(work_ref, locator):
        return {
            "target_work_unit_id": "new-work-unit",
            "target_work_unit_ref": work_ref,
            "instruction_locator": locator,
            "expected_state_revision": 4,
        }

    def assert_reconciliation(self, result):
        self.assertIs(type(result), dict)
        self.assertEqual(result, {"status": "RECONCILIATION_REQUIRED",
                                  "reconciliation_required": True})

    def test_slotless_synced_baseline_has_only_context_projection(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, _, _ = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_resume(root, "repo-a")
        self.assertEqual(result["status"], "PLUGIN_RESUME_READY")
        self.assertIs(result["reconciliation_required"], False)
        self.assertEqual(result["repository_id"], "repo-a")
        self.assertEqual(result["state_revision"], 4)
        self.assertEqual(set(result), {
            "status", "reconciliation_required", "project_id", "project_context_id",
            "repository_id", "repository", "state_revision", "state",
            "active_work_unit", "verified_baseline_sha", "next_action_hint",
            "remote_reverification_required",
        })
        for handoff_only in ("current_work", "instruction_id", "instruction_locator",
                             "result_id", "result_ref", "evidence_refs", "git",
                             "result_status", "blockers", "compact_return",
                             "next_authorized_action"):
            self.assertNotIn(handoff_only, result)

    def test_execution_slot_without_handoff_bindings_reconciles(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, _, _ = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_resume(root, "repo-a", "slot-1")
        self.assert_reconciliation(result)

    def test_every_proper_nonempty_binding_subset_reconciles_without_inference(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            bindings = self._bindings(work_ref, locator)
            for size in (1, 2, 3):
                for names in combinations(bindings, size):
                    with self.subTest(bindings=names):
                        result = build_plugin_resume(
                            root, "repo-a", **{name: bindings[name] for name in names})
                        self.assert_reconciliation(result)

    def test_complete_bindings_project_native_handoff_without_new_authority(self):
        from continuity_resume import build_repository_handoff
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            bindings = self._bindings(work_ref, locator)
            native = build_repository_handoff(root, "repo-a", **bindings)
            result = build_plugin_resume(root, "repo-a", **bindings)
        self.assertEqual(native["status"], "HANDOFF_READY")
        self.assertEqual(result["status"], "PLUGIN_RESUME_READY")
        self.assertIs(result["reconciliation_required"], False)
        self.assertEqual(set(result), {
            "status", "reconciliation_required", "project_id", "project_context_id",
            "repository_id", "repository", "state_revision", "state", "current_work",
            "instruction_id", "instruction_locator", "result_id", "result_ref",
            "evidence_refs", "git", "result_status", "blockers", "next_action_hint",
        })
        self.assertEqual(result["current_work"], native["current_work"])
        self.assertEqual(result["result_id"], native["result_id"])
        self.assertEqual(result["result_ref"], native["result_ref"])
        self.assertEqual(result["git"], native["git"])
        self.assertNotIn("next_authorized_action", result)

    def test_stale_foreign_invalid_and_native_failure_bindings_reconcile(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            bindings = self._bindings(work_ref, locator)
            cases = (
                ("wrong revision", "repo-a", {**bindings, "expected_state_revision": 5}),
                ("foreign repository", "repo-b", bindings),
                ("invalid repository", None, bindings),
                ("native handoff not ready", "repo-a", {
                    **bindings, "instruction_locator": {**locator, "blob_sha": "f" * 40}}),
            )
            for name, repository, fields in cases:
                with self.subTest(case=name):
                    self.assert_reconciliation(build_plugin_resume(root, repository, **fields))

    def test_execution_slot_requires_native_current_work_match(self):
        from framework_plugin_entry import build_plugin_resume

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(
                Path(td), with_slot=True)
            bindings = self._bindings(work_ref, locator)
            matching = build_plugin_resume(root, "repo-a", "slot-1", **bindings)
            mismatching = build_plugin_resume(root, "repo-a", "slot-X", **bindings)
        self.assertEqual(matching["status"], "PLUGIN_RESUME_READY")
        self.assertEqual(matching["current_work"]["execution_slot_id"], "slot-1")
        self.assertEqual(matching["result_id"], "fixture-result")
        self.assert_reconciliation(mismatching)

    def test_result_handoff_each_missing_binding_reconciles(self):
        from framework_plugin_entry import build_plugin_result_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            bindings = self._bindings(work_ref, locator)
            for missing in bindings:
                with self.subTest(missing=missing):
                    fields = {key: value for key, value in bindings.items() if key != missing}
                    self.assert_reconciliation(
                        build_plugin_result_handoff(root, "repo-a", **fields))

    def test_result_handoff_native_result_has_compact_return_and_exact_shape(self):
        from framework_plugin_entry import build_plugin_result_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_result_handoff(
                root, "repo-a", **self._bindings(work_ref, locator))
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertIs(result["reconciliation_required"], False)
        self.assertEqual(result["result_id"], "fixture-result")
        self.assertEqual(result["result_ref"],
                         ".gpt-codex/evidence/results/fixture-result.json")
        self.assertEqual(result["current_work"]["work_unit_id"], "new-work-unit")
        self.assertIn("RESULT_REF: fixture-result", result["compact_return"])
        self.assertEqual(set(result), {
            "status", "reconciliation_required", "project_id", "project_context_id",
            "repository_id", "repository", "state_revision", "state", "current_work",
            "instruction_id", "instruction_locator", "result_id", "result_ref",
            "evidence_refs", "git", "result_status", "blockers", "next_action_hint",
            "compact_return",
        })
        self.assertNotIn("next_authorized_action", result)

    def test_result_handoff_reconciles_native_failure_and_missing_result_id(self):
        from framework_plugin_entry import build_plugin_result_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            bindings = self._bindings(work_ref, locator)
            self.assert_reconciliation(build_plugin_result_handoff(
                root, "repo-a", **{**bindings, "expected_state_revision": 5}))
            with patch("framework_plugin_entry.build_plugin_resume",
                       return_value={"status": "PLUGIN_RESUME_READY"}):
                self.assert_reconciliation(
                    build_plugin_result_handoff(root, "repo-a", **bindings))

    def test_load_failure_shapes_across_baseline_consumers(self):
        from framework_plugin_entry import (
            build_plugin_resume, request_validation_access,
            validate_plugin_capability_request, route_plugin_feedback,
        )

        with patch("framework_plugin_entry.load_continuity_resume",
                   side_effect=ValueError("load failed")):
            self.assert_reconciliation(build_plugin_resume(Path("."), "repo-a"))
            self.assert_reconciliation(request_validation_access(
                Path("."), "repo-a", instruction_locator={}, current_state_revision=4))
            for capability in ("CONTEXT_ACCESS", "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST"):
                self.assertEqual(validate_plugin_capability_request(
                    Path("."), "repo-a", capability), ["RECONCILIATION_REQUIRED"])
            self.assert_reconciliation(route_plugin_feedback(
                Path("."), "repo-a", {}, source_binding={}, instruction_locator={}))

    def test_malformed_baseline_preserves_distinct_error_shapes(self):
        from framework_plugin_entry import (
            build_plugin_resume, request_validation_access,
            validate_plugin_capability_request, route_plugin_feedback,
        )

        for baseline in (None, []):
            with self.subTest(baseline=baseline), patch(
                    "framework_plugin_entry.load_continuity_resume", return_value=baseline):
                with self.assertRaises(AttributeError):
                    build_plugin_resume(Path("."), "repo-a")
                with self.assertRaises(AttributeError):
                    validate_plugin_capability_request(Path("."), "repo-a", "CONTEXT_ACCESS")
                self.assert_reconciliation(request_validation_access(
                    Path("."), "repo-a", instruction_locator={}, current_state_revision=4))
                self.assert_reconciliation(route_plugin_feedback(
                    Path("."), "repo-a", {}, source_binding={}, instruction_locator={}))
        with patch("framework_plugin_entry.load_continuity_resume",
                   return_value={"status": "LATEST_SYNCED_REMOTE_STATE"}):
            with self.assertRaises(KeyError):
                build_plugin_resume(Path("."), "repo-a")
            self.assertEqual(validate_plugin_capability_request(
                Path("."), "repo-a", "CONTEXT_ACCESS"), [])
            self.assert_reconciliation(request_validation_access(
                Path("."), "repo-a", instruction_locator={}, current_state_revision=4))
            self.assert_reconciliation(route_plugin_feedback(
                Path("."), "repo-a", {}, source_binding={}, instruction_locator={}))

    def test_non_latest_baseline_keeps_each_consumer_status(self):
        from framework_plugin_entry import (
            build_plugin_resume, request_validation_access,
            validate_plugin_capability_request, route_plugin_feedback,
        )

        baseline = {
            "status": "STALE_REMOTE_STATE",
            "control": {"github": {"repository_full_name": "owner/a"},
                        "project_id": "P", "project_context_id": "context-a"},
            "state": {"revision": 4},
        }
        with patch("framework_plugin_entry.load_continuity_resume", return_value=baseline), \
             patch("framework_plugin_entry.resolve_durable_instruction",
                   return_value={"status": "INSTRUCTION_RESOLVED"}):
            self.assert_reconciliation(build_plugin_resume(Path("."), "repo-a"))
            self.assertEqual(request_validation_access(
                Path("."), "repo-a", instruction_locator={}, current_state_revision=4),
                {"status": "VALIDATION_RESULT", "validation_status": "INSTRUCTION_RESOLVED",
                 "findings": []})
            for capability in ("CONTEXT_ACCESS", "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST"):
                self.assertEqual(validate_plugin_capability_request(
                    Path("."), "repo-a", capability), ["RECONCILIATION_REQUIRED"])
            self.assert_reconciliation(route_plugin_feedback(
                Path("."), "repo-a", {}, source_binding={}, instruction_locator={}))
        with patch("framework_plugin_entry.load_continuity_resume", return_value=baseline), \
             patch("framework_plugin_entry.resolve_durable_instruction",
                   return_value={"status": "RECONCILIATION_REQUIRED"}):
            self.assertEqual(request_validation_access(
                Path("."), "repo-a", instruction_locator={}, current_state_revision=4),
                {"status": "VALIDATION_RESULT", "validation_status": "RECONCILIATION_REQUIRED",
                 "findings": ["RECONCILIATION_REQUIRED"]})

class FrameworkPluginInstructionTests(unittest.TestCase):
    def test_instruction_path_is_deterministic_and_rejects_invalid_id(self):
        from framework_plugin_entry import instruction_artifact_relative_path

        self.assertEqual(
            instruction_artifact_relative_path("22222222-2222-4222-8222-222222222222"),
            ".gpt-codex/evidence/instructions/22222222-2222-4222-8222-222222222222.json",
        )
        with self.assertRaises(ValueError):
            instruction_artifact_relative_path("../other")

    def test_canonical_instruction_bytes_are_stable(self):
        from framework_plugin_entry import canonical_instruction_bytes

        self.assertEqual(canonical_instruction_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}\n')

    def test_exact_locator_resolves_instruction_bindings(self):
        from framework_plugin_entry import resolve_plugin_instruction

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            subprocess.run(["git", "-C", str(root), "remote", "set-url", "origin",
                            "https://github.com/owner/a.git"], check=True, capture_output=True)
            result = resolve_plugin_instruction(
                root, locator, "owner/a", current_state_revision=4,
                approved_scope={"src/a"},
            )
        self.assertEqual(result["status"], "INSTRUCTION_RESOLVED")
        self.assertEqual(result["target_work_unit_id"], "new-work-unit")
        self.assertEqual(result["target_work_unit_ref"], work_ref)
        self.assertEqual(result["instruction_locator"], locator)


class FrameworkPluginResultTests(unittest.TestCase):
    def test_result_handoff_requires_all_bindings(self):
        from framework_plugin_entry import build_plugin_result_handoff

        with tempfile.TemporaryDirectory() as td:
            root, _, _ = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_result_handoff(root, "repo-a")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_result_handoff_is_derived_from_exact_native_result(self):
        from framework_plugin_entry import build_plugin_result_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = build_plugin_result_handoff(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref=work_ref, instruction_locator=locator,
                expected_state_revision=4,
            )
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertIn("RESULT_REF: fixture-result", result["compact_return"])
        self.assertEqual(result["current_work"]["status"], "AUTHORIZED")
        self.assertEqual(result["result_status"], "PASS")
        self.assertNotIn("next_authorized_action", result)


class FrameworkPluginCapabilityTests(unittest.TestCase):
    def test_capability_names_are_exact_and_unknown_is_denied(self):
        from framework_plugin_entry import P2_CAPABILITIES, validate_plugin_capability_request

        self.assertEqual(P2_CAPABILITIES, (
            "CONTEXT_ACCESS", "VALIDATION_ACCESS", "EVIDENCE_FEEDBACK_ROUTING",
            "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST",
        ))
        self.assertIn("UNSUPPORTED_CAPABILITY", validate_plugin_capability_request(
            Path("."), "repo-a", "PUBLISH",
        ))

    def test_executable_request_without_pre_review_is_denied_by_core(self):
        from framework_plugin_entry import validate_plugin_capability_request

        with tempfile.TemporaryDirectory() as td:
            root, _, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            errors = validate_plugin_capability_request(
                root, "repo-a", "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST",
                instruction_locator=locator, current_state_revision=4,
                requested_action="MUTATE_APPROVED_SCOPE",
            )
        self.assertTrue(errors)
        self.assertNotIn("UNSUPPORTED_CAPABILITY", errors)

    def test_validation_access_does_not_claim_completion(self):
        from framework_plugin_entry import request_validation_access

        with tempfile.TemporaryDirectory() as td:
            root, _, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            result = request_validation_access(
                root, "repo-a", instruction_locator=locator,
                current_state_revision=4,
            )
        self.assertEqual(result["status"], "VALIDATION_RESULT")
        self.assertNotIn("complete", result)


class FrameworkPluginFeedbackTests(unittest.TestCase):
    def test_feedback_routes_only_from_bound_project_evidence(self):
        from framework_plugin_entry import route_plugin_feedback

        feedback = {
            "problem": "handoff friction", "reason": "manual read",
            "local_solution": "explicit resume", "result": "observed",
            "framework_change_recommended": False,
            "evidence_refs": [".gpt-codex/evidence/fixture-evidence.json"],
        }
        with tempfile.TemporaryDirectory() as td:
            root, _, locator = RepositoryHandoffBindingTests()._durable_fixture(Path(td))
            subprocess.run(["git", "-C", str(root), "remote", "set-url", "origin",
                            "https://github.com/owner/a.git"], check=True, capture_output=True)
            valid = route_plugin_feedback(
                root, "repo-a", feedback,
                source_binding={"project_id": "P", "project_context_id":
                                "11111111-1111-4111-8111-111111111111",
                                "work_unit_id": "new-work-unit", "state_revision": 4,
                                "instruction_id": "22222222-2222-4222-8222-222222222222",
                                "provenance": "PROJECT_EVIDENCE"},
                instruction_locator=locator,
            )
            foreign = route_plugin_feedback(
                root, "repo-a", feedback,
                source_binding={"project_id": "FOREIGN", "project_context_id":
                                "11111111-1111-4111-8111-111111111111",
                                "work_unit_id": "new-work-unit", "state_revision": 4,
                                "instruction_id": "22222222-2222-4222-8222-222222222222",
                                "provenance": "PROJECT_EVIDENCE"},
                instruction_locator=locator,
            )
        self.assertEqual(valid["status"], "FEEDBACK_ROUTED")
        self.assertEqual(foreign["status"], "RECONCILIATION_REQUIRED")
        self.assertNotIn("authorization", valid)

    def test_marker_change_is_only_a_resume_signal(self):
        from framework_plugin_entry import durable_authority_marker, detect_durable_authority_change

        baseline = {"status": "PLUGIN_RESUME_READY", "repository_id": "repo-a",
                    "state_revision": 4, "verified_baseline_sha": "a" * 40}
        before = durable_authority_marker(baseline)
        after = durable_authority_marker({**baseline, "state_revision": 5})
        self.assertFalse(detect_durable_authority_change(before, before))
        self.assertTrue(detect_durable_authority_change(before, after))


if __name__ == "__main__":
    unittest.main()
