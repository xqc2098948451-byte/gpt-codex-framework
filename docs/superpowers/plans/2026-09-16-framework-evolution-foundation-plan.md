# Framework Evolution Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete project lifecycle authority and implementer/reviewer isolation using existing Framework responsibilities without expanding the architecture.

**Architecture:** Task 1 extends the existing execution-policy, ProcessReview, FrameworkFeedback, and governed-mutation validation path with repository-backed lifecycle facts. Task 2 extends the existing ExecutionSlot and review-validation path with canonical worktree, distinct-role, target-bound, and fail-closed dispatch facts. The final gate validates both tasks together and makes no mutation.

**Tech Stack:** Python standard library, existing JSON objects and templates, Markdown authority records, Git facts, and `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-16-framework-evolution-foundation-design.md`
**DESIGN_PATH:** `docs/superpowers/specs/2026-09-16-framework-evolution-foundation-design.md`
**DESIGN_SHA:** `baaf204b860717e6766042b2dbedbf7a99c988bd`

## Global Constraints

- Reuse `CONTROL.execution_policy`, `.harness/REASONING.md`, `ProcessReview`, `FrameworkFeedback`, `ExecutionSlot`, Project validation, Instruction/Result/Evidence, and Git authority before adding any helper.
- Preserve `TASK_SPLITTING = PROJECT_DETERMINED`; do not fix task count, reviewer count, parallelism, or agent count.
- Distinguish `ARTIFACT_ACCEPTED` from `EXECUTION_AUTHORIZED`; missing repository-backed correlation yields `IMPLEMENTATION_AUTHORIZATION = DENY`.
- Preserve legacy projects without `execution_policy`; require the new Strategy fact only for Foundation-governed implementation.
- Keep seven Framework modules. Create no schema, database, project-context store, conversation store, state machine, approval artifact, execution-context ID system, registry, Plugin, scoring, automatic learning, private-reasoning store, transcript store, or second lifecycle.
- `PRIVATE_PLUGIN_PHASE = DEFERRED`; create no `.agents/`, Plugin manifest, Plugin Skill, marketplace configuration, or updater.
- Apply TDD to each behavior mutation. A reviewer remains read-only and remediation remains `REVIEW_FINDING -> GPT adjudication -> FIX_INSTRUCTION -> fresh Implementer context`.

---

### Task 1: Project Lifecycle Completion

**Files:**

- Modify: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Modify: `.gpt-codex/scripts/framework_feedback.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Test: `.gpt-codex/tests/test_framework_feedback.py`
- Test: `.gpt-codex/tests/test_self_hosting_validator.py`
- Test: `.gpt-codex/tests/test_review_lifecycle.py`

**Existing interfaces to extend:**

- `validate_execution_policy(policy) -> list[str]` retains `None` acceptance for legacy projects and validates a project-specific `strategy_profile_id` when policy exists.
- `build_process_review(records, strategy_profile, usage=None) -> ProcessReview` remains the aggregate authority; bounded record validation must preserve `UNKNOWN` usage rather than estimate it.
- `validate_framework_feedback(record) -> list[str]` and `framework_feedback_authorizes_mutation(...) -> bool` retain the rule that ordinary-project feedback is not Framework mutation authority.
- `validate_governed_mutation_entry(...) -> list[str]` remains the one mutation gate and composes a repository-backed acceptance/authorization correlation check instead of introducing approval storage.
- `validate_pre_execution_review(...)` and `validate_review_lifecycle(...)` remain the pre- and post-execution review authorities.

**Produced behavior:**

- A Foundation-governed new-project implementation requires a stable project Strategy Profile and rejects silent strategy mismatch; legacy input without `execution_policy` remains valid outside that new gate.
- Repository-only recovery validates accepted Design/Plan refs, `AUTHORIZED` Work Unit, and a precise existing Instruction/Result/Evidence correlation over project context, Work Unit, artifact/revision, instruction/result identity, target revision, state revision, and completion gate. Absence, foreign identity, stale revision, or chat-only input yields `IMPLEMENTATION_AUTHORIZATION = DENY`.
- The existing Reasoning execution record and `ProcessReview` aggregate the bounded fields `WORK_UNIT_ID`, `FINAL_RESULT`, retry/intervention/review/remediation counts, handoff result, reliable-or-`UNKNOWN` usage, Git SHA, and Result ref without duplicating scope, Strategy, test evidence, changed files, or Git authority.

- [ ] **Step 1: Add failing lifecycle and repository-authorization tests.**

  In `test_framework_feedback.py`, cover a valid project-specific policy; rejected silent profile drift; legacy `None` policy acceptance; a bounded closure record with all required references; and an `UNKNOWN` usage value that remains `UNKNOWN`. In `test_self_hosting_validator.py` and `test_review_lifecycle.py`, cover valid repository-backed Design/Plan + `AUTHORIZED` Work Unit + correlated approval fact, then independently reject missing approval, foreign project/work-unit/ref, stale target/state revision, and a chat-only or artifact-exists substitute. Assert ordinary `FrameworkFeedback` still cannot authorize Framework mutation.

- [ ] **Step 2: Run the focused RED tests.**

  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_framework_feedback.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`
  Expected: the new lifecycle/authorization assertions fail because existing validation lacks the bounded Foundation correlation or record checks, not because a second authority is missing.

- [ ] **Step 3: Implement the minimum extensions in existing authorities.**

  Extend `framework_feedback.py` with the smallest pure validators needed for a Foundation lifecycle record and stable Strategy comparison; keep `ProcessReview` as the aggregation result and `FrameworkFeedback` non-authoritative. Extend `validate_project.py` with a pure repository-authorization correlation check called by `validate_governed_mutation_entry`; it returns existing fail-closed validation errors plus `IMPLEMENTATION_AUTHORIZATION = DENY` when required proof is absent. Keep all data within existing mappings and references. Update the Reasoning template with the bounded observable record fields and the repository-only recovery rule.

- [ ] **Step 4: Run focused GREEN and regression tests.**

  Run the three focused commands from Step 2. Also run `python -m unittest discover -s .gpt-codex/tests -p "test_harness_handoff.py"` to confirm `STRATEGY_PROFILE` remains a derived handoff reference. Expected: all pass; no score, automatic learning, approval artifact, or project-to-Framework mutation path is introduced.

- [ ] **Step 5: Validate and commit Task 1.**

  Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, and `git diff --check`. Inspect that only the listed Task 1 files changed, then create one normal Task 1 commit. Do not push.

### Task 2: Executor / Reviewer Mutual Isolation

**Files:**

- Modify: `.gpt-codex/scripts/continuity_resume.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/scripts/role_communication.py`
- Test: `.gpt-codex/tests/test_navigation_project_validation.py`
- Test: `.gpt-codex/tests/test_continuity_resume.py`
- Test: `.gpt-codex/tests/test_review_lifecycle.py`
- Test: `.gpt-codex/tests/test_role_authority.py`

**Existing interfaces to extend:**

- `validate_execution_slots(state) -> list[str]`, `validate_slot_transition(previous, current) -> list[str]`, and `validate_reviewer_assignment(...) -> list[str]` remain the ExecutionSlot authority.
- Existing path resolution in `continuity_resume.py` and `project_navigation.py` supplies the base for canonical worktree facts; repository binding remains in existing Git/repository authority rather than a new identity system.
- `validate_review_result(...)`, `validate_pre_execution_review(...)`, and `validate_review_lifecycle(...)` remain reviewer authority and finding/remediation authority.
- `role_communication.py` continues to own role/message taxonomy; it validates allowlisted role inputs rather than storing conversations.

**Produced behavior:**

- Implementer and Reviewer use distinct slots and canonical worktree identities. Canonicalization resolves absolute path, symlinks, aliases, actual Git worktree root, repository identity, and worktree/admin identity; aliases resolving to one real worktree are rejected as `SAME_WORKTREE`.
- Reviewer start requires a distinct clean tracked view whose `HEAD` equals the exact review target SHA. Reviewer mutation, commit, push, mutable/uncommitted review input, or unrecoverable tracked mutation invalidates review.
- Dispatch requires a fresh independent role context and role-specific allowlisted repository inputs. It blocks on absent proof and never treats a role-label change in one conversation as independent context.
- A `REVIEW_FINDING` stays result-side evidence; only GPT adjudication may produce a correlated `FIX_INSTRUCTION` for a fresh Implementer context.

- [ ] **Step 1: Add failing isolation and mediation tests.**

  In `test_navigation_project_validation.py` and `test_continuity_resume.py`, build paired slots for one Work Unit and assert acceptance only for distinct slot IDs and distinct canonical Git worktrees. Add alias, symlink, and normalized-path cases that resolve to the same worktree and require rejection. Add clean-view, exact-HEAD/target-SHA, reviewer tracked-mutation, and stale target cases. In `test_role_authority.py` and `test_review_lifecycle.py`, assert role allowlists reject private transcript/scratchpad/raw-prompt input, reject missing fresh-role-context proof, deny Reviewer mutation/commit/push, and require GPT-mediated correlated `FIX_INSTRUCTION` rather than raw reviewer transfer.

- [ ] **Step 2: Run the focused RED tests.**

  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_navigation_project_validation.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_continuity_resume.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`
  Run: `python -m unittest discover -s .gpt-codex/tests -p "test_role_authority.py"`
  Expected: the new canonical-worktree, fresh-context, and allowlist assertions fail because the existing slot/review contracts do not yet require every Foundation fact.

- [ ] **Step 3: Implement the minimum isolation extensions.**

  Add small pure canonical-worktree and pairwise-slot checks within `continuity_resume.py`; use existing repository facts and path resolution, with no persistent context ID, registry, database, or worktree manager. Compose their errors through `validate_execution_slots`, `validate_reviewer_assignment`, and the existing review validators. Add closed allowlist validation in `role_communication.py` and call it from the existing validation path. Preserve `validate_review_result`, `validate_pre_execution_review`, and `validate_review_lifecycle` as the only reviewer/finding lifecycle, and preserve the current post-execution remediation sequence.

- [ ] **Step 4: Run focused GREEN and regression tests.**

  Run all four commands from Step 2, plus `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py"`. Expected: all pass; a reviewer remains read-only, target binding is exact, aliases cannot bypass separation, and ordinary project feedback remains non-authoritative.

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
