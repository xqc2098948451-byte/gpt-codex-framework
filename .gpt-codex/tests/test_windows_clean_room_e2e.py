import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


def environment(powershell="SUPPORTED"):
    git = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
    return {"platform": sys.platform, "python": f"{sys.version_info.major}.{sys.version_info.minor}",
            "git": "AVAILABLE" if git.returncode == 0 else "MISSING", "powershell": powershell}


def evidence(case_id, classification, **observations):
    value = {"case_id": case_id, "environment": environment(), "inputs": sorted(observations),
             "observations": observations, "classification": classification, "diagnostic_refs": []}
    return value


class WindowsCleanRoomE2ETests(unittest.TestCase):
    def assert_evidence(self, value, classification):
        self.assertEqual(set(value), {"case_id", "environment", "inputs", "observations", "classification", "diagnostic_refs"})
        self.assertEqual(value["classification"], classification)

    def test_environment_and_diagnostics_matrix(self):
        from git_continuity import evaluate_execution_capability_preflight
        from github_repository_binding import _run_bounded_diagnostic
        ready = {"powershell": {"status": "SUPPORTED"}, "python": {"status": "AVAILABLE"}, "git": {"status": "AVAILABLE"}, "remote": {"available": True}, "unicode_path_round_trip": True}
        self.assert_evidence(evidence("env-supported", evaluate_execution_capability_preflight(ready).decision), "CAPABILITY_READY")
        for name in ("powershell", "python", "git"):
            self.assertEqual(evaluate_execution_capability_preflight(dict(ready, **{name: {"status": "MISSING"}})).decision, "BLOCKED")
        success = _run_bounded_diagnostic(["tool"], "tool", runner=lambda *_a, **_k: subprocess.CompletedProcess([], 0, "ok", "warn"))
        nonzero = _run_bounded_diagnostic(["tool"], "tool", runner=lambda *_a, **_k: subprocess.CompletedProcess([], 2, "中文", "错误"))
        timeout = _run_bounded_diagnostic(["tool"], "tool", runner=lambda *_a, **_k: (_ for _ in ()).throw(subprocess.TimeoutExpired("tool", 1, output="part", stderr="err")))
        self.assert_evidence(evidence("diagnostic-success", success.completion, stderr=success.stderr), "COMPLETE")
        self.assert_evidence(evidence("diagnostic-nonzero", nonzero.completion, stdout=nonzero.stdout, stderr=nonzero.stderr), "COMPLETE")
        self.assert_evidence(evidence("diagnostic-timeout", timeout.completion, started=timeout.process_started), "INCOMPLETE")

    def test_git_recovery_handoff_and_filesystem_matrix(self):
        from git_continuity import classify_cleanup_manifest, observe_canonical_git_facts
        from continuity_resume import classify_execution_progress, resolve_immutable_artifact
        with tempfile.TemporaryDirectory(prefix="clean-room-中文-") as td:
            root = Path(td)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "中文.txt").write_text("x", encoding="utf-8")
            canonical = []
            for autocrlf in ("true", "false", "input", None):
                if autocrlf is None:
                    subprocess.run(["git", "config", "--unset-all", "core.autocrlf"], cwd=root, capture_output=True)
                else:
                    subprocess.run(["git", "config", "core.autocrlf", autocrlf], cwd=root, check=True, capture_output=True)
                observed = observe_canonical_git_facts(root)
                self.assertTrue(observed["deterministic"]); canonical.append(observed["changed_paths"])
            self.assert_evidence(evidence("git-unicode-autocrlf", "PASS", paths=canonical[0]), "PASS")
            self.assertEqual(canonical, [canonical[0]] * 4)
            manifest = {"manifest_id": "clean", "allowed_root": str(root), "entries": [{"operation": "KEEP", "target": "中文.txt"}]}
            self.assert_evidence(evidence("filesystem-keep", classify_cleanup_manifest(manifest, root, {})["decision"]), "KEEP")
            delete = dict(manifest, entries=[{"operation": "DELETE", "target": "中文.txt"}])
            self.assert_evidence(evidence("filesystem-delete", classify_cleanup_manifest(delete, root, {})["decision"]), "DELETE")
            self.assertTrue((root / "中文.txt").exists())
            state = {"project_id": "p", "revision": 1, "active_work_unit": "w"}; work = {"project_id": "p", "work_unit_id": "w", "basis_state_revision": 1, "state": "AUTHORIZED"}
            partial = {"project_id":"p","work_unit_id":"w","state_revision":1,"status":"PARTIAL","response_to_instruction_id":"i","git_base_sha":"b","completion_evidence":{"execution_state":"INCOMPLETE"}}
            self.assertEqual(classify_execution_progress(state, work, [partial], instruction_id="i", base_sha="b", safe_postcondition=False, continuation_authorized=False), "PARTIAL")
            self.assert_evidence(evidence("recovery-resume", classify_execution_progress(state, work, [partial], instruction_id="i", base_sha="b", safe_postcondition=False)), "READY_TO_CONTINUE")
            complete = dict(partial, status="PASS", completion_evidence={"execution_state":"COMPLETED","process_completed":True,"exit_code":0,"intended_scope":[],"executed_scope":[],"test_files_expected":0,"test_files_executed":0,"test_count":0,"failure_count":0,"error_count":0,"validators_expected":[],"validators_completed":[]})
            self.assertEqual(classify_execution_progress(state, work, [complete], instruction_id="i", base_sha="b", safe_postcondition=True), "ALREADY_COMPLETE")
            self.assertEqual(classify_execution_progress(state, work, [dict(partial, state_revision=2)], instruction_id="i", base_sha="b", safe_postcondition=False), "RECONCILIATION_REQUIRED")
            self.assertEqual(resolve_immutable_artifact(root, {"repository":"owner/repo","commit_sha":"main","path":"中文.txt","blob_sha":"a" * 40}, "owner/repo")["status"], "NOT_AUTHORITY")

    def test_release_phase_matrix_is_observational(self):
        from publication_contract import classify_release_phase
        sha = "a" * 40
        candidate = {"candidate_sha": sha, "candidate_consistent": True}
        local = dict(candidate, local_validation_passed=True, reviewed_sha=sha)
        result = {"status":"PASS", "sync_status":"SYNCED", "remote_verification":"VERIFIED", "publication_authority":"CONFIRMED_PUBLICATION", "remote_head_sha":sha, "evidence_refs":["r"]}
        published = dict(local, publication_result=result)
        self.assertEqual(classify_release_phase(candidate), "CANDIDATE")
        self.assertEqual(classify_release_phase(local), "LOCALLY_VERIFIED")
        self.assertEqual(classify_release_phase(published), "PUBLISHED")
        state = {"state":"COMPLETE", "revision":1, "evidence_refs":["r"], "continuity":{"sync_status":"SYNCED","latest_verified_remote_sha":sha,"latest_synced_state_revision":1,"last_verified_result_ref":"r"}}
        active = dict(published, remote_activation={"status":"VERIFIED","candidate_sha":sha,"evidence_type":"TOOL_OBSERVED"}, state=state, durable_results={"r":result})
        self.assertEqual(classify_release_phase(active), "REMOTE_ACTIVE")

    def test_handoff_and_filesystem_matrix_uses_durable_clean_room_facts(self):
        from continuity_resume import build_project_handoff, resolve_immutable_artifact
        from git_continuity import classify_cleanup_manifest
        helper_path = Path(__file__).with_name("test_harness_handoff.py")
        spec = importlib.util.spec_from_file_location("clean_room_handoff_fixture", helper_path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="clean-handoff-") as td:
            root = Path(td); fixture = module.HarnessHandoffTests(); head = fixture.write_fixture(root)
            first = build_project_handoff(root, execution_slot_id="slot-1")
            self.assertEqual(first["status"], "HANDOFF_READY")
            locator = first["artifact_locator"]["plan"]
            del first
            recovered = build_project_handoff(root, execution_slot_id="slot-1")
            self.assertEqual(recovered["current_work"]["work_unit_id"], "WU-1")
            (root / "docs" / "plan.md").unlink()
            self.assertEqual(resolve_immutable_artifact(root, locator, locator["repository"])["status"], "ALLOW")
            self.assertEqual(resolve_immutable_artifact(root, dict(locator, commit_sha="a" * 40), locator["repository"])["status"], "FAIL")
            self.assertEqual(resolve_immutable_artifact(root, dict(locator, blob_sha="a" * 40), locator["repository"])["status"], "FAIL")
            self.assertEqual(resolve_immutable_artifact(root, dict(locator, repository="other/repo"), locator["repository"])["status"], "FAIL")
            sentinel = root / "sentinel.txt"; sentinel.write_text("keep", encoding="utf-8")
            manifest = {"manifest_id":"fs", "allowed_root":str(root), "entries":[{"operation":"DELETE","target":"../sentinel.txt"}]}
            self.assertEqual(classify_cleanup_manifest(manifest, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_c8_clean_room_durable_evidence_reaches_non_authorizing_management_input(self):
        from framework_feedback import (
            build_framework_management_review_input, build_improvement_candidate,
            build_process_review_from_evidence, derive_framework_feedback,
            framework_feedback_authorizes_mutation, normalize_process_evidence,
        )
        helper_path = Path(__file__).with_name("test_harness_handoff.py")
        spec = importlib.util.spec_from_file_location("c8_clean_room_handoff_fixture", helper_path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="c8-clean-room-") as td:
            root = Path(td)
            head = module.HarnessHandoffTests().write_fixture(root)
            self.assertTrue((root / "docs" / "plan.md").is_file())
            evidence = normalize_process_evidence({
                "source": "durable-clean-room-handoff", "project_context_id": "PRJ-FRAMEWORK-MANAGEMENT",
                "work_unit_id": "framework-staged-closure-group-c-c8-001", "state_revision": 17,
                "result_ref": f"git:{head}:docs/plan.md", "evidence_refs": [f"git:{head}:docs/plan.md"],
                "source_record_refs": ["handoff:slot-1"], "completeness": "COMPLETE", "redactions": ["NONE"],
                "content": {"observation": "durable clean-room evidence consumed", "outcome": "PASS"},
                "process_record": {"work_unit_id": "framework-staged-closure-group-c-c8-001", "final_result": "PASS", "codex_retries": 0,
                                   "gpt_interventions": 0, "review_rounds": 1, "remediation_rounds": 0,
                                   "handoff_result": "HANDOFF_READY", "usage": "UNKNOWN", "git_sha": head,
                                   "result_ref": f"git:{head}:docs/plan.md"},
            })
            review = build_process_review_from_evidence([evidence], "PROJECT_PROFILE_001")
            feedback = derive_framework_feedback(review, [evidence], kind="PRESERVATION_EVIDENCE")
            candidate = build_improvement_candidate(feedback, [evidence], problem_class="PRESERVATION_EVIDENCE", management_question="Does management retain this evidence?")
            management_input = build_framework_management_review_input(review, feedback, candidate, [evidence])
            self.assertEqual((management_input["decision"], management_input["mutation"]), ("NO_DECISION", "NO_MUTATION"))
            self.assertFalse(framework_feedback_authorizes_mutation({"framework_management_only": True}, feedback))

    def test_junction_cleanup_is_rejected_without_mutation(self):
        from git_continuity import classify_cleanup_manifest
        with tempfile.TemporaryDirectory(prefix="clean-junction-") as td:
            parent = Path(td); root, outside = parent / "allowed", parent / "outside"
            root.mkdir(); outside.mkdir(); sentinel = outside / "target"; sentinel.write_text("keep", encoding="utf-8")
            created = subprocess.run(["cmd", "/c", "mklink", "/J", str(root / "link"), str(outside)], capture_output=True, text=True)
            if created.returncode != 0:
                self.skipTest("junction fixture unavailable on current host")
            manifest = {"manifest_id":"junction", "allowed_root":str(root), "entries":[{"operation":"DELETE","target":"link/target"}]}
            self.assertEqual(classify_cleanup_manifest(manifest, root, {})["decision"], "RECONCILIATION_REQUIRED")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
