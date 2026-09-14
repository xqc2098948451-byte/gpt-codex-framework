import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from continuity_resume import build_project_handoff  # noqa: E402


class HarnessHandoffTests(unittest.TestCase):
    def git(self, root, *args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def write_json(self, root, relative, value):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_fixture(self, root):
        (root / "docs").mkdir()
        (root / "docs/plan.md").write_text("plan\n", encoding="utf-8")
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        (root / ".gitignore").write_text(".gpt-codex/\n.harness/\n", encoding="utf-8")
        self.git(root, "init")
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "user.name", "Handoff Test")
        self.git(root, "add", ".gitignore", "README.md", "docs/plan.md")
        self.git(root, "commit", "-m", "fixture")
        self.git(root, "switch", "-c", "feature/handoff")
        head = self.git(root, "rev-parse", "HEAD")
        slot = {
            "slot_id": "slot-1", "role": "CODEX_IMPLEMENTER", "status": "ACTIVE",
            "work_unit_id": "WU-1", "primary_module": "framework-core",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "branch": "feature/handoff", "worktree": ".", "base_sha": head,
            "current_head_sha": head, "last_accepted_sha": head, "instruction_id": "22222222-2222-4222-8222-222222222222",
            "state_revision": 1, "next_action": "CONTINUE_IMPLEMENTATION",
        }
        self.write_json(root, ".gpt-codex/CONTROL.json", {
            "project_id": "PROJECT-ONE",
            "project_context_id": slot["project_context_id"],
            "github": {"repository_id": "repo-1", "repository_full_name": "owner/repo", "default_branch": "main"},
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
        })
        self.write_json(root, ".gpt-codex/STATE.json", {
            "revision": 1, "state": "ACTIVE", "active_work_unit": "WU-1",
            "active_execution_slots": [slot],
            "continuity": {"sync_status": "SYNCED", "latest_synced_state_revision": 1,
                           "latest_verified_remote_sha": head, "last_verified_result_ref": None},
        })
        self.write_json(root, ".gpt-codex/work/work.json", {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "PROJECT-ONE",
            "work_unit_id": "WU-1", "goal": "Continue safely.", "scope": {},
            "acceptance": [], "selected_extensions": {}, "state": "AUTHORIZED",
            "basis_state_revision": 1,
            "artifact_refs": {"design": None, "plan": {"path": "docs/plan.md", "sha": head}},
        })
        return head

    def test_handoff_contains_one_safe_next_action_and_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            head = self.write_fixture(root)
            result = build_project_handoff(root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertFalse(result["reconciliation_required"])
        self.assertEqual(result["current_work"]["work_unit_id"], "WU-1")
        self.assertEqual(result["git"]["current_head_sha"], head)
        self.assertEqual(result["accepted_artifacts"]["plan"], {"path": "docs/plan.md", "sha": head})
        self.assertEqual(result["next_action"], "CONTINUE_IMPLEMENTATION")

    def test_multiple_pending_results_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            head = self.write_fixture(root)
            state_path = root / ".gpt-codex/STATE.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            slot = state["active_execution_slots"][0]
            slot.update({"role": "CODEX_REVIEWER", "review_request_id": "33333333-3333-4333-8333-333333333333"})
            self.write_json(root, ".gpt-codex/STATE.json", state)
            for result_id in ("result-a", "result-b"):
                self.write_json(root, f".gpt-codex/evidence/results/{result_id}.json", {
                    "kernel_version": "2.0.0", "schema_version": 1, "result_id": result_id,
                    "project_id": "PROJECT-ONE", "work_unit_id": "WU-1",
                    "extension": {"kind": "SKILL", "id": "verification", "version": "1.0.0"},
                    "status": "LOCAL_COMPLETE", "evidence_refs": [], "completion_gate": "GPT_DECISION",
                    "result_message_type": "REVIEW_RESULT", "response_to_instruction_id": "33333333-3333-4333-8333-333333333333",
                    "responder_role": "CODEX_REVIEWER", "review_target_revision": head, "state_revision": 1,
                })
            result = build_project_handoff(root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_execution_slot_contradiction_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root)
            result = build_project_handoff(root, execution_slot_id="missing")
        self.assertEqual(result["status"], "EXECUTION_CONTEXT_MISMATCH")

    def test_missing_authority_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root)
            (root / ".gpt-codex/work/work.json").unlink()
            result = build_project_handoff(root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_invalid_but_readable_control_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root)
            path = root / ".gpt-codex/CONTROL.json"
            control = json.loads(path.read_text(encoding="utf-8"))
            control["roots"] = {}
            path.write_text(json.dumps(control), encoding="utf-8")
            result = build_project_handoff(root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertTrue(result["reconciliation_required"])

    def test_task_one_strategy_format_is_parsed_and_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root)
            reasoning = root / ".harness/REASONING.md"
            reasoning.parent.mkdir()
            reasoning.write_text(
                "# Development Strategy and Process Record\n\n## Strategy\n"
                "STRATEGY_PROFILE = PROJECT_DEFAULT\nGPT_STRATEGY = MINIMAL_CLOSED_LOOP\n"
                "CODEX_IMPLEMENTER_STRATEGY = MINIMAL_DIFF_TDD\nCODEX_REVIEWER_STRATEGY = CONTRACT_FIRST\n"
                "TASK_SPLITTING = PROJECT_DETERMINED\nREVIEW_POLICY = RISK_OR_MILESTONE\n"
                "INSTRUCTION_POLICY = REFERENCE_FIRST\nRESULT_RETURN_POLICY = DURABLE_REF_FIRST\n"
                "\n## Decision Records\nNOT_A_STRATEGY = ignored\n",
                encoding="utf-8",
            )
            result = build_project_handoff(root, execution_slot_id="slot-1")
        self.assertEqual(result["strategy"]["GPT_STRATEGY"], "MINIMAL_CLOSED_LOOP")
        self.assertEqual(len(result["strategy"]), 8)

    def test_missing_reasoning_is_non_blocking_and_handoff_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fixture(root)
            before = {path.relative_to(root): path.read_bytes() for path in (root / ".gpt-codex").rglob("*") if path.is_file()}
            head = self.git(root, "rev-parse", "HEAD")
            status = self.git(root, "status", "--porcelain")
            result = build_project_handoff(root, execution_slot_id="slot-1")
            after = {path.relative_to(root): path.read_bytes() for path in (root / ".gpt-codex").rglob("*") if path.is_file()}
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), head)
            self.assertEqual(self.git(root, "status", "--porcelain"), status)
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertIsNone(result["strategy"])
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
