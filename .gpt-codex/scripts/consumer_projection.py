from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


MANIFEST_RELATIVE_PATH = PurePosixPath(".gpt-codex/release/consumer-projection-manifest.json")
ALLOWED_CLASSIFICATIONS = {
    "CONSUMER_REQUIRED",
    "MANAGEMENT_ONLY",
    "DEVELOPMENT_HISTORY",
    "RELEASE_METADATA",
    "GENERATED_ARTIFACT",
    "LOCAL_ONLY",
}
LOCAL_ONLY_PARTS = {
    ".git",
    ".worktrees",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}
LOCAL_ONLY_SUFFIXES = {".pyc", ".pyo"}
SECRET_PATTERNS = (
    re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
)
_MANAGEMENT_RECORD_CLASSIFICATIONS = frozenset({
    "FRAMEWORK_MANAGEMENT", "SELF_MANAGED", "FRAMEWORK_MANAGEMENT_METADATA",
    "DERIVED_OBSERVATION_ONLY",
    "PROJECT_EVOLUTION_ENROLLMENT", "PROJECT_EVOLUTION_OBSERVATION",
})


def _contains_management_evolution_record(value: object) -> bool:
    if isinstance(value, list):
        return any(_contains_management_evolution_record(item) for item in value)
    if not isinstance(value, Mapping):
        return False
    roots = value.get("roots")
    if (
        value.get("framework_management_only") is True
        or value.get("governance_profile") == "FRAMEWORK_MANAGEMENT"
        or value.get("framework_role") == "SELF_MANAGED"
        or (isinstance(roots, Mapping) and roots.get("framework_role") == "SELF_MANAGED")
        or value.get("classification") in _MANAGEMENT_RECORD_CLASSIFICATIONS
        or value.get("explicit_enrollment") is True
        or "enrollment_id" in value
        or "enrollment_status" in value
    ):
        return True
    return any(_contains_management_evolution_record(item) for item in value.values())


class ProjectionValidationError(ValueError):
    """Raised when a consumer projection is incomplete or unsafe."""


def _relative_key(path: Path) -> str:
    return PurePosixPath(path.as_posix()).as_posix()


def _normalise_manifest_key(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "*" in value or "?" in value:
        return None
    return path.as_posix()


def _normalise_manifest_prefix(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value or not value.endswith("/"):
        return None
    if any(character in value for character in "*?[]"):
        return None
    path = PurePosixPath(value[:-1])
    if (
        not value[:-1]
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
        or f"{path.as_posix()}/" != value
    ):
        return None
    return value


def _resolve_projection_classification(
    path: str,
    exact_paths: Mapping[str, str],
    prefix_defaults: Mapping[str, str],
) -> str | None:
    exact = exact_paths.get(path)
    if exact is not None:
        return exact
    matches = [prefix for prefix in prefix_defaults if path.startswith(prefix)]
    if not matches:
        return None
    return prefix_defaults[max(matches, key=len)]


def load_projection_manifest(root: Path) -> dict[str, Any]:
    path = Path(root) / Path(*MANIFEST_RELATIVE_PATH.parts)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectionValidationError(f"cannot load projection manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ProjectionValidationError("projection manifest must be a JSON object")
    return manifest


def _iter_non_local_files(root: Path) -> list[str]:
    root = Path(root)
    result: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in LOCAL_ONLY_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() in LOCAL_ONLY_SUFFIXES:
            continue
        result.append(_relative_key(relative))
    return sorted(result)


def audit_projection_paths(root: Path, manifest: Mapping[str, object]) -> dict[str, list[str]]:
    root = Path(root)
    raw_paths = manifest.get("paths")
    raw_prefix_defaults = manifest.get("prefix_defaults", {})
    invalid_classifications: list[str] = []
    manifest_paths: dict[str, str] = {}
    prefix_defaults: dict[str, str] = {}
    if not isinstance(raw_paths, Mapping):
        invalid_classifications.append("paths")
        raw_paths = {}
    for raw_key, classification in raw_paths.items():
        key = _normalise_manifest_key(raw_key)
        if key is None or classification not in ALLOWED_CLASSIFICATIONS:
            invalid_classifications.append(str(raw_key))
            continue
        manifest_paths[key] = str(classification)
    if not isinstance(raw_prefix_defaults, Mapping):
        invalid_classifications.append("prefix_defaults")
        raw_prefix_defaults = {}
    for raw_prefix, classification in raw_prefix_defaults.items():
        prefix = _normalise_manifest_prefix(raw_prefix)
        if (
            prefix is None
            or classification not in ALLOWED_CLASSIFICATIONS
            or classification == "CONSUMER_REQUIRED"
        ):
            invalid_classifications.append(str(raw_prefix))
            continue
        prefix_defaults[prefix] = str(classification)

    actual_paths = set(_iter_non_local_files(root))
    unknown_paths = sorted(
        path
        for path in actual_paths
        if _resolve_projection_classification(path, manifest_paths, prefix_defaults) is None
    )
    missing_required_paths = sorted(
        key for key, classification in manifest_paths.items()
        if classification == "CONSUMER_REQUIRED" and not (root / Path(*PurePosixPath(key).parts)).is_file()
    )
    return {
        "unknown_paths": unknown_paths,
        "missing_required_paths": missing_required_paths,
        "invalid_classifications": sorted(set(invalid_classifications)),
    }


def build_consumer_inventory(root: Path, manifest: Mapping[str, object]) -> list[str]:
    audit = audit_projection_paths(root, manifest)
    failures = [item for values in audit.values() for item in values]
    if failures:
        raise ProjectionValidationError(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    paths = manifest.get("paths") or {}
    return sorted(
        key for key, classification in paths.items()
        if classification == "CONSUMER_REQUIRED"
    )


def stage_consumer_projection(
    root: Path,
    staging_root: Path,
    manifest: Mapping[str, object],
    *,
    production_excludes: tuple[str, ...] | list[str] = (),
) -> list[str]:
    root = Path(root).resolve()
    staging_root = Path(staging_root).resolve()
    try:
        staging_root.relative_to(root)
    except ValueError:
        pass
    else:
        raise ProjectionValidationError("staging root must be outside the Management Repository")
    if staging_root.exists() and any(staging_root.iterdir()):
        raise ProjectionValidationError(f"staging root is not empty: {staging_root}")
    staging_root.mkdir(parents=True, exist_ok=True)
    inventory = build_consumer_inventory(root, manifest)
    excluded_roots = tuple(production_excludes)
    inventory = [
        relative
        for relative in inventory
        if not any(relative == excluded or relative.startswith(excluded + "/") for excluded in excluded_roots)
    ]
    for relative in inventory:
        source = root / Path(*PurePosixPath(relative).parts)
        target = staging_root / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return inventory


def scan_consumer_boundary(
    staging_root: Path,
    manifest: Mapping[str, object] | None = None,
) -> dict[str, list[str]]:
    contamination = (manifest or {}).get("contamination") or {}
    forbidden_values = contamination.get("forbidden_values") or []
    if not isinstance(forbidden_values, list) or not all(isinstance(value, str) for value in forbidden_values):
        raise ProjectionValidationError("manifest contamination.forbidden_values must be a string list")
    staging_root = Path(staging_root)
    management_identity_hits: list[str] = []
    management_file_hits: list[str] = []
    secret_hits: list[str] = []
    unsafe_path_hits: list[str] = []
    for path in sorted(p for p in staging_root.rglob("*") if p.is_file()):
        relative = _relative_key(path.relative_to(staging_root))
        if relative in {".gpt-codex/CONTROL.json", ".gpt-codex/STATE.json"}:
            management_file_hits.append(relative)
        if relative.startswith(".gpt-codex/evidence/") or relative.startswith(".gpt-codex/results/"):
            management_file_hits.append(relative)
        if any(part in LOCAL_ONLY_PARTS for part in PurePosixPath(relative).parts):
            unsafe_path_hits.append(relative)
        if path.suffix.lower() in {".zip", ".pyc", ".pyo"}:
            unsafe_path_hits.append(relative)
        data = path.read_bytes()
        if any(needle.encode("utf-8") in data for needle in forbidden_values):
            management_identity_hits.append(relative)
        if path.suffix.lower() == ".json":
            try:
                record = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                record = None
            if _contains_management_evolution_record(record):
                management_identity_hits.append(relative)
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            secret_hits.append(relative)
    return {
        "management_identity_hits": sorted(set(management_identity_hits)),
        "management_file_hits": sorted(set(management_file_hits)),
        "secret_hits": sorted(set(secret_hits)),
        "unsafe_path_hits": sorted(set(unsafe_path_hits)),
    }


def compare_projection_to_zip(
    staging_root: Path,
    zip_path: Path,
    archive_prefix: str,
) -> dict[str, object]:
    staging_root = Path(staging_root)
    prefix = archive_prefix.rstrip("/") + "/"
    staged = {
        _relative_key(path.relative_to(staging_root)): path.read_bytes()
        for path in staging_root.rglob("*")
        if path.is_file()
    }
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        archived = {
            name[len(prefix):]: archive.read(name)
            for name in names
            if name.startswith(prefix) and not name.endswith("/")
        }
    missing = sorted(set(staged) - set(archived))
    extra = sorted(set(archived) - set(staged))
    mismatched = sorted(key for key in set(staged) & set(archived) if staged[key] != archived[key])
    return {
        "match": not (missing or extra or mismatched),
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched,
    }
