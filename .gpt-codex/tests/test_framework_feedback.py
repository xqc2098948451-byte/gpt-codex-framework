import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from framework_feedback import (  # noqa: E402
    FrameworkFeedback, ProcessReview, build_process_review,
    build_framework_management_review_input, build_improvement_candidate,
    build_process_review_from_evidence, classify_harvest_relation,
    classify_recurrence_relevance, derive_framework_feedback,
    framework_feedback_authorizes_mutation, validate_execution_policy,
    validate_framework_evolution_boundary, validate_framework_feedback,
    normalize_process_evidence, validate_process_evidence,
    validate_project_strategy_lifecycle, validate_work_unit_process_record,
)


POLICY = {
    "strategy_profile_id": "PROJECT_PROFILE_001",
    "gpt_orchestrator_strategy": "MINIMAL_CLOSED_LOOP",
    "codex_implementer_strategy": "MINIMAL_DIFF_TDD",
    "codex_reviewer_strategy": "CONTRACT_FIRST",
    "task_splitting": "PROJECT_DETERMINED",
    "review_policy": "RISK_OR_MILESTONE",
    "instruction_policy": "REFERENCE_FIRST",
    "result_return_policy": "DURABLE_REF_FIRST",
}


class FrameworkFeedbackTests(unittest.TestCase):
    def process_evidence(self, **overrides):
        value = {
            "source": "result-envelope", "project_context_id": "ctx-1",
            "work_unit_id": "WU-1", "state_revision": 17,
            "result_ref": "result:WU-1", "evidence_refs": ["evidence:WU-1"],
            "source_record_refs": ["record:WU-1"], "completeness": "COMPLETE",
            "redactions": ["TRIMMED"],
            "content": {"observation": "review succeeded", "outcome": "PASS"},
            "process_record": {"work_unit_id": "WU-1", "final_result": "PASS", "codex_retries": 0,
                               "gpt_interventions": 0, "review_rounds": 1, "remediation_rounds": 0,
                               "handoff_result": "PASS", "usage": "UNKNOWN", "git_sha": "a" * 40,
                               "result_ref": "result:WU-1"},
        }
        value.update(overrides)
        return value

    def test_c1_normalizes_bounded_complete_evidence_and_rejects_unsafe_or_authority_content(self):
        raw = self.process_evidence()
        self.assertEqual(validate_process_evidence(raw), [])
        normalized = normalize_process_evidence(raw)
        self.assertEqual(normalized["completeness"], "COMPLETE")
        self.assertEqual(normalized["evidence_identity"], normalize_process_evidence(dict(raw))["evidence_identity"])
        for invalid in (
            self.process_evidence(source=""), self.process_evidence(evidence_refs=[]),
            self.process_evidence(content={"raw_prompt": "secret"}),
            self.process_evidence(authorized_actions=["MUTATE_APPROVED_SCOPE"]),
            self.process_evidence(process_record={"work_unit_id": "bad"}),
        ):
            with self.subTest(invalid=invalid):
                self.assertEqual(validate_process_evidence(invalid), ["PROCESS_EVIDENCE_INVALID"])
        self.assertEqual(normalize_process_evidence(self.process_evidence(completeness="PARTIAL"))["completeness"], "PARTIAL")
        self.assertEqual(normalize_process_evidence(self.process_evidence(completeness="LOW_CONFIDENCE"))["completeness"], "LOW_CONFIDENCE")

    def test_c1_rejects_nonserializable_or_unbounded_nested_process_usage(self):
        for usage in ({"detail": object()}, {"detail": "x" * 513}):
            record = self.process_evidence()
            record["process_record"] = {**record["process_record"], "usage": usage}
            with self.subTest(usage=usage):
                self.assertEqual(validate_process_evidence(record), ["PROCESS_EVIDENCE_INVALID"])

    def test_c2_complete_evidence_derives_one_process_review_without_duplicate_counting(self):
        complete = normalize_process_evidence(self.process_evidence())
        partial = normalize_process_evidence(self.process_evidence(work_unit_id="WU-2", result_ref="result:WU-2", evidence_refs=["evidence:WU-2"], source_record_refs=["record:WU-2"], completeness="PARTIAL", process_record={"work_unit_id": "WU-2", "final_result": "FAIL", "codex_retries": 1, "gpt_interventions": 0, "review_rounds": 1, "remediation_rounds": 0, "handoff_result": "FAIL", "usage": "UNKNOWN", "git_sha": "b" * 40, "result_ref": "result:WU-2"}))
        review = build_process_review_from_evidence([complete, complete, partial], POLICY["strategy_profile_id"])
        self.assertEqual((review.codex_tasks, review.work_unit_ids, review.result_refs), (1, ("WU-1",), ("result:WU-1",)))
        self.assertEqual(review.success_observations, ("review succeeded",))
        self.assertEqual(review.failure_observations, ())

    def test_c3_feedback_derivation_retains_review_and_evidence_links_without_authority(self):
        evidence = normalize_process_evidence(self.process_evidence())
        review = build_process_review_from_evidence([evidence], POLICY["strategy_profile_id"])
        feedback = derive_framework_feedback(review, [evidence], kind="CAPABILITY_REUSE_SUCCESS")
        self.assertEqual(validate_framework_feedback(feedback), [])
        self.assertIn(evidence["evidence_identity"], feedback["evidence_refs"])
        self.assertIn("process-review:", " ".join(feedback["evidence_refs"]))
        self.assertFalse(framework_feedback_authorizes_mutation({"framework_management_only": True}, feedback))
        with self.assertRaises(ValueError):
            derive_framework_feedback(review, [dict(evidence, authority="yes")], kind="FRICTION")

    def test_c4_candidate_is_bounded_deterministic_and_non_authorizing(self):
        evidence = normalize_process_evidence(self.process_evidence())
        feedback = derive_framework_feedback(build_process_review_from_evidence([evidence], POLICY["strategy_profile_id"]), [evidence], kind="FRICTION")
        candidate = build_improvement_candidate(feedback, [evidence], problem_class="FRICTION", management_question="Should management inspect this?")
        self.assertEqual(candidate["candidate_identity"], build_improvement_candidate(feedback, [evidence], problem_class="FRICTION", management_question="Should management inspect this?")["candidate_identity"])
        self.assertEqual(candidate["status"], "OBSERVATION_ONLY")
        self.assertFalse(set(candidate).intersection({"authorized_actions", "release_authority", "work_unit_authority"}))

    def test_c5_recurrence_relevance_is_deterministic_and_retains_source_references(self):
        first = normalize_process_evidence(self.process_evidence())
        second = normalize_process_evidence(self.process_evidence(source="review-result", source_record_refs=["record:WU-1b"]))
        self.assertEqual(classify_recurrence_relevance([first])["classification"], "SINGLE_CURRENT")
        self.assertEqual(classify_recurrence_relevance([first, second])["classification"], "REPEATED_CURRENT")
        self.assertEqual(classify_recurrence_relevance([first], resolution="RESOLVED")["classification"], "ALREADY_RESOLVED")
        self.assertEqual(classify_recurrence_relevance([first], resolution="SUPERSEDED")["classification"], "SUPERSEDED")
        self.assertEqual(classify_recurrence_relevance([first], resolution="RETRACTED")["classification"], "INVALIDATED_OR_RETRACTED")
        self.assertEqual(classify_recurrence_relevance([first], preservation=True)["classification"], "PRESERVATION_EVIDENCE")
        self.assertTrue(classify_recurrence_relevance([first, second])["source_refs"])
        with self.assertRaises(ValueError):
            classify_recurrence_relevance([first], authoritative_source=True)
        with self.assertRaisesRegex(ValueError, "CORRELATION_CONFLICT"):
            classify_recurrence_relevance([first, normalize_process_evidence(self.process_evidence(source="review-result", content={"observation": "review failed", "outcome": "FAIL"}))])
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_PROCESS_EVIDENCE"):
            classify_recurrence_relevance([normalize_process_evidence(self.process_evidence(completeness="PARTIAL"))])

    def test_c6_harvest_relation_remains_reference_only(self):
        evidence = normalize_process_evidence(self.process_evidence())
        feedback = derive_framework_feedback(build_process_review_from_evidence([evidence], POLICY["strategy_profile_id"]), [evidence], kind="CAPABILITY_REUSE_SUCCESS")
        candidate = build_improvement_candidate(feedback, [evidence], problem_class="CAPABILITY_REUSE_SUCCESS", management_question="Inspect reuse?")
        self.assertEqual(classify_harvest_relation(candidate)["classification"], "NO_HARVEST_RELATION")
        self.assertEqual(classify_harvest_relation({**candidate, "existing_harvest_route": "harvest:existing-route"})["classification"], "HARVEST_REFERENCE_ELIGIBLE")
        self.assertEqual(classify_harvest_relation({**candidate, "existing_harvest_route": "invalid"})["classification"], "HARVEST_RELATION_AMBIGUOUS")

    def test_c7_management_input_is_non_authorizing_with_default_no_decision_no_mutation(self):
        evidence = normalize_process_evidence(self.process_evidence())
        review = build_process_review_from_evidence([evidence], POLICY["strategy_profile_id"])
        feedback = derive_framework_feedback(review, [evidence], kind="OBSERVED_GAP")
        candidate = build_improvement_candidate(feedback, [evidence], problem_class="OBSERVED_GAP", management_question="Inspect the observed gap?")
        result = build_framework_management_review_input(review, feedback, candidate, [evidence])
        self.assertEqual((result["decision"], result["mutation"]), ("NO_DECISION", "NO_MUTATION"))
        self.assertEqual(result["candidate_identity"], candidate["candidate_identity"])
        self.assertTrue(result["evidence_refs"])
        self.assertFalse(set(result).intersection({"instruction", "work_unit", "scope_authorization", "release_authority"}))

    def test_c8_closed_loop_matrix_preserves_evidence_classification_and_candidate_non_authority(self):
        complete = normalize_process_evidence(self.process_evidence())
        duplicate = normalize_process_evidence(self.process_evidence())
        stale = normalize_process_evidence(self.process_evidence(source="stale-result", source_record_refs=["record:stale"]))
        preservation = normalize_process_evidence(self.process_evidence(source="preservation-result", source_record_refs=["record:preservation"]))
        incomplete = normalize_process_evidence(self.process_evidence(completeness="PARTIAL", source_record_refs=["record:incomplete"]))

        review = build_process_review_from_evidence([complete, duplicate, incomplete], POLICY["strategy_profile_id"])
        self.assertEqual(review.codex_tasks, 1)
        feedback = derive_framework_feedback(review, [complete], kind="OBSERVED_GAP")
        candidate = build_improvement_candidate(feedback, [complete], problem_class="OBSERVED_GAP", management_question="Reject or retain this observation?")
        management_input = build_framework_management_review_input(review, feedback, candidate, [complete])
        rejected_management_input = build_framework_management_review_input(review, feedback, {**candidate, "status": "REJECTED"}, [complete])

        self.assertEqual(classify_recurrence_relevance([stale], resolution="SUPERSEDED")["classification"], "SUPERSEDED")
        self.assertEqual(classify_recurrence_relevance([complete], resolution="RESOLVED")["classification"], "ALREADY_RESOLVED")
        self.assertEqual(classify_recurrence_relevance([preservation], preservation=True)["classification"], "PRESERVATION_EVIDENCE")
        self.assertEqual((candidate["status"], management_input["decision"], management_input["mutation"]), ("OBSERVATION_ONLY", "NO_DECISION", "NO_MUTATION"))
        self.assertEqual((rejected_management_input["decision"], rejected_management_input["mutation"]), ("NO_DECISION", "NO_MUTATION"))
        self.assertFalse(framework_feedback_authorizes_mutation({"framework_management_only": True}, feedback))
        self.assertFalse(set(candidate).intersection({"instruction", "work_unit", "authorized_actions", "scope_authorization", "framework_mutation", "publication", "release"}))
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_PROCESS_EVIDENCE"):
            classify_recurrence_relevance([incomplete])

    def test_valid_fixed_execution_policy_is_accepted(self):
        self.assertEqual(validate_execution_policy(POLICY), [])
        self.assertEqual(validate_execution_policy(None), [])

    def test_project_strategy_profile_governs_work_units_and_requires_explicit_change(self):
        profile_a = POLICY["strategy_profile_id"]
        self.assertEqual(
            validate_project_strategy_lifecycle(
                POLICY,
                [{"work_unit_id": "WU-1", "strategy_profile_id": profile_a},
                 {"work_unit_id": "WU-2", "strategy_profile_id": profile_a}],
            ),
            [],
        )
        self.assertIn(
            "RECONCILIATION_REQUIRED",
            validate_project_strategy_lifecycle(
                POLICY,
                [{"work_unit_id": "WU-1", "strategy_profile_id": profile_a},
                 {"work_unit_id": "WU-2", "strategy_profile_id": "PROFILE_B"}],
            ),
        )
        changed_policy = {**POLICY, "strategy_profile_id": "PROFILE_B"}
        self.assertEqual(
            validate_project_strategy_lifecycle(
                changed_policy,
                [{"work_unit_id": "WU-3", "strategy_profile_id": "PROFILE_B"}],
                governed_strategy_change={
                    "requirement_ref": "requirement:strategy-change-1",
                    "accepted_strategy_profile_id": "PROFILE_B",
                },
            ),
            [],
        )
        self.assertEqual(validate_project_strategy_lifecycle(None, [{"strategy_profile_id": "PROFILE_B"}]), [])

    def test_closed_work_unit_record_is_bounded_and_unknown_usage_is_retained(self):
        record = {
            "work_unit_id": "WU-1", "final_result": "PASS", "codex_retries": 1,
            "gpt_interventions": 0, "review_rounds": 1, "remediation_rounds": 0,
            "handoff_result": "PASS", "usage": "UNKNOWN", "git_sha": "a" * 40,
            "result_ref": "result:WU-1",
        }
        self.assertEqual(validate_work_unit_process_record(record), [])
        review = build_process_review([record], POLICY["strategy_profile_id"])
        self.assertEqual(review.usage, "UNKNOWN")
        self.assertEqual(review.codex_tasks, 1)
        self.assertEqual(review.project_result, "PASS")
        self.assertEqual((review.work_unit_ids, review.result_refs), (("WU-1",), ("result:WU-1",)))
        self.assertIn(
            "PROCESS_REVIEW_INVALID",
            validate_work_unit_process_record({key: value for key, value in record.items() if key != "result_ref"}),
        )

    def test_process_review_aggregates_reliable_record_usage_without_overriding_explicit_usage(self):
        def record(identifier, usage):
            return {"work_unit_id": identifier, "final_result": "PASS", "codex_retries": 0,
                    "gpt_interventions": 0, "review_rounds": 0, "remediation_rounds": 0,
                    "handoff_result": "PASS", "usage": usage, "git_sha": "a" * 40,
                    "result_ref": f"result:{identifier}"}
        self.assertEqual(build_process_review([record("WU-0", "UNKNOWN")], POLICY["strategy_profile_id"]).usage, "UNKNOWN")
        self.assertEqual(build_process_review([record("WU-1", {"observed_units": 1})], POLICY["strategy_profile_id"]).usage, {"observed_units": 1})
        self.assertEqual(build_process_review([record("WU-1", {"observed_units": 1}), record("WU-2", {"observed_units": 2})], POLICY["strategy_profile_id"]).usage, {"observed_units": 3})
        self.assertEqual(build_process_review([record("WU-1", {"observed_units": 1})], POLICY["strategy_profile_id"], usage={"observed_units": 9}).usage, {"observed_units": 9})

    def test_process_review_aggregates_observable_counters_and_unknown_usage(self):
        review = build_process_review(
            [{"codex_tasks": 2, "codex_retries": 1, "project_result": "PASS"},
             {"review_rounds": 1, "handoffs": 1}],
            "PROJECT_PROFILE_001",
        )
        self.assertIsInstance(review, ProcessReview)
        self.assertEqual((review.codex_tasks, review.codex_retries, review.review_rounds, review.handoffs), (2, 1, 1, 1))
        self.assertEqual(review.project_result, "PASS")
        self.assertEqual(review.usage, "UNKNOWN")

    def test_process_review_retains_all_observable_counters(self):
        review = build_process_review(
            [{
                "codex_tasks": 1,
                "codex_retries": 2,
                "gpt_interventions": 1,
                "review_rounds": 2,
                "remediation_rounds": 1,
                "handoffs": 1,
                "handoff_failures": 0,
                "project_result": "PASS",
            }],
            "PROJECT_PROFILE_001",
            usage=None,
        )

        self.assertEqual(
            (
                review.codex_tasks,
                review.codex_retries,
                review.gpt_interventions,
                review.review_rounds,
                review.remediation_rounds,
                review.handoffs,
                review.handoff_failures,
                review.project_result,
                review.usage,
            ),
            (1, 2, 1, 2, 1, 1, 0, "PASS", "UNKNOWN"),
        )

    def test_reasoning_template_has_only_bounded_execution_record_fields(self):
        content = (ROOT / ".gpt-codex/project-template/.harness/REASONING.template.md").read_text(encoding="utf-8")

        self.assertIn("## Execution Record Format", content)
        for label in (
            "TASK:", "METHOD:", "KEY_DECISION:", "ERROR_CATEGORY:",
            "CODEX_RETRIES:", "GPT_INTERVENTIONS:", "REVIEW_ROUNDS:",
            "REMEDIATION_ROUNDS:", "HANDOFF_RESULT:", "FINAL_RESULT:", "GIT_SHA:",
            "WORK_UNIT_ID:", "RESULT_REF:", "USAGE:",
        ):
            self.assertIn(label, content)
        for forbidden in (
            "RAW_PROMPT", "PROMPT", "CHAIN_OF_THOUGHT", "PRIVATE_REASONING",
            "SCRATCHPAD", "REASONING_TRANSCRIPT", "TOKEN_TRACE",
        ):
            self.assertNotIn(forbidden, content)

    def test_feedback_is_evidence_only_and_rejects_authority(self):
        record = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                  "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        self.assertEqual(validate_framework_feedback(record), [])
        self.assertIsInstance(FrameworkFeedback(**record), FrameworkFeedback)
        for key in ("authorized_actions", "framework_mutation", "policy_update", "release_authority", "adoption_authority"):
            with self.subTest(key=key):
                self.assertEqual(validate_framework_feedback({**record, key: True}), ["FRAMEWORK_FEEDBACK_INVALID"])
        self.assertEqual(
            validate_framework_feedback({**record, "framework_mutation": "APPLY_NOW"}),
            ["FRAMEWORK_FEEDBACK_INVALID"],
        )

    def test_valid_feedback_is_evidence_but_never_mutation_authority(self):
        feedback = {"problem": "review overhead", "reason": "broad scope", "local_solution": "smaller tasks",
                    "result": "PASS", "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        ordinary = {"project_id": "PRJ-1", "governance_profile": "STANDARD",
                    "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"}}
        management = {"framework_management_only": True}

        self.assertEqual(validate_framework_evolution_boundary(ordinary, feedback), [])
        self.assertFalse(framework_feedback_authorizes_mutation(ordinary, feedback))
        self.assertEqual(validate_framework_evolution_boundary(management, feedback), [])
        self.assertFalse(framework_feedback_authorizes_mutation(management, feedback))
        for control in (None, [], {}, {"roots": None}):
            with self.subTest(control=control):
                self.assertEqual(
                    validate_framework_evolution_boundary(control, feedback),
                    ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
                )
        for roots in (
            {"project_role": "OTHER", "framework_role": "ADVISORY"},
            {"project_role": "AUTHORITATIVE", "framework_role": "SELF_MANAGED"},
        ):
            with self.subTest(roots=roots):
                self.assertEqual(
                    validate_framework_evolution_boundary({"roots": roots}, feedback),
                    ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
                )
        for control in (None, []):
            with self.subTest(malformed_control=control):
                self.assertFalse(framework_feedback_authorizes_mutation(control, feedback))
        for malformed_feedback in (None, {"framework_mutation": "APPLY_NOW"}):
            with self.subTest(malformed_feedback=malformed_feedback):
                self.assertFalse(framework_feedback_authorizes_mutation(ordinary, malformed_feedback))

    def test_feedback_template_is_evidence_only(self):
        content = (ROOT / ".gpt-codex/project-template/.harness/FEEDBACK.template.md").read_text(encoding="utf-8")

        self.assertIn("## Authority Boundary", content)
        self.assertIn("This file is project evidence only.", content)
        self.assertIn("Global evolution occurs only in the gpt-codex-framework management project after User approval.", content)
        for forbidden in ("APPROVE:", "APPLY:", "AUTHORIZED_ACTIONS:", "RELEASE:", "ADOPT:"):
            self.assertNotIn(forbidden, content)

    def test_feedback_evidence_refs_are_immutable_and_validated(self):
        feedback = FrameworkFeedback("p", "r", "s", "PASS", True, ("result:1",))
        self.assertIsInstance(feedback.evidence_refs, tuple)
        with self.assertRaises((AttributeError, TypeError)):
            feedback.evidence_refs += ("result:2",)
        with self.assertRaises(AttributeError):
            feedback.evidence_refs.append("result:2")
        base = {"problem": "p", "reason": "r", "local_solution": "s", "result": "PASS",
                "framework_change_recommended": True, "evidence_refs": ["result:1"]}
        for refs in ([], [""], ["   "], [123], ["result:1", ""], "result:1", None):
            with self.subTest(refs=refs):
                self.assertEqual(validate_framework_feedback({**base, "evidence_refs": refs}), ["FRAMEWORK_FEEDBACK_INVALID"])

    def test_policy_and_counter_negatives_and_validator_reuse(self):
        import framework_feedback
        import validate_project
        self.assertIs(validate_project.validate_execution_policy, framework_feedback.validate_execution_policy)
        for key, value in (("strategy_profile_id", ""), ("task_splitting", "OTHER"),
                           ("instruction_policy", "OTHER"), ("result_return_policy", "OTHER"),
                           ("review_policy", "OTHER")):
            with self.subTest(key=key):
                policy = dict(POLICY); policy[key] = value
                self.assertEqual(validate_execution_policy(policy), ["EXECUTION_POLICY_INVALID"])
        for record in ({"codex_retries": -1}, {"codex_retries": True}, {"review_rounds": -1}):
            with self.subTest(record=record):
                with self.assertRaisesRegex(ValueError, "PROCESS_REVIEW_INVALID"):
                    build_process_review([record], "PROJECT_PROFILE_001")

    def test_policy_key_and_length_boundaries(self):
        for key in ("strategy_profile_id", "review_policy"):
            policy = dict(POLICY); del policy[key]
            self.assertEqual(validate_execution_policy(policy), ["EXECUTION_POLICY_INVALID"])
        policy = dict(POLICY); policy["unexpected_policy_field"] = "x"
        self.assertEqual(validate_execution_policy(policy), ["EXECUTION_POLICY_INVALID"])
        policy = dict(POLICY); policy["strategy_profile_id"] = "x" * 128
        self.assertEqual(validate_execution_policy(policy), [])
        for key in ("strategy_profile_id", "gpt_orchestrator_strategy"):
            policy = dict(POLICY); policy[key] = "x" * 129
            self.assertEqual(validate_execution_policy(policy), ["EXECUTION_POLICY_INVALID"])

    def test_validate_project_cli_reports_malformed_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gov = root / ".gpt-codex"; gov.mkdir()
            policy = dict(POLICY); del policy["strategy_profile_id"]
            (gov / "CONTROL.json").write_text(json.dumps({
                "kernel_version": "2.0.0", "schema_version": 1, "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "framework_management_only": True, "governance_profile": "FRAMEWORK_MANAGEMENT",
                "framework": {"adopted_version": "2.0.0", "last_evaluated_version": "2.0.0", "evaluation_result": "ADOPTED"},
                "roots": {"project_role": "AUTHORITATIVE", "framework_role": "SELF_MANAGED", "framework_kernel_access": "READ_ONLY", "framework_builtins_access": "READ_ONLY"},
                "extensions": {"skills": [], "guardrails": [], "fitness": []}, "permissions": {}, "complexity": {}, "execution_policy": policy,
            }), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({"kernel_version": "2.0.0", "schema_version": 1, "project_id": "PROJECT-ONE", "revision": 1, "state": "ACTIVE"}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / ".gpt-codex/scripts/validate_project.py"), str(root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("EXECUTION_POLICY_INVALID", result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
