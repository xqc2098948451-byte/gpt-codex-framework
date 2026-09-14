"""Derived, non-authoritative execution telemetry vocabulary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Mapping
from uuid import uuid4

TELEMETRY_CLASSIFICATION = "DERIVED_OBSERVATION_ONLY"

EVENT_CLASSES = frozenset({
    "INSTRUCTION_ISSUED",
    "SLOT_ASSIGNED",
    "SLOT_REASSIGNED",
    "EXECUTION_STARTED",
    "EXECUTION_COMPLETED",
    "EXECUTION_BLOCKED",
    "REVIEW_REQUESTED",
    "REVIEW_RESULT",
    "FINDING_CREATED",
    "REMEDIATION_AUTHORIZED",
    "RE_REVIEW_RESULT",
    "REMOTE_EVIDENCE_OBSERVED",
    "PUBLICATION_BOUNDARY_TRANSITION",
})

MAX_ID_LENGTH = 128
MAX_REF_LENGTH = 512
MAX_TUPLE_ITEMS = 16
MAX_ENUM_LENGTH = 64

COMMON_FIELDS = frozenset({
    "event_class", "work_unit_id", "slot_id", "role", "state_revision",
    "project_context_id", "branch_ref", "base_sha", "head_sha",
    "result_status", "review_gate", "evidence_refs", "source", "provenance",
})
OPTIONAL_CORRELATION_FIELDS = frozenset({
    "instruction_id", "result_id", "finding_id", "review_request_id",
    "authoritative_record_ref",
})
PROHIBITED_AUTHORITY_FIELDS = frozenset({
    "authority_claim", "authorizes", "permission_grant",
    "state_transition_authorization", "slot_assignment_mutation",
    "publication_authority_claim",
})
UNSAFE_CONTENT_FIELDS = frozenset({
    "raw_prompt", "reasoning", "chain_of_thought", "credential", "token",
    "environment", "source_content", "diff", "tool_payload",
})
PROVENANCE_FIELDS = frozenset({
    "classification", "source_channel", "source_record_refs",
    "observed_state_revision", "observed_head_sha", "redaction_actions",
    "completeness", "producer_run_id", "producer_sequence",
})
COMPLETENESS = frozenset({"COMPLETE", "PARTIAL", "LOW_CONFIDENCE"})


class TelemetryValidationError(ValueError):
    """A bounded telemetry event failed normalization."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class TelemetryProvenance:
    classification: str
    collector_id: str
    collector_version: str
    source_channel: str
    source_record_refs: tuple[str, ...]
    observed_state_revision: int | None
    observed_head_sha: str | None
    collected_at: datetime
    redaction_actions: tuple[str, ...]
    completeness: str
    producer_run_id: str | None = None
    producer_sequence: int | None = None


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    event_id: str
    event_class: str
    work_unit_id: str | None
    slot_id: str
    role: str | None
    state_revision: int | None
    project_context_id: str | None
    branch_ref: str | None
    base_sha: str | None
    head_sha: str | None
    result_status: str | None
    review_gate: str | None
    evidence_refs: tuple[str, ...]
    timestamp: datetime
    source: str
    provenance: TelemetryProvenance
    logical_key: str
    instruction_id: str | None = None
    result_id: str | None = None
    finding_id: str | None = None
    review_request_id: str | None = None
    authoritative_record_ref: str | None = None
    observation_kind: str = "PRIMARY"
    repeats_event_id: str | None = None
    supersedes_observation_id: str | None = None
    ordering_status: str = "CURRENT"
    arrival_timestamp: datetime | None = None

    @property
    def observed_timestamp(self) -> datetime:
        return self.timestamp


def _bounded_string(value: object, limit: int, code: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or len(value) > limit:
        raise TelemetryValidationError(code)
    return value


def _bounded_tuple(value: object, limit: int) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or len(value) > MAX_TUPLE_ITEMS:
        raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
    result = tuple(_bounded_string(item, limit, "INVALID_TELEMETRY_PROVENANCE") for item in value)
    return result


def _normalize_provenance(raw: object, collector_id: str, collector_version: str, timestamp: datetime) -> TelemetryProvenance:
    if not isinstance(raw, Mapping) or set(raw) - PROVENANCE_FIELDS:
        raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
    classification = raw.get("classification")
    completeness = raw.get("completeness")
    if classification != "DERIVED" or completeness not in COMPLETENESS:
        raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
    revision = raw.get("observed_state_revision")
    sequence = raw.get("producer_sequence")
    if revision is not None and (not isinstance(revision, int) or isinstance(revision, bool) or revision < 0):
        raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
    if sequence is not None and (not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0):
        raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
    return TelemetryProvenance(
        classification="DERIVED",
        collector_id=_bounded_string(collector_id, MAX_ID_LENGTH, "INVALID_TELEMETRY_PROVENANCE"),
        collector_version=_bounded_string(collector_version, MAX_ENUM_LENGTH, "INVALID_TELEMETRY_PROVENANCE"),
        source_channel=_bounded_string(raw.get("source_channel"), MAX_ENUM_LENGTH, "INVALID_TELEMETRY_PROVENANCE"),
        source_record_refs=_bounded_tuple(raw.get("source_record_refs"), MAX_REF_LENGTH),
        observed_state_revision=revision,
        observed_head_sha=_bounded_string(raw.get("observed_head_sha"), MAX_REF_LENGTH, "INVALID_TELEMETRY_PROVENANCE"),
        collected_at=timestamp,
        redaction_actions=_bounded_tuple(raw.get("redaction_actions"), MAX_ENUM_LENGTH),
        completeness=completeness,
        producer_run_id=_bounded_string(raw.get("producer_run_id"), MAX_ID_LENGTH, "INVALID_TELEMETRY_PROVENANCE"),
        producer_sequence=sequence,
    )


def correlation_ref_for(event: TelemetryEvent) -> str | None:
    fields = {
        "INSTRUCTION_ISSUED": event.instruction_id,
        "REVIEW_REQUESTED": event.review_request_id,
        "FINDING_CREATED": event.finding_id,
        "REVIEW_RESULT": event.result_id,
        "RE_REVIEW_RESULT": event.result_id,
        "EXECUTION_COMPLETED": event.result_id,
        "EXECUTION_BLOCKED": event.result_id,
    }
    return fields.get(event.event_class, event.authoritative_record_ref)


def logical_idempotency_key(event: TelemetryEvent) -> str:
    correlation = correlation_ref_for(event)
    values: list[object] = [
        event.event_class, event.source, event.authoritative_record_ref,
        event.provenance.observed_state_revision, event.provenance.observed_head_sha,
        event.slot_id, correlation,
    ]
    if event.authoritative_record_ref is None and correlation is None:
        if event.provenance.completeness != "LOW_CONFIDENCE":
            raise TelemetryValidationError("INVALID_TELEMETRY_PROVENANCE")
        values.extend([event.provenance.producer_run_id, event.provenance.producer_sequence])
    return sha256(json.dumps(values, separators=(",", ":"), sort_keys=False).encode("utf-8")).hexdigest()


def normalize_event(payload: Mapping[str, object], *, collector_id: str, collector_version: str, timestamp: datetime) -> TelemetryEvent:
    if not isinstance(payload, Mapping):
        raise TelemetryValidationError("MALFORMED_TELEMETRY_EVENT")
    keys = set(payload)
    if keys & PROHIBITED_AUTHORITY_FIELDS:
        raise TelemetryValidationError("PROHIBITED_AUTHORITY_CLAIM")
    if keys & UNSAFE_CONTENT_FIELDS:
        raise TelemetryValidationError("UNSAFE_TELEMETRY_CONTENT")
    if keys - COMMON_FIELDS - OPTIONAL_CORRELATION_FIELDS or not COMMON_FIELDS.issubset(keys):
        raise TelemetryValidationError("MALFORMED_TELEMETRY_EVENT")
    event_class = payload.get("event_class")
    if event_class not in EVENT_CLASSES:
        raise TelemetryValidationError("MALFORMED_TELEMETRY_EVENT")
    revision = payload.get("state_revision")
    if revision is not None and (not isinstance(revision, int) or isinstance(revision, bool) or revision < 0):
        raise TelemetryValidationError("MALFORMED_TELEMETRY_EVENT")
    provenance = _normalize_provenance(payload.get("provenance"), collector_id, collector_version, timestamp)
    values = dict(
        event_id=str(uuid4()), event_class=event_class,
        work_unit_id=_bounded_string(payload.get("work_unit_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        slot_id=_bounded_string(payload.get("slot_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        role=_bounded_string(payload.get("role"), MAX_ENUM_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        state_revision=revision,
        project_context_id=_bounded_string(payload.get("project_context_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        branch_ref=_bounded_string(payload.get("branch_ref"), MAX_REF_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        base_sha=_bounded_string(payload.get("base_sha"), MAX_REF_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        head_sha=_bounded_string(payload.get("head_sha"), MAX_REF_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        result_status=_bounded_string(payload.get("result_status"), MAX_ENUM_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        review_gate=_bounded_string(payload.get("review_gate"), MAX_ENUM_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        evidence_refs=_bounded_tuple(payload.get("evidence_refs"), MAX_REF_LENGTH),
        timestamp=timestamp,
        source=_bounded_string(payload.get("source"), MAX_ENUM_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        provenance=provenance,
        instruction_id=_bounded_string(payload.get("instruction_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        result_id=_bounded_string(payload.get("result_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        finding_id=_bounded_string(payload.get("finding_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        review_request_id=_bounded_string(payload.get("review_request_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        authoritative_record_ref=_bounded_string(payload.get("authoritative_record_ref"), MAX_REF_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
    )
    provisional = TelemetryEvent(logical_key="", **values)
    return TelemetryEvent(logical_key=logical_idempotency_key(provisional), **values)
