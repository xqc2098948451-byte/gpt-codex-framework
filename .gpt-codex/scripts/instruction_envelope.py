from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path
import re
import sys
from typing import Any
from uuid import uuid4
from uuid import UUID


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
_ROLE_INPUT_ALLOWLISTS = {
    "CODEX_IMPLEMENTER": frozenset({"DURABLE_PROJECT_AUTHORITY", "GOVERNED_ARTIFACT", "GOVERNED_INSTRUCTION", "REPOSITORY_CONTENT", "VERIFICATION_EVIDENCE"}),
    "CODEX_REVIEWER": frozenset({"DURABLE_PROJECT_AUTHORITY", "GOVERNED_ARTIFACT", "GOVERNED_INSTRUCTION", "REPOSITORY_CONTENT", "VERIFICATION_EVIDENCE", "ACCEPTED_FINDING"}),
}


def _validate_role_input_sources(executor_role: object, input_source_kinds: object) -> list[str]:
    """Fail closed for runtime dispatcher inputs outside the role allowlist."""
    allowed = _ROLE_INPUT_ALLOWLISTS.get(executor_role)
    if allowed is None or not isinstance(input_source_kinds, (list, tuple)):
        return ["ROLE_DISPATCH = BLOCKED"]
    if any(not isinstance(kind, str) or kind not in allowed for kind in input_source_kinds):
        return ["ROLE_DISPATCH = BLOCKED"]
    return []


def validate_instruction_evolution_metadata(metadata: Mapping[str, Any] | None) -> list[str]:
    return validate_evolution_metadata_authority(metadata)
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_INSTRUCTION_SEMVER_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-(?:(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?(?:\+(?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")


def _value(value: Any) -> str:
    if value is None or value == "":
        return "NONE"
    return str(value)


def instruction_artifact_relative_path(instruction_id: str) -> str:
    """Return the sole project Evidence location for an Instruction ID."""
    try:
        parsed = UUID(instruction_id)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("INSTRUCTION_ID_INVALID") from exc
    if str(parsed) != instruction_id:
        raise ValueError("INSTRUCTION_ID_INVALID")
    return f".gpt-codex/evidence/instructions/{instruction_id}.json"


def canonical_instruction_bytes(envelope: Mapping[str, Any]) -> bytes:
    if not isinstance(envelope, Mapping):
        raise ValueError("INSTRUCTION_ENVELOPE_INVALID")
    return (json.dumps(dict(envelope), ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def build_pre_execution_review_request(
    mutation_instruction: Mapping[str, Any], *, current_state_revision: int,
    approved_scope: set[str], runtime_fresh_context_verified: bool,
    runtime_input_source_kinds: list[str], instruction_id: str | None = None,
) -> dict[str, Any]:
    """Construct a candidate request; no review judgment or execution authority."""
    from validate_project import (validate_instruction_authority,
        validate_instruction_envelope_contract, validate_pre_execution_review_request)
    errors = validate_instruction_envelope_contract(mutation_instruction)
    errors += validate_instruction_authority(mutation_instruction, current_state_revision, approved_scope)
    if errors:
        raise ValueError("REQUEST_CONSTRUCTION_BLOCKED:" + ",".join(dict.fromkeys(errors)))
    value = dict(mutation_instruction)
    value.update(instruction_id=instruction_id or str(uuid4()), instruction_type="REVIEW_REQUEST",
        issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_REVIEWER", return_role="GPT_ORCHESTRATOR",
        authorized_actions=["READ", "TEST", "VALIDATE", "REPORT"],
        forbidden_actions=["MUTATE_APPROVED_SCOPE", "COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION"],
        in_response_to_instruction_id=mutation_instruction["instruction_id"],
        review_target_revision=mutation_instruction.get("expected_base_sha"))
    # Approval locators are exclusive to their originating reconciliation request.
    value.pop("approval_evidence_ref", None)
    if runtime_fresh_context_verified is not True or _validate_role_input_sources("CODEX_REVIEWER", runtime_input_source_kinds):
        raise ValueError("REQUEST_CONSTRUCTION_BLOCKED:ROLE_DISPATCH = BLOCKED")
    errors = validate_instruction_envelope_contract(value)
    errors += validate_pre_execution_review_request(mutation_instruction, value, current_state_revision=current_state_revision)
    if errors:
        raise ValueError("REQUEST_CONSTRUCTION_BLOCKED:" + ",".join(dict.fromkeys(errors)))
    return value


def build_work_unit_candidate(
    root: Path, semantic_decision: Mapping[str, Any], *, predecessor_ref: Mapping[str, str],
    expected_state_revision: int, expected_head_sha: str, approved_scope: set[str],
) -> dict[str, Any]:
    """Generate bytes locally; callers govern materialization and publication."""
    import hashlib
    from copy import deepcopy
    from validate_project import _resolve_work_unit_at_ref, _schema_shape_errors, _scope_covers
    root = Path(root)
    control = json.loads((root / ".gpt-codex/CONTROL.json").read_text(encoding="utf-8"))
    state = json.loads((root / ".gpt-codex/STATE.json").read_text(encoding="utf-8"))
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if state.get("revision") != expected_state_revision:
        raise ValueError("STALE_STATE_REVISION")
    if head != expected_head_sha or state.get("project_id") != control.get("project_id"):
        raise ValueError("RECONCILIATION_REQUIRED")
    predecessor = _resolve_work_unit_at_ref(root, predecessor_ref)
    if not isinstance(predecessor, Mapping) or predecessor.get("project_id") != control.get("project_id"):
        raise ValueError("WORK_UNIT_PREDECESSOR_UNRESOLVED")
    allowed = {"work_unit_id", "goal", "scope", "acceptance", "evidence_refs", "directory_creations", "artifact_refs"}
    if not isinstance(semantic_decision, Mapping) or set(semantic_decision) - allowed:
        raise ValueError("WORK_UNIT_CANDIDATE_INVALID")
    value = deepcopy(dict(predecessor))
    value.update(deepcopy(dict(semantic_decision)))
    scope = value.get("scope", {})
    owned = scope.get("owned_paths", []) if isinstance(scope, Mapping) else []
    excluded = set(scope.get("excluded_paths", [])) if isinstance(scope, Mapping) else set()
    if not owned or not all(_scope_covers(path, approved_scope, excluded) for path in owned):
        raise ValueError("SCOPE_EXPANSION_DENIED")
    value.update(project_id=control["project_id"], project_context_id=control["project_context_id"],
        basis_state_revision=state["revision"], state="DRAFT",
        implementation_authorized=False, implementation_start_allowed=False,
        next_gate="EXPLICIT_AUTHORIZATION_REQUIRED",
        authorization={"authority_type": "CANDIDATE_ONLY", "implementation_authorized": False,
                       "implementation_start_allowed": False, "next_gate": "EXPLICIT_AUTHORIZATION_REQUIRED"},
        permissions={"authorized_actions": ["READ", "VALIDATE", "REPORT"],
                     "forbidden_actions": ["MUTATE_APPROVED_SCOPE", "COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION"]})
    # Never carry the predecessor's approvals or runtime identity as successor authority.
    for key in ("user_local_proxy", "authority_source_ref", "bootstrap_exception_ref"):
        value.pop(key, None)
    schema = json.loads((HERE.parent / "schemas/work-unit.schema.json").read_text(encoding="utf-8"))
    errors = _schema_shape_errors(value, schema)
    if errors:
        raise ValueError("WORK_UNIT_CANDIDATE_INVALID:" + ",".join(errors))
    data = canonical_instruction_bytes(value)
    return {"work_unit": value, "bytes": data, "byte_count": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest(),
            "authority": "CANDIDATE_ONLY"}


def build_fix_instruction(
    mutation_template: Mapping[str, Any], finding_result: Mapping[str, Any],
    decision: Mapping[str, Any], resolved_basis: Mapping[str, Mapping[str, Any]], *,
    current_state_revision: int, approved_scope: set[str], repository_root: Path | None = None,
) -> dict[str, Any]:
    """Correlate an explicit decision; Finding alone never permits a fix."""
    from validate_project import (validate_remediation_adjudication, validate_instruction_authority,
        validate_instruction_envelope_contract, validate_review_lifecycle)
    errors = validate_remediation_adjudication(decision, finding_result, resolved_basis)
    if decision.get("adjudicated_at_revision") != current_state_revision:
        errors.append("REMEDIATION_BASIS_STALE")
    if errors:
        raise ValueError(",".join(dict.fromkeys(errors)))
    value = dict(mutation_template)
    value.update(instruction_id=str(uuid4()), instruction_type="FIX_INSTRUCTION",
        in_response_to_result_id=finding_result.get("result_id"), finding_ids=list(finding_result.get("finding_ids", [])),
        remediation_decision_ref=decision.get("evidence_id"), fix_round=(finding_result.get("fix_round") or 0) + 1,
        review_target_revision=finding_result.get("review_target_revision"))
    errors = validate_instruction_envelope_contract(value)
    errors += validate_instruction_authority(value, current_state_revision, approved_scope)
    context = None
    if repository_root is not None:
        control = json.loads((Path(repository_root) / ".gpt-codex/CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((Path(repository_root) / ".gpt-codex/STATE.json").read_text(encoding="utf-8"))
        context = {"reviewed_revision": value.get("expected_base_sha"),
            "project_context_id": control.get("project_context_id"),
            "repository_id": (control.get("github") or {}).get("repository_id"),
            "repository_full_name": (control.get("github") or {}).get("repository_full_name"),
            "remote_ref": (state.get("continuity") or {}).get("current_remote_ref")}
    errors += validate_review_lifecycle(value, finding_result, current_state_revision,
        remediation_decision=decision, resolved_basis=resolved_basis,
        repository_root=repository_root, authoritative_review_context=context)
    if errors:
        raise ValueError("FIX_CONSTRUCTION_BLOCKED:" + ",".join(dict.fromkeys(errors)))
    return value


def render_compact_codex_handoff(
    instruction: Mapping[str, Any], locator: Mapping[str, str], *, goal: str, stop_conditions: list[str],
) -> str:
    """One copyable presentation block; the immutable Instruction stays authoritative."""
    from validate_project import validate_instruction_envelope_contract
    if validate_instruction_envelope_contract(instruction) or not isinstance(locator, Mapping):
        raise ValueError("HANDOFF_BINDING_INVALID")
    if (set(locator) != {"repository", "commit_sha", "path", "blob_sha"}
        or locator.get("repository") != instruction.get("target_github_repository_full_name")
        or locator.get("path") != instruction_artifact_relative_path(instruction.get("instruction_id"))
        or not _SHA_RE.fullmatch(str(locator.get("commit_sha", "")))
        or not _SHA_RE.fullmatch(str(locator.get("blob_sha", "")))
        or not isinstance(goal, str) or not goal.strip()
        or not isinstance(stop_conditions, list) or not stop_conditions):
        raise ValueError("HANDOFF_BINDING_INVALID")
    lines = ["```text", f"EXECUTOR: {instruction.get('executor_role')}",
             f"PROJECT_CONTEXT: {instruction.get('target_project_context_id')}",
             f"WORK_UNIT: {instruction.get('target_work_unit')}",
             f"STATE_REVISION: {instruction.get('expected_state_revision')}",
             "INSTRUCTION_LOCATOR: " + json.dumps(dict(locator), ensure_ascii=False, sort_keys=True),
             f"GOAL: {goal}", "SCOPE: " + ", ".join(instruction.get("scope_paths", [])),
             "STOP: " + "; ".join(stop_conditions),
             "Read the immutable Instruction; fresh resume and native gate are required before mutation.",
             "RETURN_TO_GPT: YES", "```"]
    if any("```" in line for line in lines[1:-1]):
        raise ValueError("HANDOFF_BINDING_INVALID")
    return "\n".join(lines)


def resolve_durable_instruction(
    root: Path, locator: Mapping[str, Any], expected_repository: str, *,
    current_state_revision: int, approved_scope: set[str] | None = None,
    excluded_scope: set[str] | None = None,
) -> dict[str, Any]:
    """Resolve immutable Instruction bytes and recheck current Core authority."""
    from continuity_resume import load_continuity_resume, read_immutable_governed_artifact
    from github_repository_binding import canonicalize_remote_url
    from validate_project import validate_instruction_authority, validate_instruction_envelope_contract

    root = Path(root)
    artifact = read_immutable_governed_artifact(root, locator, expected_repository)
    if artifact.get("status") != "ALLOW":
        return {"status": "RECONCILIATION_REQUIRED"}
    try:
        origin = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=False,
        )
        if origin.returncode != 0 or canonicalize_remote_url(origin.stdout) != f"github:{expected_repository}":
            return {"status": "RECONCILIATION_REQUIRED"}
        envelope = artifact["record"]
        # Legacy readability is separate from permission to execute an Instruction.
        raw = subprocess.check_output(["git", "-C", str(root), "show", f"{locator['commit_sha']}:{locator['path']}"])
        if raw != canonical_instruction_bytes(envelope):
            return {"status": "RECONCILIATION_REQUIRED"}
        instruction_id = envelope["instruction_id"]
        if locator["path"] != instruction_artifact_relative_path(instruction_id):
            return {"status": "RECONCILIATION_REQUIRED"}
        control = json.loads((root / ".gpt-codex/CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((root / ".gpt-codex/STATE.json").read_text(encoding="utf-8"))
        repository_id = str(control["github"]["repository_id"])
        baseline = load_continuity_resume(root, repository_id)
        work_ref = envelope["target_work_unit_ref"]
        work_path = work_ref["path"]
        work_sha = work_ref["sha"]
        if work_path != f".gpt-codex/work-units/{envelope['target_work_unit']}.json":
            return {"status": "RECONCILIATION_REQUIRED"}
        work_blob = subprocess.run(
            ["git", "-C", str(root), "show", f"{work_sha}:{work_path}"],
            capture_output=True, check=False,
        )
        if work_blob.returncode != 0:
            return {"status": "RECONCILIATION_REQUIRED"}
        from continuity_resume import _unique_json_object
        work_unit = json.loads(work_blob.stdout, object_pairs_hook=_unique_json_object)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return {"status": "RECONCILIATION_REQUIRED"}
    work_scope = set((work_unit.get("scope") or {}).get("owned_paths") or [])
    excluded = set((work_unit.get("scope") or {}).get("excluded_paths") or [])
    if approved_scope is not None:
        work_scope &= set(approved_scope)
    if excluded_scope is not None:
        excluded |= set(excluded_scope)
    if (
        baseline.get("status") != "LATEST_SYNCED_REMOTE_STATE"
        or type(current_state_revision) is not int
        or state.get("revision") != current_state_revision
        or validate_instruction_envelope_contract(envelope)
        or validate_instruction_authority(envelope, current_state_revision, work_scope, excluded)
        or envelope.get("target_project_context_id") != control.get("project_context_id")
        or envelope.get("target_project_name") != control.get("project_name")
        or str(envelope.get("target_github_repository_id")) != repository_id
        or envelope.get("target_github_repository_full_name") != expected_repository
        or control["github"].get("repository_full_name") != expected_repository
        or work_unit.get("project_id") != control.get("project_id")
        or work_unit.get("work_unit_id") != envelope.get("target_work_unit")
        or work_unit.get("state") != "AUTHORIZED"
        or work_unit.get("basis_state_revision") != current_state_revision
        or not set(envelope.get("authorized_actions") or []).issubset(
            set((work_unit.get("permissions") or {}).get("authorized_actions") or []))
    ):
        return {"status": "RECONCILIATION_REQUIRED"}
    return {
        "status": "INSTRUCTION_RESOLVED", "contract_status": artifact["contract_status"], "instruction_id": instruction_id,
        "instruction_locator": dict(locator),
        "target_work_unit_id": envelope["target_work_unit"],
        "target_work_unit_ref": dict(work_ref),
        "expected_state_revision": current_state_revision,
        "project_id": control["project_id"],
        "project_context_id": control["project_context_id"],
        "repository_id": repository_id, "repository": expected_repository,
        "envelope": envelope, "work_unit": work_unit,
    }


def validate_durable_capability_request(
    root: Path, locator: Mapping[str, Any], repository_id: str, *,
    current_state_revision: int, requested_action: str,
    review_request: Mapping[str, Any] | None = None,
    review_result: Mapping[str, Any] | None = None,
    repository_authority: Mapping[str, Any] | None = None,
) -> list[str]:
    """Route an executable request through the existing Core mutation gate."""
    from validate_project import validate_governed_mutation_entry

    root = Path(root)
    try:
        control = json.loads((root / ".gpt-codex/CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((root / ".gpt-codex/STATE.json").read_text(encoding="utf-8"))
        if str(control["github"]["repository_id"]) != str(repository_id):
            return ["RECONCILIATION_REQUIRED"]
        resolved = resolve_durable_instruction(
            root, locator, control["github"]["repository_full_name"],
            current_state_revision=current_state_revision,
        )
        if resolved.get("status") != "INSTRUCTION_RESOLVED":
            return ["RECONCILIATION_REQUIRED"]
        instruction = resolved["envelope"]
        if requested_action not in instruction.get("authorized_actions", []):
            return ["ROLE_AUTHORITY_CONFLICT"]
        return validate_governed_mutation_entry(
            control, state, resolved["work_unit"], instruction,
            review_request, review_result,
            current_state_revision=current_state_revision,
            repository_authority=repository_authority,
            repository_root=root,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return ["RECONCILIATION_REQUIRED"]


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
    target_work_unit_ref: Mapping[str, str] | None = None,
    runtime_fresh_context_verified: bool | None = None,
    runtime_input_source_kinds: list[str] | None = None,
    scope_paths: list[str] | None = None,
    remediation_decision_ref: str | None = None,
    approval_evidence_ref: Mapping[str, str] | None = None,
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
    if not isinstance(framework_version, str) or not _INSTRUCTION_SEMVER_RE.fullmatch(framework_version):
        raise ValueError("INVALID_FRAMEWORK_VERSION")
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
    if instruction_type == "REVIEW_REQUEST":
        if runtime_fresh_context_verified is not True:
            raise ValueError("ROLE_DISPATCH = BLOCKED")
        input_errors = _validate_role_input_sources(executor_role, runtime_input_source_kinds)
        if input_errors:
            raise ValueError(", ".join(input_errors))
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
    _validate_target_work_unit_ref(target_work_unit_ref)
    requires_scope = instruction_type == "FIX_INSTRUCTION" or (
        instruction_type in {"EXECUTION_INSTRUCTION", "RECONCILIATION_REQUEST"}
        and authorized_actions is not None and "MUTATE_APPROVED_SCOPE" in authorized_actions
    )
    if requires_scope and scope_paths is None:
        raise ValueError("SCOPE_PATHS_REQUIRED")
    if scope_paths is not None:
        if (not isinstance(scope_paths, list) or not 1 <= len(scope_paths) <= 100 or len(scope_paths) != len(set(scope_paths))
                or any(not isinstance(path, str) or not path or path.startswith("/") or re.match(r"^[A-Za-z]:", path) or "\\" in path
                       or any(part in {"", ".", ".."} for part in path.split("/")) for path in scope_paths)):
            raise ValueError("INVALID_SCOPE_PATHS")
    if remediation_decision_ref is not None and (not isinstance(remediation_decision_ref, str) or not remediation_decision_ref.strip()):
        raise ValueError("INVALID_REMEDIATION_DECISION_REF")
    _validate_approval_evidence_ref(approval_evidence_ref)
    if approval_evidence_ref is not None and (
        instruction_type != "RECONCILIATION_REQUEST" or authorized_actions is None or "MUTATE_APPROVED_SCOPE" not in authorized_actions
    ):
        raise ValueError("APPROVAL_EVIDENCE_REF_NOT_ALLOWED")
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
        "target_work_unit_ref": dict(target_work_unit_ref) if target_work_unit_ref is not None else None,
        "scope_paths": list(scope_paths) if scope_paths is not None else None,
        "remediation_decision_ref": remediation_decision_ref,
        "approval_evidence_ref": dict(approval_evidence_ref) if approval_evidence_ref is not None else None,
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


def _validate_target_work_unit_ref(value: Mapping[str, str] | None) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping) or set(value) != {"path", "sha"}:
        raise ValueError("INVALID_TARGET_WORK_UNIT_REF")
    path, sha = value.get("path"), value.get("sha")
    if (not isinstance(path, str) or not path.strip() or Path(path).is_absolute() or ".." in Path(path).parts
            or not isinstance(sha, str) or not _SHA_RE.fullmatch(sha)):
        raise ValueError("INVALID_TARGET_WORK_UNIT_REF")


def _validate_approval_evidence_ref(value: Mapping[str, str] | None) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping) or set(value) != {"remote_ref", "evidence_commit_sha", "path", "blob_sha"}:
        raise ValueError("INVALID_APPROVAL_EVIDENCE_REF")
    remote_ref, commit, path, blob = (value.get(key) for key in ("remote_ref", "evidence_commit_sha", "path", "blob_sha"))
    if (not isinstance(remote_ref, str) or not remote_ref.strip() or not isinstance(commit, str) or not _SHA_RE.fullmatch(commit)
            or not isinstance(blob, str) or not _SHA_RE.fullmatch(blob) or not isinstance(path, str) or not path
            or path.startswith("/") or re.match(r"^[A-Za-z]:", path) or "\\" in path
            or any(part in {"", ".", ".."} for part in path.split("/"))):
        raise ValueError("INVALID_APPROVAL_EVIDENCE_REF")


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
