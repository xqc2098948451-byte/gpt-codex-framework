from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


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
    }
