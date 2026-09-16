# Framework Evolution Foundation Design

## Status and authority

**Status:** accepted design persisted for independent review.
**Scope:** Foundation only; it authorizes neither implementation nor Plugin work.
**Governing principle:** Preserve capability, compress structure; preserve the closed loop, remove duplication.

This Design establishes two bounded capabilities: project lifecycle completion and executor/reviewer mutual isolation. It reuses the current Framework's project, control, state, Rules, Reasoning, Work Unit, Instruction, Result, Evidence, Git, ProcessReview, FrameworkFeedback, ExecutionSlot, and review authorities. `PRIVATE_PLUGIN_PHASE = DEFERRED_BUT_REQUIRED`; no Plugin is implemented by this Foundation.

Once the required capabilities close and no material finding remains, further optimization opportunities are deferred. Best practice, future convenience, possible scalability, more observability or metrics, cleaner abstraction, and parallelism efficiency do not authorize new structure. Only `CURRENT_REQUIRED_CAPABILITY_CANNOT_CLOSE` can justify a further mechanism.

## Scope A — Project lifecycle completion

### Strategy lifecycle and compatibility

The Foundation reuses `CONTROL.execution_policy`, `.harness/REASONING.md`, `ProcessReview`, `FrameworkFeedback`, and `STRATEGY_PROFILE`. A new project must have a project-specific Strategy Profile before formal implementation. `TASK_SPLITTING = PROJECT_DETERMINED` remains fixed: this Design does not fix Codex task count, reviewer count, parallelism, or agent count.

Strategy is stable at the Project level for its governed lifecycle: one accepted Project Strategy Profile governs every governed Work Unit. The required invariant is `WU.strategy_profile_id == PROJECT.accepted_strategy_profile_id`, unless existing repository authority records an explicit governed Strategy change. A Work Unit may reference that accepted profile but cannot redefine or silently override it; `WORK_UNIT_LOCAL_OVERRIDE = DENY` and `SINGLE_WORK_UNIT_FAILURE != STRATEGY_CHANGE_AUTHORITY`.

The only change path is `explicit requirement -> governed strategy change -> new/updated accepted Project Strategy authority -> persistence/validation -> subsequent Work Units use the new authority`. This reuses existing repository-backed authority and adds no Strategy registry, history database, or parallel Strategy system. Legacy projects that lack `execution_policy` do not automatically become invalid; compatibility remains fail-closed only when a new Foundation-governed implementation requires the new fact.

### Repository-backed discussion, acceptance, and authorization

There is no `DISCUSSION` repository state, `CONVERGED` repository state, Project Convergence Summary authority, approval database, or new persistence artifact. The interaction is exactly:

```text
discussion
-> GPT presents consolidated design
-> user approves
-> existing repository authorities are persisted or updated
-> validation
-> implementation authorization
```

Repository recovery must work when all ChatGPT/Codex conversations no longer exist. The continuing authority is only `PROJECT`, `CONTROL`, `STATE`, Rules, Reasoning, accepted Design, accepted Plan, Work Unit, artifact references, evidence/result references, and Git SHA.

`ARTIFACT_ACCEPTED` and `EXECUTION_AUTHORIZED` are separate facts. A pre-implementation gate accepts only repository-backed, correlatable existing facts: accepted Design/Plan refs; an `AUTHORIZED` Work Unit; and the precise approval/authorization fact in an existing Instruction, Result, or Evidence object. Applicable correlation covers `project_context_id`, `work_unit_id`, artifact ref/revision, instruction/result identity, target revision, state revision, and completion gate. Chat-only approval, remembered consent, a chat summary, model inference, and artifact existence are not authorization. Missing required proof yields `IMPLEMENTATION_AUTHORIZATION = DENY`. No generic `APPROVAL.json` is introduced.

### Bounded Work Unit process evidence and preference boundary

Every governed Work Unit closure records bounded observable process data through the existing Reasoning execution record / `ProcessReview` responsibility. The first-stage record contains:

```text
WORK_UNIT_ID
FINAL_RESULT
CODEX_RETRIES
GPT_INTERVENTIONS
REVIEW_ROUNDS
REMEDIATION_ROUNDS
HANDOFF_RESULT
USAGE
GIT_SHA
RESULT_REF
```

`USAGE` is either a reliably observed value or `UNKNOWN`; it is never estimated. The record references rather than duplicates Work Unit scope, Strategy, test evidence, changed files, or Git authority. It adds no efficiency, strategy, agent, or user-fit score.

An ordinary Project may provide `ProcessReview`, `FrameworkFeedback`, and observable evidence only. `ORDINARY_PROJECT_FEEDBACK != FRAMEWORK_MUTATION_AUTHORITY`. Global evolution follows:

```text
ordinary projects
-> evidence
-> Framework Management
-> GPT cross-project interpretation
-> recommendation
-> USER APPROVAL
-> governed Framework mutation
```

There is no automatic learning, automatic strategy switching, automatic scoring, or project-to-Framework mutation path.

## Scope B — Executor / reviewer mutual isolation

### Durable slot and worktree separation

The existing `ExecutionSlot` remains the authority; `NEW_EXECUTION_CONTEXT_ID = NO`. For one review cycle:

```text
IMPLEMENTER_SLOT_ID != REVIEWER_SLOT_ID
CANONICAL_IMPLEMENTER_WORKTREE_IDENTITY != CANONICAL_REVIEWER_WORKTREE_IDENTITY
IMPLEMENTER_PRIVATE_CONTEXT ∩ REVIEWER_INPUT = ∅
REVIEWER_PRIVATE_CONTEXT ∩ IMPLEMENTER_INPUT = ∅
```

`validate_execution_slots(state)` remains a single-slot shape, lifecycle, and state-consistency validator. It does not discover physical worktrees or Git identity. Project-level review validation composes derived root-aware Git facts through the existing Git-continuity responsibility, rather than widening that slot validator.

Worktree identity is a runtime-derived validation fact, never a persisted `worktree_id`, registry, database, or session identity. Its canonicalization pipeline is `absolute path -> resolve alias/symlink -> actual Git worktree root -> bind repository and Git worktree/admin identity`; root facts include repository identity, physical worktree root, Git worktree/admin identity, `HEAD`, and cleanliness. Pairwise isolation checks run only after these facts are derived. Two different strings that resolve to the same real worktree are `SAME_WORKTREE` and review is rejected.

### Reviewer view and exact target binding

At review start, all of the following are required:

```text
REVIEW_VIEW_DISTINCT = TRUE
REVIEW_HEAD_SHA == REVIEW_TARGET_SHA
REVIEW_TARGET_SHA == IMPLEMENTATION_RESULT_SHA
REVIEW_TRACKED_WORKTREE_CLEAN = TRUE
```

Reviewer authority is limited to `READ`, `TEST`, `VALIDATE`, and `REPORT`; it excludes `MUTATE_APPROVED_SCOPE`, `COMMIT`, and `PUSH`. The reviewer canonical worktree must differ from the implementer canonical worktree. If tracked source is changed by the Reviewer, is dirty at review entry, has the wrong `HEAD`, or cannot be proven still at the exact target revision after review, `REVIEW_RESULT_CANNOT_PASS`.

### Fresh role context and allowlisted inputs

Durable repository separation does not prove that a model never saw another role's private conversation. The existing Review Request issuance / role-action boundary must therefore require the runtime-only, non-authoritative precondition `FRESH_INDEPENDENT_ROLE_CONTEXT_VERIFIED = TRUE` plus an input allowlist. It proves only that the dispatcher/platform supplied this precondition; it cannot prove what a model has ever seen. Missing, false, or unknown freshness yields `REVIEW_REQUEST_DISPATCH = DENY` and `ROLE_DISPATCH = BLOCKED`; changing a role label in one conversation is insufficient.

This freshness fact is evaluated before a Review Request is issued and is neither persisted nor added to any schema, identity, context system, registry, or database. Existing instruction and role authority remain the only dispatch boundary; freshness does not become verification or result authority.

Implementer input may include Project authority, `CONTROL`, `STATE`, Rules, Strategy Profile, accepted Design/Plan, Work Unit, Execution/Fix Instruction, required repository files, and required verification evidence. It must not proactively receive Reviewer chat, transcripts, scratchpads, private reasoning, raw prompts, or unadjudicated conclusions.

Reviewer input may include Project authority, `CONTROL`, Rules, accepted Design/Plan, Work Unit acceptance, Review Request, exact target SHA, repository content at that SHA, target diff, required verification evidence, and accepted prior finding refs when needed. It must not receive Implementer chat, transcripts, scratchpads, private reasoning, raw prompts, self-justification, or an uncommitted mutable workspace.

### Finding mediation

The existing causal lifecycle is retained:

```text
REVIEW_FINDING
-> GPT adjudication
-> ACCEPT / REJECT / MODIFY
-> FIX_INSTRUCTION
-> fresh Implementer role context
```

Raw Reviewer conversation never goes directly to the Implementer. A finding is evidence, not execution authority.

## Architecture and explicit non-goals

The Framework module count remains `7 -> 7`. Responsibility first belongs to existing `framework-core`, `identity-context`, `role-communication`, `navigation-continuity`, and `framework-validation`; other current responsibilities are involved only when genuinely required.

This Foundation does not create a new Framework module, database, project-context store, conversation store, state machine, approval artifact, Execution Context identity subsystem, Agent Registry, Reviewer Registry, Session Manager, Context Server, automatic learning, automatic strategy switching, automatic scoring, private chain-of-thought storage, raw-prompt archive, scratchpad archive, token trace, Resource Governor, quota manager, token scheduler, parallelism optimizer, second review lifecycle, second Work Unit system, or second compatibility/update system. It also creates no Plugin, `.agents/` directory, Plugin manifest, Plugin Skill, marketplace configuration, or Plugin updater.

Any implementation must reuse existing schema where it can express the required contract. If a required Design capability cannot be expressed by the existing structure, execution stops with an explicit proven blocker; it must not infer a new schema, module, subsystem, or context system.
