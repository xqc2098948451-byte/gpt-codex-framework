# P0-5 Framework Design Continuity & Sufficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish STATE-backed `ACTIVE_EXECUTION_SLOTS` so governed work can restart safely without making a window, cache, or telemetry authoritative.

**Architecture:** `framework-core` owns authoritative STATE, STATE revisions, schema/template, and slot persistence. `navigation-continuity` owns logical lifecycle, continuation, recovery, mismatch detection, and reattachment. `framework-validation` validates their shared contract; Project Map/Resume and P0-6 remain derived only.

**Tech Stack:** Python standard library, JSON Schema Draft 2020-12, `unittest`, existing Framework validators.

**Spec:** docs/superpowers/specs/2026-09-13-framework-design-continuity-sufficiency-design.md

## Global Constraints

- Primary module/responsibility: `navigation-continuity` / `project navigation and continuity`.
- Implementation is `CROSS_MODULE_CHANGE_REQUIRED`: `framework-core`, `navigation-continuity`, `framework-validation`, and `release-projection` when the manifest is classified.
- Slot statuses are exactly `IDLE`, `ACTIVE`, `BLOCKED`, `AWAITING_REVIEW`, `REVIEWING`, and `COMPLETED`.
- `slot.state_revision` is the authoritative `STATE.revision` for the record/transition. No second slot revision sequence exists.
- P0-6 may observe slots only; it cannot create, assign, reassign, transition, recover, authorize, or score them.
- **NO PRODUCTION TASK MAY EXECUTE UNTIL P0-5 IMPLEMENTATION BASELINE RECONCILIATION WITH CANONICAL v2.6.0 MAIN IS GPT-VERIFIED.** Target: `f49cd5afaa07aabaedac516d1c0e2c3524eef845`. This Plan does not perform reconciliation, merge, rebase, cherry-pick, release, or publication.
- Every production task follows RED, verify RED, minimal implementation, GREEN, then commit.

## File map and route checks

| Exact path | Registry owner | Purpose |
| --- | --- | --- |
| `.gpt-codex/schemas/state.schema.json` | `framework-core` | Slot types, nullability, conditional shape. |
| `.gpt-codex/project-template/STATE.template.json` | `framework-core` | Empty canonical slot collection. |
| `.gpt-codex/scripts/kernel_rules.py` | `framework-core` | Generic STATE revision preconditions only; never normative P0-5 lifecycle edges. |
| `.gpt-codex/scripts/continuity_resume.py` | `navigation-continuity` | Lifecycle, recovery, mismatch and derived resume behavior. |
| `.gpt-codex/scripts/project_navigation.py` | `navigation-continuity` | Derived navigation only; never slot authority. |
| `.gpt-codex/scripts/validate_project.py` | `framework-validation` | Fail-closed slot validation orchestration. |
| `.gpt-codex/tests/test_navigation_project_validation.py` | `framework-validation` | All new slot behavior fixtures/tests. |
| `.gpt-codex/tests/test_self_hosting_validator.py` | `framework-validation` | Self-hosting regression coverage. |
| `.gpt-codex/release/consumer-projection-manifest.json` | `release-projection` | Implementation-stage path classifications. |

Before every physical change, use `classify_changed_assets()` and `route_responsibility()` from `.gpt-codex/scripts/framework_module_routing.py`. An asset without exactly one owner stops with `MODULE_ROUTE_UNRESOLVED`. New behavioral tests are intentionally added only to `.gpt-codex/tests/test_navigation_project_validation.py`, the existing `framework-validation`-owned test asset; no unowned test path is created.

### Task 0: Reconcile accepted P0-5 artifacts with canonical v2.6.0 before production execution

**Files:** Create `feature/framework-design-continuity-sufficiency-implementation` from canonical main; modify no accepted Design/Plan artifact directly. **Inputs:** `accepted_design_sha=ec74a57d10cd7db1b2e56e122d4bbaf12b6a3ceb`, `accepted_plan_sha=ACCEPTED_PLAN_SHA`, and `canonical_main_sha=f49cd5afaa07aabaedac516d1c0e2c3524eef845`.

**Evidence interface:** Return GPT-verifiable command evidence, not a new P0-5 persistence artifact, with exactly `accepted_design_sha`, `accepted_plan_sha`, `canonical_main_sha`, `implementation_base_sha`, `design_content_preserved`, `plan_content_preserved`, `registry_compatibility_result`, `state_schema_compatibility_result`, `navigation_api_compatibility_result`, `validation_api_compatibility_result`, `projection_compatibility_result`, `changed_path_conflicts`, `full_suite_result`, `framework_validation_result`, `project_validation_result`, and `blockers`. Prove compatibility by `git diff --name-status` against each accepted SHA, Registry routing on every intended path, schema/API comparison, fresh remote `ls-remote`, framework/project validators, full tests, and projection validation.

- [ ] **Step 1: Merge accepted artifacts** — Verify fresh `origin/main`, create the named branch/worktree at canonical main, then run `git merge --no-ff ACCEPTED_PLAN_SHA -m "chore: reconcile P0-5 continuity plan with v2.6.0"`. The reconciliation merge `R` must have parent 1 canonical main and parent 2 accepted Plan; no rebase, cherry-pick, amend, or history rewrite.
- [ ] **Step 2: Verify R tree and debt** — Prove `main → R` changes exactly the accepted Design and Plan paths, and compare both blobs to accepted SHAs. Run framework/project/full-suite/projection validation; projection unknown must be exactly 2 and missing required 0. Any other path, failure, or debt returns `RECONCILIATION_REQUIRED`.
- [ ] **Step 3: Create B0 and verify** — Modify only `.gpt-codex/release/consumer-projection-manifest.json`, classify both accepted paths `DEVELOPMENT_HISTORY`, commit one normal `R → B0`, then rerun full validation requiring projection unknown/missing 0 and clean worktree.
- [ ] **Step 4: Hard stop** — **NO TASK 1 OR LATER MAY EXECUTE UNTIL GPT independently verifies R parents, main→R paths/blobs, R→B0 manifest-only scope, baseline evidence, and P0_5_CLEAN_IMPLEMENTATION_BASELINE = GPT_VERIFIED with BLOCKERS = NONE.**

### Task 1: Define the STATE slot model

**Files:** Modify `.gpt-codex/schemas/state.schema.json`, `.gpt-codex/project-template/STATE.template.json`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** Add `active_execution_slots: array[ExecutionSlot]`. `instruction_id`, `review_request_id`, `review_result_ref`, `finding_ref`, `remediation_authorization_ref`, `fix_instruction_id`, and `reviewer_reassignment_ref` are `string|null`; `blocked_from_status` is slot-status-or-null and `block_reason` is bounded-string-or-null. IDLE clears every correlation; ACTIVE populates instruction; review entry/result populates review fields; remediation BLOCKED requires finding/review/predecessor/reason; BLOCKED→ACTIVE requires authorization/fix; only explicit current-state `reviewer_reassignment_ref` permits reviewer change.

- [ ] **Step 1: Write failing tests**

```python
def test_idle_slot_rejects_stale_assignment(self):
    result = self._validate(self._state_with_slot(status="IDLE", base_sha=SHA))
    self.assertIn("IDLE_SLOT_ASSIGNMENT_FORBIDDEN", result.stdout)

def test_blocked_slot_requires_reason_and_predecessor(self):
    result = self._validate(self._state_with_slot(status="BLOCKED", block_reason=None))
    self.assertIn("BLOCKED_SLOT_FIELDS_REQUIRED", result.stdout)
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect both tests to fail because no slot contract exists.
- [ ] **Step 3: Minimal implementation** — Add the JSON Schema `ExecutionSlot` definition/conditional rules and template `"active_execution_slots": []`; preserve all existing STATE and Kernel statuses.
- [ ] **Step 4: Verify GREEN** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect all tests to pass.
- [ ] **Step 5: Commit** — `git add .gpt-codex/schemas/state.schema.json .gpt-codex/project-template/STATE.template.json .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: define state execution slot contract"`

### Task 2: Implement navigation-owned transitions and core revision preconditions

**Files:** Modify `.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/kernel_rules.py`, `.gpt-codex/scripts/validate_project.py`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** `framework-core` exposes only `validate_slot_state_revision(current_revision: int, expected_revision: int) -> list[str]`. `navigation-continuity` exposes `validate_execution_slots(state: Mapping) -> list[str]` and `validate_slot_transition(previous: Mapping, current: Mapping) -> list[str]`; it owns every legal edge including `COMPLETED → IDLE → ACTIVE` and BLOCKED semantics. `validate_project.py` calls both and reports `STATE: <code>` without mutation.

- [ ] **Step 1: Write failing tests**

```python
def test_completed_to_active_requires_idle_reset(self):
    self.assertIn("SLOT_IDLE_RESET_REQUIRED", validate_slot_transition(self.completed_slot(), self.active_slot()))

def test_idle_old_work_unit_requires_reconciliation(self):
    self.assertIn("RECONCILIATION_REQUIRED", validate_execution_slots(self._state_with_slot(status="IDLE", work_unit_id="WU-1")))
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect missing helpers/error codes.
- [ ] **Step 3: Minimal implementation** — Put the legal edge graph, IDLE rules, and BLOCKED semantics in `continuity_resume.py`. Keep `kernel_rules.py` limited to generic revision equality. Forbid `COMPLETED → ACTIVE`, generic `BLOCKED → blocked_from_status`, stale writes, and non-null IDLE assignment/correlation fields.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect valid transitions and all fail-closed cases to pass.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/kernel_rules.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: validate execution slot lifecycle"`

### Task 3: Implement assignment and completion reset

**Files:** Modify `.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/validate_project.py`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** Add `activate_execution_slot(state, slot_id, assignment, expected_revision) -> dict` and `reset_completed_slot(state, slot_id, closure_refs, expected_revision) -> dict`; both return `revision == expected_revision + 1` or raise `ValueError("RECONCILIATION_REQUIRED")`. `assignment` supplies work unit, primary module, context, branch/worktree where applicable, base/current SHA, and non-idle action.

- [ ] **Step 1: Write failing tests**

```python
def test_reset_clears_all_current_assignment_facts(self):
    reset = reset_completed_slot(self.completed_state(), "S-1", ["result-1"], 4)
    slot = reset["active_execution_slots"][0]
    self.assertEqual(slot["next_action"], "AWAIT_ASSIGNMENT")
    self.assertIsNone(slot["primary_module"])
    self.assertIsNone(slot["last_accepted_sha"])

def test_activate_requires_idle_and_fresh_values(self):
    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
        activate_execution_slot(self.active_state(), "S-1", self.assignment("WU-2"), 4)
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect absent APIs.
- [ ] **Step 3: Minimal implementation** — `COMPLETED → IDLE` requires closure references, nulls every current Work Unit field/correlation/block field, and sets `AWAIT_ASSIGNMENT`; history remains Work Unit/Result/Evidence/Git/retained STATE history. Only `IDLE → ACTIVE` atomically creates fresh values; enforce one non-completed Work Unit per Implementer slot.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect reset/reuse, silent replacement, carry-forward, and stale-writer cases to pass.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: reset and assign execution slots"`

### Task 4: Enforce blocked remediation causality

**Files:** Modify `.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/validate_project.py`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** Add `block_for_remediation(state, slot_id, finding_ref, review_ref, expected_revision) -> dict` and `resume_authorized_remediation(state, slot_id, authorization_ref, fix_instruction, expected_revision) -> dict`. The first writes `REVIEWING → BLOCKED`, predecessor `REVIEWING`, and `AWAITING_REMEDIATION_AUTHORIZATION`; the second returns `ACTIVE` only after current-fact reconciliation and a valid FIX instruction.

- [ ] **Step 1: Write failing tests**

```python
def test_finding_blocks_but_does_not_authorize_mutation(self):
    slot = block_for_remediation(self.reviewing_state(), "S-1", "finding-1", "review-1", 7)["active_execution_slots"][0]
    self.assertEqual(slot["block_reason"], "AWAITING_REMEDIATION_AUTHORIZATION")

def test_reviewer_message_cannot_resume_blocked_slot(self):
    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
        resume_authorized_remediation(self.blocked_state(), "S-1", None, None, 8)
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect missing causal APIs.
- [ ] **Step 3: Minimal implementation** — Use existing `validate_instruction_authority()` for `FIX_INSTRUCTION`. A finding/Reviewer message is never authority. Mismatched finding, review, authorization, Work Unit, SHA, or STATE revision fails closed.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect only explicit GPT/User authorization plus valid instruction resumes.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: govern slot remediation recovery"`

### Task 5: Add cold recovery, mismatch, and reviewer seriality

**Files:** Modify `.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/project_navigation.py`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** Extend `load_continuity_resume(..., execution_slot_id: str|None=None) -> dict`; binding mismatch returns `status="EXECUTION_SLOT_MISMATCH"` and `reconciliation_required=True`. Add `validate_reviewer_assignment(slot, reviewer_ref, expected_revision) -> list[str]`.

- [ ] **Step 1: Write failing tests**

```python
def test_cold_resume_rejects_slot_context_or_sha_mismatch(self):
    result = load_continuity_resume(self.slot_fixture(context="foreign"), "repo-a", execution_slot_id="S-1")
    self.assertEqual(result["status"], "EXECUTION_SLOT_MISMATCH")

def test_second_reviewer_requires_explicit_reassignment(self):
    self.assertIn("RECONCILIATION_REQUIRED", validate_reviewer_assignment(self.reviewing_slot(), "reviewer-2", 9))

def test_recovery_mismatch_matrix_and_window_non_authority(self):
    for field in ("project_context_id", "work_unit_id", "role", "primary_module", "branch", "worktree", "base_sha", "current_head_sha", "last_accepted_sha", "state_revision"):
        self.assertEqual(load_continuity_resume(self.slot_fixture(mismatch=field), "repo-a", execution_slot_id="S-1")["status"], "EXECUTION_SLOT_MISMATCH")
    for condition in ("missing_durable_fact", "stale_state", "dirty_worktree", "stale_resume", "replacement_window"):
        self.assertEqual(load_continuity_resume(self.slot_fixture(condition=condition), "repo-a", execution_slot_id="S-1")["status"], "RECONCILIATION_REQUIRED")

def test_reviewer_seriality_and_reassignment_evidence(self):
    self.assertEqual(validate_reviewer_assignment(self.reviewing_slot(), "reviewer-1", 9), [])
    self.assertEqual(validate_reviewer_assignment(self.reviewing_slot(reviewer_reassignment_ref="instruction-1"), "reviewer-2", 9), [])
    self.assertIn("RECONCILIATION_REQUIRED", validate_reviewer_assignment(self.reviewing_slot(source="telemetry"), "reviewer-2", 9))
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect keyword/helper absent.
- [ ] **Step 3: Minimal implementation** — Bind CONTROL, STATE slots, Work Unit, instruction/Result/Evidence, and Git facts before action. The Step 1 matrix covers every named mismatch plus missing fact, stale revision, dirty/ambiguous worktree, missing Map with authoritative recovery, stale Resume, and replacement window. Map/Resume only supply hints. Keep one reviewer; only evidence-bound reassignment is allowed; Reviewer Result/finding and telemetry never reassign.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect mismatch/cold recovery/seriality results to pass and derived navigation to remain non-authoritative.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/project_navigation.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: recover and review execution slots"`

### Task 6: Final cross-module verification only

**Files:** `MUTATION = NONE`. Verify only `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_release_packaging.py`, and `.gpt-codex/tests/test_publication_authority.py` in `MODE = VERIFY_ONLY_REGRESSION`; no Task 6 commit.

**Interfaces:** Manifest classifies every actual implementation path once. The final routing decision includes `release-projection`; consumer bytes do not contain management identity. No Design/Plan or implementation path remains unknown after integration.

- [ ] **Step 1: Write failing classification assertion** — Add the actual new implementation paths to the manifest audit expectation only after routing confirms each owner/classification. Do not project management-only assets without an approved consumer-runtime decision.
- [ ] **Step 1: Verify clean projection** — Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`; at B0 expect `unknown = 0` and `missing required = 0`. New paths stop for routing adjudication; Task 6 never edits the manifest.
- [ ] **Step 3: Minimal implementation** — Classify those paths; rerun Registry routing with the manifest. Do not change VERSION, release records, publish state, or create a release.
- [ ] **Step 4: Verify GREEN** — Run `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'`, `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, `git diff --check`, and `git status --short`. Record `Ran N tests`, `0 failures`, and `0 errors`.
- [ ] **Step 5: Commit** — `git add .gpt-codex/release/consumer-projection-manifest.json && git commit -m "chore: classify execution continuity assets"`

## Plan self-review

- Tasks 1–6 cover required fields, IDLE nullability, atomic reset/assignment, one-active-Work-Unit, blocked remediation, revision semantics, mismatch/cold recovery, reviewer seriality, P0-6 non-authority, and projection closure.
- Dependencies are ordered: contract, validator, assignment/reset, remediation, recovery/reviewer behavior, then projection closure.
- Every referenced production path has a Registry owner; every behavior test uses the owned validator test asset.
- The Plan contains no unfinished markers, generic validation instructions, or omitted file paths.

## Plan-stage projection deviation

Do not edit the projection manifest in this Plan stage. The sole permitted stage-local debts are `docs/superpowers/specs/2026-09-13-framework-design-continuity-sufficiency-design.md` and `docs/superpowers/plans/2026-09-14-framework-design-continuity-sufficiency.md`.

`PROJECTION_STAGE_DEVIATION = DEFERRED_NONBLOCKING` until Task 6 closes integration.

## Executable field, test, and projection matrix

`instruction_id`, `review_request_id`, `review_result_ref`, `finding_ref`, `remediation_authorization_ref`, and `fix_instruction_id` are `string|null` current-assignment correlations. `instruction_id` is populated by `IDLE → ACTIVE`; review request/result references by review entry/result; finding, authorization, and fix fields by remediation flow. They are all cleared by `COMPLETED → IDLE`; durable Result/Evidence remains external history. `BLOCKED` with remediation requires non-null `finding_ref`, `review_result_ref`, `blocked_from_status="REVIEWING"`, `block_reason="AWAITING_REMEDIATION_AUTHORIZATION"`; `BLOCKED → ACTIVE` requires non-null authorization and fix instruction references.

| Status | base_sha | current_head_sha | last_accepted_sha |
| --- | --- | --- | --- |
| IDLE | forbidden/null | forbidden/null | forbidden/null |
| ACTIVE | required | required | nullable until acceptance |
| BLOCKED | required | required | nullable unless accepted milestone exists |
| AWAITING_REVIEW | required | required | required |
| REVIEWING | required | required | required exact reviewed revision |
| COMPLETED | required | required | required before reset |

Recovery checks each SHA against Git facts; branch is never a SHA substitute. Task 5 RED coverage must separately assert `EXECUTION_SLOT_MISMATCH` or `RECONCILIATION_REQUIRED` for project context, Work Unit, role, primary module, branch, worktree, base/current/accepted SHA, and STATE revision mismatches; missing durable facts, dirty/ambiguous worktree, stale Resume, missing Map with sufficient authoritative facts, and physical-window replacement. Task 6 RED coverage must assert: same reviewer continuation allowed; second reviewer without evidence rejected; evidence-bound reassignment allowed; multiple windows do not allocate reviewers; Reviewer Result/finding and telemetry cannot reassign.

At Task 6, the manifest remains `MANAGEMENT_ONLY`; listed runtime paths remain `CONSUMER_REQUIRED`; validator/test assets remain `MANAGEMENT_ONLY`. The only new classifications are the Design and Plan as `DEVELOPMENT_HISTORY`. Final evidence records the numeric unittest output (`Ran <integer> tests`, `failures = 0`, `errors = 0`), `projection unknown = 0`, `projection missing required = 0`, and a clean worktree.
