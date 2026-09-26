# P2_MINIMUM_CAPABILITY_DESIGN_REVISION_002

P2_MINIMUM_CAPABILITY_DESIGN_REVISION_002 = PASS  
STATUS = DRAFT

Base revision: `P2_MINIMUM_CAPABILITY_DESIGN_REVISION_001.md`  
Architecture authority: `POST_C9_DEVELOPMENT_ROADMAP_DESIGN.v1.md`  
Phase authority: `POST_C9_DEVELOPMENT_ROADMAP_PLAN.v1.md`  
Execution boundary: `POST_C9_EXECUTION_GOVERNANCE_AMENDMENT.v1.md`  
Evidence boundary: `P1_FRAMEWORK_EFFECTIVENESS_EVIDENCE_DESIGN.v1.md`  
Related reviewed evidence: `p1-effectiveness-evidence-implementation-001/P1_GOVERNANCE_REVIEW_RECORD.md`, `p1-effectiveness-evidence-implementation-001/P1_CONTINUOUS_EVIDENCE_CYCLE_002_RESULT.md`

`PASS` means this draft revision is internally complete enough for design review. It does not freeze P2, satisfy the P2 entry gate by itself, authorize implementation, create plugin authority, or validate a working synchronization mechanism.

## Purpose

P2 v1 remains an optional GPT/Codex governance integration layer with exactly the four minimum capabilities defined by Revision 001:

1. Context Access;
2. Validation Access;
3. Evidence Feedback Routing;
4. Authorized Governance Capability Request.

This revision makes one previously implicit integration requirement explicit: **GPT and Codex must be able to recover and exchange the minimum durable governance facts through repository-backed authority without relying on conversation history or manual transcript copying.**

The design is **automatic durable state handoff**, not automatic conversation synchronization.

## Integration need

The existing Framework already persists durable authority and evidence in repository records, but current use still leaves a practical handoff gap between GPT and Codex: one side may produce a new Instruction, Result, Evidence record, state revision, or authoritative Git SHA while the other side requires an explicit resume/read step before it can act on that change.

P1 evidence already shows a related discoverability problem: the v2.7.2+fix.2 Result explicitly names an independent post-execution review as the next action, while the visible records inspected by P1 did not expose a distinct review outcome. That evidence remains `Deferred Pending More Evidence` and is not reclassified by this Design. It supports the need to make durable handoff and resume behavior reviewable; it does not authorize P2 implementation by itself.

The user-approved integration objective for this revision is therefore:

```text
Repository-backed durable authority
        ↓
minimum GPT/Codex handoff facts
        ↓
resume / validation / authorized capability request
        ↓
optional change notification
```

## Core design rule

```text
SYNC DURABLE FACTS, NOT PRIVATE CONTEXT
```

GPT private conversation context and Codex private execution context remain separate. P2 MUST NOT mirror or archive full conversations, raw prompts, scratchpads, hidden reasoning, private agent summaries, or implementation transcripts as a synchronization mechanism.

The shared handoff surface is limited to repository-backed, authority-relevant facts already permitted by Framework governance.

## Durable handoff facts

Where applicable to the active Project and Work Unit, a resume/handoff may expose the minimum reviewable set below:

```text
PROJECT_IDENTITY
REPOSITORY_IDENTITY
FRAMEWORK_VERSION / AUTHORITY_REF
STATE_REVISION
ACTIVE_WORK_UNIT_ID
CURRENT_INSTRUCTION_ID / REF
LATEST_RESULT_ID / REF
AUTHORITATIVE_GIT_SHA
VALIDATION_STATUS / FINDING_REFS
EVIDENCE_REFS
NEXT_AUTHORIZED_ACTION
BLOCKERS_OR_RECONCILIATION
```

These are derived from existing Project, CONTROL, STATE, Work Unit, Instruction, Result, Evidence, Guardrail, validation, and Git authority. This revision creates no second state database, synchronization database, conversation store, session registry, or parallel Work Unit system.

## Context Access clarification — repository-backed resume

`Context Access` includes a repository-backed resume operation with these semantics:

```text
identify project and repository
-> resolve current released/adopted Framework authority
-> read current CONTROL / STATE authority
-> resolve active Work Unit
-> resolve current Instruction / latest Result / Evidence as needed
-> validate freshness and Git identity
-> return a compact, permitted resume view
```

A resume view is a derived information surface. It is not an authority source and MUST NOT silently repair, rewrite, advance, or reconcile repository state.

If required identity, revision, freshness, or authority references cannot be established, the result is fail-closed and returns to the existing review/reconciliation path.

## GPT -> Codex durable instruction handoff

GPT may prepare or route an already-authorized Instruction through the existing governance path. The durable handoff is complete only when the Instruction and its authority bindings are represented by the existing repository authority and can be independently resolved by Codex.

```text
GPT decision / authorized Instruction preparation
-> repository-backed Instruction authority
-> Codex resume
-> validate project / Work Unit / permission / freshness
-> execute only if current authority permits
```

Plugin delivery, notification, routing success, or visibility of an Instruction never creates execution authority.

## Codex -> GPT durable result handoff

Codex returns governed execution through existing Result/Evidence and Git authority rather than through a chat transcript.

```text
Codex execution
-> Result / Evidence / authoritative Git SHA
-> required STATE update under existing authority, when applicable
-> durable repository publication
-> GPT resume
-> review / adjudication / next authorized action
```

A successful command, test result, commit, push, or plugin response does not by itself mean `COMPLETE`; existing completion and review contracts remain authoritative.

## Change notification — optional transport enhancement

P2 MAY support a thin `Change Notification` transport enhancement that informs an execution environment that repository-backed authority has changed and a resume should be performed.

Examples of a notification source may include an available repository event, connector event, webhook, polling result, or supported product event. **This Design intentionally does not select the transport.**

The notification contains no new governance decision. Its meaning is only:

```text
DURABLE_AUTHORITY_MAY_HAVE_CHANGED
-> perform governed resume
```

A notification MUST NOT:

- authorize execution;
- approve or reject review findings;
- declare completion;
- mutate STATE or Work Units;
- replace freshness or revision checks;
- deliver private conversation state;
- require a background daemon or central message bus.

If change notification is unavailable, explicit resume or bounded polling remains valid. Framework correctness must not depend on notification delivery.

## PR boundary

GitHub Pull Requests are not the normal GPT/Codex synchronization protocol.

PRs remain appropriate for existing cross-authority or integration boundaries, including:

- ordinary code review and branch integration;
- Consumer Project -> Framework Evidence Bridge where a reviewed cross-project contribution is required;
- other existing repository integration flows that independently justify a PR.

P2 MUST NOT require one PR per Instruction, Result, review finding, or GPT/Codex handoff. Repository-backed authority records and Git revisions are the durable handoff mechanism; PR is an integration/review surface, not a message queue.

## Mapping to the four minimum capabilities

| Existing P2 capability | Revision 002 clarification |
| --- | --- |
| Context Access | Includes repository-backed resume and compact durable handoff facts. |
| Validation Access | Resume/handoff may request existing Core validation to confirm identity, revision, freshness, scope, and applicable contracts. |
| Evidence Feedback Routing | Codex/GPT observations still route to the existing P1 evidence path; handoff telemetry does not automatically become Framework authority. |
| Authorized Governance Capability Request | A named existing capability request may be routed after resume confirms current authorization; successful transport grants no new authority. |

`Change Notification` is not a fifth governance capability. It is an optional transport concern that may trigger a governed resume.

## Failure semantics

Representative fail-closed cases include:

- project or repository identity mismatch;
- stale STATE revision;
- active Work Unit mismatch;
- Instruction/Result binding mismatch;
- authoritative Git SHA mismatch;
- stale or unavailable context where freshness is required;
- unsupported requested capability;
- notification received but current durable authority cannot be resolved;
- repository event observed but no authorized next action exists.

The response is an existing finding, reconciliation requirement, `ANALYSIS_ONLY`, or denied action as applicable under current Framework contracts. P2 introduces no substitute action and no new lifecycle state.

## Consumer and self-hosting boundary

Consumer Projects continue to own their source, project state, Work Units, evidence, adoption decisions, and local execution. The Plugin reads or routes only what existing authorization permits.

Framework self-hosting receives no bypass. Candidate Framework or Plugin rules remain non-authoritative until they complete their existing acceptance, validation, release, and activation lifecycle.

## Deferred beyond this revision

This revision does not authorize or design:

- real-time conversation mirroring;
- a synchronization server;
- a message queue;
- a background daemon;
- a central project-state store;
- a session manager;
- a plugin capability registry;
- a workflow engine;
- autonomous dispatch or autonomous optimization;
- Marketplace or platform architecture;
- a specific webhook, GitHub App, MCP, polling, or product-event implementation.

Transport selection belongs to the later technical Plan/Implementation only after the P2 Design and Plan gates are satisfied.

## Design validation

| Required check | Result | Basis |
| --- | --- | --- |
| Four-capability scope preserved | PASS | No fifth governance capability is introduced; notification is explicitly transport-only. |
| Repository remains durable authority | PASS | Resume and handoff derive from existing repository records and Git facts; no parallel state store is introduced. |
| GPT/Codex private context isolation | PASS | Full conversation/transcript synchronization is explicitly excluded. |
| Work Unit / Core authority preserved | PASS | Routing, notification, and successful handoff grant no authority and cannot modify scope or completion. |
| PR misuse avoided | PASS | PR remains review/integration/evidence-bridge tooling, not the routine handoff protocol. |
| Failure remains fail-closed | PASS | Missing or conflicting identity, revision, freshness, or scope returns to existing finding/reconciliation paths. |
| Framework remains usable without plugin | PASS | Explicit resume remains valid and notification is optional. |

These are design checks only. P2 implementation still requires the normal P2 entry gate, Design freeze, Plan freeze, a separately authorized implementation Work Unit, and pre-execution review.
