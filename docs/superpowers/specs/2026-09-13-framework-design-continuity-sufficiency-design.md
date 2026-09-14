# P0-5 Framework Design Continuity & Sufficiency Control

**Status:** DESIGN

**Work Unit:** `framework-design-continuity-sufficiency-design-001`

**Primary module:** `navigation-continuity`

**Primary responsibility:** `project navigation and continuity`

## 1. Decision and scope

P0-5 defines how a governed GPT/Codex execution remains continuous when a
physical chat or desktop window disappears, a context is compacted, a handoff
is performed, or several Work Units are active concurrently. It establishes a
future `ACTIVE_EXECUTION_SLOTS` contract. A slot is a durable, logical
execution identity; it is not a chat, browser tab, desktop window, model
session, or person.

The primary route is `navigation-continuity`, whose registered responsibility
is exactly `project navigation and continuity`. P0-5 extends that module's
logical slot-lifecycle, continuation, recovery, and restart sufficiency without
changing the Framework Module Registry's ownership model. The future
implementation is `CROSS_MODULE_CHANGE_REQUIRED`: lifecycle semantics belong
to `navigation-continuity`, while the authoritative STATE model, its revision
semantics, and the physical persistence shape of slot records belong to
`framework-core`. It also consumes the existing identity, role, Work Unit,
Result/Evidence, Git, and validation contracts. It does not transfer any of
their ownership.

This design is intentionally limited to framework-development continuity. It
does not create a central service, coordinate work automatically across
projects, or make a physical execution surface authoritative.

## 2. Authority model

`ACTIVE_EXECUTION_SLOTS` is a future durable, STATE-backed contract. P0-5
under `navigation-continuity` owns its logical lifecycle, continuation,
recovery, restart, mismatch detection, and reattachment semantics.
`framework-core` owns the authoritative STATE model, STATE revision semantics,
`.gpt-codex/schemas/state.schema.json`,
`.gpt-codex/project-template/STATE.template.json`, and the physical persistence
shape of execution-slot records. The contract is recorded and updated through
that existing authoritative STATE discipline; it is not a second state
database. Its references point at, but never replace, the following
authorities:

| Fact | Existing authority | P0-5 use |
| --- | --- | --- |
| Project and repository identity | `CONTROL` / `identity-context` | Bind every slot to `project_context_id` before it may resume. |
| Current governed revision and optimistic concurrency | `STATE` / framework-core | Persist the slot fact at a known `state_revision`; reject a stale writer. |
| Authorized goal, scope, permissions, and acceptance | `WORK_UNIT` | Bind a slot to one authorized Work Unit; do not derive permission from a slot. |
| Role, instruction correlation, and return semantics | Instruction/Result envelopes / `role-communication` | Require an explicit role and return route; a slot does not authorize itself. |
| Completion and review evidence | Result and Evidence | Bind milestones, acceptance, and recovery claims to durable evidence. |
| Local/remote revision, ancestry, and synchronization | Git / `git-continuity` | Compare recorded SHAs with repository facts before continuation or review. |

Project Map remains `DERIVED_NAVIGATION_INDEX`, and Resume remains
`DERIVED_CACHE`. Either may speed recovery, but neither establishes a slot,
authorizes work, overrides a state revision, or proves that a lost window may
resume. Repository-authoritative facts remain sufficient when both are absent
or stale.

## 3. `ACTIVE_EXECUTION_SLOTS` contract

The future contract is a collection keyed by immutable `slot_id`. Each entry
contains at least the following fields. Values shown as SHA fields are full,
40-hex Git object IDs when present; no branch name alone is a revision fact.

| Field | Meaning and constraint |
| --- | --- |
| `slot_id` | Stable logical-slot identifier. It is never inferred from a physical window. |
| `role` | One exact protocol role for the slot. Implementer and Reviewer assignments are validated against the instruction/result role contracts. |
| `status` | One of the closed vocabulary in section 4. |
| `work_unit_id` | The authoritative Work Unit bound to this slot, or `null` only while an `IDLE` slot has no assignment. |
| `primary_module` | The responsibility-routed primary module for the assigned Work Unit. |
| `project_context_id` | Exact `CONTROL.project_context_id`; a mismatch is fail-closed. |
| `branch` | Intended local Git branch/ref for the Work Unit. It is a locator, not proof of identity or review. |
| `worktree` | Canonical local worktree path/identity observation. It is not a physical-window identity. |
| `base_sha` | Authorized starting revision for the Work Unit. |
| `current_head_sha` | Latest locally observed worktree `HEAD` for this slot. |
| `last_accepted_sha` | Latest exact revision accepted at the applicable milestone; durable handoff fact, never a mutable label. |
| `state_revision` | The authoritative `STATE.revision` at which this slot record or lifecycle transition is current. It is not a local navigation-cache counter and there is no second slot-specific authoritative revision sequence. |
| `next_action` | Deterministic next governed action, including the required reconciliation/review action when blocked. |

When `status` is `BLOCKED`, the record additionally requires
`blocked_from_status`, `block_reason`, and the applicable bounded correlation
references. `blocked_from_status` records the durable predecessor lifecycle
state needed for recovery/reconciliation; it is not a transition target.
`block_reason` is a bounded, machine-readable vocabulary item. A review finding
that requires remediation uses `AWAITING_REMEDIATION_AUTHORIZATION`. Relevant
references bind the block to the finding, review request/result, instruction,
and later remediation authorization as applicable. These references preserve
role-protocol causality; they do not make navigation-continuity a review or
remediation authority.

An implementation may add narrowly justified correlation fields (for example,
instruction ID, Result reference, reviewer target SHA, or reassignment
evidence). It must not add a second authority field that duplicates CONTROL,
STATE, Work Unit, Result/Evidence, or Git facts.

## 4. Slot lifecycle and invariants

The only slot statuses are:

```text
IDLE
ACTIVE
BLOCKED
AWAITING_REVIEW
REVIEWING
COMPLETED
```

`IDLE` has no active Work Unit. `ACTIVE` represents authorized execution.
`BLOCKED` records a durable stop, its bounded machine-readable reason, its
durable predecessor state, and its next reconciliation or decision.
`AWAITING_REVIEW` means the Implementer has returned a bounded milestone and
the prescribed review has not started. `REVIEWING` means the one assigned
Reviewer is inspecting a named revision. `COMPLETED` records that the slot's
bound Work Unit has reached its authorized completion gate; it does not imply a
new Work Unit or a new authority.

The lifecycle is guarded by these invariants:

1. One Implementer slot has at most one non-completed active Work Unit. A Work
   Unit cannot be silently replaced while the slot is `ACTIVE`,
   `AWAITING_REVIEW`, or `BLOCKED`.
2. A logical slot persists across Plan tasks, context compaction, handoffs, and
   physical-window replacement. A new task/window must bind to the existing
   `slot_id` or receive an explicit new assignment.
3. Physical window != logical execution slot. Closing, duplicating, or losing a
   window has no lifecycle effect by itself.
4. Reassignment is explicit, revision-bound, and evidence-backed. It names the
   source slot or assignee, target slot/assignee, Work Unit, expected state
   revision, and current/accepted SHA. No timeout, inactivity signal, model
   change, telemetry observation, or window loss may automatically reassign a
   slot.
5. Every transition uses the existing optimistic `STATE` revision write rule.
   A writer based on an older revision returns `RECONCILIATION_REQUIRED` rather
   than overwriting a newer slot fact.
6. `last_accepted_sha` and `state_revision` are durable handoff facts. A later
   actor must verify their repository ancestry and state freshness before
   continuing. A branch name, remembered conversation, or local uncommitted
   diff cannot substitute for them.
7. A Reviewer may serially review milestones and remediation for a Work Unit.
   The reviewer role remains non-mutating, and reviewer reassignment is an
   explicit, evidence-bound lifecycle event. Multiple physical review windows
   do not create multiple reviewers.
8. A Result or Evidence record supports a slot transition but does not grant a
   new assignment. A review finding remains evidence until the existing role
   protocol supplies an explicit GPT/User remediation authorization and a new
   `FIX_INSTRUCTION`. A review finding != mutation authority and does not
   return an Implementer to `ACTIVE`.
9. `COMPLETED` is not reusable for a new Work Unit. Before reuse, a durable,
   authoritative STATE revision must transition `COMPLETED → IDLE` and retain
   sufficient Result/Evidence/Work Unit correlation to prove the prior Work
   Unit is closed. The reset clears only current assignment fields:
   `work_unit_id`, branch, current head SHA, worktree, current action, and
   current block/remediation fields. It does not erase historical Work Unit,
   Result, Evidence, or Git records.
10. A new Work Unit can bind to an Implementer slot only while it is `IDLE`.
    The only assignment path is `IDLE → ACTIVE`, written as a new authoritative
    STATE revision carrying the new current assignment. This preserves one
    active Work Unit per Implementer slot.

The normal milestone sequence is:

```text
IDLE --explicit assignment--> ACTIVE --milestone Result--> AWAITING_REVIEW
AWAITING_REVIEW --explicit reviewer start--> REVIEWING
REVIEWING --accepted review without remediation--> ACTIVE or COMPLETED
REVIEWING --finding requiring remediation--> BLOCKED
any non-terminal state --verified blocking fact--> BLOCKED
BLOCKED --explicit GPT/User remediation authorization + FIX_INSTRUCTION +
current-fact reconciliation--> ACTIVE
COMPLETED --durable closure/reset transition--> IDLE --explicit new assignment--> ACTIVE
```

No arrow is triggered merely by a missing window, elapsed time, or observed
telemetry. There is no generic `BLOCKED → blocked_from_status` transition.
Returning toward any predecessor lifecycle state is permitted only when an
explicitly authorized reconciliation and current authoritative STATE, Work
Unit, Result/Evidence, and Git facts prove restoration valid. Otherwise the
outcome is `RECONCILIATION_REQUIRED`; a stale `blocked_from_status` value never
overrides current facts. A Reviewer message alone cannot authorize remediation.

## 5. Continuity, recovery, and mismatch handling

Lost-window recovery is repository-authoritative. A replacement execution
surface must load and validate durable facts before it displays or performs a
next action. It may use Project Map and Resume as hints only after the durable
checks succeed.

### 5.1 Minimum restart context

The minimum sufficient restart context is:

1. `CONTROL` identity, including `project_context_id` and repository binding;
2. current authoritative `STATE`, its revision, active Work Unit reference,
   and the matching `ACTIVE_EXECUTION_SLOTS` record;
3. the bound Work Unit's scope, permissions, acceptance, and expected base
   revision;
4. the assigned instruction/result correlation and the most recent durable
   Result/Evidence needed to justify the recorded lifecycle state;
5. observed worktree branch, clean/dirty state, local `HEAD`, remote/ref
   evidence where the stage requires it, and Git ancestry from `base_sha` and
   `last_accepted_sha`; and
6. the slot's `next_action`, any recorded blocker/reconciliation reason, and,
   for `BLOCKED`, its predecessor, finding/review, instruction, and remediation
   authorization correlations.

If any required identity, revision, Work Unit, role, or SHA fact is absent,
contradictory, stale, or cannot be validated, the new surface must not resume
execution from conversational memory. It must return the applicable
reconciliation/error state and request the next authorized action.

### 5.2 `EXECUTION_SLOT_MISMATCH`

`EXECUTION_SLOT_MISMATCH` is a P0-5 fail-closed vocabulary item. It applies
when the actor's asserted slot cannot be bound exactly to durable facts: for
example, a different `project_context_id`, Work Unit, role, primary module,
branch/worktree identity, expected base SHA, current/accepted SHA, or state
revision. It also applies when a physical surface tries to claim a slot merely
because it contains similar chat history.

On this result the executor performs no continuation, no reassignment, no
state overwrite, and no Git mutation. It preserves the conflicting observations
as evidence and routes a `RECONCILIATION_REQUEST` through the existing role
protocol. Existing more-specific failures remain applicable, including
`RECONCILIATION_REQUIRED`, project/repository identity mismatch, stale state
revision, remote-head mismatch, and stale reviewed revision.

### 5.3 Cold rediscovery sufficiency

Cold rediscovery is sufficient when a new executor can reconstruct a safe next
action without Project Map, Resume, or the lost chat. The minimum durable set
is CONTROL, STATE (including slot facts), the referenced Work Unit,
instruction/result/evidence records, and reachable Git history/ref evidence.
The executor validates identity, expected state revision, Work Unit scope,
role correlation, SHA ancestry, and review/remote requirements, then derives
one of: resume the recorded `next_action`, enter `AWAITING_REVIEW`/`REVIEWING`,
mark the recorded blocker, or request reconciliation. If that set cannot
produce exactly one safe outcome, cold rediscovery is insufficient and the
only valid result is fail-closed reconciliation.

This deliberately makes cold rediscovery a safety test rather than an attempt
to rebuild invisible conversational context.

## 6. Module relationships and boundaries

| Module/contract | Relationship to P0-5 |
| --- | --- |
| `framework-core` | Owns authoritative STATE, STATE revision semantics, the STATE schema/template, and the physical persistence shape of slot records. It does not select lifecycle actions or perform continuation recovery. |
| `navigation-continuity` | Primary owner of logical slot lifecycle, continuation, restart, recovery, mismatch detection, and slot reattachment semantics. It consumes/presents authoritative STATE-backed slot facts and retains Project Map/Resume as derived artifacts; it does not own STATE or its schema/template. |
| `git-continuity` | Supplies exact SHA, ancestry, synchronization, and remote-verification checks; it does not assign slots or choose lifecycle transitions. |
| `role-communication` | Supplies role taxonomy, instruction/result envelopes, review and remediation causality. It does not own slot persistence or reassignment policy. |
| `identity-context` | Supplies project/repository binding that every slot validates before use; it does not turn a matching window into a slot. |
| `framework-validation` | Validates slot-record shape, legal lifecycle transitions, blocked-predecessor requirements, reset requirements, the one-active-Work-Unit invariant, slot/project/context bindings, and STATE-revision consistency. It neither owns nor mutates STATE/slots. |
| Work Units | Authorize the goal, scope, permissions, and acceptance to which a slot may bind. A slot cannot expand, synthesize, or replace that authorization. |
| Project Map and Resume | Derived navigation and cache views used for acceleration only; stale/missing views trigger bounded reads or cold rediscovery, not authority loss or fabricated state. |
| Result/Evidence | Durable, revision-bound support for lifecycle and handoff facts. They remain evidence/return records, not assignment or mutation authority. |

P0-5 owns slot lifecycle/continuity semantics and durable restart context;
STATE remains the authoritative persistence model owned by `framework-core`.
P0-6 Execution Telemetry Foundation may observe lifecycle events as telemetry
dimensions only. P0-6 must not own, mutate, infer, score, or automatically
transition/reassign any slot lifecycle fact.

## 7. Non-goals

P0-5 does not introduce:

- Agent Budget policy;
- telemetry scoring or adaptive dispatch;
- automatic reassignment;
- an eighth framework module;
- a central multi-project service;
- automatic cross-project orchestration; or
- physical-window authority.

It also does not change the existing control/state authority split, Work Unit
authorization model, Result/Evidence semantics, Git continuity contract, or
consumer projection ownership.

## 8. Future implementation and validation outline

The implementation plan must route changes through the Framework Module
Registry before editing assets. It is explicitly
`CROSS_MODULE_CHANGE_REQUIRED`: `framework-core` changes own the STATE schema,
STATE template, and physical slot-record persistence shape;
`navigation-continuity` changes own lifecycle, continuation, recovery, restart,
and derived navigation behavior; and `framework-validation` changes validate
their shared contract without taking ownership. It must add negative tests for
each invariant, especially stale revision, lost-window recovery, explicit
reassignment, serial review, `REVIEWING → BLOCKED` remediation handling,
blocked predecessor/reconciliation rules, `COMPLETED → IDLE → ACTIVE` reset and
reuse, one-active-Work-Unit enforcement, and `EXECUTION_SLOT_MISMATCH`
fail-closed behavior.

Before any future release, validation must prove that framework and
self-hosting project validation still pass; Registry routing remains exact;
navigation/continuity behavior preserves Project Map and Resume as derived;
Git/review checks bind accepted revisions; and an absent/stale derived cache can
still reach the cold-rediscovery decision above.

The new design artifact may temporarily be `unknown_path` in consumer
projection validation only when that is the sole projection failure. This is
`DEFERRED_NONBLOCKING`. P0-5 Design does not mutate the
projection manifest, projection payload, or release assets to remove that
stage-local deviation.
