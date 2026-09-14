from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import secrets
from typing import Any, Callable, Mapping
from uuid import UUID, uuid4


REQUIRED_GUARDRAIL_ID = "cross-project-context-binding"
REQUIRED_GUARDRAIL_VERSION = "1.0.0"
_READ_ONLY_BOUNDARY_OPERATIONS = frozenset({"READ", "EVALUATE"})
_PROJECT_EVOLUTION_TRANSPORTS = frozenset({"MANUAL", "PROJECT_PUSH", "PROJECT_PULL"})
_RESULT_EVIDENCE_REF_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@#%+=-]{0,255}$")
_PROTECTED_RESOURCE_TYPES = frozenset({
    "CONTROL", "STATE", "WORK_UNIT", "INSTRUCTION", "RESULT", "EVIDENCE",
    "REPOSITORY_BINDING", "EXTENSION_CONFIGURATION", "PROJECT_MAP", "RESUME",
})


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


@dataclass(frozen=True)
class ProjectIdentity:
    project_id: str
    project_context_id: str
    repository_id: str
    repository_full_name: str
    default_branch: str
    project_root: Path | None
    framework_root: Path | None
    management: bool
    project_role: str
    framework_role: str


@dataclass(frozen=True)
class ProjectResourceBinding:
    project_id: str
    project_context_id: str
    repository_id: str
    repository_full_name: str | None
    resource_type: str


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


def load_project_identity(
    control: Mapping[str, Any],
    *,
    project_root: Path | None = None,
    framework_root: Path | None = None,
) -> ProjectIdentity:
    github = control.get("github")
    roots = control.get("roots")
    project_id = control.get("project_id")
    context_id = control.get("project_context_id")
    if (
        not isinstance(project_id, str) or not project_id.strip()
        or not is_valid_project_context_id(context_id)
        or not isinstance(github, Mapping)
        or not all(isinstance(github.get(key), str) and github.get(key).strip() for key in ("repository_id", "repository_full_name", "default_branch"))
        or not isinstance(roots, Mapping)
    ):
        raise ValueError("PROJECT_IDENTITY_INVALID")
    management = control.get("framework_management_only") is True
    project_role = roots.get("project_role")
    framework_role = roots.get("framework_role")
    ordinary = project_role == "AUTHORITATIVE" and framework_role == "ADVISORY"
    self_hosted = management and project_role == "AUTHORITATIVE" and framework_role == "SELF_MANAGED"
    if not (ordinary or self_hosted):
        raise ValueError("PROJECT_IDENTITY_INVALID")
    return ProjectIdentity(
        project_id=project_id.strip(), project_context_id=context_id,
        repository_id=github["repository_id"].strip(), repository_full_name=github["repository_full_name"].strip(),
        default_branch=github["default_branch"].strip(), project_root=project_root, framework_root=framework_root,
        management=management, project_role=project_role, framework_role=framework_role,
    )


def evaluate_project_identity(
    control: Mapping[str, Any], *, expected_project_id: str | None = None,
    expected_project_context_id: str | None = None, expected_repository_id: str | None = None,
    expected_repository_full_name: str | None = None,
) -> ContextDecision:
    try:
        identity = load_project_identity(control)
    except (TypeError, ValueError, KeyError):
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    if expected_project_id is not None and expected_project_id != identity.project_id:
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    if expected_project_context_id is not None and expected_project_context_id != identity.project_context_id:
        return _decision("DENY", "CROSS_PROJECT_CONTEXT_MISMATCH", packet_status="QUARANTINED")
    if expected_repository_id is not None and expected_repository_id != identity.repository_id:
        return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", packet_status="QUARANTINED")
    if expected_repository_full_name is not None and expected_repository_full_name != identity.repository_full_name:
        return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", packet_status="QUARANTINED")
    return _decision("ALLOW", "IDENTITY_MATCH", identity_match=True, freshness_match=True,
                     current_project_mutation=False, action_executable=False, authority="IDENTITY_VALIDATION")


def _evolution_input_attempts_authority(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    from role_communication import _EVOLUTION_AUTHORITY_FIELDS, validate_evolution_metadata_authority

    candidates = [value]
    metadata = value.get("evolution_metadata")
    if isinstance(metadata, Mapping):
        candidates.append(metadata)
    return any(
        _EVOLUTION_AUTHORITY_FIELDS.intersection(candidate)
        or validate_evolution_metadata_authority(candidate)
        for candidate in candidates
    )


def validate_project_evolution_enrollment(
    project_control: Mapping[str, Any], enrollment: Mapping[str, Any],
) -> ContextDecision:
    """Validate an explicit, identity-bound evolution enrollment without registering it."""
    if not isinstance(enrollment, Mapping):
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    if _evolution_input_attempts_authority(enrollment):
        return _decision("DENY", "PROJECT_AUTHORITY_BOUNDARY_VIOLATION", hard_stop=True)
    if (
        enrollment.get("explicit_enrollment") is not True
        or enrollment.get("transport") not in _PROJECT_EVOLUTION_TRANSPORTS
        or not isinstance(enrollment.get("project_id"), str) or not enrollment["project_id"].strip()
        or not is_valid_project_context_id(enrollment.get("project_context_id"))
        or not isinstance(enrollment.get("repository_id"), str) or not enrollment["repository_id"].strip()
        or ("repository_full_name" in enrollment and (
            not isinstance(enrollment["repository_full_name"], str)
            or not enrollment["repository_full_name"].strip()
        ))
    ):
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    return evaluate_project_identity(
        project_control,
        expected_project_id=enrollment["project_id"],
        expected_project_context_id=enrollment["project_context_id"],
        expected_repository_id=enrollment["repository_id"],
        expected_repository_full_name=enrollment.get("repository_full_name"),
    )


def _source_provenance_digest(provenance: Mapping[str, Any]) -> str:
    canonical = json.dumps(provenance, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _is_bounded_result_evidence_ref(value: object) -> bool:
    return isinstance(value, str) and _RESULT_EVIDENCE_REF_PATTERN.fullmatch(value) is not None


def build_project_evolution_observation(
    project_control: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    enrollment: Mapping[str, Any],
    *,
    observed_at: str,
    local_revision_ref: str,
) -> dict[str, Any]:
    """Create a bounded derived observation; it never authorizes or persists Project work."""
    if _evolution_input_attempts_authority(enrollment) or _evolution_input_attempts_authority(evaluation):
        raise ValueError("PROJECT_AUTHORITY_BOUNDARY_VIOLATION")
    enrollment_decision = validate_project_evolution_enrollment(project_control, enrollment)
    if enrollment_decision.decision != "ALLOW":
        raise ValueError(enrollment_decision.reason)
    source_version = evaluation.get("source_framework_version")
    provenance = evaluation.get("source_provenance")
    outcome = evaluation.get("classification")
    if (
        not isinstance(source_version, str) or not source_version
        or not isinstance(provenance, Mapping)
        or not isinstance(outcome, str) or not outcome
        or not isinstance(observed_at, str) or not observed_at
        or not isinstance(local_revision_ref, str) or not local_revision_ref
    ):
        raise ValueError("PROJECT_IDENTITY_INVALID")
    identity = load_project_identity(project_control)
    observation = {
        "classification": "DERIVED_OBSERVATION_ONLY",
        "project_id": identity.project_id,
        "project_context_id": identity.project_context_id,
        "repository_id": identity.repository_id,
        "source_framework_version": source_version,
        "source_provenance_digest": _source_provenance_digest(provenance),
        "compatibility_outcome": outcome,
        "observed_at": observed_at,
        "local_revision_ref": local_revision_ref,
    }
    repository_full_name = enrollment.get("repository_full_name")
    if isinstance(repository_full_name, str) and repository_full_name:
        observation["repository_full_name"] = repository_full_name
    result_evidence_ref = evaluation.get("result_evidence_ref")
    if _is_bounded_result_evidence_ref(result_evidence_ref):
        observation["result_evidence_ref"] = result_evidence_ref
    return observation


def _index_identity_tuple(value: object) -> tuple[str, str, str] | None:
    if not isinstance(value, Mapping):
        return None
    project_id = value.get("project_id")
    context_id = value.get("project_context_id")
    repository_id = value.get("repository_id")
    if (
        not isinstance(project_id, str) or not project_id.strip()
        or not is_valid_project_context_id(context_id)
        or not isinstance(repository_id, str) or not repository_id.strip()
    ):
        return None
    return project_id.strip(), context_id, repository_id.strip()


def _observation_timestamp(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def _index_row(
    identity: tuple[str, str, str], enrollment: Mapping[str, Any] | None,
    observation: Mapping[str, Any] | None, status: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "classification": "FRAMEWORK_MANAGEMENT_METADATA",
        "evolution_status": status,
        "project_id": identity[0],
        "project_context_id": identity[1],
        "repository_id": identity[2],
    }
    for source in (enrollment, observation):
        if isinstance(source, Mapping):
            full_name = source.get("repository_full_name")
            if isinstance(full_name, str) and full_name.strip():
                row["repository_full_name"] = full_name.strip()
                break
    if isinstance(enrollment, Mapping):
        enrollment_id = enrollment.get("enrollment_id")
        if _is_bounded_result_evidence_ref(enrollment_id):
            row["enrollment_id"] = enrollment_id
        row["enrollment_status"] = "RETIRED" if enrollment.get("enrollment_status") == "RETIRED" else "ACTIVE"
    if isinstance(observation, Mapping):
        for key in ("source_framework_version", "source_provenance_digest", "compatibility_outcome", "observed_at", "local_revision_ref"):
            value = observation.get(key)
            if isinstance(value, (str, int, float)) and not isinstance(value, bool):
                row[key] = value
        if _is_bounded_result_evidence_ref(observation.get("result_evidence_ref")):
            row["result_evidence_ref"] = observation["result_evidence_ref"]
    return row


def classify_framework_evolution_index(
    enrollments: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    observations: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    *, now: object, stale_after_seconds: object,
) -> list[dict[str, Any]]:
    """Classify supplied management facts only; no Project authority or persistence is created."""
    now_timestamp = _observation_timestamp(now)
    stale_after = float(stale_after_seconds) if isinstance(stale_after_seconds, (int, float)) else None
    if now_timestamp is None or stale_after is None or stale_after < 0:
        return []
    enrolled: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for enrollment in enrollments:
        identity = _index_identity_tuple(enrollment)
        if identity is not None and enrollment.get("explicit_enrollment") is True:
            enrolled.setdefault(identity, []).append(enrollment)
    observed: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for observation in observations:
        identity = _index_identity_tuple(observation)
        if identity is not None:
            observed.setdefault(identity, []).append(observation)
    repository_ids_by_context: dict[tuple[str, str], set[str]] = {}
    for identity in set(enrolled) | set(observed):
        repository_ids_by_context.setdefault(identity[:2], set()).add(identity[2])
    conflicted_contexts = {
        context for context, repository_ids in repository_ids_by_context.items()
        if len(repository_ids) > 1
    }
    rows: list[dict[str, Any]] = []
    for identity in sorted(set(enrolled) | set(observed)):
        enrollment = sorted(enrolled.get(identity, []), key=lambda item: json.dumps(item, sort_keys=True, default=str))[0] if identity in enrolled else None
        candidates = observed.get(identity, [])
        observation = max(candidates, key=lambda item: (_observation_timestamp(item.get("observed_at")) or float("-inf"), json.dumps(item, sort_keys=True, default=str))) if candidates else None
        if identity[:2] in conflicted_contexts:
            status = "PROJECT_EVOLUTION_ENROLLMENT_CONFLICT"
        elif enrollment is None:
            status = "PROJECT_EVOLUTION_NOT_ENROLLED"
        else:
            observed_at = _observation_timestamp(observation.get("observed_at")) if observation else None
            if enrollment.get("enrollment_status") == "RETIRED" or observed_at is None or now_timestamp - observed_at >= stale_after:
                status = "PROJECT_EVOLUTION_OBSERVATION_STALE"
            else:
                status = "PROJECT_EVOLUTION_OBSERVATION_CURRENT"
        rows.append(_index_row(identity, enrollment, observation, status))
    return rows


def _complete_transfer_identity(value: object) -> tuple[str, str, str, str] | None:
    identity = _index_identity_tuple(value)
    if not isinstance(value, Mapping) or identity is None or value.get("explicit_enrollment") is not True:
        return None
    full_name = value.get("repository_full_name")
    if not isinstance(full_name, str) or not full_name.strip():
        return None
    return *identity, full_name.strip()


def validate_repository_transfer(
    old_enrollment: Mapping[str, Any], new_enrollment: Mapping[str, Any], *,
    old_repository_evidence: Mapping[str, Any] | None, new_repository_evidence: Mapping[str, Any] | None,
) -> ContextDecision:
    """Validate supplied two-ended transfer evidence without transferring or mutating anything."""
    from github_repository_binding import repository_evidence_matches_identity
    from git_continuity import is_verified_repository_continuity_evidence

    old_identity = _complete_transfer_identity(old_enrollment)
    new_identity = _complete_transfer_identity(new_enrollment)
    if old_identity is None or new_identity is None:
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    if old_identity[:2] != new_identity[:2] or (old_identity[2] == new_identity[2] and old_identity[3] != new_identity[3]):
        return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
    if not (
        is_verified_repository_continuity_evidence(old_repository_evidence)
        and is_verified_repository_continuity_evidence(new_repository_evidence)
        and repository_evidence_matches_identity(old_enrollment, old_repository_evidence)
        and repository_evidence_matches_identity(new_enrollment, new_repository_evidence)
    ):
        return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", packet_status="QUARANTINED")
    return _decision(
        "ALLOW", "REPOSITORY_TRANSFER_RECONCILIATION", identity_match=True,
        current_project_mutation=False, action_executable=False, authority="REPOSITORY_EVIDENCE_READ_ONLY",
    )


def _resource_binding(resource: Mapping[str, Any], resource_type: str) -> ProjectResourceBinding | None:
    if resource_type not in _PROTECTED_RESOURCE_TYPES:
        return None
    project_id = resource.get("project_id")
    project_context_id = resource.get("project_context_id")
    repository_id = resource.get("repository_id")
    repository_full_name = resource.get("repository_full_name")
    if (
        not isinstance(project_id, str) or not project_id.strip()
        or not is_valid_project_context_id(project_context_id)
        or not isinstance(repository_id, str) or not repository_id.strip()
        or (repository_full_name is not None and (
            not isinstance(repository_full_name, str) or not repository_full_name.strip()
        ))
    ):
        return None
    return ProjectResourceBinding(
        project_id=project_id.strip(),
        project_context_id=project_context_id,
        repository_id=repository_id.strip(),
        repository_full_name=repository_full_name.strip() if isinstance(repository_full_name, str) else None,
        resource_type=resource_type,
    )


def _quarantined_resource_decision(reason: str, *, analysis_only: bool) -> ContextDecision:
    return _decision(
        "ANALYSIS_ONLY" if analysis_only else "DENY",
        reason,
        current_project_mutation=False,
        action_executable=False,
        authority="NONE",
        hard_stop=not analysis_only,
        packet_status="QUARANTINED",
    )


def evaluate_cross_project_resource_boundary(
    active_identity: ProjectIdentity,
    resource: Mapping[str, Any],
    *,
    resource_type: str,
    analysis_only: bool = False,
) -> ContextDecision:
    """Classify a protected resource without granting execution authority."""
    binding = _resource_binding(resource, resource_type)
    if binding is None:
        return _quarantined_resource_decision("PROJECT_IDENTITY_INVALID", analysis_only=analysis_only)
    if (
        binding.project_id != active_identity.project_id
        or binding.project_context_id != active_identity.project_context_id
    ):
        return _quarantined_resource_decision("CROSS_PROJECT_CONTEXT_MISMATCH", analysis_only=analysis_only)
    if (
        binding.repository_id != active_identity.repository_id
        or (
            binding.repository_full_name is not None
            and binding.repository_full_name != active_identity.repository_full_name
        )
    ):
        return _quarantined_resource_decision("GITHUB_REPOSITORY_MISMATCH", analysis_only=analysis_only)
    return _decision(
        "ALLOW",
        "RESOURCE_BINDING_MATCH",
        identity_match=True,
        freshness_match=True,
        current_project_mutation=False,
        action_executable=False,
        authority="RESOURCE_BOUNDARY_READ_ONLY",
    )


def evaluate_project_authority_boundary(
    identity: ProjectIdentity, *, source: str, operation: str,
) -> ContextDecision:
    """Validate a read-only authority boundary; never authorize mutation."""
    if source not in {"project", "framework"}:
        return _decision("DENY", "PROJECT_AUTHORITY_BOUNDARY_VIOLATION", identity_match=True,
                         current_project_mutation=False, action_executable=False, hard_stop=True)
    if operation not in _READ_ONLY_BOUNDARY_OPERATIONS:
        reason = "FRAMEWORK_ADOPTION_NOT_AUTHORIZED" if operation == "ADOPT" else "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"
        return _decision("DENY", reason, identity_match=True, current_project_mutation=False,
                         action_executable=False, hard_stop=operation != "ADOPT")
    return _decision("ALLOW", "PROJECT_AUTHORITY_BOUNDARY_READ_ONLY", identity_match=True,
                     freshness_match=True, current_project_mutation=False, action_executable=False,
                     authority="READ_ONLY_BOUNDARY")


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
            return _decision("ANALYSIS_ONLY", "CROSS_PROJECT_CONTEXT_MISMATCH", authority="NONE")
        return _decision("DENY", "CROSS_PROJECT_CONTEXT_MISMATCH", packet_status="QUARANTINED")

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
        source_repository_full_name = envelope.get("source_github_repository_full_name")
        if isinstance(github, Mapping):
            bound_repository_id = github.get("repository_id")
            bound_repository_full_name = github.get("repository_full_name")
            if not source_repository_id:
                return _decision("DENY", "SOURCE_GITHUB_REPOSITORY_MISSING", identity_match=True)
            if source_repository_id != bound_repository_id or (local_repository_id is not None and local_repository_id != bound_repository_id):
                return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", identity_match=True, packet_status="QUARANTINED")
            if source_repository_full_name not in (None, "") and source_repository_full_name != bound_repository_full_name:
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
