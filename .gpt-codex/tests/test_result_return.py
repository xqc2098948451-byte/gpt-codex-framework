import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from result_return import render_gpt_return, required_return_sections


def envelope(status="PASS"):
    return {
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": "PRJ-001",
        "work_unit_id": "WORK-012",
        "extension": {"kind": "SKILL", "id": "verification", "version": "1.0.0"},
        "status": status,
        "result_message_type": "IMPLEMENTATION_RESULT" if status == "PASS" else "REVIEW_FINDING",
        "response_to_instruction_id": "11111111-1111-4111-8111-111111111111",
        "responder_role": "CODEX_IMPLEMENTER" if status == "PASS" else "CODEX_REVIEWER",
        "return_role": "GPT_ORCHESTRATOR",
        "review_target_revision": "a" * 40,
        "finding_ids": [] if status == "PASS" else ["RCP-001"],
        "fix_round": 0,
        "remediation_decision_ref": "DECISION-001" if status != "PASS" else None,
        "protocol_error": None,
        "role_observation": {
            "role": "CODEX_IMPLEMENTER",
            "instruction_id": "11111111-1111-4111-8111-111111111111",
            "work_unit": "WORK-012",
            "reviewed_revision": "a" * 40,
            "executed_revision": None,
            "files_read": [".gpt-codex/CONTROL.json"],
            "files_changed": [],
            "tests_run": ["tests: PASS"],
            "findings": [],
            "fix_round": 0,
            "agent_spawns": 0,
            "result": "IMPLEMENTATION_RESULT",
        },
        "artifact_stage": "IMPLEMENTATION",
        "artifact_path": ".gpt-codex/scripts/example.py",
        "evidence_refs": ["EVIDENCE-001"],
        "completion_gate": "GPT_DECISION",
        "return_to_gpt_required": True,
        "state_revision": 18,
        "execution": "COMPLETED" if status == "PASS" else status,
        "changed": [".gpt-codex/scripts/result_return.py"] if status == "PASS" else [],
        "verify": ["tests: PASS"] if status == "PASS" else [],
        "deviations": [],
        "blockers": [] if status != "BLOCKED" else ["Required approval is missing"],
        "next_gpt_action": "Review the returned evidence and determine the next authorized action.",
        "git": {
            "base_sha": "abc123",
            "implementation_sha": "def456",
        },
        "parallel_batch": "BATCH-03",
        "execution_unit": "UNIT-07",
        "observability_fitness": ["fitness: PASS"],
        "extension_evidence_refs": ["EXT-EVIDENCE-002"],
    }


class ResultReturnTests(unittest.TestCase):
    def test_pass_produces_complete_paste_ready_return(self):
        rendered = render_gpt_return(envelope("PASS"))

        self.assertTrue(rendered.startswith("RESULT: PASS\n"))
        for section in required_return_sections():
            self.assertIn(section, rendered)
        self.assertIn("GIT_BASE_SHA: abc123", rendered)
        self.assertIn("IMPLEMENTATION_SHA: def456", rendered)
        self.assertIn("PARALLEL_BATCH: BATCH-03", rendered)
        self.assertIn("EXECUTION_UNIT: UNIT-07", rendered)
        self.assertIn("OBSERVABILITY_FITNESS:", rendered)
        self.assertIn("EXTENSION_EVIDENCE:", rendered)

    def test_fail_and_blocked_produce_complete_returns(self):
        for status in ("FAIL", "BLOCKED"):
            with self.subTest(status=status):
                rendered = render_gpt_return(envelope(status))
                self.assertIn(f"RESULT: {status}", rendered)
                for section in required_return_sections():
                    self.assertIn(section, rendered)
                self.assertIn("BLOCKERS:", rendered)
                self.assertIn("NEXT_GPT_ACTION:", rendered)

    def test_empty_fields_are_stable_none_values(self):
        value = envelope("FAIL")
        value.update(
            {
                "state_revision": None,
                "execution": "",
                "changed": [],
                "verify": [],
                "evidence_refs": [],
                "deviations": [],
                "blockers": [],
                "git": {},
                "parallel_batch": None,
                "execution_unit": None,
                "observability_fitness": [],
                "extension_evidence_refs": [],
                "next_gpt_action": None,
            }
        )

        rendered = render_gpt_return(value)

        self.assertIn("STATE_REVISION: NONE", rendered)
        self.assertIn("EXECUTION: NONE", rendered)
        self.assertIn("GIT_BASE_SHA: NONE", rendered)
        self.assertIn("IMPLEMENTATION_SHA: NONE", rendered)
        self.assertIn("PARALLEL_BATCH: NONE", rendered)
        self.assertIn("EXECUTION_UNIT: NONE", rendered)
        self.assertIn("CHANGED: NONE", rendered)
        self.assertIn("VERIFY: NONE", rendered)
        self.assertIn("EVIDENCE: NONE", rendered)
        self.assertIn("DEVIATIONS: NONE", rendered)
        self.assertIn("BLOCKERS: NONE", rendered)
        self.assertIn("OBSERVABILITY_FITNESS: NONE", rendered)
        self.assertIn("EXTENSION_EVIDENCE: NONE", rendered)
        self.assertIn("NEXT_GPT_ACTION: NONE", rendered)

    def test_large_logs_are_not_part_of_return_contract(self):
        value = envelope("PASS")
        value["logs"] = "FULL TEST LOG " * 10000

        rendered = render_gpt_return(value)

        self.assertNotIn("FULL TEST LOG", rendered)
        self.assertLess(len(rendered), 5000)

    def test_return_text_is_derived_from_the_envelope(self):
        value = envelope("PASS")
        first = render_gpt_return(value)
        value["evidence_refs"] = ["EVIDENCE-CHANGED"]
        second = render_gpt_return(value)

        self.assertIn("EVIDENCE-001", first)
        self.assertNotIn("EVIDENCE-001", second)
        self.assertIn("EVIDENCE-CHANGED", second)

    def test_return_is_not_emitted_when_not_required(self):
        value = envelope("PASS")
        value["return_to_gpt_required"] = False

        self.assertEqual(render_gpt_return(value), "")

    def test_role_and_result_labels_are_derived_without_generic_message_type(self):
        value = envelope("FAIL")
        rendered = render_gpt_return(value)

        self.assertIn("RESULT_MESSAGE_TYPE: REVIEW_FINDING", rendered)
        self.assertIn("RESPONDER_ROLE: CODEX_REVIEWER", rendered)
        self.assertIn("RETURN_ROLE: GPT_ORCHESTRATOR", rendered)
        self.assertIn("REVIEW_TARGET_REVISION: " + "a" * 40, rendered)
        self.assertIn("ARTIFACT_STAGE: IMPLEMENTATION", rendered)
        self.assertIn("ARTIFACT_PATH: .gpt-codex/scripts/example.py", rendered)
        self.assertNotIn("\nMESSAGE_TYPE:", "\n" + rendered)


if __name__ == "__main__":
    unittest.main()
