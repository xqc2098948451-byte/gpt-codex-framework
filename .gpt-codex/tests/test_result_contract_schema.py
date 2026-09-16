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


if __name__ == "__main__":
    unittest.main()
