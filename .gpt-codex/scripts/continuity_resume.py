from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from project_navigation import (
    affected_modules,
    classify_map_route,
    load_project_map,
    module_map_read_paths,
    validate_navigation_identity,
)


RESUME_RELATIVE_PATH = Path("continuity") / "RESUME.json"


def load_resume_checkpoint(gov: Path) -> dict[str, Any] | None:
    checkpoint_path = Path(gov) / RESUME_RELATIVE_PATH
    if not checkpoint_path.exists():
        return None
    try:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("RESUME_CHECKPOINT_INVALID") from exc
    if not isinstance(checkpoint, dict):
        raise ValueError("RESUME_CHECKPOINT_INVALID")
    if checkpoint.get("schema_version") != 1:
        raise ValueError("RESUME_CHECKPOINT_SCHEMA_UNSUPPORTED")
    if checkpoint.get("authority") != "DERIVED_CACHE":
        raise ValueError("RESUME_CHECKPOINT_AUTHORITY_INVALID")
    return checkpoint


def fingerprint_file(path: Path) -> str | None:
    source = Path(path)
    if not source.is_file():
        return None
    return "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()


def compare_context_sources(root: Path, checkpoint: dict[str, Any]) -> tuple[list[str], list[str]]:
    context_sources = checkpoint.get("context_sources", {})
    if not isinstance(context_sources, list):
        return [], []
    invalidated_context: list[str] = []
    required_reads: list[str] = []
    resolved_root = Path(root).resolve()
    for source in context_sources:
        if not isinstance(source, dict):
            continue
        relative_path = source.get("path")
        expected_fingerprint = source.get("fingerprint")
        if not isinstance(relative_path, str):
            continue
        supplied_path = Path(relative_path)
        if supplied_path.is_absolute() or ".." in supplied_path.parts:
            raise ValueError(f"RESUME_CONTEXT_SOURCE_PATH_INVALID:{relative_path}")
        candidate = (resolved_root / supplied_path).resolve()
        try:
            candidate.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(f"RESUME_CONTEXT_SOURCE_PATH_INVALID:{relative_path}") from exc
        current_fingerprint = fingerprint_file(candidate)
        if current_fingerprint is None:
            required_reads.append(relative_path)
        elif current_fingerprint != expected_fingerprint:
            invalidated_context.append(relative_path)
    return invalidated_context, required_reads


def load_continuity_resume(
    repo_root: Path,
    selected_repository_id: str,
    *,
    changed_paths: list[str] | None = None,
    candidate_module_ids: list[str] | None = None,
    observed_remote_head_sha: str | None = None,
    work_reachable: bool = True,
    attestation_is_management_only: bool = True,
    attestation_references_work: bool = True,
    generic_tree_matches: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root)
    gov = root / ".gpt-codex"
    try:
        control = json.loads((gov / "CONTROL.json").read_text(encoding="utf-8"))
        state = json.loads((gov / "STATE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("CONTINUITY_MACHINE_STATE_INVALID") from exc
    github = control.get("github")
    if not isinstance(github, dict) or set(("repository_id", "repository_full_name", "default_branch")) - set(github):
        raise ValueError("GITHUB_REPOSITORY_UNBOUND")
    if str(github["repository_id"]) != str(selected_repository_id):
        raise ValueError("GITHUB_REPOSITORY_MISMATCH")
    continuity = state.get("continuity")
    if not isinstance(continuity, dict):
        raise ValueError("CONTINUITY_STATE_MISSING")
    if continuity.get("sync_status") != "SYNCED":
        return {
            "status": "LOCAL_UNSYNCED_STATE",
            "repository_id": str(selected_repository_id),
            "state": state,
            "continuity": continuity,
        }
    baseline_sha = continuity.get("latest_verified_remote_sha")
    if observed_remote_head_sha is not None and not (
        baseline_sha
        and work_reachable
        and attestation_is_management_only
        and attestation_references_work
        and generic_tree_matches
    ):
        return {
            "status": "RECONCILIATION_REQUIRED",
            "repository_id": str(selected_repository_id),
            "verified_baseline_sha": baseline_sha,
            "current_attestation_head": observed_remote_head_sha,
            "reconciliation_required": True,
            "state": state,
            "continuity": continuity,
        }

    project_map = load_project_map(root)
    if project_map is not None:
        validate_navigation_identity(project_map, control)

    checkpoint = load_resume_checkpoint(gov)
    if checkpoint is None:
        checkpoint_working_set: dict[str, Any] = {}
        invalidated_context: list[str] = []
        missing_context: list[str] = []
    else:
        validate_navigation_identity(checkpoint, control)
        checkpoint_working_set = checkpoint.get("working_set")
        if not isinstance(checkpoint_working_set, dict):
            checkpoint_working_set = {}
        detected_invalidated, missing_context = compare_context_sources(root, checkpoint)
        invalidated_context = [
            path
            for path in checkpoint_working_set.get("invalidated_context", [])
            if isinstance(path, str)
        ] + detected_invalidated

    hot_modules = [
        module_id
        for module_id in checkpoint_working_set.get("hot_modules", [])
        if isinstance(module_id, str)
    ]
    hot_files = [
        path
        for path in checkpoint_working_set.get("hot_files", [])
        if isinstance(path, str)
    ]
    next_required_reads = [
        path
        for path in checkpoint_working_set.get("next_required_reads", [])
        if isinstance(path, str)
    ]
    changed = [path for path in changed_paths or [] if isinstance(path, str)]
    candidate_modules = [
        module_id
        for module_id in (candidate_module_ids if candidate_module_ids is not None else hot_modules)
        if isinstance(module_id, str)
    ]

    stale_modules = []
    module_map_reads = []
    if project_map is not None:
        changed_modules = affected_modules(project_map, changed)
        stale_modules = sorted(set(candidate_modules).intersection(changed_modules))
        module_map_reads = module_map_read_paths(project_map, stale_modules)
    map_route = classify_map_route(
        candidate_modules,
        stale_modules,
        map_exists=project_map is not None,
    )

    required_reads = list(dict.fromkeys(
        invalidated_context
        + missing_context
        + next_required_reads
        + [path for path in changed if path in hot_files]
        + module_map_reads
    ))
    invalidated_context = list(dict.fromkeys(invalidated_context))
    if checkpoint is None or project_map is None:
        resume_mode = "COLD_RESUME"
    elif required_reads or map_route == "MAP_PARTIAL":
        resume_mode = "DELTA_RESUME"
    else:
        resume_mode = "FAST_RESUME"

    return {
        "status": "LATEST_SYNCED_REMOTE_STATE",
        "repository_id": str(selected_repository_id),
        "project_context_id": control.get("project_context_id"),
        "control": control,
        "state": state,
        "continuity": continuity,
        "active_work_unit": state.get("active_work_unit"),
        "remote_reverification_required": True,
        "verified_baseline_sha": baseline_sha,
        "current_attestation_head": observed_remote_head_sha,
        "reconciliation_required": False,
        "resume_mode": resume_mode,
        "map_route": map_route,
        "candidate_modules": candidate_modules,
        "stale_modules": stale_modules,
        "module_map_reads": module_map_reads,
        "required_reads": required_reads,
        "hot_modules": hot_modules,
        "hot_files": hot_files,
        "invalidated_context": invalidated_context,
    }
