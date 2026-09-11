from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SyncSnapshot:
    local_head_sha: str | None
    remote_head_sha: str | None
    remote_ref: str | None
    dirty: bool
    local_ahead: int
    remote_ahead: int
    diverged: bool


@dataclass(frozen=True)
class SyncDecision:
    decision: str
    reason: str
    mutation_allowed: bool
    publish_allowed: bool


def _deny(decision: str, reason: str, mutation: bool = False, publish: bool = False) -> SyncDecision:
    return SyncDecision(decision, reason, mutation, publish)


def evaluate_sync_preflight(
    snapshot: SyncSnapshot,
    expected_base_sha: str | None,
    expected_remote_ref: str | None,
    expected_remote_head_sha: str | None,
    expected_state_revision: int,
    current_state_revision: int,
) -> SyncDecision:
    if snapshot.remote_head_sha is None or snapshot.remote_ref is None:
        return _deny("REMOTE_UNAVAILABLE", "REMOTE_UNAVAILABLE")
    if snapshot.dirty:
        return _deny("RECONCILIATION_REQUIRED", "DIRTY_WORKTREE_RECONCILIATION_REQUIRED")
    if snapshot.diverged:
        return _deny("RECONCILIATION_REQUIRED", "LOCAL_REMOTE_DIVERGED")
    if snapshot.local_ahead:
        return _deny("RECONCILIATION_REQUIRED", "LOCAL_AHEAD")
    if snapshot.remote_ahead:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_AHEAD")
    if expected_base_sha is not None and snapshot.local_head_sha != expected_base_sha:
        return _deny("RECONCILIATION_REQUIRED", "EXPECTED_BASE_SHA_MISMATCH")
    if expected_remote_ref is not None and snapshot.remote_ref != expected_remote_ref:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_REF_MISMATCH")
    if expected_remote_head_sha is not None and snapshot.remote_head_sha != expected_remote_head_sha:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_HEAD_MISMATCH")
    if expected_state_revision != current_state_revision:
        return _deny("RECONCILIATION_REQUIRED", "STALE_STATE_REVISION")
    return SyncDecision("CLEAN_SYNCED", "CLEAN_SYNCED", True, True)


def evaluate_new_work_preflight(
    snapshot: SyncSnapshot,
    expected_base_sha: str | None,
    expected_remote_ref: str | None,
    expected_remote_head_sha: str | None,
    expected_state_revision: int,
    current_state_revision: int,
) -> SyncDecision:
    decision = evaluate_sync_preflight(
        snapshot, expected_base_sha, expected_remote_ref, expected_remote_head_sha,
        expected_state_revision, current_state_revision,
    )
    if decision.decision != "CLEAN_SYNCED":
        return SyncDecision(decision.decision, decision.reason, False, False)
    return decision


def evaluate_active_work_degraded_continuation(
    identity_validated: bool,
    initial_clean_sync: bool,
    authorized_active: bool,
    remote_available: bool,
    requested_new_work_unit: bool,
) -> SyncDecision:
    if requested_new_work_unit:
        return _deny("RECONCILIATION_REQUIRED", "ACTIVE_WORK_CANNOT_START_SECOND_WORK_UNIT")
    if not (identity_validated and initial_clean_sync and authorized_active):
        return _deny("RECONCILIATION_REQUIRED", "ACTIVE_WORK_DEGRADED_AUTHORIZATION_MISSING")
    if remote_available:
        return SyncDecision("RECONNECT_PREFLIGHT_REQUIRED", "REMOTE_RECONNECT_REVALIDATION_REQUIRED", True, False)
    return SyncDecision("LOCAL_COMPLETE", "REMOTE_UNAVAILABLE", True, False)


def evaluate_publish_gate(binding: Any, sync: SyncDecision, push_status: str, remote_verification: str, state_revision_match: bool) -> SyncDecision:
    if not getattr(binding, "mutation_allowed", False) or not getattr(binding, "identity_match", False):
        return _deny("BLOCKED", "GITHUB_REPOSITORY_MISMATCH")
    if not state_revision_match:
        return _deny("RECONCILIATION_REQUIRED", "STALE_STATE_REVISION")
    if sync.decision != "CLEAN_SYNCED":
        return _deny("LOCAL_COMPLETE", "SYNC_PENDING")
    if push_status != "SUCCEEDED":
        return _deny("LOCAL_COMPLETE", "SYNC_PENDING")
    if remote_verification != "VERIFIED":
        return _deny("LOCAL_COMPLETE", "REMOTE_VERIFICATION_FAILED")
    return SyncDecision("SYNCED", "REMOTE_PUBLICATION_VERIFIED", True, True)


def verify_remote_publication(
    remote_ref: str,
    expected_publication_commit: str,
    observed_repository_id: str,
    bound_repository_id: str,
    object_reachable: bool,
    observed_remote_ref: str | None = None,
    observed_remote_head: str | None = None,
    work_reachable: bool = True,
    result_present: bool = True,
    state_present: bool = True,
) -> dict[str, Any]:
    if not observed_repository_id or not bound_repository_id or observed_repository_id != bound_repository_id:
        return {"status": "FAILED", "reason": "GITHUB_REPOSITORY_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if not observed_remote_ref and observed_remote_head is None:
        return {"status": "UNAVAILABLE", "reason": "REMOTE_UNAVAILABLE", "evidence_type": "TOOL_OBSERVED"}
    if observed_remote_ref is not None and observed_remote_ref != remote_ref:
        return {"status": "FAILED", "reason": "REMOTE_REF_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if observed_remote_head is not None and observed_remote_head != expected_publication_commit:
        return {"status": "FAILED", "reason": "REMOTE_HEAD_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if not (object_reachable and work_reachable and result_present and state_present):
        return {"status": "FAILED", "reason": "REMOTE_OBJECT_OR_RECORD_MISSING", "evidence_type": "TOOL_OBSERVED"}
    return {
        "status": "VERIFIED",
        "reason": "REMOTE_PUBLICATION_VERIFIED",
        "evidence_type": "TOOL_OBSERVED",
        "remote_ref": remote_ref,
        "remote_head_sha": expected_publication_commit,
    }
