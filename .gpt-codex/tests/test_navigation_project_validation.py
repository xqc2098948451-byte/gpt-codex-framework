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
            review_result_ref="review-result-1",
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
