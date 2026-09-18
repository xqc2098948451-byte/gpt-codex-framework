import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class GitContinuityTests(unittest.TestCase):
    def test_cleanup_manifest_classifier_is_pure_and_fails_closed(self):
        from git_continuity import classify_cleanup_manifest
        with tempfile.TemporaryDirectory(prefix="manifest-") as temporary:
            root = Path(temporary) / "allowed"
            root.mkdir()
            (root / "中文.txt").write_text("safe", encoding="utf-8")
            before = (root / "中文.txt").read_bytes()
            manifest = {"manifest_id": "m-1", "allowed_root": str(root), "entries": [{"operation": "DELETE", "target": "中文.txt"}]}
            result = classify_cleanup_manifest(manifest, root, {})
            self.assertEqual(result["decision"], "DELETE")
            self.assertEqual((root / "中文.txt").read_bytes(), before)
            self.assertEqual(classify_cleanup_manifest({"manifest_id": "m-1", "allowed_root": str(root), "entries": [{"operation": "KEEP", "target": "中文.txt"}]}, root, {})["decision"], "KEEP")
            for target in ("../outside", str(root / "中文.txt"), "*.txt", "missing.txt"):
                with self.subTest(target=target):
                    self.assertEqual(classify_cleanup_manifest({"manifest_id": "m-1", "allowed_root": str(root), "entries": [{"operation": "DELETE", "target": target}]}, root, {})["decision"], "RECONCILIATION_REQUIRED")
            duplicate = {"manifest_id": "m-1", "allowed_root": str(root), "entries": [{"operation": "DELETE", "target": "中文.txt"}, {"operation": "KEEP", "target": "中文.txt"}]}
            self.assertEqual(classify_cleanup_manifest(duplicate, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertEqual(classify_cleanup_manifest({"entries": [{"operation": "DELETE", "target": "中文.txt"}]}, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertEqual(classify_cleanup_manifest({"manifest_id": "m-1", "allowed_root": str(parent := root.parent), "entries": [{"operation": "DELETE", "target": "中文.txt"}]}, root, {})["decision"], "RECONCILIATION_REQUIRED")

    def test_cleanup_manifest_blocks_symlink_escape_without_mutation(self):
        from git_continuity import classify_cleanup_manifest
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root, outside = parent / "allowed", parent / "outside"
            (root / "safe").mkdir(parents=True); outside.mkdir(); (outside / "file").write_text("outside", encoding="utf-8")
            try:
                (root / "safe" / "link").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink fixture unavailable: {exc}")
            manifest = {"manifest_id": "m-2", "allowed_root": str(root), "entries": [{"operation": "DELETE", "target": "safe/link/file"}]}
            self.assertEqual(classify_cleanup_manifest(manifest, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertTrue((outside / "file").exists())

    def test_cleanup_manifest_blocks_windows_junction_escape_without_mutation(self):
        from git_continuity import classify_cleanup_manifest
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root, outside = parent / "allowed", parent / "outside"
            root.mkdir(); outside.mkdir(); (outside / "target").write_text("outside", encoding="utf-8")
            junction = root / "link"
            created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)], capture_output=True, text=True)
            if created.returncode != 0:
                self.skipTest("junction fixture unavailable on current host")
            manifest = {"manifest_id": "m-junction", "allowed_root": str(root), "entries": [{"operation": "DELETE", "target": "link/target"}]}
            self.assertEqual(classify_cleanup_manifest(manifest, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertEqual((outside / "target").read_text(encoding="utf-8"), "outside")
    def test_canonical_eol_observation_is_stable_for_supported_ambient_values_and_unicode_path(self):
        from git_continuity import observe_canonical_git_facts

        with tempfile.TemporaryDirectory(prefix="中文-") as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "中文.txt").write_bytes(b"line\r\n")
            subprocess.run(["git", "add", "中文.txt"], cwd=root, check=True, capture_output=True)
            expected = None
            for value in ("true", "false", "input", None):
                if value is None:
                    subprocess.run(["git", "config", "--unset-all", "core.autocrlf"], cwd=root, capture_output=True)
                else:
                    subprocess.run(["git", "config", "core.autocrlf", value], cwd=root, check=True, capture_output=True)
                observed = observe_canonical_git_facts(root)
                self.assertTrue(observed["deterministic"])
                self.assertEqual(observed["ambient_autocrlf"], "UNSET" if value is None else value.upper())
                expected = observed["changed_paths"] if expected is None else expected
                self.assertEqual(observed["changed_paths"], expected)

    def test_canonical_eol_observation_fails_closed_for_malformed_config_or_probe_failure(self):
        from git_continuity import observe_canonical_git_facts

        malformed = observe_canonical_git_facts(Path("."), runner=lambda _command, _root: (0, "bogus\n", ""))
        self.assertFalse(malformed["mutation_allowed"])
        failed = observe_canonical_git_facts(Path("."), runner=lambda _command, _root: (1, "", "failure"))
        self.assertFalse(failed["mutation_allowed"])

    def test_lf_index_crlf_worktree_has_ambient_sensitivity_but_canonical_facts_are_equivalent(self):
        from git_continuity import observe_canonical_git_facts

        ambient_paths, canonical_paths = {}, {}
        for value in ("true", "false", "input", None):
            with tempfile.TemporaryDirectory(prefix="a2-eol-") as temporary:
                root = Path(temporary)
                subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
                subprocess.run(["git", "config", "user.name", "A2 Fixture"], cwd=root, check=True, capture_output=True)
                subprocess.run(["git", "config", "user.email", "a2@example.invalid"], cwd=root, check=True, capture_output=True)
                tracked = root / "line-endings.txt"
                tracked.write_bytes(b"alpha\nbeta\n")
                subprocess.run(["git", "add", "line-endings.txt"], cwd=root, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", "LF baseline"], cwd=root, check=True, capture_output=True)
                tracked_bytes = subprocess.run(
                    ["git", "show", "HEAD:line-endings.txt"], cwd=root, check=True, capture_output=True
                ).stdout
                self.assertEqual(tracked_bytes, b"alpha\nbeta\n")
                tracked.write_bytes(b"alpha\r\nbeta\r\n")
                if value is None:
                    subprocess.run(["git", "config", "--unset-all", "core.autocrlf"], cwd=root, capture_output=True)
                else:
                    subprocess.run(["git", "config", "core.autocrlf", value], cwd=root, check=True, capture_output=True)
                ambient = subprocess.run(["git", "diff", "--name-only"], cwd=root, check=True, capture_output=True).stdout
                ambient_paths["unset" if value is None else value] = ambient
                canonical_paths["unset" if value is None else value] = observe_canonical_git_facts(root)["changed_paths"]
                self.assertEqual(tracked.read_bytes(), b"alpha\r\nbeta\r\n")
        self.assertGreater(len(set(ambient_paths.values())), 1, ambient_paths)
        self.assertEqual(len(set(canonical_paths.values())), 1, canonical_paths)
    def test_execution_capability_preflight_allows_supported_remote_route_without_gh(self):
        from git_continuity import evaluate_execution_capability_preflight

        decision = evaluate_execution_capability_preflight({
            "powershell": {"status": "SUPPORTED"}, "python": {"status": "AVAILABLE"},
            "git": {"status": "AVAILABLE"}, "gh": {"status": "ABSENT"},
            "remote": {"available": True}, "unicode_path_round_trip": True,
        })
        self.assertTrue(decision.mutation_allowed)
        self.assertEqual(decision.decision, "CAPABILITY_READY")

    def test_execution_capability_preflight_denies_missing_or_malformed_required_facts_before_mutation(self):
        from git_continuity import evaluate_execution_capability_preflight

        ready = {
            "powershell": {"status": "SUPPORTED"}, "python": {"status": "AVAILABLE"},
            "git": {"status": "AVAILABLE"}, "remote": {"available": True},
            "unicode_path_round_trip": True,
        }
        for key, value in (("powershell", {"status": "UNAVAILABLE"}), ("python", {"status": "UNAVAILABLE"}),
                           ("git", {"status": "UNAVAILABLE"}), ("remote", {"available": False}),
                           ("unicode_path_round_trip", False), ("powershell", "malformed")):
            with self.subTest(key=key, value=value):
                observed = dict(ready)
                observed[key] = value
                decision = evaluate_execution_capability_preflight(observed)
                self.assertFalse(decision.mutation_allowed)
                self.assertIn(decision.decision, {"BLOCKED", "RECONCILIATION_REQUIRED"})
    @classmethod
    def setUpClass(cls):
        cls.available = importlib.util.find_spec("git_continuity") is not None

    def test_continuity_module_exists(self):
        self.assertTrue(self.available, "continuity decision core is required")

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_new_work_requires_clean_synced(self):
        from git_continuity import SyncSnapshot, evaluate_new_work_preflight

        clean = SyncSnapshot("a", "a", "refs/heads/main", False, 0, 0, False)
        offline = SyncSnapshot("a", None, "refs/heads/main", False, 0, 0, False)
        self.assertTrue(evaluate_new_work_preflight(clean, "a", "refs/heads/main", "a", 1, 1).mutation_allowed)
        self.assertFalse(evaluate_new_work_preflight(offline, "a", "refs/heads/main", "a", 1, 1).mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_active_authorized_work_can_degrade_but_cannot_pass_or_start_new_unit(self):
        from git_continuity import evaluate_active_work_degraded_continuation

        decision = evaluate_active_work_degraded_continuation(True, True, True, False, False)
        self.assertTrue(decision.mutation_allowed)
        self.assertFalse(decision.publish_allowed)
        self.assertEqual(decision.decision, "LOCAL_COMPLETE")
        self.assertFalse(evaluate_active_work_degraded_continuation(True, True, True, False, True).mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("git_continuity"), "RED: module not implemented")
    def test_publish_gate_requires_live_remote_verification(self):
        from github_repository_binding import BindingDecision
        from git_continuity import SyncDecision, evaluate_publish_gate

        binding = BindingDecision("ALLOW", "OK", True, True)
        sync = SyncDecision("CLEAN_SYNCED", "OK", True, True)
        self.assertEqual(evaluate_publish_gate(binding, sync, "SUCCEEDED", "VERIFIED", True).decision, "SYNCED")
        self.assertNotEqual(evaluate_publish_gate(binding, sync, "SUCCEEDED", "UNAVAILABLE", True).decision, "SYNCED")

    def test_review_revision_requires_descendant_of_formal_review(self):
        from git_continuity import validate_review_revision

        self.assertEqual(validate_review_revision(None, "b" * 40, lambda _old, _new: False), [])
        self.assertEqual(validate_review_revision("a" * 40, "b" * 40, lambda _old, _new: True), [])
        errors = validate_review_revision("a" * 40, "b" * 40, lambda _old, _new: False)
        self.assertIn("RECONCILIATION_REQUIRED", errors)
        self.assertIn("REVIEWED_REVISION_NOT_ANCESTOR", errors)

    def test_review_revision_rejects_invalid_sha_inputs(self):
        from git_continuity import validate_review_revision

        for previous, candidate in (("bad", "b" * 40), (None, "bad"), ("a" * 40, None)):
            with self.subTest(previous=previous, candidate=candidate):
                errors = validate_review_revision(previous, candidate, lambda _old, _new: True)
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn("REVIEWED_REVISION_INVALID", errors)

    def test_review_history_operations_are_append_only_after_design_plan_review(self):
        from git_continuity import validate_review_history_operation

        for stage in ("DESIGN", "PLAN"):
            for operation in ("EDIT", "COMMIT", "FAST_FORWARD_PUSH", "VERIFY_REMOTE"):
                with self.subTest(stage=stage, operation=operation):
                    self.assertEqual(validate_review_history_operation(stage, operation), [])
            for operation in (
                "AMEND", "REBASE", "RESET_REVIEWED", "FORCE_PUSH", "FORCE_WITH_LEASE",
                "REPLACE_BRANCH", "DELETE_BRANCH", "MERGE_MAIN", "TAG", "RELEASE", "PUBLISH",
            ):
                with self.subTest(stage=stage, operation=operation):
                    errors = validate_review_history_operation(stage, operation)
                    self.assertIn("ROLE_AUTHORITY_CONFLICT", errors)
                    self.assertIn("REVIEW_HISTORY_REWRITE_FORBIDDEN", errors)

        self.assertEqual(validate_review_history_operation("IMPLEMENTATION", "AMEND"), [])

    def test_worktree_cleanup_is_evidence_gated_and_fail_closed(self):
        from git_continuity import evaluate_worktree_cleanup

        self.assertEqual(evaluate_worktree_cleanup(False, True, True, False), "CLEAN")
        for facts in (
            (True, True, True, False),
            (False, False, True, False),
            (False, True, False, False),
            (False, True, True, True),
        ):
            with self.subTest(facts=facts):
                self.assertEqual(evaluate_worktree_cleanup(*facts), "KEEP")
        for position in range(4):
            facts = [False, True, True, False]
            facts[position] = None
            with self.subTest(unknown_position=position):
                self.assertEqual(evaluate_worktree_cleanup(*facts), "KEEP")


if __name__ == "__main__":
    unittest.main()
