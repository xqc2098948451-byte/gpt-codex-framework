from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from context_binding import evaluate_cross_project_resource_boundary, load_project_identity
from kernel_rules import validate_slot_state_revision
from publication_contract import validate_completion_evidence
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


def classify_execution_progress(
    state: Mapping,
    work_unit: Mapping,
    results: Sequence[Mapping],
    *,
    instruction_id: str,
    base_sha: str | None,
    safe_postcondition: bool,
    continuation_authorized: bool = True,
    side_effect_state: str = "SAFE_TO_REPEAT",
) -> str:
    """Pure A4 projection over durable facts; never persists a lifecycle state."""
    if not isinstance(state, Mapping) or not isinstance(work_unit, Mapping) or not isinstance(results, Sequence):
        return "RECONCILIATION_REQUIRED"
    revision = state.get("revision")
    if (state.get("project_id") != work_unit.get("project_id") or state.get("active_work_unit") != work_unit.get("work_unit_id") or work_unit.get("basis_state_revision") != revision or work_unit.get("state") != "AUTHORIZED"):
        return "RECONCILIATION_REQUIRED"
    if not results:
        return "NOT_STARTED"
    if len(results) != 1:
        return "RECONCILIATION_REQUIRED"
    result = results[0]
    if not isinstance(result, Mapping) or result.get("project_id") != state.get("project_id") or result.get("work_unit_id") != work_unit.get("work_unit_id") or result.get("state_revision") != revision or result.get("response_to_instruction_id") != instruction_id or (base_sha is not None and result.get("git_base_sha") != base_sha):
        return "RECONCILIATION_REQUIRED"
    evidence = result.get("completion_evidence")
    if not isinstance(evidence, Mapping):
        return "RECONCILIATION_REQUIRED"
    if result.get("status") == "FAIL":
        concrete_failure = any(
            isinstance(value, int) and not isinstance(value, bool) and value > threshold
            for value, threshold in (
                (evidence.get("exit_code"), 0),
                (evidence.get("failure_count"), 0),
                (evidence.get("error_count"), 0),
            )
        )
        return "FAILED" if concrete_failure else "RECONCILIATION_REQUIRED"
    if result.get("status") in {"PARTIAL", "INCOMPLETE"} and evidence.get("execution_state") == "INCOMPLETE":
        if side_effect_state == "AMBIGUOUS":
            return "RECONCILIATION_REQUIRED"
        return "READY_TO_CONTINUE" if continuation_authorized else "PARTIAL"
    if result.get("status") == "PASS" and safe_postcondition and not validate_completion_evidence(result):
        return "ALREADY_COMPLETE"
    return "RECONCILIATION_REQUIRED"


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
        from validate_project import validate_instruction_authority, validate_instruction_envelope_contract
    except ImportError:
        return ["RECONCILIATION_REQUIRED"]
    if (
        validate_instruction_envelope_contract(reassignment_instruction)
        or validate_instruction_authority(reassignment_instruction, expected_revision)
    ):
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
        from validate_project import validate_result_envelope_contract, validate_review_result
    except ImportError:
        return False
    if validate_result_envelope_contract(record) or validate_result_authority(record):
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


def _canonical_worktree_identity(root: Path) -> Path | None:
    """Return the nonpersistent physical Git worktree identity for a root candidate."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def _derive_pairwise_review_facts(
    root: Path, control: Mapping, state: Mapping, review_request: Mapping,
) -> dict[str, Any]:
    """Derive nonpersistent, root-verified executor/reviewer review facts."""
    slots = state.get("active_execution_slots") if isinstance(state, Mapping) else None
    if not isinstance(slots, list) or not isinstance(review_request, Mapping):
        return _recovery_result()
    context_id, work_unit_id = review_request.get("target_project_context_id"), review_request.get("target_work_unit")
    reviewers = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("role") == "CODEX_REVIEWER" and slot.get("project_context_id") == context_id and slot.get("work_unit_id") == work_unit_id and slot.get("review_request_id") == review_request.get("instruction_id")]
    implementers = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("role") == "CODEX_IMPLEMENTER" and slot.get("project_context_id") == context_id and slot.get("work_unit_id") == work_unit_id]
    if len(reviewers) != 1 or len(implementers) != 1:
        return _recovery_result()
    implementer, reviewer = implementers[0], reviewers[0]
    if implementer.get("slot_id") == reviewer.get("slot_id"):
        return _recovery_result()
    roots = []
    verified_slots = []
    for slot in (implementer, reviewer):
        worktree = slot.get("worktree")
        if not isinstance(worktree, str) or not worktree.strip():
            return _recovery_result()
        candidate = (Path(root) / worktree).resolve()
        normalized_slots = [
            dict(candidate_slot, worktree=".") if candidate_slot.get("slot_id") == slot.get("slot_id") else dict(candidate_slot)
            for candidate_slot in slots
        ]
        recovery_state = dict(state, active_execution_slots=normalized_slots)
        recovery = _execution_slot_recovery(
            candidate, control, recovery_state, slot.get("slot_id"), None, None,
        )
        if recovery.get("reconciliation_required") or not isinstance(recovery.get("execution_slot"), Mapping):
            return _recovery_result()
        identity = _canonical_worktree_identity(candidate)
        if identity is None:
            return _recovery_result()
        roots.append(identity)
        verified_slots.append(recovery["execution_slot"])
    implementer, reviewer = verified_slots
    implementation_sha, reviewer_head_sha = implementer.get("current_head_sha"), reviewer.get("current_head_sha")
    if roots[0] == roots[1] or implementation_sha != review_request.get("review_target_revision") or reviewer_head_sha != review_request.get("review_target_revision"):
        return _recovery_result()
    return {"status": "LATEST_SYNCED_REMOTE_STATE", "reconciliation_required": False,
            "implementer_slot_id": implementer.get("slot_id"), "reviewer_slot_id": reviewer.get("slot_id"),
            "canonical_implementer_worktree": str(roots[0]), "canonical_reviewer_worktree": str(roots[1]),
            "implementation_sha": implementation_sha, "reviewer_head_sha": reviewer_head_sha,
            "reviewer_tracked_clean": True}


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


def _git_object_path_exists(root: Path, sha: str, path: str) -> bool:
    if not isinstance(path, str) or not path.strip() or not isinstance(sha, str) or not _COMMIT_SHA.fullmatch(sha):
        return False
    try:
        result = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{sha}:{path}"],
                                capture_output=True, text=True, check=False)
    except OSError:
        return False
    return result.returncode == 0


def resolve_immutable_artifact(root: Path, locator: Mapping[str, Any], expected_repository: str | None = None) -> dict[str, Any]:
    """Resolve only an exact commit/path/blob tuple; mutable refs are not authority."""
    if not isinstance(locator, Mapping) or not isinstance(locator.get("repository"), str) or not locator["repository"].strip():
        return {"status": "FAIL", "reason": "ARTIFACT_LOCATOR_INVALID"}
    if not isinstance(expected_repository, str) or not expected_repository.strip():
        return {"status": "FAIL", "reason": "ARTIFACT_REPOSITORY_CONTEXT_REQUIRED"}
    if locator["repository"] != expected_repository:
        return {"status": "FAIL", "reason": "ARTIFACT_REPOSITORY_MISMATCH"}
    commit = locator.get("commit_sha")
    path = locator.get("path")
    blob = locator.get("blob_sha")
    if not isinstance(commit, str) or not _COMMIT_SHA.fullmatch(commit):
        return {"status": "NOT_AUTHORITY", "reason": "IMMUTABLE_COMMIT_REQUIRED"}
    if not isinstance(path, str) or not path.strip() or Path(path).is_absolute() or ".." in Path(path).parts:
        return {"status": "FAIL", "reason": "ARTIFACT_PATH_INVALID"}
    if not isinstance(blob, str) or not _COMMIT_SHA.fullmatch(blob) or not _git_object_path_exists(root, commit, path):
        return {"status": "FAIL", "reason": "ARTIFACT_OBJECT_UNAVAILABLE"}
    try:
        actual = subprocess.run(["git", "-C", str(root), "rev-parse", f"{commit}:{path}"], capture_output=True, text=True, check=False)
    except OSError:
        return {"status": "FAIL", "reason": "ARTIFACT_OBJECT_UNAVAILABLE"}
    if actual.returncode != 0 or actual.stdout.strip().lower() != blob.lower():
        return {"status": "FAIL", "reason": "ARTIFACT_BLOB_MISMATCH"}
    return {"status": "ALLOW", "locator": {"repository": locator["repository"], "commit_sha": commit, "path": path, "blob_sha": blob}}


def _artifact_locators(root: Path, repository: str, refs: Mapping[str, Any]) -> dict[str, Any] | None:
    locators: dict[str, Any] = {"design": None, "plan": None}
    for name, ref in refs.items():
        if ref is None:
            continue
        try:
            blob = subprocess.run(["git", "-C", str(root), "rev-parse", f"{ref['sha']}:{ref['path']}"], capture_output=True, text=True, check=False)
        except (OSError, KeyError):
            return None
        candidate = {"repository": repository, "commit_sha": ref["sha"], "path": ref["path"], "blob_sha": blob.stdout.strip()}
        resolved = resolve_immutable_artifact(root, candidate, repository)
        if resolved["status"] != "ALLOW":
            return None
        locators[name] = resolved["locator"]
    return locators


def _resolve_result_reference(root: Path, reference: object) -> tuple[Path, str] | None:
    if not isinstance(reference, str) or not reference.strip():
        return None
    evidence_root = root / ".gpt-codex" / "evidence" / "results"
    prefix = ".gpt-codex/evidence/results/"
    if reference.startswith(prefix):
        name = reference[len(prefix):]
        if not name or "/" in name or "\\" in name or not name.endswith(".json"):
            return None
        return evidence_root / name, name[:-5]
    if any(separator in reference for separator in ("/", "\\")) or reference.endswith(".json"):
        return None
    return evidence_root / f"{reference}.json", reference


def _validated_artifact_refs(root: Path, work_unit: Mapping) -> dict[str, Any] | None:
    refs = work_unit.get("artifact_refs")
    if refs is None:
        return {"design": None, "plan": None}
    if not isinstance(refs, Mapping) or set(refs) - {"design", "plan"}:
        return None
    result: dict[str, Any] = {"design": None, "plan": None}
    for name in ("design", "plan"):
        ref = refs.get(name)
        if ref is None:
            continue
        if not isinstance(ref, Mapping) or set(ref) != {"path", "sha"} or not _git_object_path_exists(root, ref.get("sha"), ref.get("path")):
            return None
        result[name] = {"path": ref["path"], "sha": ref["sha"]}
    return result


def _discover_pending_result(root: Path, control: Mapping, slot: Mapping, state: Mapping) -> tuple[Mapping | None, list[str]]:
    directory = root / ".gpt-codex" / "evidence" / "results"
    if not directory.exists():
        return None, []
    try:
        records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]
    except (OSError, json.JSONDecodeError):
        return None, ["RECONCILIATION_REQUIRED"]
    matches = [record for record in records if isinstance(record, Mapping) and _valid_recovery_result(record, control, slot, state)]
    if len(matches) > 1:
        return None, ["RECONCILIATION_REQUIRED"]
    return (matches[0] if matches else None), []


def _load_harness_strategy(root: Path) -> dict[str, str] | None:
    path = root / ".harness" / "REASONING.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    in_strategy = False
    result: dict[str, str] = {}
    for line in lines[:128]:
        if line == "## Strategy":
            in_strategy = True
            continue
        if in_strategy and line.startswith("## "):
            break
        if in_strategy and " = " in line:
            key, value = line.split(" = ", 1)
            if key.strip() and value.strip():
                result[key.strip()] = value.strip()
    return result or None


def build_project_handoff(root: Path, execution_slot_id: str | None = None) -> dict[str, Any]:
    try:
        control = json.loads((root / ".gpt-codex" / "CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((root / ".gpt-codex" / "STATE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _recovery_result()
    if not isinstance(control, Mapping):
        return _recovery_result()
    try:
        identity = load_project_identity(control, project_root=root)
    except (TypeError, ValueError, KeyError):
        return _recovery_result()
    slots = state.get("active_execution_slots")
    if not isinstance(slots, list):
        return _recovery_result()
    candidates = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("status") != "IDLE"
                  and (execution_slot_id is None or slot.get("slot_id") == execution_slot_id)]
    if execution_slot_id is not None and not candidates:
        return _recovery_result("EXECUTION_CONTEXT_MISMATCH")
    if len(candidates) != 1:
        return _recovery_result()
    slot = candidates[0]
    recovery = _execution_slot_recovery(root, control, state, slot.get("slot_id"), None, None)
    if recovery.get("reconciliation_required"):
        return _recovery_result("EXECUTION_CONTEXT_MISMATCH" if recovery.get("status") == "EXECUTION_SLOT_MISMATCH" else recovery.get("status"))
    work_unit = _load_recovery_work_unit(root, control, slot, state)
    refs = _validated_artifact_refs(root, work_unit) if work_unit else None
    locators = _artifact_locators(root, identity.repository_full_name, refs) if refs is not None else None
    pending, errors = _discover_pending_result(root, control, slot, state)
    latest_result_ref = (state.get("continuity") or {}).get("last_verified_result_ref")
    if latest_result_ref is not None:
        resolved_result = _resolve_result_reference(root, latest_result_ref)
        if resolved_result is None:
            return _recovery_result()
        try:
            latest_result = json.loads(resolved_result[0].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return _recovery_result()
        result_identity = latest_result.get("result_id") if isinstance(latest_result, Mapping) else None
        if not isinstance(result_identity, str) or not result_identity.strip():
            result_identity = latest_result_ref if isinstance(latest_result_ref, str) and latest_result_ref.startswith(".gpt-codex/evidence/results/") else None
        if not isinstance(latest_result, Mapping) or result_identity is None or not isinstance(latest_result.get("evidence_refs"), list):
            return _recovery_result()
        if not (isinstance(latest_result_ref, str) and latest_result_ref.startswith(".gpt-codex/evidence/results/")) and result_identity != resolved_result[1]:
            return _recovery_result()
        try:
            identities = []
            for candidate_path in (root / ".gpt-codex" / "evidence" / "results").glob("*.json"):
                candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
                if isinstance(candidate, Mapping) and isinstance(candidate.get("result_id"), str) and candidate["result_id"].strip():
                    identities.append(candidate["result_id"])
        except (OSError, json.JSONDecodeError):
            return _recovery_result()
        if isinstance(latest_result.get("result_id"), str) and identities.count(latest_result["result_id"]) != 1:
            return _recovery_result()
    if refs is None or locators is None or errors:
        return _recovery_result()
    return {"status": "HANDOFF_READY", "reconciliation_required": False,
            "project": {"project_id": identity.project_id, "project_context_id": identity.project_context_id,
                        "repository": identity.repository_full_name},
            "state": {"revision": state.get("revision"), "state": state.get("state")},
            "current_work": {"execution_slot_id": slot.get("slot_id"), "status": slot.get("status"), "work_unit_id": slot.get("work_unit_id")},
            "git": {"branch": slot.get("branch"), "base_sha": slot.get("base_sha"), "current_head_sha": slot.get("current_head_sha"),
                    "last_accepted_sha": slot.get("last_accepted_sha")},
            "accepted_artifacts": refs, "artifact_locator": locators, "strategy": _load_harness_strategy(root),
            "latest_result_ref": latest_result_ref,
            "pending_result_ref": pending.get("result_id") if pending else None, "blocker": slot.get("block_reason"),
            "next_action": slot.get("next_action")}


def build_repository_handoff(
    root: Path,
    selected_repository_id: str,
    *,
    target_work_unit_id: str,
    target_work_unit_ref: Mapping[str, str],
    instruction_locator: Mapping[str, str],
    expected_state_revision: int,
    observed_remote_head_sha: str | None = None,
) -> dict[str, Any]:
    """Derive an exact Result handoff for a Project without execution slots.

    This is a read-only Core operation.  Absence of any durable authority fact
    is reconciliation, never an invitation to select STATE's legacy work unit.
    """
    root = Path(root)
    if (
        not _is_nonempty_string(target_work_unit_id)
        or not isinstance(target_work_unit_ref, Mapping)
        or set(target_work_unit_ref) != {"path", "sha"}
        or not isinstance(instruction_locator, Mapping)
        or type(expected_state_revision) is not int
    ):
        return _recovery_result()

    def git(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", "-C", str(root), *args], capture_output=True,
                text=True, check=False,
            )
        except OSError:
            return None
        return completed.stdout.strip() if completed.returncode == 0 else None

    def committed_json(commit: str, path: str) -> Mapping | None:
        raw = git("show", f"{commit}:{path}")
        if raw is None:
            return None
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, Mapping) else None

    try:
        baseline = load_continuity_resume(root, selected_repository_id,
                                          observed_remote_head_sha=observed_remote_head_sha)
        control = baseline["control"]
        state = baseline["state"]
        github = control["github"]
    except (ValueError, KeyError, TypeError):
        return _recovery_result()
    if (
        baseline.get("status") != "LATEST_SYNCED_REMOTE_STATE"
        or state.get("revision") != expected_state_revision
        or state.get("project_id") != control.get("project_id")
        or str(github.get("repository_id")) != str(selected_repository_id)
        or not _is_nonempty_string(control.get("project_context_id"))
    ):
        return _recovery_result()
    slot_view = None
    if "active_execution_slots" in state:
        slot_view = build_project_handoff(root)
        if slot_view.get("status") != "HANDOFF_READY":
            return _recovery_result()
        if slot_view["current_work"].get("work_unit_id") != target_work_unit_id:
            return _recovery_result()

    repository = github.get("repository_full_name")
    origin = git("remote", "get-url", "origin")
    if origin is not None:
        origin = origin.replace("\\", "/")
    if not isinstance(repository, str) or not isinstance(origin, str) or not (
        origin.rstrip("/").removesuffix(".git").endswith("/" + repository)
        or origin.rstrip("/").removesuffix(".git").endswith(":" + repository)
    ):
        return _recovery_result()
    work_path, work_sha = target_work_unit_ref.get("path"), target_work_unit_ref.get("sha")
    expected_work_path = f".gpt-codex/work-units/{target_work_unit_id}.json"
    if work_path != expected_work_path or not _git_object_path_exists(root, work_sha, work_path):
        return _recovery_result()
    work_unit = committed_json(work_sha, work_path)
    if (
        work_unit is None
        or work_unit.get("work_unit_id") != target_work_unit_id
        or work_unit.get("project_id") != control.get("project_id")
        or work_unit.get("state") != "AUTHORIZED"
        or work_unit.get("basis_state_revision") != expected_state_revision
    ):
        return _recovery_result()
    refs = _validated_artifact_refs(root, work_unit)
    if refs is None or _artifact_locators(root, repository, refs) is None:
        return _recovery_result()
    if resolve_immutable_artifact(root, instruction_locator, repository).get("status") != "ALLOW":
        return _recovery_result()
    instruction = committed_json(instruction_locator["commit_sha"], instruction_locator["path"])
    if instruction is None or instruction_locator.get("path") != (
        f".gpt-codex/evidence/instructions/{instruction.get('instruction_id')}.json"
    ):
        return _recovery_result()
    if slot_view is not None:
        slot_id = slot_view["current_work"]["execution_slot_id"]
        slot = next((item for item in state["active_execution_slots"]
                     if item.get("slot_id") == slot_id), None)
        if (
            slot is None or slot.get("instruction_id") != instruction.get("instruction_id")
            or slot.get("state_revision") != expected_state_revision
        ):
            return _recovery_result()
    from validate_project import validate_instruction_authority, validate_instruction_envelope_contract
    allowed_scope = set((work_unit.get("scope") or {}).get("owned_paths") or [])
    excluded_scope = set((work_unit.get("scope") or {}).get("excluded_paths") or [])
    if (
        validate_instruction_envelope_contract(instruction)
        or validate_instruction_authority(instruction, expected_state_revision,
                                          allowed_scope, excluded_scope)
        or instruction.get("target_work_unit") != target_work_unit_id
        or instruction.get("target_work_unit_ref") != dict(target_work_unit_ref)
        or instruction.get("target_project_context_id") != control.get("project_context_id")
        or instruction.get("target_project_name") != control.get("project_name")
        or str(instruction.get("target_github_repository_id")) != str(selected_repository_id)
        or instruction.get("target_github_repository_full_name") != repository
        or instruction.get("expected_state_revision") != expected_state_revision
        or not set(instruction.get("authorized_actions") or []).issubset(
            set((work_unit.get("permissions") or {}).get("authorized_actions") or []))
    ):
        return _recovery_result()

    head = git("rev-parse", "HEAD")
    remote = git("ls-remote", "origin", f"refs/heads/{github.get('default_branch')}")
    remote_head = remote.split()[0] if remote else None
    if (
        not head or not _COMMIT_SHA.fullmatch(head)
        or remote_head != head
        or (observed_remote_head_sha is not None and observed_remote_head_sha != head)
    ):
        return _recovery_result()
    verified_sha = baseline.get("verified_baseline_sha")
    if (
        not isinstance(verified_sha, str)
        or not _COMMIT_SHA.fullmatch(verified_sha)
        or git("cat-file", "-t", verified_sha) != "commit"
        or git("merge-base", verified_sha, head) != verified_sha
    ):
        return _recovery_result()

    result_dir = root / ".gpt-codex" / "evidence" / "results"
    try:
        paths = sorted(result_dir.glob("*.json"))
    except OSError:
        return _recovery_result()
    matches: list[tuple[str, Mapping]] = []
    seen_ids: set[str] = set()
    for path in paths:
        relative = path.relative_to(root).as_posix()
        record = committed_json(head, relative)
        if record is None or git("status", "--porcelain", "--", relative) != "":
            return _recovery_result()
        result_id = record.get("result_id")
        if not _is_nonempty_string(result_id) or result_id in seen_ids:
            return _recovery_result()
        seen_ids.add(result_id)
        if record.get("response_to_instruction_id") == instruction.get("instruction_id"):
            matches.append((relative, record))
    if len(matches) != 1:
        return _recovery_result()
    result_path, result = matches[0]
    from publication_contract import validate_result_authority
    from validate_project import validate_result_envelope_contract
    result_sha = (result.get("git") or {}).get("implementation_sha") or result.get("implementation_sha")
    if (
        validate_result_envelope_contract(result) or validate_result_authority(result)
        or result.get("project_id") != control.get("project_id")
        or result.get("source_project_context_id") != control.get("project_context_id")
        or str(result.get("source_github_repository_id")) != str(selected_repository_id)
        or result.get("source_github_repository_full_name") != repository
        or result.get("work_unit_id") != target_work_unit_id
        or result.get("state_revision") != expected_state_revision
        or not isinstance(result_sha, str) or not _COMMIT_SHA.fullmatch(result_sha)
        or git("cat-file", "-t", result_sha) != "commit"
        or git("merge-base", result_sha, head) != result_sha
    ):
        return _recovery_result()
    evidence_refs = result.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        return _recovery_result()
    for reference in evidence_refs:
        if (
            not isinstance(reference, str)
            or not reference.startswith(".gpt-codex/evidence/")
            or ".." in Path(reference).parts
            or not reference.endswith(".json")
            or git("cat-file", "-e", f"{head}:{reference}") is None
        ):
            return _recovery_result()
    return {
        "status": "HANDOFF_READY", "reconciliation_required": False,
        "project": {"project_id": control["project_id"],
                    "project_context_id": control["project_context_id"],
                    "repository": repository, "repository_id": str(selected_repository_id)},
        "state": {"revision": expected_state_revision, "state": state.get("state")},
        "current_work": slot_view["current_work"] if slot_view is not None else
                        {"work_unit_id": target_work_unit_id, "status": work_unit.get("state")},
        "instruction_id": instruction["instruction_id"],
        "instruction_locator": dict(instruction_locator),
        "result_id": result["result_id"], "result_ref": result_path,
        "evidence_refs": evidence_refs,
        "git": {"implementation_sha": result_sha, "current_head_sha": head},
        "result_status": result["status"],
        "next_action_hint": result.get("next_gpt_action"),
        "blockers": result.get("blockers") or [],
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
