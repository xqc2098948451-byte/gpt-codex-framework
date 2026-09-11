import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class BoundedAttestationTests(unittest.TestCase):
    def setUp(self):
        from git_continuity import evaluate_attestation_chain

        self.evaluate_attestation_chain = evaluate_attestation_chain

    def valid_chain(self, **overrides):
        value = {
            "work_sha": "w-sha",
            "publication_sha": "p-sha",
            "verified_work": True,
            "publication_references_work": True,
            "publication_references_self": False,
            "publication_is_management_only": True,
            "generic_tree_matches": True,
        }
        value.update(overrides)
        return value

    def test_work_candidate_is_local_complete_pending(self):
        result = self.evaluate_attestation_chain(self.valid_chain(verified_work=False, publication_sha=None))
        self.assertEqual(result["status"], "LOCAL_COMPLETE")
        self.assertEqual(result["sync_status"], "SYNC_PENDING")
        self.assertEqual(result["publication_authority"], "PUBLICATION_CANDIDATE_ONLY")

    def test_publication_can_attest_verified_work_without_self_reference(self):
        result = self.evaluate_attestation_chain(self.valid_chain())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["sync_status"], "SYNCED")
        self.assertEqual(result["remote_verification"], "VERIFIED")
        self.assertEqual(result["verified_baseline_sha"], "w-sha")
        self.assertNotEqual(result.get("publication_sha"), result.get("verified_baseline_sha"))

    def test_publication_self_reference_is_rejected(self):
        result = self.evaluate_attestation_chain(
            self.valid_chain(publication_references_self=True)
        )
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_publication_generic_drift_requires_reconciliation(self):
        result = self.evaluate_attestation_chain(
            self.valid_chain(generic_tree_matches=False)
        )
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_publication_cannot_attest_unverified_work(self):
        result = self.evaluate_attestation_chain(
            self.valid_chain(verified_work=False)
        )
        self.assertEqual(result["status"], "LOCAL_COMPLETE")
        self.assertEqual(result["publication_authority"], "PUBLICATION_CANDIDATE_ONLY")


if __name__ == "__main__":
    unittest.main()
