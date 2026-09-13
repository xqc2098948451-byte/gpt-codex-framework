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


class ReviewLifecycleTests(unittest.TestCase):
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
