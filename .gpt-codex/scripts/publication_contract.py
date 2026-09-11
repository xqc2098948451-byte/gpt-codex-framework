from __future__ import annotations

from collections.abc import Mapping
from typing import Any


CANDIDATE_AUTHORITY = "PUBLICATION_CANDIDATE_ONLY"
VERIFIED_AUTHORITY = "CONFIRMED_PUBLICATION"


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

    if status == "PASS" and remote_verification != "VERIFIED":
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
            if result.get("status") != "PASS":
                errors.append("COMPLETE state requires Result.status=PASS")

    if continuity.get("sync_status") == "SYNCED":
        latest_sha = continuity.get("latest_verified_remote_sha")
        if not latest_sha:
            errors.append("SYNCED state requires latest_verified_remote_sha")
        if not result_ref or result_ref not in durable_results:
            errors.append("SYNCED state requires durable verified Result")
        else:
            result = durable_results[result_ref]
            errors.extend(f"SYNCED result: {error}" for error in validate_result_authority(result))
            if result.get("remote_verification") != "VERIFIED":
                errors.append("SYNCED state requires verified publication evidence")
            if latest_sha and result.get("remote_head_sha") not in {latest_sha, result.get("verified_baseline_sha")}:
                errors.append("latest_verified_remote_sha does not match verified Result")
    return errors
