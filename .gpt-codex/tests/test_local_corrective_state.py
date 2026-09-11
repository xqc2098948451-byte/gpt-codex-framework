import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / ".gpt-codex"


class LocalCorrectiveStateTests(unittest.TestCase):
    def test_current_state_is_forward_only_reconciliation_pending(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        continuity = state["continuity"]
        self.assertEqual(state["revision"], 2)
        self.assertEqual(state["state"], "RECONCILIATION_REQUIRED")
        self.assertEqual(continuity["sync_status"], "SYNC_PENDING")
        self.assertIsNone(continuity["latest_verified_remote_sha"])

    def test_corrective_result_is_local_candidate_only(self):
        result_path = GOV / "evidence" / "results" / "RESULT-V2.2.1-LOCAL-CORRECTIVE.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "LOCAL_COMPLETE")
        self.assertEqual(result["sync_status"], "SYNC_PENDING")
        self.assertEqual(result["remote_verification"], "NOT_ATTEMPTED")
        self.assertEqual(result["publication_authority"], "PUBLICATION_CANDIDATE_ONLY")
        self.assertEqual(result["push_status"], "NOT_ATTEMPTED")
        self.assertEqual(result["source_project_context_id"], "cb1e0450-df32-4ff6-8a33-35187b69a866")
        self.assertEqual(result["source_github_repository_id"], "1366213495")

    def test_current_state_references_corrective_evidence(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        self.assertIn(
            ".gpt-codex/evidence/results/RESULT-V2.2.1-LOCAL-CORRECTIVE.json",
            state["evidence_refs"],
        )


if __name__ == "__main__":
    unittest.main()
