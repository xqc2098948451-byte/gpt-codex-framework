"""Shared role and message-side rules for the role communication protocol."""

from __future__ import annotations

from collections.abc import Iterable


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
    }
)

ARTIFACT_STAGES = frozenset({"DESIGN", "PLAN", "IMPLEMENTATION"})

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


def allowed_actions_for_role(role: str) -> frozenset[str]:
    return _ALLOWED_ACTIONS.get(role, frozenset())


def _as_action_values(values: Iterable[object] | None) -> list[object]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    return list(values)


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
    for action in authorized + forbidden:
        if not isinstance(action, str) or action not in ACTIONS:
            if "UNKNOWN_ACTION" not in errors:
                errors.append("UNKNOWN_ACTION")
    if any(isinstance(action, str) and action not in allowed_actions_for_role(role) for action in authorized):
        errors.append("ACTION_NOT_ALLOWED_FOR_ROLE")
    if set(authorized).intersection(forbidden):
        errors.append("ACTION_IN_AUTHORIZED_AND_FORBIDDEN")
    return errors

