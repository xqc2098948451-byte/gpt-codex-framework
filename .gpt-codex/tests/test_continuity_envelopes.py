import sys
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from instruction_envelope import build_instruction_envelope, render_codex_instruction
from result_return import render_gpt_return


class ContinuityEnvelopeTests(unittest.TestCase):
    context = "11111111-1111-4111-8111-111111111111"

    def test_instruction_carries_repository_identity_and_remote_hint(self):
        envelope = build_instruction_envelope(
            "WORK_UNIT", self.context, "Example", 3, "2.2.0",
            target_github_repository_id="123",
            target_github_repository_full_name="owner/repo",
            expected_remote_ref="refs/heads/main",
            expected_remote_head_sha="abc",
            expected_remote_name="upstream",
        )
        self.assertEqual(envelope["target_github_repository_id"], "123")
        self.assertEqual(envelope["expected_remote_name"], "upstream")
        rendered = render_codex_instruction(envelope, "work", {"execution_strategy": "串行", "approval": "需要 GPT 判断"})
        self.assertIn("TARGET_GITHUB_REPOSITORY_ID: 123", rendered)
        self.assertIn("EXPECTED_REMOTE_NAME: upstream", rendered)

    def test_result_distinguishes_local_pending_from_synced_pass(self):
        base = {
            "return_to_gpt_required": True,
            "status": "LOCAL_COMPLETE",
            "source_project_context_id": self.context,
            "source_project_name": "Example",
            "framework_version": "2.2.0",
            "work_unit_id": "W-1",
            "state_revision": 3,
            "execution": "COMPLETED",
            "evidence_refs": [], "changed": [], "verify": [], "deviations": [], "blockers": [],
            "git": {"base_sha": "a", "implementation_sha": "b"},
            "sync_status": "SYNC_PENDING", "push_status": "NOT_ATTEMPTED", "remote_verification": "UNAVAILABLE",
            "publication_authority": "PUBLICATION_CANDIDATE_ONLY",
            "completion_gate": "GPT_DECISION",
        }
        rendered = render_gpt_return(base)
        self.assertIn("SOURCE_GITHUB_REPOSITORY_ID: NONE", rendered)
        self.assertIn("SYNC_STATUS: SYNC_PENDING", rendered)
        self.assertIn("PUBLICATION_AUTHORITY: PUBLICATION_CANDIDATE_ONLY", rendered)
        self.assertNotIn("RESULT: PASS", rendered)

    def test_result_schema_allows_nonfinal_local_complete_status(self):
        schema = json.loads((ROOT / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))
        self.assertIn("LOCAL_COMPLETE", schema["properties"]["status"]["enum"])


if __name__ == "__main__":
    unittest.main()
