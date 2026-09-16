import importlib.util
import inspect
import sys
import unittest
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


class ReviewLifecycleTests(unittest.TestCase):
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
            fix_instruction(), finding_result(), current_state_revision=8, remediation_decision="DECISION-001"
        )
        self.assertEqual(errors, [])

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
                remediation_decision="DECISION-001", re_review_result=re_review,
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
                remediation_decision="DECISION-001", authoritative_review_context=context,
            ),
            [],
        )
        stale = dict(context, reviewed_revision=NEW_SHA)
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision="DECISION-001", authoritative_review_context=stale,
            ),
        )
        foreign = dict(context, project_context_id="OTHER")
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision="DECISION-001", authoritative_review_context=foreign,
            ),
        )
        foreign_repository = dict(context, repository_id="other/repository")
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validator.validate_review_lifecycle(
                fix_instruction(), finding, current_state_revision=8,
                remediation_decision="DECISION-001", authoritative_review_context=foreign_repository,
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
            remediation_decision="DECISION-001", re_review_result=re_review,
        )
        self.assertIn("RE_REVIEW_INSTRUCTION_CORRELATION_REQUIRED", errors)
        self.assertIn("RESULTING_REVISION_REQUIRED", errors)


if __name__ == "__main__":
    unittest.main()
