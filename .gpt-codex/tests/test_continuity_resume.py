import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class ContinuityResumeTests(unittest.TestCase):
    def test_execution_progress_projection_derives_safe_and_fail_closed_outcomes(self):
        from continuity_resume import classify_execution_progress
        state = {"project_id": "p", "revision": 13, "active_work_unit": "wu"}
        work_unit = {"project_id": "p", "work_unit_id": "wu", "basis_state_revision": 13, "state": "AUTHORIZED"}
        self.assertEqual(classify_execution_progress(state, work_unit, [], instruction_id="i", base_sha="b", safe_postcondition=False), "NOT_STARTED")
        partial = {"project_id": "p", "work_unit_id": "wu", "state_revision": 13, "status": "PARTIAL", "response_to_instruction_id": "i", "git_base_sha": "b", "completion_evidence": {"execution_state": "INCOMPLETE"}}
        self.assertEqual(classify_execution_progress(state, work_unit, [partial], instruction_id="i", base_sha="b", safe_postcondition=False, continuation_authorized=False), "PARTIAL")
        self.assertEqual(classify_execution_progress(state, work_unit, [partial], instruction_id="i", base_sha="b", safe_postcondition=False), "READY_TO_CONTINUE")
        self.assertEqual(classify_execution_progress(state, work_unit, [partial], instruction_id="i", base_sha="b", safe_postcondition=False, side_effect_state="AMBIGUOUS"), "RECONCILIATION_REQUIRED")
        failed = dict(partial, status="FAIL")
        self.assertEqual(classify_execution_progress(state, work_unit, [failed], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        done = dict(partial, status="PASS", completion_evidence={
            "execution_state": "COMPLETED", "process_completed": True, "exit_code": 0,
            "intended_scope": ["x"], "executed_scope": ["x"],
            "test_files_expected": 1, "test_files_executed": 1, "test_count": 1,
            "failure_count": 0, "error_count": 0,
            "validators_expected": ["validate_project"],
            "validators_completed": ["validate_project"],
        })
        self.assertEqual(classify_execution_progress(state, work_unit, [done], instruction_id="i", base_sha="b", safe_postcondition=True), "ALREADY_COMPLETE")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(done, response_to_instruction_id="other")], instruction_id="i", base_sha="b", safe_postcondition=True), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(done, git_base_sha="other")], instruction_id="i", base_sha="b", safe_postcondition=True), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [done], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        validators_mismatch = json.loads(json.dumps(done))
        validators_mismatch["completion_evidence"]["validators_completed"] = []
        self.assertEqual(classify_execution_progress(state, work_unit, [validators_mismatch], instruction_id="i", base_sha="b", safe_postcondition=True), "RECONCILIATION_REQUIRED")
        incomplete_completion = json.loads(json.dumps(done))
        del incomplete_completion["completion_evidence"]["test_files_executed"]
        self.assertEqual(classify_execution_progress(state, work_unit, [incomplete_completion], instruction_id="i", base_sha="b", safe_postcondition=True), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(partial, state_revision=12)], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [partial, done], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        reloaded = json.loads(json.dumps({"state": state, "work_unit": work_unit, "results": [partial]}))
        self.assertEqual(classify_execution_progress(**reloaded, instruction_id="i", base_sha="b", safe_postcondition=False), "READY_TO_CONTINUE")

    def test_execution_progress_projection_requires_concrete_failure_evidence(self):
        from continuity_resume import classify_execution_progress

        state = {"project_id": "p", "revision": 13, "active_work_unit": "wu"}
        work_unit = {"project_id": "p", "work_unit_id": "wu", "basis_state_revision": 13, "state": "AUTHORIZED"}
        failed = {
            "project_id": "p", "work_unit_id": "wu", "state_revision": 13,
            "status": "FAIL", "response_to_instruction_id": "i", "git_base_sha": "b",
        }
        self.assertEqual(classify_execution_progress(state, work_unit, [failed], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        no_signal = dict(failed, completion_evidence={"exit_code": 0, "failure_count": 0, "error_count": 0})
        self.assertEqual(classify_execution_progress(state, work_unit, [no_signal], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(failed, completion_evidence={"exit_code": 1})], instruction_id="i", base_sha="b", safe_postcondition=False), "FAILED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(failed, completion_evidence={"failure_count": 1})], instruction_id="i", base_sha="b", safe_postcondition=False), "FAILED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(failed, completion_evidence={"error_count": 1})], instruction_id="i", base_sha="b", safe_postcondition=False), "FAILED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(failed, state_revision=12, completion_evidence={"exit_code": 1})], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
        self.assertEqual(classify_execution_progress(state, work_unit, [dict(failed, git_base_sha="other", completion_evidence={"exit_code": 1})], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
    def test_pairwise_derivation_rejects_ambiguous_correlated_reviewers(self):
        from continuity_resume import _derive_pairwise_review_facts
        slots = [
            {"slot_id": "impl", "role": "CODEX_IMPLEMENTER", "project_context_id": "ctx", "work_unit_id": "wu"},
            {"slot_id": "review-1", "role": "CODEX_REVIEWER", "project_context_id": "ctx", "work_unit_id": "wu", "review_request_id": "request"},
            {"slot_id": "review-2", "role": "CODEX_REVIEWER", "project_context_id": "ctx", "work_unit_id": "wu", "review_request_id": "request"},
        ]
        result = _derive_pairwise_review_facts(Path("."), {}, {"active_execution_slots": slots}, {"instruction_id": "request", "target_project_context_id": "ctx", "target_work_unit": "wu"})
        self.assertTrue(result["reconciliation_required"])

    def test_pairwise_derivation_rejects_reviewer_without_unique_implementer_peer(self):
        from continuity_resume import _derive_pairwise_review_facts
        slots = [{"slot_id": "review", "role": "CODEX_REVIEWER", "project_context_id": "ctx", "work_unit_id": "wu", "review_request_id": "request"}]
        result = _derive_pairwise_review_facts(Path("."), {}, {"active_execution_slots": slots}, {"instruction_id": "request", "target_project_context_id": "ctx", "target_work_unit": "wu"})
        self.assertTrue(result["reconciliation_required"])

    def test_pairwise_derivation_rejects_identical_implementer_and_reviewer_slot_id(self):
        from continuity_resume import _derive_pairwise_review_facts
        slots = [
            {"slot_id": "shared", "role": "CODEX_IMPLEMENTER", "project_context_id": "ctx", "work_unit_id": "wu"},
            {"slot_id": "shared", "role": "CODEX_REVIEWER", "project_context_id": "ctx", "work_unit_id": "wu", "review_request_id": "request"},
        ]
        result = _derive_pairwise_review_facts(Path("."), {}, {"active_execution_slots": slots}, {"instruction_id": "request", "target_project_context_id": "ctx", "target_work_unit": "wu"})
        self.assertTrue(result["reconciliation_required"])
    def test_pairwise_derivation_uses_full_recovery_for_each_selected_slot(self):
        from continuity_resume import _derive_pairwise_review_facts

        state = {
            "active_execution_slots": [
                {"slot_id": "impl", "role": "CODEX_IMPLEMENTER", "project_context_id": "ctx", "work_unit_id": "wu", "worktree": "impl", "current_head_sha": "a" * 40},
                {"slot_id": "review", "role": "CODEX_REVIEWER", "project_context_id": "ctx", "work_unit_id": "wu", "review_request_id": "request", "worktree": "review", "current_head_sha": "a" * 40},
            ],
        }
        request = {"instruction_id": "request", "target_project_context_id": "ctx", "target_work_unit": "wu", "review_target_revision": "a" * 40}
        def recovery(_root, _control, _state, slot_id, _binding, _facts):
            return {"status": "LATEST_SYNCED_REMOTE_STATE", "reconciliation_required": False,
                    "execution_slot": next(slot for slot in state["active_execution_slots"] if slot["slot_id"] == slot_id)}

        with patch("continuity_resume._execution_slot_recovery", side_effect=recovery) as full_recovery, patch(
            "continuity_resume._canonical_worktree_identity", side_effect=[Path("impl"), Path("review")],
        ):
            _derive_pairwise_review_facts(Path("."), {}, state, request)
        self.assertEqual(full_recovery.call_count, 2)

    def test_pairwise_worktree_identity_distinguishes_aliases_from_real_worktrees(self):
        from continuity_resume import _canonical_worktree_identity

        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "implementation"
            reviewer = Path(td) / "reviewer"
            subprocess.run(["git", "init", "-b", "main", str(root)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "tracked.txt").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "base"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "worktree", "add", "-b", "reviewer", str(reviewer)], check=True, capture_output=True)
            alias = Path(td) / "implementation-alias"
            try:
                alias.symlink_to(root, target_is_directory=True)
            except OSError as exc:
                junction = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(alias), str(root)],
                    capture_output=True,
                    text=True,
                )
                if junction.returncode:
                    self.skipTest(f"symlink/junction unavailable: {exc}; {junction.stderr}")

            self.assertEqual(_canonical_worktree_identity(root), _canonical_worktree_identity(alias))
            self.assertNotEqual(_canonical_worktree_identity(root), _canonical_worktree_identity(reviewer))

    def test_pairwise_fact_derivation_fails_closed_without_a_unique_role_pair(self):
        from continuity_resume import _derive_pairwise_review_facts

        result = _derive_pairwise_review_facts(
            Path("."), {}, {"active_execution_slots": []},
            {"instruction_id": "review", "target_project_context_id": "ctx", "target_work_unit": "wu"},
        )
        self.assertTrue(result["reconciliation_required"])
    def test_resume_marks_only_the_changed_shared_fixture_module_stale(self):
        from continuity_resume import load_continuity_resume
        from test_context_window_resume import GovernedProjectFixture

        with tempfile.TemporaryDirectory() as td:
            fixture = GovernedProjectFixture.write(Path(td))
            result = load_continuity_resume(
                fixture.root,
                "repo-a",
                changed_paths=["src/billing/invoice.ts"],
                candidate_module_ids=["auth", "billing"],
            )

        self.assertEqual(result["stale_modules"], ["billing"])
        self.assertEqual(
            result["module_map_reads"],
            [".gpt-codex/navigation/modules/billing.json"],
        )

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

    def _write_json(self, root, relative_path, payload):
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _write_resume_navigation_fixture(self, root, *, with_map=True, with_checkpoint=True):
        from continuity_resume import fingerprint_file

        self._write_json(root, ".gpt-codex/CONTROL.json", {
            "project_id": "P",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
            "github": {
                "repository_id": "repo-a",
                "repository_full_name": "owner/a",
                "default_branch": "main",
            },
        })
        self._write_json(root, ".gpt-codex/STATE.json", {
            "project_id": "P",
            "revision": 4,
            "state": "VERIFYING",
            "continuity": {
                "current_remote_ref": "refs/heads/main",
                "latest_verified_remote_sha": "p",
                "latest_synced_state_revision": 4,
                "last_verified_result_ref": None,
                "sync_status": "SYNCED",
            },
        })

        context_sources = []
        if with_map:
            project_map = self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
                "project_id": "P",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": "repo-a",
                "anchor_sha": None,
                "architecture_summary": "Authentication session handling.",
                "modules": [{
                    "id": "auth",
                    "purpose": "Manage authentication sessions.",
                    "paths": ["src/auth/"],
                    "entry_points": ["src/auth/session.ts"],
                    "keywords": ["auth", "session"],
                    "module_map": ".gpt-codex/navigation/modules/auth.json",
                    "verified_at_sha": None,
                    "freshness": "UNKNOWN",
                }],
            })
            auth_map = self._write_json(root, ".gpt-codex/navigation/modules/auth.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
                "project_id": "P",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "module_id": "auth",
                "responsibility": "Manage authentication sessions.",
                "tracked_paths": ["src/auth/"],
                "key_files": [{
                    "path": "src/auth/session.ts",
                    "role": "Session implementation.",
                }],
                "interfaces": [],
                "depends_on": [],
                "tests": ["tests/auth/session.test.ts"],
                "configuration": [],
                "data_models": [],
                "read_when": ["Working on authentication sessions."],
                "verified_at_sha": None,
                "freshness": "UNKNOWN",
            })
            context_sources = [
                {
                    "path": ".gpt-codex/navigation/PROJECT_MAP.json",
                    "fingerprint": fingerprint_file(project_map),
                },
                {
                    "path": ".gpt-codex/navigation/modules/auth.json",
                    "fingerprint": fingerprint_file(auth_map),
                },
            ]

        if with_checkpoint:
            checkpoint = self._resume_checkpoint(context_sources, hot_modules=["auth"])
            checkpoint["working_set"]["hot_files"] = ["src/auth/session.ts"]
            self._write_json(root, ".gpt-codex/continuity/RESUME.json", checkpoint)

    def test_resume_uses_fast_route_when_navigation_and_checkpoint_are_fresh(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)

            result = load_continuity_resume(root, "repo-a")

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["resume_mode"], "FAST_RESUME")
            self.assertEqual(result["candidate_modules"], ["auth"])
            self.assertEqual(result["stale_modules"], [])
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [])
            for path in (
                ".gpt-codex/PROJECT.md",
                ".gpt-codex/navigation/PROJECT_MAP.json",
                ".gpt-codex/navigation/modules/auth.json",
            ):
                self.assertNotIn(path, result["required_reads"])

    def test_resume_keeps_fast_mode_for_planned_continuation_reads(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)
            checkpoint_path = root / ".gpt-codex/continuity/RESUME.json"
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["working_set"]["next_required_reads"] = [
                "tests/auth/session.test.ts",
            ]
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")

            result = load_continuity_resume(root, "repo-a")

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["resume_mode"], "FAST_RESUME")
            self.assertEqual(result["required_reads"], ["tests/auth/session.test.ts"])

    def test_resume_treats_unknown_candidate_modules_as_a_map_miss(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)

            result = load_continuity_resume(
                root,
                "repo-a",
                candidate_module_ids=["removed-module"],
            )

            self.assertEqual(result["candidate_modules"], [])
            self.assertEqual(result["map_route"], "MAP_MISS")
            self.assertEqual(result["resume_mode"], "FAST_RESUME")

    def test_resume_normalizes_changed_hot_file_paths_before_targeting_reads(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)

            result = load_continuity_resume(
                root,
                "repo-a",
                changed_paths=["./src/auth/session.ts"],
                candidate_module_ids=["auth"],
            )

            self.assertIn("./src/auth/session.ts", result["required_reads"])

    def test_resume_navigation_fixture_uses_schema_shaped_maps(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)
            project_map = json.loads(
                (root / ".gpt-codex/navigation/PROJECT_MAP.json").read_text(encoding="utf-8")
            )
            auth_map = json.loads(
                (root / ".gpt-codex/navigation/modules/auth.json").read_text(encoding="utf-8")
            )

            self.assertEqual(
                set(project_map),
                {
                    "schema_version",
                    "authority",
                    "project_id",
                    "project_context_id",
                    "repository_id",
                    "anchor_sha",
                    "architecture_summary",
                    "modules",
                },
            )
            self.assertEqual(
                set(project_map["modules"][0]),
                {
                    "id",
                    "purpose",
                    "paths",
                    "entry_points",
                    "keywords",
                    "module_map",
                    "verified_at_sha",
                    "freshness",
                },
            )
            self.assertEqual(
                set(auth_map),
                {
                    "schema_version",
                    "authority",
                    "project_id",
                    "project_context_id",
                    "module_id",
                    "responsibility",
                    "tracked_paths",
                    "key_files",
                    "interfaces",
                    "depends_on",
                    "tests",
                    "configuration",
                    "data_models",
                    "read_when",
                    "verified_at_sha",
                    "freshness",
                },
            )

    def test_resume_uses_delta_route_for_a_changed_candidate_module(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)

            result = load_continuity_resume(
                root,
                "repo-a",
                changed_paths=["src/auth/session.ts"],
                candidate_module_ids=["auth"],
            )

            self.assertEqual(result["map_route"], "MAP_PARTIAL")
            self.assertEqual(result["resume_mode"], "DELTA_RESUME")
            self.assertEqual(result["stale_modules"], ["auth"])
            self.assertIn(
                ".gpt-codex/navigation/modules/auth.json",
                result["module_map_reads"],
            )
            self.assertIn("src/auth/session.ts", result["required_reads"])

    def test_resume_ignores_unrelated_changed_paths_for_candidate_modules(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(root)

            result = load_continuity_resume(
                root,
                "repo-a",
                changed_paths=["docs/unrelated.md"],
                candidate_module_ids=["auth"],
            )

            self.assertEqual(result["stale_modules"], [])
            self.assertNotIn("docs/unrelated.md", result["required_reads"])

    def test_resume_uses_cold_route_when_navigation_and_checkpoint_are_missing(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_resume_navigation_fixture(
                root,
                with_map=False,
                with_checkpoint=False,
            )

            result = load_continuity_resume(root, "repo-a")

            self.assertEqual(result["map_route"], "MAP_MISSING")
            self.assertEqual(result["resume_mode"], "COLD_RESUME")
            self.assertNotEqual(result["resume_mode"], "BOOTSTRAP")

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
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
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

    def test_local_unsynced_resume_returns_all_non_optimization_fields(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gov = root / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({
                "project_id": "P", "project_context_id": "11111111-1111-4111-8111-111111111111",
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
                "github": {
                    "repository_id": "repo-a",
                    "repository_full_name": "owner/a",
                    "default_branch": "main",
                },
            }), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({
                "continuity": {"sync_status": "LOCAL_ONLY"},
            }), encoding="utf-8")

            result = load_continuity_resume(root, "repo-a")

            self.assertEqual(result["resume_mode"], "COLD_RESUME")
            self.assertEqual(result["map_route"], "MAP_MISSING")
            for key in (
                "candidate_modules",
                "stale_modules",
                "module_map_reads",
                "required_reads",
                "hot_modules",
                "hot_files",
                "invalidated_context",
            ):
                self.assertEqual(result[key], [])

    def test_resume_blocks_wrong_repository(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({"project_id": "P", "project_context_id": "11111111-1111-4111-8111-111111111111", "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"}, "github": {"repository_id": "repo-a", "repository_full_name": "o/a", "default_branch": "main"}}), encoding="utf-8")
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
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
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
                "project_id": "P", "project_context_id": "11111111-1111-4111-8111-111111111111",
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
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
            self.assertEqual(result["resume_mode"], "COLD_RESUME")
            self.assertEqual(result["map_route"], "MAP_MISSING")
            for key in (
                "candidate_modules",
                "stale_modules",
                "module_map_reads",
                "required_reads",
                "hot_modules",
                "hot_files",
                "invalidated_context",
            ):
                self.assertEqual(result[key], [])


class ContinuityArtifactReferenceCompatibilityTests(unittest.TestCase):
    def test_legacy_work_unit_without_artifact_refs_remains_valid(self):
        from continuity_resume import _validated_artifact_refs

        self.assertEqual(
            _validated_artifact_refs(Path("."), {"work_unit_id": "legacy"}),
            {"design": None, "plan": None},
        )


class RepositoryHandoffBindingTests(unittest.TestCase):
    def _durable_fixture(self, root, *, with_slot=False):
        import subprocess
        from instruction_envelope import build_instruction_envelope

        remote = root / "owner" / "a"
        remote.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        local = root / "checkout"
        subprocess.run(["git", "clone", str(remote), str(local)], check=True, capture_output=True)

        def git(*args):
            return subprocess.run(["git", "-C", str(local), *args],
                                  check=True, capture_output=True, text=True).stdout.strip()

        def write(path, value):
            destination = local / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.com")
        git("checkout", "-b", "main")
        (local / ".gitignore").write_text(
            ".gpt-codex/STATE.json\n.gpt-codex/work/\n", encoding="utf-8")
        context_id = "11111111-1111-4111-8111-111111111111"
        instruction_id = "22222222-2222-4222-8222-222222222222"
        write(".gpt-codex/CONTROL.json", {
            "project_id": "P", "project_context_id": context_id,
            "project_name": "Fixture", "github": {"repository_id": "repo-a",
            "repository_full_name": "owner/a", "default_branch": "main"},
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
        })
        write(".gpt-codex/STATE.json", {
            "project_id": "P", "revision": 4, "state": "AUTHORIZED",
            "active_work_unit": "historical-work-unit",
            "continuity": {"sync_status": "SYNCED", "latest_verified_remote_sha": "a" * 40,
                           "latest_synced_state_revision": 4,
                           "last_verified_result_ref": None},
        })
        work_path = ".gpt-codex/work-units/new-work-unit.json"
        write(work_path, {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P",
            "work_unit_id": "new-work-unit", "state": "AUTHORIZED", "basis_state_revision": 4,
            "scope": {"owned_paths": ["src/a"], "excluded_paths": []},
            "permissions": {"authorized_actions": ["READ", "MUTATE_APPROVED_SCOPE"]},
        })
        git("add", ".")
        git("commit", "-m", "fixture work unit")
        work_sha = git("rev-parse", "HEAD")
        work_ref = {"path": work_path, "sha": work_sha}
        instruction = build_instruction_envelope(
            "EXECUTION_INSTRUCTION", context_id, "Fixture", 4, "2.7.4",
            target_work_unit="new-work-unit", instruction_id=instruction_id,
            target_work_unit_ref=work_ref, target_github_repository_id="repo-a",
            target_github_repository_full_name="owner/a", scope_paths=["src/a"],
            issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER",
            return_role="GPT_ORCHESTRATOR",
            authorized_actions=["READ", "MUTATE_APPROVED_SCOPE"],
            forbidden_actions=["COMMIT", "PUSH"],
        )
        instruction_path = f".gpt-codex/evidence/instructions/{instruction_id}.json"
        (local / instruction_path).parent.mkdir(parents=True, exist_ok=True)
        from instruction_envelope import canonical_instruction_bytes
        (local / instruction_path).write_bytes(canonical_instruction_bytes(instruction))
        git("add", ".")
        git("commit", "-m", "fixture instruction")
        execution_sha = git("rev-parse", "HEAD")
        state_path = local / ".gpt-codex/STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["continuity"]["latest_verified_remote_sha"] = work_sha
        write(".gpt-codex/STATE.json", state)
        locator = {"repository": "owner/a", "commit_sha": execution_sha,
                   "path": instruction_path, "blob_sha": git("rev-parse", f"HEAD:{instruction_path}")}
        evidence_path = ".gpt-codex/evidence/fixture-evidence.json"
        write(evidence_path, {"evidence_id": "fixture-evidence"})
        result_path = ".gpt-codex/evidence/results/fixture-result.json"
        write(result_path, {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P",
            "work_unit_id": "new-work-unit", "extension": {}, "status": "PASS",
            "result_id": "fixture-result", "response_to_instruction_id": instruction_id,
            "source_project_context_id": context_id,
            "source_project_name": "Fixture", "framework_version": "2.7.4",
            "source_github_repository_id": "repo-a",
            "source_github_repository_full_name": "owner/a",
            "state_revision": 4, "evidence_refs": [evidence_path],
            "completion_gate": "GPT_DECISION", "remote_verification": "VERIFIED",
            "git": {"implementation_sha": execution_sha},
            "next_gpt_action": "REVIEW", "return_to_gpt_required": True,
        })
        git("add", ".")
        git("commit", "-m", "fixture result")
        git("push", "-u", "origin", "main")
        if with_slot:
            head = git("rev-parse", "HEAD")
            slot = {
                "slot_id": "slot-1", "role": "CODEX_IMPLEMENTER", "status": "ACTIVE",
                "work_unit_id": "new-work-unit", "primary_module": "core",
                "project_context_id": context_id, "branch": "main", "worktree": ".",
                "base_sha": head, "current_head_sha": head, "last_accepted_sha": head,
                "instruction_id": instruction_id, "state_revision": 4,
                "next_action": "REVIEW",
            }
            state_path = local / ".gpt-codex/STATE.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["active_work_unit"] = "new-work-unit"
            state["active_execution_slots"] = [slot]
            state["continuity"]["latest_verified_remote_sha"] = head
            write(".gpt-codex/STATE.json", state)
            write(".gpt-codex/work/work.json", {
                "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P",
                "work_unit_id": "new-work-unit", "goal": "Fixture", "scope": {},
                "acceptance": [], "selected_extensions": {}, "state": "AUTHORIZED",
                "basis_state_revision": 4,
            })
        return local, work_ref, locator

    def _commit_result_records(self, root, records):
        import subprocess

        for name, record in records.items():
            (root / ".gpt-codex/evidence/results" / name).write_text(
                json.dumps(record) + "\n", encoding="utf-8")
        for args in (("add", ".gpt-codex/evidence/results"),
                     ("commit", "-m", "result inventory regression"),
                     ("push", "origin", "main")):
            subprocess.run(["git", "-C", str(root), *args],
                           check=True, capture_output=True)

    def _inventory_handoff(self, root, work_ref, locator):
        from continuity_resume import build_repository_handoff

        return build_repository_handoff(
            root, "repo-a", target_work_unit_id="new-work-unit",
            target_work_unit_ref=work_ref, instruction_locator=locator,
            expected_state_revision=4,
        )

    def test_unrelated_legacy_results_without_ids_allow_exact_target_handoff(self):
        import subprocess

        for count in (1, 13, 25):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as td:
                root, work_ref, locator = self._durable_fixture(Path(td))
                records = {f"legacy-{i:02d}.json": {
                    "response_to_instruction_id": f"historical-instruction-{i}",
                    "evidence_refs": [],
                } for i in range(count)}
                self._commit_result_records(root, records)
                paths = [root / ".gpt-codex/evidence/results" / name for name in records]
                before = {path: path.read_bytes() for path in paths}
                result = self._inventory_handoff(root, work_ref, locator)
                self.assertEqual(result["status"], "HANDOFF_READY")
                self.assertEqual(result["result_id"], "fixture-result")
                self.assertEqual(result["result_ref"],
                                 ".gpt-codex/evidence/results/fixture-result.json")
                self.assertEqual(result["instruction_id"],
                                 "22222222-2222-4222-8222-222222222222")
                for path in paths:
                    self.assertEqual(path.read_bytes(), before[path])
                    self.assertNotIn("result_id", json.loads(path.read_bytes()))
                self.assertEqual(subprocess.run(
                    ["git", "-C", str(root), "status", "--porcelain"],
                    check=True, capture_output=True, text=True).stdout, "")

    def test_current_target_result_requires_nonempty_string_id_with_legacy_inventory(self):
        for value in (None, "", "   ", 7, []):
            with self.subTest(result_id=value), tempfile.TemporaryDirectory() as td:
                root, work_ref, locator = self._durable_fixture(Path(td))
                target = json.loads((root / ".gpt-codex/evidence/results/fixture-result.json").read_bytes())
                if value is None:
                    target.pop("result_id")
                else:
                    target["result_id"] = value
                self._commit_result_records(root, {
                    "fixture-result.json": target,
                    "legacy.json": {"response_to_instruction_id": "old-instruction"},
                })
                self.assertEqual(self._inventory_handoff(root, work_ref, locator)["status"],
                                 "RECONCILIATION_REQUIRED")

    def test_duplicate_nonempty_result_ids_reconcile_including_unrelated_history(self):
        for duplicate_id in ("fixture-result", "historical-result"):
            with self.subTest(duplicate_id=duplicate_id), tempfile.TemporaryDirectory() as td:
                root, work_ref, locator = self._durable_fixture(Path(td))
                records = {"legacy.json": {"response_to_instruction_id": "old-instruction"},
                           "historical-a.json": {"result_id": duplicate_id}}
                if duplicate_id != "fixture-result":
                    records["historical-b.json"] = {"result_id": duplicate_id}
                self._commit_result_records(root, records)
                self.assertEqual(self._inventory_handoff(root, work_ref, locator)["status"],
                                 "RECONCILIATION_REQUIRED")

    def test_two_results_matching_current_instruction_still_reconcile(self):
        for second_id in (None, "another-current-result"):
            with self.subTest(second_id=second_id), tempfile.TemporaryDirectory() as td:
                root, work_ref, locator = self._durable_fixture(Path(td))
                second = json.loads((root / ".gpt-codex/evidence/results/fixture-result.json").read_bytes())
                if second_id is None:
                    second.pop("result_id")
                else:
                    second["result_id"] = second_id
                self._commit_result_records(root, {"second-current.json": second})
                self.assertEqual(self._inventory_handoff(root, work_ref, locator)["status"],
                                 "RECONCILIATION_REQUIRED")

    def test_legacy_result_still_requires_committed_clean_parseable_json(self):
        for invalid in ("uncommitted", "dirty", "unparseable"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as td:
                root, work_ref, locator = self._durable_fixture(Path(td))
                legacy_path = root / ".gpt-codex/evidence/results/legacy.json"
                if invalid == "uncommitted":
                    legacy_path.write_text("{}\n", encoding="utf-8")
                elif invalid == "dirty":
                    self._commit_result_records(root, {"legacy.json": {}})
                    legacy_path.write_text('{"dirty": true}\n', encoding="utf-8")
                else:
                    import subprocess
                    legacy_path.write_text("{invalid JSON\n", encoding="utf-8")
                    for args in (("add", "."), ("commit", "-m", "invalid JSON"),
                                 ("push", "origin", "main")):
                        subprocess.run(["git", "-C", str(root), *args],
                                       check=True, capture_output=True)
                self.assertEqual(self._inventory_handoff(root, work_ref, locator)["status"],
                                 "RECONCILIATION_REQUIRED")

    def test_slotless_handoff_uses_exact_instruction_and_result(self):
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = self._durable_fixture(Path(td))
            result = build_repository_handoff(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref=work_ref, instruction_locator=locator,
                expected_state_revision=4,
            )
            self.assertEqual(result["status"], "HANDOFF_READY")
            self.assertEqual(result["result_id"], "fixture-result")
            self.assertNotIn("execution_slot_id", result["current_work"])
            self.assertNotIn("next_authorized_action", result)

    def test_slotless_handoff_rejects_invalid_continuity_commits(self):
        import subprocess
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = self._durable_fixture(Path(td))
            def git(*args, input=None):
                return subprocess.run(["git", "-C", str(root), *args], input=input,
                                      capture_output=True, text=True, check=True).stdout.strip()
            noncommit = git("hash-object", "-w", "--stdin", input="blob")
            unrelated = git("commit-tree", git("rev-parse", "HEAD^{tree}"),
                            "-m", "unrelated")
            state_path = root / ".gpt-codex/STATE.json"
            for sha in ("not-a-sha", "a" * 40, noncommit, unrelated):
                with self.subTest(sha=sha):
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                    state["continuity"]["latest_verified_remote_sha"] = sha
                    state_path.write_text(json.dumps(state), encoding="utf-8")
                    result = build_repository_handoff(
                        root, "repo-a", target_work_unit_id="new-work-unit",
                        target_work_unit_ref=work_ref, instruction_locator=locator,
                        expected_state_revision=4,
                    )
                    self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_slotless_handoff_accepts_exact_verified_head(self):
        import subprocess
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = self._durable_fixture(Path(td))
            head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, check=True).stdout.strip()
            state_path = root / ".gpt-codex/STATE.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["continuity"]["latest_verified_remote_sha"] = head
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result = build_repository_handoff(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref=work_ref, instruction_locator=locator,
                expected_state_revision=4,
            )
            self.assertEqual(result["status"], "HANDOFF_READY")

    def test_instruction_resolution_checks_actual_origin_identity(self):
        import subprocess
        from instruction_envelope import resolve_durable_instruction

        with tempfile.TemporaryDirectory() as td:
            root, _, locator = self._durable_fixture(Path(td))
            def set_origin(url):
                subprocess.run(["git", "-C", str(root), "remote", "set-url", "origin", url],
                               check=True, capture_output=True)
            for url in ("https://github.com/owner/a.git", "git@github.com:owner/a.git"):
                with self.subTest(url=url):
                    set_origin(url)
                    result = resolve_durable_instruction(
                        root, locator, "owner/a", current_state_revision=4)
                    self.assertEqual(result["status"], "INSTRUCTION_RESOLVED")
            set_origin("https://github.com/other/repo.git")
            result = resolve_durable_instruction(root, locator, "owner/a", current_state_revision=4)
            self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
            set_origin("https://github.com/owner/a.git")
            result = resolve_durable_instruction(root, locator, "owner/other", current_state_revision=4)
            self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
            set_origin("https://github.com/owner/other.git")
            result = resolve_durable_instruction(
                root, {**locator, "repository": "owner/other"}, "owner/other",
                current_state_revision=4,
            )
            self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_instruction_resolution_requires_canonical_committed_bytes(self):
        import subprocess
        from instruction_envelope import resolve_durable_instruction

        with tempfile.TemporaryDirectory() as td:
            root, _, locator = self._durable_fixture(Path(td))
            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args],
                                      check=True, capture_output=True, text=True).stdout.strip()
            git("remote", "set-url", "origin", "https://github.com/owner/a.git")
            def resolve(candidate):
                return resolve_durable_instruction(root, candidate, "owner/a",
                                                   current_state_revision=4)["status"]
            self.assertEqual(resolve(locator), "INSTRUCTION_RESOLVED")
            path = root / locator["path"]
            envelope = json.loads(path.read_bytes())
            variants = (
                json.dumps(envelope, ensure_ascii=False, indent=2).encode("utf-8"),
                json.dumps(envelope, ensure_ascii=False, indent=4).encode("utf-8"),
                path.read_bytes() + b"\n",
                json.dumps({**envelope, "target_project_name": "Foreign"},
                           ensure_ascii=False).encode("utf-8"),
            )
            for index, raw in enumerate(variants):
                with self.subTest(index=index):
                    path.write_bytes(raw)
                    git("add", locator["path"])
                    git("commit", "-m", f"variant {index}")
                    candidate = {**locator, "commit_sha": git("rev-parse", "HEAD"),
                                 "blob_sha": git("rev-parse", f"HEAD:{locator['path']}")}
                    self.assertEqual(resolve(candidate), "RECONCILIATION_REQUIRED")
            self.assertEqual(resolve({**locator, "blob_sha": "a" * 40}),
                             "RECONCILIATION_REQUIRED")

    def test_complete_slot_authority_enriches_exact_result_handoff(self):
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            root, work_ref, locator = self._durable_fixture(Path(td), with_slot=True)
            result = build_repository_handoff(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref=work_ref, instruction_locator=locator,
                expected_state_revision=4,
            )
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertEqual(result["current_work"]["execution_slot_id"], "slot-1")

    def test_missing_explicit_bindings_reconcile_without_using_active_work_unit(self):
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            result = build_repository_handoff(
                Path(td), "repo-a", target_work_unit_id=None,
                target_work_unit_ref=None, instruction_locator=None,
                expected_state_revision=None,
            )
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_slotless_repository_handoff_requires_unique_durable_result(self):
        from continuity_resume import build_repository_handoff

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gov = root / ".gpt-codex"
            gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps({
                "project_id": "P", "project_context_id": "11111111-1111-4111-8111-111111111111",
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
                "github": {"repository_id": "repo-a", "repository_full_name": "owner/a", "default_branch": "main"},
            }), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({
                "project_id": "P", "revision": 4, "state": "AUTHORIZED",
                "active_work_unit": "historical-work-unit",
                "continuity": {"sync_status": "SYNCED", "latest_verified_remote_sha": "a" * 40,
                               "latest_synced_state_revision": 4,
                               "last_verified_result_ref": None},
            }), encoding="utf-8")
            result = build_repository_handoff(
                root, "repo-a", target_work_unit_id="new-work-unit",
                target_work_unit_ref={"path": ".gpt-codex/work-units/new-work-unit.json", "sha": "a" * 40},
                instruction_locator={"repository": "owner/a", "commit_sha": "a" * 40,
                                     "path": ".gpt-codex/evidence/instructions/11111111-1111-4111-8111-111111111111.json",
                                     "blob_sha": "b" * 40},
                expected_state_revision=4,
            )
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertNotIn("next_authorized_action", result)


if __name__ == "__main__":
    unittest.main()


class OptionalGithubContractTests(unittest.TestCase):
    """Five semantic regressions over native identity and derived-resource entry points."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.gov = self.root / ".gpt-codex"
        template = Path(__file__).resolve().parents[1] / "project-template"
        self.control = json.loads((template / "CONTROL.template.json").read_text(encoding="utf-8"))
        self.control.pop("github")
        self.control["project_context_id"] = "11111111-1111-4111-8111-111111111111"
        self.control["extensions"] = {"skills": [], "guardrails": [], "fitness": []}
        self.project_map = json.loads((template / "navigation/PROJECT_MAP.template.json").read_text(encoding="utf-8"))
        self.module_map = json.loads((template / "navigation/modules/MODULE_MAP.template.json").read_text(encoding="utf-8"))
        self.checkpoint = json.loads((template / "continuity/RESUME.template.json").read_text(encoding="utf-8"))
        for payload in (self.project_map, self.module_map, self.checkpoint):
            payload["project_context_id"] = self.control["project_context_id"]
        self.state = json.loads((template / "STATE.template.json").read_text(encoding="utf-8"))
        self.adoption_work_unit = {
            "project_id": self.control["project_id"], "work_unit_id": "WU-F001-ADOPTION-PROBE",
            "state": "AUTHORIZED", "basis_state_revision": 0,
        }
        self.adoption_instruction = {
            "target_work_unit": self.adoption_work_unit["work_unit_id"],
            "target_project_context_id": self.control["project_context_id"],
            "expected_state_revision": 0, "executor_role": "CODEX_IMPLEMENTER",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"], "forbidden_actions": [],
        }
        self.write_fixture()

    def write_fixture(self):
        for relative, payload in (("CONTROL.json", self.control), ("STATE.json", self.state),
                                  ("navigation/PROJECT_MAP.json", self.project_map),
                                  ("navigation/modules/MODULE_MAP.example-module.json", self.module_map),
                                  ("continuity/RESUME.json", self.checkpoint)):
            path = self.gov / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload), encoding="utf-8")

    def check_resources(self):
        from context_binding import load_project_identity, evaluate_cross_project_resource_boundary
        from project_navigation import validate_navigation_identity, load_project_map, load_module_map
        from continuity_resume import load_resume_checkpoint
        from validate_project import validate_project_identity_and_derived
        identity = load_project_identity(self.control)
        project_map = load_project_map(self.root)
        module_map = load_module_map(self.root, self.project_map["modules"][0]["module_map"])
        for payload, kind in ((project_map, "PROJECT_MAP"), (module_map, "MODULE_MAP"), (self.checkpoint, "RESUME")):
            decision = evaluate_cross_project_resource_boundary(
                identity, payload, resource_type=kind,
                **({"parent_project_map": project_map} if kind == "MODULE_MAP" else {}))
            self.assertEqual(decision.decision, "ALLOW")
            self.assertFalse(decision.action_executable)
            validate_navigation_identity(payload, self.control, resource_type=kind,
                                         **({"parent_project_map": project_map} if kind == "MODULE_MAP" else {}))
        self.assertEqual(load_resume_checkpoint(self.gov, self.control), self.checkpoint)
        self.assertEqual(validate_project_identity_and_derived(self.root, self.gov, self.control), [])

    def test_local_only_identity_resources_and_continuity(self):
        from context_binding import load_project_identity, evaluate_project_identity
        from continuity_resume import load_continuity_resume
        from validate_project import validate_framework_adoption
        identity = load_project_identity(self.control)
        self.assertEqual((identity.repository_id, identity.repository_full_name, identity.default_branch), (None, None, None))
        self.assertEqual(evaluate_project_identity(self.control).decision, "ALLOW")
        self.assertEqual(validate_framework_adoption(self.control, self.adoption_instruction,
                         self.adoption_work_unit, current_state_revision=0), [])
        self.check_resources()
        resumed = load_continuity_resume(self.root, None)
        self.assertEqual(resumed["status"], "LOCAL_PROJECT_STATE")
        self.assertIsNone(resumed["repository_id"])
        self.assertFalse(resumed["remote_reverification_required"])
        self.assertNotIn("repository_id", self.module_map)

    def test_partial_github_identity_never_bypasses_protected_validation(self):
        from context_binding import evaluate_project_identity
        from project_navigation import validate_navigation_identity
        from continuity_resume import load_resume_checkpoint, load_continuity_resume
        from validate_project import validate_framework_adoption
        self.control["github"] = {"repository_id": "repo-a"}
        self.write_fixture()
        self.assertEqual(evaluate_project_identity(self.control).reason, "PROJECT_IDENTITY_INVALID")
        self.assertEqual(validate_framework_adoption(self.control, self.adoption_instruction,
                         self.adoption_work_unit, current_state_revision=0), ["PROJECT_IDENTITY_INVALID"])
        for call in (lambda: validate_navigation_identity(self.project_map, self.control),
                     lambda: load_resume_checkpoint(self.gov, self.control),
                     lambda: load_continuity_resume(self.root, None)):
            with self.assertRaisesRegex(ValueError, "^PROJECT_IDENTITY_INVALID$"):
                call()

    def test_local_explicit_github_target_is_unbound(self):
        from context_binding import evaluate_project_identity
        from continuity_resume import load_continuity_resume
        from validate_project import validate_framework_adoption
        for expected in ({"expected_repository_id": "repo-a"}, {"expected_repository_full_name": "owner/a"}):
            decision = evaluate_project_identity(self.control, **expected)
            self.assertEqual((decision.decision, decision.reason), ("DENY", "GITHUB_REPOSITORY_UNBOUND"))
        for target in ({"target_github_repository_id": "repo-a"},
                       {"target_github_repository_full_name": "owner/a"}):
            with self.subTest(target=target):
                self.assertEqual(validate_framework_adoption(self.control, dict(self.adoption_instruction, **target),
                                 self.adoption_work_unit, current_state_revision=0), ["GITHUB_REPOSITORY_UNBOUND"])
        with self.assertRaisesRegex(ValueError, "^GITHUB_REPOSITORY_UNBOUND$"):
            load_continuity_resume(self.root, "repo-a")

    def bind_github(self):
        self.control["github"] = {"repository_id": "repo-a", "repository_full_name": "owner/a", "default_branch": "main"}
        self.project_map["repository_id"] = self.checkpoint["repository_id"] = "repo-a"
        self.state["continuity"]["sync_status"] = "SYNCED"
        self.write_fixture()

    def test_bound_github_identity_and_module_parent_chain_match(self):
        from context_binding import evaluate_project_identity
        from continuity_resume import load_continuity_resume
        from validate_project import validate_framework_adoption
        self.bind_github()
        self.assertEqual(evaluate_project_identity(self.control, expected_repository_id="repo-a",
                                                 expected_repository_full_name="owner/a").decision, "ALLOW")
        self.assertEqual(validate_framework_adoption(self.control,
                         dict(self.adoption_instruction, target_github_repository_id="repo-a",
                              target_github_repository_full_name="owner/a"),
                         self.adoption_work_unit, current_state_revision=0), [])
        self.check_resources()
        self.assertEqual(load_continuity_resume(self.root, "repo-a")["status"], "LATEST_SYNCED_REMOTE_STATE")
        self.assertNotIn("repository_id", self.module_map)

    def test_bound_mismatch_and_cross_project_resources_fail_closed(self):
        from context_binding import load_project_identity, evaluate_project_identity, evaluate_cross_project_resource_boundary
        from project_navigation import validate_navigation_identity
        from continuity_resume import load_continuity_resume, load_resume_checkpoint
        from validate_project import validate_framework_adoption
        self.bind_github()
        identity = load_project_identity(self.control)
        self.assertEqual(evaluate_project_identity(self.control, expected_repository_id="foreign").reason, "GITHUB_REPOSITORY_MISMATCH")
        self.assertEqual(evaluate_project_identity(self.control, expected_repository_full_name="foreign/repo").reason, "GITHUB_REPOSITORY_MISMATCH")
        for target, reason in (({"target_github_repository_id": "foreign"}, "GITHUB_REPOSITORY_MISMATCH"),
                               ({"target_github_repository_full_name": "foreign/repo"}, "GITHUB_REPOSITORY_MISMATCH"),
                               ({"target_github_repository_id": ""}, "PROJECT_IDENTITY_INVALID")):
            with self.subTest(target=target):
                self.assertEqual(validate_framework_adoption(self.control, dict(self.adoption_instruction, **target),
                                 self.adoption_work_unit, current_state_revision=0), [reason])
        with self.assertRaisesRegex(ValueError, "^GITHUB_REPOSITORY_MISMATCH$"):
            load_continuity_resume(self.root, "foreign")
        for kind, payload in (("PROJECT_MAP", self.project_map), ("MODULE_MAP", self.module_map), ("RESUME", self.checkpoint)):
            kwargs = {"parent_project_map": self.project_map} if kind == "MODULE_MAP" else {}
            for foreign in (dict(payload, project_id="foreign"),
                            dict(payload, project_context_id="22222222-2222-4222-8222-222222222222")):
                decision = evaluate_cross_project_resource_boundary(identity, foreign, resource_type=kind, **kwargs)
                self.assertEqual((decision.decision, decision.reason), ("DENY", "CROSS_PROJECT_CONTEXT_MISMATCH"))
            if kind != "MODULE_MAP":
                for repository_id in (None, "foreign"):
                    with self.assertRaises(ValueError):
                        validate_navigation_identity(dict(payload, repository_id=repository_id), self.control, resource_type=kind)
        decision = evaluate_cross_project_resource_boundary(identity, self.module_map, resource_type="MODULE_MAP",
                    parent_project_map=dict(self.project_map, repository_id="foreign"))
        self.assertEqual(decision.reason, "GITHUB_REPOSITORY_MISMATCH")
        self.assertEqual(evaluate_cross_project_resource_boundary(identity, self.module_map, resource_type="MODULE_MAP").decision, "DENY")
        self.assertEqual(evaluate_cross_project_resource_boundary(identity, self.module_map, resource_type="MODULE_MAP",
                         parent_project_map=dict(self.project_map, authority="FOREIGN_AUTHORITY")).decision, "DENY")
        with self.assertRaises(ValueError):
            validate_navigation_identity(dict(self.project_map, project_context_id=None), self.control)
        self.checkpoint["repository_id"] = "foreign"
        self.write_fixture()
        with self.assertRaisesRegex(ValueError, "^GITHUB_REPOSITORY_MISMATCH$"):
            load_resume_checkpoint(self.gov, self.control)
