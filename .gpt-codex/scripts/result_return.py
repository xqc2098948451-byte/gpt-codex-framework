from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


_REQUIRED_SECTIONS = (
    "WORK_UNIT:",
    "STATE_REVISION:",
    "EXECUTION:",
    "CHANGED:",
    "VERIFY:",
    "EVIDENCE:",
    "DEVIATIONS:",
    "BLOCKERS:",
    "NEXT_GPT_ACTION:",
)


def required_return_sections() -> tuple[str, ...]:
    return _REQUIRED_SECTIONS


def _text(value: Any) -> str:
    if value is None or value == "" or value == [] or value == {}:
        return "NONE"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    return str(value)


def _items(value: Any) -> list[str]:
    if value is None or value == "" or value == [] or value == {}:
        return ["NONE"]
    if isinstance(value, Mapping):
        return [f"{key}: {_text(value[key])}" for key in sorted(value)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_text(item) for item in value] or ["NONE"]
    return [_text(value)]


def _section(label: str, value: Any) -> list[str]:
    if value is None or value == "" or value == [] or value == {}:
        return [f"{label}: NONE"]
    return [f"{label}:", *[f"- {item}" for item in _items(value)]]


def render_gpt_return(envelope: Mapping[str, Any]) -> str:
    """Render the copyable GPT return view from one machine Result Envelope."""

    if not envelope.get("return_to_gpt_required", False):
        return ""

    git = envelope.get("git") or {}
    if not isinstance(git, Mapping):
        git = {}

    lines = [
        f"RESULT: {_text(envelope.get('status'))}",
        f"SOURCE_PROJECT_CONTEXT_ID: {_text(envelope.get('source_project_context_id'))}",
        f"SOURCE_PROJECT_NAME: {_text(envelope.get('source_project_name'))}",
        f"FRAMEWORK_VERSION: {_text(envelope.get('framework_version'))}",
        f"INSTRUCTION_TYPE: {_text(envelope.get('instruction_type'))}",
        f"RESULT_MESSAGE_TYPE: {_text(envelope.get('result_message_type'))}",
        f"RESPONSE_TO_INSTRUCTION_ID: {_text(envelope.get('response_to_instruction_id'))}",
        f"RESPONDER_ROLE: {_text(envelope.get('responder_role'))}",
        f"RETURN_ROLE: {_text(envelope.get('return_role'))}",
        f"REVIEW_TARGET_REVISION: {_text(envelope.get('review_target_revision'))}",
        *_section("FINDING_IDS", envelope.get("finding_ids")),
        f"FIX_ROUND: {_text(envelope.get('fix_round'))}",
        f"REMEDIATION_DECISION_REF: {_text(envelope.get('remediation_decision_ref'))}",
        f"PROTOCOL_ERROR: {_text(envelope.get('protocol_error'))}",
        *_section("ROLE_OBSERVATION", envelope.get("role_observation")),
        f"ARTIFACT_STAGE: {_text(envelope.get('artifact_stage'))}",
        f"ARTIFACT_PATH: {_text(envelope.get('artifact_path'))}",
        f"SOURCE_GITHUB_REPOSITORY_ID: {_text(envelope.get('source_github_repository_id'))}",
        f"SOURCE_GITHUB_REPOSITORY_FULL_NAME: {_text(envelope.get('source_github_repository_full_name'))}",
        f"CURRENT_REMOTE_REF: {_text(envelope.get('current_remote_ref'))}",
        f"LOCAL_HEAD_SHA: {_text(envelope.get('local_head_sha'))}",
        f"REMOTE_HEAD_SHA: {_text(envelope.get('remote_head_sha'))}",
        f"SYNC_STATUS: {_text(envelope.get('sync_status'))}",
        f"PUSH_STATUS: {_text(envelope.get('push_status'))}",
        f"REMOTE_VERIFICATION: {_text(envelope.get('remote_verification'))}",
        f"PUBLICATION_AUTHORITY: {_text(envelope.get('publication_authority'))}",
        f"WORK_UNIT: {_text(envelope.get('work_unit_id'))}",
        f"STATE_REVISION: {_text(envelope.get('state_revision'))}",
        f"EXECUTION: {_text(envelope.get('execution'))}",
        *_section("CHANGED", envelope.get("changed")),
        *_section("VERIFY", envelope.get("verify")),
        *_section("EVIDENCE", envelope.get("evidence_refs")),
        *_section("DEVIATIONS", envelope.get("deviations")),
        *_section("BLOCKERS", envelope.get("blockers")),
        f"GIT_BASE_SHA: {_text(git.get('base_sha', envelope.get('git_base_sha')))}",
        f"IMPLEMENTATION_SHA: {_text(git.get('implementation_sha', envelope.get('implementation_sha')))}",
        f"PARALLEL_BATCH: {_text(envelope.get('parallel_batch'))}",
        f"EXECUTION_UNIT: {_text(envelope.get('execution_unit'))}",
        *_section("OBSERVABILITY_FITNESS", envelope.get("observability_fitness")),
        *_section("EXTENSION_EVIDENCE", envelope.get("extension_evidence_refs")),
        f"NEXT_GPT_ACTION: {_text(envelope.get('next_gpt_action'))}",
    ]
    return "\n".join(lines)
