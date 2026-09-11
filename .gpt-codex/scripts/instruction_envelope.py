from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4


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
) -> dict[str, Any]:
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
    envelope: dict[str, Any] = {
        "instruction_id": instruction_id or str(uuid4()),
        "instruction_type": instruction_type,
        "target_project_context_id": target_project_context_id,
        "target_project_name": target_project_name,
        "expected_state_revision": expected_state_revision,
        "framework_version": framework_version,
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
    }
    envelope.update({key: value for key, value in optional.items() if value is not None})
    return envelope


def render_codex_instruction(
    envelope: Mapping[str, Any],
    task_body: str,
    routing: Mapping[str, str],
) -> str:
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
    ):
        if key in envelope:
            lines.append(f"{label}: {_value(envelope.get(key))}")
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
