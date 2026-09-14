from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Any, Mapping

KERNEL_VERSION = "2.0.0"
SCHEMA_VERSION = 1

STATES = {
    "PROPOSED", "AUTHORIZED", "ACTIVE", "VERIFYING", "COMPLETE",
    "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED",
}

ALLOWED_TRANSITIONS = {
    "PROPOSED": {"AUTHORIZED", "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"},
    "AUTHORIZED": {"ACTIVE", "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"},
    "ACTIVE": {"VERIFYING", "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"},
    "VERIFYING": {"COMPLETE", "ACTIVE", "BLOCKED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"},
    "COMPLETE": set(),
    "BLOCKED": {"ACTIVE", "AUTHORIZED", "AWAITING_APPROVAL", "RECONCILIATION_REQUIRED"},
    "AWAITING_APPROVAL": {"AUTHORIZED", "ACTIVE", "BLOCKED", "RECONCILIATION_REQUIRED"},
    "RECONCILIATION_REQUIRED": {"PROPOSED", "AUTHORIZED", "ACTIVE", "BLOCKED"},
}

PERMISSION_RANK = {"DENY": 0, "APPROVAL_REQUIRED": 1, "ALLOW": 2}
EVIDENCE_SOURCES = {"TOOL_OBSERVED", "USER_ASSERTED", "SYSTEM_DERIVED", "MODEL_INFERRED"}
EXTENSION_KINDS = {"SKILL", "GUARDRAIL", "FITNESS"}
MATURITY = {"PROJECT_LOCAL", "HARVEST_CANDIDATE", "SHARED_CANDIDATE", "BUILTIN", "DEPRECATED", "RETIRED"}
COMPAT_RESULTS = {"ADOPTED", "NO_ACTION", "OPTIONAL_REUSE", "RECOMMENDED_UPGRADE", "REQUIRED_MIGRATION", "CONFLICT"}
COMPLETION_GATES = {"NONE", "GPT_DECISION", "USER_APPROVAL"}
REASON_TYPES = {"OBSERVED_EVIDENCE", "EXPLICIT_REQUIREMENT", "CREDIBLE_RISK"}
GOVERNANCE_PROFILES = {"MINIMAL", "STANDARD", "EXTENDED"}
_EVOLUTION_SOURCE_FIELDS = frozenset({
    "classification", "framework_version", "source_provenance",
    "compatibility_rules", "migration_available",
})
_COMMIT_SHA = re.compile(r"^[0-9a-fA-F]{40}$")


@dataclass(frozen=True)
class EvolutionSourceDecision:
    classification: str
    reason: str
    source: Mapping[str, Any] | None


def _freeze_evolution_source_snapshot(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_evolution_source_snapshot(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_evolution_source_snapshot(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze_evolution_source_snapshot(item) for item in value)
    return value


def validate_framework_evolution_source(source: Mapping[str, Any]) -> EvolutionSourceDecision:
    """Validate a Framework publication without granting Project authority."""
    if not isinstance(source, Mapping) or set(source) != _EVOLUTION_SOURCE_FIELDS:
        return EvolutionSourceDecision("FRAMEWORK_SOURCE_INVALID", "FRAMEWORK_SOURCE_INVALID", None)
    framework_version = source.get("framework_version")
    provenance = source.get("source_provenance")
    compatibility_rules = source.get("compatibility_rules")
    commit_sha = provenance.get("commit_sha") if isinstance(provenance, Mapping) else None
    if (
        source.get("classification") != "READ_ONLY_EVOLUTION_SOURCE"
        or not isinstance(framework_version, str)
        or not framework_version.strip()
        or len(framework_version) > 128
        or not isinstance(provenance, Mapping)
        or not isinstance(commit_sha, str)
        or not _COMMIT_SHA.fullmatch(commit_sha)
        or not isinstance(compatibility_rules, Mapping)
        or not isinstance(source.get("migration_available"), bool)
    ):
        return EvolutionSourceDecision("FRAMEWORK_SOURCE_INVALID", "FRAMEWORK_SOURCE_INVALID", None)
    return EvolutionSourceDecision(
        "READ_ONLY_EVOLUTION_SOURCE",
        "FRAMEWORK_SOURCE_VALID",
        _freeze_evolution_source_snapshot(source),
    )


def can_transition(current: str, target: str) -> bool:
    return current in STATES and target in ALLOWED_TRANSITIONS[current]


def revision_matches(current_revision: int, expected_revision: int) -> bool:
    return isinstance(current_revision, int) and current_revision >= 0 and current_revision == expected_revision


def permission_narrows(parent: str, child: str) -> bool:
    if parent not in PERMISSION_RANK or child not in PERMISSION_RANK:
        return False
    return PERMISSION_RANK[child] <= PERMISSION_RANK[parent]


def evidence_can_authorize(source: str, target_state: str | None = None, high_impact: bool = False) -> bool:
    if source not in EVIDENCE_SOURCES:
        return False
    if source == "MODEL_INFERRED" and (target_state == "COMPLETE" or high_impact):
        return False
    return True


def project_extension_has_provenance(ext: dict) -> bool:
    if ext.get("maturity") != "PROJECT_LOCAL":
        return True
    prov = ext.get("provenance") or {}
    refs = prov.get("evidence_refs") or []
    return bool(prov.get("reason_type") in REASON_TYPES and prov.get("reason") and refs and prov.get("retire_when"))


def harvest_candidate_is_safe(candidate: dict) -> bool:
    return (
        candidate.get("maturity") == "HARVEST_CANDIDATE"
        and candidate.get("source_project_authoritative") is True
        and candidate.get("source_project_write_allowed") is False
        and candidate.get("promotion_status") != "BUILTIN"
    )


def framework_evaluation_is_adoption(control: dict) -> bool:
    fw = control.get("framework") or {}
    return fw.get("last_evaluated_version") == fw.get("adopted_version") and fw.get("evaluation_result") == "ADOPTED"


def check_common_version(obj: dict) -> list[str]:
    errors = []
    if obj.get("kernel_version") != KERNEL_VERSION:
        errors.append(f"kernel_version must be {KERNEL_VERSION}")
    if obj.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    return errors


def transition_has_sufficient_evidence(target_state: str, evidence_sources: list[str]) -> bool:
    if target_state != "COMPLETE":
        return True
    if not evidence_sources:
        return False
    return any(source in EVIDENCE_SOURCES and source != "MODEL_INFERRED" for source in evidence_sources)
