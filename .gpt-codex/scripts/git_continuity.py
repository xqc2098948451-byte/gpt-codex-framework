from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess
from typing import Any, Callable, Mapping
from pathlib import Path


_REVIEW_STAGES = frozenset({"DESIGN", "PLAN", "IMPLEMENTATION"})
_PENDING_VERIFICATION = frozenset({"NOT_ATTEMPTED", "INCOMPLETE", "UNAVAILABLE", "PENDING"})
_CONFLICTING_VERIFICATION = frozenset({
    "DIVERGED",
    "STALE_STATE_REVISION",
    "IDENTITY_CONFLICT",
    "REPOSITORY_MISMATCH",
    "REMOTE_REF_MISMATCH",
    "REMOTE_HEAD_MISMATCH",
})
_FORBIDDEN_REVIEW_OPERATIONS = frozenset({
    "AMEND",
    "REBASE",
    "RESET_REVIEWED",
    "FORCE_PUSH",
    "FORCE_WITH_LEASE",
    "REPLACE_BRANCH",
    "DELETE_BRANCH",
    "MERGE_MAIN",
    "TAG",
    "RELEASE",
    "PUBLISH",
})
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def plan_management_transaction(operation: str, scope_paths: list[str]) -> dict[str, Any]:
    """Non-authoritative plan for one existing-authority metadata transaction."""
    if operation not in {"STATE_SYNC", "EVIDENCE_FINALIZATION", "VERIFIED_WORK_PUBLICATION"}:
        raise ValueError("MANAGEMENT_OPERATION_DENIED")
    if not isinstance(scope_paths, list) or not scope_paths or len(scope_paths) != len(set(scope_paths)):
        raise ValueError("MANAGEMENT_SCOPE_DENIED")
    for path in scope_paths:
        if not isinstance(path, str) or not (
            path == ".gpt-codex/STATE.json"
            or re.fullmatch(r"\.gpt-codex/evidence/(?:results/)?[A-Za-z0-9_.-]+\.json", path)
        ):
            raise ValueError("MANAGEMENT_SCOPE_DENIED")
    return {"operation": operation, "scope_paths": list(scope_paths), "authority": "DERIVED_PLAN_ONLY",
            "gates": ["PRE_EXECUTION", "POST_EXECUTION"], "new_work_unit_required": False,
            "temporary_branch_required": False, "transaction_record_count": 1,
            "destructive_actions": "USE_EXISTING_EXPLICIT_USER_AUTHORIZATION_PATH"}


def build_validation_plan(changed_paths: list[str], *, finding: bool = False, release: bool = False) -> dict[str, Any]:
    """Risk advice, not a validator result, exemption or reusable authority cache."""
    if not isinstance(changed_paths, list) or not changed_paths or not all(_is_safe_evidence_path(p) for p in changed_paths):
        raise ValueError("VALIDATION_SCOPE_INVALID")
    safety = any(p in {"AGENTS.md", ".gpt-codex/KERNEL.md", ".gpt-codex/STATE.json", ".gpt-codex/CONTROL.json"}
                 or p.startswith(".gpt-codex/schemas/")
                 or p in {".gpt-codex/scripts/validate_project.py", ".gpt-codex/scripts/context_binding.py",
                          ".gpt-codex/scripts/role_communication.py", ".gpt-codex/scripts/git_continuity.py"}
                 for p in changed_paths)
    return {"risk_tier": "RELEASE" if release else "CORE_AUTHORITY" if safety else "FOCUSED",
            "full_suite_required": release, "focused_regression_required": True,
            "affected_validators_required": True, "real_world_acceptance_required": True,
            "original_user_path_reproduction_required": finding, "core_fail_closed_required": safety,
            "independent_review_required": True, "self_proof_replaces_review": False,
            "repeat_validation": "ONLY_CHANGED_INPUTS_OR_UNRESOLVED_FAILURES", "authority": "DERIVED_ADVICE_ONLY"}


def _is_safe_evidence_path(value: object) -> bool:
    return (
        isinstance(value, str) and bool(value) and "\\" not in value
        and not value.startswith("/") and not re.match(r"^[A-Za-z]:", value)
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


def observe_bound_remote(root: Path, control: Mapping[str, Any], remote_ref: str) -> dict[str, Any]:
    """Live canonical remote and GitHub ID observation; never cached by attestation."""
    from github_repository_binding import canonicalize_remote_url, compare_repository_binding, ObservedRepository
    if not isinstance(remote_ref, str) or not re.fullmatch(r'refs/heads/[A-Za-z0-9_./-]+', remote_ref):
        raise ValueError('REMOTE_REF_MISMATCH')
    root = Path(root)
    def run(*args: str) -> str:
        return subprocess.check_output(list(args), text=True, stderr=subprocess.DEVNULL, timeout=30).strip()
    try:
        github = control['github']
        canonical = canonicalize_remote_url(run('git', '-C', str(root), 'remote', 'get-url', 'origin'))
        if canonical != 'github:' + github['repository_full_name']:
            raise ValueError('GITHUB_REPOSITORY_MISMATCH')
        metadata = json.loads(run('gh', 'api', 'repos/' + github['repository_full_name']))
        observed = ObservedRepository(str(metadata['id']), metadata['full_name'], 'origin', canonical)
        decision = compare_repository_binding(control, observed)
        if decision.decision != 'ALLOW':
            raise ValueError(decision.reason)
        lines = run('git', '-C', str(root), 'ls-remote', 'origin', remote_ref).splitlines()
        if len(lines) != 1 or lines[0].split() != [lines[0].split()[0], remote_ref] or not _SHA_RE.fullmatch(lines[0].split()[0]):
            raise ValueError('REMOTE_UNAVAILABLE')
        return {'repository_id': observed.repository_id, 'repository': observed.repository_full_name,
                'remote_ref': remote_ref, 'remote_head_sha': lines[0].split()[0], 'evidence_type': 'TOOL_OBSERVED'}
    except (OSError, subprocess.SubprocessError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('REMOTE_UNAVAILABLE') from exc


def plan_low_risk_correction(changed_paths: list[str], approved_scope: set[str]) -> dict[str, Any]:
    """Focused validation advice under existing authorization; never an execution gate."""
    if (not isinstance(changed_paths, list) or not changed_paths or len(set(changed_paths)) != len(changed_paths)
            or any(not _is_safe_evidence_path(p) or p not in approved_scope
                   or not (p.startswith('docs/') or re.fullmatch(r'\.gpt-codex/evidence/[A-Za-z0-9_.-]+\.json', p))
                   for p in changed_paths)):
        raise ValueError('LOW_RISK_CORRECTION_DENIED')
    return {**build_validation_plan(changed_paths, finding=True), 'authority': 'DERIVED_PLAN_ONLY',
            'existing_work_unit_reused': True, 'native_entry_required': True,
            'candidate_reverification_required': True, 'pre_post_required': True}


def build_state_sync_finalization(root: Path, *, work_sha: str, remote_ref: str,
                                 expected_state_revision: int, result_ref: str,
                                 post_request: Mapping[str, Any] | None,
                                 post_result: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build, never write, a STATE sync candidate after exact-W independent POST.

    Caller must separately authorize/apply closure, persist and validate Result,
    then publish P. Result PASS never changes a Work Unit to COMPLETE here.
    """
    from copy import deepcopy
    from validate_project import (validate_instruction_envelope_contract, validate_result_envelope_contract,
                                  validate_review_result, validate_instruction_authority,
                                  validate_committed_candidate_scope, _resolve_work_unit_at_ref)
    root = Path(root).resolve()
    if not isinstance(post_request, Mapping) or not isinstance(post_result, Mapping):
        raise ValueError('INDEPENDENT_POST_REQUIRED')
    if (validate_instruction_envelope_contract(post_request) or validate_result_envelope_contract(post_result)
            or validate_review_result(post_result) or post_request.get('instruction_type') != 'REVIEW_REQUEST'
            or post_request.get('executor_role') != 'CODEX_REVIEWER' or post_result.get('responder_role') != 'CODEX_REVIEWER'
            or post_result.get('status') != 'PASS' or post_result.get('result_message_type') != 'REVIEW_RESULT'
            or post_result.get('response_to_instruction_id') != post_request.get('instruction_id')
            or post_result.get('review_target_revision') != work_sha or post_request.get('review_target_revision') != work_sha):
        raise ValueError('INDEPENDENT_POST_REQUIRED')
    control = json.loads((root / '.gpt-codex/CONTROL.json').read_bytes())
    state = json.loads((root / '.gpt-codex/STATE.json').read_bytes())
    if type(expected_state_revision) is not int or state.get('revision') != expected_state_revision:
        raise ValueError('STALE_STATE_REVISION')
    github = control['github']
    for source, target, value in (
        ('source_project_name', 'target_project_name', control['project_name']),
        ('source_project_context_id', 'target_project_context_id', control['project_context_id']),
        ('source_github_repository_id', 'target_github_repository_id', github['repository_id']),
        ('source_github_repository_full_name', 'target_github_repository_full_name', github['repository_full_name']),
        ('current_remote_ref', 'expected_remote_ref', remote_ref),
        ('state_revision', 'expected_state_revision', expected_state_revision),
    ):
        if post_result.get(source) != value or post_request.get(target) != value:
            raise ValueError('RECONCILIATION_REQUIRED:POST_BINDING_MISMATCH')
    unit = _resolve_work_unit_at_ref(root, post_request.get('target_work_unit_ref'))
    owned = ((unit or {}).get('scope') or {}).get('owned_paths', [])
    if (not isinstance(unit, Mapping) or unit.get('state') != 'AUTHORIZED'
            or unit.get('project_id') != control['project_id'] or unit.get('basis_state_revision') != expected_state_revision
            or post_result.get('project_id') != control['project_id']
            or unit.get('work_unit_id') != post_result.get('work_unit_id')
            or unit.get('work_unit_id') != post_request.get('target_work_unit')
            or '.gpt-codex/STATE.json' not in owned or result_ref not in owned
            or not re.fullmatch(r'\.gpt-codex/evidence/(?:results/)?[A-Za-z0-9_.-]+\.json', result_ref)):
        raise ValueError('FINALIZATION_SCOPE_DENIED')
    execution_id = post_request.get('in_response_to_instruction_id')
    if not isinstance(execution_id, str) or not re.fullmatch(r'[0-9a-fA-F-]{36}', execution_id):
        raise ValueError('RECONCILIATION_REQUIRED:INSTRUCTION_CORRELATION')
    execution_path = root / f'.gpt-codex/evidence/instructions/{execution_id}.json'
    try:
        execution = json.loads(execution_path.read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('RECONCILIATION_REQUIRED:INSTRUCTION_CORRELATION') from exc
    if (execution.get('instruction_id') != execution_id or execution.get('instruction_type') != 'EXECUTION_INSTRUCTION'
            or execution.get('target_work_unit_ref') != post_request.get('target_work_unit_ref')
            or execution.get('target_work_unit') != unit['work_unit_id']
            or validate_instruction_envelope_contract(execution)
            or validate_instruction_authority(execution, expected_state_revision, set(owned), set(unit['scope'].get('excluded_paths', [])))
            or validate_instruction_authority(post_request, expected_state_revision, set(owned), set(unit['scope'].get('excluded_paths', [])))
            or validate_committed_candidate_scope(root, execution.get('expected_base_sha'), work_sha, set(execution['scope_paths']), set())):
        raise ValueError('RECONCILIATION_REQUIRED:INSTRUCTION_CORRELATION')
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain=v1', '--untracked-files=all'])
    if head != work_sha or dirty:
        raise ValueError('STALE_AUTHORITY:WORK_CANDIDATE_CHANGED')
    observed = observe_bound_remote(root, control, remote_ref)
    if observed['remote_head_sha'] != work_sha:
        raise ValueError('REMOTE_HEAD_MISMATCH')
    candidate = deepcopy(state)
    candidate['revision'] = expected_state_revision + 1
    candidate.setdefault('continuity', {}).update(current_remote_ref=remote_ref, latest_verified_remote_sha=work_sha,
        latest_synced_state_revision=candidate['revision'], last_verified_result_ref=result_ref, sync_status='SYNCED')
    if result_ref not in candidate.setdefault('evidence_refs', []):
        candidate['evidence_refs'].append(result_ref)
    return {'authority': 'DERIVED_FINALIZATION_CANDIDATE', 'state': candidate,
            'work_unit_completed': False, 'publication_verification_required': True, 'remote_observation': observed}


def verify_work_publication(root: Path, *, work_sha: str, publication_sha: str,
                            remote_ref: str, scope_paths: list[str]) -> dict[str, Any]:
    """Observe an actual exact metadata-only W/P chain; no caller-supplied booleans."""
    from publication_contract import validate_state_authority
    root = Path(root).resolve()
    def git(*args: str) -> str:
        return subprocess.check_output(['git', '-C', str(root), *args], text=True, encoding='utf-8',
                                       stderr=subprocess.DEVNULL).strip()
    if not _SHA_RE.fullmatch(work_sha) or not _SHA_RE.fullmatch(publication_sha):
        raise ValueError('RECONCILIATION_REQUIRED')
    parents = git('rev-list', '--parents', '-n', '1', publication_sha).split()[1:]
    if parents != [work_sha]:
        raise ValueError('RECONCILIATION_REQUIRED:PUBLICATION_PARENT_MISMATCH')
    changed = git('diff', '--name-only', work_sha, publication_sha, '--').splitlines()
    if (not changed or not isinstance(scope_paths, list) or len(scope_paths) != len(set(scope_paths))
            or not set(changed).issubset(scope_paths) or any(not _is_safe_evidence_path(p)
            or not (p == '.gpt-codex/STATE.json' or re.fullmatch(r'\.gpt-codex/(?:evidence/(?:results/)?|work-units/)[A-Za-z0-9_.-]+\.json', p)) for p in changed)):
        raise ValueError('PUBLICATION_SCOPE_DENIED')
    control = json.loads(git('show', f'{work_sha}:.gpt-codex/CONTROL.json'))
    original = json.loads(git('show', f'{work_sha}:.gpt-codex/STATE.json'))
    state = json.loads(git('show', f'{publication_sha}:.gpt-codex/STATE.json'))
    continuity = state.get('continuity', {})
    result_ref = continuity.get('last_verified_result_ref')
    if (not _is_safe_evidence_path(result_ref) or result_ref not in scope_paths
            or continuity.get('latest_verified_remote_sha') != work_sha or continuity.get('sync_status') != 'SYNCED'
            or continuity.get('current_remote_ref') != remote_ref or state.get('revision') != original.get('revision', -1) + 1
            or state.get('project_id') != control.get('project_id')):
        raise ValueError('RECONCILIATION_REQUIRED:STATE_FINALIZATION_MISMATCH')
    result = json.loads(git('show', f'{publication_sha}:{result_ref}'))
    if validate_state_authority(state, {result_ref: result}):
        raise ValueError('RECONCILIATION_REQUIRED:PUBLICATION_RESULT_INVALID')
    for path in changed:
        if path.startswith('.gpt-codex/work-units/'):
            before = json.loads(git('show', f'{work_sha}:{path}'))
            after = json.loads(git('show', f'{publication_sha}:{path}'))
            allowed = {'state', 'authorization', 'implementation_authorized', 'implementation_start_allowed', 'next_gate', 'closure', 'evidence_refs'}
            closure = after.get('closure', {})
            authorization = after.get('authorization', {})
            if (before.get('work_unit_id') != result.get('work_unit_id')
                    or after.get('state') != 'COMPLETE' or after.get('implementation_authorized') is not False
                    or after.get('implementation_start_allowed') is not False or after.get('next_gate') != 'COMPLETE'
                    or authorization.get('implementation_authorized') is not False
                    or authorization.get('implementation_start_allowed') is not False or authorization.get('status') != 'COMPLETE'
                    or closure.get('verified_work_sha') != work_sha or not closure.get('independent_post_result_id')
                    or any(before.get(k) != after.get(k) for k in set(before) | set(after) if k not in allowed)):
                raise ValueError('PUBLICATION_SCOPE_DENIED')
    observed = observe_bound_remote(root, control, remote_ref)
    if observed['remote_head_sha'] != publication_sha:
        raise ValueError('REMOTE_HEAD_MISMATCH')
    verified = verify_remote_publication(remote_ref, publication_sha, observed['repository_id'],
        control['github']['repository_id'], True, observed_remote_ref=remote_ref,
        observed_remote_head=observed['remote_head_sha'])
    if verified['status'] != 'VERIFIED':
        raise ValueError(verified['reason'])
    return {**evaluate_attestation_chain({'work_sha': work_sha, 'publication_sha': publication_sha,
        'verified_work': True, 'publication_references_work': True, 'publication_references_self': False,
        'publication_is_management_only': True, 'generic_tree_matches': True}),
        'changed_paths': changed, 'remote_observation': observed}


def resolve_approval_evidence_locator(
    repository_root: Path,
    locator: Mapping[str, str],
) -> tuple[Mapping[str, object] | None, list[str]]:
    """Resolve approval evidence from its immutable commit/path/blob tuple.

    ``remote_ref`` proves that the bound commit remains transport-reachable;
    it is deliberately never used as the source of the approval bytes.
    """

    required = {"remote_ref", "evidence_commit_sha", "path", "blob_sha"}
    if (
        not isinstance(repository_root, Path) or not isinstance(locator, Mapping)
        or set(locator) != required
    ):
        return None, ["APPROVAL_EVIDENCE_LOCATOR_INVALID"]
    remote_ref = locator.get("remote_ref")
    commit = locator.get("evidence_commit_sha")
    path = locator.get("path")
    blob = locator.get("blob_sha")
    if (
        not isinstance(remote_ref, str) or not remote_ref.strip() or "\n" in remote_ref
        or remote_ref.startswith("-") or not isinstance(commit, str) or not _SHA_RE.fullmatch(commit)
        or not isinstance(blob, str) or not _SHA_RE.fullmatch(blob) or not _is_safe_evidence_path(path)
    ):
        return None, ["APPROVAL_EVIDENCE_LOCATOR_INVALID"]

    def run(*args: str) -> subprocess.CompletedProcess[bytes]:
        try:
            return subprocess.run(["git", "-C", str(repository_root), *args], capture_output=True, check=False)
        except OSError:
            return subprocess.CompletedProcess(args, 127, b"", b"")

    if run("rev-parse", "--verify", f"{commit}^{{commit}}").returncode != 0:
        return None, ["APPROVAL_EVIDENCE_COMMIT_MISSING"]
    object_spec = f"{commit}:{path}"
    resolved = run("rev-parse", "--verify", object_spec)
    if resolved.returncode != 0:
        return None, ["APPROVAL_EVIDENCE_PATH_MISSING"]
    actual_blob = resolved.stdout.decode("ascii", "ignore").strip()
    if not _SHA_RE.fullmatch(actual_blob) or run("cat-file", "-e", f"{actual_blob}^{{blob}}").returncode != 0:
        return None, ["APPROVAL_EVIDENCE_PATH_MISSING"]
    if actual_blob.lower() != blob.lower():
        return None, ["APPROVAL_EVIDENCE_BLOB_MISMATCH"]

    remote = run("ls-remote", "origin", remote_ref)
    remote_lines = remote.stdout.decode("utf-8", "surrogateescape").splitlines() if remote.returncode == 0 else []
    remote_head = next((line.split("\t", 1)[0] for line in remote_lines if "\t" in line and line.split("\t", 1)[1] == remote_ref), None)
    if not isinstance(remote_head, str) or not _SHA_RE.fullmatch(remote_head):
        return None, ["APPROVAL_EVIDENCE_REMOTE_UNREACHABLE"]
    if run("merge-base", "--is-ancestor", commit, remote_head).returncode != 0:
        return None, ["APPROVAL_EVIDENCE_REMOTE_UNREACHABLE"]

    payload = run("cat-file", "blob", actual_blob)
    if payload.returncode != 0:
        return None, ["APPROVAL_EVIDENCE_PATH_MISSING"]
    try:
        parsed = json.loads(payload.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, ["APPROVAL_EVIDENCE_PAYLOAD_INVALID"]
    if not isinstance(parsed, Mapping):
        return None, ["APPROVAL_EVIDENCE_PAYLOAD_INVALID"]
    return parsed, []


@dataclass(frozen=True)
class SyncSnapshot:
    local_head_sha: str | None
    remote_head_sha: str | None
    remote_ref: str | None
    dirty: bool
    local_ahead: int
    remote_ahead: int
    diverged: bool


@dataclass(frozen=True)
class SyncDecision:
    decision: str
    reason: str
    mutation_allowed: bool
    publish_allowed: bool


def _canonical_git_runner(command: list[str], root: Path) -> tuple[int, str, str]:
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, check=False)
    except OSError as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout.decode("utf-8", "surrogateescape"), result.stderr.decode("utf-8", "surrogateescape")


def observe_canonical_git_facts(root: Path, runner: Callable[[list[str], Path], tuple[int, str, str]] = _canonical_git_runner) -> dict[str, Any]:
    """Read EOL-sensitive Git facts with a command-local canonical override."""
    code, stdout, _stderr = runner(["git", "config", "--get", "--local", "core.autocrlf"], root)
    if code not in (0, 1):
        return {"deterministic": False, "mutation_allowed": False, "reason": "GIT_PROBE_FAILED"}
    ambient = "UNSET" if code == 1 or not stdout.strip() else stdout.strip().upper()
    if ambient not in {"TRUE", "FALSE", "INPUT", "UNSET"}:
        return {"deterministic": False, "mutation_allowed": False, "reason": "AUTOCRLF_MALFORMED"}
    code, status, _stderr = runner(["git", "-c", "core.autocrlf=false", "status", "--porcelain", "-z"], root)
    if code != 0:
        return {"deterministic": False, "mutation_allowed": False, "reason": "GIT_PROBE_FAILED"}
    paths = tuple(sorted(item[3:] for item in status.split("\0") if len(item) >= 4))
    return {"deterministic": True, "mutation_allowed": True, "ambient_autocrlf": ambient, "changed_paths": paths}


def evaluate_execution_capability_preflight(observed: Mapping[str, Any]) -> SyncDecision:
    """Fail closed before mutation from bounded A1 capability observations."""
    if not isinstance(observed, Mapping):
        return _deny("RECONCILIATION_REQUIRED", "CAPABILITY_OBSERVATION_MALFORMED")
    required = (("powershell", "SUPPORTED"), ("python", "AVAILABLE"), ("git", "AVAILABLE"))
    for name, expected in required:
        fact = observed.get(name)
        if not isinstance(fact, Mapping) or not isinstance(fact.get("status"), str):
            return _deny("RECONCILIATION_REQUIRED", "CAPABILITY_OBSERVATION_MALFORMED")
        if fact["status"] != expected:
            return _deny("BLOCKED", f"REQUIRED_CAPABILITY_{name.upper()}_{fact['status']}")
    remote = observed.get("remote")
    if not isinstance(remote, Mapping) or not isinstance(remote.get("available"), bool):
        return _deny("RECONCILIATION_REQUIRED", "CAPABILITY_OBSERVATION_MALFORMED")
    if not remote["available"]:
        return _deny("BLOCKED", "REQUIRED_CAPABILITY_REMOTE_UNAVAILABLE")
    if observed.get("unicode_path_round_trip") is not True:
        return _deny("BLOCKED", "REQUIRED_CAPABILITY_UNICODE_UNAVAILABLE")
    return SyncDecision("CAPABILITY_READY", "CAPABILITY_READY", True, False)


def evaluate_worktree_cleanup(
    active_work_unit: bool | None,
    durable_git_authority: bool | None,
    review_or_integration_sufficient: bool | None,
    has_dirty_only_data: bool | None,
) -> str:
    """Authorize cleanup only when every supplied evidence fact is conclusive."""
    if (
        active_work_unit is False
        and durable_git_authority is True
        and review_or_integration_sufficient is True
        and has_dirty_only_data is False
    ):
        return "CLEAN"
    return "KEEP"


def classify_cleanup_manifest(manifest: Mapping[str, Any], allowed_root: Path, filesystem_facts: Mapping[str, Any]) -> dict[str, Any]:
    """Classify one manifest target without changing the filesystem."""
    evidence = {"manifest_identity": None, "allowed_root": str(allowed_root), "target": None, "canonical_path": None}
    if not isinstance(manifest, Mapping) or not isinstance(allowed_root, Path):
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_INVALID"}
    manifest_id, manifest_root = manifest.get("manifest_id"), manifest.get("allowed_root")
    if not isinstance(manifest_id, str) or not manifest_id.strip() or len(manifest_id) > 160 or not isinstance(manifest_root, str) or not manifest_root.strip():
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_IDENTITY_INVALID"}
    try:
        root = Path(manifest_root).resolve()
    except OSError:
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_ROOT_INVALID"}
    if root != allowed_root.resolve():
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_ROOT_MISMATCH"}
    evidence["manifest_identity"] = manifest_id
    evidence["allowed_root"] = str(root)
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_INVALID"}
    targets = [entry.get("target") for entry in entries if isinstance(entry, Mapping)]
    if len(entries) != len(targets) or not all(isinstance(target, str) for target in targets) or len(set(targets)) != len(targets) or len(entries) != 1:
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_AMBIGUOUS"}
    entry = entries[0]
    operation, target = entry.get("operation"), entry.get("target")
    evidence["target"] = target
    if operation not in {"KEEP", "DELETE"} or not isinstance(target, str) or not target or any(char in target for char in "*?[]"):
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "MANIFEST_ENTRY_INVALID"}
    candidate = Path(target)
    if candidate.is_absolute() or candidate.drive or ".." in candidate.parts:
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "TARGET_PATH_UNSAFE"}
    raw_target = root / candidate
    if not raw_target.exists():
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "TARGET_MISSING"}
    try:
        stat = raw_target.lstat()
        reparse = raw_target.is_symlink() or bool(getattr(stat, "st_file_attributes", 0) & 0x400)
        canonical = raw_target.resolve()
        canonical.relative_to(root)
    except (OSError, ValueError):
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "TARGET_ESCAPES_ROOT"}
    evidence["canonical_path"] = str(canonical)
    if reparse:
        return {**evidence, "decision": "RECONCILIATION_REQUIRED", "reason": "TARGET_REPARSE_POINT"}
    return {**evidence, "decision": operation, "classification": "IN_ROOT_ORDINARY", "reason": "MANIFEST_TARGET_VALID"}


def is_verified_repository_continuity_evidence(evidence: Mapping[str, Any] | None) -> bool:
    """Recognize supplied continuity evidence without reading a repository or remote."""
    return isinstance(evidence, Mapping) and evidence.get("status") == "VERIFIED"


def review_routing_for_stage(stage: str, remote_trigger: str | None = None) -> dict[str, str]:
    """Return the single review route for a protocol artifact stage."""

    if stage not in _REVIEW_STAGES:
        raise ValueError("UNKNOWN_REVIEW_STAGE")
    if remote_trigger is not None and (not isinstance(remote_trigger, str) or not remote_trigger.strip()):
        raise ValueError("INVALID_REMOTE_TRIGGER")
    if stage in {"DESIGN", "PLAN"}:
        route = {
            "stage": stage,
            "remote_review_visibility": "REQUIRED",
            "gpt_review": "REQUIRED",
            "reviewer_role": "GPT_REVIEWER",
        }
    else:
        route = {
            "stage": stage,
            "remote_review_visibility": "OPTIONAL",
            "technical_review": "CODEX_REVIEWER",
        }
    route["remote_trigger"] = remote_trigger or (
        "FORMAL_REVIEW" if stage in {"DESIGN", "PLAN"} else "MILESTONE_OR_RISK"
    )
    return route


def validate_review_revision(
    previous_reviewed_sha: str | None,
    candidate_sha: str,
    is_ancestor: Callable[[str, str], bool],
) -> list[str]:
    """Require a valid candidate revision to descend from formal review evidence."""

    if (previous_reviewed_sha is not None and not _SHA_RE.fullmatch(previous_reviewed_sha)) or not isinstance(candidate_sha, str) or not _SHA_RE.fullmatch(candidate_sha):
        return ["RECONCILIATION_REQUIRED", "REVIEWED_REVISION_INVALID"]
    if previous_reviewed_sha is None:
        return []
    if not callable(is_ancestor):
        return ["RECONCILIATION_REQUIRED", "ANCESTRY_VERIFICATION_FAILED"]
    try:
        valid_ancestry = bool(is_ancestor(previous_reviewed_sha, candidate_sha))
    except Exception:
        valid_ancestry = False
    if not valid_ancestry:
        return ["RECONCILIATION_REQUIRED", "REVIEWED_REVISION_NOT_ANCESTOR"]
    return []


def validate_review_history_operation(stage: str, operation: str) -> list[str]:
    """Deny reviewed DESIGN/PLAN history rewrites and publication operations."""

    if stage not in _REVIEW_STAGES:
        return ["INVALID_REVIEW_STAGE"]
    if not isinstance(operation, str) or not operation.strip():
        return ["INVALID_REVIEW_OPERATION"]
    if stage in {"DESIGN", "PLAN"} and operation.upper() in _FORBIDDEN_REVIEW_OPERATIONS:
        return ["ROLE_AUTHORITY_CONFLICT", "REVIEW_HISTORY_REWRITE_FORBIDDEN"]
    return []


def classify_review_sync(
    stage: str,
    push_status: str,
    remote_verification: str,
    remote_head_sha: str | None,
    expected_head_sha: str,
) -> str:
    """Classify review synchronization without treating missing evidence as conflict."""

    if stage not in _REVIEW_STAGES:
        raise ValueError("UNKNOWN_REVIEW_STAGE")
    if not isinstance(expected_head_sha, str) or not _SHA_RE.fullmatch(expected_head_sha):
        raise ValueError("EXPECTED_HEAD_REVISION_INVALID")
    if remote_head_sha is not None and remote_head_sha != expected_head_sha:
        return "RECONCILIATION_REQUIRED"
    if remote_verification in _CONFLICTING_VERIFICATION:
        return "RECONCILIATION_REQUIRED"
    if push_status == "SUCCEEDED" and remote_verification == "VERIFIED" and remote_head_sha == expected_head_sha:
        return "SYNCED"
    return "LOCAL_COMPLETE / SYNC_PENDING"


def evaluate_attestation_chain(facts: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the bounded W -> verified W -> management-only P protocol."""
    work_sha = facts.get("work_sha")
    publication_sha = facts.get("publication_sha")
    if not facts.get("verified_work") or not publication_sha:
        return {
            "status": "LOCAL_COMPLETE",
            "sync_status": "SYNC_PENDING",
            "remote_verification": "NOT_ATTEMPTED",
            "publication_authority": "PUBLICATION_CANDIDATE_ONLY",
            "verified_baseline_sha": None,
            "publication_sha": publication_sha,
        }
    if (
        not work_sha
        or not facts.get("publication_references_work")
        or facts.get("publication_references_self")
        or not facts.get("publication_is_management_only")
        or not facts.get("generic_tree_matches")
    ):
        return {
            "status": "RECONCILIATION_REQUIRED",
            "sync_status": "RECONCILIATION_REQUIRED",
            "remote_verification": "FAILED",
            "publication_authority": "PUBLICATION_CANDIDATE_ONLY",
            "verified_baseline_sha": work_sha,
            "publication_sha": publication_sha,
        }
    return {
        "status": "PASS",
        "sync_status": "SYNCED",
        "remote_verification": "VERIFIED",
        "publication_authority": "CONFIRMED_PUBLICATION",
        "verified_baseline_sha": work_sha,
        "publication_sha": publication_sha,
    }


def _deny(decision: str, reason: str, mutation: bool = False, publish: bool = False) -> SyncDecision:
    return SyncDecision(decision, reason, mutation, publish)


def evaluate_sync_preflight(
    snapshot: SyncSnapshot,
    expected_base_sha: str | None,
    expected_remote_ref: str | None,
    expected_remote_head_sha: str | None,
    expected_state_revision: int,
    current_state_revision: int,
) -> SyncDecision:
    if snapshot.remote_head_sha is None or snapshot.remote_ref is None:
        return _deny("REMOTE_UNAVAILABLE", "REMOTE_UNAVAILABLE")
    if snapshot.dirty:
        return _deny("RECONCILIATION_REQUIRED", "DIRTY_WORKTREE_RECONCILIATION_REQUIRED")
    if snapshot.diverged:
        return _deny("RECONCILIATION_REQUIRED", "LOCAL_REMOTE_DIVERGED")
    if snapshot.local_ahead:
        return _deny("RECONCILIATION_REQUIRED", "LOCAL_AHEAD")
    if snapshot.remote_ahead:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_AHEAD")
    if expected_base_sha is not None and snapshot.local_head_sha != expected_base_sha:
        return _deny("RECONCILIATION_REQUIRED", "EXPECTED_BASE_SHA_MISMATCH")
    if expected_remote_ref is not None and snapshot.remote_ref != expected_remote_ref:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_REF_MISMATCH")
    if expected_remote_head_sha is not None and snapshot.remote_head_sha != expected_remote_head_sha:
        return _deny("RECONCILIATION_REQUIRED", "REMOTE_HEAD_MISMATCH")
    if expected_state_revision != current_state_revision:
        return _deny("RECONCILIATION_REQUIRED", "STALE_STATE_REVISION")
    return SyncDecision("CLEAN_SYNCED", "CLEAN_SYNCED", True, True)


def evaluate_new_work_preflight(
    snapshot: SyncSnapshot,
    expected_base_sha: str | None,
    expected_remote_ref: str | None,
    expected_remote_head_sha: str | None,
    expected_state_revision: int,
    current_state_revision: int,
) -> SyncDecision:
    decision = evaluate_sync_preflight(
        snapshot, expected_base_sha, expected_remote_ref, expected_remote_head_sha,
        expected_state_revision, current_state_revision,
    )
    if decision.decision != "CLEAN_SYNCED":
        return SyncDecision(decision.decision, decision.reason, False, False)
    return decision


def evaluate_active_work_degraded_continuation(
    identity_validated: bool,
    initial_clean_sync: bool,
    authorized_active: bool,
    remote_available: bool,
    requested_new_work_unit: bool,
) -> SyncDecision:
    if requested_new_work_unit:
        return _deny("RECONCILIATION_REQUIRED", "ACTIVE_WORK_CANNOT_START_SECOND_WORK_UNIT")
    if not (identity_validated and initial_clean_sync and authorized_active):
        return _deny("RECONCILIATION_REQUIRED", "ACTIVE_WORK_DEGRADED_AUTHORIZATION_MISSING")
    if remote_available:
        return SyncDecision("RECONNECT_PREFLIGHT_REQUIRED", "REMOTE_RECONNECT_REVALIDATION_REQUIRED", True, False)
    return SyncDecision("LOCAL_COMPLETE", "REMOTE_UNAVAILABLE", True, False)


def evaluate_publish_gate(binding: Any, sync: SyncDecision, push_status: str, remote_verification: str, state_revision_match: bool) -> SyncDecision:
    if not getattr(binding, "mutation_allowed", False) or not getattr(binding, "identity_match", False):
        return _deny("BLOCKED", "GITHUB_REPOSITORY_MISMATCH")
    if not state_revision_match:
        return _deny("RECONCILIATION_REQUIRED", "STALE_STATE_REVISION")
    if sync.decision != "CLEAN_SYNCED":
        return _deny("LOCAL_COMPLETE", "SYNC_PENDING")
    if push_status != "SUCCEEDED":
        return _deny("LOCAL_COMPLETE", "SYNC_PENDING")
    if remote_verification != "VERIFIED":
        return _deny("LOCAL_COMPLETE", "REMOTE_VERIFICATION_FAILED")
    return SyncDecision("SYNCED", "REMOTE_PUBLICATION_VERIFIED", True, True)


def verify_remote_publication(
    remote_ref: str,
    expected_publication_commit: str,
    observed_repository_id: str,
    bound_repository_id: str,
    object_reachable: bool,
    observed_remote_ref: str | None = None,
    observed_remote_head: str | None = None,
    work_reachable: bool = True,
    result_present: bool = True,
    state_present: bool = True,
) -> dict[str, Any]:
    if not observed_repository_id or not bound_repository_id or observed_repository_id != bound_repository_id:
        return {"status": "FAILED", "reason": "GITHUB_REPOSITORY_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if not observed_remote_ref and observed_remote_head is None:
        return {"status": "UNAVAILABLE", "reason": "REMOTE_UNAVAILABLE", "evidence_type": "TOOL_OBSERVED"}
    if observed_remote_ref is not None and observed_remote_ref != remote_ref:
        return {"status": "FAILED", "reason": "REMOTE_REF_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if observed_remote_head is not None and observed_remote_head != expected_publication_commit:
        return {"status": "FAILED", "reason": "REMOTE_HEAD_MISMATCH", "evidence_type": "TOOL_OBSERVED"}
    if not (object_reachable and work_reachable and result_present and state_present):
        return {"status": "FAILED", "reason": "REMOTE_OBJECT_OR_RECORD_MISSING", "evidence_type": "TOOL_OBSERVED"}
    return {
        "status": "VERIFIED",
        "reason": "REMOTE_PUBLICATION_VERIFIED",
        "evidence_type": "TOOL_OBSERVED",
        "remote_ref": remote_ref,
        "remote_head_sha": expected_publication_commit,
    }


def verify_remote_activation(facts: Mapping[str, Any]) -> dict[str, Any]:
    """Classify caller-supplied authoritative activation observations only."""
    if not isinstance(facts, Mapping) or facts.get("evidence_source") != "TOOL_OBSERVED":
        return {"status": "FAILED", "reason": "REMOTE_EVIDENCE_SOURCE_INVALID", "evidence_type": "TOOL_OBSERVED"}
    required = (
        "bound_repository_id", "observed_repository_id", "expected_remote_ref", "observed_remote_ref",
        "candidate_sha", "observed_remote_branch_sha", "observed_tag_target_sha", "target_version",
        "expected_tag", "observed_tag", "observed_release_version", "observed_remote_version",
    )
    if any(facts.get(key) is None for key in required):
        return {"status": "UNAVAILABLE", "reason": "REMOTE_ACTIVATION_FACT_UNAVAILABLE", "evidence_type": "TOOL_OBSERVED"}
    for left, right, code in (
        ("observed_repository_id", "bound_repository_id", "GITHUB_REPOSITORY_MISMATCH"),
        ("observed_remote_ref", "expected_remote_ref", "REMOTE_REF_MISMATCH"),
        ("observed_remote_branch_sha", "candidate_sha", "REMOTE_HEAD_MISMATCH"),
        ("observed_tag_target_sha", "candidate_sha", "REMOTE_TAG_TARGET_MISMATCH"),
        ("observed_tag", "expected_tag", "REMOTE_RELEASE_VERSION_MISMATCH"),
        ("observed_release_version", "target_version", "REMOTE_RELEASE_VERSION_MISMATCH"),
        ("observed_remote_version", "target_version", "REMOTE_VERSION_MISMATCH"),
    ):
        if facts[left] != facts[right]:
            return {"status": "FAILED", "reason": code, "evidence_type": "TOOL_OBSERVED"}
    for expected, observed, code in (
        ("expected_artifact_sha256", "observed_artifact_sha256", "REMOTE_ARTIFACT_SHA_MISMATCH"),
        ("expected_artifact_size_bytes", "observed_artifact_size_bytes", "REMOTE_ARTIFACT_SIZE_MISMATCH"),
    ):
        if facts.get(expected) is not None:
            if facts.get(observed) is None:
                return {"status": "UNAVAILABLE", "reason": "REMOTE_ACTIVATION_FACT_UNAVAILABLE", "evidence_type": "TOOL_OBSERVED"}
            if facts[expected] != facts[observed]:
                return {"status": "FAILED", "reason": code, "evidence_type": "TOOL_OBSERVED"}
    return {"status": "VERIFIED", "reason": "REMOTE_ACTIVATION_VERIFIED", "evidence_type": "TOOL_OBSERVED", "candidate_sha": facts["candidate_sha"]}
