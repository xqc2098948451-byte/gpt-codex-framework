#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from kernel_rules import *
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
    if isinstance(value, str) and 'minLength' in schema and len(value) < schema['minLength']:
        errors.append(f'{path} must not be empty')
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


def main():
    ap = argparse.ArgumentParser(description='Validate GPT-Codex v2 project governance mechanically.')
    ap.add_argument('project_root', type=Path)
    ap.add_argument(
        '--previous-state',
        type=Path,
        help='authoritative STATE snapshot immediately preceding the current STATE revision',
    )
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
    previous_state = None
    if args.previous_state is not None:
        try:
            previous_state = load(args.previous_state)
        except Exception:
            errors.extend(['STATE: PREVIOUS_STATE_INVALID', 'STATE: RECONCILIATION_REQUIRED'])
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
        if previous_state is None:
            errors.extend(['STATE: PREVIOUS_STATE_REQUIRED', 'STATE: RECONCILIATION_REQUIRED'])
        elif not isinstance(previous_state, Mapping):
            errors.extend(['STATE: PREVIOUS_STATE_INVALID', 'STATE: RECONCILIATION_REQUIRED'])
        else:
            previous_state_errors = (
                check_common_version(previous_state)
                + validate_execution_slots(previous_state)
            )
            if previous_state_errors:
                errors.extend(['STATE: PREVIOUS_STATE_INVALID', 'STATE: RECONCILIATION_REQUIRED'])
            previous_revision = previous_state.get('revision')
            current_revision = state.get('revision')
            if (
                previous_state.get('project_id') != state.get('project_id')
                or not isinstance(previous_revision, int)
                or isinstance(previous_revision, bool)
                or validate_slot_state_revision(current_revision, previous_revision + 1)
            ):
                errors.extend(['STATE: PREVIOUS_STATE_MISMATCH', 'STATE: RECONCILIATION_REQUIRED'])
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
                    errors.extend(['STATE: PREVIOUS_SLOT_REQUIRED', 'STATE: RECONCILIATION_REQUIRED'])
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
    if control.get('governance_profile') not in GOVERNANCE_PROFILES and not (management_project and control.get('governance_profile') == 'FRAMEWORK_MANAGEMENT'):
        errors.append('invalid governance_profile')
    github = control.get('github')
    if github is not None:
        if not isinstance(github, dict) or set(github) != {'repository_id', 'repository_full_name', 'default_branch'}:
            errors.append('GITHUB_REPOSITORY_BINDING: exactly repository_id, repository_full_name, default_branch are required')
        elif not all(isinstance(github.get(key), str) and github.get(key).strip() for key in ('repository_id', 'repository_full_name', 'default_branch')):
            errors.append('GITHUB_REPOSITORY_BINDING: fields must be non-empty strings')
        repository_guardrails = [item for item in (control.get('extensions') or {}).get('guardrails', []) if item.get('id') == REQUIRED_REPOSITORY_GUARDRAIL]
        if len(repository_guardrails) != 1 or not repository_guardrails[0].get('enabled'):
            errors.append('GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled')
    continuity = state.get('continuity')
    if continuity is not None:
        required_continuity = {'current_remote_ref', 'latest_verified_remote_sha', 'latest_synced_state_revision', 'last_verified_result_ref', 'sync_status'}
        if not isinstance(continuity, dict) or not required_continuity.issubset(continuity):
            errors.append('STATE.continuity: incomplete continuity facts')
        elif continuity.get('sync_status') not in {'SYNCED', 'SYNC_PENDING', 'RECONCILIATION_REQUIRED'}:
            errors.append('STATE.continuity: invalid sync_status')
    project_context_id = control.get('project_context_id')
    if str(fw.get('adopted_version', '')).startswith('2.1.'):
        if not is_valid_project_context_id(project_context_id):
            errors.append('PROJECT_CONTEXT_BINDING: MIGRATION_REQUIRED (PROJECT_CONTEXT_ID_MISSING)')
        else:
            binding = required_guardrail_allows(control, 'project_validation')
            if binding.decision != 'ALLOW':
                errors.append(f'PROJECT_CONTEXT_BINDING: {binding.reason}')
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
