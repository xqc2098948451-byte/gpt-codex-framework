import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class ContinuityResumeTests(unittest.TestCase):
    def _resume_checkpoint(self, context_sources=None, hot_modules=None):
        return {
            "schema_version": 1,
            "authority": "DERIVED_CACHE",
            "project_id": "P",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "repo-a",
            "context_sources": context_sources or [],
            "objective": "Resume work.",
            "decision": None,
            "blocker": None,
            "verification": [],
            "working_set": {
                "hot_modules": hot_modules or [],
                "hot_files": [],
                "next_required_reads": [],
                "invalidated_context": [],
            },
        }

    def test_load_resume_checkpoint_returns_none_when_checkpoint_is_absent(self):
        from continuity_resume import load_resume_checkpoint

        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(load_resume_checkpoint(Path(td) / ".gpt-codex"))

    def test_load_resume_checkpoint_rejects_non_file_and_invalid_payloads(self):
        from continuity_resume import load_resume_checkpoint

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            checkpoint_path = gov / "continuity" / "RESUME.json"
            checkpoint_path.parent.mkdir(parents=True)
            checkpoint_path.mkdir()
            with self.assertRaisesRegex(ValueError, "^RESUME_CHECKPOINT_INVALID$"):
                load_resume_checkpoint(gov)
            checkpoint_path.rmdir()

            invalid_payloads = (
                ("[\"not an object\"]", "RESUME_CHECKPOINT_INVALID"),
                (json.dumps({**self._resume_checkpoint(), "schema_version": 2}), "RESUME_CHECKPOINT_SCHEMA_UNSUPPORTED"),
                (json.dumps({**self._resume_checkpoint(), "authority": "CANONICAL"}), "RESUME_CHECKPOINT_AUTHORITY_INVALID"),
            )
            for payload, error in invalid_payloads:
                checkpoint_path.write_text(payload, encoding="utf-8")
                with self.subTest(error=error), self.assertRaisesRegex(ValueError, f"^{error}$"):
                    load_resume_checkpoint(gov)

    def test_load_resume_checkpoint_retains_hot_modules(self):
        from continuity_resume import load_resume_checkpoint

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            checkpoint_path = gov / "continuity" / "RESUME.json"
            checkpoint_path.parent.mkdir(parents=True)
            checkpoint_path.write_text(
                json.dumps(self._resume_checkpoint(hot_modules=["core.resume", "core.context"])),
                encoding="utf-8",
            )

            checkpoint = load_resume_checkpoint(gov)

            self.assertEqual(checkpoint["working_set"]["hot_modules"], ["core.resume", "core.context"])

    def test_fingerprint_file_uses_exact_raw_bytes_sha256_format(self):
        from continuity_resume import fingerprint_file

        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "binary.dat"
            source.write_bytes(b"\x00\xff\r\n")

            self.assertEqual(
                fingerprint_file(source),
                "sha256:e9489f37fb3051e9efa1dc916004d7274e7b63975e3209708947267f2393a9be",
            )

    def test_compare_context_sources_invalidates_only_changed_source(self):
        from continuity_resume import compare_context_sources, fingerprint_file

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            changed = root / "context" / "changed.md"
            unchanged = root / "context" / "unchanged.md"
            changed.parent.mkdir()
            changed.write_text("before", encoding="utf-8")
            unchanged.write_text("unchanged", encoding="utf-8")
            checkpoint = self._resume_checkpoint([
                {"path": "context/changed.md", "fingerprint": fingerprint_file(changed)},
                {"path": "context/unchanged.md", "fingerprint": fingerprint_file(unchanged)},
            ])
            changed.write_text("after", encoding="utf-8")

            invalidated_context, required_reads = compare_context_sources(root, checkpoint)

            self.assertEqual(invalidated_context, ["context/changed.md"])
            self.assertEqual(required_reads, [])

    def test_compare_context_sources_keeps_unchanged_project_map_valid(self):
        from continuity_resume import compare_context_sources, fingerprint_file

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project_map = root / ".gpt-codex" / "navigation" / "PROJECT_MAP.json"
            project_map.parent.mkdir(parents=True)
            project_map.write_text('{"modules": []}', encoding="utf-8")
            checkpoint = self._resume_checkpoint([
                {"path": ".gpt-codex/navigation/PROJECT_MAP.json", "fingerprint": fingerprint_file(project_map)},
            ])

            invalidated_context, required_reads = compare_context_sources(root, checkpoint)

            self.assertNotIn(".gpt-codex/navigation/PROJECT_MAP.json", invalidated_context)
            self.assertEqual(required_reads, [])

    def test_compare_context_sources_queues_missing_declared_source(self):
        from continuity_resume import compare_context_sources

        with tempfile.TemporaryDirectory() as td:
            invalidated_context, required_reads = compare_context_sources(
                Path(td),
                self._resume_checkpoint([{"path": "context/missing.md", "fingerprint": "sha256:missing"}]),
            )

            self.assertEqual(invalidated_context, [])
            self.assertEqual(required_reads, ["context/missing.md"])

    def test_compare_context_sources_rejects_absolute_and_parent_paths(self):
        from continuity_resume import compare_context_sources

        with tempfile.TemporaryDirectory() as td:
            for unsafe_path in ("../outside.md", str((Path(td) / "outside.md").resolve())):
                checkpoint = self._resume_checkpoint([{"path": unsafe_path, "fingerprint": "sha256:ignored"}])
                with self.subTest(unsafe_path=unsafe_path), self.assertRaisesRegex(
                    ValueError, f"^RESUME_CONTEXT_SOURCE_PATH_INVALID:{re.escape(unsafe_path)}$"
                ):
                    compare_context_sources(Path(td), checkpoint)

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

    def test_resume_accepts_attestation_head_p_for_verified_baseline_w(self):
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
                "project_id": "P", "revision": 4, "state": "COMPLETE",
                "continuity": {"current_remote_ref": "refs/heads/main", "latest_verified_remote_sha": "w",
                                "latest_synced_state_revision": 4, "last_verified_result_ref": "result.json", "sync_status": "SYNCED"},
            }), encoding="utf-8")
            result = load_continuity_resume(
                root,
                "repo-a",
                observed_remote_head_sha="p",
                work_reachable=True,
                attestation_is_management_only=True,
                attestation_references_work=True,
                generic_tree_matches=True,
            )
            self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
            self.assertEqual(result["verified_baseline_sha"], "w")
            self.assertEqual(result["current_attestation_head"], "p")

    def test_resume_requires_reconciliation_when_attested_work_is_unreachable(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gov = root / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({
                "github": {"repository_id": "repo-a", "repository_full_name": "owner/a", "default_branch": "main"},
            }), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({
                "continuity": {"sync_status": "SYNCED", "latest_verified_remote_sha": "w"},
            }), encoding="utf-8")
            result = load_continuity_resume(
                root,
                "repo-a",
                observed_remote_head_sha="p",
                work_reachable=False,
                attestation_is_management_only=True,
                attestation_references_work=True,
                generic_tree_matches=True,
            )
            self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")


if __name__ == "__main__":
    unittest.main()
