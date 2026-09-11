from __future__ import annotations

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
