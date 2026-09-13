from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable


_REVIEW_STAGES = frozenset({"DESIGN", "PLAN", "IMPLEMENTATION"})
_PENDING_VERIFICATION = frozenset({"NOT_ATTEMPTED", "INCOMPLETE", "UNAVAILABLE", "PENDING"})
_CONFLICTING_VERIFICATION = frozenset({
    "DIVERGED",
    "STALE_STATE_REVISION",
    "IDENTITY_CONFLICT",
    "REPOSITORY_MISMATCH",
    "REMOTE_REF_MISMATCH",
    "REMOTE_HEAD_MISMATCH",
})
_FORBIDDEN_REVIEW_OPERATIONS = frozenset({
    "AMEND",
    "REBASE",
    "RESET_REVIEWED",
    "FORCE_PUSH",
    "FORCE_WITH_LEASE",
    "REPLACE_BRANCH",
    "DELETE_BRANCH",
    "MERGE_MAIN",
    "TAG",
    "RELEASE",
    "PUBLISH",
})
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


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


def review_routing_for_stage(stage: str, remote_trigger: str | None = None) -> dict[str, str]:
    """Return the single review route for a protocol artifact stage."""

    if stage not in _REVIEW_STAGES:
        raise ValueError("UNKNOWN_REVIEW_STAGE")
    if remote_trigger is not None and (not isinstance(remote_trigger, str) or not remote_trigger.strip()):
        raise ValueError("INVALID_REMOTE_TRIGGER")
    if stage in {"DESIGN", "PLAN"}:
        route = {
            "stage": stage,
            "remote_review_visibility": "REQUIRED",
            "gpt_review": "REQUIRED",
            "reviewer_role": "GPT_REVIEWER",
        }
    else:
        route = {
            "stage": stage,
            "remote_review_visibility": "OPTIONAL",
            "technical_review": "CODEX_REVIEWER",
        }
    route["remote_trigger"] = remote_trigger or (
        "FORMAL_REVIEW" if stage in {"DESIGN", "PLAN"} else "MILESTONE_OR_RISK"
    )
    return route


def validate_review_revision(
    previous_reviewed_sha: str | None,
    candidate_sha: str,
    is_ancestor: Callable[[str, str], bool],
) -> list[str]:
    """Require a valid candidate revision to descend from formal review evidence."""

    if (previous_reviewed_sha is not None and not _SHA_RE.fullmatch(previous_reviewed_sha)) or not isinstance(candidate_sha, str) or not _SHA_RE.fullmatch(candidate_sha):
        return ["RECONCILIATION_REQUIRED", "REVIEWED_REVISION_INVALID"]
    if previous_reviewed_sha is None:
        return []
    if not callable(is_ancestor):
        return ["RECONCILIATION_REQUIRED", "ANCESTRY_VERIFICATION_FAILED"]
    try:
        valid_ancestry = bool(is_ancestor(previous_reviewed_sha, candidate_sha))
    except Exception:
        valid_ancestry = False
    if not valid_ancestry:
        return ["RECONCILIATION_REQUIRED", "REVIEWED_REVISION_NOT_ANCESTOR"]
    return []


def validate_review_history_operation(stage: str, operation: str) -> list[str]:
    """Deny reviewed DESIGN/PLAN history rewrites and publication operations."""

    if stage not in _REVIEW_STAGES:
        return ["INVALID_REVIEW_STAGE"]
    if not isinstance(operation, str) or not operation.strip():
        return ["INVALID_REVIEW_OPERATION"]
    if stage in {"DESIGN", "PLAN"} and operation.upper() in _FORBIDDEN_REVIEW_OPERATIONS:
        return ["ROLE_AUTHORITY_CONFLICT", "REVIEW_HISTORY_REWRITE_FORBIDDEN"]
    return []


def classify_review_sync(
    stage: str,
    push_status: str,
    remote_verification: str,
    remote_head_sha: str | None,
    expected_head_sha: str,
) -> str:
    """Classify review synchronization without treating missing evidence as conflict."""

    if stage not in _REVIEW_STAGES:
        raise ValueError("UNKNOWN_REVIEW_STAGE")
    if not isinstance(expected_head_sha, str) or not _SHA_RE.fullmatch(expected_head_sha):
        raise ValueError("EXPECTED_HEAD_REVISION_INVALID")
    if remote_head_sha is not None and remote_head_sha != expected_head_sha:
        return "RECONCILIATION_REQUIRED"
    if remote_verification in _CONFLICTING_VERIFICATION:
        return "RECONCILIATION_REQUIRED"
    if push_status == "SUCCEEDED" and remote_verification == "VERIFIED" and remote_head_sha == expected_head_sha:
        return "SYNCED"
    return "LOCAL_COMPLETE / SYNC_PENDING"


def evaluate_attestation_chain(facts: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the bounded W -> verified W -> management-only P protocol."""
    work_sha = facts.get("work_sha")
    publication_sha = facts.get("publication_sha")
    if not facts.get("verified_work") or not publication_sha:
        return {
            "status": "LOCAL_COMPLETE",
            "sync_status": "SYNC_PENDING",
            "remote_verification": "NOT_ATTEMPTED",
            "publication_authority": "PUBLICATION_CANDIDATE_ONLY",
            "verified_baseline_sha": None,
            "publication_sha": publication_sha,
        }
    if (
        not work_sha
        or not facts.get("publication_references_work")
        or facts.get("publication_references_self")
        or not facts.get("publication_is_management_only")
        or not facts.get("generic_tree_matches")
    ):
        return {
            "status": "RECONCILIATION_REQUIRED",
            "sync_status": "RECONCILIATION_REQUIRED",
            "remote_verification": "FAILED",
            "publication_authority": "PUBLICATION_CANDIDATE_ONLY",
            "verified_baseline_sha": work_sha,
            "publication_sha": publication_sha,
        }
    return {
        "status": "PASS",
        "sync_status": "SYNCED",
        "remote_verification": "VERIFIED",
        "publication_authority": "CONFIRMED_PUBLICATION",
        "verified_baseline_sha": work_sha,
        "publication_sha": publication_sha,
    }


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
