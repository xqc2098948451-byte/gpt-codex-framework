# Framework Staged Closure Design — v2.7.2 through v2.7.4

## 1. Status and governing authority

**Status:** Proposed Design candidate; not accepted and not implementation authority.

This Design is authored against released Framework `2.7.1` at immutable base `6600a55ace1faf160309c82a1e5e2663c22d3dc6`. That released authority, `AGENTS.md`, `.gpt-codex/KERNEL.md`, `CONTROL.json`, `STATE.json`, the active Work Unit, release records, and current durable Result/Evidence records govern this candidate. This document does not govern its own creation, review, acceptance, implementation, publication, or activation.

```text
GROUP_A_RELEASE = 2.7.2
GROUP_B_RELEASE = 2.7.3
GROUP_C_RELEASE = 2.7.4
TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO
HISTORICAL_ACCEPTED_CONTRACT_REPAIR_DESIGN_REWRITTEN = NO
HISTORICAL_ACCEPTED_CONTRACT_REPAIR_PLAN_REWRITTEN = NO
PLUGIN_WORK_RESUMED = NO
BRIDGE_005_CREATED = NO
NEW_FRAMEWORK_MODULE_REQUIRED = NO
NEW_AUTHORITY_SUBSYSTEM_REQUIRED = NO
IMPLEMENTATION_AUTHORIZED_BY_THIS_DESIGN = NO
```

A local candidate, commit, tag, package, or chat claim is not an active-release fact. Release activation exists only after the current publication authority verifies it remotely.

## 2. Observed evidence

The v2.7.1 baseline establishes these facts:

- `VERSION`, release record/manifest, and remote main checkpoint identify v2.7.1.
- The Kernel already owns one State model, optimistic revision binding, evidence-source restrictions, narrow authority, and the generic `RECONCILIATION_REQUIRED` outcome.
- The accepted Contract Repair Design/Plan preserve Tasks 5–9 as future work; they do not authorize execution now.
- Instruction Envelope, `validate_project.py`, Result/Handoff, and review-lifecycle contracts are current authority/mutation-entry surfaces. `continuity_resume.py` and `git_continuity.py` already provide durable continuity mechanisms.
- `release_framework.py` packages from `VERSION`; `publication_contract.py` separates candidate authority from confirmed publication; release metadata/archive preserve historical facts.
- `execution_telemetry.py` is derived-observation-only, bounded, retained for limited duration, and excludes authority/private-reasoning fields. `framework_feedback.py` already supplies ProcessReview, FrameworkFeedback, and a no-mutation evolution boundary.
- Harness FEEDBACK/process records, Result-derived Handoff, and Harvest exist. Handoff is derived presentation; Harvest is evidence-based reuse, not policy authority.
- Deferred Plugin work is contextual evidence only, not a prerequisite or staged-closure work item.

These observations support design; they do not prove a future candidate valid, active, or authorized.

## 3. Problem statement

Post-v2.7.1 closure has three distinct needs. Execution reliability has proven friction around runtime assumptions, tool discovery, EOL-sensitive Git facts, subprocess diagnosis, interrupted runs, and release-state finalization. Accepted Contract Repair Tasks 5–9 still need native closure without semantic weakening, but only after the prior release is remotely active. Existing bounded telemetry/feedback needs a production path to decision-ready optimization input without becoming automatic Framework evolution.

The solution must reuse existing responsibility owners and must not become a workflow engine, authority layer, State system, Resume system, module, database, daemon, queue, or chat-history store.

## 4. Goals

1. Release one closure group per version: A/2.7.2, B/2.7.3, C/2.7.4.
2. Make Group A report deterministic ready, complete, blocked, partial, and reconciliation outcomes before destructive mutation.
3. Preserve Tasks 5–9 technical semantics exactly while placing their future execution in Group B after v2.7.2 remote activation.
4. Make Group C produce bounded evidence-linked improvement input for GPT/User Framework-management decisions, never mutation authority.
5. Make cold recovery derive one continuation from repository facts or return `RECONCILIATION_REQUIRED`.
6. Reuse current authority, review, Result, Evidence, Handoff, Resume, Harvest, release, and publication contracts.

## 5. Non-goals

This Design adds no eighth module, central authority subsystem, second STATE, second Work Unit model, second review lifecycle, second Resume system, database, queue, daemon, background service, conversation-history dependency, automatic Framework/Plugin evolution, automatic policy change/release, opaque scoring, resource governor, or speculative governance.

It neither creates bridge-005 nor resumes/modifies Plugin work. It does not rewrite accepted Design/Plan history, implement any group, change Framework behavior, or authorize a mutation. Local destructive-file safety remains operational support, not Framework policy authority.

## 6. Existing capabilities reused

| Responsibility | Existing owner | Intended boundary |
| --- | --- | --- |
| Runtime and commands | existing execution callers, `git_continuity.py` | Group A normalizes preflight/result facts in current paths. |
| Resume | `continuity_resume.py`, State, Work Unit, Result/Evidence | Group A derives status; it creates no Resume record. |
| Authority/review/mutation | Instruction Envelope, `validate_project.py`, Result/review lifecycle | Group B retains accepted native Contract Repair composition. |
| Release/activation | `release_framework.py`, `publication_contract.py`, metadata, Git continuity | Group A distinguishes candidate/local/published/remote-active facts. |
| Handoff | Result Return and Handoff | Group A derives recovery facts only. |
| Telemetry/feedback | `execution_telemetry.py`, `framework_feedback.py`, Harness records | Group C gives existing types a durable derivation path. |
| Reuse | Harvest and existing Framework-management lifecycle | Group C uses Harvest only for genuine reusable-extension evidence. |

## 7. Authority precedence

For every staged action:

```text
Current released Framework authority
  > Project durable authority
  > accepted Design/Plan
  > current valid Work Unit/State
  > user decision within its authority
  > auxiliary generic workflow guidance
```

This is the regression invariant for the observed `ROLE_ORCHESTRATION_FAILURE` / `AUTHORITY_ROUTING_FAILURE` class. Generic skills/tools can assist execution but may not invent a gate, invalidate valid approval, rewrite accepted Design/Plan semantics, grant mutation authority, or override Project authority. An irreconcilable conflict returns `RECONCILIATION_REQUIRED`; no new authority layer is created.

## 8. Three-release architecture

```text
2.7.1 REMOTELY ACTIVE
  -> Group A: Stabilization / Execution Reliability
  -> 2.7.2 REMOTELY ACTIVE
  -> Group B: Contract Repair Native Closure
  -> 2.7.3 REMOTELY ACTIVE
  -> Group C: Optimization Closed Loop
  -> 2.7.4 REMOTELY ACTIVE
```

Every group independently follows current implementation, verification, applicable independent pre/post review, GPT adjudication, release, remote-active verification, and machine-state finalization. A commit, tag, package, local test, or chat statement alone cannot advance the sequence.

## 9. Group A v2.7.2 architecture

Group A is minimum execution-layer stabilization, extending current owners rather than building a general runner.

1. **Runtime preflight:** before mutating work, observe supported PowerShell, Python, Git, encoding, authentication, and required capabilities. Incompatibility fails before mutation as blocked/reconciliation.
2. **Capability discovery:** do not assume `gh` or a fixed `pwsh` path. Select an observed supported mechanism; absent capability becomes a clear blocked/reconciliation result.
3. **Deterministic Git/EOL facts:** define canonical text/EOL behavior so validation/rehearsal see equivalent relevant Git facts without dependence on incidental `core.autocrlf`.
4. **Subprocess observability:** retain exit code, stdout, and stderr for relevant command results, including failure, subject to bounded/redacted evidence.
5. **Resumability:** derive at least `NOT_STARTED`, `PARTIAL`, `READY_TO_CONTINUE`, `ALREADY_COMPLETE`, and `FAILED` or `RECONCILIATION_REQUIRED`. This is a narrow projection over existing durable facts, not a workflow engine.
6. **Idempotency:** a supported completed safe operation rerun must become `ALREADY_COMPLETE`; unknown side effects remain blocked/reconciliation.
7. **Release/state finalization:** distinguish package-time from activation-time facts across VERSION, relevant CONTROL/STATE, release metadata, and remote verification without rewriting history.
8. **Machine-readable Handoff:** reuse Instruction/Result/Handoff/Resume to derive recovery facts and reduce copy/paste; the view is not authority.
9. **Manifest destructive safety:** reuse exact-path, allowed-parent, containment, and reparse-point checks for authorized operational cleanup only.

## 10. Group A failure/recovery semantics

| Observation | Outcome | Next action |
| --- | --- | --- |
| No durable start/result and preflight passes | `NOT_STARTED` | Start only under current authorization. |
| Incomplete operation with valid identity/scope/base | `PARTIAL` then `READY_TO_CONTINUE` | Re-observe and continue from durable evidence. |
| Matching safe postcondition/evidence | `ALREADY_COMPLETE` | Return evidence; do not repeat the side effect. |
| Missing runtime, auth, or tool before mutation | `BLOCKED` | Restore/reconcile capability; do not mutate. |
| Exit failure or incomplete subprocess evidence | `FAILED` | Diagnose from retained evidence; retry uses normal authorization. |
| Conflicting revision, identity, scope, base, release, or activation fact | `RECONCILIATION_REQUIRED` | Stop and reconcile through durable authority. |

The status names are derived runner observations, not Kernel-State replacements. Completion is idempotent only where operation identity, safe postcondition, scope, and evidence match; destructive or ambiguous reruns remain denied.

## 11. Group A acceptance boundary

Group A requires focused and clean-room proof of preflight, capability discovery, EOL determinism, subprocess evidence, resume/idempotency projection, release-state finalization, derived Handoff, and manifest safety. It then follows the existing full validation/review/publication lifecycle and must be remotely active as v2.7.2 before Group B starts.

Group A explicitly does not complete approval-evidence locator verification, actual Git scope oracle closure, native control-plane composition, first native seed consumption, or the production-shaped Contract Repair proof. Those are Group B.

## 12. Group B v2.7.3 inherited Contract Repair architecture

Group B is Contract Repair Native Closure. It starts only after fresh v2.7.2 remote-active and current repository/runtime observations. It inherits accepted Contract Repair Tasks 5–9 with unchanged technical semantics. Only future scheduling/release placement changes: this work now belongs in v2.7.3 after Group A activation.

The retained native composition includes immutable approval evidence, exact mutation scope, pre-execution review/freshness, State revision binding, one governed mutation entry, durable authority artifacts, and fail-closed outcomes. This Design neither creates nor authorizes `framework-contract-repair-bridge-005`; bridge-004 cannot be reused, and Group A/v2.7.2 does not complete native Contract Repair authority. Therefore Group B still requires the accepted future migration-authority lifecycle before any Tasks 5–9 mutation. It preserves the accepted future bridge-005 identifier/role unless separately accepted future authority supersedes it. Its payload, exact scope, base facts, review evidence, and approval are not frozen now: they are prepared and re-observed only after v2.7.2 is remotely active, then receive independent PRE_EXECUTION review, exact-payload USER_APPROVER approval, and remote verification before use. No candidate rule may self-authorize that bridge.

## 13. Contract Repair Tasks 5–9 inheritance rules

```text
TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO
```

- **Task 5:** external approval-evidence locator verification remains immutable/content-addressed; a mutable ref is reachability/discovery only.
- **Task 6:** actual Git changed-path oracle remains the post-execution scope authority. Before `COMMIT` or `PUSH`, it normalizes and unions tracked unstaged paths from `git diff --name-only -z`, tracked staged paths from `git diff --cached --name-only -z`, and untracked paths from `git ls-files --others --exclude-standard -z`; before `PUSH`, it additionally reads the committed candidate path set. The governed mutation path rejects `COMMIT`/`PUSH` unless each applicable actual-path union/set is a subset of the instruction's exact `scope_paths`. Expected evidence, including `files_changed`, and caller declarations never grant or replace authority.
- **Task 7:** native control-plane composition stays within the existing instruction/validator/governed-entry architecture, with anti-self-authorization, exact eligible scope, independent authority, review freshness, State revision binding, one governed mutation entry, and fail-closed behavior. It preserves two-hop approval correlation exactly: `APPROVAL_REQUEST.in_response_to_instruction_id = RECONCILIATION_REQUEST.instruction_id`; `APPROVAL_RESULT.response_to_instruction_id = APPROVAL_REQUEST.instruction_id`; and `APPROVAL_RESULT.approved_instruction.instruction_id = RECONCILIATION_REQUEST.instruction_id`. The gate compares the closed `approved_instruction` authority core exactly with the actual `RECONCILIATION_REQUEST` authority core, including identity, expected State revision, base SHA, normalized exact `scope_paths`, issuer/executor roles, authorized action, and immutable target Work Unit reference. The execution-side locator remains bound to immutable external approval evidence (`evidence_commit_sha`, path, and `blob_sha`) with required remote reachability/verification; a mutable ref head is transport/discovery only and cannot replace the bound commit/blob tuple.
- **Task 8:** first native seed materialization/bounded consumption retain accepted durable authority and exact limits; they are not general bootstrap authority.
- **Task 9:** production-shaped composed FIX/control-plane proof retains schema, taxonomy, role, correlation, and authority composition; fixtures/in-memory shortcuts cannot replace it.

Before execution, re-observe v2.7.2 active facts. Mechanical path/interface/ref drift may be rebound only if all listed authority semantics are identical. Any behavioral/authority difference requires a governed Design/Plan amendment.

## 14. Group B acceptance boundary

Group B acceptance requires all accepted Tasks 5–9 focused, composed, negative, and production-shaped proof obligations; the full established validation/review/release lifecycle; and v2.7.3 remote-active verification. No candidate/tag/publication attempt/review-only result is activation evidence.

## 15. Group C v2.7.4 optimization closed loop

```text
Execution / iteration facts
  -> ProcessReview
  -> FrameworkFeedback
  -> Improvement Candidate
  -> Framework-management review input
  -> GPT/User decision
  -> existing Framework evolution lifecycle
```

Group C begins only after v2.7.3 is remotely active. Its output is decision-ready evidence, never automatic Framework evolution, policy change, mutation, release, Plugin work, or authority grant.

## 16. Optimization data model/flow

1. **Fact:** an existing Result/Evidence/Harness process record or normalized observation supplies bounded identity, source, correlation, classification, completeness, and evidence references. No private reasoning, transcript, or full tool trace is stored.
2. **ProcessReview:** `framework_feedback.py` derives durable bounded review from valid process records and strategy profile. Existing counters become production facts through this derivation.
3. **FrameworkFeedback:** observed problems, friction, workarounds, preservation successes, and supporting references pass existing feedback/evolution-boundary validation.
4. **Improvement Candidate:** a bounded non-authorizing representation links feedback, evidence, recurrence/relevance, and a management question. It has no mutation permission, approved scope, or release status.
5. **Repetition/current relevance:** deterministic grouping uses explicit subject/classification/correlation/evidence and labels repeated, resolved, superseded, incomplete, or current evidence without opaque scoring.
6. **Review input:** candidates enter existing Framework-management GPT/User review. A later accepted Design/Plan and valid Work Unit are still required before any change.

Telemetry provenance, retention, redaction, idempotency, and observation-only limits remain mandatory. Incomplete/unknown observations stay bounded uncertainty or are excluded from conclusions.

## 17. Harvest relationship

Harvest is used only for evidence supporting reusable project-extension generalization under its existing contract. Defect/optimization feedback is not automatically Harvest, and Harvest is not Framework evolution authority. Feedback may reference Harvest where reusable extension semantics are genuinely at issue; otherwise the flows remain separate. “Generalize after repetition” applies without conflating the two purposes.

## 18. Cold recovery and window independence

Fresh windows derive recovery only from:

```text
AGENTS.md
-> repository identity
-> active VERSION / release
-> CONTROL
-> STATE
-> active Work Unit
-> accepted staged-closure Design immutable ref
-> accepted Master Plan immutable ref
-> latest Result/Evidence
-> relevant Git/GitHub facts
```

The output is exactly:

```text
PROJECT_IDENTITY
ACTIVE_FRAMEWORK_VERSION
ACTIVE_FRAMEWORK_SHA
CURRENT_GROUP
CURRENT_TARGET_RELEASE
CURRENT_WORK_UNIT
LAST_COMPLETED_TASK
LATEST_REVIEW_STATE
BLOCKERS
NEXT_AUTHORIZED_ACTION
DESIGN_REF
PLAN_REF
```

Every value identifies its durable source/ref. Missing, stale, conflicting, or multiply-authoritative continuation yields `RECONCILIATION_REQUIRED`. Chat memory and editable Handoff never establish progress. This is derived from existing State/Work Unit/Result/Evidence/Resume/Handoff/Git-continuity authority and adds no Resume subsystem.

## 19. Release/state finalization

| Fact | Meaning | Source |
| --- | --- | --- |
| `CANDIDATE` | Local candidate exists; no activation authority. | Candidate Result/Evidence and Git facts |
| `LOCALLY_VERIFIED` | Required local validation/review is bound to candidate identity. | Verification/review Result/Evidence |
| `PUBLISHED` | Existing publication authority confirms intended remote publication. | Publication Result/Evidence and remote observation |
| `REMOTE_ACTIVE` | Active remote branch/tag/release/version/SHA facts are independently bound. | Tool-observed remote verification and state finalization |

Packaging facts cover deterministic source version, artifact bytes, manifest/record, validation, and candidate identity. Activation facts cover remote identity bound to the exact reviewed candidate. Finalization records observed facts and never rewrites older evidence or infers remote-active from packaging.

## 20. Runtime/environment determinism

Group A preflight records runtime choice, Python/Git versions, encoding, executable discovery, auth/capability outcomes, and relevant EOL facts before mutation. No undeclared fallback is selected. Tool absence yields blocked/reconciliation. Canonical text behavior, rehearsal configuration, and path encoding are explicit and tested on Windows, including Chinese/Unicode paths. Diagnostics retain exit/stdout/stderr in bounded evidence.

An unavoidable implementation-level schema question is explicit: whether Group A derived status/finalization facts fit existing Result/Evidence/Handoff metadata or need additive schema representation. This Design assumes no permission to change schemas. The Master Plan must map facts against v2.7.1; if an additive field is necessary, owner, compatibility, migration, and consumer-projection impact require a governed amendment before implementation.

## 21. Testing strategy

- Focused contract tests cover preflight/discovery, canonical EOL, exit/stdout/stderr normalization, status derivation, safe idempotency, release-state facts, derived Handoff, and manifest safety.
- Negative tests cover unsupported shell, absent capability, malformed/missing evidence, stale/conflicting state, outside-manifest path, and ambiguous completion.
- Group B retains all accepted focused/composed Contract Repair, negative, and production-shaped assertions.
- Group C tests bounded/redacted observation, review derivation, feedback validation, recurrence/relevance, non-authorizing candidates, and Harvest separation.
- Each candidate runs current full framework/project/consumer-projection validation and applicable release/publication checks.

Tests prove candidate behavior; existing review/publication/remote verification establishes activation.

## 22. Clean-room E2E strategy

Real clean-room Windows coverage includes supported PowerShell 7; unsupported shell before mutation; Chinese/Unicode paths; EOL sensitivity under differing user configuration with equivalent canonical facts; tool-present/absent paths; applicable bootstrap/resume; partial execution plus authorized continuation; idempotent `ALREADY_COMPLETE`; and release-state finalization through independent remote-active observation.

Group A clean-room coverage proves its bounded scope, not final whole-project E2E closure. Groups B/C add composed clean-room evidence at their own boundaries.

## 23. Design/Plan dual-review lifecycle

```text
DESIGN_AUTHOR
-> independent CODEX_REVIEWER
-> GPT_REVIEWER
-> USER_APPROVER acceptance
-> immutable accepted Design ref
```

After acceptance, one Master Execution Plan covers all three groups sufficiently for repository-only recovery:

```text
PLAN_AUTHOR
-> independent CODEX_REVIEWER
-> GPT_REVIEWER
-> USER_APPROVER acceptance
-> immutable accepted Plan ref
```

The author never reviews its own artifact. These are current acceptance lifecycles, not extra execution gates.

## 24. Execution review lifecycle

Each group retains existing PRE_EXECUTION and POST_EXECUTION review, finding, GPT adjudication, bounded FIX instruction, and re-review semantics. A finding is evidence, not execution authority. Auxiliary workflow guidance cannot invalidate a valid decision. Real authority conflict uses current durable reconciliation, not a new gate.

## 25. Compatibility/migration impact

The intended future implementation is additive and responsibility-local only where proven necessary. Kernel versioning, schema compatibility, consumer projection, Result/Handoff compatibility, and historical evidence are preserved. No migration is authorized here.

Before each group, observe active release, repository identity, consumer packaging, runtime support, and current contract shape. Mechanical rebinding is allowed only with unchanged semantics. A behavioral/authority change, including the unresolved section-20 schema mapping, needs a governed amendment and compatibility/migration plan.

## 26. Security/authority invariants

- No authority means no mutation; model inference/telemetry cannot authorize.
- Group B retains exact durable scope, immutable approval evidence, anti-self-authorization, review freshness, State revision binding, and one governed mutation entry.
- Runtime/capability failure occurs before mutation; discovery cannot broaden access or select an unapproved publication channel.
- Handoff, Resume projections, telemetry, ProcessReview, Feedback, and Improvement Candidates are derived, never parallel authority.
- Destructive file operations use exact manifests, allowed parents, containment, and reparse-point protections.
- Group C excludes private reasoning, transcripts, and unrestricted tool traces.
- Generic skills/tools remain subordinate under section 7 precedence.

## 27. Release sequencing

```text
Group A -> 2.7.2 -> remote-active verification -> state finalization
Group B -> 2.7.3 -> remote-active verification -> state finalization
Group C -> 2.7.4 -> remote-active verification -> state finalization
```

Group A executes against active v2.7.1. Group B only after fresh v2.7.2 remote-active facts; Group C only after fresh v2.7.3 facts. B/C re-observe current facts and never replay chat/stale mappings. A+B and B+C combined releases are prohibited.

## 28. Plugin boundary

Plugin work remains deferred. This Design does not resume Task 3 Plugin Core, modify/activate/release Plugin, or make it a prerequisite for v2.7.2/v2.7.3/v2.7.4. Authority-routing evidence may inform a later Plugin decision but does not merge Plugin work into these releases.

## 29. Explicit deferred work

Deferred: Plugin work; bridge-005 payload preparation, scope selection, review evidence, approval, and authorization until after v2.7.2 is remotely active; automatic Framework/Plugin evolution; State Oracle work outside accepted Contract Repair scope; new authority/State/Resume/workflow systems; databases/services/daemons; opaque scoring/resource governance; and any semantic amendment or unresolved schema decision. Deferral grants no authority to resume.

## 30. Design acceptance criteria

Independent review can accept only if repository facts confirm:

1. all 30 sections are complete without unresolved markers or self-authorizing language;
2. A/B/C map one-to-one to 2.7.2/2.7.3/2.7.4 with remote-active gates;
3. Group A covers required reliability surfaces without claiming whole-project closure;
4. Tasks 5–9 are semantically unchanged and Group B waits for v2.7.2 activation;
5. Group C produces bounded review input without automatic mutation/policy/release/service/scoring;
6. precedence prevents generic guidance from overriding Framework/Project authority or inventing a gate;
7. cold recovery is repository-only and conflicts reconcile;
8. existing mechanisms are reused with no unnecessary module/subsystem/schema assumption;
9. Plugin remains deferred, this candidate neither creates nor authorizes bridge-005, and historical accepted artifacts are unchanged; and
10. the section-20 schema question is explicit and requires amendment if compatibility cannot be proven.
