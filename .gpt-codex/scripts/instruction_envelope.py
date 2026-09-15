from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
import re
import sys
from typing import Any
from uuid import uuid4


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from role_communication import (  # noqa: E402
    ARTIFACT_STAGES,
    INSTRUCTION_TYPES,
    ROLES,
    resolve_legacy_codex_route,
    validate_action_authority,
    validate_evolution_metadata_authority,
    validate_executor_role,
    validate_instruction_type,
)


LEGACY_INSTRUCTION_ALIASES = frozenset({"WORK_UNIT", "IMPLEMENTATION"})
LEGACY_DEFAULTS = {
    "issuer_role": "GPT_ORCHESTRATOR",
    "executor_role": "CODEX_IMPLEMENTER",
    "return_role": "GPT_ORCHESTRATOR",
}
COMPLETION_GATES = frozenset({"NONE", "GPT_DECISION", "USER_APPROVAL"})


def validate_instruction_evolution_metadata(metadata: Mapping[str, Any] | None) -> list[str]:
    return validate_evolution_metadata_authority(metadata)
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _value(value: Any) -> str:
    if value is None or value == "":
        return "NONE"
    return str(value)


def build_instruction_envelope(
    instruction_type: str,
    target_project_context_id: str | None,
    target_project_name: str | None,
    expected_state_revision: int | None,
    framework_version: str,
    target_work_unit: str | None = None,
    expected_base_sha: str | None = None,
    permission_scope: str | None = None,
    bootstrap_target_project_id: str | None = None,
    bootstrap_challenge_id: str | None = None,
    bootstrap_phase: str | None = None,
    instruction_id: str | None = None,
    target_github_repository_id: str | None = None,
    target_github_repository_full_name: str | None = None,
    expected_remote_ref: str | None = None,
    expected_remote_head_sha: str | None = None,
    expected_remote_name: str | None = None,
    *,
    issuer_role: str | None = None,
    executor_role: str | list[str] | None = None,
    return_role: str | None = None,
    authorized_actions: list[str] | None = None,
    forbidden_actions: list[str] | None = None,
    evidence_requirements: Mapping[str, Any] | None = None,
    completion_gate: str | None = None,
    in_response_to_instruction_id: str | None = None,
    in_response_to_result_id: str | None = None,
    review_target_revision: str | None = None,
    finding_ids: list[str] | None = None,
    fix_round: int | None = None,
    artifact_stage: str | None = None,
    legacy_route_marker: str | None = None,
    legacy_route_context: str | list[str] | None = None,
    evolution_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    type_errors = validate_instruction_type(instruction_type)
    if type_errors:
        raise ValueError(", ".join(type_errors))
    metadata_errors = validate_instruction_evolution_metadata(evolution_metadata)
    if metadata_errors:
        raise ValueError(", ".join(metadata_errors))
    if instruction_type != "PROJECT_CONTEXT_BOOTSTRAP" and not target_project_context_id:
        raise ValueError("normal instructions require target_project_context_id")
    if bootstrap_phase in {"INITIAL_READ_ONLY", "CHALLENGE_BOUND"} and instruction_type != "PROJECT_CONTEXT_BOOTSTRAP":
        raise ValueError("bootstrap_phase is only valid for PROJECT_CONTEXT_BOOTSTRAP")
    if bootstrap_phase == "CHALLENGE_BOUND" and not bootstrap_challenge_id:
        raise ValueError("challenge-bound bootstrap requires bootstrap_challenge_id")
    if instruction_type != "PROJECT_CONTEXT_BOOTSTRAP" and target_github_repository_id is None:
        # v2.1 instructions remain valid; continuity callers must opt into the
        # repository binding explicitly through this field.
        pass
    legacy_executor = None
    if legacy_route_marker is not None or legacy_route_context is not None:
        legacy_executor = resolve_legacy_codex_route(legacy_route_marker, legacy_route_context)
        if legacy_executor == "CODEX_REVIEWER" and instruction_type != "REVIEW_REQUEST":
            raise ValueError("LEGACY_ROUTE_CONTEXT_CONFLICT")
        if legacy_executor == "CODEX_IMPLEMENTER" and instruction_type == "REVIEW_REQUEST":
            raise ValueError("LEGACY_ROUTE_CONTEXT_CONFLICT")
        if executor_role is not None and executor_role != legacy_executor:
            raise ValueError("LEGACY_ROUTE_EXECUTOR_CONFLICT")
        executor_role = legacy_executor

    role_defaults = LEGACY_DEFAULTS if instruction_type in LEGACY_INSTRUCTION_ALIASES or instruction_type == "PROJECT_CONTEXT_BOOTSTRAP" else {}
    issuer_role = issuer_role if issuer_role is not None else role_defaults.get("issuer_role")
    executor_role = executor_role if executor_role is not None else role_defaults.get("executor_role")
    return_role = return_role if return_role is not None else role_defaults.get("return_role")
    executor_errors = validate_executor_role(executor_role)
    if executor_errors:
        raise ValueError(", ".join(executor_errors))
    if issuer_role is None and instruction_type not in LEGACY_INSTRUCTION_ALIASES and instruction_type != "PROJECT_CONTEXT_BOOTSTRAP":
        raise ValueError("ISSUER_ROLE_REQUIRED")
    if return_role is None and instruction_type not in LEGACY_INSTRUCTION_ALIASES and instruction_type != "PROJECT_CONTEXT_BOOTSTRAP":
        raise ValueError("RETURN_ROLE_REQUIRED")
    if issuer_role is not None and (not isinstance(issuer_role, str) or issuer_role not in ROLES):
        raise ValueError("UNKNOWN_ISSUER_ROLE")
    if return_role is not None and (not isinstance(return_role, str) or return_role not in ROLES):
        raise ValueError("UNKNOWN_RETURN_ROLE")
    authorized_actions = _normalize_action_collection(authorized_actions)
    forbidden_actions = _normalize_action_collection(forbidden_actions)
    if authorized_actions is not None or forbidden_actions is not None:
        action_errors = validate_action_authority(
            executor_role,
            authorized_actions,
            forbidden_actions,
        )
        if action_errors:
            raise ValueError(", ".join(action_errors))
    if evidence_requirements is not None:
        _validate_evidence_requirements(evidence_requirements)
    if completion_gate is not None and completion_gate not in COMPLETION_GATES:
        raise ValueError("INVALID_COMPLETION_GATE")
    for field_name, value in (
        ("in_response_to_instruction_id", in_response_to_instruction_id),
        ("in_response_to_result_id", in_response_to_result_id),
    ):
        if value is not None and (not isinstance(value, str) or not _UUID_RE.fullmatch(value)):
            raise ValueError(f"INVALID_CORRELATION:{field_name}")
    if review_target_revision is not None and (
        not isinstance(review_target_revision, str) or not _SHA_RE.fullmatch(review_target_revision)
    ):
        raise ValueError("INVALID_REVIEW_TARGET_REVISION")
    if finding_ids is not None:
        if not isinstance(finding_ids, list) or not all(isinstance(item, str) and item.strip() for item in finding_ids):
            raise ValueError("INVALID_FINDING_IDS")
        if len(finding_ids) > 50:
            raise ValueError("FINDING_IDS_LIMIT_EXCEEDED")
    if fix_round is not None and (not isinstance(fix_round, int) or isinstance(fix_round, bool) or fix_round < 0):
        raise ValueError("INVALID_FIX_ROUND")
    if artifact_stage is not None and artifact_stage not in ARTIFACT_STAGES:
        raise ValueError("INVALID_ARTIFACT_STAGE")
    envelope: dict[str, Any] = {
        "instruction_id": instruction_id or str(uuid4()),
        "instruction_type": instruction_type,
        "target_project_context_id": target_project_context_id,
        "target_project_name": target_project_name,
        "expected_state_revision": expected_state_revision,
        "framework_version": framework_version,
        "issuer_role": issuer_role,
        "executor_role": executor_role,
        "return_role": return_role,
    }
    optional = {
        "target_work_unit": target_work_unit,
        "expected_base_sha": expected_base_sha,
        "permission_scope": permission_scope,
        "bootstrap_target_project_id": bootstrap_target_project_id,
        "bootstrap_challenge_id": bootstrap_challenge_id,
        "bootstrap_phase": bootstrap_phase,
        "target_github_repository_id": target_github_repository_id,
        "target_github_repository_full_name": target_github_repository_full_name,
        "expected_remote_ref": expected_remote_ref,
        "expected_remote_head_sha": expected_remote_head_sha,
        "expected_remote_name": expected_remote_name,
        "authorized_actions": authorized_actions,
        "forbidden_actions": forbidden_actions,
        "evidence_requirements": evidence_requirements,
        "completion_gate": completion_gate,
        "in_response_to_instruction_id": in_response_to_instruction_id,
        "in_response_to_result_id": in_response_to_result_id,
        "review_target_revision": review_target_revision,
        "finding_ids": finding_ids,
        "fix_round": fix_round,
        "artifact_stage": artifact_stage,
        "evolution_metadata": dict(evolution_metadata) if evolution_metadata is not None else None,
    }
    envelope.update({key: value for key, value in optional.items() if value is not None})
    return envelope


def _normalize_action_collection(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise ValueError("INVALID_ACTIONS_SHAPE")
    if not all(isinstance(action, str) for action in value):
        raise ValueError("INVALID_ACTION")
    return list(value)


def _validate_evidence_requirements(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("INVALID_EVIDENCE_REQUIREMENTS")
    allowed_keys = {
        "files_read", "files_changed", "tests", "validation", "findings", "revision", "result_references"
    }
    if any(key not in allowed_keys for key in value):
        raise ValueError("INVALID_EVIDENCE_REQUIREMENTS")
    for key, item in value.items():
        if key == "revision":
            if not isinstance(item, bool):
                raise ValueError("INVALID_EVIDENCE_REQUIREMENTS")
        elif not isinstance(item, list) or len(item) > 100 or not all(isinstance(entry, str) and entry.strip() for entry in item):
            raise ValueError("INVALID_EVIDENCE_REQUIREMENTS")


_MINIMAL_TASK_REFS = ("BASE_SHA", "PLAN_REF", "STATE_REF", "OPEN_FINDINGS", "STRATEGY_PROFILE")

def render_minimal_codex_task(envelope: Mapping[str, Any], *, goal: str, scope: list[str], constraints: list[str], done: list[str], refs: Mapping[str, str] | None = None, transfer: Mapping[str, Any] | None = None) -> str:
    def items(value: object) -> list[str]:
        if not isinstance(value, list) or not value or len(value) > 100 or not all(isinstance(x, str) and x.strip() for x in value):
            raise ValueError("MINIMAL_TASK_INVALID")
        return value
    if not isinstance(goal, str) or not goal.strip(): raise ValueError("MINIMAL_TASK_INVALID")
    scope, constraints, done = items(scope), items(constraints), items(done)
    if refs is not None and (not isinstance(refs, Mapping) or set(refs) - set(_MINIMAL_TASK_REFS) or not all(isinstance(v, str) and v.strip() for v in refs.values())): raise ValueError("MINIMAL_TASK_INVALID")
    if transfer is None: transfer={"upload_required":False,"source":"Git SHA:path"}
    if not isinstance(transfer, Mapping) or not isinstance(transfer.get("upload_required"), bool): raise ValueError("MINIMAL_TASK_INVALID")
    upload=transfer["upload_required"]
    allowed={"upload_required","source","items"} if upload else {"upload_required","source"}
    if set(transfer)!=allowed or not isinstance(transfer.get("source"),str) or not transfer["source"].strip(): raise ValueError("MINIMAL_TASK_INVALID")
    if not upload and transfer["source"] != "Git SHA:path": raise ValueError("MINIMAL_TASK_INVALID")
    upload_items=transfer.get("items",[])
    if upload: upload_items=items(upload_items)
    lines=[f"是否需要你上传内容：{'需要' if upload else '不需要'}",f"需要上传的内容：{'、'.join(upload_items) if upload else '无'}",f"读取来源：{transfer['source']}", "",f"INSTRUCTION_ID: {_value(envelope.get('instruction_id'))}",f"INSTRUCTION_TYPE: {_value(envelope.get('instruction_type'))}",f"TARGET_WORK_UNIT: {_value(envelope.get('target_work_unit'))}"]
    display=dict(refs or {})
    if envelope.get("expected_base_sha") is not None: display["BASE_SHA"]=str(envelope["expected_base_sha"])
    lines += [f"{key}: {display[key]}" for key in _MINIMAL_TASK_REFS if key in display]
    for label, value in (("GOAL",[goal]),("SCOPE",scope),("CONSTRAINTS",constraints),("DONE",done)):
        lines += ["",f"{label}:",*[f"- {item}" for item in value]]
    return "\n".join(lines)

def render_codex_instruction(
    envelope: Mapping[str, Any],
    task_body: str,
    routing: Mapping[str, str],
) -> str:
    metadata_errors = validate_instruction_evolution_metadata(envelope.get("evolution_metadata"))
    if metadata_errors:
        raise ValueError(", ".join(metadata_errors))
    lines = [
        f"INSTRUCTION_ID: {_value(envelope.get('instruction_id'))}",
        f"INSTRUCTION_TYPE: {_value(envelope.get('instruction_type'))}",
        f"TARGET_PROJECT_CONTEXT_ID: {_value(envelope.get('target_project_context_id'))}",
        f"TARGET_PROJECT_NAME: {_value(envelope.get('target_project_name'))}",
        f"EXPECTED_STATE_REVISION: {_value(envelope.get('expected_state_revision'))}",
        f"FRAMEWORK_VERSION: {_value(envelope.get('framework_version'))}",
    ]
    for key, label in (
        ("target_work_unit", "TARGET_WORK_UNIT"),
        ("expected_base_sha", "EXPECTED_BASE_SHA"),
        ("permission_scope", "PERMISSION_SCOPE"),
        ("bootstrap_target_project_id", "BOOTSTRAP_TARGET_PROJECT_ID"),
        ("bootstrap_challenge_id", "BOOTSTRAP_CHALLENGE_ID"),
        ("bootstrap_phase", "BOOTSTRAP_PHASE"),
        ("target_github_repository_id", "TARGET_GITHUB_REPOSITORY_ID"),
        ("target_github_repository_full_name", "TARGET_GITHUB_REPOSITORY_FULL_NAME"),
        ("expected_remote_ref", "EXPECTED_REMOTE_REF"),
        ("expected_remote_head_sha", "EXPECTED_REMOTE_HEAD_SHA"),
        ("expected_remote_name", "EXPECTED_REMOTE_NAME"),
        ("issuer_role", "ISSUER_ROLE"),
        ("executor_role", "EXECUTOR_ROLE"),
        ("return_role", "RETURN_ROLE"),
        ("authorized_actions", "AUTHORIZED_ACTIONS"),
        ("forbidden_actions", "FORBIDDEN_ACTIONS"),
        ("evidence_requirements", "EVIDENCE_REQUIREMENTS"),
        ("completion_gate", "COMPLETION_GATE"),
        ("in_response_to_instruction_id", "IN_RESPONSE_TO_INSTRUCTION_ID"),
        ("in_response_to_result_id", "IN_RESPONSE_TO_RESULT_ID"),
        ("review_target_revision", "REVIEW_TARGET_REVISION"),
        ("finding_ids", "FINDING_IDS"),
        ("fix_round", "FIX_ROUND"),
        ("artifact_stage", "ARTIFACT_STAGE"),
    ):
        if key in envelope:
            value = envelope.get(key)
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            elif isinstance(value, Mapping):
                value = json.dumps(value, ensure_ascii=False, sort_keys=True)
            lines.append(f"{label}: {_value(value)}")
    if envelope.get("instruction_type") == "PROJECT_CONTEXT_BOOTSTRAP" and envelope.get("bootstrap_phase") == "CHALLENGE_BOUND" and task_body.strip():
        raise ValueError("challenge-bound bootstrap cannot contain a business task")
    lines.extend(
        [
            f"【执行策略】{_value(routing.get('execution_strategy'))}",
            f"【完成后是否需要批准】{_value(routing.get('approval'))}",
            "",
            task_body,
        ]
    )
    return "\n".join(lines)
