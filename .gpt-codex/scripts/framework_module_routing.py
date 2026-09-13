from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


REGISTRY_PATH = ".gpt-codex/framework-modules/REGISTRY.json"
MODULE_FIELDS = (
    "MODULE_ID",
    "VERSION",
    "PURPOSE",
    "RESPONSIBILITIES",
    "NON_RESPONSIBILITIES",
    "OWNED_ASSETS",
    "ENTRY_POINTS",
    "INPUTS",
    "OUTPUTS",
    "DEPENDS_ON",
    "USED_BY",
    "INVARIANTS",
    "PERMISSIONS",
    "CHANGE_RISK",
    "REQUIRED_TESTS",
    "RELATED_MODULES",
)
MODULE_FIELD_SET = frozenset(MODULE_FIELDS)
SELECTOR_TYPES = frozenset({"EXACT_PATH", "PATH_PREFIX", "LOGICAL_ASSET"})
REGISTRY_STATUSES = frozenset({"ACTIVE", "INACTIVE"})
FAILURE_ORDER = (
    "MODULE_REGISTRY_INVALID",
    "MODULE_DESCRIPTOR_INVALID",
    "MODULE_DEPENDENCY_INVALID",
    "MODULE_OWNERSHIP_CONFLICT",
)
_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


class ModuleRoutingError(ValueError):
    code: str
    details: dict[str, Any]

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


@dataclass(frozen=True)
class RouteDecision:
    outcome: str
    primary_module: str | None
    affected_modules: tuple[str, ...]
    why_cross_module: str | None
    contracts_affected: tuple[str, ...]
    invariants_affected: tuple[str, ...]
    required_tests: tuple[str, ...]


def _error(code: str, message: str, **details: Any) -> ModuleRoutingError:
    return ModuleRoutingError(code, message, details=details)


def _normalize_path(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("path must be a string")
    value = value.replace("\\", "/")
    if not value or value.startswith("/") or _DRIVE_PREFIX.match(value):
        raise ValueError("path must be repository-relative")
    components = value.split("/")
    if any(component in {"", ".", ".."} for component in components):
        raise ValueError("path contains an unsafe component")
    return "/".join(components)


def _normalize_logical_asset(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("logical asset must be a string")
    value = value.strip()
    if not value:
        raise ValueError("logical asset must be non-empty")
    return value


def _normalize_selector(selector: Any) -> tuple[str, str]:
    if not isinstance(selector, Mapping) or set(selector) != {"type", "value"}:
        raise ValueError("selector must contain exactly type and value")
    selector_type = selector["type"]
    if not isinstance(selector_type, str) or selector_type not in SELECTOR_TYPES:
        raise ValueError("selector type is invalid")
    value = selector["value"]
    if selector_type == "LOGICAL_ASSET":
        return selector_type, _normalize_logical_asset(value)
    return selector_type, _normalize_path(value)


def _load_json(path: Path, code: str, message: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise _error(code, message, path=str(path)) from exc


def _validate_registry_shape(registry: Any) -> bool:
    if not isinstance(registry, Mapping):
        return False
    if set(registry) != {"schema_version", "authority", "framework_version", "modules"}:
        return False
    if registry.get("schema_version") != 1:
        return False
    if registry.get("authority") != "FRAMEWORK_MODULE_REGISTRY":
        return False
    framework_version = registry.get("framework_version")
    if not isinstance(framework_version, str) or not framework_version:
        return False
    modules = registry.get("modules")
    if not isinstance(modules, list):
        return False
    for entry in modules:
        if not isinstance(entry, Mapping) or set(entry) != {"module_id", "descriptor", "status"}:
            return False
        if not isinstance(entry.get("module_id"), str) or not entry["module_id"]:
            return False
        if entry.get("status") not in REGISTRY_STATUSES:
            return False
        try:
            descriptor = _normalize_path(entry["descriptor"])
        except (KeyError, ValueError):
            return False
        if not descriptor.endswith(".json"):
            return False
    return True


def load_registry(root: Path) -> dict[str, Any]:
    path = Path(root) / REGISTRY_PATH
    registry = _load_json(path, "MODULE_REGISTRY_INVALID", "registry is invalid")
    if not _validate_registry_shape(registry):
        raise _error("MODULE_REGISTRY_INVALID", "registry is invalid")
    return dict(registry)


def load_module_descriptor(root: Path, descriptor_path: str) -> dict[str, Any]:
    try:
        normalized = _normalize_path(descriptor_path)
    except ValueError as exc:
        raise _error("MODULE_DESCRIPTOR_INVALID", "descriptor is invalid", path=descriptor_path) from exc
    path = Path(root) / normalized
    descriptor = _load_json(path, "MODULE_DESCRIPTOR_INVALID", "descriptor is invalid")
    if not isinstance(descriptor, Mapping):
        raise _error("MODULE_DESCRIPTOR_INVALID", "descriptor is invalid", path=descriptor_path)
    return dict(descriptor)


def _descriptor_shape_valid(descriptor: Any) -> bool:
    if not isinstance(descriptor, Mapping) or set(descriptor) != MODULE_FIELD_SET:
        return False
    for field in ("MODULE_ID", "VERSION", "PURPOSE", "CHANGE_RISK"):
        if not isinstance(descriptor[field], str) or not descriptor[field]:
            return False
    for field in (
        "RESPONSIBILITIES",
        "NON_RESPONSIBILITIES",
        "ENTRY_POINTS",
        "INPUTS",
        "OUTPUTS",
        "DEPENDS_ON",
        "USED_BY",
        "INVARIANTS",
        "PERMISSIONS",
        "REQUIRED_TESTS",
        "RELATED_MODULES",
    ):
        if not isinstance(descriptor[field], list) or not all(
            isinstance(item, str) for item in descriptor[field]
        ):
            return False
    if not isinstance(descriptor["OWNED_ASSETS"], list):
        return False
    return True


def _required_test_is_valid(root: Path, value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    looks_like_path = (
        "/" in value or "\\" in value or value.startswith(".") or value.endswith((".py", ".json"))
    )
    if not looks_like_path:
        return True
    try:
        normalized = _normalize_path(value)
    except ValueError:
        return False
    return (Path(root) / normalized).is_file()


def _descriptor_checks(root: Path, entry: Mapping[str, Any]) -> tuple[dict[str, Any] | None, bool, bool]:
    descriptor_error = False
    selector_error = False
    try:
        descriptor = load_module_descriptor(root, str(entry["descriptor"]))
    except ModuleRoutingError:
        return None, True, False
    if not _descriptor_shape_valid(descriptor):
        return descriptor, True, False
    if descriptor["MODULE_ID"] != entry["module_id"]:
        descriptor_error = True
    for selector in descriptor["OWNED_ASSETS"]:
        try:
            _normalize_selector(selector)
        except (ValueError, KeyError):
            selector_error = True
    if any(not _required_test_is_valid(root, test) for test in descriptor["REQUIRED_TESTS"]):
        descriptor_error = True
    return descriptor, descriptor_error, selector_error


def _selectors_conflict(left: tuple[str, str], right: tuple[str, str]) -> bool:
    left_type, left_value = left
    right_type, right_value = right
    if left_type == "LOGICAL_ASSET" or right_type == "LOGICAL_ASSET":
        return left_type == right_type == "LOGICAL_ASSET" and left_value == right_value
    if left_type == right_type == "EXACT_PATH":
        return left_value == right_value
    if left_type == "PATH_PREFIX" and right_type == "EXACT_PATH":
        return right_value == left_value or right_value.startswith(left_value + "/")
    if left_type == "EXACT_PATH" and right_type == "PATH_PREFIX":
        return left_value == right_value or left_value.startswith(right_value + "/")
    if left_type == right_type == "PATH_PREFIX":
        return (
            left_value == right_value
            or left_value.startswith(right_value + "/")
            or right_value.startswith(left_value + "/")
        )
    return False


def _registry_entries(registry: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [entry for entry in registry.get("modules", []) if isinstance(entry, Mapping)]


def validate_registry(
    root: Path,
    registry: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    def add(code: str) -> None:
        if code not in errors:
            errors.append(code)

    if registry is None:
        try:
            registry = load_registry(root)
        except ModuleRoutingError:
            return ["MODULE_REGISTRY_INVALID"]
    if not _validate_registry_shape(registry):
        return ["MODULE_REGISTRY_INVALID"]

    entries = _registry_entries(registry)
    module_ids = [entry["module_id"] for entry in entries]
    if len(module_ids) != len(set(module_ids)):
        add("MODULE_REGISTRY_INVALID")

    descriptors: dict[str, dict[str, Any]] = {}
    selectors: list[tuple[str, tuple[str, str]]] = []
    for entry in entries:
        descriptor, descriptor_error, selector_error = _descriptor_checks(root, entry)
        if descriptor_error or selector_error:
            add("MODULE_DESCRIPTOR_INVALID")
        if descriptor is None:
            continue
        descriptors[entry["module_id"]] = descriptor
        for selector in descriptor["OWNED_ASSETS"]:
            try:
                selectors.append((entry["module_id"], _normalize_selector(selector)))
            except (ValueError, KeyError):
                pass

    known_ids = set(module_ids)
    for module_id, descriptor in descriptors.items():
        dependencies = descriptor["DEPENDS_ON"]
        used_by = descriptor["USED_BY"]
        if any(dependency not in known_ids for dependency in dependencies):
            add("MODULE_DEPENDENCY_INVALID")
        if any(consumer not in known_ids for consumer in used_by):
            add("MODULE_DEPENDENCY_INVALID")
        for dependency in dependencies:
            if dependency in descriptors and module_id not in descriptors[dependency]["USED_BY"]:
                add("MODULE_DEPENDENCY_INVALID")
        for consumer in used_by:
            if consumer in descriptors and module_id not in descriptors[consumer]["DEPENDS_ON"]:
                add("MODULE_DEPENDENCY_INVALID")

    for producer_id, producer in descriptors.items():
        for contract in producer["OUTPUTS"]:
            for consumer_id, consumer in descriptors.items():
                if consumer_id == producer_id or contract not in consumer["INPUTS"]:
                    continue
                if (
                    consumer_id not in producer["USED_BY"]
                    or producer_id not in consumer["DEPENDS_ON"]
                ):
                    add("MODULE_DEPENDENCY_INVALID")

    for index, (left_module, left_selector) in enumerate(selectors):
        for right_module, right_selector in selectors[index + 1 :]:
            if left_module != right_module and _selectors_conflict(left_selector, right_selector):
                add("MODULE_OWNERSHIP_CONFLICT")
    return errors


def _descriptor_index(root: Path, registry: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in _registry_entries(registry):
        module_id = entry.get("module_id")
        if isinstance(module_id, str):
            index[module_id] = load_module_descriptor(root, str(entry.get("descriptor", "")))
    return index


def classify_changed_assets(
    root: Path,
    registry: Mapping[str, Any],
    planned_assets: Sequence[str],
) -> dict[str, tuple[str, ...]]:
    descriptors = _descriptor_index(root, registry)
    normalized_assets: list[tuple[str, str | None, str | None]] = []
    for asset in planned_assets:
        normalized_path: str | None = None
        normalized_logical: str | None = None
        try:
            normalized_path = _normalize_path(asset)
        except (TypeError, ValueError):
            pass
        try:
            normalized_logical = _normalize_logical_asset(asset)
        except (TypeError, ValueError):
            pass
        if normalized_path is None and normalized_logical is None:
            exc = ValueError("planned asset is neither a safe path nor a logical identifier")
            raise _error("MODULE_ROUTE_UNRESOLVED", "planned asset is invalid", asset=asset) from exc
        key = normalized_path if normalized_path is not None else normalized_logical
        normalized_assets.append((key, normalized_path, normalized_logical))

    result: dict[str, tuple[str, ...]] = {}
    for key, candidate_path, candidate_logical in normalized_assets:
        owners: set[str] = set()
        for module_id, descriptor in descriptors.items():
            for selector in descriptor.get("OWNED_ASSETS", []):
                try:
                    selector_type, selector_value = _normalize_selector(selector)
                except (ValueError, KeyError):
                    continue
                if (
                    selector_type == "EXACT_PATH"
                    and candidate_path is not None
                    and candidate_path == selector_value
                ):
                    owners.add(module_id)
                elif (
                    selector_type == "PATH_PREFIX"
                    and candidate_path is not None
                    and (
                        candidate_path == selector_value
                        or candidate_path.startswith(selector_value + "/")
                    )
                ):
                    owners.add(module_id)
                elif (
                    selector_type == "LOGICAL_ASSET"
                    and candidate_logical is not None
                    and candidate_logical == selector_value
                ):
                    owners.add(module_id)
        result[key] = tuple(sorted(owners))
    return result


def _stable_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def required_tests_for_change(
    root: Path,
    registry: Mapping[str, Any],
    module_ids: Sequence[str],
) -> tuple[str, ...]:
    descriptors = _descriptor_index(root, registry)
    tests: set[str] = set()
    for module_id in sorted(set(module_ids)):
        descriptor = descriptors.get(module_id)
        if descriptor is None:
            raise _error("MODULE_DESCRIPTOR_INVALID", "descriptor is invalid", module_id=module_id)
        for test in descriptor["REQUIRED_TESTS"]:
            if not _required_test_is_valid(root, test):
                raise _error("MODULE_DESCRIPTOR_INVALID", "descriptor is invalid", test=test)
            if "/" in test or "\\" in test or test.startswith(".") or test.endswith((".py", ".json")):
                tests.add(_normalize_path(test))
            else:
                tests.add(test.strip())
    return tuple(sorted(tests))


def detect_cross_module_change(
    primary_module: str,
    affected_modules: Sequence[str],
    *,
    contracts_affected: Sequence[str] = (),
    invariants_affected: Sequence[str] = (),
) -> RouteDecision:
    affected = tuple(sorted(set(affected_modules)))
    contracts = _stable_unique(contracts_affected)
    invariants = _stable_unique(invariants_affected)
    is_cross_module = len(affected) > 1
    return RouteDecision(
        outcome="CROSS_MODULE_CHANGE_REQUIRED" if is_cross_module else "MODULE_ROUTE",
        primary_module=primary_module,
        affected_modules=affected,
        why_cross_module=(
            "foreign owned asset or consumed contract is affected"
            if is_cross_module
            else None
        ),
        contracts_affected=contracts,
        invariants_affected=invariants,
        required_tests=(),
    )


def route_responsibility(
    root: Path,
    candidate_module_id: str,
    responsibility: str,
    *,
    planned_assets: Sequence[str] = (),
    contracts_affected: Sequence[str] = (),
    invariants_affected: Sequence[str] = (),
) -> RouteDecision:
    registry = load_registry(root)
    errors = validate_registry(root, registry)
    if errors:
        raise _error(errors[0], "registry validation failed")

    entries = {entry["module_id"]: entry for entry in _registry_entries(registry)}
    entry = entries.get(candidate_module_id)
    if entry is None:
        raise _error(
            "MODULE_NOT_REGISTERED",
            "module is not registered",
            module_id=candidate_module_id,
        )
    if entry["status"] != "ACTIVE":
        raise _error(
            "MODULE_ROUTE_UNRESOLVED",
            "module is not an active route target",
            module_id=candidate_module_id,
        )
    descriptor = load_module_descriptor(root, entry["descriptor"])
    if responsibility not in descriptor["RESPONSIBILITIES"]:
        raise _error(
            "MODULE_ROUTE_UNRESOLVED",
            "responsibility is not declared",
            responsibility=responsibility,
        )

    owners_by_asset = classify_changed_assets(root, registry, planned_assets)
    if any(not owners for owners in owners_by_asset.values()):
        raise _error("MODULE_ROUTE_UNRESOLVED", "planned asset has no primary owner")
    if any(len(owners) > 1 for owners in owners_by_asset.values()):
        raise _error("MODULE_OWNERSHIP_CONFLICT", "planned asset has multiple primary owners")

    affected = {candidate_module_id}
    for owners in owners_by_asset.values():
        affected.update(owners)

    for contract in contracts_affected:
        if contract not in descriptor["OUTPUTS"]:
            raise _error(
                "MODULE_ROUTE_UNRESOLVED",
                "contract is not a declared output",
                contract=contract,
            )
        for consumer_id, consumer_entry in entries.items():
            if consumer_id == candidate_module_id or consumer_entry["status"] != "ACTIVE":
                continue
            consumer = load_module_descriptor(root, consumer_entry["descriptor"])
            if contract in consumer["INPUTS"]:
                affected.add(consumer_id)

    decision = detect_cross_module_change(
        candidate_module_id,
        tuple(affected),
        contracts_affected=contracts_affected,
        invariants_affected=invariants_affected,
    )
    return replace(
        decision,
        required_tests=required_tests_for_change(root, registry, decision.affected_modules),
    )
