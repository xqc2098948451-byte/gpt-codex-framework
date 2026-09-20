"""Shared role and message-side rules for the role communication protocol."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re


ROLES = frozenset(
    {
        "GPT_ORCHESTRATOR",
        "GPT_REVIEWER",
        "CODEX_IMPLEMENTER",
        "CODEX_REVIEWER",
        "USER_APPROVER",
        "USER_LOCAL",
        "INFORMATION_ONLY",
    }
)
_EVOLUTION_METADATA_CLASSIFICATIONS = frozenset({
    "READ_ONLY_EVOLUTION_SOURCE", "FRAMEWORK_MANAGEMENT_METADATA", "DERIVED_OBSERVATION_ONLY",
})
_EVOLUTION_AUTHORITY_FIELDS = frozenset({
    "authorized_actions", "target_work_unit", "state_revision", "command", "retry", "queue",
    "project_mutation", "role_authority", "schedule_execution", "force_adoption",
})
_APPROVED_INSTRUCTION_KEYS = frozenset({
    "instruction_id", "expected_state_revision", "expected_base_sha", "scope_paths",
    "target_project_context_id", "target_project_name", "target_github_repository_id",
    "target_github_repository_full_name", "target_work_unit_ref", "issuer_role",
    "executor_role", "authorized_actions",
})
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def validate_evolution_metadata_authority(metadata: Mapping[str, object] | None) -> list[str]:
    """Keep evolution metadata descriptive; Role Protocol remains the authority source."""
    if not isinstance(metadata, Mapping):
        return []
    if (
        metadata.get("classification") in _EVOLUTION_METADATA_CLASSIFICATIONS
        and _EVOLUTION_AUTHORITY_FIELDS.intersection(metadata)
    ):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    return []

INSTRUCTION_TYPES = frozenset(
    {
        "EXECUTION_INSTRUCTION",
        "REVIEW_REQUEST",
        "FIX_INSTRUCTION",
        "APPROVAL_REQUEST",
        "RECONCILIATION_REQUEST",
        "INFORMATION_ONLY",
        "PROJECT_CONTEXT_BOOTSTRAP",
        # Explicitly registered legacy instruction aliases.
        "WORK_UNIT",
        "IMPLEMENTATION",
    }
)

RESULT_MESSAGE_TYPES = frozenset(
    {
        "REVIEW_RESULT",
        "REVIEW_FINDING",
        "IMPLEMENTATION_RESULT",
        "INVALID_INSTRUCTION",
        "ROLE_AUTHORITY_CONFLICT",
        "APPROVAL_RESULT",
    }
)

ACTIONS = frozenset(
    {
        "READ",
        "TEST",
        "VALIDATE",
        "REPORT",
        "MUTATE_APPROVED_SCOPE",
        "ROUTE",
        "BIND",
        "INTERPRET",
        "REQUEST_APPROVAL",
        "ISSUE_INSTRUCTION",
        "APPROVE",
        "REJECT",
        "LOCAL_ACTION",
        "COMMIT",
        "PUSH",
        "PUBLISH",
        "AUTHORIZE",
        "SCOPE_EXPANSION",
    }
)

ARTIFACT_STAGES = frozenset({"DESIGN", "PLAN", "IMPLEMENTATION"})

LEGACY_CODEX_ROUTE_MARKER = "[CODEX]"
_LEGACY_IMPLEMENTATION_CONTEXTS = frozenset({"IMPLEMENTATION", "WORK_UNIT"})
_LEGACY_REVIEW_CONTEXTS = frozenset({"REVIEW", "REVIEW_REQUEST"})

_ALLOWED_ACTIONS = {
    "CODEX_IMPLEMENTER": frozenset(
        {"READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"}
    ),
    "CODEX_REVIEWER": frozenset({"READ", "TEST", "VALIDATE", "REPORT"}),
    "GPT_ORCHESTRATOR": frozenset(
        {
            "ROUTE",
            "BIND",
            "INTERPRET",
            "REQUEST_APPROVAL",
            "ISSUE_INSTRUCTION",
            "READ",
            "REPORT",
        }
    ),
    "GPT_REVIEWER": frozenset({"READ", "TEST", "VALIDATE", "REPORT", "INTERPRET"}),
    "USER_APPROVER": frozenset({"APPROVE", "REJECT"}),
    "USER_LOCAL": frozenset({"LOCAL_ACTION", "READ", "REPORT"}),
    "INFORMATION_ONLY": frozenset({"READ", "REPORT"}),
}


def _is_compound(value: object) -> bool:
    if isinstance(value, (list, tuple, set, frozenset)):
        return True
    return isinstance(value, str) and any(delimiter in value for delimiter in (",", ";", "\n"))


def validate_executor_role(value: object) -> list[str]:
    """Return stable protocol errors for the required scalar executor role."""

    if value is None or value == "":
        return ["EXECUTOR_REQUIRED"]
    if _is_compound(value):
        return ["EXECUTOR_MUST_BE_SCALAR"]
    if not isinstance(value, str) or value not in ROLES:
        return ["UNKNOWN_EXECUTOR_ROLE"]
    return []


def validate_instruction_type(value: object) -> list[str]:
    if not isinstance(value, str) or not value:
        return ["UNKNOWN_INSTRUCTION_TYPE"]
    if value in RESULT_MESSAGE_TYPES:
        return ["RESULT_TYPE_NOT_ALLOWED_AS_INSTRUCTION"]
    if value not in INSTRUCTION_TYPES:
        return ["UNKNOWN_INSTRUCTION_TYPE"]
    return []


def validate_result_message_type(value: object) -> list[str]:
    if not isinstance(value, str) or not value:
        return ["UNKNOWN_RESULT_MESSAGE_TYPE"]
    if value in INSTRUCTION_TYPES:
        return ["INSTRUCTION_TYPE_NOT_ALLOWED_AS_RESULT"]
    if value not in RESULT_MESSAGE_TYPES:
        return ["UNKNOWN_RESULT_MESSAGE_TYPE"]
    return []


def is_intrinsic_approval_result(result: Mapping[str, object] | None) -> bool:
    """Recognize only the closed, non-execution USER_APPROVER transaction."""
    if not isinstance(result, Mapping):
        return False
    core = result.get("approved_instruction")
    if not isinstance(core, Mapping) or set(core) != _APPROVED_INSTRUCTION_KEYS:
        return False
    scope_paths = core.get("scope_paths")
    work_unit_ref = core.get("target_work_unit_ref")
    safe_paths = (
        isinstance(scope_paths, list) and bool(scope_paths) and len(scope_paths) == len(set(scope_paths))
        and all(isinstance(path, str) and path and not path.startswith(("/", "\\"))
                and "\\" not in path and ".." not in path.split("/") and "" not in path.split("/")
                for path in scope_paths)
    )
    valid_core = (
        isinstance(core.get("instruction_id"), str) and bool(_UUID_RE.fullmatch(core["instruction_id"]))
        and isinstance(core.get("expected_state_revision"), int) and not isinstance(core.get("expected_state_revision"), bool)
        and core["expected_state_revision"] >= 0
        and isinstance(core.get("expected_base_sha"), str) and bool(_SHA_RE.fullmatch(core["expected_base_sha"]))
        and safe_paths
        and all(isinstance(core.get(key), str) and bool(core[key]) for key in (
            "target_project_context_id", "target_project_name", "target_github_repository_id",
            "target_github_repository_full_name",
        ))
        and isinstance(work_unit_ref, Mapping) and set(work_unit_ref) == {"path", "sha"}
        and isinstance(work_unit_ref.get("path"), str) and bool(work_unit_ref["path"])
        and not work_unit_ref["path"].startswith(("/", "\\")) and "\\" not in work_unit_ref["path"]
        and ".." not in work_unit_ref["path"].split("/") and "" not in work_unit_ref["path"].split("/")
        and isinstance(work_unit_ref.get("sha"), str) and bool(_SHA_RE.fullmatch(work_unit_ref["sha"]))
        and core.get("issuer_role") == "GPT_ORCHESTRATOR"
        and core.get("executor_role") == "CODEX_IMPLEMENTER"
        and isinstance(core.get("authorized_actions"), list) and "MUTATE_APPROVED_SCOPE" in core["authorized_actions"]
    )
    forbidden_locator_fields = {"approval_evidence_ref", "evidence_commit_sha", "blob_sha"}
    return valid_core and not forbidden_locator_fields.intersection(result) and (
        isinstance(result.get("result_id"), str) and bool(result["result_id"].strip())
        and result.get("result_message_type") == "APPROVAL_RESULT"
        and result.get("responder_role") == "USER_APPROVER"
        and result.get("status") == "PASS" and result.get("decision") in {"APPROVE", "REJECT"}
        and isinstance(result.get("response_to_instruction_id"), str)
        and bool(_UUID_RE.fullmatch(result["response_to_instruction_id"]))
        and result.get("evidence_refs") == [] and result.get("completion_gate") == "NONE"
        and result.get("remote_verification") == "NOT_ATTEMPTED"
        and "completion_evidence" in result and result.get("completion_evidence") is None
        and result.get("publication_authority") is None and result.get("sync_status") is None
        and result.get("remote_head_sha") is None
    )


def allowed_actions_for_role(role: str) -> frozenset[str]:
    return _ALLOWED_ACTIONS.get(role, frozenset())


def resolve_legacy_codex_route(route_marker: object, context: object) -> str:
    """Map only an explicit legacy [CODEX] marker plus one bounded context."""

    if route_marker != LEGACY_CODEX_ROUTE_MARKER:
        raise ValueError("UNKNOWN_LEGACY_ROUTE_MARKER")
    if context is None or context == "":
        raise ValueError("LEGACY_ROUTE_CONTEXT_REQUIRED")
    if isinstance(context, str):
        contexts = [context]
    elif isinstance(context, (list, tuple, set, frozenset)):
        contexts = list(context)
    else:
        raise ValueError("LEGACY_ROUTE_CONTEXT_INVALID")
    if len(contexts) != 1:
        raise ValueError("LEGACY_ROUTE_AMBIGUOUS")
    value = contexts[0]
    if value in _LEGACY_IMPLEMENTATION_CONTEXTS:
        return "CODEX_IMPLEMENTER"
    if value in _LEGACY_REVIEW_CONTEXTS:
        return "CODEX_REVIEWER"
    raise ValueError("UNKNOWN_LEGACY_ROUTE_CONTEXT")


def _as_action_values(values: Iterable[object] | None) -> list[object] | None:
    if values is None:
        return []
    if isinstance(values, (str, bytes, bytearray)):
        return None
    if isinstance(values, (list, tuple, set, frozenset)):
        return list(values)
    return None


def validate_action_authority(
    role: object,
    authorized_actions: Iterable[object] | None,
    forbidden_actions: Iterable[object] | None,
) -> list[str]:
    """Validate action vocabulary, role authority, and authorized/forbidden overlap."""

    if not isinstance(role, str) or role not in ROLES:
        return ["UNKNOWN_ROLE"]

    authorized = _as_action_values(authorized_actions)
    forbidden = _as_action_values(forbidden_actions)
    errors: list[str] = []
    if authorized is None or forbidden is None:
        return ["INVALID_ACTIONS_SHAPE"]
    for action in authorized + forbidden:
        if not isinstance(action, str) or action not in ACTIONS:
            if "UNKNOWN_ACTION" not in errors:
                errors.append("UNKNOWN_ACTION")
    if any(isinstance(action, str) and action not in allowed_actions_for_role(role) for action in authorized):
        errors.append("ACTION_NOT_ALLOWED_FOR_ROLE")
    authorized_strings = {action for action in authorized if isinstance(action, str)}
    forbidden_strings = {action for action in forbidden if isinstance(action, str)}
    if authorized_strings.intersection(forbidden_strings):
        errors.append("ACTION_IN_AUTHORIZED_AND_FORBIDDEN")
    return errors
