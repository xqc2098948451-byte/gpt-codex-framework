# GPT–Codex Framework — Minimal Closed-Loop Harness Upgrade Design

## Status

**DESIGN FROZEN FOR REVIEW**

- Date: 2026-09-15
- Repository: `xqc2098948451-byte/gpt-codex-framework`
- P0 frozen baseline SHA: `224d8c0ebdfdc0aa7024f2c69f06fc6fcfe4c699`
- This document defines the next Harness-upgrade design only.
- No implementation, schema mutation, release, publication, or existing-P0 deletion is authorized by this document.

## 1. Purpose

The next Framework iteration must not grow into a larger governance platform. Its purpose is to preserve the capabilities already proven useful in P0 while reducing structural cost and converting the Framework into a reusable development Harness that is:

- reusable across different projects;
- recoverable after GPT/Codex session loss;
- separated from product and production runtime;
- able to collect bounded development-process evidence;
- able to produce Framework feedback without granting ordinary projects Framework mutation authority;
- able to evolve centrally inside `gpt-codex-framework` using evidence from many projects;
- simpler over time, not more complex by default.

The target is not “more agents.” The target is a smaller, durable development loop.

## 2. Highest Global Principle

The highest rule applies equally to:

- every ordinary project using the Harness;
- project directory design;
- GPT/Codex collaboration;
- the Harness itself;
- the `gpt-codex-framework` repository.

> **Preserve capability, compress structure; preserve the closed loop, remove duplication.**

Equivalent operational rule:

> Use the smallest structure that completely satisfies the real requirement. Reuse an existing responsibility before adding a new one. When adding structure, simultaneously check whether an older structure can be merged or removed. Never add complexity merely for symmetry, future possibility, agent count, Codex parallelism, or architectural appearance.

### 2.1 Derived global rules

1. **Minimal Closed Loop** — every feature must close a real user/development loop with the least structure needed.
2. **Single Authority** — the same fact must not have multiple competing authoritative owners.
3. **Recoverability First** — important development state must be recoverable from the repository and durable evidence without relying on a lost chat/session.
4. **Reference First** — reference authoritative artifacts instead of repeatedly copying their contents.
5. **Data Is Not Evolution Authority** — project data, telemetry, process reviews, and feedback cannot mutate Framework policy.
6. **Evidence-Driven Evolution** — global Framework changes require evidence from real project use; a single project problem can create a candidate, not a global rule.
7. **Centralized Framework Evolution** — only the `gpt-codex-framework` project can create or change global Harness rules, strategy profiles, templates, and Framework versions.
8. **Production Isolation** — Harness artifacts are development/governance assets and must not become product runtime dependencies.
9. **Responsibility Before Structure** — stable responsibility comes before directories/modules; directories must not be invented first and justified later.
10. **Stability Before Cosmetic Refactoring** — do not reorganize a working structure without measurable or operational benefit.

## 3. Target Project Layering

Every ordinary project must distinguish three semantic areas:

```text
HARNESS_ROOT
PRODUCT_ROOTS
DEPLOY_ROOTS
```

The default lightweight layout is:

```text
project/
├── .harness/
│   ├── RULES.md
│   ├── STATE.md
│   ├── REASONING.md
│   └── FEEDBACK.md
├── app/
└── ops/
```

The names `app/` and `ops/` are defaults, not mandatory global names. A project may use `src/`, `frontend/`, `backend/`, `infra/`, or multiple product roots when its real responsibility boundaries justify them.

### 3.1 HARNESS_ROOT

Contains only development/governance support:

- project and Harness rules;
- current development state;
- fixed development strategy and bounded process records;
- Framework feedback;
- other Harness-only artifacts that survive the minimum-structure test.

### 3.2 PRODUCT_ROOTS

Contain product functionality and product-owned tests/assets.

### 3.3 DEPLOY_ROOTS

Contain only artifacts genuinely required to build, deploy, migrate, configure, or operate the product in production.

### 3.4 Production invariant

Removing `HARNESS_ROOT` must not break product runtime behavior.

Production packaging must exclude Harness-only material unless an explicit, product-runtime requirement proves otherwise.

## 4. User / GPT / Codex Responsibility Boundary

### 4.1 User

The User owns:

- final project direction;
- major requirement decisions;
- major architecture trade-offs;
- approval of Framework evolution;
- approval of global development-strategy changes.

### 4.2 GPT

GPT owns:

- requirement understanding;
- architecture;
- project direction;
- decomposition of concrete work;
- deciding whether Codex is needed;
- deciding how many Codex tasks are needed for the current project;
- deciding whether tasks should be sequential or parallel;
- deciding whether/when independent review is justified;
- adjudicating issues that Codex is not authorized to decide.

There is no Framework-wide fixed Codex count, Work Unit count, reviewer count, or parallelism target.

### 4.3 Codex

Codex should perform development work after “what to do” is sufficiently explicit:

- implementation;
- tests;
- bounded fixes;
- verification;
- Git operations within granted scope;
- bounded code review when requested.

Codex must not infer global Framework evolution authority from local project execution.

## 5. Minimal Codex Task Protocol

The default task protocol should converge toward four required concepts:

```text
GOAL
SCOPE
CONSTRAINTS
DONE
```

Where needed, GPT may add references such as:

```text
BASE_SHA
PLAN_REF
STATE_REF
OPEN_FINDINGS
STRATEGY_PROFILE
```

These are references, not additional governance layers.

The Framework must avoid resending large repeated rule sets when a durable reference already exists.

Default policy: **REFERENCE_FIRST**.

The current complex P0 Work Unit / Instruction structures are not deleted by this Design. They are candidates for capability-preserving reduction during the reduction phase.

## 6. Minimal Harness Files

The target ordinary-project Harness begins with four conceptual files rather than many subsystems.

### 6.1 `RULES.md`

Long-lived project rules, including:

- project-specific constraints;
- current Harness version/profile;
- semantic root mapping (`HARNESS_ROOT`, `PRODUCT_ROOTS`, `DEPLOY_ROOTS`);
- production exclusion rules;
- stable maintenance rules;
- any project-specific rule that must survive session loss.

### 6.2 `STATE.md`

Only current, still-actionable development state, for example:

- current project status;
- current goal/task;
- current branch;
- base SHA;
- current SHA;
- current blocker;
- pending result reference;
- next action.

It must not become a permanent archive of every lifecycle transition.

### 6.3 `REASONING.md`

Despite the name, this file must not store private model chain-of-thought.

It stores observable and reusable development information:

- fixed project development strategy;
- decision style/profile identifiers;
- major architecture decisions;
- important method choices;
- bounded summaries of errors/retries;
- milestone/project process reviews;
- reasons for significant directory/structure changes.

If later evidence shows that the name causes persistent confusion, renaming may be proposed through normal Framework evolution rather than creating an extra file now.

### 6.4 `FEEDBACK.md`

Contains Framework feedback produced by the ordinary project. A minimal feedback item contains:

- problem;
- likely reason;
- how the project handled it;
- result;
- whether Framework change is recommended;
- supporting references/evidence.

Feedback is not Framework authority.

## 7. Operational Handoff and Cold Recovery

This is the highest-priority capability because the current project exposed a real handoff failure.

A fresh GPT receiving only the repository must be able to determine, without relying on prior chat/model memory:

- project identity;
- current project state;
- current task/goal;
- current branch and immutable Git SHA;
- fixed development strategy;
- most recent durable result or pending result;
- current blocker, if any;
- exactly one safe next action or an explicit reconciliation requirement.

### 7.1 Handoff output

Handoff should be a derived view, not a new authoritative state file.

Conceptual output:

```text
PROJECT
CURRENT_STATE
CURRENT_WORK
GIT
STRATEGY
LATEST_RESULT
PENDING_RESULT
BLOCKER
NEXT_ACTION
```

### 7.2 Recovery result states

At minimum:

```text
HANDOFF_READY
EXECUTION_CONTEXT_MISMATCH
RECONCILIATION_REQUIRED
```

### 7.3 Artifact discovery

Accepted design/plan or other long-lived task artifacts must be recoverable by immutable reference where such artifacts remain part of the resulting Harness.

A durable reference must prefer:

```text
path + immutable Git SHA
```

over branch-name searching.

### 7.4 Pending result discovery

If a GPT session disappears after Codex has completed work, a new GPT must be able to discover the unique relevant durable result using bounded correlations such as:

- project identity;
- current task identity/reference;
- instruction/review correlation where retained;
- target/current SHA;
- canonical result validity.

Zero matches means no pending result. More than one authoritative candidate means reconciliation; the Harness must not guess.

## 8. Fixed Project Development Strategy

At project start, choose a bounded, explicit strategy profile that remains stable through normal development and session changes.

Conceptual example:

```text
GPT_STRATEGY = MINIMAL_CLOSED_LOOP
CODEX_IMPLEMENTER_STRATEGY = MINIMAL_DIFF_TDD
CODEX_REVIEWER_STRATEGY = CONTRACT_FIRST
TASK_SPLITTING = PROJECT_DETERMINED
REVIEW_POLICY = RISK_OR_MILESTONE
INSTRUCTION_POLICY = REFERENCE_FIRST
RESULT_RETURN_POLICY = DURABLE_REF_FIRST
```

The strategy records observable working method, not private hidden reasoning.

Strategy changes during a project require an explicit versioned decision. A new GPT/Codex window does not itself change the strategy.

## 9. Simplified Execution Record

Do not build a complex Trace subsystem.

For important tasks, retain only data with demonstrated analytical/recovery value, such as:

- what task was performed;
- method/profile used;
- important decision summary;
- error category;
- Codex retry count;
- GPT intervention count;
- review count;
- remediation count;
- handoff success/failure;
- final result;
- key Git SHA/reference.

The record should be milestone-oriented, not every-tool-call logging.

## 10. Development Process Review

At major milestones and project closure, derive a bounded `PROCESS_REVIEW` from durable project facts.

Useful comparison fields may include:

- strategy profile/version;
- number of concrete Codex tasks;
- retries;
- GPT interventions;
- review rounds;
- remediation rounds;
- handoffs and handoff failures;
- significant findings;
- final project result/quality gate;
- duplicated context/instruction patterns when reliably observable;
- reliable resource/cost data if the platform exposes it.

If token/credit/cost is not reliably available, record `UNKNOWN`; do not fabricate precision.

The purpose is to compare methods across projects and iterations, not to create automated scoring authority.

## 11. Framework Feedback Boundary

Ordinary projects may produce:

```text
ITERATION_DATA
PROCESS_REVIEW
FRAMEWORK_FEEDBACK
IMPROVEMENT_CANDIDATE
```

They may not produce authoritative global policy or mutate the Framework.

A project may solve its own local problem using project authority. If it believes the solution should become universal, it records feedback instead of editing global Framework rules.

## 12. Centralized Framework Evolution

Only `gpt-codex-framework` may perform global Harness evolution.

Required path:

```text
ordinary projects
    ↓
feedback + process evidence
    ↓
gpt-codex-framework
    ↓
GPT analysis / improvement proposal
    ↓
User approval
    ↓
Codex implementation
    ↓
review / verification
    ↓
Harness vNext
    ↓
future project adoption
```

Projects must not directly push development-policy changes to one another.

Telemetry, process reviews, feedback, usage metrics, and local fixes are evidence inputs only. None of them authorize Framework mutation, release, or strategy changes.

## 13. Simple Efficiency Data

The first efficiency iteration explicitly avoids a Resource Governor, automatic budget engine, model scheduler, or agent scoring system.

Collect only metrics that can materially inform process decisions, for example:

- GPT intervention count;
- Codex task count;
- Codex retry count;
- review/remediation count;
- handoff failures;
- project result;
- token/credit/cost only when reliably available.

Initial efficiency gains should come primarily from:

- REFERENCE_FIRST;
- DURABLE_REF_FIRST;
- risk/milestone review rather than review-everything;
- GPT choosing task count per real project;
- eliminating duplicated protocols and state.

## 14. Project Directory Evolution

Project structure is not assumed to be perfectly designed at project start. It should evolve based on actual responsibility and change patterns while preserving capability.

### 14.1 Structure review moments

Perform structure review only at meaningful points:

- major architecture change;
- important milestone;
- project closure.

Do not restructure directories continuously.

### 14.2 Split signals

Consider splitting only when supported by real boundaries such as:

- clearly different responsibilities;
- different deployment/runtime lifecycles;
- security/permission boundaries;
- independent testing/ownership;
- repeated unrelated-change interference.

Do not split based on arbitrary file counts, line counts, agent counts, or parallelism convenience.

### 14.3 Merge/delete signals

Consider merging/removing when:

- directories always change together;
- separation has no independent responsibility;
- layers contain trivial wrappers only;
- old structure has been fully superseded;
- directory depth increases navigation cost without reducing coupling;
- duplicate `utils/common/core/helper` structures exist without clear ownership.

### 14.4 Structure capability invariant

Before structure optimization, define the existing required capability set. After the change:

```text
AFTER_CAPABILITIES >= BEFORE_CAPABILITIES
```

and at least one of these must be true:

- structural complexity measurably decreases;
- responsibility boundary becomes materially clearer;
- deployment/maintenance/testing cost measurably improves.

If none is true, do not reorganize.

### 14.5 Local vs global directory authority

An ordinary project may reorganize its own project directories under project authority.

It may not make its local structure a new Framework-wide template. A proposed global directory convention must flow through `FEEDBACK.md` to `gpt-codex-framework`, where multiple-project evidence can be evaluated.

## 15. Project Closure Convergence

At project completion, the Harness must converge rather than accumulate temporary development state.

Archive/remove transient items such as:

- obsolete current-task markers;
- resolved blockers;
- stale pending execution state;
- temporary debugging context;
- scratch/migration/experiment artifacts with no long-term responsibility.

Retain long-lived information such as:

- final project state;
- current architecture;
- important design decisions;
- maintenance rules;
- final strategy profile;
- relevant process review;
- Framework feedback and supporting references.

## 16. P0 Capability-Preservation and Reduction

The existing P0 system has proven useful capabilities that must not be lost casually, including:

- Git SHA/ancestry authority;
- Framework/Project separation;
- project isolation;
- role boundaries;
- review/remediation causality;
- cold recovery principles;
- production/consumer projection boundaries;
- fail-closed behavior on ambiguity.

However, the current structures that carry those capabilities are not automatically permanent.

During the reduction phase, explicitly evaluate whether the following can be merged, reduced, made derived-only, or removed while preserving capability:

- complex Work Unit structures;
- execution slots;
- Resume persistence;
- Project Map;
- telemetry runtime;
- large instruction/result envelopes;
- repeated schemas/validators;
- module boundaries that have no remaining independent responsibility.

No item is deleted solely because it is complex. Deletion requires a proven replacement path and regression proof.

## 17. Canonical Reuse During Transition

While existing P0 contracts remain active, cross-module consumers must reuse the canonical contract/schema/validator before applying local contextual checks.

The transition rule is:

```text
Canonical Contract Validation
→ Authority Validation
→ Local Context / Correlation Validation
```

Long term, the Framework should reduce the number of protocols requiring canonical validators rather than proliferate validators around an ever-growing contract set.

## 18. Explicit Non-Goals

Do not build unless future real-project evidence proves necessity:

- Planner subsystem;
- Dispatcher subsystem;
- general Agent Manager;
- fixed parallel execution model;
- complex role/permission matrix beyond demonstrated needs;
- Resource Governor;
- token scheduler;
- automatic model selector;
- automatic Framework optimizer;
- automatic learning/policy mutation;
- separate Learning/Incident/Proposal systems when one feedback/evolution flow is sufficient;
- persistent Trace platform;
- telemetry dashboard/analytics platform;
- directory-management engine.

## 19. Development Baseline Freeze

### 19.1 Highest lifecycle

```text
DRAFT
↓
USER_ACCEPTED
↓
PERSISTED
↓
PROJECTION_CLOSED
↓
BASELINE_VERIFIED
↓
DEVELOPMENT_BASELINE_FROZEN
```

Only `DEVELOPMENT_BASELINE_FROZEN` authorizes implementation.

### 19.2 Durable before frozen

An artifact is not formally frozen merely because GPT generated it or calculated a sandbox hash. Formal Design and Plan authority requires durable Git storage, referenced as immutable `Git SHA:path`. Chat content, GPT sandbox files, Codex uncommitted files, and local temporary copies are not formal frozen authority.

### 19.3 Whole-development freeze and revision

Before implementation, one verified development baseline contains the accepted Design, complete Implementation Plan, highest/global principles, architecture, fixed project strategy, complete task sequence, each task's GOAL/SCOPE/CONSTRAINTS/DONE, global acceptance conditions, production/project/framework boundaries, projection classification closure, and a clean validation/test baseline.

The baseline is immutable by Git commit. If the Design or Plan changes after execution begins: stop affected execution; GPT adjudicates; revise and persist the Design/Plan; close projection; validate the baseline; create `DEVELOPMENT_BASELINE vNext`; then resume. Execution never silently drifts from a frozen Plan.

The baseline freezes WHAT, WHY, ARCHITECTURE, CONSTRAINTS, TASK SEQUENCE, ACCEPTANCE, and STRATEGY. It does not freeze actual Codex count, actual parallelism, runtime blockers, findings, retry count, remediation, current accepted SHA, or next action; these remain execution-time facts.

### 19.4 GPT → Codex transfer visibility

Every user-facing GPT → Codex instruction begins with:

```text
是否需要你上传内容：需要 / 不需要
需要上传的内容：<文件列表或无>
读取来源：<Git SHA:path / 当前附件 / 其他明确来源>
```

When durable `Git SHA:path` is available, upload is not required. When content exists only in GPT's temporary environment, upload is required. Content already attached to the current Codex session does not require another upload. If access cannot be reliably established, upload is required and Codex must not guess. This human-facing preface grants no new authority.

## 20. Implementation Phases

Implementation should proceed in dependency order rather than by module count.

### Phase 1 — Project / Harness / Production Isolation

Prove semantic roots, packaging boundaries, and that Harness removal does not break product runtime.

### Phase 2 — Operational Handoff + Minimal Current State

Provide a single repository-based recovery path and converge current-state representation toward the minimum required for safe continuation.

### Phase 3 — Fixed Development Strategy + Simplified Execution Record

Persist observable project strategy and bounded process records across sessions.

### Phase 4 — Framework Feedback + Central Evolution Boundary

Ordinary projects emit feedback/evidence; only `gpt-codex-framework` can turn it into global Framework evolution after User approval.

### Phase 5 — Minimal Codex Task Protocol + Result Return Simplification

Reduce repeated task/result payloads while preserving scope, constraints, completion proof, Git safety, and review causality.

### Phase 6 — Simple Efficiency Metrics

Record only reliable, decision-useful process/cost metrics.

### Phase 7 — Existing Framework Reduction Review

Evaluate P0 structures one by one. Preserve capabilities; merge/delete only where regression evidence proves equivalence or improvement.

## 21. Acceptance Scenarios

The Harness upgrade is not complete until at least these scenarios are proven:

1. **Fresh GPT handoff:** a new GPT with repository access can identify current state, strategy, relevant result, and one safe next action without old chat.
2. **Artifact off default branch:** a required accepted artifact can be resolved by immutable reference rather than branch-name guessing.
3. **Lost GPT after Codex completion:** a new GPT can discover the unique pending durable result or fail closed on ambiguity.
4. **Harness/production separation:** production packaging excludes Harness assets and product runtime works without `.harness/`.
5. **Stable strategy across sessions:** replacing GPT/Codex sessions does not silently change the project strategy profile.
6. **Compact task/result exchange:** normal GPT↔Codex traffic relies primarily on bounded goals/references/results rather than repeated full governance text.
7. **Ordinary-project feedback only:** an ordinary project can produce useful Framework feedback but cannot mutate Framework policy.
8. **Central evolution only:** a Framework-wide strategy/rule change is performed only inside `gpt-codex-framework` after User approval.
9. **Process evidence:** completed projects produce enough bounded data to compare development methods without collecting hidden reasoning.
10. **Directory convergence:** milestone/closure review can keep, merge, split, move, or remove project structure based on real responsibility while preserving capability.
11. **No automatic self-evolution:** telemetry/process/feedback data cannot independently change policies or release a new Framework.
12. **P0 capability preservation:** any removed/merged P0 structure has regression evidence proving no loss of required capabilities.

## 22. Final Closed Loop

```text
User
  ↓
GPT — direction / architecture / concrete task decomposition
  ↓
Codex — bounded implementation / tests / review
  ↓
Product code + bounded development record
  ↓
Project completion / process review
  ↓
Framework Feedback
  ↓
gpt-codex-framework
  ↓
Multi-project evidence analysis
  ↓
User approval
  ↓
Harness vNext
  ↓
Future projects adopt intentionally
```

In parallel, every project structure follows:

```text
minimal initial structure
  ↓
real development
  ↓
observed responsibility/change patterns
  ↓
structure review
  ↓
keep / merge / split / move / delete
  ↓
project closure convergence
```

Both loops remain governed by the same rule:

> **Preserve capability, compress structure; preserve the closed loop, remove duplication.**

## 23. Design Closure Boundary

This Design is intentionally closed at the conceptual level above.

Implementation planning must not add new subsystems merely because implementation detail is still unknown. If implementation discovers that a new structure is required, that requirement must be justified against the highest global principle and routed back for explicit design adjudication rather than silently expanding scope.

The next permitted step after this Design is repository storage/review of this exact Design, followed by an implementation plan. No implementation starts from this document alone.
