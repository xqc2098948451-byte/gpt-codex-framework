import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResultContractSchemaTests(unittest.TestCase):
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

    def test_handoff_names_envelope_as_source_and_return_as_derived_view(self):
        handoff = (ROOT / "builtins" / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Result Envelope", handoff)
        self.assertIn("derived", handoff.lower())
        self.assertIn("Return To GPT Required", handoff)
        self.assertIn("NONE", handoff)


if __name__ == "__main__":
    unittest.main()
