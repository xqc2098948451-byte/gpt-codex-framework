import json
from pathlib import Path
from typing import Any


PROJECT_MAP_RELATIVE = Path(".gpt-codex/navigation/PROJECT_MAP.json")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"NAVIGATION_INVALID_JSON:{path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"NAVIGATION_INVALID_OBJECT:{path}")
    return payload


def load_project_map(root: Path) -> dict[str, Any] | None:
    path = root / PROJECT_MAP_RELATIVE
    if not path.exists():
        return None
    project_map = _load_json(path)
    if project_map.get("schema_version") != 1:
        raise ValueError("NAVIGATION_SCHEMA_UNSUPPORTED")
    if project_map.get("authority") != "DERIVED_NAVIGATION_INDEX":
        raise ValueError("NAVIGATION_AUTHORITY_INVALID")

    module_ids = [
        module.get("id")
        for module in project_map.get("modules", [])
        if isinstance(module, dict)
    ]
    if len(module_ids) != len(set(module_ids)):
        raise ValueError("NAVIGATION_DUPLICATE_MODULE_ID")
    return project_map


def load_module_map(root: Path, relative_path: str) -> dict[str, Any]:
    supplied_path = Path(relative_path)
    if supplied_path.is_absolute() or ".." in supplied_path.parts:
        raise ValueError(f"MODULE_MAP_PATH_INVALID:{relative_path}")

    resolved_root = root.resolve()
    candidate = (resolved_root / supplied_path).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"MODULE_MAP_PATH_INVALID:{relative_path}") from exc

    module_map = _load_json(candidate)
    if module_map.get("schema_version") != 1:
        raise ValueError("MODULE_MAP_SCHEMA_UNSUPPORTED")
    if module_map.get("authority") != "DERIVED_NAVIGATION_INDEX":
        raise ValueError("MODULE_MAP_AUTHORITY_INVALID")
    return module_map


def validate_navigation_identity(
    navigation: dict[str, Any], control: dict[str, Any]
) -> None:
    if navigation.get("project_id") != control.get("project_id"):
        raise ValueError("NAVIGATION_PROJECT_ID_MISMATCH")
    if navigation.get("project_context_id") != control.get("project_context_id"):
        raise ValueError("NAVIGATION_PROJECT_CONTEXT_MISMATCH")

    navigation_repository_id = navigation.get("repository_id")
    control_repository_id = (control.get("github") or {}).get("repository_id")
    if (
        navigation_repository_id is not None
        and control_repository_id is not None
        and navigation_repository_id != control_repository_id
    ):
        raise ValueError("NAVIGATION_REPOSITORY_MISMATCH")


def module_by_id(
    project_map: dict[str, Any], module_id: str
) -> dict[str, Any] | None:
    matches = [
        module
        for module in project_map.get("modules", [])
        if isinstance(module, dict) and module.get("id") == module_id
    ]
    if len(matches) != 1:
        return None
    return matches[0]
