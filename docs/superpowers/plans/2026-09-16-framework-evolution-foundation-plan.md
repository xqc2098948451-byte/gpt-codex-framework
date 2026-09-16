# Framework Evolution Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete project lifecycle authority and implementer/reviewer isolation using existing Framework responsibilities without expanding the architecture.

**Architecture:** Task 1 extends the existing execution-policy, ProcessReview, FrameworkFeedback, and governed-mutation validation path with repository-backed lifecycle facts. Task 2 extends the existing ExecutionSlot and review-validation path with canonical worktree, distinct-role, target-bound, and fail-closed dispatch facts. The final gate validates both tasks together and makes no mutation.

**Tech Stack:** Python standard library, existing JSON objects and templates, Markdown authority records, Git facts, and `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-16-framework-evolution-foundation-design.md`
**DESIGN_PATH:** `docs/superpowers/specs/2026-09-16-framework-evolution-foundation-design.md`
**DESIGN_SHA:** `c955888d9075672e11a350efd96640ac4da68763`

## Global Constraints

- Reuse `CONTROL.execution_policy`, `.harness/REASONING.md`, `ProcessReview`, `FrameworkFeedback`, `ExecutionSlot`, Project validation, Instruction/Result/Evidence, and Git authority before adding any helper.
- Preserve `TASK_SPLITTING = PROJECT_DETERMINED`; do not fix task count, reviewer count, parallelism, or agent count.
- Distinguish `ARTIFACT_ACCEPTED` from `EXECUTION_AUTHORIZED`; missing repository-backed correlation yields `IMPLEMENTATION_AUTHORIZATION = DENY`.
- Preserve legacy projects without `execution_policy`; require the new Strategy fact only for Foundation-governed implementation.
- Keep seven Framework modules. Create no schema file, database, project-context store, conversation store, state machine, approval artifact, execution-context ID system, registry, Plugin, scoring, automatic learning, private-reasoning store, transcript store, or second lifecycle. The sole permitted existing-schema extension is optional Instruction `target_work_unit_ref`, used only by the governed repository-backed mutation gate.
- `PRIVATE_PLUGIN_PHASE = DEFERRED`; create no `.agents/`, Plugin manifest, Plugin Skill, marketplace configuration, or updater.
- Apply TDD to each behavior mutation. A reviewer remains read-only and remediation remains `REVIEW_FINDING -> GPT adjudication -> FIX_INSTRUCTION -> fresh Implementer context`.

---

### Task 1: Project Lifecycle Completion

**Files:**

- Modify: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Modify: `.gpt-codex/schemas/instruction-envelope.schema.json`
- Modify: `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`
- Modify: `.gpt-codex/scripts/framework_feedback.py`
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Test: `.gpt-codex/tests/test_framework_feedback.py`
- Test: `.gpt-codex/tests/test_self_hosting_validator.py`
- Test: `.gpt-codex/tests/test_review_lifecycle.py`
- Test: `.gpt-codex/tests/test_instruction_envelope.py`

**Existing interfaces to extend:**

- `validate_execution_policy(policy) -> list[str]` retains `None` acceptance for legacy projects and validates the accepted project `strategy_profile_id` when policy exists; the Foundation gate compares each governed Work Unit reference to that project authority.
- `build_process_review(records, strategy_profile, usage=None) -> ProcessReview` remains the aggregate authority; bounded record validation must preserve `UNKNOWN` usage rather than estimate it.
- `validate_framework_feedback(record) -> list[str]` and `framework_feedback_authorizes_mutation(...) -> bool` retain the rule that ordinary-project feedback is not Framework mutation authority.
- `instruction_envelope.build_instruction_envelope(...)` and the existing Instruction schema/template gain optional `target_work_unit_ref = {path, sha}` without breaking legacy parsing; it binds the logical `target_work_unit` to a durable immutable Work Unit artifact.
- `validate_governed_mutation_entry(...) -> list[str]` remains the one mutation gate and composes root-aware repository-backed acceptance/authorization correlation through that locator instead of introducing approval storage.
- `validate_pre_execution_review(...)` and `validate_review_lifecycle(...)` remain the pre- and post-execution review authorities.

**Produced behavior:**

- A Foundation-governed new-project implementation requires one accepted Project Strategy Profile across its governed Work Units. Each Work Unit may reference, but cannot redefine or silently override, that profile; silent cross-Work-Unit drift fails. Strategy baseline comes from `CONTROL.execution_policy` at the Instruction base SHA. A change passes only when the repository-resolved `AUTHORIZED` Work Unit owns `.gpt-codex/CONTROL.json`, its optional locator matches `target_work_unit`, and existing Instruction/project/state/artifact authority correlates. Legacy input without `execution_policy` remains valid outside that new gate.
- Repository-only recovery validates accepted Design/Plan refs, an immutable `target_work_unit_ref` resolving at its Git SHA to the `AUTHORIZED` Work Unit, and a precise existing Instruction/Result/Evidence correlation over project context, Work Unit, artifact/revision, instruction/result identity, target revision, state revision, and completion gate. Missing, foreign, stale, Git-unresolvable, or chat-only input yields `IMPLEMENTATION_AUTHORIZATION = DENY`.
- The existing Reasoning execution record and `ProcessReview` aggregate the bounded fields `WORK_UNIT_ID`, `FINAL_RESULT`, retry/intervention/review/remediation counts, handoff result, reliable-or-`UNKNOWN` usage, Git SHA, and Result ref without duplicating scope, Strategy, test evidence, changed files, or Git authority.

- [ ] **Step 1: Add failing lifecycle and repository-authorization tests.**

  In `test_framework_feedback.py`, add only these Strategy lifecycle cases: (A) two governed Work Units that reference the same accepted Project profile pass; (B) a silent Work Unit profile drift fails; (C) a Git-base Strategy change passes only through an `AUTHORIZED` locator-resolved Work Unit owning `.gpt-codex/CONTROL.json`; and (D) legacy `None` policy acceptance passes. Do not add Strategy registry, history, or parallel-subsystem tests. Lock reliable record-level usage preservation/compatible aggregation, `UNKNOWN` fallback, and explicit aggregate compatibility. In `test_self_hosting_validator.py` and `test_review_lifecycle.py`, cover a valid Git-resolved Design/Plan + `AUTHORIZED` Work Unit locator + correlated authorization fact; reject missing object, wrong SHA/path, Work Unit ID mismatch, cross-project object, in-memory mapping without locator, stale target/state revision, and chat-only or artifact-exists substitutes. In `test_instruction_envelope.py`, exclusively lock the optional `target_work_unit_ref` Instruction Envelope contract: valid `{path, sha}` shape; rejection of missing/empty path, missing/invalid SHA, and unexpected shape; legacy builder/parser compatibility without the field; and consistent field name, optionality, and shape across builder, template, and schema. Assert ordinary `FrameworkFeedback` still cannot authorize Framework mutation.

- [ ] **Step 2: Run the focused RED tests.**

  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_framework_feedback.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py"`
  Expected: the new lifecycle/authorization assertions fail because existing validation lacks the bounded Foundation correlation or record checks, not because a second authority is missing.

- [ ] **Step 3: Implement the minimum extensions in existing authorities.**

  Extend the existing Instruction schema/template and `instruction_envelope.py` only to carry optional `target_work_unit_ref {path, sha}` while retaining legacy parsing. Extend `framework_feedback.py` with the smallest pure lifecycle-record, Strategy, and usage aggregation validators; keep `ProcessReview` as the aggregation result and `FrameworkFeedback` non-authoritative. Extend `validate_project.py` with root-aware Git resolution of the locator and immutable Work Unit Design/Plan refs, called by `validate_governed_mutation_entry`; it derives baseline Strategy from `CONTROL.json` at the base SHA and returns existing fail-closed errors plus `IMPLEMENTATION_AUTHORIZATION = DENY` when proof is absent. Keep all data within existing artifacts and references; create no registry or new artifact. Update the Reasoning template only with the bounded observable record fields and repository-only recovery rule.

- [ ] **Step 4: Run focused GREEN and regression tests.**

  Run the three focused commands from Step 2. Also run `python -m unittest discover -s .gpt-codex/tests -p "test_harness_handoff.py"` to confirm `STRATEGY_PROFILE` remains a derived handoff reference. Expected: all pass; no score, automatic learning, approval artifact, or project-to-Framework mutation path is introduced.

- [ ] **Step 5: Validate and commit Task 1.**

  Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, and `git diff --check`. Inspect that only the listed Task 1 files changed, then create one normal Task 1 commit. Do not push.

### Task 2: Executor / Reviewer Mutual Isolation

**Files:**

- Modify: `.gpt-codex/scripts/continuity_resume.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Test: `.gpt-codex/tests/test_navigation_project_validation.py`
- Test: `.gpt-codex/tests/test_continuity_resume.py`
- Test: `.gpt-codex/tests/test_review_lifecycle.py`
- Test: `.gpt-codex/tests/test_instruction_envelope.py`

**Existing interfaces to extend:**

- `validate_execution_slots(state) -> list[str]` remains limited to single-slot shape, lifecycle, and state consistency; it must not discover physical worktrees or Git identity. `validate_slot_transition(previous, current) -> list[str]` and `validate_reviewer_assignment(...) -> list[str]` retain their existing slot/reassignment responsibility.
- `.gpt-codex/scripts/validate_project.py:validate_pre_execution_review(...)` is the project-level reviewer-correlation composition entry. It consumes nonpersisted root-aware facts derived by the existing Git-continuity path `.gpt-codex/scripts/continuity_resume.py:_execution_slot_recovery(...) -> _git_recovery_is_current(root, slot, state)`, rather than moving Git discovery into `validate_execution_slots`.
- `validate_review_result(...)`, `validate_pre_execution_review(...)`, and `validate_review_lifecycle(...)` remain reviewer authority and finding/remediation authority.
- `.gpt-codex/scripts/instruction_envelope.py:build_instruction_envelope(...)` is the existing Review Request issuance boundary. It preserves `.gpt-codex/scripts/role_communication.py:validate_action_authority(...)` as role/action authority and checks dispatcher-supplied runtime freshness and role-specific input-source allowlist preconditions before a `REVIEW_REQUEST` envelope is issued. The input-source observation is runtime-only and non-authoritative: it is neither serialized into an Instruction Envelope nor added to project state or JSON schema.

**Produced behavior:**

- Implementer and Reviewer use distinct slots and canonical worktree identities. Root facts are derived as `absolute path -> resolve alias/symlink -> actual Git worktree root -> bind repository and Git worktree/admin identity`, then include `HEAD` and cleanliness before pairwise comparison. Aliases resolving to one real worktree are rejected as `SAME_WORKTREE`; no `worktree_id`, registry, database, or session identity is persisted.
- Reviewer start requires the reviewer canonical worktree to differ from the implementer canonical worktree, reviewer `HEAD == REVIEW_TARGET_SHA`, `REVIEW_TARGET_SHA == IMPLEMENTATION_RESULT_SHA`, and a clean tracked reviewer worktree. A dirty/mutated view, wrong SHA, or a post-review view no longer at the target yields `REVIEW_RESULT_CANNOT_PASS`.
- Dispatch requires two independent runtime-only, non-authoritative preconditions: `FRESH_INDEPENDENT_ROLE_CONTEXT_VERIFIED = TRUE`, and role input-source kinds contained in a role-specific allowlist. `CODEX_IMPLEMENTER` allows only `DURABLE_PROJECT_AUTHORITY`, `GOVERNED_ARTIFACT`, `GOVERNED_INSTRUCTION`, `REPOSITORY_CONTENT`, and `VERIFICATION_EVIDENCE`; `CODEX_REVIEWER` allows that same set plus `ACCEPTED_FINDING`. Any unclassified, raw prompt, transcript, scratchpad, private reasoning/summary, or uncommitted private-workspace source is outside the allowlist and yields `ROLE_DISPATCH = BLOCKED`. The input observation is not written to an envelope, schema, identity, registry, database, project state, or context system. Freshness proves only that the dispatcher/platform supplied that precondition, never that a model has not seen prior context; missing, false, or unknown freshness yields `REVIEW_REQUEST_DISPATCH = DENY` and `ROLE_DISPATCH = BLOCKED` independently of input-source validation.
- A `REVIEW_FINDING` stays result-side evidence; only GPT adjudication may produce a correlated `FIX_INSTRUCTION` for a fresh Implementer context.

- [ ] **Step 1: Add failing isolation, runtime-input, and mediation tests.**

  Add only these focused cases. (A) In `test_continuity_resume.py` and `test_navigation_project_validation.py`, aliases that resolve to the same actual worktree fail isolation. (B) Distinct physical worktrees pass when all other correlations hold. (C) In `test_review_lifecycle.py`, a reviewer with a wrong `HEAD` / review target SHA fails. (D) A dirty or mutated reviewer view denies review pass. (E) In `test_instruction_envelope.py`, missing, false, or unknown `FRESH_INDEPENDENT_ROLE_CONTEXT_VERIFIED` prevents a Review Request from being issued; retain this independently from input-source tests. (F) In that same test file, a Reviewer with only approved durable source kinds passes; an Implementer transcript, scratchpad, private reasoning, raw prompt, temporary private summary, or uncommitted private-workspace source for Reviewer input fails closed; and a Reviewer transcript, scratchpad, private reasoning, raw prompt, or unadjudicated Reviewer conclusion for Implementer input fails closed. (G) An unknown source kind fails closed for either role. (H) A GPT-adjudicated governed `FIX_INSTRUCTION` source remains allowed for a fresh Implementer, while a raw Reviewer conclusion remains blocked. Test source-kind membership only; do not scan source text or add persistence tests.

- [ ] **Step 2: Run the focused RED tests.**

  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_navigation_project_validation.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_continuity_resume.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py"`
  Expected: the new canonical-worktree, fresh-context, runtime role-input allowlist, and mediation assertions fail because the existing contracts do not yet require every Foundation fact.

- [ ] **Step 3: Implement the minimum isolation extensions.**

  Extend the existing Git-continuity responsibility in `continuity_resume.py` around `_execution_slot_recovery(...)` and `_git_recovery_is_current(root, slot, state)` to derive the required nonpersisted root facts. Preserve `validate_execution_slots(state)` as slot-only; do not compose root facts through it. At the existing project-level entry `validate_project.validate_pre_execution_review(...)`, compare derived facts only after canonicalization and enforce canonical reviewer/implementer inequality, exact implementation/review target/`HEAD` correlation, clean entry, and unchanged target after review. At the existing issuance boundary `instruction_envelope.build_instruction_envelope(...)`, add the smallest pure runtime validation of dispatcher-observed input source kinds against an allowlist for `CODEX_IMPLEMENTER` and `CODEX_REVIEWER`; unknown or out-of-role kinds block dispatch. Keep source kinds runtime-only and do not serialize them into the envelope, schema, or project state. Independently fail closed before constructing a `REVIEW_REQUEST` unless the dispatcher supplies `FRESH_INDEPENDENT_ROLE_CONTEXT_VERIFIED = TRUE`. Reuse `role_communication.validate_action_authority(...)` unchanged for role/action authority. Preserve `validate_review_result`, `validate_pre_execution_review`, and `validate_review_lifecycle` as the only reviewer/finding lifecycle, including `REVIEW_FINDING -> GPT adjudication -> FIX_INSTRUCTION -> fresh Implementer context`.

- [ ] **Step 4: Run focused GREEN and regression tests.**

  Run all four commands from Step 2, plus `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py"`. Expected: all pass; a reviewer remains read-only, target binding is exact, aliases cannot bypass separation, fresh-context and source-allowlist preconditions remain independent, GPT-mediated remediation remains valid, and ordinary project feedback remains non-authoritative.

- [ ] **Step 5: Validate and commit Task 2.**

  Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, and `git diff --check`. Inspect that only the listed Task 2 files changed, then create one normal Task 2 commit. Do not push.

## Final Gate: Integrated Verify-Only

**Files:** none.

- [ ] **Step 1: Verify all Foundation contracts without mutation.**

  Confirm Task 1's Strategy binding, no silent drift, legacy compatibility, repository-only recovery, repository-backed authorization, bounded process evidence, `UNKNOWN` usage, and ordinary-project feedback boundary. Confirm Task 2's distinct slots, canonical distinct worktrees, alias rejection, clean exact-SHA reviewer view, reviewer mutation invalidation, allowlists, fresh role context, and GPT-mediated remediation.

- [ ] **Step 2: Verify architecture and capability preservation.**

  Confirm module registry remains seven modules; no database, state machine, project-context store, approval artifact, private-reasoning store, automatic learning, scoring system, Plugin, or new schema exists. Evaluate the existing `evaluate_structure_change(before_capabilities, after_capabilities, evidence)` with the retained capability set and a measurable maintenance/complexity benefit; require `ALLOW` and `AFTER_CAPABILITIES >= BEFORE_CAPABILITIES`.

- [ ] **Step 3: Run integrated validation.**

  Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`; `python .gpt-codex/scripts/validate_framework.py`; `python .gpt-codex/scripts/validate_project.py .`; `python -m unittest discover -s .gpt-codex/tests -p "test_*.py"`; and `git diff --check`. Inspect `git status --short` and the Task 1/Task 2 commit paths. Expected: zero unknown/missing/invalid projection paths, all validators and tests pass, and no verify-only commit is created.

## Plugin Boundary

`PRIVATE_PLUGIN_PHASE = DEFERRED`. After Foundation closure, run capability-before-Design again using real Foundation evidence before deciding whether Plugin work is necessary or how many tasks it needs. This Plan creates no Plugin artifact or Plugin implementation work.
