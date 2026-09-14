import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / ".gpt-codex"


class LocalCorrectiveStateTests(unittest.TestCase):
    def test_current_state_is_complete_and_synchronized(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        continuity = state["continuity"]
        self.assertEqual(state["revision"], 7)
        self.assertEqual(state["state"], "COMPLETE")
        self.assertEqual(state["active_work_unit"], "framework-project-separation-release-001")
        self.assertEqual(continuity["sync_status"], "SYNCED")
        self.assertEqual(continuity["latest_synced_state_revision"], 7)
        self.assertEqual(
            continuity["last_verified_result_ref"],
            ".gpt-codex/evidence/results/RESULT-V2.6.0-PUBLICATION.json",
        )
        self.assertEqual(
            continuity["latest_verified_remote_sha"],
            "a2f950138895df1a56564880977ed8530653b89f",
        )

    def test_historical_v250_result_is_confirmed_publication_attestation(self):
        result_path = GOV / "evidence" / "results" / "RESULT-V2.5.0-PUBLICATION.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["sync_status"], "SYNCED")
        self.assertEqual(result["remote_verification"], "VERIFIED")
        self.assertEqual(result["publication_authority"], "CONFIRMED_PUBLICATION")
        self.assertEqual(result["push_status"], "SUCCEEDED")
        self.assertEqual(result["source_project_context_id"], "cb1e0450-df32-4ff6-8a33-35187b69a866")
        self.assertEqual(result["source_github_repository_id"], "1366213495")
        self.assertEqual(result["framework_version"], "2.5.0")

    def test_current_v260_result_is_confirmed_publication_attestation(self):
        result_path = GOV / "evidence" / "results" / "RESULT-V2.6.0-PUBLICATION.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["framework_version"], "2.6.0")
        self.assertEqual(result["state_revision"], 7)
        self.assertEqual(result["remote_head_sha"], "a2f950138895df1a56564880977ed8530653b89f")
        self.assertEqual(result["publication_authority"], "CONFIRMED_PUBLICATION")
        self.assertEqual(result["publication_attestation"], "P is management-only and does not self-reference P.")

    def test_current_state_references_corrective_evidence(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        self.assertIn(
            ".gpt-codex/evidence/results/RESULT-V2.5.0-PUBLICATION.json",
            state["evidence_refs"],
        )
        self.assertIn(
            ".gpt-codex/evidence/results/RESULT-V2.6.0-PUBLICATION.json",
            state["evidence_refs"],
        )


if __name__ == "__main__":
    unittest.main()
