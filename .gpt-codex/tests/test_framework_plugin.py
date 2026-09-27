import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
