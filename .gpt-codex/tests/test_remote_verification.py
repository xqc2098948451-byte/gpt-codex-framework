import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from git_continuity import verify_remote_publication


class RemoteVerificationTests(unittest.TestCase):
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
