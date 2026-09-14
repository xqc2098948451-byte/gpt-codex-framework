"""Derived, non-authoritative execution telemetry vocabulary."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Mapping, Sequence
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
RECOMMENDED_RETENTION_DAYS = 30

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
    "access_token", "host_id", "user_id", "source_contents", "raw_diff",
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


def _required_bounded_string(value: object, limit: int, code: str) -> str:
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
        if (
            event.provenance.completeness != "LOW_CONFIDENCE"
            or event.provenance.producer_run_id is None
            or event.provenance.producer_sequence is None
        ):
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
        slot_id=_required_bounded_string(payload.get("slot_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
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
        source=_required_bounded_string(payload.get("source"), MAX_ENUM_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        provenance=provenance,
        instruction_id=_bounded_string(payload.get("instruction_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        result_id=_bounded_string(payload.get("result_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        finding_id=_bounded_string(payload.get("finding_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        review_request_id=_bounded_string(payload.get("review_request_id"), MAX_ID_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
        authoritative_record_ref=_bounded_string(payload.get("authoritative_record_ref"), MAX_REF_LENGTH, "MALFORMED_TELEMETRY_EVENT"),
    )
    provisional = TelemetryEvent(logical_key="", **values)
    return TelemetryEvent(logical_key=logical_idempotency_key(provisional), **values)


@dataclass(frozen=True, slots=True)
class AuthoritativeSnapshot:
    project_context_id: str | None
    state_revision: int | None
    head_sha: str | None
    correlation_ref: str | None
    result_status: str | None
    git_relation: str = "UNKNOWN"

    def __post_init__(self) -> None:
        if self.git_relation not in {"MATCH", "ANCESTOR", "DIVERGED", "UNKNOWN"}:
            raise TelemetryValidationError("MALFORMED_TELEMETRY_EVENT")


def repeat_subject_key(event: TelemetryEvent) -> str:
    correlation = correlation_ref_for(event)
    if event.authoritative_record_ref is None and correlation is None:
        values: list[object] = [
            event.event_class,
            event.slot_id,
            event.provenance.producer_run_id,
        ]
        return sha256(json.dumps(values, separators=(",", ":")).encode("utf-8")).hexdigest()
    values: list[object] = [
        event.event_class, event.authoritative_record_ref,
        event.provenance.observed_state_revision, event.provenance.observed_head_sha,
        event.slot_id, correlation,
    ]
    return sha256(json.dumps(values, separators=(",", ":")).encode("utf-8")).hexdigest()


def classify_ordering(
    event: TelemetryEvent,
    *,
    authoritative: AuthoritativeSnapshot | None,
    previous_related_event: TelemetryEvent | None,
) -> str:
    correlation = correlation_ref_for(event)
    if authoritative is not None:
        if authoritative.project_context_id is not None and event.project_context_id != authoritative.project_context_id:
            return "INCONSISTENT"
        if authoritative.git_relation == "DIVERGED" and event.state_revision == authoritative.state_revision:
            return "INCONSISTENT"
        if authoritative.correlation_ref is not None and correlation is not None and authoritative.correlation_ref == correlation:
            if authoritative.result_status is not None and event.result_status is not None and authoritative.result_status != event.result_status:
                return "INCONSISTENT"
        if (authoritative.state_revision is not None and event.state_revision is not None and event.state_revision < authoritative.state_revision) or authoritative.git_relation == "ANCESTOR":
            return "STALE"
    if previous_related_event is not None and repeat_subject_key(event) == repeat_subject_key(previous_related_event):
        if event.state_revision is not None and previous_related_event.state_revision is not None and event.state_revision < previous_related_event.state_revision:
            return "OUT_OF_ORDER"
        if (event.provenance.producer_run_id is not None and event.provenance.producer_run_id == previous_related_event.provenance.producer_run_id and event.provenance.producer_sequence is not None and previous_related_event.provenance.producer_sequence is not None and event.provenance.producer_sequence < previous_related_event.provenance.producer_sequence):
            return "OUT_OF_ORDER"
        if event.timestamp < previous_related_event.timestamp:
            return "LATE"
    return "CURRENT"


class TelemetryCollector:
    """Caller-owned, in-memory append-only derived observations."""

    def __init__(self) -> None:
        self._events: list[TelemetryEvent] = []
        self._by_logical_key: dict[str, TelemetryEvent] = {}
        self._earliest_by_repeat_subject: dict[str, TelemetryEvent] = {}
        self._latest_by_repeat_subject: dict[str, TelemetryEvent] = {}

    @staticmethod
    def _canonical(event: TelemetryEvent) -> TelemetryEvent:
        return replace(event, event_id="", logical_key="", arrival_timestamp=None, ordering_status="CURRENT", observation_kind="PRIMARY", repeats_event_id=None, supersedes_observation_id=None)

    def emit(
        self,
        event: TelemetryEvent,
        *,
        authoritative: AuthoritativeSnapshot | None = None,
        arrival_timestamp: datetime | None = None,
    ) -> TelemetryEvent:
        subject = repeat_subject_key(event)
        previous = self._latest_by_repeat_subject.get(subject)
        ordering = classify_ordering(event, authoritative=authoritative, previous_related_event=previous)
        emitted = replace(event, ordering_status=ordering, arrival_timestamp=arrival_timestamp)
        existing = self._by_logical_key.get(event.logical_key)
        if existing is not None and self._canonical(existing) == self._canonical(emitted):
            return existing
        earliest = self._earliest_by_repeat_subject.get(subject)
        if earliest is not None:
            emitted = replace(emitted, observation_kind="REPEAT", repeats_event_id=earliest.event_id)
        self._events.append(emitted)
        self._by_logical_key[event.logical_key] = emitted
        self._earliest_by_repeat_subject.setdefault(subject, emitted)
        self._latest_by_repeat_subject[subject] = emitted
        return emitted

    def events(self) -> tuple[TelemetryEvent, ...]:
        return tuple(self._events)


def retention_deadline(event: TelemetryEvent) -> datetime:
    """Return policy metadata without scheduling or deleting telemetry."""
    return event.timestamp + timedelta(days=RECOMMENDED_RETENTION_DAYS)


def telemetry_availability(events: Sequence[TelemetryEvent], logical_key: str) -> str:
    if any(event.logical_key == logical_key for event in events):
        return "TELEMETRY_AVAILABLE"
    return "TELEMETRY_ABSENT"


def unknown_detail_from_telemetry(events: Sequence[TelemetryEvent], logical_key: str) -> str:
    if telemetry_availability(events, logical_key) == "TELEMETRY_ABSENT":
        return "UNKNOWN_FROM_TELEMETRY"
    return "TELEMETRY_AVAILABLE"
