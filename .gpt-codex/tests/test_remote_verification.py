import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from git_continuity import verify_remote_activation, verify_remote_publication


class RemoteVerificationTests(unittest.TestCase):
    def test_remote_activation_requires_exact_tool_observed_facts(self):
        facts = {
            "evidence_source": "TOOL_OBSERVED", "bound_repository_id": "repo-1",
            "observed_repository_id": "repo-1", "expected_remote_ref": "refs/heads/main",
            "observed_remote_ref": "refs/heads/main", "candidate_sha": "a" * 40,
            "observed_remote_branch_sha": "a" * 40, "observed_tag_target_sha": "a" * 40,
            "target_version": "2.7.2", "expected_tag": "v2.7.2", "observed_tag": "v2.7.2",
            "observed_release_version": "2.7.2", "observed_remote_version": "2.7.2",
            "expected_artifact_sha256": "b" * 64, "observed_artifact_sha256": "b" * 64,
            "expected_artifact_size_bytes": 17, "observed_artifact_size_bytes": 17,
        }
        self.assertEqual(verify_remote_activation(facts)["status"], "VERIFIED")
        for key, value, code in (
            ("observed_remote_branch_sha", "c" * 40, "REMOTE_HEAD_MISMATCH"),
            ("observed_tag_target_sha", "c" * 40, "REMOTE_TAG_TARGET_MISMATCH"),
            ("observed_release_version", "2.7.1", "REMOTE_RELEASE_VERSION_MISMATCH"),
            ("observed_remote_version", "2.7.1", "REMOTE_VERSION_MISMATCH"),
            ("observed_artifact_sha256", "c" * 64, "REMOTE_ARTIFACT_SHA_MISMATCH"),
            ("observed_artifact_size_bytes", 18, "REMOTE_ARTIFACT_SIZE_MISMATCH"),
        ):
            with self.subTest(code=code):
                result = verify_remote_activation(dict(facts, **{key: value}))
                self.assertEqual(result["status"], "FAILED")
                self.assertEqual(result["reason"], code)
        self.assertNotEqual(verify_remote_activation(dict(facts, observed_tag=None))["status"], "VERIFIED")
        self.assertNotEqual(verify_remote_activation(dict(facts, evidence_source="MODEL_INFERRED"))["status"], "VERIFIED")
    def test_verified_publication_requires_remote_head_and_objects(self):
        result = verify_remote_publication(
            "refs/heads/main", "p", "repo-1", "repo-1", True,
            observed_remote_ref="refs/heads/main", observed_remote_head="p", work_reachable=True,
            result_present=True, state_present=True,
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["evidence_type"], "TOOL_OBSERVED")

    def test_push_success_with_mismatched_head_is_failed(self):
        result = verify_remote_publication(
            "refs/heads/main", "p", "repo-1", "repo-1", True,
            observed_remote_ref="refs/heads/main", observed_remote_head="other",
        )
        self.assertEqual(result["status"], "FAILED")

    def test_unavailable_remote_is_not_synced(self):
        result = verify_remote_publication("refs/heads/main", "p", "repo-1", "repo-1", True)
        self.assertEqual(result["status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
