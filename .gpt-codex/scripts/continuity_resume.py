from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_continuity_resume(repo_root: Path, selected_repository_id: str) -> dict[str, Any]:
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
    return {
        "status": "LATEST_SYNCED_REMOTE_STATE",
        "repository_id": str(selected_repository_id),
        "project_context_id": control.get("project_context_id"),
        "control": control,
        "state": state,
        "continuity": continuity,
        "active_work_unit": state.get("active_work_unit"),
        "remote_reverification_required": True,
    }
