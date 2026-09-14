from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from context_binding import evaluate_cross_project_resource_boundary, load_project_identity
from kernel_rules import validate_slot_state_revision
from role_communication import validate_evolution_metadata_authority

from project_navigation import (
    affected_modules,
    classify_map_route,
    load_project_map,
    module_by_id,
    module_map_read_paths,
    normalise_relative_path,
    validate_navigation_identity,
)


RESUME_RELATIVE_PATH = Path("continuity") / "RESUME.json"

_SLOT_STATUSES = frozenset({"IDLE", "ACTIVE", "BLOCKED", "AWAITING_REVIEW", "REVIEWING", "COMPLETED"})
_IDLE_CLEARED_FIELDS = (
    "work_unit_id", "primary_module", "branch", "worktree", "base_sha",
    "current_head_sha", "last_accepted_sha", "instruction_id", "review_request_id",
    "review_result_ref", "finding_ref", "remediation_authorization_ref",
    "fix_instruction_id", "reviewer_reassignment_ref", "blocked_from_status", "block_reason",
)
_LEGAL_SLOT_EDGES = {
    "IDLE": frozenset({"IDLE", "ACTIVE", "BLOCKED"}),
    "ACTIVE": frozenset({"ACTIVE", "AWAITING_REVIEW", "BLOCKED"}),
    "AWAITING_REVIEW": frozenset({"AWAITING_REVIEW", "REVIEWING", "BLOCKED"}),
    "REVIEWING": frozenset({"REVIEWING", "ACTIVE", "BLOCKED", "COMPLETED"}),
    "BLOCKED": frozenset({"BLOCKED", "ACTIVE"}),
    "COMPLETED": frozenset({"COMPLETED", "IDLE"}),
}
_SLOT_BINDING_FIELDS = (
    "project_context_id", "work_unit_id", "role", "primary_module", "branch",
    "worktree", "base_sha", "current_head_sha", "last_accepted_sha", "state_revision",
)
_ASSIGNMENT_FIELDS = (
    "work_unit_id", "primary_module", "project_context_id", "branch", "worktree",
    "base_sha", "current_head_sha", "instruction_id", "next_action",
)
_ASSIGNMENT_STRING_FIELDS = (
    "work_unit_id", "primary_module", "project_context_id", "instruction_id", "next_action",
)
_COMMIT_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
_EVIDENCE_SOURCES = frozenset({"TOOL_OBSERVED", "USER_ASSERTED", "SYSTEM_DERIVED", "MODEL_INFERRED"})


def _unique_errors(errors: list[str]) -> list[str]:
    return list(dict.fromkeys(errors))


def validate_execution_slots(state: Mapping) -> list[str]:
    """Validate the current STATE-backed slot shape without changing STATE."""
    slots = state.get("active_execution_slots")
    if slots is None:
        return []
    if not isinstance(slots, list):
        return ["ACTIVE_EXECUTION_SLOTS_INVALID", "RECONCILIATION_REQUIRED"]

    errors: list[str] = []
    for slot in slots:
        if not isinstance(slot, Mapping):
            errors.extend(("ACTIVE_EXECUTION_SLOTS_INVALID", "RECONCILIATION_REQUIRED"))
            continue
        status = slot.get("status")
        if status not in _SLOT_STATUSES:
            errors.extend(("EXECUTION_SLOT_STATUS_INVALID", "RECONCILIATION_REQUIRED"))
            continue
        if validate_slot_state_revision(slot.get("state_revision"), state.get("revision")):
            errors.extend(("SLOT_STATE_REVISION_MISMATCH", "RECONCILIATION_REQUIRED"))
        if status == "IDLE" and (
            any(slot.get(field) is not None for field in _IDLE_CLEARED_FIELDS)
            or slot.get("next_action") != "AWAIT_ASSIGNMENT"
        ):
            errors.extend(("IDLE_SLOT_ASSIGNMENT_FORBIDDEN", "RECONCILIATION_REQUIRED"))
        if status == "BLOCKED":
            blocked_from_status = slot.get("blocked_from_status")
            block_reason = slot.get("block_reason")
            missing_blocked_fields = (
                blocked_from_status not in _SLOT_STATUSES
                or not isinstance(block_reason, str)
                or not block_reason.strip()
            )
            missing_remediation_correlation = (
                block_reason == "AWAITING_REMEDIATION_AUTHORIZATION"
                and any(
                    not isinstance(slot.get(field), str) or not slot[field]
                    for field in ("finding_ref", "review_request_id", "review_result_ref")
                )
            )
            if missing_blocked_fields or missing_remediation_correlation:
                errors.extend(("BLOCKED_SLOT_FIELDS_REQUIRED", "RECONCILIATION_REQUIRED"))
    return _unique_errors(errors)


def validate_slot_transition(previous: Mapping, current: Mapping) -> list[str]:
    """Validate a proposed lifecycle edge without authorizing or persisting it."""
    if not isinstance(previous, Mapping) or not isinstance(current, Mapping):
        return ["RECONCILIATION_REQUIRED"]
    previous_status = previous.get("status")
    current_status = current.get("status")
    if previous_status not in _SLOT_STATUSES or current_status not in _SLOT_STATUSES:
        return ["EXECUTION_SLOT_STATUS_INVALID", "RECONCILIATION_REQUIRED"]
    if previous_status == "COMPLETED" and current_status == "ACTIVE":
        return ["SLOT_IDLE_RESET_REQUIRED"]
    if previous_status == "BLOCKED" and (
        current_status == previous.get("blocked_from_status") and current_status != "ACTIVE"
    ):
        return ["SLOT_BLOCKED_RETURN_FORBIDDEN"]
    if current_status not in _LEGAL_SLOT_EDGES[previous_status]:
        return ["SLOT_TRANSITION_INVALID"]
    if previous_status == "BLOCKED" and current_status == "ACTIVE":
        if any(
            not isinstance(current.get(field), str) or not current[field]
            for field in ("remediation_authorization_ref", "fix_instruction_id")
        ):
            return ["RECONCILIATION_REQUIRED"]
    return []


def _reconciliation_required() -> None:
    raise ValueError("RECONCILIATION_REQUIRED")


def _current_slot(state: Mapping, slot_id: str, expected_revision: int) -> tuple[dict[str, Any], int]:
    if (
        not isinstance(state, Mapping)
        or not isinstance(slot_id, str)
        or not slot_id
        or validate_slot_state_revision(state.get("revision"), expected_revision)
        or validate_execution_slots(state)
    ):
        _reconciliation_required()
    slots = state.get("active_execution_slots")
    if not isinstance(slots, list):
        _reconciliation_required()
    matching_indexes = [
        index for index, candidate in enumerate(slots)
        if isinstance(candidate, Mapping) and candidate.get("slot_id") == slot_id
    ]
    if len(matching_indexes) != 1:
        _reconciliation_required()
    index = matching_indexes[0]
    return dict(slots[index]), index


def _updated_state(state: Mapping, slot_index: int, slot: dict[str, Any]) -> dict[str, Any]:
    updated = dict(state)
    slots = list(state["active_execution_slots"])
    slots[slot_index] = slot
    updated["active_execution_slots"] = slots
    updated["revision"] = state["revision"] + 1
    slot["state_revision"] = updated["revision"]
    return updated


def _valid_closure_refs(closure_refs: object) -> bool:
    return (
        isinstance(closure_refs, (list, tuple))
        and bool(closure_refs)
        and all(isinstance(reference, str) and reference.strip() for reference in closure_refs)
    )


def _valid_assignment(assignment: object, slot: Mapping) -> bool:
    if not isinstance(assignment, Mapping) or set(assignment) != set(_ASSIGNMENT_FIELDS):
        return False
    if any(
        not isinstance(assignment.get(field), str) or not assignment[field].strip()
        for field in _ASSIGNMENT_STRING_FIELDS
    ):
        return False
    if assignment["next_action"] == "AWAIT_ASSIGNMENT":
        return False
    if assignment["project_context_id"] != slot.get("project_context_id"):
        return False
    if any(
        value is not None and (not isinstance(value, str) or not value.strip())
        for value in (assignment["branch"], assignment["worktree"])
    ):
        return False
    return all(
        isinstance(assignment[field], str) and _COMMIT_SHA.fullmatch(assignment[field])
        for field in ("base_sha", "current_head_sha")
    )


def reset_completed_slot(
    state: Mapping,
    slot_id: str,
    closure_refs: object,
    expected_revision: int,
) -> dict[str, Any]:
    """Perform the only Task-3 completion reset: COMPLETED to fresh IDLE."""
    slot, slot_index = _current_slot(state, slot_id, expected_revision)
    if slot.get("status") != "COMPLETED" or not _valid_closure_refs(closure_refs):
        _reconciliation_required()
    reset = dict(slot)
    for field in _IDLE_CLEARED_FIELDS:
        reset[field] = None
    reset["status"] = "IDLE"
    reset["next_action"] = "AWAIT_ASSIGNMENT"
    if validate_slot_transition(slot, reset):
        _reconciliation_required()
    return _updated_state(state, slot_index, reset)


def activate_execution_slot(
    state: Mapping,
    slot_id: str,
    assignment: Mapping,
    expected_revision: int,
) -> dict[str, Any]:
    """Perform the only Task-3 assignment edge: IDLE to a fresh ACTIVE slot."""
    slot, slot_index = _current_slot(state, slot_id, expected_revision)
    if slot.get("status") != "IDLE" or not _valid_assignment(assignment, slot):
        _reconciliation_required()
    active = dict(slot)
    for field in _IDLE_CLEARED_FIELDS:
        active[field] = None
    active.update(assignment)
    active["status"] = "ACTIVE"
    if validate_slot_transition(slot, active):
        _reconciliation_required()
    return _updated_state(state, slot_index, active)


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _fact_matches(
    facts: Mapping,
    fact_name: str,
    reference_field: str,
    expected: object,
) -> bool:
    fact = facts.get(fact_name)
    return isinstance(fact, Mapping) and fact.get(reference_field) == expected


def block_for_remediation(
    state: Mapping,
    slot_id: str,
    finding_ref: str,
    review_ref: str,
    expected_revision: int,
) -> dict[str, Any]:
    """Record a reviewing slot's finding without granting remediation authority."""
    slot, slot_index = _current_slot(state, slot_id, expected_revision)
    if (
        slot.get("status") != "REVIEWING"
        or not _is_nonempty_string(finding_ref)
        or not _is_nonempty_string(review_ref)
        or not _is_nonempty_string(slot.get("review_request_id"))
    ):
        _reconciliation_required()
    blocked = dict(slot)
    blocked.update({
        "status": "BLOCKED",
        "review_result_ref": review_ref,
        "finding_ref": finding_ref,
        "remediation_authorization_ref": None,
        "fix_instruction_id": None,
        "blocked_from_status": "REVIEWING",
        "block_reason": "AWAITING_REMEDIATION_AUTHORIZATION",
        "next_action": "AWAIT_REMEDIATION_AUTHORIZATION",
    })
    if validate_slot_transition(slot, blocked) or validate_execution_slots(_updated_state(state, slot_index, blocked)):
        _reconciliation_required()
    return _updated_state(state, slot_index, blocked)


def _has_current_remediation_chain(
    slot: Mapping,
    authorization_ref: object,
    fix_instruction: object,
    expected_revision: int,
    authoritative_facts: object,
) -> bool:
    if not isinstance(authoritative_facts, Mapping):
        return False
    finding_ids = fix_instruction.get("finding_ids") if isinstance(fix_instruction, Mapping) else None
    required_facts = {
        "work_unit", "finding", "review_request", "review_result",
        "remediation_authorization", "current_git",
    }
    if not required_facts.issubset(authoritative_facts):
        return False
    if (
        not _is_nonempty_string(authorization_ref)
        or (
            slot.get("remediation_authorization_ref") is not None
            and slot.get("remediation_authorization_ref") != authorization_ref
        )
    ):
        return False
    if not _fact_matches(authoritative_facts, "work_unit", "work_unit_id", slot.get("work_unit_id")):
        return False
    if not _fact_matches(authoritative_facts, "finding", "finding_ref", slot.get("finding_ref")):
        return False
    if not _fact_matches(authoritative_facts, "review_request", "review_request_id", slot.get("review_request_id")):
        return False
    if not _fact_matches(authoritative_facts, "review_result", "review_result_ref", slot.get("review_result_ref")):
        return False
    if not _fact_matches(
        authoritative_facts,
        "remediation_authorization",
        "remediation_authorization_ref",
        authorization_ref,
    ):
        return False
    authorization = authoritative_facts["remediation_authorization"]
    if authorization.get("issuer_role") not in {"GPT_ORCHESTRATOR", "USER_APPROVER"}:
        return False
    review_result = authoritative_facts["review_result"]
    finding = authoritative_facts["finding"]
    reviewed_sha = review_result.get("review_target_revision")
    if (
        not isinstance(reviewed_sha, str)
        or not _COMMIT_SHA.fullmatch(reviewed_sha)
        or finding.get("review_target_revision") != reviewed_sha
        or not _fact_matches(authoritative_facts, "current_git", "current_head_sha", slot.get("current_head_sha"))
        or authoritative_facts["current_git"].get("current_head_sha") != reviewed_sha
    ):
        return False
    if (
        not isinstance(fix_instruction, Mapping)
        or not _is_nonempty_string(fix_instruction.get("instruction_id"))
        or (
            slot.get("fix_instruction_id") is not None
            and slot.get("fix_instruction_id") != fix_instruction.get("instruction_id")
        )
        or fix_instruction.get("instruction_type") != "FIX_INSTRUCTION"
        or fix_instruction.get("expected_base_sha") != reviewed_sha
        or fix_instruction.get("target_work_unit") != slot.get("work_unit_id")
        or not isinstance(finding_ids, list)
        or slot.get("finding_ref") not in finding_ids
    ):
        return False
    # This import is deliberately lazy: validate_project imports this module for
    # validation orchestration, while this mutation helper consumes its existing
    # pure Role Protocol authority gate without reproducing those rules.
    from validate_project import validate_instruction_authority
    return not validate_instruction_authority(fix_instruction, expected_revision)


def resume_authorized_remediation(
    state: Mapping,
    slot_id: str,
    authorization_ref: str,
    fix_instruction: Mapping,
    expected_revision: int,
    *,
    authoritative_facts: Mapping,
) -> dict[str, Any]:
    """Resume only a fully reconciled, explicitly authorized remediation."""
    slot, slot_index = _current_slot(state, slot_id, expected_revision)
    if (
        slot.get("status") != "BLOCKED"
        or slot.get("blocked_from_status") != "REVIEWING"
        or slot.get("block_reason") != "AWAITING_REMEDIATION_AUTHORIZATION"
        or not _has_current_remediation_chain(
            slot, authorization_ref, fix_instruction, expected_revision, authoritative_facts,
        )
    ):
        _reconciliation_required()
    active = dict(slot)
    active.update({
        "status": "ACTIVE",
        "remediation_authorization_ref": authorization_ref,
        "fix_instruction_id": fix_instruction["instruction_id"],
        "blocked_from_status": None,
        "block_reason": None,
        "next_action": "CONTINUE_IMPLEMENTATION",
    })
    if validate_slot_transition(slot, active) or validate_execution_slots(_updated_state(state, slot_index, active)):
        _reconciliation_required()
    return _updated_state(state, slot_index, active)


def _non_optimization_resume_fields() -> dict[str, Any]:
    return {
        "resume_mode": "COLD_RESUME",
        "map_route": "MAP_MISSING",
        "candidate_modules": [],
        "stale_modules": [],
        "module_map_reads": [],
        "required_reads": [],
        "hot_modules": [],
        "hot_files": [],
        "invalidated_context": [],
    }


def validate_reviewer_assignment(
    slot: Mapping,
    reviewer_ref: str,
    expected_revision: int,
    *,
    reassignment_instruction: Mapping | None = None,
    reassignment_evidence: Mapping | None = None,
    project_control: Mapping | None = None,
) -> list[str]:
    """Validate a review-request identity, never an agent or physical window."""
    if (
        not isinstance(slot, Mapping)
        or not _is_nonempty_string(reviewer_ref)
        or validate_slot_state_revision(slot.get("state_revision"), expected_revision)
        or not _is_nonempty_string(slot.get("review_request_id"))
    ):
        return ["RECONCILIATION_REQUIRED"]
    if reviewer_ref == slot.get("review_request_id"):
        return []
    if not _is_nonempty_string(slot.get("reviewer_reassignment_ref")):
        return ["RECONCILIATION_REQUIRED"]
    if (
        not isinstance(reassignment_instruction, Mapping)
        or not isinstance(reassignment_evidence, Mapping)
        or not isinstance(project_control, Mapping)
        or project_control.get("project_context_id") != slot.get("project_context_id")
    ):
        return ["RECONCILIATION_REQUIRED"]
    try:
        from validate_project import validate_instruction_authority
    except ImportError:
        return ["RECONCILIATION_REQUIRED"]
    if validate_instruction_authority(reassignment_instruction, expected_revision):
        return ["RECONCILIATION_REQUIRED"]
    if (
        reassignment_instruction.get("instruction_id") != reviewer_ref
        or reassignment_instruction.get("instruction_type") != "REVIEW_REQUEST"
        or reassignment_instruction.get("issuer_role") != "GPT_ORCHESTRATOR"
        or reassignment_instruction.get("executor_role") != "CODEX_REVIEWER"
        or reassignment_instruction.get("target_work_unit") != slot.get("work_unit_id")
        or reassignment_instruction.get("target_project_context_id") != slot.get("project_context_id")
        or reassignment_instruction.get("expected_state_revision") != expected_revision
        or reassignment_instruction.get("review_target_revision") != slot.get("current_head_sha")
    ):
        return ["RECONCILIATION_REQUIRED"]
    required_evidence = {
        "evidence_id": slot.get("reviewer_reassignment_ref"),
        "subject": "REVIEWER_REASSIGNMENT",
        "source_review_request_id": slot.get("review_request_id"),
        "target_review_request_id": reviewer_ref,
        "work_unit_id": slot.get("work_unit_id"),
        "state_revision": expected_revision,
        "current_head_sha": slot.get("current_head_sha"),
        "last_accepted_sha": slot.get("last_accepted_sha"),
    }
    if (
        any(reassignment_evidence.get(field) != value for field, value in required_evidence.items())
        or not _valid_evidence_record(
            reassignment_evidence, project_control, expected_revision, reject_model_inferred=True,
        )
    ):
        return ["RECONCILIATION_REQUIRED"]
    return []


def _recovery_result(status: str = "RECONCILIATION_REQUIRED") -> dict[str, Any]:
    return {"status": status, "reconciliation_required": True}


def _valid_evidence_record(
    evidence: Mapping, control: Mapping, expected_revision: int, *, reject_model_inferred: bool = False,
) -> bool:
    required = ("kernel_version", "schema_version", "evidence_id", "project_id", "source", "subject", "state_revision", "result")
    if (
        not isinstance(evidence, Mapping)
        or any(field not in evidence for field in required)
        or evidence.get("kernel_version") != "2.0.0"
        or evidence.get("schema_version") != 1
        or not _is_nonempty_string(evidence.get("evidence_id"))
        or not _is_nonempty_string(evidence.get("subject"))
        or not _is_nonempty_string(evidence.get("result"))
        or evidence.get("source") not in _EVIDENCE_SOURCES
        or (reject_model_inferred and evidence.get("source") == "MODEL_INFERRED")
        or isinstance(evidence.get("state_revision"), bool)
        or evidence.get("state_revision") != expected_revision
        or evidence.get("project_id") != control.get("project_id")
    ):
        return False
    try:
        from validate_project import validate_evidence_project_binding
    except ImportError:
        return False
    return not validate_evidence_project_binding(
        evidence, control, current_state_revision=expected_revision,
    )


def _load_recovery_work_unit(root: Path, control: Mapping, slot: Mapping, state: Mapping) -> Mapping | None:
    work_root = root / ".gpt-codex" / "work"
    if not work_root.is_dir():
        return None
    candidates: list[Mapping] = []
    try:
        paths = sorted(work_root.rglob("*.json"))
    except OSError:
        return None
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(record, Mapping) or record.get("project_id") != control.get("project_id"):
            return None
        if record.get("work_unit_id") == slot.get("work_unit_id"):
            candidates.append(record)
    if len(candidates) != 1:
        return None
    record = candidates[0]
    required = (
        "kernel_version", "schema_version", "work_unit_id", "project_id", "goal", "scope",
        "acceptance", "selected_extensions", "state", "basis_state_revision",
    )
    if (
        any(field not in record for field in required)
        or record.get("kernel_version") != "2.0.0"
        or record.get("schema_version") != 1
        or not _is_nonempty_string(record.get("goal"))
        or record.get("state") != "AUTHORIZED"
        or not isinstance(record.get("basis_state_revision"), int)
        or isinstance(record.get("basis_state_revision"), bool)
        or record.get("basis_state_revision") < 0
        or record.get("basis_state_revision") > state.get("revision")
    ):
        return None
    return record


def _valid_recovery_result(record: Mapping, control: Mapping, slot: Mapping, state: Mapping) -> bool:
    required = (
        "kernel_version", "schema_version", "project_id", "work_unit_id", "extension", "status",
        "evidence_refs", "completion_gate",
    )
    if (
        any(field not in record for field in required)
        or record.get("kernel_version") != "2.0.0"
        or record.get("schema_version") != 1
        or record.get("project_id") != control.get("project_id")
        or record.get("work_unit_id") != slot.get("work_unit_id")
        or not isinstance(record.get("extension"), Mapping)
        or not _is_nonempty_string(record.get("status"))
        or not isinstance(record.get("evidence_refs"), list)
        or not _is_nonempty_string(record.get("completion_gate"))
    ):
        return False
    try:
        from publication_contract import validate_result_authority
        from validate_project import validate_review_result
    except ImportError:
        return False
    if validate_result_authority(record):
        return False
    if record.get("result_message_type") == "REVIEW_RESULT":
        return (
            not validate_review_result(record)
            and record.get("response_to_instruction_id") == slot.get("review_request_id")
            and record.get("responder_role") == "CODEX_REVIEWER"
            and record.get("review_target_revision") == slot.get("current_head_sha")
            and record.get("state_revision") == state.get("revision")
        )
    return True


def _lifecycle_records_are_durable(
    root: Path, control: Mapping, slot: Mapping, state: Mapping,
) -> bool:
    references = {
        value
        for field in (
            "review_result_ref", "finding_ref", "remediation_authorization_ref",
            "reviewer_reassignment_ref",
        )
        if isinstance((value := slot.get(field)), str) and value
    }
    if not references:
        return True
    records: dict[str, list[Mapping]] = {reference: [] for reference in references}
    for directory in (root / ".gpt-codex" / "evidence",):
        if not directory.exists():
            continue
        if not directory.is_dir():
            return False
        try:
            paths = sorted(directory.rglob("*.json"))
        except OSError:
            return False
        for path in paths:
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return False
            if not isinstance(record, Mapping):
                return False
            for reference in references:
                if record.get("result_id") == reference or record.get("evidence_id") == reference:
                    records[reference].append(record)
    for reference, matches in records.items():
        if len(matches) != 1:
            return False
        record = matches[0]
        if reference == slot.get("review_result_ref"):
            if record.get("result_id") != reference or not _valid_recovery_result(record, control, slot, state):
                return False
        elif record.get("evidence_id") == reference:
            if not _valid_evidence_record(record, control, state.get("revision")):
                return False
        elif record.get("result_id") == reference:
            if not _valid_recovery_result(record, control, slot, state):
                return False
        else:
            return False
    return True


def _git_recovery_is_current(root: Path, slot: Mapping, state: Mapping) -> bool:
    def git(*args: str) -> tuple[int, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(root), *args], capture_output=True, text=True, check=False,
            )
        except OSError:
            return 127, ""
        return result.returncode, result.stdout.strip()

    code, inside = git("rev-parse", "--is-inside-work-tree")
    if code != 0 or inside != "true":
        return False
    code, head = git("rev-parse", "HEAD")
    if code != 0 or head != slot.get("current_head_sha"):
        return False
    code, branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    if code != 0 or branch != slot.get("branch"):
        return False
    code, top_level = git("rev-parse", "--show-toplevel")
    if code != 0 or Path(top_level).resolve() != root.resolve():
        return False
    worktree = slot.get("worktree")
    if not isinstance(worktree, str) or (root / worktree).resolve() != root.resolve():
        return False
    code, porcelain = git("status", "--porcelain")
    if code != 0 or porcelain:
        return False
    for revision in (slot.get("base_sha"), slot.get("last_accepted_sha")):
        if revision is None:
            continue
        if not isinstance(revision, str) or not _COMMIT_SHA.fullmatch(revision):
            return False
        code, _ = git("cat-file", "-e", f"{revision}^{{commit}}")
        if code != 0:
            return False
        code, _ = git("merge-base", "--is-ancestor", revision, head)
        if code != 0:
            return False
    continuity = state.get("continuity")
    return (
        isinstance(continuity, Mapping)
        and continuity.get("sync_status") == "SYNCED"
        and continuity.get("latest_synced_state_revision") == state.get("revision")
        and continuity.get("latest_verified_remote_sha") == slot.get("base_sha")
    )


def _execution_slot_recovery(
    root: Path,
    control: Mapping,
    state: Mapping,
    execution_slot_id: str,
    execution_slot_binding: object,
    authoritative_facts: object,
) -> dict[str, Any]:
    slots = state.get("active_execution_slots")
    if not isinstance(slots, list):
        return _recovery_result()
    matches = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("slot_id") == execution_slot_id]
    if len(matches) != 1:
        return _recovery_result()
    slot = matches[0]
    if isinstance(execution_slot_binding, Mapping):
        for field in _SLOT_BINDING_FIELDS:
            if field in execution_slot_binding and execution_slot_binding[field] != slot.get(field):
                return _recovery_result("EXECUTION_SLOT_MISMATCH")
    elif execution_slot_binding is not None:
        return _recovery_result()
    if (
        slot.get("project_context_id") != control.get("project_context_id")
        or slot.get("work_unit_id") != state.get("active_work_unit")
        or validate_execution_slots(state)
    ):
        return _recovery_result()
    if (
        slot.get("state_revision") != state.get("revision")
        or not _is_nonempty_string(slot.get("next_action"))
        or _load_recovery_work_unit(root, control, slot, state) is None
        or not _lifecycle_records_are_durable(root, control, slot, state)
        or not _git_recovery_is_current(root, slot, state)
    ):
        return _recovery_result()
    return {
        "status": "LATEST_SYNCED_REMOTE_STATE",
        "reconciliation_required": False,
        "execution_slot_id": execution_slot_id,
        "execution_slot": dict(slot),
        "next_action": slot["next_action"],
    }


def load_resume_checkpoint(gov: Path, control: dict[str, Any] | None = None) -> dict[str, Any] | None:
    checkpoint_path = Path(gov) / RESUME_RELATIVE_PATH
    if not checkpoint_path.exists():
        return None
    try:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("RESUME_CHECKPOINT_INVALID") from exc
    if not isinstance(checkpoint, dict):
        raise ValueError("RESUME_CHECKPOINT_INVALID")
    if checkpoint.get("schema_version") != 1:
        raise ValueError("RESUME_CHECKPOINT_SCHEMA_UNSUPPORTED")
    if checkpoint.get("authority") != "DERIVED_CACHE":
        raise ValueError("RESUME_CHECKPOINT_AUTHORITY_INVALID")
    if validate_evolution_metadata_authority(checkpoint.get("evolution_metadata")):
        raise ValueError("PROJECT_AUTHORITY_BOUNDARY_VIOLATION")
    if control is not None:
        try:
            identity = load_project_identity(control)
        except ValueError:
            identity = None
        if identity is not None:
            decision = evaluate_cross_project_resource_boundary(identity, checkpoint, resource_type="RESUME")
            if decision.decision != "ALLOW":
                raise ValueError(decision.reason)
    return checkpoint


def fingerprint_file(path: Path) -> str | None:
    source = Path(path)
    if not source.is_file():
        return None
    return "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()


def compare_context_sources(root: Path, checkpoint: dict[str, Any]) -> tuple[list[str], list[str]]:
    context_sources = checkpoint.get("context_sources", {})
    if not isinstance(context_sources, list):
        return [], []
    invalidated_context: list[str] = []
    required_reads: list[str] = []
    resolved_root = Path(root).resolve()
    for source in context_sources:
        if not isinstance(source, dict):
            continue
        relative_path = source.get("path")
        expected_fingerprint = source.get("fingerprint")
        if not isinstance(relative_path, str):
            continue
        supplied_path = Path(relative_path)
        if supplied_path.is_absolute() or ".." in supplied_path.parts:
            raise ValueError(f"RESUME_CONTEXT_SOURCE_PATH_INVALID:{relative_path}")
        candidate = (resolved_root / supplied_path).resolve()
        try:
            candidate.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(f"RESUME_CONTEXT_SOURCE_PATH_INVALID:{relative_path}") from exc
        current_fingerprint = fingerprint_file(candidate)
        if current_fingerprint is None:
            required_reads.append(relative_path)
        elif current_fingerprint != expected_fingerprint:
            invalidated_context.append(relative_path)
    return invalidated_context, required_reads


def load_continuity_resume(
    repo_root: Path,
    selected_repository_id: str,
    *,
    changed_paths: list[str] | None = None,
    candidate_module_ids: list[str] | None = None,
    observed_remote_head_sha: str | None = None,
    work_reachable: bool = True,
    attestation_is_management_only: bool = True,
    attestation_references_work: bool = True,
    generic_tree_matches: bool = True,
    execution_slot_id: str | None = None,
    execution_slot_binding: Mapping | None = None,
    authoritative_facts: Mapping | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    gov = root / ".gpt-codex"
    try:
        control = json.loads((gov / "CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((gov / "STATE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("CONTINUITY_MACHINE_STATE_INVALID") from exc
    github = control.get("github")
    if not isinstance(github, dict) or set(("repository_id", "repository_full_name", "default_branch")) - set(github):
        raise ValueError("GITHUB_REPOSITORY_UNBOUND")
    if str(github["repository_id"]) != str(selected_repository_id):
        raise ValueError("GITHUB_REPOSITORY_MISMATCH")
    continuity = state.get("continuity")
    if not isinstance(continuity, dict):
        raise ValueError("CONTINUITY_STATE_MISSING")
    if continuity.get("sync_status") != "SYNCED":
        return {
            "status": "LOCAL_UNSYNCED_STATE",
            "repository_id": str(selected_repository_id),
            "state": state,
            "continuity": continuity,
            **_non_optimization_resume_fields(),
        }
    baseline_sha = continuity.get("latest_verified_remote_sha")
    if observed_remote_head_sha is not None and not (
        baseline_sha
        and work_reachable
        and attestation_is_management_only
        and attestation_references_work
        and generic_tree_matches
    ):
        return {
            "status": "RECONCILIATION_REQUIRED",
            "repository_id": str(selected_repository_id),
            "verified_baseline_sha": baseline_sha,
            "current_attestation_head": observed_remote_head_sha,
            "reconciliation_required": True,
            "state": state,
            "continuity": continuity,
            **_non_optimization_resume_fields(),
        }

    if execution_slot_id is not None:
        return _execution_slot_recovery(
            root,
            control,
            state,
            execution_slot_id,
            execution_slot_binding,
            authoritative_facts,
        )

    project_map = load_project_map(root)
    if project_map is not None:
        validate_navigation_identity(project_map, control)

    checkpoint = load_resume_checkpoint(gov, control)
    if checkpoint is None:
        checkpoint_working_set: dict[str, Any] = {}
        invalidated_context: list[str] = []
        missing_context: list[str] = []
    else:
        validate_navigation_identity(checkpoint, control)
        checkpoint_working_set = checkpoint.get("working_set")
        if not isinstance(checkpoint_working_set, dict):
            checkpoint_working_set = {}
        detected_invalidated, missing_context = compare_context_sources(root, checkpoint)
        invalidated_context = [
            path
            for path in checkpoint_working_set.get("invalidated_context", [])
            if isinstance(path, str)
        ] + detected_invalidated

    hot_modules = [
        module_id
        for module_id in checkpoint_working_set.get("hot_modules", [])
        if isinstance(module_id, str)
    ]
    hot_files = [
        path
        for path in checkpoint_working_set.get("hot_files", [])
        if isinstance(path, str)
    ]
    next_required_reads = [
        path
        for path in checkpoint_working_set.get("next_required_reads", [])
        if isinstance(path, str)
    ]
    changed = [path for path in changed_paths or [] if isinstance(path, str)]
    candidate_module_inputs = [
        module_id
        for module_id in (candidate_module_ids if candidate_module_ids is not None else hot_modules)
        if isinstance(module_id, str)
    ]
    candidate_modules = []
    if project_map is not None:
        candidate_modules = list(dict.fromkeys(
            module_id
            for module_id in candidate_module_inputs
            if module_by_id(project_map, module_id) is not None
        ))

    stale_modules = []
    module_map_reads = []
    if project_map is not None:
        changed_modules = affected_modules(project_map, changed)
        stale_modules = sorted(set(candidate_modules).intersection(changed_modules))
        module_map_reads = module_map_read_paths(project_map, stale_modules)
    map_route = classify_map_route(
        candidate_modules,
        stale_modules,
        map_exists=project_map is not None,
    )
    normalised_hot_files = {normalise_relative_path(hot_file) for hot_file in hot_files}

    invalidating_reads = list(dict.fromkeys(
        invalidated_context
        + missing_context
        + [
            path
            for path in changed
            if normalise_relative_path(path) in normalised_hot_files
        ]
        + module_map_reads
    ))
    required_reads = list(dict.fromkeys(invalidating_reads + next_required_reads))
    invalidated_context = list(dict.fromkeys(invalidated_context))
    if checkpoint is None or project_map is None:
        resume_mode = "COLD_RESUME"
    elif invalidating_reads or map_route == "MAP_PARTIAL":
        resume_mode = "DELTA_RESUME"
    else:
        resume_mode = "FAST_RESUME"

    return {
        "status": "LATEST_SYNCED_REMOTE_STATE",
        "repository_id": str(selected_repository_id),
        "project_context_id": control.get("project_context_id"),
        "control": control,
        "state": state,
        "continuity": continuity,
        "active_work_unit": state.get("active_work_unit"),
        "remote_reverification_required": True,
        "verified_baseline_sha": baseline_sha,
        "current_attestation_head": observed_remote_head_sha,
        "reconciliation_required": False,
        "resume_mode": resume_mode,
        "map_route": map_route,
        "candidate_modules": candidate_modules,
        "stale_modules": stale_modules,
        "module_map_reads": module_map_reads,
        "required_reads": required_reads,
        "hot_modules": hot_modules,
        "hot_files": hot_files,
        "invalidated_context": invalidated_context,
    }
