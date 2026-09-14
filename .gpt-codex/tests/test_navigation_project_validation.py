import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class NavigationProjectValidationTests(unittest.TestCase):
    def _write_json(self, root, relative_path, payload):
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def _write_project(self, root):
        self._write_json(root, ".gpt-codex/CONTROL.json", {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "framework_management_only": True,
            "governance_profile": "FRAMEWORK_MANAGEMENT",
            "framework": {"evaluation_result": "ADOPTED"},
            "roots": {
                "project_role": "AUTHORITATIVE",
                "framework_role": "SELF_MANAGED",
                "framework_kernel_access": "READ_ONLY",
                "framework_builtins_access": "READ_ONLY",
            },
            "extensions": {"skills": [], "guardrails": [], "fitness": []},
        })
        self._write_json(root, ".gpt-codex/STATE.json", {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "revision": 7,
            "state": "ACTIVE",
        })

    def _project_map(self, modules):
        return {
            "schema_version": 1,
            "authority": "DERIVED_NAVIGATION_INDEX",
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": None,
            "anchor_sha": None,
            "architecture_summary": "A project summary.",
            "modules": modules,
        }

    def _module(self, module_id="core", module_map=".gpt-codex/navigation/modules/core.json"):
        return {
            "id": module_id,
            "purpose": "Core behavior.",
            "paths": ["src/core/"],
            "entry_points": ["src/core/index.py"],
            "keywords": ["core"],
            "module_map": module_map,
            "verified_at_sha": None,
            "freshness": "UNKNOWN",
        }

    def _module_map(self, module_id="core", project_id="PROJECT-ONE"):
        return {
            "schema_version": 1,
            "authority": "DERIVED_NAVIGATION_INDEX",
            "project_id": project_id,
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "module_id": module_id,
            "responsibility": "Core behavior.",
            "tracked_paths": ["src/core/"],
            "key_files": [{"path": "src/core/index.py", "role": "Entry point."}],
            "interfaces": [],
            "depends_on": [],
            "tests": [],
            "configuration": [],
            "data_models": [],
            "read_when": [],
            "verified_at_sha": None,
            "freshness": "UNKNOWN",
        }

    def _validate(self, root, *, previous_state=None):
        command = [sys.executable, str(ROOT / ".gpt-codex/scripts/validate_project.py"), str(root)]
        if previous_state is not None:
            command.extend(["--previous-state", str(previous_state)])
        return subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def _state_with_slot(self, status, *, block_reason="AWAITING_REMEDIATION_AUTHORIZATION"):
        return {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "revision": 7,
            "state": "ACTIVE",
            "active_execution_slots": [{
                "slot_id": "CODEX-IMPL-B",
                "role": "CODEX_IMPLEMENTER",
                "status": status,
                "work_unit_id": "framework-design-continuity-sufficiency-implementation-task-1",
                "primary_module": "framework-core",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "branch": "feature/framework-design-continuity-sufficiency-implementation",
                "worktree": "worktrees/feature-framework-design-continuity-sufficiency-implementation",
                "base_sha": "a" * 40,
                "current_head_sha": "b" * 40,
                "last_accepted_sha": None,
                "state_revision": 7,
                "next_action": "CONTINUE_IMPLEMENTATION",
                "instruction_id": "instruction-1",
                "review_request_id": None,
                "review_result_ref": None,
                "finding_ref": None,
                "remediation_authorization_ref": None,
                "fix_instruction_id": None,
                "reviewer_reassignment_ref": None,
                "blocked_from_status": None,
                "block_reason": block_reason,
            }],
        }

    def _slot(self, status, **overrides):
        slot = self._state_with_slot("ACTIVE")["active_execution_slots"][0]
        slot["status"] = status
        if status == "IDLE":
            for field in (
                "work_unit_id", "primary_module", "branch", "worktree", "base_sha",
                "current_head_sha", "last_accepted_sha", "instruction_id",
                "review_request_id", "review_result_ref", "finding_ref",
                "remediation_authorization_ref", "fix_instruction_id",
                "reviewer_reassignment_ref", "blocked_from_status", "block_reason",
            ):
                slot[field] = None
            slot["next_action"] = "AWAIT_ASSIGNMENT"
        elif status == "AWAITING_REVIEW":
            slot["review_request_id"] = "review-request-1"
        elif status == "REVIEWING":
            slot["review_request_id"] = "review-request-1"
            slot["review_result_ref"] = "review-result-1"
        elif status == "BLOCKED":
            slot.update({
                "blocked_from_status": "REVIEWING",
                "block_reason": "AWAITING_REMEDIATION_AUTHORIZATION",
                "review_request_id": "review-request-1",
                "review_result_ref": "review-result-1",
                "finding_ref": "finding-1",
            })
        slot.update(overrides)
        return slot

    def _slot_state(self, revision, slot):
        slot = dict(slot)
        slot["state_revision"] = revision
        return {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "revision": revision,
            "state": "ACTIVE",
            "active_execution_slots": [slot],
        }

    def completed_state(self):
        return self._slot_state(4, self._slot(
            "COMPLETED",
            last_accepted_sha="c" * 40,
            review_request_id="review-request-1",
            review_result_ref=None,
            finding_ref="finding-1",
            remediation_authorization_ref="authorization-1",
            fix_instruction_id="fix-instruction-1",
            reviewer_reassignment_ref="reassignment-1",
            blocked_from_status="REVIEWING",
            block_reason="AWAITING_REMEDIATION_AUTHORIZATION",
        ))

    def active_state(self):
        return self._slot_state(4, self._slot("ACTIVE"))

    def assignment(self, work_unit_id):
        return {
            "work_unit_id": work_unit_id,
            "primary_module": "navigation-continuity",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "branch": "feature/framework-design-continuity-sufficiency-implementation",
            "worktree": "worktrees/feature-framework-design-continuity-sufficiency-implementation",
            "base_sha": "d" * 40,
            "current_head_sha": "e" * 40,
            "instruction_id": "instruction-2",
            "next_action": "CONTINUE_IMPLEMENTATION",
        }

    def _git(self, root, *args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _commit_authoritative_state_history(self, root, previous_slot, current_slot):
        self._write_project(root)
        self._write_json(root, ".gpt-codex/STATE.json", self._slot_state(6, previous_slot))
        self._git(root, "init", "--quiet")
        self._git(root, "config", "user.email", "test@example.invalid")
        self._git(root, "config", "user.name", "State Test")
        self._git(root, "add", ".")
        self._git(root, "commit", "--quiet", "-m", "state revision 6")
        self._write_json(root, ".gpt-codex/STATE.json", self._slot_state(7, current_slot))
        self._git(root, "add", ".gpt-codex/STATE.json")
        self._git(root, "commit", "--quiet", "-m", "state revision 7")

    def test_project_without_navigation_or_resume_is_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)

            result = self._validate(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reset_clears_all_current_assignment_facts(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import reset_completed_slot

        original = self.completed_state()
        reset = reset_completed_slot(original, "CODEX-IMPL-B", ["result-1"], 4)
        slot = reset["active_execution_slots"][0]

        self.assertEqual(reset["revision"], 5)
        self.assertEqual(slot["status"], "IDLE")
        self.assertEqual(slot["state_revision"], 5)
        self.assertEqual(slot["next_action"], "AWAIT_ASSIGNMENT")
        for field in (
            "work_unit_id", "primary_module", "branch", "worktree", "base_sha",
            "current_head_sha", "last_accepted_sha", "instruction_id",
            "review_request_id", "review_result_ref", "finding_ref",
            "remediation_authorization_ref", "fix_instruction_id",
            "reviewer_reassignment_ref", "blocked_from_status", "block_reason",
        ):
            self.assertIsNone(slot[field])
        self.assertEqual(original["revision"], 4)

    def test_activate_requires_idle_and_fresh_values(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(self.active_state(), "CODEX-IMPL-B", self.assignment("WU-2"), 4)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(
                self._slot_state(4, self._slot("IDLE")),
                "CODEX-IMPL-B",
                self.assignment(""),
                4,
            )

    def test_activate_creates_fresh_assignment_after_completed_reset(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot, reset_completed_slot

        reset = reset_completed_slot(self.completed_state(), "CODEX-IMPL-B", ["result-1"], 4)
        activated = activate_execution_slot(reset, "CODEX-IMPL-B", self.assignment("WU-2"), 5)
        slot = activated["active_execution_slots"][0]

        self.assertEqual(activated["revision"], 6)
        self.assertEqual(slot["status"], "ACTIVE")
        self.assertEqual(slot["state_revision"], 6)
        self.assertEqual(slot["work_unit_id"], "WU-2")
        self.assertEqual(slot["primary_module"], "navigation-continuity")
        self.assertEqual(slot["instruction_id"], "instruction-2")
        self.assertEqual(slot["last_accepted_sha"], None)
        self.assertEqual(slot["review_request_id"], None)
        self.assertEqual(slot["finding_ref"], None)
        self.assertEqual(slot["block_reason"], None)

    def test_slot_assignment_rejects_stale_revision_and_double_assignment(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot, reset_completed_slot

        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            reset_completed_slot(self.completed_state(), "CODEX-IMPL-B", ["result-1"], 3)
        reset = reset_completed_slot(self.completed_state(), "CODEX-IMPL-B", ["result-1"], 4)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(reset, "CODEX-IMPL-B", self.assignment("WU-2"), 4)
        activated = activate_execution_slot(reset, "CODEX-IMPL-B", self.assignment("WU-2"), 5)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(activated, "CODEX-IMPL-B", self.assignment("WU-3"), 6)

    def test_reset_rejects_every_non_completed_slot_status(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import reset_completed_slot

        for status in ("IDLE", "ACTIVE", "BLOCKED", "AWAITING_REVIEW", "REVIEWING"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    reset_completed_slot(
                        self._slot_state(4, self._slot(status)),
                        "CODEX-IMPL-B",
                        ["result-1"],
                        4,
                    )

    def test_reset_rejects_invalid_closure_references(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import reset_completed_slot

        for closure_refs in (None, [], (), "", "result-1", [""], ["   "], [123], ["result-1", ""], ["result-1", None]):
            with self.subTest(closure_refs=closure_refs):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    reset_completed_slot(self.completed_state(), "CODEX-IMPL-B", closure_refs, 4)

        reset = reset_completed_slot(self.completed_state(), "CODEX-IMPL-B", ["result-1"], 4)
        self.assertEqual(reset["active_execution_slots"][0]["status"], "IDLE")

    def test_activation_requires_every_declared_assignment_field(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        for field in (
            "work_unit_id", "primary_module", "project_context_id", "branch", "worktree",
            "base_sha", "current_head_sha", "instruction_id", "next_action",
        ):
            with self.subTest(field=field):
                assignment = self.assignment("WU-2")
                del assignment[field]
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    activate_execution_slot(
                        self._slot_state(4, self._slot("IDLE")),
                        "CODEX-IMPL-B",
                        assignment,
                        4,
                    )

    def test_activation_rejects_extra_fields_and_mismatched_project_context(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        extra = self.assignment("WU-2")
        extra["unexpected_field"] = "value"
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(self._slot_state(4, self._slot("IDLE")), "CODEX-IMPL-B", extra, 4)

        mismatched_context = self.assignment("WU-2")
        mismatched_context["project_context_id"] = "22222222-2222-4222-8222-222222222222"
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(
                self._slot_state(4, self._slot("IDLE")),
                "CODEX-IMPL-B",
                mismatched_context,
                4,
            )

        activated = activate_execution_slot(
            self._slot_state(4, self._slot("IDLE")),
            "CODEX-IMPL-B",
            self.assignment("WU-2"),
            4,
        )
        self.assertEqual(activated["active_execution_slots"][0]["project_context_id"], "11111111-1111-4111-8111-111111111111")

    def test_activation_rejects_malformed_sha_fields(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        invalid_shas = ("", "abc", "a" * 39, "a" * 41, "g" * 40, None)
        for field in ("base_sha", "current_head_sha"):
            for value in invalid_shas:
                with self.subTest(field=field, value=value):
                    assignment = self.assignment("WU-2")
                    assignment[field] = value
                    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                        activate_execution_slot(
                            self._slot_state(4, self._slot("IDLE")),
                            "CODEX-IMPL-B",
                            assignment,
                            4,
                        )

    def test_activation_rejects_empty_string_assignment_fields(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        for field in ("work_unit_id", "primary_module", "project_context_id", "instruction_id", "next_action"):
            for value in ("", "   "):
                with self.subTest(field=field, value=value):
                    assignment = self.assignment("WU-2")
                    assignment[field] = value
                    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                        activate_execution_slot(
                            self._slot_state(4, self._slot("IDLE")),
                            "CODEX-IMPL-B",
                            assignment,
                            4,
                        )
        assignment = self.assignment("WU-2")
        assignment["next_action"] = "AWAIT_ASSIGNMENT"
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            activate_execution_slot(self._slot_state(4, self._slot("IDLE")), "CODEX-IMPL-B", assignment, 4)

    def test_activation_validates_branch_and_worktree_shapes(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import activate_execution_slot

        for field in ("branch", "worktree"):
            for value in (None, "local-value"):
                with self.subTest(field=field, valid_value=value):
                    assignment = self.assignment("WU-2")
                    assignment[field] = value
                    activated = activate_execution_slot(
                        self._slot_state(4, self._slot("IDLE")),
                        "CODEX-IMPL-B",
                        assignment,
                        4,
                    )
                    self.assertEqual(activated["active_execution_slots"][0][field], value)
            for value in ("", "   ", 123, {}):
                with self.subTest(field=field, invalid_value=value):
                    assignment = self.assignment("WU-2")
                    assignment[field] = value
                    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                        activate_execution_slot(
                            self._slot_state(4, self._slot("IDLE")),
                            "CODEX-IMPL-B",
                            assignment,
                            4,
                        )

    def reviewing_state(self):
        return self._slot_state(8, self._slot(
            "REVIEWING",
            work_unit_id="WU-1",
            primary_module="navigation-continuity",
            base_sha="a" * 40,
            current_head_sha="a" * 40,
            review_request_id="review-request-1",
            review_result_ref=None,
        ))

    def blocked_state(self):
        return self._slot_state(8, self._slot(
            "BLOCKED",
            work_unit_id="WU-1",
            primary_module="navigation-continuity",
            base_sha="a" * 40,
            current_head_sha="a" * 40,
            last_accepted_sha="a" * 40,
            review_request_id="review-request-1",
            review_result_ref="review-result-1",
            finding_ref="finding-1",
            remediation_authorization_ref="authorization-1",
            fix_instruction_id="fix-instruction-1",
            blocked_from_status="REVIEWING",
            block_reason="AWAITING_REMEDIATION_AUTHORIZATION",
        ))

    def valid_fix_instruction(
        self,
        instruction_id="fix-instruction-1",
        *,
        expected_state_revision=8,
        target_work_unit="WU-1",
        finding_ids=None,
    ):
        return {
            "instruction_id": instruction_id,
            "instruction_type": "FIX_INSTRUCTION",
            "issuer_role": "GPT_ORCHESTRATOR",
            "executor_role": "CODEX_IMPLEMENTER",
            "return_role": "GPT_ORCHESTRATOR",
            "expected_state_revision": expected_state_revision,
            "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": ["PUBLISH"],
            "target_work_unit": target_work_unit,
            "scope_paths": [".gpt-codex/scripts/continuity_resume.py"],
            "finding_ids": ["finding-1"] if finding_ids is None else finding_ids,
            "in_response_to_result_id": "22222222-2222-4222-8222-222222222222",
            "expected_base_sha": "a" * 40,
            "fix_round": 1,
        }

    def complete_authoritative_facts(self):
        return {
            "work_unit": {"work_unit_id": "WU-1"},
            "review_request": {"review_request_id": "review-request-1"},
            "review_result": {"review_result_ref": "review-result-1", "review_target_revision": "a" * 40},
            "finding": {"finding_ref": "finding-1", "review_target_revision": "a" * 40},
            "remediation_authorization": {
                "remediation_authorization_ref": "authorization-1",
                "issuer_role": "GPT_ORCHESTRATOR",
            },
            "current_git": {"current_head_sha": "a" * 40},
        }

    def task5_slot(self, **overrides):
        slot = self._slot(
            "AWAITING_REVIEW",
            work_unit_id="WU-1",
            primary_module="navigation-continuity",
            project_context_id="11111111-1111-4111-8111-111111111111",
            branch="feature/task-5",
            worktree=".",
            base_sha="a" * 40,
            current_head_sha="a" * 40,
            last_accepted_sha="a" * 40,
            instruction_id="instruction-1",
            review_request_id="review-request-1",
            review_result_ref=None,
            next_action="AWAIT_REVIEW",
        )
        slot["state_revision"] = 8
        slot.update(overrides)
        return slot

    def task5_binding(self, slot):
        return {
            field: slot[field]
            for field in (
                "project_context_id", "work_unit_id", "role", "primary_module", "branch",
                "worktree", "base_sha", "current_head_sha", "last_accepted_sha", "state_revision",
            )
        }

    def task5_authoritative_facts(self):
        return {
            "work_unit_id": "WU-1",
            "instruction_id": "instruction-1",
            "review_request_id": "review-request-1",
            "review_result_ref": None,
            "current_git_sha": "a" * 40,
            "git_ancestry_valid": True,
            "state_revision": 8,
            "worktree_clean": True,
            "worktree_unambiguous": True,
        }

    def _write_task5_project(self, root, slot):
        self._write_project(root)
        control_path = root / ".gpt-codex/CONTROL.json"
        control = json.loads(control_path.read_text(encoding="utf-8"))
        control["github"] = {
            "repository_id": "repo-a",
            "repository_full_name": "owner/repo-a",
            "default_branch": "main",
        }
        self._write_json(root, ".gpt-codex/CONTROL.json", control)
        self._write_json(root, ".gpt-codex/STATE.json", {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "revision": 8,
            "state": "ACTIVE",
            "active_work_unit": "WU-1",
            "active_execution_slots": [slot],
            "continuity": {
                "current_remote_ref": "refs/heads/main",
                "latest_verified_remote_sha": "a" * 40,
                "latest_synced_state_revision": 8,
                "last_verified_result_ref": "result-1",
                "sync_status": "SYNCED",
            },
        })

    def _task5_work_unit(self, *, basis_state_revision=8):
        return {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "work_unit_id": "WU-1",
            "goal": "Await an independent review.",
            "scope": {
                "owned_paths": [".gpt-codex/scripts/continuity_resume.py"],
                "excluded_paths": [],
            },
            "acceptance": ["Review request is ready."],
            "selected_extensions": {"skills": [], "guardrails": [], "fitness": []},
            "permissions": {},
            "state": "AUTHORIZED",
            "basis_state_revision": basis_state_revision,
        }

    def _task5_review_result(self, head):
        return {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "result_id": "review-result-1",
            "project_id": "PROJECT-ONE",
            "work_unit_id": "WU-1",
            "extension": {"kind": "SKILL", "id": "verification", "version": "1.0.0"},
            "status": "LOCAL_COMPLETE",
            "evidence_refs": [],
            "completion_gate": "GPT_DECISION",
            "result_message_type": "REVIEW_RESULT",
            "response_to_instruction_id": "review-request-1",
            "responder_role": "CODEX_REVIEWER",
            "review_target_revision": head,
            "state_revision": 8,
        }

    def _git(self, root, *args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _write_task5_durable_project(
        self, root, *, include_work_unit=True, work_units=None, include_result=False,
        state_revision=8,
    ):
        self._write_task5_project(root, self.task5_slot())
        (root / ".gitignore").write_text(
            ".gpt-codex/CONTROL.json\n.gpt-codex/STATE.json\n.gpt-codex/work/\n.gpt-codex/evidence/\n.gpt-codex/continuity/\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("task-5 durable recovery fixture\n", encoding="utf-8")
        self._git(root, "init")
        self._git(root, "config", "user.email", "test@example.invalid")
        self._git(root, "config", "user.name", "Task Five Test")
        self._git(root, "add", ".gitignore", "README.md")
        self._git(root, "commit", "-m", "fixture baseline")
        self._git(root, "switch", "-c", "feature/task-5")
        head = self._git(root, "rev-parse", "HEAD")
        slot = self.task5_slot(
            base_sha=head,
            current_head_sha=head,
            last_accepted_sha=head,
            branch="feature/task-5",
        )
        slot["state_revision"] = state_revision
        self._write_task5_project(root, slot)
        state_path = root / ".gpt-codex/STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["revision"] = state_revision
        state["active_execution_slots"][0] = slot
        state["continuity"]["latest_synced_state_revision"] = state_revision
        state["continuity"]["latest_verified_remote_sha"] = head
        self._write_json(root, ".gpt-codex/STATE.json", state)
        if include_result:
            slot["review_result_ref"] = "review-result-1"
            state["active_execution_slots"][0] = slot
            self._write_json(root, ".gpt-codex/STATE.json", state)
            result = self._task5_review_result(head)
            result["state_revision"] = state_revision
            self._write_json(root, ".gpt-codex/evidence/results/review-result-1.json", result)
        if include_work_unit:
            records = [self._task5_work_unit(basis_state_revision=state_revision)] if work_units is None else work_units
            for index, record in enumerate(records):
                self._write_json(root, f".gpt-codex/work/record-{index}.json", record)
        self.assertEqual(self._git(root, "status", "--porcelain"), "")
        return slot

    def task5_resume(self, *, slot=None, binding=None, facts=None):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            slot = self.task5_slot() if slot is None else slot
            self._write_task5_project(root, slot)
            return load_continuity_resume(
                root,
                "repo-a",
                execution_slot_id="CODEX-IMPL-B",
                execution_slot_binding=self.task5_binding(slot) if binding is None else binding,
                authoritative_facts=self.task5_authoritative_facts() if facts is None else facts,
            )

    def task5_durable_resume(
        self, *, include_work_unit=True, work_units=None, include_result=False,
        state_revision=8, facts=None, binding=None,
    ):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            slot = self._write_task5_durable_project(
                root,
                include_work_unit=include_work_unit,
                work_units=work_units,
                include_result=include_result,
                state_revision=state_revision,
            )
            return load_continuity_resume(
                root,
                "repo-a",
                execution_slot_id="CODEX-IMPL-B",
                execution_slot_binding=self.task5_binding(slot) if binding is None else binding,
                authoritative_facts=facts,
            )

    def test_finding_blocks_but_does_not_authorize_resumption_or_mutate_input(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import block_for_remediation, resume_authorized_remediation

        source = self.reviewing_state()
        source_before = json.loads(json.dumps(source))
        blocked = block_for_remediation(source, "CODEX-IMPL-B", "finding-1", "review-result-1", 8)
        slot = blocked["active_execution_slots"][0]
        self.assertEqual(slot["status"], "BLOCKED")
        self.assertEqual(slot["blocked_from_status"], "REVIEWING")
        self.assertEqual(slot["block_reason"], "AWAITING_REMEDIATION_AUTHORIZATION")
        self.assertEqual(source, source_before)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            resume_authorized_remediation(
                blocked, "CODEX-IMPL-B", None, None, 9,
                authoritative_facts=self.complete_authoritative_facts(),
            )

    def test_block_for_remediation_rejects_invalid_preconditions(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import block_for_remediation

        for status in ("IDLE", "ACTIVE", "BLOCKED", "AWAITING_REVIEW", "COMPLETED"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    block_for_remediation(
                        self._slot_state(8, self._slot(status)),
                        "CODEX-IMPL-B", "finding-1", "review-result-1", 8,
                    )
        for finding_ref, review_ref in (("", "review-result-1"), ("   ", "review-result-1"), ("finding-1", ""), ("finding-1", "   "), (None, "review-result-1"), ("finding-1", None)):
            with self.subTest(finding_ref=finding_ref, review_ref=review_ref):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    block_for_remediation(self.reviewing_state(), "CODEX-IMPL-B", finding_ref, review_ref, 8)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            block_for_remediation(self.reviewing_state(), "CODEX-IMPL-B", "finding-1", "review-result-1", 7)

    def test_remediation_resume_rejects_each_causal_mismatch(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        for mismatch in (
            "finding_ref", "review_request_id", "review_result_ref",
            "remediation_authorization_ref", "fix_instruction_id", "work_unit_id",
            "reviewed_current_sha", "state_revision",
        ):
            with self.subTest(mismatch=mismatch):
                state = self.blocked_state()
                facts = self.complete_authoritative_facts()
                authorization_ref = "authorization-1"
                instruction = self.valid_fix_instruction()
                slot = state["active_execution_slots"][0]
                if mismatch == "reviewed_current_sha":
                    facts["current_git"]["current_head_sha"] = "b" * 40
                elif mismatch == "state_revision":
                    state["revision"] = 7
                elif mismatch == "fix_instruction_id":
                    instruction["instruction_id"] = "fix-instruction-2"
                elif mismatch == "remediation_authorization_ref":
                    authorization_ref = "authorization-2"
                elif mismatch == "work_unit_id":
                    facts["work_unit"]["work_unit_id"] = "WU-2"
                else:
                    facts_key = {
                        "finding_ref": ("finding", "finding_ref"),
                        "review_request_id": ("review_request", "review_request_id"),
                        "review_result_ref": ("review_result", "review_result_ref"),
                    }[mismatch]
                    facts[facts_key[0]][facts_key[1]] = "mismatch"
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        state, "CODEX-IMPL-B", authorization_ref, instruction, 8,
                        authoritative_facts=facts,
                    )

    def test_remediation_resume_rejects_incomplete_or_malformed_authority(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        for missing_key in (
            "work_unit", "finding", "review_request", "review_result",
            "remediation_authorization", "current_git",
        ):
            with self.subTest(missing_key=missing_key):
                facts = self.complete_authoritative_facts()
                del facts[missing_key]
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        self.blocked_state(), "CODEX-IMPL-B", "authorization-1",
                        self.valid_fix_instruction(), 8, authoritative_facts=facts,
                    )
        for subset in (
            {"finding": self.complete_authoritative_facts()["finding"]},
            {"review_result": self.complete_authoritative_facts()["review_result"]},
            {"remediation_authorization": self.complete_authoritative_facts()["remediation_authorization"]},
            {"current_git": self.complete_authoritative_facts()["current_git"]},
            {"reviewer_message": "resume now"},
            None,
            "not-a-mapping",
        ):
            with self.subTest(subset=subset):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        self.blocked_state(), "CODEX-IMPL-B", "authorization-1",
                        self.valid_fix_instruction(), 8, authoritative_facts=subset,
                    )

    def test_remediation_resume_rejects_non_blocked_and_invalid_authorization_or_instruction(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        for state in (
            self.reviewing_state(),
            self._slot_state(8, self._slot("ACTIVE")),
            self._slot_state(8, self._slot("BLOCKED", blocked_from_status="ACTIVE")),
            self._slot_state(8, self._slot("BLOCKED", block_reason="OTHER")),
        ):
            with self.subTest(state=state["active_execution_slots"][0]["status"]):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        state, "CODEX-IMPL-B", "authorization-1", self.valid_fix_instruction(), 8,
                        authoritative_facts=self.complete_authoritative_facts(),
                    )
        invalid_authority = self.complete_authoritative_facts()
        invalid_authority["remediation_authorization"]["issuer_role"] = "CODEX_REVIEWER"
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            resume_authorized_remediation(
                self.blocked_state(), "CODEX-IMPL-B", "authorization-1", self.valid_fix_instruction(), 8,
                authoritative_facts=invalid_authority,
            )
        invalid_instruction = self.valid_fix_instruction()
        invalid_instruction["issuer_role"] = "CODEX_REVIEWER"
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            resume_authorized_remediation(
                self.blocked_state(), "CODEX-IMPL-B", "authorization-1", invalid_instruction, 8,
                authoritative_facts=self.complete_authoritative_facts(),
            )
        malformed_instruction = self.valid_fix_instruction(finding_ids=None)
        malformed_instruction["finding_ids"] = None
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            resume_authorized_remediation(
                self.blocked_state(), "CODEX-IMPL-B", "authorization-1", malformed_instruction, 8,
                authoritative_facts=self.complete_authoritative_facts(),
            )

    def test_complete_current_remediation_chain_resumes_without_mutating_inputs(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        state = self.blocked_state()
        facts = self.complete_authoritative_facts()
        state_before = json.loads(json.dumps(state))
        facts_before = json.loads(json.dumps(facts))
        resumed = resume_authorized_remediation(
            state, "CODEX-IMPL-B", "authorization-1", self.valid_fix_instruction(), 8,
            authoritative_facts=facts,
        )
        slot = resumed["active_execution_slots"][0]
        self.assertEqual(resumed["revision"], 9)
        self.assertEqual(slot["state_revision"], 9)
        self.assertEqual(slot["status"], "ACTIVE")
        self.assertEqual(slot["work_unit_id"], "WU-1")
        self.assertEqual(slot["finding_ref"], "finding-1")
        self.assertEqual(slot["remediation_authorization_ref"], "authorization-1")
        self.assertEqual(state, state_before)
        self.assertEqual(facts, facts_before)

    def test_real_block_authorization_fix_resume_chain_is_atomic(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import block_for_remediation, resume_authorized_remediation

        source = self.reviewing_state()
        source_before = json.loads(json.dumps(source))
        blocked = block_for_remediation(source, "CODEX-IMPL-B", "finding-1", "review-result-1", 8)
        blocked_before = json.loads(json.dumps(blocked))
        blocked_slot = blocked["active_execution_slots"][0]
        self.assertEqual(blocked["revision"], 9)
        self.assertEqual(blocked_slot["status"], "BLOCKED")
        self.assertIsNone(blocked_slot["remediation_authorization_ref"])
        self.assertIsNone(blocked_slot["fix_instruction_id"])

        resumed = resume_authorized_remediation(
            blocked,
            "CODEX-IMPL-B",
            "authorization-1",
            self.valid_fix_instruction(expected_state_revision=9),
            9,
            authoritative_facts=self.complete_authoritative_facts(),
        )
        slot = resumed["active_execution_slots"][0]
        self.assertEqual(resumed["revision"], 10)
        self.assertEqual(slot["state_revision"], 10)
        self.assertEqual(slot["status"], "ACTIVE")
        self.assertEqual(slot["work_unit_id"], "WU-1")
        self.assertEqual(slot["finding_ref"], "finding-1")
        self.assertEqual(slot["remediation_authorization_ref"], "authorization-1")
        self.assertEqual(slot["fix_instruction_id"], "fix-instruction-1")
        self.assertEqual(source, source_before)
        self.assertEqual(blocked, blocked_before)

    def test_remediation_fix_instruction_must_bind_current_work_unit_and_finding(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        for instruction in (
            self.valid_fix_instruction(target_work_unit="WU-OTHER"),
            self.valid_fix_instruction(finding_ids=["finding-OTHER"]),
        ):
            with self.subTest(instruction=instruction):
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        self.blocked_state(),
                        "CODEX-IMPL-B",
                        "authorization-1",
                        instruction,
                        8,
                        authoritative_facts=self.complete_authoritative_facts(),
                    )

    def test_remediation_rejects_preexisting_contradictory_correlations(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import resume_authorized_remediation

        for field, value in (
            ("remediation_authorization_ref", "authorization-old"),
            ("fix_instruction_id", "fix-old"),
        ):
            with self.subTest(field=field):
                state = self.blocked_state()
                state["active_execution_slots"][0][field] = value
                with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
                    resume_authorized_remediation(
                        state,
                        "CODEX-IMPL-B",
                        "authorization-1",
                        self.valid_fix_instruction(),
                        8,
                        authoritative_facts=self.complete_authoritative_facts(),
                    )

    def test_real_block_chain_requires_fix_instruction_for_blocked_revision(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import block_for_remediation, resume_authorized_remediation

        blocked = block_for_remediation(
            self.reviewing_state(), "CODEX-IMPL-B", "finding-1", "review-result-1", 8,
        )
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            resume_authorized_remediation(
                blocked,
                "CODEX-IMPL-B",
                "authorization-1",
                self.valid_fix_instruction(expected_state_revision=8),
                9,
                authoritative_facts=self.complete_authoritative_facts(),
            )

    def test_execution_slot_binding_mismatch_matrix(self):
        for field in (
            "project_context_id", "work_unit_id", "role", "primary_module", "branch",
            "worktree", "base_sha", "current_head_sha", "last_accepted_sha", "state_revision",
        ):
            with self.subTest(field=field):
                slot = self.task5_slot()
                binding = self.task5_binding(slot)
                binding[field] = 7 if field == "state_revision" else "mismatch"
                result = self.task5_resume(slot=slot, binding=binding)
                self.assertEqual(result["status"], "EXECUTION_SLOT_MISMATCH")
                self.assertTrue(result["reconciliation_required"])

    def test_cold_recovery_rejects_forged_caller_authority_without_durable_records(self):
        result = self.task5_resume(facts=self.task5_authoritative_facts())
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertTrue(result["reconciliation_required"])

    def test_cold_recovery_requires_a_real_work_unit_even_when_caller_claims_authority(self):
        result = self.task5_durable_resume(
            include_work_unit=False,
            facts=self.task5_authoritative_facts(),
        )
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertTrue(result["reconciliation_required"])

    def test_cold_recovery_uses_real_work_unit_and_git_without_caller_authority(self):
        result = self.task5_durable_resume()
        self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
        self.assertFalse(result["reconciliation_required"])
        self.assertEqual(result["next_action"], "AWAIT_REVIEW")

    def test_cold_recovery_accepts_template_work_unit_and_historical_basis_revision(self):
        work_unit = self._task5_work_unit(basis_state_revision=8)
        result = self.task5_durable_resume(work_units=[work_unit], state_revision=9)
        self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
        self.assertEqual(result["next_action"], "AWAIT_REVIEW")

    def test_cold_recovery_rejects_future_work_unit_basis_revision(self):
        work_unit = self._task5_work_unit(basis_state_revision=10)
        result = self.task5_durable_resume(work_units=[work_unit], state_revision=9)
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_cold_recovery_rejects_result_missing_existing_contract_fields(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        for field in ("kernel_version", "status"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                legacy_work_unit = self._task5_work_unit()
                legacy_work_unit["scope"] = [".gpt-codex/scripts/continuity_resume.py"]
                legacy_work_unit["selected_extensions"] = []
                slot = self._write_task5_durable_project(
                    root,
                    work_units=[legacy_work_unit],
                    include_result=True,
                )
                result_path = root / ".gpt-codex/evidence/results/review-result-1.json"
                durable_result = json.loads(result_path.read_text(encoding="utf-8"))
                del durable_result[field]
                self._write_json(root, ".gpt-codex/evidence/results/review-result-1.json", durable_result)
                result = load_continuity_resume(
                    root,
                    "repo-a",
                    execution_slot_id="CODEX-IMPL-B",
                    execution_slot_binding=self.task5_binding(slot),
                )
                self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_cold_recovery_requires_durable_lifecycle_evidence_when_slot_references_it(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            slot = self._write_task5_durable_project(root, include_result=True)
            state_path = root / ".gpt-codex/STATE.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            (root / ".gpt-codex/evidence/results/review-result-1.json").unlink()
            self._write_json(root, ".gpt-codex/STATE.json", state)

            result = load_continuity_resume(
                root,
                "repo-a",
                execution_slot_id="CODEX-IMPL-B",
                execution_slot_binding=self.task5_binding(slot),
            )

        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_cold_recovery_rejects_lifecycle_result_that_does_not_bind_the_slot(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            slot = self._write_task5_durable_project(root, include_result=True)
            result_path = root / ".gpt-codex/evidence/results/review-result-1.json"
            result_record = json.loads(result_path.read_text(encoding="utf-8"))
            result_record["response_to_instruction_id"] = "review-request-other"
            self._write_json(root, ".gpt-codex/evidence/results/review-result-1.json", result_record)

            result = load_continuity_resume(
                root,
                "repo-a",
                execution_slot_id="CODEX-IMPL-B",
                execution_slot_binding=self.task5_binding(slot),
            )

        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_cold_recovery_fails_closed_for_real_git_and_work_unit_conflicts(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        def recover(root, slot):
            return load_continuity_resume(
                root,
                "repo-a",
                execution_slot_id="CODEX-IMPL-B",
                execution_slot_binding=self.task5_binding(slot),
            )

        for condition in (
            "dirty", "head_mismatch", "base_not_ancestor", "accepted_not_ancestor",
            "duplicate_work_unit", "foreign_work_unit",
        ):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                slot = self._write_task5_durable_project(root)
                if condition == "dirty":
                    (root / "dirty.txt").write_text("not clean\n", encoding="utf-8")
                elif condition in {"head_mismatch", "base_not_ancestor", "accepted_not_ancestor"}:
                    state_path = root / ".gpt-codex/STATE.json"
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                    if condition == "head_mismatch":
                        state["active_execution_slots"][0]["current_head_sha"] = "b" * 40
                    else:
                        self._git(root, "switch", "--orphan", "unrelated")
                        (root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
                        self._git(root, "add", "unrelated.txt")
                        self._git(root, "commit", "-m", "unrelated")
                        unrelated = self._git(root, "rev-parse", "HEAD")
                        self._git(root, "switch", "feature/task-5")
                        field = "base_sha" if condition == "base_not_ancestor" else "last_accepted_sha"
                        state["active_execution_slots"][0][field] = unrelated
                        if field == "base_sha":
                            state["continuity"]["latest_verified_remote_sha"] = unrelated
                    self._write_json(root, ".gpt-codex/STATE.json", state)
                    slot = state["active_execution_slots"][0]
                elif condition == "duplicate_work_unit":
                    self._write_json(root, ".gpt-codex/work/duplicate.json", self._task5_work_unit())
                else:
                    foreign = self._task5_work_unit()
                    foreign["project_id"] = "PROJECT-OTHER"
                    self._write_json(root, ".gpt-codex/work/record-0.json", foreign)

                result = recover(root, slot)
                self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")

    def test_cold_recovery_keeps_derived_navigation_and_window_observations_non_authoritative(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_continuity_resume

        for condition in ("missing_map", "missing_resume", "stale_resume", "replacement_window"):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                slot = self._write_task5_durable_project(root)
                if condition == "stale_resume":
                    self._write_json(root, ".gpt-codex/continuity/RESUME.json", {
                        "schema_version": 1,
                        "authority": "DERIVED_CACHE",
                        "context_sources": [{"path": "README.md", "fingerprint": "sha256:stale"}],
                    })
                result = load_continuity_resume(
                    root,
                    "repo-a",
                    execution_slot_id="CODEX-IMPL-B",
                    execution_slot_binding=self.task5_binding(slot),
                )
                self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
                self.assertEqual(result["next_action"], "AWAIT_REVIEW")

    def test_reviewer_reference_is_the_review_request_and_reassignment_needs_durable_chain(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_reviewer_assignment

        slot = self.task5_slot(
            role="CODEX_REVIEWER",
            reviewer_reassignment_ref="reassignment-1",
        )
        self.assertEqual(validate_reviewer_assignment(slot, "review-request-1", 8), [])
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validate_reviewer_assignment(slot, "review-request-2", 8),
        )
        project_control = {
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
        }
        reassignment_instruction = {
            "instruction_id": "review-request-2",
            "instruction_type": "REVIEW_REQUEST",
            "issuer_role": "GPT_ORCHESTRATOR",
            "executor_role": "CODEX_REVIEWER",
            "return_role": "GPT_ORCHESTRATOR",
            "expected_state_revision": 8,
            "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT"],
            "forbidden_actions": ["MUTATE_APPROVED_SCOPE", "COMMIT", "PUSH", "PUBLISH"],
            "target_work_unit": "WU-1",
            "target_project_context_id": "11111111-1111-4111-8111-111111111111",
            "review_target_revision": "a" * 40,
        }
        reassignment_evidence = {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "evidence_id": "reassignment-1",
            "project_id": "PROJECT-ONE",
            "source": "TOOL_OBSERVED",
            "subject": "REVIEWER_REASSIGNMENT",
            "state_revision": 8,
            "result": "PASS",
            "source_review_request_id": "review-request-1",
            "target_review_request_id": "review-request-2",
            "work_unit_id": "WU-1",
            "current_head_sha": "a" * 40,
            "last_accepted_sha": "a" * 40,
        }
        self.assertEqual(
            validate_reviewer_assignment(
                slot,
                "review-request-2",
                8,
                reassignment_instruction=reassignment_instruction,
                reassignment_evidence=reassignment_evidence,
                project_control=project_control,
            ),
            [],
        )
        for field, value in (
            ("expected_state_revision", 7),
            ("target_work_unit", "WU-OTHER"),
            ("target_project_context_id", "22222222-2222-4222-8222-222222222222"),
            ("instruction_id", "review-request-other"),
            ("issuer_role", "CODEX_REVIEWER"),
            ("executor_role", "CODEX_IMPLEMENTER"),
            ("review_target_revision", "b" * 40),
        ):
            with self.subTest(field=field):
                invalid_instruction = dict(reassignment_instruction, **{field: value})
                self.assertIn(
                    "RECONCILIATION_REQUIRED",
                    validate_reviewer_assignment(
                        slot,
                        "review-request-2",
                        8,
                        reassignment_instruction=invalid_instruction,
                        reassignment_evidence=reassignment_evidence,
                        project_control=project_control,
                    ),
                )
        for field, value in (
            ("evidence_id", "made-up"),
            ("source_review_request_id", "review-request-other"),
            ("target_review_request_id", "review-request-other"),
            ("work_unit_id", "WU-OTHER"),
            ("state_revision", 7),
            ("current_head_sha", "b" * 40),
            ("source", "MODEL_INFERRED"),
            ("project_id", "PROJECT-OTHER"),
            ("source", "TELEMETRY"),
        ):
            with self.subTest(evidence_field=field):
                invalid_evidence = dict(reassignment_evidence, **{field: value})
                self.assertIn(
                    "RECONCILIATION_REQUIRED",
                    validate_reviewer_assignment(
                        slot,
                        "review-request-2",
                        8,
                        reassignment_instruction=reassignment_instruction,
                        reassignment_evidence=invalid_evidence,
                        project_control=project_control,
                    ),
                )

    def test_idle_slot_rejects_stale_assignment_without_state_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            state_path = root / ".gpt-codex/STATE.json"
            self._write_json(root, ".gpt-codex/STATE.json", self._state_with_slot("IDLE"))
            state_before = state_path.read_text(encoding="utf-8")

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("IDLE_SLOT_ASSIGNMENT_FORBIDDEN", result.stdout)
            self.assertEqual(state_path.read_text(encoding="utf-8"), state_before)

    def test_blocked_slot_requires_reason_and_predecessor_without_state_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            state_path = root / ".gpt-codex/STATE.json"
            self._write_json(
                root,
                ".gpt-codex/STATE.json",
                self._state_with_slot("BLOCKED", block_reason=None),
            )
            state_before = state_path.read_text(encoding="utf-8")

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOCKED_SLOT_FIELDS_REQUIRED", result.stdout)
            self.assertEqual(state_path.read_text(encoding="utf-8"), state_before)

    def test_slot_state_revision_must_match_authoritative_state_revision(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            state = self._state_with_slot("ACTIVE")
            state["active_execution_slots"][0]["state_revision"] = 6
            self._write_json(root, ".gpt-codex/STATE.json", state)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SLOT_STATE_REVISION_MISMATCH", result.stdout)

    def test_completed_to_active_requires_idle_reset(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_slot_transition

        errors = validate_slot_transition(self._slot("COMPLETED"), self._slot("ACTIVE"))

        self.assertIn("SLOT_IDLE_RESET_REQUIRED", errors)

    def test_idle_old_work_unit_requires_reconciliation(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_execution_slots

        state = {"revision": 7, "active_execution_slots": [self._slot("IDLE", work_unit_id="WU-1")]}
        state_before = json.loads(json.dumps(state))

        errors = validate_execution_slots(state)

        self.assertIn("IDLE_SLOT_ASSIGNMENT_FORBIDDEN", errors)
        self.assertIn("RECONCILIATION_REQUIRED", errors)
        self.assertEqual(state, state_before)

    def test_slot_transition_allows_frozen_lifecycle_edges(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_slot_transition

        for previous_status, current_status in (
            ("IDLE", "ACTIVE"),
            ("ACTIVE", "AWAITING_REVIEW"),
            ("ACTIVE", "BLOCKED"),
            ("AWAITING_REVIEW", "REVIEWING"),
            ("REVIEWING", "ACTIVE"),
            ("REVIEWING", "COMPLETED"),
            ("REVIEWING", "BLOCKED"),
            ("COMPLETED", "IDLE"),
        ):
            with self.subTest(previous=previous_status, current=current_status):
                self.assertEqual(
                    validate_slot_transition(self._slot(previous_status), self._slot(current_status)),
                    [],
                )
        self.assertEqual(
            validate_slot_transition(
                self._slot("BLOCKED"),
                self._slot(
                    "ACTIVE",
                    remediation_authorization_ref="authorization-1",
                    fix_instruction_id="fix-instruction-1",
                ),
            ),
            [],
        )

    def test_blocked_cannot_return_generically_to_predecessor(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_slot_transition

        errors = validate_slot_transition(self._slot("BLOCKED"), self._slot("REVIEWING"))

        self.assertIn("SLOT_BLOCKED_RETURN_FORBIDDEN", errors)

    def test_blocked_to_active_requires_current_remediation_correlations(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import validate_slot_transition

        errors = validate_slot_transition(self._slot("BLOCKED"), self._slot("ACTIVE"))

        self.assertIn("RECONCILIATION_REQUIRED", errors)

    def test_slot_revision_precondition_fails_closed_when_stale(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from kernel_rules import validate_slot_state_revision

        self.assertEqual(validate_slot_state_revision(7, 7), [])
        self.assertIn("RECONCILIATION_REQUIRED", validate_slot_state_revision(8, 7))

    def test_missing_authoritative_state_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/STATE.json", self._slot_state(7, self._slot("ACTIVE")))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AUTHORITATIVE_STATE_HISTORY_REQUIRED", result.stdout)

    def test_forged_previous_state_cannot_mask_authoritative_completed_to_active_transition(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("COMPLETED"),
                self._slot("ACTIVE"),
            )
            forged_path = root / "forged-previous-state.json"
            self._write_json(root, "forged-previous-state.json", self._slot_state(6, self._slot("ACTIVE")))

            result = self._validate(root, previous_state=forged_path)

            self.assertNotEqual(result.returncode, 0)

    def test_project_validation_resolves_completed_previous_slot_from_git_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("COMPLETED"),
                self._slot("ACTIVE"),
            )

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SLOT_IDLE_RESET_REQUIRED", result.stdout)

    def test_tampered_previous_state_file_cannot_establish_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("COMPLETED"),
                self._slot("ACTIVE"),
            )
            tampered_path = root / "tampered-previous-state.json"
            self._write_json(root, "tampered-previous-state.json", self._slot_state(6, self._slot("ACTIVE")))

            result = self._validate(root, previous_state=tampered_path)

            self.assertNotEqual(result.returncode, 0)

    def test_current_state_byte_tampering_breaks_git_authority_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("ACTIVE"),
                self._slot("ACTIVE"),
            )
            state_path = root / ".gpt-codex/STATE.json"
            tampered = json.loads(state_path.read_text(encoding="utf-8"))
            tampered["active_execution_slots"][0]["next_action"] = "FORGED_NEXT_ACTION"
            self._write_json(root, ".gpt-codex/STATE.json", tampered)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AUTHORITATIVE_STATE_CURRENT_MISMATCH", result.stdout)

    def test_project_validation_rejects_invalid_git_history_edge_despite_fabricated_legal_previous_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("IDLE"),
                self._slot("REVIEWING"),
            )
            forged_path = root / "forged-legal-previous-state.json"
            self._write_json(root, "forged-legal-previous-state.json", self._slot_state(6, self._slot("AWAITING_REVIEW")))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SLOT_TRANSITION_INVALID", result.stdout)
            forged_result = self._validate(root, previous_state=forged_path)
            self.assertNotEqual(forged_result.returncode, 0)

    def test_project_validation_uses_real_blocked_previous_slot_from_git_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("BLOCKED"),
                self._slot("REVIEWING"),
            )

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SLOT_BLOCKED_RETURN_FORBIDDEN", result.stdout)

    def test_project_validation_rejects_structurally_invalid_git_predecessor(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("IDLE", work_unit_id="stale-work-unit"),
                self._slot("ACTIVE"),
            )

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AUTHORITATIVE_PREVIOUS_STATE_INVALID", result.stdout)

    def test_project_validation_accepts_genuine_unchanged_slot_from_git_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._commit_authoritative_state_history(
                root,
                self._slot("ACTIVE"),
                self._slot("ACTIVE"),
            )

            result = self._validate(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_foreign_project_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            project_map = self._project_map([])
            project_map["project_id"] = "PROJECT-FOREIGN"
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", project_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_PROJECT_ID_MISMATCH", result.stdout)

    def test_incomplete_identity_valid_project_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            project_map = self._project_map([])
            del project_map["architecture_summary"]
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", project_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PROJECT_MAP_SCHEMA_INVALID", result.stdout)

    def test_foreign_module_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", self._module_map(project_id="PROJECT-FOREIGN"))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_PROJECT_ID_MISMATCH", result.stdout)

    def test_incomplete_identity_valid_module_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            module_map = self._module_map()
            del module_map["responsibility"]
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", module_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_SCHEMA_INVALID", result.stdout)

    def test_duplicate_module_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(), self._module()]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_DUPLICATE_MODULE_ID", result.stdout)

    def test_malformed_project_map_module_shape_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(module_id={})]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_INVALID_SHAPE", result.stdout)

    def test_module_map_id_must_match_project_map_entry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", self._module_map(module_id="foreign"))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_ID_MISMATCH", result.stdout)

    def test_module_map_path_must_be_project_relative_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(module_map="navigation/modules/core.txt")]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_PATH_INVALID", result.stdout)

    def test_resume_claiming_authoritative_state_is_rejected_without_state_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            state_path = root / ".gpt-codex/STATE.json"
            state_before = state_path.read_text(encoding="utf-8")
            self._write_json(root, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "CANONICAL_STATE",
                "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "revision": 999,
                "state": "COMPLETE",
            })

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_CHECKPOINT_AUTHORITY_INVALID", result.stdout)
            self.assertEqual(state_path.read_text(encoding="utf-8"), state_before)

    def test_incomplete_identity_valid_resume_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "DERIVED_CACHE",
                "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": None,
            })

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_SCHEMA_INVALID", result.stdout)

    def test_map_and_resume_evolution_metadata_cannot_be_authority(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        sys.path.insert(0, str(scripts))
        from continuity_resume import load_resume_checkpoint
        from project_navigation import validate_navigation_identity

        control = {
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "github": {"repository_id": "123"},
        }
        project_map = self._project_map([])
        project_map["repository_id"] = "123"
        project_map["evolution_metadata"] = {
            "classification": "DERIVED_OBSERVATION_ONLY",
            "target_work_unit": "WU-FOREIGN",
        }
        with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
            validate_navigation_identity(project_map, control)

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            self._write_json(gov.parent, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "DERIVED_CACHE",
                "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": "123",
                "evolution_metadata": {
                    "classification": "DERIVED_OBSERVATION_ONLY",
                    "command": "adopt",
                },
            })
            with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
                load_resume_checkpoint(gov)

    def test_complete_identity_binds_map_and_resume_to_task1_boundary(self):
        scripts = ROOT / ".gpt-codex" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from continuity_resume import load_resume_checkpoint
        from project_navigation import validate_navigation_identity

        control = {
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "github": {"repository_id": "123", "repository_full_name": "owner/project", "default_branch": "main"},
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
        }
        valid_map = self._project_map([])
        valid_map["repository_id"] = "123"
        self.assertIsNone(validate_navigation_identity(valid_map, control))
        for field, value, code in (
            ("project_context_id", "22222222-2222-4222-8222-222222222222", "CROSS_PROJECT_CONTEXT_MISMATCH"),
            ("repository_id", "456", "GITHUB_REPOSITORY_MISMATCH"),
            ("repository_id", None, "PROJECT_IDENTITY_INVALID"),
        ):
            candidate = {**valid_map, field: value}
            with self.subTest(kind="map", code=code), self.assertRaisesRegex(ValueError, code):
                validate_navigation_identity(candidate, control)

        with tempfile.TemporaryDirectory() as td:
            gov = Path(td) / ".gpt-codex"
            base_resume = {
                "schema_version": 1, "authority": "DERIVED_CACHE", "project_id": "PROJECT-ONE",
                "project_context_id": control["project_context_id"], "repository_id": "123",
            }
            for field, value, code in (
                (None, None, None),
                ("project_context_id", "22222222-2222-4222-8222-222222222222", "CROSS_PROJECT_CONTEXT_MISMATCH"),
                ("repository_id", "456", "GITHUB_REPOSITORY_MISMATCH"),
                ("repository_id", None, "PROJECT_IDENTITY_INVALID"),
            ):
                candidate = dict(base_resume)
                if field is not None:
                    candidate[field] = value
                self._write_json(gov.parent, ".gpt-codex/continuity/RESUME.json", candidate)
                if code is None:
                    self.assertEqual(load_resume_checkpoint(gov, control), candidate)
                else:
                    with self.subTest(kind="resume", code=code), self.assertRaisesRegex(ValueError, code):
                        load_resume_checkpoint(gov, control)


if __name__ == "__main__":
    unittest.main()
