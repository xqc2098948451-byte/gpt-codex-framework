import importlib.util
import inspect
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALID_ID = "11111111-1111-4111-8111-111111111111"
VALID_SHA = "a" * 40


def load_instruction_envelope():
    path = ROOT / "scripts" / "instruction_envelope.py"
    spec = importlib.util.spec_from_file_location("instruction_envelope_roles_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionRoleContractTests(unittest.TestCase):
    def modern_kwargs(self):
        return {
            "issuer_role": "GPT_ORCHESTRATOR",
            "executor_role": "CODEX_IMPLEMENTER",
            "return_role": "GPT_ORCHESTRATOR",
            "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": ["PUBLISH"],
            "evidence_requirements": {
                "files_read": [".gpt-codex/CONTROL.json"],
                "files_changed": [".gpt-codex/scripts/example.py"],
                "tests": ["python -m unittest"],
                "validation": ["framework", "project"],
                "revision": True,
                "result_references": [VALID_ID],
            },
            "completion_gate": "GPT_DECISION",
            "in_response_to_instruction_id": VALID_ID,
            "in_response_to_result_id": VALID_ID,
            "review_target_revision": VALID_SHA,
            "finding_ids": ["RCP-001"],
            "fix_round": 1,
            "artifact_stage": "IMPLEMENTATION",
            "scope_paths": [".gpt-codex/scripts/example.py"],
        }

    def build(self, **overrides):
        ie = load_instruction_envelope()
        kwargs = self.modern_kwargs()
        kwargs.update(overrides)
        return ie.build_instruction_envelope(
            instruction_type="EXECUTION_INSTRUCTION",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.4.0",
            target_work_unit="WU-001",
            **kwargs,
        )

    def test_schema_and_template_expose_only_instruction_side_contract(self):
        schema = json.loads((ROOT / "schemas" / "instruction-envelope.schema.json").read_text(encoding="utf-8"))
        template = json.loads((ROOT / "project-template" / "INSTRUCTION_ENVELOPE.template.json").read_text(encoding="utf-8"))
        expected = {
            "issuer_role", "executor_role", "return_role", "authorized_actions",
            "forbidden_actions", "evidence_requirements", "completion_gate",
            "in_response_to_instruction_id", "in_response_to_result_id",
            "review_target_revision", "finding_ids", "fix_round", "artifact_stage",
            "scope_paths", "remediation_decision_ref", "approval_evidence_ref",
        }
        self.assertTrue(expected.issubset(schema["properties"]))
        self.assertTrue(expected.issubset(template))
        self.assertNotIn("message_type", schema["properties"])
        self.assertNotIn("result_message_type", schema["properties"])
        locator = schema["properties"]["approval_evidence_ref"]
        self.assertFalse(locator["additionalProperties"])
        self.assertEqual(locator["required"], ["remote_ref", "evidence_commit_sha", "path", "blob_sha"])
        self.assertEqual(
            schema["properties"]["instruction_type"]["enum"],
            [
                "EXECUTION_INSTRUCTION", "REVIEW_REQUEST", "FIX_INSTRUCTION",
                "APPROVAL_REQUEST", "RECONCILIATION_REQUEST", "INFORMATION_ONLY",
                "PROJECT_CONTEXT_BOOTSTRAP", "WORK_UNIT", "IMPLEMENTATION",
            ],
        )

    def test_builder_serializes_supplied_role_action_evidence_and_correlation_fields(self):
        envelope = self.build()
        for key, value in self.modern_kwargs().items():
            self.assertEqual(envelope[key], value)
        self.assertNotIn("message_type", envelope)
        self.assertNotIn("result_message_type", envelope)

    def test_renderer_emits_instruction_type_and_role_fields_once(self):
        ie = load_instruction_envelope()
        rendered = ie.render_codex_instruction(
            self.build(),
            "Run the authorized task body.",
            {"execution_strategy": "serial", "approval": "GPT decision"},
        )
        self.assertEqual(rendered.count("INSTRUCTION_TYPE:"), 1)
        self.assertNotIn("MESSAGE_TYPE:", rendered)
        self.assertNotIn("RESULT_MESSAGE_TYPE:", rendered)
        self.assertIn("EXECUTOR_ROLE: CODEX_IMPLEMENTER", rendered)
        self.assertIn("AUTHORIZED_ACTIONS: READ, TEST, VALIDATE, REPORT, MUTATE_APPROVED_SCOPE", rendered)
        self.assertIn("REVIEW_TARGET_REVISION: " + VALID_SHA, rendered)

    def test_result_side_types_are_rejected_from_instruction_builder(self):
        ie = load_instruction_envelope()
        with self.assertRaisesRegex(ValueError, "RESULT_TYPE_NOT_ALLOWED_AS_INSTRUCTION"):
            ie.build_instruction_envelope(
                instruction_type="REVIEW_FINDING",
                target_project_context_id=VALID_ID,
                target_project_name="Example Project",
                expected_state_revision=7,
                framework_version="2.4.0",
                executor_role="CODEX_IMPLEMENTER",
            )

    def test_modern_instructions_require_one_scalar_known_executor(self):
        ie = load_instruction_envelope()
        base = {
            "instruction_type": "EXECUTION_INSTRUCTION",
            "target_project_context_id": VALID_ID,
            "target_project_name": "Example Project",
            "expected_state_revision": 7,
            "framework_version": "2.4.0",
        }
        for value, error in (
            (None, "EXECUTOR_REQUIRED"),
            (["CODEX_IMPLEMENTER", "CODEX_REVIEWER"], "EXECUTOR_MUST_BE_SCALAR"),
            ("CODEX_IMPLEMENTER,CODEX_REVIEWER", "EXECUTOR_MUST_BE_SCALAR"),
            ("AGENT", "UNKNOWN_EXECUTOR_ROLE"),
        ):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, error):
                ie.build_instruction_envelope(**base, executor_role=value)

    def test_action_authority_and_correlation_bounds_fail_closed(self):
        ie = load_instruction_envelope()
        base = {
            "instruction_type": "EXECUTION_INSTRUCTION",
            "target_project_context_id": VALID_ID,
            "target_project_name": "Example Project",
            "expected_state_revision": 7,
            "framework_version": "2.4.0",
            "issuer_role": "GPT_ORCHESTRATOR",
            "executor_role": "CODEX_REVIEWER",
            "return_role": "GPT_ORCHESTRATOR",
        }
        with self.assertRaisesRegex(ValueError, "ACTION_NOT_ALLOWED_FOR_ROLE"):
            ie.build_instruction_envelope(**base, authorized_actions=["MUTATE_APPROVED_SCOPE"])
        with self.assertRaisesRegex(ValueError, "ACTION_IN_AUTHORIZED_AND_FORBIDDEN"):
            ie.build_instruction_envelope(**base, authorized_actions=["READ"], forbidden_actions=["READ"])
        with self.assertRaisesRegex(ValueError, "INVALID_CORRELATION"):
            ie.build_instruction_envelope(**base, in_response_to_instruction_id="not-a-uuid")

        with self.assertRaisesRegex(ValueError, "INVALID_ACTIONS_SHAPE"):
            ie.build_instruction_envelope(**base, authorized_actions="READ")

    def test_new_instructions_require_issuer_and_return_roles(self):
        ie = load_instruction_envelope()
        base = {
            "instruction_type": "EXECUTION_INSTRUCTION",
            "target_project_context_id": VALID_ID,
            "target_project_name": "Example Project",
            "expected_state_revision": 7,
            "framework_version": "2.4.0",
            "executor_role": "CODEX_IMPLEMENTER",
            "issuer_role": "GPT_ORCHESTRATOR",
            "return_role": "GPT_ORCHESTRATOR",
        }
        for field in ("issuer_role", "return_role"):
            with self.subTest(field=field):
                value = dict(base)
                value.pop(field)
                with self.assertRaisesRegex(ValueError, f"{field.upper()}_REQUIRED"):
                    ie.build_instruction_envelope(**value)

    def test_bounded_legacy_codex_route_maps_to_one_executor(self):
        ie = load_instruction_envelope()
        self.assertIn("legacy_route_marker", inspect.signature(ie.build_instruction_envelope).parameters)
        envelope = ie.build_instruction_envelope(
            instruction_type="REVIEW_REQUEST",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.4.0",
            issuer_role="GPT_ORCHESTRATOR",
            return_role="GPT_ORCHESTRATOR",
            legacy_route_marker="[CODEX]",
            legacy_route_context="REVIEW",
            runtime_fresh_context_verified=True,
            runtime_input_source_kinds=["DURABLE_PROJECT_AUTHORITY", "REPOSITORY_CONTENT"],
        )
        self.assertEqual(envelope["executor_role"], "CODEX_REVIEWER")
        with self.assertRaisesRegex(ValueError, "LEGACY_ROUTE_CONTEXT_REQUIRED"):
            ie.build_instruction_envelope(
                instruction_type="EXECUTION_INSTRUCTION",
                target_project_context_id=VALID_ID,
                target_project_name="Example Project",
                expected_state_revision=7,
                framework_version="2.4.0",
                issuer_role="GPT_ORCHESTRATOR",
                return_role="GPT_ORCHESTRATOR",
                legacy_route_marker="[CODEX]",
            )

    def test_legacy_aliases_map_to_one_implementer_without_result_side_reinterpretation(self):
        ie = load_instruction_envelope()
        for instruction_type in ("WORK_UNIT", "IMPLEMENTATION"):
            envelope = ie.build_instruction_envelope(
                instruction_type=instruction_type,
                target_project_context_id=VALID_ID,
                target_project_name="Example Project",
                expected_state_revision=7,
                framework_version="2.1.0",
            )
            self.assertEqual(envelope["executor_role"], "CODEX_IMPLEMENTER")
            self.assertEqual(envelope["issuer_role"], "GPT_ORCHESTRATOR")
            self.assertEqual(envelope["return_role"], "GPT_ORCHESTRATOR")

    def test_reconciliation_approval_evidence_locator_is_closed_and_eligible(self):
        ie = load_instruction_envelope()
        locator = {"remote_ref": "refs/heads/gpt-codex-approval-evidence", "evidence_commit_sha": "a" * 40, "path": "approvals/approval-result.json", "blob_sha": "b" * 40}
        base = dict(instruction_type="RECONCILIATION_REQUEST", target_project_context_id=VALID_ID, target_project_name="Example Project", expected_state_revision=7, framework_version="2.7.2+fix.1", issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR", authorized_actions=["MUTATE_APPROVED_SCOPE"], scope_paths=[".gpt-codex/STATE.json"])
        self.assertEqual(ie.build_instruction_envelope(**base, approval_evidence_ref=locator)["approval_evidence_ref"], locator)
        invalids = [{"remote_ref": locator["remote_ref"], "evidence_commit_sha": locator["evidence_commit_sha"], "path": locator["path"]}, {**locator, "extra": "no"}, {**locator, "path": "../x"}, {**locator, "path": "a/../b"}, {**locator, "path": "a\\b"}, {**locator, "path": "/absolute"}, {**locator, "path": "C:/drive"}, {**locator, "evidence_commit_sha": "bad"}, {**locator, "blob_sha": "bad"}]
        for value in invalids:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "INVALID_APPROVAL_EVIDENCE_REF"):
                ie.build_instruction_envelope(**base, approval_evidence_ref=value)
        with self.assertRaisesRegex(ValueError, "APPROVAL_EVIDENCE_REF_NOT_ALLOWED"):
            ie.build_instruction_envelope(**{**base, "instruction_type": "EXECUTION_INSTRUCTION"}, approval_evidence_ref=locator)
        with self.assertRaisesRegex(ValueError, "APPROVAL_EVIDENCE_REF_NOT_ALLOWED"):
            ie.build_instruction_envelope(**{k: v for k, v in base.items() if k != "authorized_actions"}, approval_evidence_ref=locator)


if __name__ == "__main__":
    unittest.main()
