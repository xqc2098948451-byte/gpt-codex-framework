import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
VALID_SHA = "a" * 40
NEW_SHA = "b" * 40


def load_validator():
    path = ROOT / "scripts" / "validate_project.py"
    spec = importlib.util.spec_from_file_location("validate_project_lifecycle_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finding_result():
    return {
        "result_id": "22222222-2222-4222-8222-222222222222",
        "result_message_type": "REVIEW_FINDING",
        "responder_role": "CODEX_REVIEWER",
        "review_target_revision": VALID_SHA,
        "finding_ids": ["RCP-FINDING-001"],
        "fix_round": 0,
        "evidence_refs": ["evidence/review-001.json"],
        "status": "FAIL",
    }


def fix_instruction():
    return {
        "instruction_id": "33333333-3333-4333-8333-333333333333",
        "instruction_type": "FIX_INSTRUCTION",
        "issuer_role": "GPT_ORCHESTRATOR",
        "executor_role": "CODEX_IMPLEMENTER",
        "return_role": "GPT_ORCHESTRATOR",
        "expected_state_revision": 8,
        "expected_base_sha": VALID_SHA,
        "target_project_context_id": "PROJECT-CONTEXT-001",
        "target_github_repository_id": "repo-001",
        "target_github_repository_full_name": "owner/project",
        "expected_remote_ref": "refs/heads/feature",
        "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
        "forbidden_actions": ["PUBLISH"],
        "in_response_to_result_id": "22222222-2222-4222-8222-222222222222",
        "finding_ids": ["RCP-FINDING-001"],
        "remediation_decision_ref": "DECISION-001",
        "fix_round": 1,
    }


def mutation_instruction():
    instruction = fix_instruction()
    instruction.update({
        "instruction_id": "11111111-1111-4111-8111-111111111111",
        "instruction_type": "EXECUTION_INSTRUCTION",
        "target_work_unit": "WU-001",
        "expected_state_revision": 8,
    })
    instruction.pop("in_response_to_result_id")
    instruction.pop("finding_ids")
    instruction.pop("remediation_decision_ref")
    instruction.pop("fix_round")
    return instruction


def review_request():
    return {
        **mutation_instruction(),
        "instruction_id": "44444444-4444-4444-8444-444444444444",
        "instruction_type": "REVIEW_REQUEST",
        "executor_role": "CODEX_REVIEWER",
        "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT"],
        "in_response_to_instruction_id": "11111111-1111-4111-8111-111111111111",
        "review_target_revision": VALID_SHA,
    }


def review_result():
    return {
        "result_message_type": "REVIEW_RESULT",
        "responder_role": "CODEX_REVIEWER",
        "response_to_instruction_id": "44444444-4444-4444-8444-444444444444",
        "review_target_revision": VALID_SHA,
        "status": "PASS",
    }


def remediation_decision_evidence(*, decision="ACCEPT", basis_type="ACCEPTED_AUTHORITY_BASIS",
                                  finding_ids=None, basis_refs=None, adjudicated_at_revision=8):
    return {
        "evidence_id": "DECISION-001",
        "subject": "REMEDIATION_ADJUDICATION",
        "finding_ids": finding_ids if finding_ids is not None else ["RCP-FINDING-001"],
        "decision": decision,
        "basis_type": basis_type,
        "basis_refs": basis_refs if basis_refs is not None else ["basis/accepted-001"],
        "adjudicated_at_revision": adjudicated_at_revision,
    }


def resolved_basis(*, basis_type="ACCEPTED_AUTHORITY_BASIS", finding_ids=None,
                   state_revision=8, accepted=True, failing=False):
    return {
        "basis/accepted-001": {
            "basis_type": basis_type,
            "finding_ids": finding_ids if finding_ids is not None else ["RCP-FINDING-001"],
            "state_revision": state_revision,
            "accepted": accepted,
            "failing": failing,
        },
    }


def write_durable_adjudication_repository(root, decision_evidence=None, basis_evidence=None, state_revision=8):
    decision_evidence = decision_evidence or remediation_decision_evidence()
    basis_evidence = basis_evidence or {
        "evidence_id": "basis/accepted-001",
        **resolved_basis()["basis/accepted-001"],
    }
    evidence_dir = root / ".gpt-codex" / "evidence"
    evidence_dir.mkdir(parents=True)
    decision_path = ".gpt-codex/evidence/decision.json"
    basis_path = ".gpt-codex/evidence/basis.json"
    (root / decision_path).write_text(json.dumps(decision_evidence), encoding="utf-8")
    (root / basis_path).write_text(json.dumps(basis_evidence), encoding="utf-8")
    (root / ".gpt-codex" / "STATE.json").write_text(json.dumps({
        "project_id": "PRJ-FRAMEWORK-MANAGEMENT",
        "revision": state_revision,
        "evidence_refs": [decision_path, basis_path],
    }), encoding="utf-8")
    for command in (
        ["git", "init"], ["git", "config", "user.email", "tests@example.invalid"],
        ["git", "config", "user.name", "Tests"], ["git", "add", "."], ["git", "commit", "-m", "fixture"],
    ):
        subprocess.run(command, cwd=root, check=True, capture_output=True)


class ReviewLifecycleTests(unittest.TestCase):
    def test_task9_composed_fix_chain_uses_production_builder_lifecycle_and_git_oracle(self):
        """Task 9: exercise the whole FIX route, not a private helper in isolation."""
        from instruction_envelope import build_instruction_envelope

        validator = load_validator()
        control = json.loads((ROOT / "CONTROL.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="task9-fix-") as temporary:
            root = Path(temporary)
            decision = remediation_decision_evidence(adjudicated_at_revision=16)
            basis = {"evidence_id": "basis/accepted-001", **resolved_basis(state_revision=16)["basis/accepted-001"]}
            write_durable_adjudication_repository(root, decision, basis, state_revision=16)
            (root / "src").mkdir(); (root / "src/fix.py").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/fix.py"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "fix baseline"], cwd=root, check=True, capture_output=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            finding = {
                **finding_result(), "review_target_revision": base,
                "source_project_context_id": control["project_context_id"],
                "source_github_repository_id": control["github"]["repository_id"],
                "source_github_repository_full_name": control["github"]["repository_full_name"],
                "current_remote_ref": "refs/heads/main",
            }
            fix = build_instruction_envelope(
                "FIX_INSTRUCTION", control["project_context_id"], "Framework", 16, "2.7.2",
                target_work_unit="WU-B5-FIX", expected_base_sha=base, scope_paths=["src/fix.py"],
                remediation_decision_ref="DECISION-001", instruction_id="33333333-3333-4333-8333-333333333333",
                target_github_repository_id=control["github"]["repository_id"], target_github_repository_full_name=control["github"]["repository_full_name"],
                expected_remote_ref="refs/heads/main", issuer_role="GPT_ORCHESTRATOR",
                executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR",
                authorized_actions=["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"], forbidden_actions=[],
                in_response_to_result_id=finding["result_id"], finding_ids=finding["finding_ids"], fix_round=1,
            )
            review = build_instruction_envelope(
                "REVIEW_REQUEST", control["project_context_id"], "Framework", 16, "2.7.2",
                target_work_unit="WU-B5-FIX", expected_base_sha=base, scope_paths=["src/fix.py"],
                instruction_id="44444444-4444-4444-8444-444444444444", target_github_repository_id=control["github"]["repository_id"],
                target_github_repository_full_name=control["github"]["repository_full_name"], expected_remote_ref="refs/heads/main",
                issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_REVIEWER", return_role="GPT_ORCHESTRATOR",
                authorized_actions=["READ", "TEST", "VALIDATE", "REPORT"], forbidden_actions=[],
                in_response_to_instruction_id=fix["instruction_id"], review_target_revision=base,
                runtime_fresh_context_verified=True, runtime_input_source_kinds=["REPOSITORY_CONTENT"],
            )
            result = {"result_message_type": "REVIEW_RESULT", "responder_role": "CODEX_REVIEWER", "status": "PASS",
                      "response_to_instruction_id": review["instruction_id"], "review_target_revision": base,
                      "source_project_context_id": control["project_context_id"], "source_github_repository_id": control["github"]["repository_id"],
                      "source_github_repository_full_name": control["github"]["repository_full_name"], "current_remote_ref": "refs/heads/main"}
            state = {"project_id": control["project_id"], "revision": 16}
            work_unit = {"project_id": control["project_id"], "work_unit_id": "WU-B5-FIX", "state": "AUTHORIZED",
                         "basis_state_revision": 16, "scope": {"owned_paths": ["src/fix.py"], "excluded_paths": []}}
            valid = lambda item=fix, req=review, res=result, finding_item=finding: validator.validate_governed_mutation_entry(
                control, state, work_unit, item, req, res, current_state_revision=16, repository_root=root, finding_result=finding_item,
            )
            self.assertEqual(validator.validate_review_lifecycle(fix, finding, current_state_revision=16, repository_root=root), [])
            self.assertEqual(valid(), [])
            faults = {
                "FIX-01 missing remediation_decision_ref": ({key: value for key, value in fix.items() if key != "remediation_decision_ref"}, review, result, finding),
                "FIX-02 wrong finding/result correlation": ({**fix, "in_response_to_result_id": "55555555-5555-4555-8555-555555555555"}, review, result, finding),
                "FIX-03 stale finding review target": (fix, review, result, {**finding, "review_target_revision": NEW_SHA}),
                "FIX-05 wrong expected_base_sha": ({**fix, "expected_base_sha": NEW_SHA}, review, result, finding),
                "FIX-06 stale expected_state_revision": ({**fix, "expected_state_revision": 15}, review, result, finding),
                "FIX-07 missing PRE review": (fix, None, None, finding),
                "FIX-08 stale PRE review": (fix, {**review, "review_target_revision": NEW_SHA}, result, finding),
                "FIX-09 scope escape": ({**fix, "scope_paths": ["outside.py"]}, review, result, finding),
            }
            observed = {}
            for name, (item, req, res, finding_item) in faults.items():
                with self.subTest(name=name):
                    observed[name] = valid(item, req, res, finding_item)
                    self.assertTrue(observed[name], name)
                    self.assertEqual(valid(), [])
            decision_path = root / ".gpt-codex/evidence/decision.json"
            original_decision = decision_path.read_text(encoding="utf-8")
            try:
                decision_path.write_text(json.dumps({**decision, "adjudicated_at_revision": 15}), encoding="utf-8")
                subprocess.run(["git", "add", ".gpt-codex/evidence/decision.json"], cwd=root, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", "stale adjudication fixture"], cwd=root, check=True, capture_output=True)
                observed["FIX-04 stale remediation/adjudication basis"] = validator.validate_review_lifecycle(
                    fix, finding, current_state_revision=16, repository_root=root,
                )
                self.assertTrue(observed["FIX-04 stale remediation/adjudication basis"])
            finally:
                subprocess.run(["git", "reset", "--hard", base], cwd=root, check=True, capture_output=True)
                self.assertEqual(decision_path.read_text(encoding="utf-8"), original_decision)
            self.assertEqual(valid(), [])
            for case, path, staged in (
                ("FIX-10 actual Git outside-scope unstaged path", "outside-unstaged.py", False),
                ("FIX-11 actual Git outside-scope staged path", "outside-staged.py", True),
                ("FIX-12 actual Git outside-scope untracked path", "outside-untracked.py", False),
            ):
                target = root / path
                target.write_text("escape\n", encoding="utf-8")
                if staged:
                    subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)
                observed[case] = valid()
                self.assertIn("SCOPE_EXPANSION_DENIED", observed[case])
                if staged:
                    subprocess.run(["git", "reset", "--", path], cwd=root, check=True, capture_output=True)
                target.unlink()
                self.assertEqual(valid(), [])
            self.assertEqual(len(observed), 12)
    def test_task7_control_plane_paths_remain_exact_files(self):
        validator = load_validator()
        self.assertTrue(validator._is_control_plane_path(".gpt-codex/STATE.json"))
        self.assertTrue(validator._is_control_plane_path(".gpt-codex/evidence/results/result.json"))
        self.assertFalse(validator._is_control_plane_path(".gpt-codex/work-units/"))
        self.assertFalse(validator._is_control_plane_path(".gpt-codex/scripts/validate_project.py"))

    def test_pairwise_review_policy_rejects_missing_or_ambiguous_slots(self):
        validator = load_validator()
        state = {"active_execution_slots": [{"slot_id": "impl", "role": "CODEX_IMPLEMENTER", "project_context_id": "PROJECT-CONTEXT-001", "work_unit_id": "WU-001"}]}
        facts = {"implementer_slot_id": "impl", "reviewer_slot_id": "reviewer", "canonical_implementer_worktree": "impl-root", "canonical_reviewer_worktree": "review-root", "implementation_sha": VALID_SHA, "reviewer_head_sha": VALID_SHA, "reviewer_tracked_clean": True}
        self.assertIn("RECONCILIATION_REQUIRED", validator._validate_pairwise_review_policy(state, review_request(), facts))
        state["active_execution_slots"].append({"slot_id": "reviewer", "role": "CODEX_REVIEWER", "project_context_id": "PROJECT-CONTEXT-001", "work_unit_id": "WU-001", "review_request_id": review_request()["instruction_id"]})
        self.assertEqual(validator._validate_pairwise_review_policy(state, review_request(), facts), [])
    def test_repository_authority_requires_correlated_execution_fact_not_artifact_existence(self):
        validator = load_validator()
        mutation = mutation_instruction()
        authority = {
            "accepted_design_ref": "design:foundation@" + VALID_SHA,
            "accepted_plan_ref": "plan:foundation@" + NEW_SHA,
            "project_context_id": mutation["target_project_context_id"],
            "work_unit_id": mutation["target_work_unit"],
            "state_revision": 8,
            "authorization": {
                "authority_type": "EVIDENCE",
                "instruction_id": mutation["instruction_id"],
                "status": "EXECUTION_AUTHORIZED",
                "target_revision": VALID_SHA,
            },
        }
        self.assertIn(
            "IMPLEMENTATION_AUTHORIZATION = DENY",
            validator.validate_repository_authorization(
                authority, mutation, {"work_unit_id": mutation["target_work_unit"]},
                current_state_revision=8,
            ),
        )
        self.assertIn(
            "IMPLEMENTATION_AUTHORIZATION = DENY",
            validator.validate_repository_authorization(
                {**authority, "authorization": {**authority["authorization"], "status": "ARTIFACT_ACCEPTED"}},
                mutation, {"work_unit_id": mutation["target_work_unit"]}, current_state_revision=8,
            ),
        )

    def test_pre_execution_review_requires_exact_authorization_and_correlation(self):
        validator = load_validator()
        mutation = mutation_instruction()
        request = review_request()
        result = review_result()
        self.assertIn(
            "PRE_EXECUTION_REVIEW_REQUIRED",
            validator.validate_pre_execution_review(mutation, None, None, current_state_revision=8),
        )
        self.assertIn(
            "PRE_EXECUTION_REVIEW_REQUEST_CORRELATION_REQUIRED",
            validator.validate_pre_execution_review(
                mutation, {**request, "in_response_to_instruction_id": fix_instruction()["instruction_id"]}, result,
                current_state_revision=8,
            ),
        )
        self.assertIn(
            "PRE_EXECUTION_REVIEW_RESULT_CORRELATION_REQUIRED",
            validator.validate_pre_execution_review(
                mutation, request, {**result, "response_to_instruction_id": fix_instruction()["instruction_id"]},
                current_state_revision=8,
            ),
        )
        self.assertIn(
            "PRE_EXECUTION_REVIEW_TARGET_MISMATCH",
            validator.validate_pre_execution_review(
                mutation, {**request, "review_target_revision": NEW_SHA}, result, current_state_revision=8,
            ),
        )
        self.assertIn(
            "PRE_EXECUTION_REVIEW_NOT_APPROVED",
            validator.validate_pre_execution_review(
                mutation, request, {**result, "status": "FAIL"}, current_state_revision=8,
            ),
        )
        self.assertEqual(validator.validate_pre_execution_review(mutation, request, result, current_state_revision=8), [])

    def test_pre_execution_review_preserves_reviewer_and_identity_failures(self):
        validator = load_validator()
        mutation = mutation_instruction()
        request = review_request()
        reviewer_mutation = {**request, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]}
        errors = validator.validate_pre_execution_review(mutation, reviewer_mutation, review_result(), current_state_revision=8)
        self.assertIn("REVIEWER_MUTATION_DENIED", errors)
        context = {
            "reviewed_revision": VALID_SHA, "project_context_id": "FOREIGN", "repository_id": "repo-001",
            "repository_full_name": "owner/project", "remote_ref": "refs/heads/feature",
        }
        errors = validator.validate_pre_execution_review(
            mutation, request, {**review_result(), "source_project_context_id": "PROJECT-CONTEXT-001", "source_github_repository_id": "repo-001", "source_github_repository_full_name": "owner/project", "current_remote_ref": "refs/heads/feature"},
            current_state_revision=8, authoritative_review_context=context,
        )
        self.assertIn("RECONCILIATION_REQUIRED", errors)

    def test_legacy_instruction_cannot_bypass_pre_execution_review(self):
        validator = load_validator()
        legacy = {**mutation_instruction(), "instruction_type": "WORK_UNIT"}
        self.assertIn(
            "PRE_EXECUTION_REVIEW_REQUIRED",
            validator.validate_pre_execution_review(legacy, None, None, current_state_revision=8),
        )
    def test_finding_requires_evidence_and_does_not_authorize_a_fix(self):
        validator = load_validator()
        finding = finding_result()
        self.assertEqual(validator.validate_review_result(finding), [])
        errors = validator.validate_review_lifecycle(None, finding)
        self.assertIn("FIX_INSTRUCTION_REQUIRED", errors)
        self.assertIn("REMEDIATION_DECISION_REQUIRED", errors)

    def test_finding_without_evidence_or_reviewed_sha_is_rejected(self):
        validator = load_validator()
        invalid = finding_result()
        invalid.pop("evidence_refs")
        invalid.pop("review_target_revision")
        errors = validator.validate_review_result(invalid)
        self.assertIn("FINDING_EVIDENCE_REQUIRED", errors)
        self.assertIn("REVIEW_TARGET_REVISION_REQUIRED", errors)

    def test_explicit_decision_and_new_fix_instruction_are_required_for_remediation(self):
        validator = load_validator()
        errors = validator.validate_review_lifecycle(
            fix_instruction(), finding_result(), current_state_revision=8,
            remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(),
        )
        self.assertEqual(errors, [])

    def test_remediation_adjudication_accepts_authority_and_regression_bases(self):
        validator = load_validator()
        self.assertEqual(
            validator.validate_remediation_adjudication(
                remediation_decision_evidence(), finding_result(), resolved_basis(),
            ),
            [],
        )
        regression_decision = remediation_decision_evidence(
            basis_type="CONCRETE_REGRESSION_EVIDENCE",
        )
        regression_basis = resolved_basis(
            basis_type="CONCRETE_REGRESSION_EVIDENCE", accepted=False, failing=True,
        )
        self.assertEqual(
            validator.validate_remediation_adjudication(
                regression_decision, finding_result(), regression_basis,
            ),
            [],
        )

    def test_remediation_adjudication_fails_closed_for_invalid_or_unrelated_basis(self):
        validator = load_validator()
        valid_decision = remediation_decision_evidence()
        cases = {
            "missing_ref": (remediation_decision_evidence(basis_refs=[]), resolved_basis()),
            "unresolved": (remediation_decision_evidence(basis_refs=["basis/missing"]), resolved_basis()),
            "preference": (remediation_decision_evidence(basis_type="PREFERENCE"), resolved_basis()),
            "reject": (remediation_decision_evidence(decision="REJECT"), resolved_basis()),
            "unrelated": (valid_decision, resolved_basis(finding_ids=["OTHER-FINDING"])),
            "stale": (valid_decision, resolved_basis(state_revision=7)),
            "non_failing_regression": (
                remediation_decision_evidence(basis_type="CONCRETE_REGRESSION_EVIDENCE"),
                resolved_basis(basis_type="CONCRETE_REGRESSION_EVIDENCE", accepted=False, failing=False),
            ),
            "wrong_finding": (remediation_decision_evidence(finding_ids=["OTHER-FINDING"]), resolved_basis()),
        }
        for case_name, (decision, basis) in cases.items():
            with self.subTest(case_name):
                errors = validator.validate_remediation_adjudication(decision, finding_result(), basis)
                self.assertTrue(errors)
                if case_name == "unresolved":
                    self.assertIn("REMEDIATION_BASIS_UNRESOLVED", errors)

    def test_review_lifecycle_requires_decision_evidence_to_resolve_instruction_ref(self):
        validator = load_validator()
        self.assertEqual(
            validator.validate_review_lifecycle(
                fix_instruction(), finding_result(), current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(),
            ),
            [],
        )
        errors = validator.validate_review_lifecycle(
            fix_instruction(), finding_result(), current_state_revision=8,
            remediation_decision=remediation_decision_evidence(basis_refs=["basis/missing"]),
            resolved_basis=resolved_basis(),
        )
        self.assertIn("REMEDIATION_BASIS_UNRESOLVED", errors)

    def test_review_lifecycle_rejects_missing_decision_ref(self):
        validator = load_validator()
        instruction = fix_instruction()
        instruction.pop("remediation_decision_ref")
        errors = validator.validate_review_lifecycle(
            instruction, finding_result(), current_state_revision=8,
            remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(),
        )
        self.assertIn("REMEDIATION_DECISION_MISMATCH", errors)

    def test_governed_fix_rejects_fake_memory_adjudication_without_durable_evidence(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_durable_adjudication_repository(
                root, decision_evidence={"evidence_id": "OTHER-DECISION"},
                basis_evidence={"evidence_id": "OTHER-BASIS"},
            )
            errors = validator.validate_review_lifecycle(
                fix_instruction(), finding_result(), current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(),
                repository_root=root,
            )
        self.assertIn("REMEDIATION_BASIS_UNRESOLVED", errors)

    def test_governed_fix_accepts_repository_resolved_adjudication(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_durable_adjudication_repository(root)
            errors = validator.validate_review_lifecycle(
                fix_instruction(), finding_result(), current_state_revision=8,
                repository_root=root,
            )
        self.assertEqual(errors, [])

    def test_governed_fix_accepts_repository_resolved_regression_evidence(self):
        validator = load_validator()
        decision = remediation_decision_evidence(basis_type="CONCRETE_REGRESSION_EVIDENCE")
        basis = {
            "evidence_id": "basis/accepted-001",
            **resolved_basis(
                basis_type="CONCRETE_REGRESSION_EVIDENCE", accepted=False, failing=True,
            )["basis/accepted-001"],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_durable_adjudication_repository(root, decision, basis)
            errors = validator.validate_review_lifecycle(
                fix_instruction(), finding_result(), current_state_revision=8, repository_root=root,
            )
        self.assertEqual(errors, [])

    def test_governed_mutation_entry_composes_durable_fix_gate(self):
        validator = load_validator()
        control = {
            "project_id": "PRJ-FRAMEWORK-MANAGEMENT",
            "project_context_id": "PROJECT-CONTEXT-001",
            "github": {"repository_id": "repo-001", "repository_full_name": "owner/project"},
        }
        state = {"project_id": "PRJ-FRAMEWORK-MANAGEMENT", "revision": 8}
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_durable_adjudication_repository(
                root, decision_evidence={"evidence_id": "OTHER-DECISION"},
                basis_evidence={"evidence_id": "OTHER-BASIS"},
            )
            errors = validator.validate_governed_mutation_entry(
                control, state, {}, fix_instruction(), review_request(), review_result(),
                current_state_revision=8, repository_root=root, finding_result=finding_result(),
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(),
            )
        self.assertIn("REMEDIATION_BASIS_UNRESOLVED", errors)

    def test_re_review_binds_new_revision_and_retains_original_evidence(self):
        validator = load_validator()
        re_review = {
            "result_message_type": "REVIEW_RESULT",
            "responder_role": "CODEX_REVIEWER",
            "response_to_instruction_id": "33333333-3333-4333-8333-333333333333",
            "review_target_revision": NEW_SHA,
            "fix_round": 1,
            "evidence_refs": ["evidence/review-001.json", "evidence/re-review-002.json"],
            "status": "PASS",
        }
        self.assertEqual(
            validator.validate_review_lifecycle(
                fix_instruction(), finding_result(), current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), re_review_result=re_review,
                resulting_revision=NEW_SHA,
            ),
            [],
        )

    def test_empty_remediation_decision_is_rejected(self):
        validator = load_validator()
        errors = validator.validate_review_lifecycle(
            fix_instruction(), finding_result(), current_state_revision=8, remediation_decision=""
        )
        self.assertIn("REMEDIATION_DECISION_REQUIRED", errors)

    def test_review_lifecycle_binds_exact_revision_and_identity(self):
        validator = load_validator()
        self.assertIn("authoritative_review_context", inspect.signature(validator.validate_review_lifecycle).parameters)
        context = {
            "reviewed_revision": VALID_SHA,
            "project_context_id": "PROJECT-CONTEXT-001",
            "repository_id": "repo-001",
            "repository_full_name": "owner/project",
            "remote_ref": "refs/heads/feature",
        }
        finding = finding_result()
        finding.update({
            "source_project_context_id": "PROJECT-CONTEXT-001",
            "source_github_repository_id": "repo-001",
            "source_github_repository_full_name": "owner/project",
            "current_remote_ref": "refs/heads/feature",
        })
        self.assertEqual(
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), authoritative_review_context=context,
            ),
            [],
        )
        stale = dict(context, reviewed_revision=NEW_SHA)
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), authoritative_review_context=stale,
            ),
        )
        foreign = dict(context, project_context_id="OTHER")
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), authoritative_review_context=foreign,
            ),
        )
        foreign_repository = dict(context, repository_id="other/repository")
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), authoritative_review_context=foreign_repository,
            ),
        )

    def test_re_review_requires_fix_correlation_and_resulting_revision(self):
        validator = load_validator()
        re_review = {
            "result_message_type": "REVIEW_RESULT",
            "responder_role": "CODEX_REVIEWER",
            "review_target_revision": NEW_SHA,
            "fix_round": 1,
            "evidence_refs": ["evidence/review-001.json"],
        }
        errors = validator.validate_review_lifecycle(
            fix_instruction(), finding_result(), current_state_revision=8,
            remediation_decision=remediation_decision_evidence(), resolved_basis=resolved_basis(), re_review_result=re_review,
        )
        self.assertIn("RE_REVIEW_INSTRUCTION_CORRELATION_REQUIRED", errors)
        self.assertIn("RESULTING_REVISION_REQUIRED", errors)


if __name__ == "__main__":
    unittest.main()
