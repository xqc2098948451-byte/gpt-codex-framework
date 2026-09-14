# GPT–Codex Framework — Execution Telemetry Foundation Design

## Status and route

This is the P0-6 execution-telemetry design.  It is a design-only artifact:
it does not change Kernel, CONTROL, STATE, Work Unit, Result, Evidence, Git,
role protocol, slot lifecycle, schemas, templates, validators, release
metadata, consumer projection, or production behavior.

The Framework Module Registry is authoritative for the route.  It validates
with no errors, and the exact declared route is:

| Field | Decision |
| --- | --- |
| Candidate / primary module | `framework-core` |
| Exact declared responsibility | `framework governance` |
| Route outcome | `MODULE_ROUTE` |
| Affected modules | `framework-core` only |
| Cross-module status | No production cross-module change in this Design stage |

This is not a stretched ownership claim: the design defines a governance
boundary and deliberately does not own or alter another module's production
assets.  A future implementation that changes role protocol, Result/Evidence,
Git continuity, validation, or projection assets must be routed again for its
actual changed assets and consumed contracts.

Baseline: base SHA `9d09c69eec0a9fe6ae3eac0ad4e73934e3a3dc88`.

## 1. Purpose and non-authority invariant

P0-6 defines a minimal append-only observation stream for governed work.  It
answers what was observed, when, and from which bounded source; it does not
decide what is allowed, true, accepted, or next.

```text
CONTROL / STATE / Work Unit / Result / Evidence / Git facts
    = authoritative governance facts

telemetry event
    = derived observation of those facts or of bounded execution activity
```

An event may reference an authoritative record, but no consumer may invert
that reference and treat telemetry as a replacement record.  If an event and
an authoritative source disagree, the authoritative source wins; the event is
marked inconsistent or stale for investigation.  Telemetry cannot authorize
mutation, approval, release, publication, routing, role elevation, slot
reassignment, or adoption.  It also cannot create a state transition, make a
review pass, close a finding, prove delivery, or repair missing evidence.

This classification is `DERIVED_OBSERVATION_ONLY`, not an authority class,
policy engine, or central service.

## 2. Scope and existing contracts

P0-6 observes existing governance without adding an eighth Framework module,
a message bus, a state machine, a source of identity, or an execution-control
plane.  The canonical instruction and Result Envelope remain the causal
contracts for role-aware work.  CONTROL binds project identity and enabled
Guardrails; STATE owns revision and legal state; Work Unit owns bounded scope
and authorization; Result and Evidence own durable outcome/evidence; Git and
remote verification own commit/ref facts.

`instruction issued` is an observation of an already-authorized instruction,
not proof that transport delivered it or that execution began.  Likewise,
`remote evidence observed` reports what a permitted observer saw; it is not a
push, a review approval, a merge, a release, or a publication authorization.

## 3. Event model

Every event has one `event_class` and the common fields below.  Values are
copied or derived from the bounded source at observation time; missing values
are represented explicitly as `null`/`NONE` with a reason in provenance, never
silently invented.

| Required field | Meaning |
| --- | --- |
| `work_unit_id` | Work Unit being observed; never a substitute for its authorization. |
| `slot_id` | Observed P0-5 slot identifier, or `NONE` only where no slot is applicable. |
| `role` | Role observed acting or being assigned; not a grant to that role. |
| `state_revision` | Observed authoritative STATE revision. |
| `project_context_id` | Observed CONTROL-bound context identity. |
| `branch_ref` | Observed branch/ref, including an explicitly named remote ref when applicable. |
| `base_sha` / `head_sha` | Observed Git boundary SHAs; no ancestry claim is implied without Git evidence. |
| `result_status` | Observed canonical Result status, or `NONE` before a Result exists. |
| `review_gate` | Observed configured/targeted review-gate identity/status, not a gate decision. |
| `evidence_refs` | Stable references to the authoritative Result/Evidence/Git records used. |
| `timestamp` | UTC RFC 3339 time at which this observation was emitted. |
| `source` | Bounded producer/channel, for example `instruction-envelope`, `state-read`, `result-envelope`, `git-local`, or `remote-evidence-read`. |
| `provenance` | Source record IDs, observed-at revision/SHA, collector version, redaction flags, and any completeness/consistency qualification. |

`event_id` is a UUID or similarly collision-resistant immutable identifier
allocated by the collector.  It identifies one emitted record, not a Work
Unit, slot, instruction, Result, Evidence item, or Git commit.  Correlation
references such as `instruction_id`, `result_id`, `finding_id`,
`review_request_id`, and `authoritative_record_ref` are optional by event
class, but must be present whenever the corresponding authoritative fact
exists.  They retain their original authority and identity.

The minimum event classes are:

| Event class | Observation boundary |
| --- | --- |
| `INSTRUCTION_ISSUED` | An authoritative instruction exists. No delivery/execution inference. |
| `SLOT_ASSIGNED` / `SLOT_REASSIGNED` | P0-5 recorded an assignment/reassignment. P0-6 did not perform it. |
| `EXECUTION_STARTED` | Bounded execution evidence was observed for the instruction/slot. |
| `EXECUTION_COMPLETED` | A completion Result was observed; it is not acceptance or publication. |
| `EXECUTION_BLOCKED` | A blocked Result/state/evidence condition was observed. |
| `REVIEW_REQUESTED` | An authoritative review request or gate target was observed. |
| `REVIEW_RESULT` | A reviewer Result was observed, including a non-finding conclusion. |
| `FINDING_CREATED` | A `REVIEW_FINDING` Result/Evidence item was observed. It does not approve remediation. |
| `REMEDIATION_AUTHORIZED` | An explicit GPT/User authorization record was observed. It is not created by telemetry. |
| `RE_REVIEW_RESULT` | A re-review Result was observed and correlated to the prior remediation/finding. |
| `REMOTE_EVIDENCE_OBSERVED` | An allowed remote evidence channel exposed a ref, artifact, or Result fact. |
| `PUBLICATION_BOUNDARY_TRANSITION` | Only when an authoritative publication-boundary state/fact changes or is observed. The event cannot publish. |

The final class is conditional: ordinary local implementation, review, and
design work emits no publication-boundary event unless the pre-existing
publication contract makes such a boundary relevant.

## 4. Identity, idempotency, and repeated observations

The logical idempotency key is a deterministic tuple:

```text
event_class + source + authoritative_record_ref + observed_state_revision
+ observed_head_sha + slot_id + correlation_ref
```

`correlation_ref` is the applicable instruction, Result, review request,
finding, remediation decision, or publication record.  The producer must use
the narrowest authoritative reference available.  If an event has no durable
authoritative record (for example a bounded local execution-start signal), its
key additionally contains an immutable producer run ID and monotonic local
sequence.  That fallback is explicitly lower-confidence in provenance.

Collectors must make retries idempotent: same logical key and equivalent
canonical payload is one logical observation.  A transport may retain one
physical record and suppress duplicates, or retain duplicate receipts linked
to the canonical `event_id`; it must not multiply lifecycle facts.  Duplicate
arrivals with different non-authoritative metadata (for example receive time)
are repeated observations, not revisions of authority.

Repeated observations of the same source fact are allowed when they add a
distinct `observed_at` time, source, or remote-read attempt.  They must carry
`observation_kind: REPEAT`, link `repeats_event_id`, and never overwrite the
earlier observation.  A changed authoritative fact produces a new event with
a new idempotency key and an explicit `supersedes_observation_id` only at the
telemetry layer; it does not mutate the authoritative record.

## 5. Time, ordering, absence, and staleness

Event order is not authority order.  Consumers order causal narratives first
by authoritative revision, Result/Evidence correlation, and Git ancestry;
they use telemetry timestamp only as a display/collection aid.  A late or
out-of-order arrival is retained with `arrival_timestamp`,
`observed_timestamp`, and `ordering_status: LATE` or `OUT_OF_ORDER`.  It may
fill an observation gap, but cannot roll back a slot, state, review, Result,
or publication fact.

Missing telemetry means `TELEMETRY_ABSENT`, not “did not happen.”  The
consumer must re-read the applicable authoritative sources and return
`UNKNOWN_FROM_TELEMETRY` when they cannot reconstruct the requested detail.
No lifecycle block, retry, escalation, or approval may be triggered solely
because telemetry is missing.

An event is stale when its recorded state revision, base/head SHA, referenced
Result/Evidence version, or remote observation point no longer matches the
currently-read authoritative fact needed by the consumer.  It remains
historical telemetry labelled `STALE`; it cannot be updated in place or used
for current routing.  Conflicting identity, context, Git, or causal references
are labelled `INCONSISTENT` and require normal authoritative reconciliation.

## 6. Provenance, privacy, and retention

Each event provenance records: collector identity/version, source/channel,
source-record references, observed state revision and Git/ref snapshot,
collection timestamp, normalization/redaction actions, completeness level,
and any fallback local-run identifier.  Provenance must say `DERIVED` and may
not assert that it is an Evidence, Result, approval, or authority record.

Collection is data-minimized.  Store stable IDs, enums, bounded status values,
repository-relative paths only when already present in authoritative evidence,
and references rather than raw logs, prompts, diffs, secrets, personal data,
intermediate reasoning, tool payloads, or source contents.  Reject or redact
credentials, access tokens, host/user identifiers, full command environment,
and unbounded free text.  Evidence references point to existing governed
retention/access controls; telemetry does not duplicate their contents.

Raw transport/collector traces are ephemeral.  Retain normalized telemetry
only for the shortest policy-approved operational/audit period, with a
recommended default of 30 days; delete or aggregate it after expiry.  A
retention exception needs the existing project governance and privacy process,
not a telemetry flag.  Authoritative Result and Evidence follow their own
retention rules and may outlive telemetry.  Deleting telemetry must not delete
or invalidate Result/Evidence.

## 7. P0-5 slot-lifecycle boundary and reconstruction

P0-5 alone defines `ACTIVE_EXECUTION_SLOTS` lifecycle authority, including
slot existence, assignment/reassignment, active/inactive status, revision
checks, and legal transitions.  P0-6 observes a P0-5 slot record only after
it exists.  It does not reserve a slot, select an executor, assign or
reassign one, infer a legal transition, recover a stale slot, or treat an
execution event as evidence that a slot is active.

When telemetry is absent, the following can be reconstructed from
authoritative data, subject to ordinary evidence availability:

| Question | Authoritative reconstruction source |
| --- | --- |
| What was allowed and for which Work Unit? | CONTROL, enabled Guardrails, Work Unit, and instruction envelope. |
| Which slot is/was active and its legal history? | P0-5 `ACTIVE_EXECUTION_SLOTS` and STATE revision history. |
| What result or review/finding occurred? | Result Envelope and Evidence references. |
| What code/ref was observed or remotely verified? | Git facts, continuity records, and remote evidence. |
| Whether remediation was authorized? | Explicit GPT/User authorization record and subsequent FIX_INSTRUCTION. |
| Whether publication occurred/is allowed? | Existing publication contract and authoritative Result/Evidence/Git facts. |

Exact collector timing, duplicate delivery attempts, and transient local start
signals cannot necessarily be reconstructed without telemetry.  Their absence
does not weaken the governance facts above.

## 8. Consumers and non-goals

P1 Evidence Quality may assess whether authoritative evidence references are
complete or well-bound.  P2 Failure Pattern Registry may consume sanitized,
derived event aggregates to propose investigations.  Neither consumer receives
authority through telemetry; neither may automatically change policy, route
work, authorize remediation, elevate a role, or adopt a pattern.  Any future
change remains subject to the existing authorization chain and a separately
routed Work Unit.

P0-6 does not implement dashboards, automatic optimization, scoring, agent
budgets, anomaly remediation, learning loops, a new module, or a central
analytics service.  It also does not prescribe storage infrastructure,
collection daemons, background jobs, analytics schemas, or a new consumer
projection artifact.

## 9. Future implementation and validation

A future implementation must remain additive and must first re-route every
changed asset.  It should test event shape and source-bound provenance;
deduplication/retry equivalence; repeat and conflicting observations; late and
out-of-order handling; absence/staleness behavior; redaction and expiry; slot
non-authority; Result/Evidence precedence; and the proof that no telemetry
path can authorize any prohibited action.

It must also run the governing framework/project validation and affected
module tests.  If it changes a consumer-projected asset or a projection
classification, it must separately satisfy consumer-projection and runtime
closure tests.  No P0-6 implementation may claim that telemetry itself proves
execution, remote synchronization, review approval, or publication.

## 10. Projection-stage deviation and self-review

This Design-stage file is intentionally not added to the consumer projection
manifest.  The manifest is not edited in Design.  Its path is the sole
stage-local projection debt (`unknown_path`) introduced by this Work Unit and
is development history, not a consumer artifact.  A later approved projection
or release stage must classify it explicitly or otherwise resolve it before a
projection-validation claim.  No other unknown path is introduced.

Self-review confirms: there is one authority chain; telemetry is derived and
append-only; required event classes and fields are defined; deduplication,
late/missing/stale observations, provenance, privacy, and retention are
bounded; P0-5 lifecycle authority remains untouched; authoritative
reconstruction works without telemetry; and future P1/P2 consumers cannot
create a feedback authority loop.
