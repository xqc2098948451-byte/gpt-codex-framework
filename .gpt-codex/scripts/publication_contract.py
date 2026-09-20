from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from role_communication import is_intrinsic_approval_result


CANDIDATE_AUTHORITY = "PUBLICATION_CANDIDATE_ONLY"
VERIFIED_AUTHORITY = "CONFIRMED_PUBLICATION"
_INTRINSIC_APPROVAL_OUTER_KEYS = frozenset({
    "kernel_version", "schema_version", "project_id", "work_unit_id", "extension", "status",
    "return_to_gpt_required", "source_project_context_id", "source_project_name", "framework_version",
    "result_message_type", "result_id", "decision", "approved_instruction", "response_to_instruction_id",
    "responder_role", "return_role", "review_target_revision", "finding_ids", "fix_round",
    "remediation_decision_ref", "protocol_error", "role_observation", "artifact_stage", "artifact_path",
    "source_github_repository_id", "source_github_repository_full_name", "current_remote_ref", "local_head_sha",
    "remote_head_sha", "sync_status", "push_status", "remote_verification", "publication_authority",
    "state_revision", "execution", "changed", "verify", "evidence_refs", "deviations", "blockers", "git",
    "git_base_sha", "implementation_sha", "parallel_batch", "execution_unit", "observability_fitness",
    "extension_evidence_refs", "next_gpt_action", "completion_evidence", "completion_gate",
})


def _is_intrinsic_approval_transaction(result: Mapping[str, Any]) -> bool:
    """Fail closed unless every outer field belongs to the intrinsic Result surface."""
    return set(result).issubset(_INTRINSIC_APPROVAL_OUTER_KEYS) and is_intrinsic_approval_result(result)


def classify_release_phase(facts: Mapping[str, Any]) -> str:
    """Derive an observational release phase from already supplied facts."""
    if not isinstance(facts, Mapping) or facts.get("candidate_consistent") is not True:
        return "RECONCILIATION_REQUIRED"
    candidate_sha = facts.get("candidate_sha")
    if not isinstance(candidate_sha, str) or not candidate_sha:
        return "RECONCILIATION_REQUIRED"
    reviewed_sha = facts.get("reviewed_sha")
    if reviewed_sha is not None and reviewed_sha != candidate_sha:
        return "RECONCILIATION_REQUIRED"
    if facts.get("local_validation_passed") is not True or reviewed_sha != candidate_sha:
        return "CANDIDATE"
    phase = "LOCALLY_VERIFIED"
    result = facts.get("publication_result")
    if not isinstance(result, Mapping):
        return phase
    if result.get("remote_head_sha") not in {candidate_sha, result.get("verified_baseline_sha")}:
        return "RECONCILIATION_REQUIRED"
    if result.get("publication_authority") != VERIFIED_AUTHORITY or validate_result_authority(result):
        return phase
    phase = "PUBLISHED"
    activation = facts.get("remote_activation")
    if not isinstance(activation, Mapping):
        return phase
    if activation.get("candidate_sha") not in {None, candidate_sha}:
        return "RECONCILIATION_REQUIRED"
    if activation.get("status") != "VERIFIED" or activation.get("evidence_type") != "TOOL_OBSERVED":
        return phase
    state = facts.get("state")
    durable_results = facts.get("durable_results")
    if not isinstance(state, Mapping):
        return phase
    if state.get("continuity", {}).get("sync_status") != "SYNCED":
        return phase
    if validate_state_authority(state, durable_results if isinstance(durable_results, Mapping) else {}):
        return "RECONCILIATION_REQUIRED"
    if state.get("continuity", {}).get("latest_verified_remote_sha") != candidate_sha:
        return "RECONCILIATION_REQUIRED"
    return "REMOTE_ACTIVE"


def validate_completion_evidence(result: Mapping[str, Any]) -> list[str]:
    """Fail closed when a PASS/BLOCKED result lacks its bounded closure facts."""
    if _is_intrinsic_approval_transaction(result):
        return []
    evidence = result.get("completion_evidence")
    if not isinstance(evidence, Mapping):
        # Historical publication results remain valid until a governed result
        # opts into CAP-01; new INCOMPLETE/BLOCKED states require the evidence.
        return ["COMPLETION_EVIDENCE_REQUIRED"] if result.get("status") in {"INCOMPLETE", "BLOCKED"} or (result.get("status") == "PASS" and "result_message_type" in result) else []
    state = evidence.get("execution_state")
    if result.get("status") == "PASS":
        required = (
            state == "COMPLETED", evidence.get("process_completed") is True,
            evidence.get("exit_code") == 0,
            isinstance(evidence.get("intended_scope"), list) and evidence.get("intended_scope") == evidence.get("executed_scope"),
            isinstance(evidence.get("test_files_expected"), int) and evidence.get("test_files_expected") == evidence.get("test_files_executed"),
            isinstance(evidence.get("test_count"), int), evidence.get("failure_count") == 0,
            evidence.get("error_count") == 0,
            isinstance(evidence.get("validators_expected"), list) and isinstance(evidence.get("validators_completed"), list)
            and evidence.get("validators_expected") == evidence.get("validators_completed"),
        )
        return [] if all(required) else ["PASS_COMPLETION_EVIDENCE_INCOMPLETE"]
    if result.get("status") == "BLOCKED":
        return [] if state == "BLOCKED" and bool(evidence.get("blocker_evidence_refs")) else ["BLOCKED_REQUIRES_PROVEN_BLOCKER"]
    if result.get("status") == "INCOMPLETE":
        return [] if state == "INCOMPLETE" else ["INCOMPLETE_EXECUTION_STATE_REQUIRED"]
    return []


def validate_result_authority(
    result: Mapping[str, Any],
    verified_evidence_refs: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    status = result.get("status")
    sync_status = result.get("sync_status")
    remote_verification = result.get("remote_verification")
    authority = result.get("publication_authority")
    evidence_refs = result.get("evidence_refs") or []

    intrinsic_approval = _is_intrinsic_approval_transaction(result)
    if status == "PASS" and not intrinsic_approval and remote_verification != "VERIFIED":
        errors.append("PASS requires remote_verification=VERIFIED")
    if status == "PASS" and authority == CANDIDATE_AUTHORITY:
        errors.append("PUBLICATION_CANDIDATE_ONLY cannot have status=PASS")
    if sync_status == "SYNCED":
        if remote_verification != "VERIFIED":
            errors.append("SYNCED requires remote_verification=VERIFIED")
        if authority == CANDIDATE_AUTHORITY:
            errors.append("PUBLICATION_CANDIDATE_ONLY cannot have sync_status=SYNCED")
        if not evidence_refs:
            errors.append("SYNCED requires verified publication evidence refs")
        if not result.get("remote_head_sha"):
            errors.append("SYNCED requires remote_head_sha")
    if authority == CANDIDATE_AUTHORITY and sync_status == "SYNCED":
        errors.append("candidate authority cannot be synchronized")
    if verified_evidence_refs is not None and authority == VERIFIED_AUTHORITY:
        missing = set(evidence_refs) - set(verified_evidence_refs)
        if missing:
            errors.append(f"verified publication evidence missing: {sorted(missing)}")
    return errors


def validate_state_authority(
    state: Mapping[str, Any],
    durable_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    durable_results = durable_results or {}
    continuity = state.get("continuity") or {}
    evidence_refs = state.get("evidence_refs") or []
    result_ref = continuity.get("last_verified_result_ref")

    if state.get("state") == "COMPLETE":
        if not evidence_refs:
            errors.append("COMPLETE state requires durable evidence_refs")
        if not result_ref or result_ref not in durable_results:
            errors.append("COMPLETE state requires durable verified Result")
        else:
            result = durable_results[result_ref]
            errors.extend(f"COMPLETE result: {error}" for error in validate_result_authority(result))
            if _is_intrinsic_approval_transaction(result):
                errors.append("COMPLETE state cannot use intrinsic approval Result")
            if result.get("status") != "PASS":
                errors.append("COMPLETE state requires Result.status=PASS")

    if continuity.get("sync_status") == "SYNCED":
        latest_sha = continuity.get("latest_verified_remote_sha")
        if continuity.get("latest_synced_state_revision") != state.get("revision"):
            errors.append("SYNCED state requires current latest_synced_state_revision")
        if not evidence_refs:
            errors.append("SYNCED state requires durable evidence_refs")
        if not latest_sha:
            errors.append("SYNCED state requires latest_verified_remote_sha")
        if not result_ref or result_ref not in durable_results:
            errors.append("SYNCED state requires durable verified Result")
        else:
            result = durable_results[result_ref]
            errors.extend(f"SYNCED result: {error}" for error in validate_result_authority(result))
            if _is_intrinsic_approval_transaction(result):
                errors.append("SYNCED state cannot use intrinsic approval Result")
            if result.get("remote_verification") != "VERIFIED":
                errors.append("SYNCED state requires verified publication evidence")
            if latest_sha and result.get("remote_head_sha") not in {latest_sha, result.get("verified_baseline_sha")}:
                errors.append("latest_verified_remote_sha does not match verified Result")
    return errors
