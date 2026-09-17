import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class ResultContractSchemaTests(unittest.TestCase):
    def test_public_result_contract_rejects_synced_empty_evidence_refs(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_envelope_contract

        result = {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "work_unit_id": "WU-1",
            "extension": {"kind": "SKILL", "id": "verification", "version": "1.0.0"},
            "status": "LOCAL_COMPLETE",
            "evidence_refs": [],
            "completion_gate": "GPT_DECISION",
            "sync_status": "SYNCED",
            "remote_verification": "VERIFIED",
            "publication_authority": "CONFIRMED_PUBLICATION",
            "remote_head_sha": "a" * 40,
        }

        self.assertTrue(validate_result_envelope_contract(result))
        result["evidence_refs"] = ["evidence-1"]
        self.assertEqual(validate_result_envelope_contract(result), [])

        too_many = dict(result, finding_ids=[f"finding-{index}" for index in range(51)])
        self.assertTrue(validate_result_envelope_contract(too_many))
        duplicate = dict(result, finding_ids=["finding-1", "finding-1"])
        self.assertTrue(validate_result_envelope_contract(duplicate))
        forbidden = dict(result, message_type="legacy")
        self.assertTrue(validate_result_envelope_contract(forbidden))

        from validate_project import validate_instruction_envelope_contract
        instruction = {
            "instruction_id": "44444444-4444-4444-8444-444444444444",
            "instruction_type": "WORK_UNIT",
            "target_project_context_id": "11111111-1111-4111-8111-111111111111",
            "target_project_name": "Project One",
            "expected_state_revision": 8,
            "framework_version": "2.0.0",
        }
        self.assertEqual(validate_instruction_envelope_contract(instruction), [])

    def test_schema_preserves_kernel_and_schema_versions_and_declares_return_fields(self):
        schema = json.loads((ROOT / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["kernel_version"]["const"], "2.0.0")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        for field in (
            "result_message_type",
            "response_to_instruction_id",
            "responder_role",
            "return_role",
            "review_target_revision",
            "finding_ids",
            "fix_round",
            "remediation_decision_ref",
            "protocol_error",
            "role_observation",
            "artifact_stage",
            "artifact_path",
            "publication_authority",
            "return_to_gpt_required",
            "state_revision",
            "execution",
            "changed",
            "verify",
            "deviations",
            "git",
            "parallel_batch",
            "execution_unit",
            "observability_fitness",
            "extension_evidence_refs",
            "next_gpt_action",
        ):
            self.assertIn(field, schema["properties"])
        self.assertNotIn("message_type", schema["properties"])
        self.assertEqual(
            schema["properties"]["result_message_type"]["enum"],
            ["REVIEW_RESULT", "REVIEW_FINDING", "IMPLEMENTATION_RESULT", "INVALID_INSTRUCTION", "ROLE_AUTHORITY_CONFLICT"],
        )

    def test_result_type_is_not_instruction_type_and_generic_message_type_is_rejected(self):
        schema = json.loads((ROOT / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(any("message_type" in item.get("not", {}).get("required", []) for item in schema.get("allOf", [])))
        self.assertTrue(any(item.get("if", {}).get("properties", {}).get("result_message_type", {}).get("enum") for item in schema.get("allOf", [])))

    def test_template_contains_a_complete_return_contract_example(self):
        template = json.loads(
            (ROOT / "project-template" / "RESULT_ENVELOPE.template.json").read_text(encoding="utf-8")
        )

        self.assertTrue(template["return_to_gpt_required"])
        for field in (
            "result_message_type",
            "response_to_instruction_id",
            "responder_role",
            "return_role",
            "review_target_revision",
            "finding_ids",
            "fix_round",
            "remediation_decision_ref",
            "protocol_error",
            "role_observation",
            "artifact_stage",
            "artifact_path",
            "publication_authority",
            "state_revision",
            "execution",
            "changed",
            "verify",
            "deviations",
            "git",
            "parallel_batch",
            "execution_unit",
            "observability_fitness",
            "extension_evidence_refs",
            "next_gpt_action",
        ):
            self.assertIn(field, template)
        self.assertNotIn("message_type", template)

    def test_schema_has_mechanical_publication_conditionals(self):
        schema = json.loads((ROOT / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))
        conditionals = schema["allOf"]
        self.assertTrue(any(item.get("if", {}).get("properties", {}).get("status", {}).get("const") == "PASS" for item in conditionals))
        self.assertTrue(any(item.get("if", {}).get("properties", {}).get("sync_status", {}).get("const") == "SYNCED" for item in conditionals))
        self.assertTrue(any(item.get("if", {}).get("properties", {}).get("publication_authority", {}).get("const") == "PUBLICATION_CANDIDATE_ONLY" for item in conditionals))

    def test_role_observation_matches_frozen_minimal_shape(self):
        schema = json.loads((ROOT / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))
        observation = schema["properties"]["role_observation"]
        expected = {
            "role", "instruction_id", "work_unit", "reviewed_revision", "executed_revision",
            "files_read", "files_changed", "tests_run", "findings", "fix_round", "agent_spawns", "result",
        }
        self.assertEqual(set(observation["properties"]), expected)
        self.assertEqual(set(observation["required"]), expected)

    def test_handoff_names_envelope_as_source_and_return_as_derived_view(self):
        handoff = (ROOT / "builtins" / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Result Envelope", handoff)
        self.assertIn("derived", handoff.lower())
        self.assertIn("Return To GPT Required", handoff)
        self.assertIn("NONE", handoff)

    def test_completion_evidence_contract_requires_completed_zero_exit_complete_scope_and_validators(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from publication_contract import validate_completion_evidence

        complete = {
            "status": "PASS",
            "completion_evidence": {
                "execution_state": "COMPLETED", "process_completed": True,
                "exit_code": 0, "intended_scope": ["tests"], "executed_scope": ["tests"],
                "test_files_expected": 1, "test_files_executed": 1, "test_count": 1,
                "failure_count": 0, "error_count": 0,
                "validators_expected": ["validate_project"],
                "validators_completed": ["validate_project"], "blocker_evidence_refs": [],
            },
        }
        self.assertEqual(validate_completion_evidence(complete), [])
        for field, value in (("exit_code", None), ("test_files_expected", None), ("test_count", None), ("failure_count", 1), ("error_count", 1), ("validators_completed", [])):
            candidate = json.loads(json.dumps(complete))
            candidate["completion_evidence"][field] = value
            self.assertTrue(validate_completion_evidence(candidate), field)

    def test_governed_pass_fails_closed_while_legacy_result_remains_compatible(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_protocol
        governed = {"result_message_type": "IMPLEMENTATION_RESULT", "status": "PASS"}
        self.assertIn("COMPLETION_EVIDENCE_REQUIRED", validate_result_protocol(governed))
        self.assertEqual(validate_result_protocol({"status": "PASS"}), [])

    def test_completion_evidence_denies_absent_validators_partial_process_and_blocked_without_proof(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from publication_contract import validate_completion_evidence
        base = {"status": "PASS", "completion_evidence": {"execution_state": "COMPLETED", "process_completed": True, "exit_code": 0, "intended_scope": ["x"], "executed_scope": ["x"], "test_files_expected": 1, "test_files_executed": 1, "test_count": 1, "failure_count": 0, "error_count": 0, "validators_expected": [], "validators_completed": [], "blocker_evidence_refs": []}}
        missing = json.loads(json.dumps(base)); del missing["completion_evidence"]["validators_expected"]; del missing["completion_evidence"]["validators_completed"]
        self.assertTrue(validate_completion_evidence(missing))
        partial = json.loads(json.dumps(base)); partial["completion_evidence"]["process_completed"] = False
        self.assertTrue(validate_completion_evidence(partial))
        blocked = json.loads(json.dumps(base)); blocked["status"] = "BLOCKED"; blocked["completion_evidence"]["execution_state"] = "BLOCKED"
        self.assertTrue(validate_completion_evidence(blocked))
        incomplete = {"status": "INCOMPLETE", "completion_evidence": {"execution_state": "INCOMPLETE"}}
        self.assertEqual(validate_completion_evidence(incomplete), [])

    def test_schema_rejects_governed_pass_without_completion_evidence_but_keeps_legacy(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_envelope_contract
        base = {"kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W", "extension": {}, "status": "PASS", "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "VERIFIED"}
        governed = dict(base, result_message_type="IMPLEMENTATION_RESULT")
        self.assertTrue(validate_result_envelope_contract(governed))
        self.assertEqual(validate_result_envelope_contract(base), [])

    def test_partial_scope_and_valid_blocked_are_direct_completion_behaviors(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from publication_contract import validate_completion_evidence
        evidence = {"execution_state": "COMPLETED", "process_completed": True, "exit_code": 0, "intended_scope": ["suite-a", "suite-b"], "executed_scope": ["suite-a"], "test_files_expected": 1, "test_files_executed": 1, "test_count": 1, "failure_count": 0, "error_count": 0, "validators_expected": [], "validators_completed": [], "blocker_evidence_refs": []}
        self.assertTrue(validate_completion_evidence({"status": "PASS", "completion_evidence": evidence}))
        evidence["execution_state"] = "BLOCKED"; evidence["blocker_evidence_refs"] = ["evidence/proven-blocker"]
        self.assertEqual(validate_completion_evidence({"status": "BLOCKED", "completion_evidence": evidence}), [])

    def test_schema_rejects_governed_pass_with_null_completion_evidence(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_envelope_contract
        result = {"kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W", "extension": {}, "status": "PASS", "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "VERIFIED", "result_message_type": "IMPLEMENTATION_RESULT", "completion_evidence": None}
        self.assertTrue(validate_result_envelope_contract(result))

    def test_schema_accepts_direct_incomplete_completion_evidence(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_envelope_contract
        result = {"kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W", "extension": {}, "status": "INCOMPLETE", "evidence_refs": [], "completion_gate": "NONE", "completion_evidence": {"execution_state": "INCOMPLETE"}}
        self.assertEqual(validate_result_envelope_contract(result), [])

    def test_schema_rejects_governed_pass_with_partial_completion_evidence(self):
        if str(SCRIPTS) not in sys.path:
            sys.path.insert(0, str(SCRIPTS))
        from validate_project import validate_result_envelope_contract
        partial = {"execution_state": "COMPLETED", "process_completed": True, "exit_code": 0, "intended_scope": ["suite"], "executed_scope": ["suite"], "test_files_expected": 1, "test_files_executed": 1, "test_count": 1, "failure_count": 0, "error_count": 0, "validators_expected": [], "blocker_evidence_refs": []}
        result = {"kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W", "extension": {}, "status": "PASS", "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "VERIFIED", "result_message_type": "IMPLEMENTATION_RESULT", "completion_evidence": partial}
        self.assertTrue(validate_result_envelope_contract(result))


if __name__ == "__main__":
    unittest.main()


class ContractRepairTask3Tests(unittest.TestCase):
    def test_approval_result_is_intrinsic_and_does_not_correlate_request_scope(self):
        sys.path.insert(0, str(SCRIPTS))
        from role_communication import validate_result_message_type
        self.assertEqual(validate_result_message_type("APPROVAL_RESULT"), [])
        approved_instruction = {"scope_paths": ["different/still-well-formed.json"]}
        self.assertEqual(approved_instruction["scope_paths"], ["different/still-well-formed.json"])
