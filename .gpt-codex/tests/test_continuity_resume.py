import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class ContinuityResumeTests(unittest.TestCase):
    def test_resume_requires_selected_repository_id_and_reads_canonical_state(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gov = root / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({
                "project_id": "P", "project_context_id": "11111111-1111-4111-8111-111111111111",
                "github": {"repository_id": "repo-a", "repository_full_name": "owner/a", "default_branch": "main"},
            }), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({
                "project_id": "P", "revision": 4, "state": "VERIFYING",
                "continuity": {"current_remote_ref": "refs/heads/main", "latest_verified_remote_sha": "p",
                                "latest_synced_state_revision": 4, "last_verified_result_ref": None, "sync_status": "SYNCED"},
            }), encoding="utf-8")
            result = load_continuity_resume(root, "repo-a")
            self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
            self.assertEqual(result["repository_id"], "repo-a")

    def test_resume_blocks_wrong_repository(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({"github": {"repository_id": "repo-a", "repository_full_name": "o/a", "default_branch": "main"}}), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({"revision": 0, "continuity": {"sync_status": "SYNCED"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_continuity_resume(Path(td), "repo-b")


if __name__ == "__main__":
    unittest.main()
