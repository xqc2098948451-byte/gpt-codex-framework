import json
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / ".gpt-codex"


class LocalCorrectiveStateTests(unittest.TestCase):
    def assert_durable_current_state_contract(self, state):
        continuity = state["continuity"]
        self.assertEqual(state["kernel_version"], "2.0.0")
        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(state["project_id"], "PRJ-FRAMEWORK-MANAGEMENT")
        self.assertIsInstance(state["revision"], int)
        self.assertGreaterEqual(state["revision"], 0)
        self.assertIn(state["state"], {"PROPOSED", "AUTHORIZED", "ACTIVE", "VERIFYING", "COMPLETE", "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"})
        self.assertTrue({"current_remote_ref", "latest_verified_remote_sha", "latest_synced_state_revision", "last_verified_result_ref", "sync_status"}.issubset(continuity))
        self.assertIn(continuity["sync_status"], {"SYNCED", "SYNC_PENDING", "RECONCILIATION_REQUIRED"})
        self.assertIsInstance(continuity["latest_synced_state_revision"], int)
        self.assertLessEqual(continuity["latest_synced_state_revision"], state["revision"])
        result_ref = continuity["last_verified_result_ref"]
        if result_ref is not None:
            self.assertIsInstance(result_ref, str)
            self.assertFalse(Path(result_ref).is_absolute())
            self.assertTrue((ROOT / result_ref).is_file())
        if continuity["sync_status"] == "SYNCED":
            self.assertIsInstance(continuity["latest_verified_remote_sha"], str)
            self.assertRegex(continuity["latest_verified_remote_sha"], r"^[0-9a-f]{40}$")

    def test_current_state_satisfies_durable_contract(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        self.assert_durable_current_state_contract(state)

    def test_state_oracle_accepts_lifecycle_variation_and_rejects_durable_faults(self):
        state = json.loads((GOV / "STATE.json").read_text(encoding="utf-8"))
        varied = deepcopy(state)
        varied["revision"] += 1
        varied["state"] = "ACTIVE"
        varied["active_work_unit"] = None
        self.assert_durable_current_state_contract(varied)
        identity_fault = deepcopy(varied)
        identity_fault["project_id"] = "FOREIGN"
        with self.assertRaises(AssertionError):
            self.assert_durable_current_state_contract(identity_fault)
        continuity_fault = deepcopy(varied)
        continuity_fault["continuity"]["latest_synced_state_revision"] = varied["revision"] + 1
        with self.assertRaises(AssertionError):
            self.assert_durable_current_state_contract(continuity_fault)

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
