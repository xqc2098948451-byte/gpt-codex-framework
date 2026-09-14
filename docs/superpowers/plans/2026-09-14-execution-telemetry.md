# Execution Telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal, sanitized, derived-only execution-telemetry contract that observes governed work without creating governance authority.

**Architecture:** `framework-core` will own one standard-library Python module that validates and normalizes telemetry events and an in-memory, caller-owned append-only collector. The collector returns derived observations and never writes CONTROL, STATE, Work Units, Result/Evidence, Git facts, slot facts, files, or a repository event history. Consumer projection is a separate `release-projection` concern: the implementation assets are management-only until a consumer requirement is independently proven.

**Tech Stack:** Python 3 standard library (`dataclasses`, `datetime`, `hashlib`, `json`, `uuid`, `unittest`); existing Framework Module Registry and consumer-projection validator.

**Spec:** docs/superpowers/specs/2026-09-13-execution-telemetry-design.md

## Global Constraints

- Telemetry is `DERIVED_OBSERVATION_ONLY`; CONTROL, STATE, Work Unit, Instruction/Result, Evidence, Git, publication, and future P0-5 slot facts remain authoritative.
- Telemetry must not authorize mutation, approval, review acceptance, finding closure, remediation, routing, role elevation, slot assignment/reassignment, state transition, adoption, release, or publication.
- Use no database, message bus, daemon, background service, scheduler, dashboard, network collector, analytics service, scoring engine, learning loop, agent-budget mechanism, or repository-tracked event log.
- Runtime events exist only in the caller-owned `TelemetryCollector` process memory. Persisting, forwarding, retaining, or deleting records is outside this implementation and not required for Framework correctness.
- `event_id` identifies one immutable emitted record. The deterministic logical idempotency key is separate and consists of `event_class`, `source`, `authoritative_record_ref`, `observed_state_revision`, `observed_head_sha`, `slot_id`, and `correlation_ref`.
- `slot_id` and `source` are required, non-empty bounded strings. `slot_id="NONE"` is the only explicit no-slot value; Python `None` is not a substitute for it. The Design-intentionally nullable observation fields remain nullable: `work_unit_id`, `role`, `state_revision`, `project_context_id`, `branch_ref`, `base_sha`, `head_sha`, `result_status`, and `review_gate`.
- When neither `authoritative_record_ref` nor `correlation_ref_for(event)` provides durable identity, the logical key retains both `producer_run_id` and monotonic `producer_sequence`. That fallback is valid only with `completeness="LOW_CONFIDENCE"`, a non-empty bounded `producer_run_id`, and a non-negative integer `producer_sequence`; missing either provenance value raises `INVALID_TELEMETRY_PROVENANCE`. Never construct an identity from `(None, None)`.
- Use authoritative state revision, Result/Evidence correlation, Git ancestry, and publication facts before telemetry time. A late, stale, or inconsistent event is observational only and cannot roll back an authority record.
- `TELEMETRY_ABSENT` means no telemetry observation is available, not that the governed action did not occur. `UNKNOWN_FROM_TELEMETRY` is observational incompleteness, not a governance failure.
- `slot_id` accepts `NONE`; P0-6 only observes future P0-5 slot facts and must not implement lifecycle, assignment, reassignment, transition, or recovery.
- Reject/redact raw prompts, reasoning, credentials, tokens, host/user identifiers, full environments, personal data, unbounded free text, source contents, diffs, and arbitrary tool payloads. Store only bounded IDs, enums, statuses, and references.
- The recommended telemetry retention value is 30 days. Expiration is a pure policy calculation; it neither deletes data nor changes Result/Evidence retention or Framework correctness.
- Do not add a JSON schema. A closed Python dataclass/API validator is sufficient because the sole runtime seam is in-process, caller-owned, standard-library Python; no external interchange, file persistence, or consumer payload exists in scope.
- Every physical implementation asset must be registered with an exact owner before routing uses it. No fuzzy/logical fallback is permitted for a path.
- During implementation, classify the Design and Plan as `DEVELOPMENT_HISTORY`; classify the telemetry script and its test as `MANAGEMENT_ONLY` until a separately authorized consumer requirement proves otherwise.

## File and ownership map

| Path | Change | Owning module and reason | Projection classification |
| --- | --- | --- | --- |
| `.gpt-codex/framework-modules/modules/framework-core.json` | Modify | `framework-core`; add exact ownership of the telemetry script/test and list its required test. This descriptor is already owned by the module-prefix selector. | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/execution_telemetry.py` | Create | `framework-core`; exact `OWNED_ASSETS` entry is added before the file is routed. It provides derived framework-governance observation only. | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_execution_telemetry.py` | Create | `framework-core`; exact `OWNED_ASSETS` entry and `REQUIRED_TESTS` entry are added before the file is routed. | MANAGEMENT_ONLY |
| `.gpt-codex/release/consumer-projection-manifest.json` | Modify | `release-projection`; it already owns this exact path. Its authority is classification management only; it gains no telemetry authority. | MANAGEMENT_ONLY |
| `docs/superpowers/specs/2026-09-13-execution-telemetry-design.md` | Modify only in the projection manifest | Development history; no production semantics change. | DEVELOPMENT_HISTORY |
| `docs/superpowers/plans/2026-09-14-execution-telemetry.md` | Modify only in the projection manifest | Development history; no production semantics change. | DEVELOPMENT_HISTORY |

No change is planned to `CONTROL`, `STATE`, Work Unit schemas/templates, Instruction/Result schemas, Evidence, Git continuity, P0-5 navigation-continuity assets, publication contracts, or validation entry points. `framework-validation`, `role-communication`, `navigation-continuity`, and `git-continuity` are observed-contract boundaries only, not implementation owners.

`.gpt-codex/release/consumer-projection-manifest.json` is canonically
`MANAGEMENT_ONLY` as the existing manifest self-classification. Changing entries
inside that manifest does not change the manifest file's own classification.

After Task 1, the exact ownership proof is:

```python
owners = classify_changed_assets(
    ROOT,
    load_registry(ROOT),
    [
        ".gpt-codex/scripts/execution_telemetry.py",
        ".gpt-codex/tests/test_execution_telemetry.py",
    ],
)
assert owners[".gpt-codex/scripts/execution_telemetry.py"] == ("framework-core",)
assert owners[".gpt-codex/tests/test_execution_telemetry.py"] == ("framework-core",)
```

This proves the assets do not route as unowned. The implementation route is
`CROSS_MODULE_CHANGE_REQUIRED` only in Task 6, where the existing
`release-projection` manifest is changed. That cross-module change affects the
consumer-projection contract and its invariant that management-only assets do
not become consumer authority; it does not change any observed governance
contract.

---

### Task 1: Register framework-core telemetry assets and contract vocabulary

**Files:**
- Modify: `.gpt-codex/framework-modules/modules/framework-core.json`
- Create: `.gpt-codex/scripts/execution_telemetry.py`
- Create: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: `EVENT_CLASSES: frozenset[str]`, `COMMON_FIELDS: frozenset[str]`, `OPTIONAL_CORRELATION_FIELDS: frozenset[str]`, and `PROHIBITED_AUTHORITY_CLAIMS: frozenset[str]` from `execution_telemetry.py`.
- Produces: exact `framework-core` ownership for both new paths and a `REQUIRED_TESTS` entry for `.gpt-codex/tests/test_execution_telemetry.py`.
- Consumes: `classify_changed_assets(root, registry, planned_assets)` and `route_responsibility(root, candidate_module_id, responsibility, planned_assets=...)` from `framework_module_routing.py`.
- Produces test fixtures `NOW`, `LATER`, and `valid_payload(**overrides) -> dict[str, object]`. `valid_payload` returns every common field with bounded representative values, `slot_id="NONE"`, `evidence_refs=[]`, and `provenance={"classification": "DERIVED"}` before applying `overrides`.

- [ ] **Step 1: Write the failing registry-and-vocabulary test**

```python
def test_framework_core_owns_the_telemetry_paths_and_exposes_all_event_classes(self):
    registry = load_registry(ROOT)
    assets = [
        ".gpt-codex/scripts/execution_telemetry.py",
        ".gpt-codex/tests/test_execution_telemetry.py",
    ]
    owners = classify_changed_assets(ROOT, registry, assets)
    self.assertEqual(owners[assets[0]], ("framework-core",))
    self.assertEqual(owners[assets[1]], ("framework-core",))
    self.assertEqual(module.EVENT_CLASSES, frozenset({
        "INSTRUCTION_ISSUED", "SLOT_ASSIGNED", "SLOT_REASSIGNED",
        "EXECUTION_STARTED", "EXECUTION_COMPLETED", "EXECUTION_BLOCKED",
        "REVIEW_REQUESTED", "REVIEW_RESULT", "FINDING_CREATED",
        "REMEDIATION_AUTHORIZED", "RE_REVIEW_RESULT",
        "REMOTE_EVIDENCE_OBSERVED", "PUBLICATION_BOUNDARY_TRANSITION",
    }))
```

- [ ] **Step 2: Run the test to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because `execution_telemetry.py` and its exact descriptor ownership entries do not yet exist.

- [ ] **Step 3: Add the minimal ownership and vocabulary implementation**

Add these two `EXACT_PATH` selectors and the test path to `framework-core.json`:

```json
{"type": "EXACT_PATH", "value": ".gpt-codex/scripts/execution_telemetry.py"},
{"type": "EXACT_PATH", "value": ".gpt-codex/tests/test_execution_telemetry.py"}
```

Create the module constants with the exact closed sets used by the test; set
`COMMON_FIELDS` to the 14 Design fields and
`OPTIONAL_CORRELATION_FIELDS` to `instruction_id`, `result_id`, `finding_id`,
`review_request_id`, and `authoritative_record_ref`. Set
`PROHIBITED_AUTHORITY_CLAIMS` to the prohibited actions in Global Constraints.

- [ ] **Step 4: Run the ownership and route proof to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py && python -c "import sys; from pathlib import Path; sys.path.insert(0, '.gpt-codex/scripts'); from framework_module_routing import route_responsibility; print(route_responsibility(Path('.'), 'framework-core', 'framework governance', planned_assets=['.gpt-codex/scripts/execution_telemetry.py', '.gpt-codex/tests/test_execution_telemetry.py']).outcome)"`

Expected: PASS and `MODULE_ROUTE`.

- [ ] **Step 5: Commit the independently testable registry foundation**

```bash
git add .gpt-codex/framework-modules/modules/framework-core.json .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "feat: register execution telemetry contract"
```

### Task 2: Normalize and validate source-bound telemetry events

**Files:**
- Modify: `.gpt-codex/scripts/execution_telemetry.py`
- Modify: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: frozen, slotted `TelemetryProvenance` and `TelemetryEvent` values with no retained caller mapping/list/object.
- Produces: `normalize_event(payload: Mapping[str, object], *, collector_id: str, collector_version: str, timestamp: datetime) -> TelemetryEvent`, `correlation_ref_for(event: TelemetryEvent) -> str | None`, and `logical_idempotency_key(event: TelemetryEvent) -> str`.
- Produces: `TelemetryValidationError(code: str)` for `MALFORMED_TELEMETRY_EVENT`, `PROHIBITED_AUTHORITY_CLAIM`, `UNSAFE_TELEMETRY_CONTENT`, and `INVALID_TELEMETRY_PROVENANCE`.
- Produces the test helper `normalized_event(**overrides: object) -> TelemetryEvent` exactly as follows:

```python
def normalized_event(**overrides: object) -> TelemetryEvent:
    values = dict(overrides)
    timestamp = values.pop("timestamp", NOW)
    return normalize_event(
        valid_payload(**values),
        collector_id="collector",
        collector_version="1.0",
        timestamp=timestamp,
    )
```
- Consumes: the closed sets from Task 1 only; it does not read or mutate authoritative records.

- [ ] **Step 1: Write failing normalization and non-authority tests**

```python
def test_normalize_event_requires_common_fields_and_derived_provenance(self):
    event = normalize_event(valid_payload(), collector_id="collector", collector_version="1.0", timestamp=NOW)
    self.assertEqual(event.provenance.classification, "DERIVED")
    self.assertEqual(event.slot_id, "NONE")
    with self.assertRaisesRegex(TelemetryValidationError, "MALFORMED_TELEMETRY_EVENT"):
        normalize_event({"event_class": "EXECUTION_STARTED"}, collector_id="collector", collector_version="1.0", timestamp=NOW)
    for field in ("slot_id", "source"):
        with self.subTest(field=field), self.assertRaisesRegex(TelemetryValidationError, "MALFORMED_TELEMETRY_EVENT"):
            normalize_event(valid_payload(**{field: None}), collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_low_confidence_fallback_requires_run_and_sequence(self):
    fallback = valid_payload(
        event_class="REMOTE_EVIDENCE_OBSERVED",
        result_id=None,
        authoritative_record_ref=None,
        provenance={
            "classification": "DERIVED", "completeness": "LOW_CONFIDENCE",
            "producer_run_id": "run-1", "producer_sequence": 0,
        },
    )
    event = normalize_event(fallback, collector_id="collector", collector_version="1.0", timestamp=NOW)
    self.assertIsNone(correlation_ref_for(event))
    self.assertTrue(event.logical_key)
    for omitted in ("producer_run_id", "producer_sequence"):
        invalid = dict(fallback)
        invalid["provenance"] = dict(fallback["provenance"])
        invalid["provenance"].pop(omitted)
        with self.subTest(omitted=omitted), self.assertRaisesRegex(TelemetryValidationError, "INVALID_TELEMETRY_PROVENANCE"):
            normalize_event(invalid, collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_normalize_event_rejects_authority_claims_and_sensitive_content(self):
    with self.assertRaisesRegex(TelemetryValidationError, "PROHIBITED_AUTHORITY_CLAIM"):
        normalize_event(valid_payload(authority_claim="APPROVAL"), collector_id="collector", collector_version="1.0", timestamp=NOW)
    with self.assertRaisesRegex(TelemetryValidationError, "UNSAFE_TELEMETRY_CONTENT"):
        normalize_event(valid_payload(raw_prompt="secret"), collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_normalized_event_extracts_collector_only_timestamp(self):
    event = normalized_event(timestamp=LATER)
    self.assertEqual(event.timestamp, LATER)
    self.assertNotIn("timestamp", valid_payload())
```

- [ ] **Step 2: Run the normalization tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because `TelemetryEvent`, `normalize_event`, and `TelemetryValidationError` are not implemented.

- [ ] **Step 3: Write the minimal normalization implementation**

```python
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
```

Define `MAX_ID_LENGTH = 128`, `MAX_REF_LENGTH = 512`, `MAX_TUPLE_ITEMS = 16`,
and `MAX_ENUM_LENGTH = 64`. Accept only the known event/common/correlation keys
and the known raw provenance mapping keys. Validate raw input, copy scalar and
tuple values, and construct `TelemetryProvenance`; no nested mapping/list/object
survives. Require `classification == "DERIVED"`, `completeness` in
`{"COMPLETE", "PARTIAL", "LOW_CONFIDENCE"}`, tuple strings within the limits,
and no free-text fields. Check reserved authority fields
`authority_claim`, `authorizes`, `permission_grant`,
`state_transition_authorization`, `slot_assignment_mutation`, and
`publication_authority_claim` first and raise `PROHIBITED_AUTHORITY_CLAIM`.
Then check raw-content fields `raw_prompt`, `reasoning`, `chain_of_thought`,
`credential`, `token`, `environment`, `source_content`, `diff`, and
`tool_payload` and raise `UNSAFE_TELEMETRY_CONTENT`. Other unknown keys raise
`MALFORMED_TELEMETRY_EVENT`. Do not scan ordinary values: `result_status="PASS"`
and publication/review observations remain valid.

`slot_id` and `source` must each be non-empty strings no longer than
`MAX_ID_LENGTH`; reject missing, `None`, empty, or non-string values with
`MALFORMED_TELEMETRY_EVENT`. Accept `slot_id="NONE"` as the explicit no-slot
representation only. Preserve the intentionally nullable common observation
fields listed in Global Constraints.

`correlation_ref_for` uses this closed precedence table: `INSTRUCTION_ISSUED`
uses `instruction_id`; `REVIEW_REQUESTED` uses `review_request_id`;
`FINDING_CREATED` uses `finding_id`; `REVIEW_RESULT`, `RE_REVIEW_RESULT`,
`EXECUTION_COMPLETED`, and `EXECUTION_BLOCKED` use `result_id`; all other
classes use `authoritative_record_ref`. A missing applicable durable reference
returns `None`. `logical_idempotency_key` hashes the canonical tuple
`(event_class, source, authoritative_record_ref, provenance.observed_state_revision,
provenance.observed_head_sha, slot_id, correlation_ref_for(event))`; only when
both authoritative and correlation references are missing it additionally uses
`producer_run_id` and `producer_sequence` and requires `LOW_CONFIDENCE`, a
non-empty bounded producer run ID, and a non-negative producer sequence.
When this fallback is selected, reject missing or invalid run/sequence values
with `INVALID_TELEMETRY_PROVENANCE`; do not create any key from `(None, None)`.

- [ ] **Step 4: Run the normalization suite to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; the normalized event is derived-only and malformed/sensitive/authority-bearing payloads are rejected.

- [ ] **Step 5: Commit normalization**

```bash
git add .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "feat: validate normalized telemetry events"
```

### Task 3: Add repeat identity, immutable ordering inputs, and collector behavior

**Files:**
- Modify: `.gpt-codex/scripts/execution_telemetry.py`
- Modify: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: frozen, slotted `AuthoritativeSnapshot(project_context_id, state_revision, head_sha, correlation_ref, result_status, git_relation="UNKNOWN")`; `git_relation` is exactly one of `MATCH`, `ANCESTOR`, `DIVERGED`, `UNKNOWN` and is supplied by the existing Git authority layer. It intentionally has no `publication_status` field: the accepted event contract has no event-side same-vocabulary publication status.
- Produces: `repeat_subject_key(event: TelemetryEvent) -> str`, `classify_ordering(event: TelemetryEvent, *, authoritative: AuthoritativeSnapshot | None, previous_related_event: TelemetryEvent | None) -> str`, `TelemetryCollector.emit(event: TelemetryEvent, *, authoritative: AuthoritativeSnapshot | None = None, arrival_timestamp: datetime | None = None) -> TelemetryEvent`, and `TelemetryCollector.events() -> tuple[TelemetryEvent, ...]`.
- Consumes: Task 2 final logical-key and correlation APIs; it does not calculate Git ancestry or mutate an authoritative input.

- [ ] **Step 1: Write failing idempotency and chronology tests**

```python
def test_retry_is_one_logical_observation_but_repeat_is_append_only(self):
    collector = TelemetryCollector()
    first = collector.emit(normalized_event())
    retry = collector.emit(normalized_event())
    repeat = collector.emit(normalized_event(timestamp=LATER, source="remote-evidence-read"))
    self.assertEqual(retry.event_id, first.event_id)
    self.assertEqual(len(collector.events()), 2)
    self.assertEqual(repeat.observation_kind, "REPEAT")
    self.assertEqual(repeat.repeats_event_id, first.event_id)

def test_changed_authoritative_fact_is_distinct_and_stale_or_inconsistent_never_rolls_back(self):
    collector = TelemetryCollector()
    first = collector.emit(normalized_event(head_sha="a" * 40), authoritative=AuthoritativeSnapshot(None, 1, "a" * 40, None, None))
    changed = collector.emit(normalized_event(head_sha="b" * 40), authoritative=AuthoritativeSnapshot(None, 2, "b" * 40, None, None))
    stale = collector.emit(normalized_event(head_sha="a" * 40), authoritative=AuthoritativeSnapshot(None, 2, "b" * 40, None, None, "ANCESTOR"))
    self.assertNotEqual(first.logical_key, changed.logical_key)
    self.assertEqual(stale.ordering_status, "STALE")

def test_ordering_statuses_and_immutable_inputs_are_exact(self):
    current = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", state_revision=3, timestamp=NOW)
    self.assertEqual(classify_ordering(current, authoritative=None, previous_related_event=None), "CURRENT")

    previous = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", state_revision=3, timestamp=LATER)
    late = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", state_revision=3, timestamp=NOW)
    self.assertEqual(classify_ordering(late, authoritative=None, previous_related_event=previous), "LATE")

    out_of_order = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", state_revision=2, timestamp=NOW)
    self.assertEqual(classify_ordering(out_of_order, authoritative=None, previous_related_event=previous), "OUT_OF_ORDER")

    snapshot = AuthoritativeSnapshot("ctx-1", 3, None, "result-1", None)
    stale = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", project_context_id="ctx-1", state_revision=2)
    self.assertEqual(classify_ordering(stale, authoritative=snapshot, previous_related_event=None), "STALE")

    inconsistent = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", project_context_id="ctx-other", state_revision=3)
    self.assertEqual(classify_ordering(inconsistent, authoritative=snapshot, previous_related_event=None), "INCONSISTENT")

    overlap = normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", project_context_id="ctx-1", state_revision=2, timestamp=NOW)
    self.assertEqual(classify_ordering(overlap, authoritative=snapshot, previous_related_event=previous), "STALE")
    with self.assertRaises(FrozenInstanceError):
        current.provenance.collector_id = "other"

def test_low_confidence_producer_sequence_is_a_reachable_out_of_order_chain(self):
    collector = TelemetryCollector()
    first = collector.emit(normalized_event(
        event_class="REMOTE_EVIDENCE_OBSERVED", slot_id="NONE",
        result_id=None,
        authoritative_record_ref=None,
        provenance={"classification": "DERIVED", "completeness": "LOW_CONFIDENCE", "producer_run_id": "run-1", "producer_sequence": 5},
    ))
    later_arrival = collector.emit(normalized_event(
        event_class="REMOTE_EVIDENCE_OBSERVED", slot_id="NONE",
        result_id=None,
        authoritative_record_ref=None,
        provenance={"classification": "DERIVED", "completeness": "LOW_CONFIDENCE", "producer_run_id": "run-1", "producer_sequence": 3},
    ))
    self.assertNotEqual(first.logical_key, later_arrival.logical_key)
    self.assertEqual(later_arrival.ordering_status, "OUT_OF_ORDER")

def test_repeat_lineage_uses_earliest_but_chronology_uses_latest_related_observation(self):
    collector = TelemetryCollector()
    e1 = collector.emit(normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", timestamp=NOW))
    e2 = collector.emit(normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", source="remote-evidence-read", timestamp=LATER))
    e3 = collector.emit(normalized_event(event_class="EXECUTION_COMPLETED", result_id="result-1", source="reviewer-read", timestamp=NOW))
    self.assertEqual(e3.repeats_event_id, e1.event_id)
    self.assertEqual(e3.ordering_status, "LATE")
```

- [ ] **Step 2: Run the idempotency and chronology tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because `TelemetryCollector`, logical-key calculation, repeat linkage, and ordering classification are absent.

- [ ] **Step 3: Write the minimal collector implementation**

Use private in-memory dictionaries keyed by Task 2 logical key, repeat-subject
key, and immutable event ID. Keep two logically distinct related-event views:
one map retains the earliest canonical event for stable `repeats_event_id`
lineage, while another retains the latest appended logical observation for
chronology classification. A suppressed retry creates no new logical
observation and updates neither view. Every appended related observation updates
the latest view; pass that latest related observation, not the earliest lineage
event, to `classify_ordering`. `repeat_subject_key` hashes exactly
`(event_class, authoritative_record_ref, provenance.observed_state_revision,
provenance.observed_head_sha, slot_id, correlation_ref_for(event))`; it excludes
source, timestamp, and arrival time. With no durable/correlation identity it
uses the bounded fallback subject `(event_class, slot_id, producer_run_id)` plus
only stable already-required subject components that do not distinguish emitted
sequence items. It must not include `producer_sequence`; consequently sequence
5 followed by sequence 3 in the same producer run is one chronology chain.
Same logical key plus equal canonical payload returns the existing
event and appends nothing. Different logical key plus equal repeat-subject key
appends a `REPEAT` whose `repeats_event_id` is the earliest related event.
Changed repeat-subject key appends `PRIMARY` and may set only telemetry-layer
`supersedes_observation_id`.

Classify in fixed order: `INCONSISTENT`, `STALE`, `OUT_OF_ORDER`, `LATE`,
`CURRENT`. `INCONSISTENT` covers project-context mismatch, `DIVERGED` relation
at the same revision, or matching correlation with conflicting canonical Result
status when both `authoritative.result_status` and `event.result_status` exist.
`PUBLICATION_BOUNDARY_TRANSITION` remains a valid observation event and may be
inconsistent through those meaningful contradictions or causal/correlation
contradiction, but Task 3 performs no direct publication-status equality
comparison: no event-side same-vocabulary field exists. `STALE` covers lower event revision or `ANCESTOR` Git relation.
`OUT_OF_ORDER` covers a lower revision in the same repeat/correlation chain or
a lower sequence in the same producer run only when no `INCONSISTENT` or
`STALE` condition applies. `LATE` covers an earlier event timestamp for the
same repeat subject only after all higher-precedence checks, including
`OUT_OF_ORDER`. `CURRENT` is the remainder. The overlap assertion above proves
that an event lower than both current authoritative STATE and a prior related
telemetry event is `STALE`, not `OUT_OF_ORDER`. Use `dataclasses.replace` to
return a new frozen event with `arrival_timestamp`; never mutate event,
snapshot, or prior event.

- [ ] **Step 4: Run the collector suite to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; retries do not multiply logical lifecycle observations, changed-source repeats remain append-only, every ordering status has an exact input, and frozen event/provenance values cannot change authoritative input.

- [ ] **Step 5: Commit collector semantics**

```bash
git add .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "feat: add telemetry idempotency and ordering"
```

### Task 4: Enforce privacy minimization and non-authoritative retention policy

**Files:**
- Modify: `.gpt-codex/scripts/execution_telemetry.py`
- Modify: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: `RECOMMENDED_RETENTION_DAYS: int = 30`, `retention_deadline(event: TelemetryEvent) -> datetime`, and `telemetry_availability(events: Sequence[TelemetryEvent], logical_key: str) -> str`.
- Produces: `TELEMETRY_ABSENT` and `UNKNOWN_FROM_TELEMETRY` as derived query outcomes only.
- Consumes: Task 2 normalization and Task 3 collector without adding storage, deletion, scheduling, or authoritative fallback.

- [ ] **Step 1: Write failing privacy, retention, and absence tests**

```python
def test_redaction_rejects_all_forbidden_raw_content_classes(self):
    for key in ("raw_prompt", "chain_of_thought", "credential", "access_token", "host_id", "user_id", "tool_payload", "source_contents", "raw_diff"):
        with self.subTest(key=key), self.assertRaisesRegex(TelemetryValidationError, "UNSAFE_TELEMETRY_CONTENT"):
            normalize_event(valid_payload(**{key: "secret"}), collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_nested_mutable_provenance_cannot_survive_normalization(self):
    raw = valid_payload(provenance={"classification": "DERIVED", "source_record_refs": ["result:1"], "redaction_actions": []})
    event = normalize_event(raw, collector_id="collector", collector_version="1.0", timestamp=NOW)
    raw["provenance"]["source_record_refs"].append("result:2")
    self.assertEqual(event.provenance.source_record_refs, ("result:1",))
    with self.assertRaisesRegex(TelemetryValidationError, "INVALID_TELEMETRY_PROVENANCE"):
        normalize_event(valid_payload(provenance={"classification": "DERIVED", "nested": {"token": "secret"}}), collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_retention_and_absence_are_non_authoritative(self):
    self.assertEqual(telemetry_availability((), "missing"), "TELEMETRY_ABSENT")
    self.assertEqual(unknown_detail_from_telemetry((), "missing"), "UNKNOWN_FROM_TELEMETRY")
    self.assertEqual(retention_deadline(normalized_event()) - NOW, timedelta(days=30))
```

- [ ] **Step 2: Run the privacy and retention tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because retention and absence helpers are absent or raw-content categories are accepted.

- [ ] **Step 3: Write the minimal policy-only implementation**

Add `unknown_detail_from_telemetry(events: Sequence[TelemetryEvent], logical_key: str) -> str` returning `UNKNOWN_FROM_TELEMETRY` whenever no bounded observation can answer the request. `retention_deadline` adds 30 days to the event timestamp and has no delete method. Keep `TelemetryCollector` free of files, network operations, timers, and background callbacks. Extend the Task 2 allowlist checks to reject nested containers and every sensitive test key; convert permitted reference lists to tuples before constructing provenance.

- [ ] **Step 4: Run privacy and retention tests to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; only normalized bounded metadata can enter the collector, and expiry/absence cannot alter Result/Evidence or governance.

- [ ] **Step 5: Commit privacy and retention semantics**

```bash
git add .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "feat: constrain telemetry privacy and retention"
```

### Task 5: Prove authority boundaries and future-slot compatibility

**Files:**
- Modify: `.gpt-codex/scripts/execution_telemetry.py`
- Modify: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: `authoritative_reconstruction_required(detail: str) -> tuple[str, ...]` and `assert_observation_only(event: TelemetryEvent) -> None`.
- Consumes: only normalized events and returns references to existing authority roots; it does not import or depend on a P0-5 implementation.

- [ ] **Step 1: Write failing authority-boundary tests**

```python
def test_event_classes_do_not_infer_authority(self):
    assertions = {
        "INSTRUCTION_ISSUED": "delivered_or_executing",
        "EXECUTION_COMPLETED": "accepted",
        "REVIEW_RESULT": "remediation_authorized",
        "REMOTE_EVIDENCE_OBSERVED": "synced_or_published",
        "SLOT_ASSIGNED": "slot_assignment_authority",
        "PUBLICATION_BOUNDARY_TRANSITION": "CONFIRMED_PUBLICATION",
    }
    for event_class, claim in assertions.items():
        with self.subTest(event_class=event_class), self.assertRaisesRegex(TelemetryValidationError, "PROHIBITED_AUTHORITY_CLAIM"):
            normalize_event(valid_payload(event_class=event_class, authority_claim=claim), collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_p0_5_is_observed_only_and_authoritative_reconstruction_skips_telemetry(self):
    event = normalize_event(valid_payload(slot_id="NONE"), collector_id="collector", collector_version="1.0", timestamp=NOW)
    assert_observation_only(event)
    self.assertEqual(authoritative_reconstruction_required("slot"), ("ACTIVE_EXECUTION_SLOTS", "STATE"))
    self.assertEqual(authoritative_reconstruction_required("publication"), ("publication contract", "Result/Evidence", "Git"))
```

- [ ] **Step 2: Run authority-boundary tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because the reconstruction map and observation-only assertion do not exist.

- [ ] **Step 3: Write the minimal boundary implementation**

`assert_observation_only` rejects any event provenance or payload that presents telemetry as Evidence, Result, approval, verified publication, assignment authority, state transition, review acceptance, or remediation. `authoritative_reconstruction_required` returns fixed tuples for `authorization`, `slot`, `result`, `git`, `publication`, and unknown detail; unknown returns the empty tuple rather than inventing an authority. It must return P0-5 names only as references and must not create a slot record or state transition.

- [ ] **Step 4: Run authority-boundary tests to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; zero telemetry leaves CONTROL, STATE, Work Unit, Result/Evidence, Git, publication contract, and future slot authority intact.

- [ ] **Step 5: Commit authority boundaries**

```bash
git add .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "test: prove telemetry authority boundaries"
```

### Task 6: Close projection classifications without projecting telemetry runtime

**Files:**
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Modify: `.gpt-codex/tests/test_consumer_projection.py`

**Interfaces:**
- Consumes: `audit_projection_paths(root, manifest) -> dict[str, list[str]]` from `consumer_projection.py`.
- Produces: exact `DEVELOPMENT_HISTORY` entries for this accepted Design and Plan, plus exact `MANAGEMENT_ONLY` entries for the telemetry script and test.
- Cross-module route: primary `framework-core`; affected `framework-core`, `release-projection`; why: framework-core adds the derived runtime seam and release-projection classifies its physical paths. Contracts affected: `CONSUMER_PROJECTION_CONTRACT`. Invariant affected: management-only assets are not consumer runtime authority. Required tests: `test_execution_telemetry.py`, `test_consumer_projection.py`, `test_consumer_runtime_closure.py`, `test_release_packaging.py`, `test_publication_authority.py`.

- [ ] **Step 1: Write the failing exact-classification test**

```python
def test_execution_telemetry_is_management_only_and_stage_docs_are_history(self):
    manifest = load_projection_manifest(ROOT)
    paths = manifest["paths"]
    self.assertEqual(paths[".gpt-codex/scripts/execution_telemetry.py"], "MANAGEMENT_ONLY")
    self.assertEqual(paths[".gpt-codex/tests/test_execution_telemetry.py"], "MANAGEMENT_ONLY")
    self.assertEqual(paths["docs/superpowers/specs/2026-09-13-execution-telemetry-design.md"], "DEVELOPMENT_HISTORY")
    self.assertEqual(paths["docs/superpowers/plans/2026-09-14-execution-telemetry.md"], "DEVELOPMENT_HISTORY")
    self.assertEqual(audit_projection_paths(ROOT, manifest)["unknown_paths"], [])
```

- [ ] **Step 2: Run projection test to verify RED**

Run: `python .gpt-codex/tests/test_consumer_projection.py`

Expected: FAIL because the four exact manifest entries do not exist and the telemetry/stage paths are unknown.

- [ ] **Step 3: Add only exact manifest classifications**

Add the four literal path/classification pairs from Step 1. Do not add a wildcard, consumer-required telemetry asset, release metadata, archive, or runtime payload. Do not alter `consumer_projection.py`, publication authority, release tooling, or existing consumer assets.

- [ ] **Step 4: Run projection tests to verify GREEN**

Run: `python .gpt-codex/tests/test_consumer_projection.py && python .gpt-codex/tests/test_consumer_runtime_closure.py && python .gpt-codex/tests/test_release_packaging.py && python .gpt-codex/tests/test_publication_authority.py`

Expected: PASS; the projection audit is complete and no telemetry runtime artifact appears in the consumer staging inventory.

- [ ] **Step 5: Commit projection closure**

```bash
git add .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/tests/test_consumer_projection.py
git commit -m "chore: classify execution telemetry paths"
```

### Task 7: Run final contract regression and review-ready verification

**Files:**
- Modify: no production or test files; use the Task 1-6 files exactly as committed.

**Interfaces:**
- Consumes: the registry route, telemetry contract, projection manifest, and existing framework/project validators.
- Produces: fresh review evidence that telemetry remains derived-only, route-owned, projection-classified, and non-authoritative. This is a verification-only task; its RED→GREEN coverage is supplied by the independently testable implementation tasks above.

- [ ] **Step 1: Verify focused contracts and the complete test suite**

Run: `python .gpt-codex/scripts/validate_framework.py && python .gpt-codex/scripts/validate_project.py . && python .gpt-codex/tests/test_framework_module_schemas.py && python .gpt-codex/tests/test_framework_module_routing.py && python .gpt-codex/tests/test_framework_module_validation.py && python .gpt-codex/tests/test_execution_telemetry.py && python .gpt-codex/tests/test_consumer_projection.py && python -m unittest discover -s .gpt-codex/tests -p 'test_*.py' && python .gpt-codex/scripts/validate_consumer_projection.py --root .`

Expected: every command exits 0. Record the `Ran N tests` count and `OK`/failure/error totals from the full-suite command in final evidence; final acceptance requires 0 failures and 0 errors, projection unknown/missing counts of 0, and no waiver.

- [ ] **Step 2: Verify scoped history, remote synchronization, and clean state**

Run: `git diff --check 80b9f383a157ee59dd890f4a5bf48638b3e436b1..HEAD && git status --short && git rev-parse HEAD && git ls-remote --heads origin feature/execution-telemetry-design`

Expected: no whitespace errors and no uncommitted changes. Run this check again after the normal push; the SHA returned by `git ls-remote --heads origin feature/execution-telemetry-design` must exactly equal the final local `git rev-parse HEAD`. A successful `git push` alone is not remote verification.

- [ ] **Step 3: Push the already-committed fast-forward implementation normally**

```bash
git push origin feature/execution-telemetry-design
```

## Plan self-review

Coverage is complete: Tasks 1-2 cover all event classes, common/correlation fields, provenance, required `slot_id`/`source` validation, LOW_CONFIDENCE fallback identity, malformed input, and non-authority; Task 3 covers retry idempotency, distinct logical fallback sequence observations, earliest repeat lineage, latest-related chronology, changed authority facts, repeats, late/out-of-order/stale/inconsistent behavior; Task 4 covers telemetry absence, unknown detail, privacy minimization, and non-authoritative retention; Task 5 covers P0-5, Result/Evidence, Git/publication, and authority reconstruction boundaries; Task 6 closes exact projection classifications; Task 7 provides final regression evidence.

Round-3 consistency check: `logical_idempotency_key` retains `producer_run_id` and
`producer_sequence` only for valid no-durable-identity LOW_CONFIDENCE events;
`repeat_subject_key` identifies their producer run but excludes producer
sequence. The collector separately tracks earliest repeat lineage and latest
chronology. `slot_id` and `source` are required strings, while intentionally
nullable observation fields remain nullable. `AuthoritativeSnapshot` and
`TelemetryEvent` contain no `publication_status`; `result_status` is compared
only against matching-correlation authoritative Result status. The precedence
remains `INCONSISTENT → STALE → OUT_OF_ORDER → LATE → CURRENT`.

`PROJECTION_STAGE_DEVIATION = DEFERRED_NONBLOCKING`: this Plan-stage change does
not alter the manifest; the permitted stage debt remains the exact Design/Plan
pair until the separately authorized projection task.

The plan contains no persistence implementation, telemetry history, automatic action, new module, schema, central service, or P0-5 lifecycle dependency. All names introduced in later tasks are defined in the task where they are first produced. The implementation is intentionally additive and uses only standard-library test conventions already present in the repository.
