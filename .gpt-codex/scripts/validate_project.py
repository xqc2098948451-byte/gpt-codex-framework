#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, uuid
from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from kernel_rules import *
from framework_feedback import validate_execution_policy, validate_project_strategy_lifecycle
from context_binding import (
    build_project_evolution_observation,
    evaluate_project_identity,
    evaluate_return,
    is_valid_project_context_id,
    required_guardrail_allows,
    validate_project_evolution_enrollment,
)
from continuity_resume import (
    load_resume_checkpoint,
    validate_execution_slots,
    validate_slot_transition,
)
from publication_contract import validate_result_authority, validate_state_authority
from role_communication import (
    INSTRUCTION_TYPES,
    RESULT_MESSAGE_TYPES,
    ROLES,
    validate_action_authority,
    validate_executor_role,
    validate_instruction_type,
    validate_result_message_type,
)
from project_navigation import (
    load_module_map,
    load_project_map,
    validate_navigation_identity,
)

REQUIRED_CONTEXT_GUARDRAIL = 'cross-project-context-binding'
REQUIRED_REPOSITORY_GUARDRAIL = 'github-repository-binding'
FRAMEWORK_ROOT = HERE.parent.parent

_MUTATING_ACTIONS = frozenset({"MUTATE_APPROVED_SCOPE", "COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION"})
_LEGACY_INSTRUCTION_TYPES = frozenset({"WORK_UNIT", "IMPLEMENTATION", "PROJECT_CONTEXT_BOOTSTRAP"})
_ROLE_AWARE_INSTRUCTION_TYPES = INSTRUCTION_TYPES - _LEGACY_INSTRUCTION_TYPES
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")


def validate_project_identity_boundary(control: Mapping[str, Any], *, consumer: bool) -> list[str]:
    management = control.get("framework_management_only") is True
    roots = control.get("roots") or {}
    explicit_management = management and control.get("governance_profile") == "FRAMEWORK_MANAGEMENT" and roots.get("framework_role") == "SELF_MANAGED"
    ordinary_consumer = (
        not management and control.get("governance_profile") != "FRAMEWORK_MANAGEMENT"
        and roots.get("project_role") == "AUTHORITATIVE" and roots.get("framework_role") == "ADVISORY"
        and roots.get("framework_kernel_access") == "READ_ONLY" and roots.get("framework_builtins_access") == "READ_ONLY"
    )
    if (consumer and not ordinary_consumer) or (not consumer and not explicit_management):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    return []


def _is_safe_repository_relative_path(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
    ):
        return False
    return all(component not in {"", ".", ".."} for component in value.split("/"))


def _paths_overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _root_pairs(harness: str, products: list[str], deploy: list[str]) -> list[tuple[str, str]]:
    roots = [harness, *products, *deploy]
    return [
        (roots[index], roots[other])
        for index in range(len(roots))
        for other in range(index + 1, len(roots))
    ]


def validate_harness_root_separation(control: Mapping[str, Any]) -> list[str]:
    roots = control.get("roots")
    if not isinstance(roots, Mapping):
        return []
    declared = (
        "harness_root" in roots
        or "product_roots" in roots
        or "deploy_roots" in roots
        or "production_excludes" in roots
    )
    if not declared:
        return []
    harness = roots.get("harness_root")
    products = roots.get("product_roots")
    deploy = roots.get("deploy_roots")
    excludes = roots.get("production_excludes")
    if (
        not isinstance(harness, str) or not harness.strip()
        or not isinstance(products, list) or not products
        or not all(isinstance(item, str) and item.strip() for item in products)
        or not isinstance(deploy, list)
        or not all(isinstance(item, str) and item.strip() for item in deploy)
        or not isinstance(excludes, list)
        or not all(isinstance(item, str) and item.strip() for item in excludes)
    ):
        return ["HARNESS_ROOTS_INVALID"]
    if not all(_is_safe_repository_relative_path(item) for item in [harness, *products, *deploy, *excludes]):
        return ["HARNESS_ROOTS_INVALID"]
    if any(_paths_overlap(left, right) for left, right in _root_pairs(harness, products, deploy)):
        return ["HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP"]
    if harness not in excludes:
        return ["HARNESS_PRODUCTION_EXCLUSION_REQUIRED"]
    return []


def has_complete_declared_project_identity(control: Mapping[str, Any]) -> bool:
    return "project_context_id" in control and "github" in control


def validate_identity_before_derived(root: Path, gov: Path, control: Mapping[str, Any], *, active_context_id: str, local_repository_id: str) -> list[str]:
    decision = evaluate_project_identity(control, expected_project_context_id=active_context_id, expected_repository_id=local_repository_id)
    if decision.decision != "ALLOW":
        return [decision.reason]
    return validate_optional_navigation_and_resume(root, gov, dict(control))


def validate_project_identity_and_derived(root: Path, gov: Path, control: Mapping[str, Any]) -> list[str]:
    if not has_complete_declared_project_identity(control):
        return validate_optional_navigation_and_resume(root, gov, dict(control))
    github = control.get("github")
    repository_id = github.get("repository_id") if isinstance(github, Mapping) else None
    return validate_identity_before_derived(
        root,
        gov,
        control,
        active_context_id=control.get("project_context_id"),
        local_repository_id=repository_id,
    )


def validate_project_evolution_orchestration() -> list[str]:
    """Confirm Task 5's local-only interfaces exist without evaluating or mutating a Project."""
    return [] if callable(validate_project_evolution_enrollment) and callable(build_project_evolution_observation) else [
        "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"
    ]


def evaluate_framework_compatibility(
    project_control: Mapping[str, Any], framework_facts: Mapping[str, Any],
) -> dict[str, Any]:
    if framework_facts.get("identity_conflict") or framework_facts.get("authority_conflict"):
        classification, reason = "CONFLICT", "FRAMEWORK_PROJECT_CONFLICT"
    elif framework_facts.get("evaluated_version") == (project_control.get("framework") or {}).get("adopted_version"):
        classification, reason = "NO_ACTION", "ADOPTED_VERSION_MATCH"
    elif framework_facts.get("requires_migration"):
        classification, reason = "REQUIRED_MIGRATION", "EXPLICIT_MIGRATION_REQUIRED"
    elif framework_facts.get("compatible") and framework_facts.get("reusable"):
        classification, reason = "OPTIONAL_REUSE", "COMPATIBLE_REUSE_AVAILABLE"
    elif framework_facts.get("compatible"):
        classification, reason = "RECOMMENDED_UPGRADE", "COMPATIBLE_NEWER_FRAMEWORK"
    else:
        classification, reason = "CONFLICT", "FRAMEWORK_COMPATIBILITY_CONFLICT"
    return {"classification": classification, "reason": reason, "mutated": False, "adoption_authorized": False}


_EXTERNAL_EVOLUTION_CLASSIFICATIONS = frozenset({
    "READ_ONLY_EVOLUTION_SOURCE", "DERIVED_OBSERVATION_ONLY", "FRAMEWORK_MANAGEMENT_METADATA",
})
_EXTERNAL_AUTHORITY_FIELDS = frozenset({
    "authorized_actions", "target_work_unit", "state_revision", "command", "retry", "queue",
    "project_mutation", "role_authority", "schedule_execution", "force_adoption",
})


def _project_identity_decision(
    project_control: Mapping[str, Any], instruction: Mapping[str, Any] | None = None,
):
    decision = evaluate_project_identity(project_control)
    if decision.decision != "ALLOW" or instruction is None:
        return decision
    expected_context = instruction.get("target_project_context_id")
    if expected_context is not None:
        target_control = dict(project_control)
        target_control["project_context_id"] = expected_context
        target_identity = evaluate_project_identity(target_control)
        if target_identity.decision != "ALLOW":
            return target_identity
        decision = evaluate_project_identity(project_control, expected_project_context_id=expected_context)
        if decision.decision != "ALLOW":
            return decision
    expected_repository_id = instruction.get("target_github_repository_id")
    if expected_repository_id is not None:
        target_control = dict(project_control)
        target_github = dict(project_control.get("github") or {})
        target_github["repository_id"] = expected_repository_id
        target_control["github"] = target_github
        target_identity = evaluate_project_identity(target_control)
        if target_identity.decision != "ALLOW":
            return target_identity
        decision = evaluate_project_identity(project_control, expected_repository_id=expected_repository_id)
        if decision.decision != "ALLOW":
            return decision
    expected_repository_full_name = instruction.get("target_github_repository_full_name")
    if expected_repository_full_name is not None:
        target_control = dict(project_control)
        target_github = dict(project_control.get("github") or {})
        target_github["repository_full_name"] = expected_repository_full_name
        target_control["github"] = target_github
        target_identity = evaluate_project_identity(target_control)
        if target_identity.decision != "ALLOW":
            return target_identity
        return evaluate_project_identity(
            project_control,
            expected_repository_full_name=expected_repository_full_name,
        )
    return decision


def _external_evolution_metadata_attempts_authority(instruction: Mapping[str, Any]) -> bool:
    metadata = instruction.get("evolution_metadata")
    if not isinstance(metadata, Mapping) and instruction.get("classification") in _EXTERNAL_EVOLUTION_CLASSIFICATIONS:
        metadata = instruction
    return (
        isinstance(metadata, Mapping)
        and metadata.get("classification") in _EXTERNAL_EVOLUTION_CLASSIFICATIONS
        and bool(_EXTERNAL_AUTHORITY_FIELDS.intersection(metadata))
    )


def _evaluation_result(
    classification: str,
    reason: str,
    provenance: Mapping[str, Any] | None = None,
    source_framework_version: str | None = None,
) -> dict[str, Any]:
    return {
        "classification": classification,
        "reason": reason,
        "mutated": False,
        "adoption_authorized": False,
        "source_provenance": dict(provenance) if provenance is not None else None,
        "source_framework_version": source_framework_version,
    }


def evaluate_project_evolution(
    project_control: Mapping[str, Any], source: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify a valid Framework source using local facts without adopting it."""
    identity = _project_identity_decision(project_control)
    if identity.decision != "ALLOW":
        return _evaluation_result(identity.reason, identity.reason)
    source_decision = validate_framework_evolution_source(source)
    if source_decision.classification != "READ_ONLY_EVOLUTION_SOURCE":
        return _evaluation_result("FRAMEWORK_SOURCE_INVALID", "FRAMEWORK_SOURCE_INVALID")
    accepted_source = source_decision.source or {}
    compatibility_facts = dict(accepted_source["compatibility_rules"])
    compatibility_facts["evaluated_version"] = accepted_source["framework_version"]
    compatibility = evaluate_framework_compatibility(project_control, compatibility_facts)
    return _evaluation_result(
        compatibility["classification"],
        compatibility["reason"],
        accepted_source["source_provenance"],
        accepted_source["framework_version"],
    )


def validate_framework_adoption(
    project_control: Mapping[str, Any], instruction: Mapping[str, Any], work_unit: Mapping[str, Any], *,
    current_state_revision: int, source: Mapping[str, Any] | None = None,
) -> list[str]:
    identity = _project_identity_decision(project_control, instruction)
    if identity.decision != "ALLOW":
        return [identity.reason]
    if source is not None:
        source_decision = validate_framework_evolution_source(source)
        if source_decision.classification != "READ_ONLY_EVOLUTION_SOURCE":
            return ["FRAMEWORK_SOURCE_INVALID"]
    if _external_evolution_metadata_attempts_authority(instruction):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    if project_control.get("project_id") != work_unit.get("project_id"):
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    if instruction.get("target_work_unit") != work_unit.get("work_unit_id") or work_unit.get("state") != "AUTHORIZED":
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    if instruction.get("expected_state_revision") != work_unit.get("basis_state_revision") or work_unit.get("basis_state_revision") != current_state_revision:
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    executor_role = instruction.get("executor_role")
    authorized_actions = instruction.get("authorized_actions")
    forbidden_actions = instruction.get("forbidden_actions")
    if validate_executor_role(executor_role):
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    if "MUTATE_APPROVED_SCOPE" not in (authorized_actions or []):
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    if validate_action_authority(executor_role, authorized_actions, forbidden_actions):
        return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
    return []


def validate_evidence_project_binding(
    evidence: Mapping[str, Any], project_control: Mapping[str, Any], *, current_state_revision: int | None = None,
) -> list[str]:
    if evidence.get("project_id") != project_control.get("project_id"):
        return ["PROJECT_IDENTITY_INVALID"]
    return []


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA_RE.fullmatch(value))


def _validate_identity(candidate: Mapping[str, Any], context: Mapping[str, Any], field_map: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    for context_key, candidate_key in field_map.items():
        if context_key not in context:
            continue
        expected = context.get(context_key)
        actual = candidate.get(candidate_key)
        if not _is_nonempty_string(expected) or actual != expected:
            errors.extend(["RECONCILIATION_REQUIRED", f"IDENTITY_MISMATCH:{candidate_key}"])
    return errors


def _validate_pairwise_review_policy(
    state: Mapping[str, Any], review_request: Mapping[str, Any], facts: Mapping[str, Any],
) -> list[str]:
    """Fail closed on the durable executor/reviewer pair and its verified facts."""
    slots = state.get("active_execution_slots") if isinstance(state, Mapping) else None
    if not isinstance(slots, list) or not isinstance(review_request, Mapping) or not isinstance(facts, Mapping):
        return ["RECONCILIATION_REQUIRED"]
    context_id, work_unit_id = review_request.get("target_project_context_id"), review_request.get("target_work_unit")
    reviewers = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("role") == "CODEX_REVIEWER" and slot.get("project_context_id") == context_id and slot.get("work_unit_id") == work_unit_id and slot.get("review_request_id") == review_request.get("instruction_id")]
    implementers = [slot for slot in slots if isinstance(slot, Mapping) and slot.get("role") == "CODEX_IMPLEMENTER" and slot.get("project_context_id") == context_id and slot.get("work_unit_id") == work_unit_id]
    if len(reviewers) != 1 or len(implementers) != 1:
        return ["RECONCILIATION_REQUIRED"]
    required = ("implementer_slot_id", "reviewer_slot_id", "canonical_implementer_worktree", "canonical_reviewer_worktree", "implementation_sha", "reviewer_head_sha", "reviewer_tracked_clean")
    if any(key not in facts for key in required):
        return ["RECONCILIATION_REQUIRED"]
    if facts["implementer_slot_id"] != implementers[0].get("slot_id") or facts["reviewer_slot_id"] != reviewers[0].get("slot_id") or facts["implementer_slot_id"] == facts["reviewer_slot_id"] or facts["canonical_implementer_worktree"] == facts["canonical_reviewer_worktree"] or facts["implementation_sha"] != review_request.get("review_target_revision") or facts["reviewer_head_sha"] != review_request.get("review_target_revision") or facts["reviewer_tracked_clean"] is not True:
        return ["RECONCILIATION_REQUIRED"]
    return []


def validate_instruction_authority(
    instruction: Mapping[str, Any],
    current_state_revision: int | None = None,
    approved_scope: set[str] | None = None,
) -> list[str]:
    """Pure fail-closed authority gate for a parsed Instruction Envelope."""

    if not isinstance(instruction, Mapping):
        return ["INVALID_INSTRUCTION"]
    errors: list[str] = []
    type_errors = validate_instruction_type(instruction.get("instruction_type"))
    if type_errors:
        errors.extend(["INVALID_INSTRUCTION", *type_errors])

    instruction_type = instruction.get("instruction_type")
    role_required = instruction_type in _ROLE_AWARE_INSTRUCTION_TYPES

    executor_errors = validate_executor_role(instruction.get("executor_role"))
    if executor_errors:
        errors.extend(["INVALID_INSTRUCTION", *executor_errors])

    issuer = instruction.get("issuer_role")
    return_role = instruction.get("return_role")
    if role_required and issuer is None:
        errors.extend(["INVALID_INSTRUCTION", "ISSUER_ROLE_REQUIRED"])
    if role_required and return_role is None:
        errors.extend(["INVALID_INSTRUCTION", "RETURN_ROLE_REQUIRED"])
    if issuer is not None and (not isinstance(issuer, str) or issuer not in ROLES):
        errors.append("INVALID_INSTRUCTION")
        errors.append("UNKNOWN_ISSUER_ROLE")
    if return_role is not None and (not isinstance(return_role, str) or return_role not in ROLES):
        errors.append("INVALID_INSTRUCTION")
        errors.append("UNKNOWN_RETURN_ROLE")

    executor = instruction.get("executor_role")
    action_errors = validate_action_authority(
        executor,
        instruction.get("authorized_actions"),
        instruction.get("forbidden_actions"),
    ) if not executor_errors else []
    if action_errors:
        errors.append("ROLE_AUTHORITY_CONFLICT")
        errors.extend(action_errors)
    if instruction_type in {"EXECUTION_INSTRUCTION", "REVIEW_REQUEST", "FIX_INSTRUCTION", "APPROVAL_REQUEST", "RECONCILIATION_REQUEST"} and issuer != "GPT_ORCHESTRATOR":
        errors.extend(["ROLE_AUTHORITY_CONFLICT", "ISSUER_NOT_AUTHORIZED"])
    if instruction_type == "FIX_INSTRUCTION":
        if executor != "CODEX_IMPLEMENTER":
            errors.extend(["ROLE_AUTHORITY_CONFLICT", "FIX_EXECUTOR_MUST_BE_CODEX_IMPLEMENTER"])
        if not isinstance(instruction.get("finding_ids"), list) or not instruction.get("finding_ids"):
            errors.append("FINDING_REFERENCE_REQUIRED")
        result_ref = instruction.get("in_response_to_result_id")
        if not isinstance(result_ref, str) or not _UUID_RE.fullmatch(result_ref):
            errors.append("FINDING_RESULT_REFERENCE_REQUIRED")
        if not _is_sha(instruction.get("expected_base_sha")):
            errors.append("REVIEW_BASE_REVISION_REQUIRED")
        if not isinstance(instruction.get("fix_round"), int) or isinstance(instruction.get("fix_round"), bool) or instruction.get("fix_round") < 1:
            errors.append("FIX_ROUND_REQUIRED")
    if instruction_type == "REVIEW_REQUEST" and executor != "CODEX_REVIEWER":
        errors.extend(["ROLE_AUTHORITY_CONFLICT", "REVIEW_EXECUTOR_MUST_BE_CODEX_REVIEWER"])
    authorized_values = instruction.get("authorized_actions")
    if executor == "CODEX_REVIEWER" and isinstance(authorized_values, (list, tuple, set, frozenset)) and any(
        action in _MUTATING_ACTIONS for action in authorized_values
    ):
        errors.extend(["ROLE_AUTHORITY_CONFLICT", "REVIEWER_MUTATION_DENIED"])

    expected_revision = instruction.get("expected_state_revision")
    if current_state_revision is not None and expected_revision is not None and expected_revision != current_state_revision:
        errors.extend(["RECONCILIATION_REQUIRED", "STALE_STATE_REVISION"])

    requested_scope = instruction.get("scope_paths")
    if approved_scope is not None and requested_scope is not None:
        if not isinstance(requested_scope, (list, tuple, set, frozenset)) or not set(requested_scope).issubset(approved_scope):
            errors.extend(["ROLE_AUTHORITY_CONFLICT", "SCOPE_EXPANSION_DENIED"])
    return list(dict.fromkeys(errors))


def validate_review_result(result: Mapping[str, Any]) -> list[str]:
    """Validate result-side review evidence without granting remediation authority."""

    if not isinstance(result, Mapping):
        return ["INVALID_RESULT"]
    errors = validate_result_message_type(result.get("result_message_type"))
    if errors:
        return ["INVALID_RESULT", *errors]
    result_type = result["result_message_type"]
    if result_type in {"REVIEW_RESULT", "REVIEW_FINDING"}:
        if not _is_sha(result.get("review_target_revision")):
            errors.append("REVIEW_TARGET_REVISION_REQUIRED")
        if result_type == "REVIEW_FINDING" and not isinstance(result.get("evidence_refs"), list):
            errors.append("FINDING_EVIDENCE_REQUIRED")
        if result_type == "REVIEW_FINDING" and not result.get("evidence_refs"):
            errors.append("FINDING_EVIDENCE_REQUIRED")
        if result.get("responder_role") != "CODEX_REVIEWER":
            errors.append("ROLE_AUTHORITY_CONFLICT")
            errors.append("REVIEW_RESPONDER_MUST_BE_CODEX_REVIEWER")
        if result.get("mutation_claim") or result.get("authorized_actions") or result.get("fix_instruction"):
            errors.extend(["ROLE_AUTHORITY_CONFLICT", "REVIEWER_MUTATION_DENIED"])
    return list(dict.fromkeys(errors))


def validate_review_lifecycle(
    instruction: Mapping[str, Any] | None,
    finding_result: Mapping[str, Any],
    current_state_revision: int | None = None,
    remediation_decision: str | None = None,
    re_review_result: Mapping[str, Any] | None = None,
    resulting_revision: str | None = None,
    authoritative_review_context: Mapping[str, Any] | None = None,
) -> list[str]:
    """Validate finding evidence, explicit remediation, fix causality, and re-review."""

    if not isinstance(finding_result, Mapping):
        return ["INVALID_RESULT"]
    if instruction is not None and not isinstance(instruction, Mapping):
        return ["INVALID_INSTRUCTION"]
    errors = validate_review_result(finding_result)
    if finding_result.get("result_message_type") != "REVIEW_FINDING":
        return errors
    if instruction is None or instruction.get("instruction_type") != "FIX_INSTRUCTION":
        errors.append("FIX_INSTRUCTION_REQUIRED")
    if not _is_nonempty_string(remediation_decision):
        errors.append("REMEDIATION_DECISION_REQUIRED")
    if authoritative_review_context is not None:
        if not isinstance(authoritative_review_context, Mapping):
            errors.extend(["RECONCILIATION_REQUIRED", "REVIEW_CONTEXT_INVALID"])
        else:
            current_revision = authoritative_review_context.get("reviewed_revision")
            if not _is_sha(current_revision):
                errors.extend(["RECONCILIATION_REQUIRED", "REVIEW_CONTEXT_REVISION_REQUIRED"])
            elif finding_result.get("review_target_revision") != current_revision:
                errors.extend(["RECONCILIATION_REQUIRED", "STALE_REVIEW_REVISION"])
            errors.extend(_validate_identity(
                finding_result,
                authoritative_review_context,
                {
                    "project_context_id": "source_project_context_id",
                    "repository_id": "source_github_repository_id",
                    "repository_full_name": "source_github_repository_full_name",
                    "remote_ref": "current_remote_ref",
                },
            ))
    if instruction is not None and instruction.get("instruction_type") == "FIX_INSTRUCTION":
        errors.extend(validate_instruction_authority(instruction, current_state_revision))
        if instruction.get("in_response_to_result_id") != finding_result.get("result_id"):
            errors.append("FINDING_CORRELATION_REQUIRED")
        if not set(instruction.get("finding_ids") or []).intersection(finding_result.get("finding_ids") or []):
            errors.append("FINDING_CORRELATION_REQUIRED")
        if instruction.get("expected_base_sha") != finding_result.get("review_target_revision"):
            errors.append("REVIEW_TARGET_REVISION_MISMATCH")
        if instruction.get("review_target_revision") is not None and instruction.get("review_target_revision") != finding_result.get("review_target_revision"):
            errors.append("REVIEW_TARGET_REVISION_MISMATCH")
        if instruction.get("fix_round") != (finding_result.get("fix_round") or 0) + 1:
            errors.append("FIX_ROUND_MISMATCH")
        if remediation_decision is not None and instruction.get("remediation_decision_ref") != remediation_decision:
            errors.append("REMEDIATION_DECISION_MISMATCH")
        if instruction.get("executor_role") != "CODEX_IMPLEMENTER":
            errors.append("FIX_EXECUTOR_MUST_BE_CODEX_IMPLEMENTER")
        if authoritative_review_context is not None and isinstance(authoritative_review_context, Mapping):
            errors.extend(_validate_identity(
                instruction,
                authoritative_review_context,
                {
                    "project_context_id": "target_project_context_id",
                    "repository_id": "target_github_repository_id",
                    "repository_full_name": "target_github_repository_full_name",
                    "remote_ref": "expected_remote_ref",
                },
            ))

    if re_review_result is not None:
        errors.extend(validate_review_result(re_review_result))
        if re_review_result.get("result_message_type") not in {"REVIEW_RESULT", "REVIEW_FINDING"}:
            errors.append("REVIEW_RESULT_REQUIRED")
        if resulting_revision is None:
            errors.append("RESULTING_REVISION_REQUIRED")
        elif re_review_result.get("review_target_revision") != resulting_revision:
            errors.append("RE_REVIEW_REVISION_MISMATCH")
        if instruction is not None and re_review_result.get("response_to_instruction_id") != instruction.get("instruction_id"):
            errors.append("RE_REVIEW_INSTRUCTION_CORRELATION_REQUIRED")
        if not set(finding_result.get("evidence_refs") or []).issubset(set(re_review_result.get("evidence_refs") or [])):
            errors.append("ORIGINAL_EVIDENCE_NOT_RETAINED")
    return list(dict.fromkeys(errors))


def validate_pre_execution_review(
    mutation_instruction: Mapping[str, Any],
    review_request: Mapping[str, Any] | None,
    review_result: Mapping[str, Any] | None,
    *,
    current_state_revision: int,
    authoritative_review_context: Mapping[str, Any] | None = None,
) -> list[str]:
    """Compose existing authority checks before a durable mutation may execute."""

    errors = validate_instruction_authority(mutation_instruction, current_state_revision)
    if not isinstance(mutation_instruction, Mapping) or not _UUID_RE.fullmatch(str(mutation_instruction.get("instruction_id", ""))):
        errors.append("INVALID_INSTRUCTION")
    expected_base = mutation_instruction.get("expected_base_sha") if isinstance(mutation_instruction, Mapping) else None
    if not _is_sha(expected_base):
        errors.append("INVALID_INSTRUCTION")
    if review_request is None or review_result is None:
        errors.append("PRE_EXECUTION_REVIEW_REQUIRED")
        return list(dict.fromkeys(errors))

    errors.extend(validate_instruction_authority(review_request, current_state_revision))
    if not isinstance(review_request, Mapping):
        return list(dict.fromkeys(errors))
    if (
        review_request.get("instruction_type") != "REVIEW_REQUEST"
        or review_request.get("issuer_role") != "GPT_ORCHESTRATOR"
        or review_request.get("executor_role") != "CODEX_REVIEWER"
        or review_request.get("return_role") != "GPT_ORCHESTRATOR"
        or review_request.get("in_response_to_instruction_id") != mutation_instruction.get("instruction_id")
    ):
        errors.append("PRE_EXECUTION_REVIEW_REQUEST_CORRELATION_REQUIRED")
    errors.extend(_validate_identity(
        review_request, mutation_instruction,
        {
            "target_project_context_id": "target_project_context_id",
            "target_github_repository_id": "target_github_repository_id",
            "target_github_repository_full_name": "target_github_repository_full_name",
            "target_work_unit": "target_work_unit",
            "expected_remote_ref": "expected_remote_ref",
        },
    ))
    if review_request.get("expected_state_revision") != mutation_instruction.get("expected_state_revision"):
        errors.extend(["RECONCILIATION_REQUIRED", "STALE_STATE_REVISION"])
    if review_request.get("review_target_revision") != expected_base:
        errors.append("PRE_EXECUTION_REVIEW_TARGET_MISMATCH")

    errors.extend(validate_review_result(review_result))
    if not isinstance(review_result, Mapping):
        return list(dict.fromkeys(errors))
    if (
        review_result.get("result_message_type") != "REVIEW_RESULT"
        or review_result.get("responder_role") != "CODEX_REVIEWER"
        or review_result.get("status") != "PASS"
    ):
        errors.append("PRE_EXECUTION_REVIEW_NOT_APPROVED")
    if review_result.get("response_to_instruction_id") != review_request.get("instruction_id"):
        errors.append("PRE_EXECUTION_REVIEW_RESULT_CORRELATION_REQUIRED")
    if review_result.get("review_target_revision") != expected_base:
        errors.append("PRE_EXECUTION_REVIEW_TARGET_MISMATCH")
    if authoritative_review_context is not None:
        if not isinstance(authoritative_review_context, Mapping):
            errors.extend(["RECONCILIATION_REQUIRED", "REVIEW_CONTEXT_INVALID"])
        else:
            if authoritative_review_context.get("reviewed_revision") != expected_base:
                errors.extend(["RECONCILIATION_REQUIRED", "STALE_REVIEW_REVISION"])
            errors.extend(_validate_identity(
                review_result, authoritative_review_context,
                {
                    "project_context_id": "source_project_context_id",
                    "repository_id": "source_github_repository_id",
                    "repository_full_name": "source_github_repository_full_name",
                    "remote_ref": "current_remote_ref",
                },
            ))
            pairwise_state = authoritative_review_context.get("pairwise_state")
            pairwise_facts = authoritative_review_context.get("pairwise_facts")
            if pairwise_state is not None or pairwise_facts is not None:
                errors.extend(_validate_pairwise_review_policy(pairwise_state, review_request, pairwise_facts))
    return list(dict.fromkeys(errors))


def _validate_project_guardrails(project_control: Mapping[str, Any], *, prefix_context_error: bool) -> list[str]:
    """Apply the existing version-aware project Guardrail decisions once."""

    errors: list[str] = []
    raw_extensions = project_control.get("extensions")
    if raw_extensions is None:
        extensions = {}
    elif not isinstance(raw_extensions, Mapping):
        errors.append("RECONCILIATION_REQUIRED")
        extensions = {}
    else:
        extensions = raw_extensions
    raw_framework = project_control.get("framework")
    if raw_framework is None:
        framework = {}
    elif not isinstance(raw_framework, Mapping):
        errors.append("RECONCILIATION_REQUIRED")
        framework = {}
    else:
        framework = raw_framework
    github = project_control.get("github")
    if isinstance(github, Mapping):
        guardrails = extensions.get("guardrails", [])
        repository_guardrails = [
            item for item in guardrails if isinstance(item, Mapping) and item.get("id") == REQUIRED_REPOSITORY_GUARDRAIL
        ] if isinstance(guardrails, list) else []
        if len(repository_guardrails) != 1 or repository_guardrails[0].get("enabled") is not True:
            errors.append("GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled")
    if str(framework.get("adopted_version", "")).startswith("2.1."):
        if not is_valid_project_context_id(project_control.get("project_context_id")):
            reason = "MIGRATION_REQUIRED (PROJECT_CONTEXT_ID_MISSING)"
            errors.append(f"PROJECT_CONTEXT_BINDING: {reason}" if prefix_context_error else reason)
        else:
            decision = required_guardrail_allows(project_control, "project_validation")
            if decision.decision != "ALLOW":
                errors.append(
                    f"PROJECT_CONTEXT_BINDING: {decision.reason}" if prefix_context_error else decision.reason
                )
    return errors


def validate_governed_mutation_entry(
    project_control: Mapping[str, Any],
    state: Mapping[str, Any],
    work_unit: Mapping[str, Any],
    mutation_instruction: Mapping[str, Any],
    review_request: Mapping[str, Any] | None,
    review_result: Mapping[str, Any] | None,
    *,
    current_state_revision: int,
    approved_scope: set[str] | None = None,
    repository_authority: Mapping[str, Any] | None = None,
    repository_root: Path | None = None,
) -> list[str]:
    """One fail-closed entry that composes existing project mutation authorities."""

    errors: list[str] = []
    if not isinstance(project_control, Mapping) or not isinstance(state, Mapping) or not isinstance(work_unit, Mapping):
        return ["RECONCILIATION_REQUIRED"]
    management = project_control.get("framework_management_only") is True
    errors.extend(validate_project_identity_boundary(project_control, consumer=not management))
    identity = _project_identity_decision(project_control, mutation_instruction)
    if identity.decision != "ALLOW":
        errors.append(identity.reason)
    if state.get("project_id") != project_control.get("project_id"):
        errors.extend(["RECONCILIATION_REQUIRED", "PROJECT_IDENTITY_INVALID"])
    if state.get("revision") != current_state_revision:
        errors.extend(["RECONCILIATION_REQUIRED", "STALE_STATE_REVISION"])
    authority_work_unit = work_unit
    policy = project_control.get("execution_policy")
    if policy is not None:
        canonical_work_unit = _resolve_work_unit_at_ref(repository_root, mutation_instruction.get("target_work_unit_ref")) if repository_root is not None else None
        current_head = None
        if repository_root is not None:
            result = subprocess.run(
                ["git", "-C", str(repository_root), "rev-parse", "HEAD"], capture_output=True, text=True,
            )
            if result.returncode == 0 and _is_sha(result.stdout.strip()):
                current_head = result.stdout.strip()
        current_control = _git_json_at_path(repository_root, current_head, ".gpt-codex/CONTROL.json") if current_head is not None else None
        if not isinstance(canonical_work_unit, Mapping) or not isinstance(current_control, Mapping):
            errors.append("RECONCILIATION_REQUIRED")
        else:
            assertion_keys = ("project_id", "work_unit_id", "state", "basis_state_revision", "strategy_profile_id")
            optional_assertion_keys = ("scope", "artifact_refs")
            if (
                current_control.get("execution_policy") != policy
                or any(work_unit.get(key) != canonical_work_unit.get(key) for key in assertion_keys)
                or any(key in work_unit and work_unit.get(key) != canonical_work_unit.get(key) for key in optional_assertion_keys)
            ):
                errors.append("RECONCILIATION_REQUIRED")
            authority_work_unit = canonical_work_unit
        errors.extend(validate_project_strategy_lifecycle(policy, [authority_work_unit]))
        errors.extend(validate_repository_authorization(
            repository_authority, mutation_instruction, authority_work_unit, current_state_revision=current_state_revision,
            repository_root=repository_root, project_control=project_control,
        ))
        baseline = _git_json_at_path(repository_root, mutation_instruction.get("expected_base_sha"), ".gpt-codex/CONTROL.json") if repository_root is not None else None
        baseline_policy = baseline.get("execution_policy") if isinstance(baseline, Mapping) else None
        if not isinstance(baseline_policy, Mapping): errors.append("RECONCILIATION_REQUIRED")
        elif baseline_policy.get("strategy_profile_id") != policy.get("strategy_profile_id"):
            resolved = _resolve_work_unit_at_ref(repository_root, mutation_instruction.get("target_work_unit_ref")) if repository_root is not None else None
            owned = ((resolved.get("scope") or {}).get("owned_paths") if isinstance(resolved, Mapping) else None)
            actions = mutation_instruction.get("authorized_actions") if isinstance(mutation_instruction, Mapping) else None
            if not isinstance(owned, list) or ".gpt-codex/CONTROL.json" not in owned or not isinstance(actions, list) or "MUTATE_APPROVED_SCOPE" not in actions:
                errors.append("RECONCILIATION_REQUIRED")
    errors.extend(validate_framework_adoption(
        project_control, mutation_instruction, authority_work_unit, current_state_revision=current_state_revision,
    ))
    errors.extend(validate_instruction_authority(mutation_instruction, current_state_revision, approved_scope))
    errors.extend(_validate_project_guardrails(project_control, prefix_context_error=False))
    github = project_control.get("github")
    authoritative_review_context = {
        "reviewed_revision": mutation_instruction.get("expected_base_sha") if isinstance(mutation_instruction, Mapping) else None,
        "project_context_id": project_control.get("project_context_id"),
        "repository_id": github.get("repository_id") if isinstance(github, Mapping) else None,
        "repository_full_name": github.get("repository_full_name") if isinstance(github, Mapping) else None,
        "remote_ref": mutation_instruction.get("expected_remote_ref") if isinstance(mutation_instruction, Mapping) else None,
    }
    if state.get("active_execution_slots") is not None:
        if not isinstance(review_request, Mapping) or not isinstance(repository_root, Path):
            errors.append("RECONCILIATION_REQUIRED")
        else:
            from continuity_resume import _derive_pairwise_review_facts
            derived_pairwise_facts = _derive_pairwise_review_facts(
                repository_root, project_control, state, review_request,
            )
            if derived_pairwise_facts.get("reconciliation_required"):
                errors.append("RECONCILIATION_REQUIRED")
            else:
                authoritative_review_context["pairwise_state"] = state
                authoritative_review_context["pairwise_facts"] = derived_pairwise_facts
    errors.extend(validate_pre_execution_review(
        mutation_instruction, review_request, review_result, current_state_revision=current_state_revision,
        authoritative_review_context=authoritative_review_context,
    ))
    return list(dict.fromkeys(errors))


def validate_repository_authorization(
    authority: Mapping[str, Any] | None,
    mutation_instruction: Mapping[str, Any],
    work_unit: Mapping[str, Any],
    *,
    current_state_revision: int,
    repository_root: Path | None = None,
    project_control: Mapping[str, Any] | None = None,
) -> list[str]:
    """Validate existing repository facts without creating an approval authority."""
    deny = ["IMPLEMENTATION_AUTHORIZATION = DENY"]
    if not isinstance(authority, Mapping) or not isinstance(mutation_instruction, Mapping) or not isinstance(work_unit, Mapping) or repository_root is None or not isinstance(project_control, Mapping):
        return deny
    required = {"project_context_id", "work_unit_id", "state_revision", "authorization"}
    optional_assertions = {"accepted_design_ref", "accepted_plan_ref"}
    if not required.issubset(authority) or not set(authority).issubset(required | optional_assertions) or any(not _is_nonempty_string(authority.get(key)) for key in ("project_context_id", "work_unit_id")):
        return deny
    authorization = authority.get("authorization")
    if not isinstance(authorization, Mapping) or set(authorization) != {"authority_type", "instruction_id", "status", "target_revision"}:
        return deny
    resolved = _resolve_work_unit_at_ref(repository_root, mutation_instruction.get("target_work_unit_ref"))
    if not isinstance(resolved, Mapping): return deny
    refs = resolved.get("artifact_refs")
    if not isinstance(refs, Mapping): return deny
    expected_design = _artifact_ref_text(refs.get("design")); expected_plan = _artifact_ref_text(refs.get("plan"))
    if (
        authorization.get("authority_type") not in {"INSTRUCTION", "RESULT", "EVIDENCE"}
        or authorization.get("status") != "EXECUTION_AUTHORIZED"
        or authority.get("project_context_id") != mutation_instruction.get("target_project_context_id")
        or authority.get("work_unit_id") != work_unit.get("work_unit_id")
        or authority.get("state_revision") != current_state_revision
        or authorization.get("instruction_id") != mutation_instruction.get("instruction_id")
        or authorization.get("target_revision") != mutation_instruction.get("expected_base_sha")
        or ("accepted_design_ref" in authority and authority.get("accepted_design_ref") != expected_design)
        or ("accepted_plan_ref" in authority and authority.get("accepted_plan_ref") != expected_plan)
        or resolved.get("work_unit_id") != mutation_instruction.get("target_work_unit")
        or resolved.get("project_id") != project_control.get("project_id")
        or resolved.get("state") != "AUTHORIZED"
        or resolved.get("basis_state_revision") != current_state_revision
        or not _immutable_artifact_refs_resolve(repository_root, resolved.get("artifact_refs"))
    ):
        return deny
    return []

def _artifact_ref_text(ref: object) -> str | None:
    if not isinstance(ref, Mapping) or set(ref) != {"path", "sha"}: return None
    path, sha = ref.get("path"), ref.get("sha")
    return f"{path}@{sha}" if isinstance(path, str) and _is_sha(sha) else None

def _resolve_work_unit_at_ref(root: Path, reference: object) -> Mapping[str, Any] | None:
    if not isinstance(reference, Mapping) or set(reference) != {"path", "sha"}: return None
    path, sha = reference.get("path"), reference.get("sha")
    if not isinstance(path, str) or not _is_safe_repository_relative_path(path) or not _is_sha(sha): return None
    return _git_json_at_path(root, sha, path)

def _git_json_at_path(root: Path, sha: object, path: object) -> Mapping[str, Any] | None:
    if not isinstance(root, Path) or not _is_sha(sha) or not isinstance(path, str) or not _is_safe_repository_relative_path(path): return None
    result = subprocess.run(["git", "-C", str(root), "show", f"{sha}:{path}"], capture_output=True)
    if result.returncode: return None
    try: value=json.loads(result.stdout)
    except json.JSONDecodeError: return None
    return value if isinstance(value, Mapping) else None

def _immutable_artifact_refs_resolve(root: Path, refs: object) -> bool:
    if not isinstance(refs, Mapping) or set(refs) != {"design", "plan"}: return False
    for ref in refs.values():
        if not isinstance(ref, Mapping) or set(ref) != {"path", "sha"}: return False
        path, sha=ref.get("path"), ref.get("sha")
        if not isinstance(path, str) or not _is_safe_repository_relative_path(path) or not _is_sha(sha): return False
        if subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{sha}:{path}"], capture_output=True).returncode: return False
    return True


def validate_result_protocol(result: Mapping[str, Any]) -> list[str]:
    """Apply protocol result checks only to envelopes opting into result classification."""

    if "result_message_type" not in result:
        return []
    return validate_review_result(result)


def _cataloged_builtin(kind: str, extension_id: str) -> tuple[bool, str]:
    catalog_path = FRAMEWORK_ROOT / '.gpt-codex' / 'builtins' / 'INDEX.json'
    try:
        catalog = load(catalog_path)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f'Framework Built-in catalog unavailable: {exc}'
    bucket = None
    for candidate in ('required', 'optional'):
        if extension_id in (catalog.get(candidate) or {}).get(kind, []):
            bucket = candidate
            break
    if bucket is None:
        return False, f'Builtin {kind}/{extension_id} is not present in Framework catalog'
    manifest_path = FRAMEWORK_ROOT / '.gpt-codex' / 'builtins' / kind / extension_id / 'manifest.json'
    try:
        manifest = load(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f'Builtin {kind}/{extension_id} manifest unavailable: {exc}'
    expected_kind = {'skills': 'SKILL', 'guardrails': 'GUARDRAIL', 'fitness': 'FITNESS'}[kind]
    manifest_errors = check_common_version(manifest)
    if manifest.get('id') != extension_id:
        manifest_errors.append('manifest id mismatch')
    if manifest.get('kind') != expected_kind:
        manifest_errors.append(f'manifest kind must be {expected_kind}')
    if manifest.get('maturity') != 'BUILTIN':
        manifest_errors.append('manifest maturity must be BUILTIN')
    if manifest_errors:
        return False, f'Builtin {kind}/{extension_id} invalid: {", ".join(manifest_errors)}'
    return True, ''


def load(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def _matches_json_type(value, expected_type: str) -> bool:
    if expected_type == 'object':
        return isinstance(value, dict)
    if expected_type == 'array':
        return isinstance(value, list)
    if expected_type == 'string':
        return isinstance(value, str)
    if expected_type == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == 'boolean':
        return isinstance(value, bool)
    if expected_type == 'null':
        return value is None
    return True


def _schema_shape_errors(value, schema: dict, path: str = '$') -> list[str]:
    errors = []
    expected = schema.get('type')
    expected_types = expected if isinstance(expected, list) else [expected]
    if expected and not any(_matches_json_type(value, item) for item in expected_types):
        return [f'{path} must be {" or ".join(expected_types)}']
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path} must equal {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path} must be one of {schema["enum"]!r}')
    if isinstance(value, str) and 'pattern' in schema:
        try:
            if re.search(schema['pattern'], value) is None:
                errors.append(f'{path} does not match required pattern')
        except re.error:
            errors.append(f'{path} has unsupported schema pattern')
    if isinstance(value, str) and schema.get('format') == 'uuid':
        try:
            uuid.UUID(value)
        except (ValueError, AttributeError, TypeError):
            errors.append(f'{path} must be a UUID')
    if isinstance(value, str) and 'minLength' in schema and len(value) < schema['minLength']:
        errors.append(f'{path} must not be empty')
    if isinstance(value, (int, float)) and not isinstance(value, bool) and 'minimum' in schema and value < schema['minimum']:
        errors.append(f'{path} must be at least {schema["minimum"]}')
    if isinstance(value, dict):
        properties = schema.get('properties') or {}
        for required in schema.get('required') or []:
            if required not in value:
                errors.append(f'{path}.{required} is required')
        if schema.get('additionalProperties') is False:
            for key in value:
                if key not in properties:
                    errors.append(f'{path}.{key} is not allowed')
        for key, child_schema in properties.items():
            if key in value:
                errors += _schema_shape_errors(value[key], child_schema, f'{path}.{key}')
    if isinstance(value, list) and schema.get('items'):
        for index, item in enumerate(value):
            errors += _schema_shape_errors(item, schema['items'], f'{path}[{index}]')
    if isinstance(value, list) and 'maxItems' in schema and len(value) > schema['maxItems']:
        errors.append(f'{path} has too many items')
    if isinstance(value, list) and 'minItems' in schema and len(value) < schema['minItems']:
        errors.append(f'{path} has too few items')
    if isinstance(value, list) and schema.get('uniqueItems'):
        serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
        if len(serialized) != len(set(serialized)):
            errors.append(f'{path} must contain unique items')
    if 'not' in schema and not _schema_shape_errors(value, schema['not'], path):
        errors.append(f'{path} matches a forbidden schema')
    for branch in schema.get('allOf') or []:
        if not isinstance(branch, dict):
            continue
        if 'if' in branch:
            condition_matches = not _schema_shape_errors(value, branch['if'], path)
            selected = branch.get('then') if condition_matches else branch.get('else')
            if isinstance(selected, dict):
                errors += _schema_shape_errors(value, selected, path)
        else:
            errors += _schema_shape_errors(value, branch, path)
    return errors


def _derived_schema_errors(payload: dict, schema_name: str) -> list[str]:
    schema_path = FRAMEWORK_ROOT / '.gpt-codex' / 'schemas' / f'{schema_name}.schema.json'
    try:
        schema = load(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f'{schema_name.upper().replace("-", "_")}_SCHEMA_UNAVAILABLE:{exc}']
    return [
        f'{schema_name.upper().replace("-", "_")}_SCHEMA_INVALID:{error}'
        for error in _schema_shape_errors(payload, schema)
    ]


def validate_instruction_envelope_contract(instruction: Mapping[str, Any]) -> list[str]:
    """Validate an already-built Instruction Envelope against its authoritative schema."""
    if not isinstance(instruction, Mapping):
        return ['INSTRUCTION_ENVELOPE_SCHEMA_INVALID:$ must be object']
    return _derived_schema_errors(dict(instruction), 'instruction-envelope')


def validate_result_envelope_contract(result: Mapping[str, Any]) -> list[str]:
    """Validate an already-built Result Envelope against its authoritative schema."""
    if not isinstance(result, Mapping):
        return ['RESULT_ENVELOPE_SCHEMA_INVALID:$ must be object']
    return _derived_schema_errors(dict(result), 'result-envelope')


def validate_optional_navigation_and_resume(root: Path, gov: Path, control: dict) -> list[str]:
    errors = []
    try:
        project_map = load_project_map(root)
    except ValueError as exc:
        errors.append(str(exc))
        project_map = None
    except TypeError:
        errors.append('NAVIGATION_INVALID_SHAPE')
        project_map = None
    if project_map is not None:
        errors += _derived_schema_errors(project_map, 'project-map')
        try:
            validate_navigation_identity(project_map, control)
        except ValueError as exc:
            errors.append(str(exc))
        for module in project_map.get('modules', []):
            if not isinstance(module, dict):
                errors.append('NAVIGATION_MODULE_INVALID')
                continue
            module_id = module.get('id')
            module_map_path = module.get('module_map')
            if not isinstance(module_map_path, str):
                errors.append('MODULE_MAP_PATH_INVALID')
                continue
            supplied_path = Path(module_map_path)
            if (
                supplied_path.is_absolute()
                or '..' in supplied_path.parts
                or supplied_path.suffix.lower() != '.json'
            ):
                errors.append(f'MODULE_MAP_PATH_INVALID:{module_map_path}')
                continue
            module_map_file = root / supplied_path
            if not module_map_file.exists():
                continue
            try:
                module_map = load_module_map(root, module_map_path)
                errors += _derived_schema_errors(module_map, 'module-map')
                validate_navigation_identity(module_map, control)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if module_map.get('module_id') != module_id:
                errors.append('MODULE_MAP_ID_MISMATCH')
    try:
        checkpoint = load_resume_checkpoint(gov)
    except ValueError as exc:
        errors.append(str(exc))
        checkpoint = None
    if checkpoint is not None:
        errors += _derived_schema_errors(checkpoint, 'resume')
        try:
            validate_navigation_identity(checkpoint, control)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def _git_state_bytes(root: Path, revision: str) -> bytes | None:
    result = subprocess.run(
        ['git', '-C', str(root), 'show', f'{revision}:.gpt-codex/STATE.json'],
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def _authoritative_previous_state(root: Path, state_path: Path, current_state: Mapping) -> Mapping:
    current_bytes = state_path.read_bytes()
    head_state_bytes = _git_state_bytes(root, 'HEAD')
    if head_state_bytes is None:
        raise ValueError('AUTHORITATIVE_STATE_HISTORY_REQUIRED')
    if head_state_bytes != current_bytes:
        raise ValueError('AUTHORITATIVE_STATE_CURRENT_MISMATCH')
    current_revision = current_state.get('revision')
    if not isinstance(current_revision, int) or isinstance(current_revision, bool) or current_revision <= 0:
        raise ValueError('AUTHORITATIVE_STATE_HISTORY_REQUIRED')
    history = subprocess.run(
        ['git', '-C', str(root), 'rev-list', '--first-parent', 'HEAD^'],
        capture_output=True,
        text=True,
    )
    if history.returncode != 0:
        raise ValueError('AUTHORITATIVE_STATE_HISTORY_REQUIRED')
    for revision in history.stdout.splitlines():
        state_bytes = _git_state_bytes(root, revision)
        if state_bytes is None:
            continue
        try:
            candidate = json.loads(state_bytes)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(candidate, Mapping)
            and candidate.get('project_id') == current_state.get('project_id')
            and candidate.get('revision') == current_revision - 1
        ):
            return candidate
    raise ValueError('AUTHORITATIVE_STATE_HISTORY_REQUIRED')


def main():
    ap = argparse.ArgumentParser(description='Validate GPT-Codex v2 project governance mechanically.')
    ap.add_argument('project_root', type=Path)
    args = ap.parse_args()
    root = args.project_root.resolve()
    gov = root / '.gpt-codex'
    control_p = gov / 'CONTROL.json'
    state_p = gov / 'STATE.json'
    errors = []
    errors += validate_project_evolution_orchestration()
    for p in (control_p, state_p):
        if not p.exists():
            errors.append(f'missing {p}')
    if errors:
        print('\n'.join('FAIL: '+e for e in errors)); return 1
    try:
        control, state = load(control_p), load(state_p)
    except Exception as e:
        print(f'FAIL: invalid JSON: {e}'); return 1
    errors += [f'CONTROL: {e}' for e in check_common_version(control)]
    errors += [f'STATE: {e}' for e in check_common_version(state)]
    if control.get('project_id') != state.get('project_id'):
        errors.append('project_id mismatch between CONTROL and STATE')
    if state.get('state') not in STATES:
        errors.append('invalid STATE.state')
    if not isinstance(state.get('revision'), int) or state.get('revision') < 0:
        errors.append('STATE.revision must be a non-negative integer')
    errors += [f'STATE: {error}' for error in validate_execution_slots(state)]
    execution_slots = state.get('active_execution_slots')
    if isinstance(execution_slots, list) and execution_slots:
        try:
            previous_state = _authoritative_previous_state(root, state_p, state)
        except OSError:
            errors.extend(['STATE: AUTHORITATIVE_STATE_HISTORY_REQUIRED', 'STATE: RECONCILIATION_REQUIRED'])
        except ValueError as exc:
            errors.extend([f'STATE: {exc}', 'STATE: RECONCILIATION_REQUIRED'])
        else:
            previous_state_errors = (
                check_common_version(previous_state)
                + validate_execution_slots(previous_state)
            )
            if previous_state_errors:
                errors.extend(['STATE: AUTHORITATIVE_PREVIOUS_STATE_INVALID', 'STATE: RECONCILIATION_REQUIRED'])
            else:
                previous_revision = previous_state.get('revision')
                current_revision = state.get('revision')
                if (
                    previous_state.get('project_id') != state.get('project_id')
                    or not isinstance(previous_revision, int)
                    or isinstance(previous_revision, bool)
                    or validate_slot_state_revision(current_revision, previous_revision + 1)
                ):
                    errors.extend(['STATE: AUTHORITATIVE_PREVIOUS_STATE_MISMATCH', 'STATE: RECONCILIATION_REQUIRED'])
                else:
                    previous_slots = previous_state.get('active_execution_slots')
                    previous_by_slot_id = {}
                    if isinstance(previous_slots, list):
                        previous_by_slot_id = {
                            slot.get('slot_id'): slot
                            for slot in previous_slots
                            if isinstance(slot, Mapping) and isinstance(slot.get('slot_id'), str)
                        }
                    for slot in execution_slots:
                        if not isinstance(slot, Mapping):
                            continue
                        previous_slot = previous_by_slot_id.get(slot.get('slot_id'))
                        if previous_slot is None:
                            errors.extend(['STATE: AUTHORITATIVE_PREVIOUS_SLOT_REQUIRED', 'STATE: RECONCILIATION_REQUIRED'])
                            continue
                        errors += [
                            f'STATE: {error}'
                            for error in validate_slot_transition(previous_slot, slot)
                        ]
    fw = control.get('framework') or {}
    if fw.get('evaluation_result') not in COMPAT_RESULTS:
        errors.append('invalid framework evaluation_result')
    management_project = control.get('framework_management_only') is True
    errors += validate_project_identity_boundary(control, consumer=not management_project)
    errors += validate_execution_policy(control.get("execution_policy"))
    errors += validate_harness_root_separation(control)
    if control.get('governance_profile') not in GOVERNANCE_PROFILES and not (management_project and control.get('governance_profile') == 'FRAMEWORK_MANAGEMENT'):
        errors.append('invalid governance_profile')
    github = control.get('github')
    if github is not None:
        if not isinstance(github, dict) or set(github) != {'repository_id', 'repository_full_name', 'default_branch'}:
            errors.append('GITHUB_REPOSITORY_BINDING: exactly repository_id, repository_full_name, default_branch are required')
        elif not all(isinstance(github.get(key), str) and github.get(key).strip() for key in ('repository_id', 'repository_full_name', 'default_branch')):
            errors.append('GITHUB_REPOSITORY_BINDING: fields must be non-empty strings')
    continuity = state.get('continuity')
    if continuity is not None:
        required_continuity = {'current_remote_ref', 'latest_verified_remote_sha', 'latest_synced_state_revision', 'last_verified_result_ref', 'sync_status'}
        if not isinstance(continuity, dict) or not required_continuity.issubset(continuity):
            errors.append('STATE.continuity: incomplete continuity facts')
        elif continuity.get('sync_status') not in {'SYNCED', 'SYNC_PENDING', 'RECONCILIATION_REQUIRED'}:
            errors.append('STATE.continuity: invalid sync_status')
    errors.extend(_validate_project_guardrails(control, prefix_context_error=True))
    roots = control.get('roots') or {}
    roots_valid = (
        roots.get('project_role') == 'AUTHORITATIVE' and roots.get('framework_role') == 'ADVISORY'
    ) or (
        management_project and roots.get('project_role') == 'AUTHORITATIVE' and roots.get('framework_role') == 'SELF_MANAGED'
    )
    if not roots_valid:
        errors.append('dual-root authority must be project=AUTHORITATIVE/framework=ADVISORY')
    if roots.get('framework_kernel_access') != 'READ_ONLY' or roots.get('framework_builtins_access') != 'READ_ONLY':
        errors.append('framework Kernel/Built-ins must be READ_ONLY during ordinary project operation')
    ids = set()
    for kind in ('skills','guardrails','fitness'):
        for item in (control.get('extensions') or {}).get(kind, []):
            iid = item.get('id')
            if not iid:
                errors.append(f'{kind} contains extension without id')
            elif iid in ids:
                errors.append(f'duplicate extension id: {iid}')
            ids.add(iid)
            if item.get('enabled'):
                installed = item.get('installed_path')
                if not installed:
                    if not (management_project and item.get('source') == 'builtin'):
                        errors.append(f'{kind}/{iid}: enabled extension missing installed_path')
                    else:
                        valid_builtin, reason = _cataloged_builtin(kind, iid)
                        if not valid_builtin:
                            errors.append(f'{kind}/{iid}: {reason}')
                elif installed:
                    ip = root / installed
                    if not ip.exists():
                        errors.append(f'{kind}/{iid}: installed_path does not exist: {installed}')
                if item.get('source') == 'builtin' and installed:
                    valid_builtin, reason = _cataloged_builtin(kind, iid)
                    if not valid_builtin:
                        errors.append(f'{kind}/{iid}: {reason}')
    if state.get('state') == 'COMPLETE' and not state.get('evidence_refs'):
        errors.append('COMPLETE state requires durable evidence_refs')
    durable_results = {}
    for ref in set((state.get('evidence_refs') or []) + [((state.get('continuity') or {}).get('last_verified_result_ref'))]):
        if not ref:
            continue
        result_path = root / ref
        if not result_path.is_file():
            continue
        try:
            candidate = load(result_path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(candidate, dict) and 'status' in candidate:
            durable_results[ref] = candidate
            errors += [f'RESULT {ref}: {error}' for error in validate_result_authority(candidate)]
            errors += [f'RESULT_PROTOCOL {ref}: {error}' for error in validate_result_protocol(candidate)]
            if 'source_project_context_id' in candidate:
                decision = evaluate_return(
                    candidate,
                    control.get('project_context_id'),
                    None,
                    project_control=control,
                    local_repository_id=(control.get('github') or {}).get('repository_id'),
                )
                if decision.decision != 'ALLOW':
                    errors.append(f'RESULT {ref}: {decision.reason}')
        elif isinstance(candidate, dict) and 'evidence_id' in candidate:
            errors += [
                f'EVIDENCE {ref}: {error}'
                for error in validate_evidence_project_binding(
                    candidate, control, current_state_revision=state.get('revision'),
                )
            ]
    errors += [f'STATE: {error}' for error in validate_state_authority(state, durable_results)]
    errors += validate_project_identity_and_derived(root, gov, control)
    # Validate project-local contracts if present.
    ext_root = gov / 'extensions'
    if ext_root.exists():
        for p in ext_root.rglob('*.json'):
            try: ext = load(p)
            except Exception as e:
                errors.append(f'{p}: invalid JSON: {e}'); continue
            errors += [f'{p}: {e}' for e in check_common_version(ext)]
            if ext.get('kind') not in EXTENSION_KINDS: errors.append(f'{p}: invalid kind')
            if ext.get('maturity') not in MATURITY: errors.append(f'{p}: invalid maturity')
            if not project_extension_has_provenance(ext): errors.append(f'{p}: project-local extension lacks required provenance/evidence/retirement')
    if errors:
        for e in errors: print('FAIL:', e)
        print(f'RESULT: FAIL ({len(errors)} errors)')
        return 1
    print('RESULT: PASS')
    print(f'PROJECT: {control.get("project_id")}')
    print(f'STATE: {state.get("state")}@revision-{state.get("revision")}')
    print('PROJECT_CONTEXT_BINDING: PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
