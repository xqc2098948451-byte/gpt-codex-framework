from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import secrets
from typing import Any, Callable, Mapping
from uuid import UUID, uuid4


REQUIRED_GUARDRAIL_ID = "cross-project-context-binding"
REQUIRED_GUARDRAIL_VERSION = "1.0.0"


@dataclass
class ContextDecision:
    decision: str
    reason: str = "NONE"
    identity_match: bool = False
    freshness_match: bool = False
    current_project_mutation: bool = False
    action_executable: bool = False
    authority: str = "NONE"
    hard_stop: bool = False
    business_execution: bool = False
    packet_status: str = "NONE"


def is_valid_project_context_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return value == str(parsed)


def generate_project_context_id() -> str:
    return str(uuid4())


def _decision(decision: str, reason: str, **kwargs: Any) -> ContextDecision:
    return ContextDecision(decision=decision, reason=reason, **kwargs)


def _guardrail_items(project_control: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    extensions = project_control.get("extensions") or {}
    if not isinstance(extensions, Mapping):
        return []
    guardrails = extensions.get("guardrails") or []
    if not isinstance(guardrails, list):
        return []
    return [item for item in guardrails if isinstance(item, Mapping) and item.get("id") == REQUIRED_GUARDRAIL_ID]


def required_guardrail_allows(project_control: Mapping[str, Any], operation: str) -> ContextDecision:
    """Validate the one CONTROL.extensions.guardrails[] safety fact."""

    context_id = project_control.get("project_context_id")
    if not is_valid_project_context_id(context_id):
        return _decision("BOOTSTRAP_REQUIRED", "PROJECT_CONTEXT_ID_MISSING")

    framework = project_control.get("framework") or {}
    adopted = framework.get("adopted_version") if isinstance(framework, Mapping) else None
    if not isinstance(adopted, str) or not adopted.startswith("2.1."):
        return _decision("ALLOW", "V2_1_CONTRACT_NOT_ADOPTED", identity_match=True, freshness_match=True)

    extensions = project_control.get("extensions") or {}
    malformed_collection = not isinstance(extensions, Mapping) or not isinstance(extensions.get("guardrails", []), list)
    if malformed_collection:
        return _decision("DENY", "REQUIRED_CONTEXT_GUARDRAIL_MALFORMED")

    items = _guardrail_items(project_control)
    if not items:
        return _decision("DENY", "REQUIRED_CONTEXT_GUARDRAIL_ABSENT")
    if len(items) != 1:
        return _decision("DENY", "REQUIRED_CONTEXT_GUARDRAIL_MALFORMED")

    item = items[0]
    if (
        item.get("source") != "builtin"
        or item.get("version") != REQUIRED_GUARDRAIL_VERSION
        or not isinstance(item.get("enabled"), bool)
    ):
        return _decision("DENY", "REQUIRED_CONTEXT_GUARDRAIL_MALFORMED")
    if not item["enabled"]:
        return _decision("DENY", "REQUIRED_CONTEXT_GUARDRAIL_DISABLED")
    return _decision("ALLOW", "REQUIRED_CONTEXT_GUARDRAIL_PRESENT", identity_match=True, freshness_match=True)


def bootstrap_project_context(
    control: Mapping[str, Any],
    project_name: str,
    id_factory: Callable[[], str] = generate_project_context_id,
) -> dict[str, Any]:
    result = deepcopy(dict(control))
    existing = result.get("project_context_id")
    if not is_valid_project_context_id(existing):
        result["project_context_id"] = id_factory()
    if not result.get("project_name"):
        result["project_name"] = project_name
    return result


def _valid_or_missing(value: Any) -> str:
    if value is None or value == "":
        return "MISSING"
    return "VALID" if is_valid_project_context_id(value) else "MALFORMED"


def evaluate_instruction(
    envelope: Mapping[str, Any],
    local_context_id: str | None,
    current_state_revision: int | None,
    analysis_only: bool = False,
    project_control: Mapping[str, Any] | None = None,
    local_repository_id: str | None = None,
) -> ContextDecision:
    target = envelope.get("target_project_context_id")
    target_status = _valid_or_missing(target)
    if target_status == "MISSING":
        return _decision("DENY", "TARGET_PROJECT_CONTEXT_MISSING")
    if target_status == "MALFORMED":
        return _decision("DENY", "TARGET_PROJECT_CONTEXT_MALFORMED")
    if not is_valid_project_context_id(local_context_id):
        return _decision("BOOTSTRAP_REQUIRED", "LOCAL_PROJECT_CONTEXT_MISSING")
    if target != local_context_id:
        if analysis_only:
            return _decision("ANALYSIS_ONLY", "CROSS_PROJECT_INSTRUCTION_MISMATCH", authority="NONE")
        return _decision("DENY", "CROSS_PROJECT_INSTRUCTION_MISMATCH", packet_status="QUARANTINED")

    expected = envelope.get("expected_state_revision")
    if expected is not None and current_state_revision is not None and expected != current_state_revision:
        return _decision(
            "RECONCILIATION_REQUIRED",
            "STALE_INSTRUCTION",
            identity_match=True,
            freshness_match=False,
        )
    if project_control is not None:
        github = project_control.get("github")
        target_repository_id = envelope.get("target_github_repository_id")
        if isinstance(github, Mapping):
            bound_repository_id = github.get("repository_id")
            if not target_repository_id:
                return _decision("DENY", "TARGET_GITHUB_REPOSITORY_MISSING", identity_match=True)
            if target_repository_id != bound_repository_id or (local_repository_id is not None and local_repository_id != bound_repository_id):
                return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", identity_match=True, packet_status="QUARANTINED")
        guardrail = required_guardrail_allows(project_control, "instruction")
        if guardrail.decision != "ALLOW":
            return guardrail
    return _decision(
        "ALLOW",
        "IDENTITY_AND_FRESHNESS_MATCH",
        identity_match=True,
        freshness_match=True,
        current_project_mutation=True,
        action_executable=True,
        authority="CURRENT_PROJECT_PATH",
    )


def evaluate_return(
    envelope: Mapping[str, Any],
    active_context_id: str | None,
    current_state_revision: int | None = None,
    analysis_only: bool = False,
    project_control: Mapping[str, Any] | None = None,
    local_repository_id: str | None = None,
) -> ContextDecision:
    if not is_valid_project_context_id(active_context_id):
        return _decision("DENY", "ACTIVE_PROJECT_CONTEXT_UNBOUND")
    source = envelope.get("source_project_context_id")
    source_status = _valid_or_missing(source)
    if source_status == "MISSING":
        return _decision("DENY", "SOURCE_PROJECT_CONTEXT_MISSING")
    if source_status == "MALFORMED":
        return _decision("DENY", "SOURCE_PROJECT_CONTEXT_MALFORMED")
    if source != active_context_id:
        if analysis_only:
            return _decision("ANALYSIS_ONLY", "CROSS_PROJECT_CONTEXT_MISMATCH", authority="NONE", packet_status="QUARANTINED")
        return _decision("DENY", "CROSS_PROJECT_CONTEXT_MISMATCH", packet_status="QUARANTINED")

    state_revision = envelope.get("state_revision")
    if state_revision is not None and current_state_revision is not None and state_revision != current_state_revision:
        return _decision(
            "RECONCILIATION_REQUIRED",
            "STALE_STATE_REVISION",
            identity_match=True,
            freshness_match=False,
        )
    if project_control is not None:
        github = project_control.get("github")
        source_repository_id = envelope.get("source_github_repository_id")
        if isinstance(github, Mapping):
            bound_repository_id = github.get("repository_id")
            if not source_repository_id:
                return _decision("DENY", "SOURCE_GITHUB_REPOSITORY_MISSING", identity_match=True)
            if source_repository_id != bound_repository_id or (local_repository_id is not None and local_repository_id != bound_repository_id):
                return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", identity_match=True, packet_status="QUARANTINED")
        guardrail = required_guardrail_allows(project_control, "return")
        if guardrail.decision != "ALLOW":
            return guardrail
    return _decision(
        "ALLOW",
        "IDENTITY_AND_FRESHNESS_MATCH",
        identity_match=True,
        freshness_match=True,
        current_project_mutation=True,
        action_executable=True,
        authority="CURRENT_PROJECT_PATH",
    )


def evaluate_bootstrap(
    envelope: Mapping[str, Any],
    local_control: Mapping[str, Any] | None,
) -> ContextDecision:
    if local_control and local_control.get("project_id"):
        target = envelope.get("bootstrap_target_project_id")
        if not target:
            return _decision("DENY", "BOOTSTRAP_TARGET_PROJECT_ID_MISSING")
        if target != local_control.get("project_id"):
            return _decision("DENY", "CROSS_PROJECT_BOOTSTRAP_MISMATCH")
        return _decision("ALLOW", "LEGACY_BOOTSTRAP_BOUND", hard_stop=True, business_execution=False)

    if envelope.get("bootstrap_challenge_id"):
        return _decision("DENY", "BOOTSTRAP_CHALLENGE_MISMATCH")
    return _decision("BOOTSTRAP_REQUIRED", "BOOTSTRAP_CHALLENGE_REQUIRED")


def create_bootstrap_challenge(
    project_facts: Mapping[str, Any],
    challenge_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    factory = challenge_factory or (lambda: secrets.token_urlsafe(24))
    return {
        "bootstrap_challenge_id": factory(),
        "project_name_hint": project_facts.get("project_name_hint"),
        "repo_root_hint": project_facts.get("repo_root_hint"),
        "repository_fingerprint_hint": project_facts.get("repository_fingerprint_hint"),
        "consumed": False,
        "stale": False,
    }


def verify_bootstrap_challenge(
    envelope: Mapping[str, Any],
    pending_challenge: dict[str, Any],
) -> ContextDecision:
    if pending_challenge.get("consumed"):
        return _decision("DENY", "BOOTSTRAP_CHALLENGE_REPLAY")
    if pending_challenge.get("stale"):
        return _decision("DENY", "BOOTSTRAP_CHALLENGE_STALE")
    received = envelope.get("bootstrap_challenge_id")
    expected = pending_challenge.get("bootstrap_challenge_id")
    if not received or received != expected:
        return _decision("DENY", "BOOTSTRAP_CHALLENGE_MISMATCH")
    pending_challenge["consumed"] = True
    return _decision("ALLOW", "BOOTSTRAP_CHALLENGE_VERIFIED", hard_stop=True, business_execution=False)


def recover_contamination(kind: str, baseline_confirmed: bool = False) -> dict[str, Any]:
    if kind not in {"CHAT_ONLY_CONTAMINATION", "REPOSITORY_MUTATION_POSSIBLE"}:
        raise ValueError(f"unsupported contamination kind: {kind}")
    return {
        "status": "CONTEXT_CONTAMINATION_DETECTED",
        "recovery": "LAST_VALID_PROJECT_CONTEXT",
        "audit_required": kind == "REPOSITORY_MUTATION_POSSIBLE" and not baseline_confirmed,
        "audit_mode": "READ_ONLY_CONTAMINATION_AUDIT" if kind == "REPOSITORY_MUTATION_POSSIBLE" else "NONE",
        "destructive_rollback": False,
        "baseline_confirmed": baseline_confirmed,
    }
