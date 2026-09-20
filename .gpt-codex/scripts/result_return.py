from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from role_communication import validate_evolution_metadata_authority


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


def validate_result_evolution_metadata(metadata: Mapping[str, Any] | None) -> list[str]:
    return validate_evolution_metadata_authority(metadata)


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
    metadata_errors = validate_result_evolution_metadata(envelope.get("evolution_metadata"))
    if metadata_errors:
        raise ValueError(", ".join(metadata_errors))

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
        f"RESULT_ID: {_text(envelope.get('result_id'))}",
        f"DECISION: {_text(envelope.get('decision'))}",
        *_section("APPROVED_INSTRUCTION", envelope.get('approved_instruction')),
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


def render_compact_gpt_return(envelope: Mapping[str, Any]) -> str:
    """Render the derived durable-reference-first GPT return view."""

    if not envelope.get("return_to_gpt_required", False):
        return ""
    result_ref = envelope.get("result_id")
    if not isinstance(result_ref, str) or not result_ref.strip():
        raise ValueError("DURABLE_RESULT_REF_REQUIRED")

    locator = envelope.get("artifact_locator")
    locator_text = "NONE"
    if isinstance(locator, Mapping):
        repository, commit, path, blob = (locator.get(key) for key in ("repository", "commit_sha", "path", "blob_sha"))
        repository_lower = repository.lower() if isinstance(repository, str) else ""
        path_lower = path.lower() if isinstance(path, str) else ""
        if (
            isinstance(repository, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}/[A-Za-z0-9_.-]{1,80}", repository)
            and not any(marker in repository_lower for marker in ("ghp_", "token", "password", "secret"))
            and isinstance(commit, str) and re.fullmatch(r"[0-9a-fA-F]{40}", commit)
            and isinstance(blob, str) and re.fullmatch(r"[0-9a-fA-F]{40}", blob)
            and isinstance(path, str) and 0 < len(path) <= 240 and not re.match(r"^[A-Za-z]:", path)
            and not path.startswith(("/", "\\")) and ".." not in Path(path).parts
            and not any(char in path for char in "*?[]")
            and not any(ord(char) < 32 or ord(char) == 127 for char in path)
            and not any(marker in path_lower for marker in ("token", "secret", "credential", "password", "ghp_"))
        ):
            locator_text = f"repository={repository};commit_sha={commit};path={path};blob_sha={blob}"

    git = envelope.get("git")
    if not isinstance(git, Mapping):
        git = {}
    blockers = envelope.get("blockers")
    blocker_text = "NONE"
    if (
        isinstance(blockers, Sequence)
        and not isinstance(blockers, (str, bytes, bytearray))
        and blockers
    ):
        blocker_text = ", ".join(str(item) for item in blockers)

    return "\n".join(
        [
            f"RESULT: {_text(envelope.get('status'))}",
            f"WORK_UNIT: {_text(envelope.get('work_unit_id'))}",
            f"HEAD_SHA: {_text(git.get('implementation_sha', envelope.get('implementation_sha')))}",
            f"RESULT_REF: {result_ref}",
            f"STATE_REVISION: {_text(envelope.get('state_revision'))}",
            f"EVIDENCE_REFS: {_text(', '.join(str(item) for item in envelope.get('evidence_refs', [])) if isinstance(envelope.get('evidence_refs'), Sequence) and not isinstance(envelope.get('evidence_refs'), (str, bytes, bytearray)) else None)}",
            f"REVIEW_STATUS: {_text(envelope.get('review_status'))}",
            f"ARTIFACT_LOCATOR: {locator_text}",
            f"BLOCKERS: {blocker_text}",
            f"NEXT_ACTION: {_text(envelope.get('next_gpt_action'))}",
        ]
    )
