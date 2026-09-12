import json
from pathlib import Path, PurePosixPath
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


def _normalise_relative(value: str) -> str:
    return PurePosixPath(value.replace("\\", "/")).as_posix()


def _is_safe_relative(value: str) -> bool:
    candidate = PurePosixPath(value)
    return (
        not candidate.is_absolute()
        and ".." not in candidate.parts
        and not (candidate.parts and candidate.parts[0].endswith(":"))
    )


def path_belongs_to_module(path: str, module: dict[str, Any]) -> bool:
    candidate = _normalise_relative(path)
    if not _is_safe_relative(candidate):
        return False
    for raw_prefix in module.get("paths") or []:
        prefix = _normalise_relative(raw_prefix).rstrip("/")
        if not _is_safe_relative(prefix):
            continue
        if candidate == prefix or candidate.startswith(prefix + "/"):
            return True
    return False


def affected_modules(project_map: dict[str, Any], changed_paths: list[str]) -> list[str]:
    module_ids = {
        module_id
        for module in project_map.get("modules", [])
        if isinstance(module, dict)
        and isinstance(module_id := module.get("id"), str)
        and any(path_belongs_to_module(path, module) for path in changed_paths)
    }
    return sorted(module_ids)


def module_map_read_paths(
    project_map: dict[str, Any], module_ids: list[str]
) -> list[str]:
    paths = []
    for module_id in module_ids:
        module = module_by_id(project_map, module_id)
        if module is not None and isinstance(module.get("module_map"), str):
            paths.append(module["module_map"])
    return paths


def classify_map_route(
    candidate_module_ids: list[str],
    stale_module_ids: list[str],
    map_exists: bool = True,
) -> str:
    if not map_exists:
        return "MAP_MISSING"
    if not candidate_module_ids:
        return "MAP_MISS"
    if set(candidate_module_ids).intersection(stale_module_ids):
        return "MAP_PARTIAL"
    return "MAP_HIT"
