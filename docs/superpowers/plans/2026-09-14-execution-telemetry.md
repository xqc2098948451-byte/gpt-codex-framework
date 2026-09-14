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
- When no durable authoritative record exists, the logical key may add only `producer_run_id` and monotonic `producer_sequence`; provenance must mark that fallback lower-confidence.
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
| `.gpt-codex/release/consumer-projection-manifest.json` | Modify | `release-projection`; it already owns this exact path and only classifies paths. It gains no telemetry authority. | CONSUMER_REQUIRED as the existing manifest |
| `docs/superpowers/specs/2026-09-13-execution-telemetry-design.md` | Modify only in the projection manifest | Development history; no production semantics change. | DEVELOPMENT_HISTORY |
| `docs/superpowers/plans/2026-09-14-execution-telemetry.md` | Modify only in the projection manifest | Development history; no production semantics change. | DEVELOPMENT_HISTORY |

No change is planned to `CONTROL`, `STATE`, Work Unit schemas/templates, Instruction/Result schemas, Evidence, Git continuity, P0-5 navigation-continuity assets, publication contracts, or validation entry points. `framework-validation`, `role-communication`, `navigation-continuity`, and `git-continuity` are observed-contract boundaries only, not implementation owners.

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
- Produces: `TelemetryEvent` frozen dataclass with `event_id`, `event_class`, all common fields, optional correlation fields, `provenance`, `logical_key`, `observation_kind`, `repeats_event_id`, `supersedes_observation_id`, and `ordering_status`.
- Produces: `normalize_event(payload: Mapping[str, object], *, collector_id: str, collector_version: str, timestamp: datetime) -> TelemetryEvent`.
- Produces: `TelemetryValidationError(code: str)` for `MALFORMED_TELEMETRY_EVENT`, `PROHIBITED_AUTHORITY_CLAIM`, `UNSAFE_TELEMETRY_CONTENT`, and `INVALID_TELEMETRY_PROVENANCE`.
- Produces the test helper `normalized_event(**overrides) -> TelemetryEvent`, which calls `normalize_event(valid_payload(**overrides), collector_id="collector", collector_version="1.0", timestamp=overrides.pop("timestamp", NOW))`.
- Consumes: the closed sets from Task 1 only; it does not read or mutate authoritative records.

- [ ] **Step 1: Write failing normalization and non-authority tests**

```python
def test_normalize_event_requires_common_fields_and_derived_provenance(self):
    event = normalize_event(valid_payload(), collector_id="collector", collector_version="1.0", timestamp=NOW)
    self.assertEqual(event.provenance["classification"], "DERIVED")
    self.assertEqual(event.slot_id, "NONE")
    with self.assertRaisesRegex(TelemetryValidationError, "MALFORMED_TELEMETRY_EVENT"):
        normalize_event({"event_class": "EXECUTION_STARTED"}, collector_id="collector", collector_version="1.0", timestamp=NOW)

def test_normalize_event_rejects_authority_claims_and_sensitive_content(self):
    with self.assertRaisesRegex(TelemetryValidationError, "PROHIBITED_AUTHORITY_CLAIM"):
        normalize_event(valid_payload(authority_claim="APPROVAL"), collector_id="collector", collector_version="1.0", timestamp=NOW)
    with self.assertRaisesRegex(TelemetryValidationError, "UNSAFE_TELEMETRY_CONTENT"):
        normalize_event(valid_payload(raw_prompt="secret"), collector_id="collector", collector_version="1.0", timestamp=NOW)
```

- [ ] **Step 2: Run the normalization tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because `TelemetryEvent`, `normalize_event`, and `TelemetryValidationError` are not implemented.

- [ ] **Step 3: Write the minimal normalization implementation**

```python
@dataclass(frozen=True)
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
    provenance: Mapping[str, object]
    instruction_id: str | None = None
    result_id: str | None = None
    finding_id: str | None = None
    review_request_id: str | None = None
    authoritative_record_ref: str | None = None
    logical_key: str
    observation_kind: str = "PRIMARY"
    repeats_event_id: str | None = None
    supersedes_observation_id: str | None = None
    ordering_status: str = "CURRENT"
```

Require every common field key, allow only the five optional correlation keys,
require `provenance["classification"] == "DERIVED"`, require a non-empty
bounded `source`, normalize absent optional values to `None`/`NONE`, and reject
unknown keys, authority-claim keys, raw-content keys, unbounded strings, and
non-reference evidence values. Generate `event_id` with `uuid.uuid4()` and
call the Task 3 `logical_idempotency_key` helper after it is added; until then,
use a private deterministic SHA-256 helper with the same input tuple.

- [ ] **Step 4: Run the normalization suite to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; the normalized event is derived-only and malformed/sensitive/authority-bearing payloads are rejected.

- [ ] **Step 5: Commit normalization**

```bash
git add .gpt-codex/scripts/execution_telemetry.py .gpt-codex/tests/test_execution_telemetry.py
git commit -m "feat: validate normalized telemetry events"
```

### Task 3: Add logical idempotency, repeats, and ordering classifications

**Files:**
- Modify: `.gpt-codex/scripts/execution_telemetry.py`
- Modify: `.gpt-codex/tests/test_execution_telemetry.py`

**Interfaces:**
- Produces: `logical_idempotency_key(event: TelemetryEvent) -> str` and `classify_ordering(event: TelemetryEvent, authoritative: Mapping[str, object] | None) -> str`.
- Produces: `TelemetryCollector.emit(event: TelemetryEvent, *, authoritative: Mapping[str, object] | None = None) -> TelemetryEvent` and `TelemetryCollector.events() -> tuple[TelemetryEvent, ...]`.
- Consumes: Task 2 events; `authoritative` is read-only input containing only the relevant state revision, head SHA, correlation reference, and publication fact.

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
    first = collector.emit(normalized_event(head_sha="a" * 40), authoritative={"head_sha": "a" * 40})
    changed = collector.emit(normalized_event(head_sha="b" * 40), authoritative={"head_sha": "b" * 40})
    stale = collector.emit(normalized_event(head_sha="a" * 40), authoritative={"head_sha": "b" * 40})
    self.assertNotEqual(first.logical_key, changed.logical_key)
    self.assertEqual(stale.ordering_status, "STALE")
```

- [ ] **Step 2: Run the idempotency and chronology tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because `TelemetryCollector`, logical-key calculation, repeat linkage, and ordering classification are absent.

- [ ] **Step 3: Write the minimal collector implementation**

Use private in-memory dictionaries keyed by logical key and immutable event ID.
The key serializes only the Design tuple, adding `producer_run_id` and
`producer_sequence` only when `authoritative_record_ref` is absent. Same key
and equal normalized canonical payload returns the existing event. Same source
fact with a changed source or timestamp emits an immutable `REPEAT` record
linked by `repeats_event_id`. A changed authoritative tuple emits a distinct
event. `classify_ordering` returns `LATE`, `OUT_OF_ORDER`, `STALE`, or
`INCONSISTENT` from authoritative revision/correlation/SHA/publication inputs,
never from timestamp alone; it never writes the supplied mapping.

- [ ] **Step 4: Run the collector suite to verify GREEN**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: PASS; retries do not multiply logical lifecycle observations, repeats remain append-only, and stale/inconsistent observations cannot change authoritative input.

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

def test_retention_and_absence_are_non_authoritative(self):
    self.assertEqual(telemetry_availability((), "missing"), "TELEMETRY_ABSENT")
    self.assertEqual(unknown_detail_from_telemetry((), "missing"), "UNKNOWN_FROM_TELEMETRY")
    self.assertEqual(retention_deadline(normalized_event()) - NOW, timedelta(days=30))
```

- [ ] **Step 2: Run the privacy and retention tests to verify RED**

Run: `python .gpt-codex/tests/test_execution_telemetry.py`

Expected: FAIL because retention and absence helpers are absent or raw-content categories are accepted.

- [ ] **Step 3: Write the minimal policy-only implementation**

Add `unknown_detail_from_telemetry(events: Sequence[TelemetryEvent], logical_key: str) -> str` returning `UNKNOWN_FROM_TELEMETRY` whenever no bounded observation can answer the request. `retention_deadline` adds 30 days to the event timestamp and has no delete method. Keep `TelemetryCollector` free of files, network operations, timers, and background callbacks. Extend the Task 2 forbidden-key set to cover every test key.

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

- [ ] **Step 1: Verify the complete framework contract**

Run: `python .gpt-codex/scripts/validate_framework.py && python .gpt-codex/scripts/validate_project.py . && python .gpt-codex/tests/test_framework_module_schemas.py && python .gpt-codex/tests/test_framework_module_routing.py && python .gpt-codex/tests/test_framework_module_validation.py && python .gpt-codex/tests/test_execution_telemetry.py && python .gpt-codex/scripts/validate_consumer_projection.py --root .`

Expected: every command exits 0, including consumer projection after Task 6 closes the two stage-document debts and classifies every new implementation path.

- [ ] **Step 2: Verify scoped history, remote synchronization, and clean state**

Run: `git diff --check 80b9f383a157ee59dd890f4a5bf48638b3e436b1..HEAD && git status --short && git rev-parse HEAD && git ls-remote --heads origin feature/execution-telemetry-design`

Expected: no whitespace errors, no uncommitted changes, and the pushed remote branch head equals local `HEAD`.

- [ ] **Step 3: Push the already-committed fast-forward implementation normally**

```bash
git push origin feature/execution-telemetry-design
```

## Plan self-review

Coverage is complete: Tasks 1-2 cover all event classes, common/correlation fields, provenance, malformed input, and non-authority; Task 3 covers retry idempotency, equivalent duplicates, changed authority facts, repeats, late/out-of-order/stale/inconsistent behavior; Task 4 covers telemetry absence, unknown detail, privacy minimization, and non-authoritative retention; Task 5 covers P0-5, Result/Evidence, Git/publication, and authority reconstruction boundaries; Task 6 closes exact projection classifications; Task 7 provides final regression evidence.

The plan contains no persistence implementation, telemetry history, automatic action, new module, schema, central service, or P0-5 lifecycle dependency. All names introduced in later tasks are defined in the task where they are first produced. The implementation is intentionally additive and uses only standard-library test conventions already present in the repository.
