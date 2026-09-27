"""Thin optional presentation adapter for repository-native governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from continuity_resume import build_repository_handoff, load_continuity_resume
from instruction_envelope import (
    canonical_instruction_bytes,
    instruction_artifact_relative_path,
    resolve_durable_instruction,
    validate_durable_capability_request,
)
from result_return import render_compact_gpt_return
from framework_feedback import validate_framework_evolution_boundary

P2_CAPABILITIES = (
    "CONTEXT_ACCESS", "VALIDATION_ACCESS", "EVIDENCE_FEEDBACK_ROUTING",
    "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST",
)


def _reconcile() -> dict[str, Any]:
    return {"status": "RECONCILIATION_REQUIRED", "reconciliation_required": True}


def resolve_plugin_instruction(
    root: Path, locator: Mapping[str, Any], expected_repository: str, *,
    current_state_revision: int, approved_scope: set[str] | None = None,
    excluded_scope: set[str] | None = None,
) -> dict[str, Any]:
    return resolve_durable_instruction(
        root, locator, expected_repository,
        current_state_revision=current_state_revision,
        approved_scope=approved_scope, excluded_scope=excluded_scope,
    )


def build_plugin_resume(
    root: Path, selected_repository_id: str, execution_slot_id: str | None = None, *,
    target_work_unit_id: str | None = None,
    target_work_unit_ref: Mapping[str, str] | None = None,
    instruction_locator: Mapping[str, str] | None = None,
    expected_state_revision: int | None = None,
) -> dict[str, Any]:
    try:
        baseline = load_continuity_resume(root, selected_repository_id)
    except (ValueError, KeyError, TypeError):
        return _reconcile()
    if baseline.get("status") != "LATEST_SYNCED_REMOTE_STATE":
        return _reconcile()
    bindings = (target_work_unit_id, target_work_unit_ref,
                instruction_locator, expected_state_revision)
    if all(value is None for value in bindings):
        if execution_slot_id is not None:
            return _reconcile()
        control = baseline["control"]
        state = baseline["state"]
        return {
            "status": "PLUGIN_RESUME_READY", "reconciliation_required": False,
            "project_id": control.get("project_id"),
            "project_context_id": control.get("project_context_id"),
            "repository_id": str(selected_repository_id),
            "repository": control.get("github", {}).get("repository_full_name"),
            "state_revision": state.get("revision"), "state": state.get("state"),
            "active_work_unit": state.get("active_work_unit"),
            "verified_baseline_sha": baseline.get("verified_baseline_sha"),
            "next_action_hint": state.get("next_action"),
            "remote_reverification_required": True,
        }
    if any(value is None for value in bindings):
        return _reconcile()
    handoff = build_repository_handoff(
        root, selected_repository_id,
        target_work_unit_id=target_work_unit_id,
        target_work_unit_ref=target_work_unit_ref,
        instruction_locator=instruction_locator,
        expected_state_revision=expected_state_revision,
    )
    if handoff.get("status") != "HANDOFF_READY":
        return _reconcile()
    if execution_slot_id is not None and handoff.get("current_work", {}).get("execution_slot_id") != execution_slot_id:
        return _reconcile()
    return {
        "status": "PLUGIN_RESUME_READY", "reconciliation_required": False,
        "project_id": handoff["project"]["project_id"],
        "project_context_id": handoff["project"]["project_context_id"],
        "repository_id": handoff["project"]["repository_id"],
        "repository": handoff["project"]["repository"],
        "state_revision": handoff["state"]["revision"],
        "state": handoff["state"]["state"],
        "current_work": handoff["current_work"],
        "instruction_id": handoff["instruction_id"],
        "instruction_locator": handoff["instruction_locator"],
        "result_id": handoff["result_id"],
        "result_ref": handoff["result_ref"],
        "evidence_refs": handoff["evidence_refs"],
        "git": handoff["git"],
        "result_status": handoff["result_status"],
        "blockers": handoff["blockers"],
        "next_action_hint": handoff["next_action_hint"],
    }


def build_plugin_result_handoff(
    root: Path, selected_repository_id: str, *,
    target_work_unit_id: str | None = None,
    target_work_unit_ref: Mapping[str, str] | None = None,
    instruction_locator: Mapping[str, str] | None = None,
    expected_state_revision: int | None = None,
    execution_slot_id: str | None = None,
) -> dict[str, Any]:
    if any(value is None for value in (
        target_work_unit_id, target_work_unit_ref,
        instruction_locator, expected_state_revision,
    )):
        return _reconcile()
    resume = build_plugin_resume(
        root, selected_repository_id, execution_slot_id,
        target_work_unit_id=target_work_unit_id,
        target_work_unit_ref=target_work_unit_ref,
        instruction_locator=instruction_locator,
        expected_state_revision=expected_state_revision,
    )
    if resume.get("status") != "PLUGIN_RESUME_READY" or "result_id" not in resume:
        return _reconcile()
    compact = render_compact_gpt_return({
        "return_to_gpt_required": True,
        "status": resume["result_status"],
        "work_unit_id": resume["current_work"]["work_unit_id"],
        "git": resume["git"],
        "result_id": resume["result_id"],
        "state_revision": resume["state_revision"],
        "evidence_refs": resume["evidence_refs"],
        "next_gpt_action": resume["next_action_hint"],
        "blockers": resume["blockers"],
    })
    return {**resume, "status": "HANDOFF_READY", "compact_return": compact}


def request_validation_access(
    root: Path, selected_repository_id: str, *,
    instruction_locator: Mapping[str, Any], current_state_revision: int,
) -> dict[str, Any]:
    try:
        baseline = load_continuity_resume(root, selected_repository_id)
        repository = baseline["control"]["github"]["repository_full_name"]
    except (ValueError, KeyError, TypeError):
        return _reconcile()
    resolved = resolve_durable_instruction(
        root, instruction_locator, repository,
        current_state_revision=current_state_revision,
    )
    return {"status": "VALIDATION_RESULT", "validation_status": resolved["status"],
            "findings": [] if resolved["status"] == "INSTRUCTION_RESOLVED" else
                        ["RECONCILIATION_REQUIRED"]}


def validate_plugin_capability_request(
    root: Path, selected_repository_id: str, capability: str, *,
    instruction_locator: Mapping[str, Any] | None = None,
    current_state_revision: int | None = None,
    requested_action: str | None = None,
    review_request: Mapping[str, Any] | None = None,
    review_result: Mapping[str, Any] | None = None,
    repository_authority: Mapping[str, Any] | None = None,
) -> list[str]:
    if capability not in P2_CAPABILITIES:
        return ["UNSUPPORTED_CAPABILITY"]
    try:
        baseline = load_continuity_resume(root, selected_repository_id)
    except (ValueError, KeyError, TypeError):
        return ["RECONCILIATION_REQUIRED"]
    if baseline.get("status") != "LATEST_SYNCED_REMOTE_STATE":
        return ["RECONCILIATION_REQUIRED"]
    if capability != "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST":
        return []
    if (
        instruction_locator is None or type(current_state_revision) is not int
        or not isinstance(requested_action, str) or not requested_action
    ):
        return ["RECONCILIATION_REQUIRED"]
    return validate_durable_capability_request(
        root, instruction_locator, selected_repository_id,
        current_state_revision=current_state_revision,
        requested_action=requested_action,
        review_request=review_request, review_result=review_result,
        repository_authority=repository_authority,
    )


def route_plugin_feedback(
    root: Path, selected_repository_id: str, feedback: Mapping[str, Any], *,
    source_binding: Mapping[str, Any], instruction_locator: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        baseline = load_continuity_resume(root, selected_repository_id)
        control, state = baseline["control"], baseline["state"]
    except (ValueError, KeyError, TypeError):
        return _reconcile()
    if (
        baseline.get("status") != "LATEST_SYNCED_REMOTE_STATE"
        or not isinstance(source_binding, Mapping)
        or source_binding.get("project_id") != control.get("project_id")
        or source_binding.get("project_context_id") != control.get("project_context_id")
        or source_binding.get("state_revision") != state.get("revision")
        or source_binding.get("provenance") != "PROJECT_EVIDENCE"
        or validate_framework_evolution_boundary(control, feedback)
    ):
        return _reconcile()
    resolved = resolve_durable_instruction(
        root, instruction_locator, control["github"]["repository_full_name"],
        current_state_revision=state["revision"],
    )
    if (
        resolved.get("status") != "INSTRUCTION_RESOLVED"
        or source_binding.get("instruction_id") != resolved["instruction_id"]
        or source_binding.get("work_unit_id") != resolved["target_work_unit_id"]
    ):
        return _reconcile()
    if "result_id" in source_binding:
        handoff = build_repository_handoff(
            root, selected_repository_id,
            target_work_unit_id=resolved["target_work_unit_id"],
            target_work_unit_ref=resolved["target_work_unit_ref"],
            instruction_locator=instruction_locator,
            expected_state_revision=state["revision"],
        )
        if handoff.get("status") != "HANDOFF_READY" or handoff.get("result_id") != source_binding["result_id"]:
            return _reconcile()
    return {"status": "FEEDBACK_ROUTED", "destination": "P1_FRAMEWORK_FEEDBACK",
            "project_id": control["project_id"],
            "work_unit_id": resolved["target_work_unit_id"],
            "state_revision": state["revision"], "mutation": "NONE"}


def durable_authority_marker(resume: Mapping[str, Any]) -> tuple[str, int | None, str | None, str | None]:
    if resume.get("status") not in {"PLUGIN_RESUME_READY", "HANDOFF_READY"}:
        raise ValueError("VERIFIED_RESUME_REQUIRED")
    git = resume.get("git")
    sha = git.get("current_head_sha") if isinstance(git, Mapping) else resume.get("verified_baseline_sha")
    return (str(resume["repository_id"]), resume.get("state_revision"),
            sha, resume.get("result_ref"))


def detect_durable_authority_change(
    previous_marker: tuple[str, int | None, str | None, str | None],
    current_marker: tuple[str, int | None, str | None, str | None],
) -> bool:
    """True means only DURABLE_AUTHORITY_MAY_HAVE_CHANGED; resume again."""
    return previous_marker != current_marker
