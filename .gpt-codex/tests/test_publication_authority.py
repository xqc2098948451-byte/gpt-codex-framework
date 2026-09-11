import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class PublicationAuthorityTests(unittest.TestCase):
    def setUp(self):
        from publication_contract import validate_result_authority, validate_state_authority

        self.validate_result_authority = validate_result_authority
        self.validate_state_authority = validate_state_authority

    def result(self, **overrides):
        value = {
            "status": "PASS",
            "sync_status": "SYNCED",
            "remote_verification": "VERIFIED",
            "publication_authority": "CONFIRMED_PUBLICATION",
            "remote_head_sha": "w-sha",
            "evidence_refs": ["result.json"],
        }
        value.update(overrides)
        return value

    def state(self, **overrides):
        value = {
            "state": "COMPLETE",
            "evidence_refs": ["result.json"],
            "continuity": {
                "sync_status": "SYNCED",
                "latest_verified_remote_sha": "w-sha",
                "last_verified_result_ref": "result.json",
            },
        }
        value.update(overrides)
        return value

    def test_pass_requires_verified_remote_for_each_nonverified_status(self):
        for verification in ("NOT_ATTEMPTED", "FAILED", "UNAVAILABLE"):
            with self.subTest(verification=verification):
                errors = self.validate_result_authority(
                    self.result(remote_verification=verification)
                )
                self.assertTrue(errors)

    def test_pass_with_verified_formal_publication_is_allowed(self):
        self.assertEqual(self.validate_result_authority(self.result()), [])

    def test_candidate_authority_cannot_pass_or_sync(self):
        errors = self.validate_result_authority(
            self.result(publication_authority="PUBLICATION_CANDIDATE_ONLY")
        )
        self.assertGreaterEqual(len(errors), 2)

    def test_synced_requires_verified_publication_evidence(self):
        errors = self.validate_result_authority(
            self.result(remote_verification="VERIFIED", evidence_refs=[])
        )
        self.assertTrue(errors)

    def test_candidate_state_cannot_be_complete(self):
        candidate = self.result(publication_authority="PUBLICATION_CANDIDATE_ONLY", status="LOCAL_COMPLETE", sync_status="SYNC_PENDING")
        errors = self.validate_state_authority(self.state(), {"result.json": candidate})
        self.assertTrue(errors)

    def test_complete_requires_durable_verified_result(self):
        errors = self.validate_state_authority(self.state(), {})
        self.assertTrue(errors)

    def test_synced_state_requires_nonempty_verified_baseline_sha(self):
        state = self.state()
        state["continuity"]["latest_verified_remote_sha"] = None
        errors = self.validate_state_authority(state, {"result.json": self.result()})
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
