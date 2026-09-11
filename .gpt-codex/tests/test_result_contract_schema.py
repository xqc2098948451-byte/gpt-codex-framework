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

    def test_template_contains_a_complete_return_contract_example(self):
        template = json.loads(
            (ROOT / "project-template" / "RESULT_ENVELOPE.template.json").read_text(encoding="utf-8")
        )

        self.assertTrue(template["return_to_gpt_required"])
        for field in (
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

    def test_handoff_names_envelope_as_source_and_return_as_derived_view(self):
        handoff = (ROOT / "builtins" / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Result Envelope", handoff)
        self.assertIn("derived", handoff.lower())
        self.assertIn("Return To GPT Required", handoff)
        self.assertIn("NONE", handoff)


if __name__ == "__main__":
    unittest.main()
