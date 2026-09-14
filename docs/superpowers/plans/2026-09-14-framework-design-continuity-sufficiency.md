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

**Interfaces:** Add `block_for_remediation(state, slot_id, finding_ref, review_ref, expected_revision) -> dict` and:

```python
resume_authorized_remediation(
    state,
    slot_id,
    authorization_ref,
    fix_instruction,
    expected_revision,
    *,
    authoritative_facts,
) -> dict
```

The first writes `REVIEWING → BLOCKED`, predecessor `REVIEWING`, and `AWAITING_REMEDIATION_AUTHORIZATION`; the second returns `ACTIVE` only after current-fact reconciliation and a valid FIX instruction. `authoritative_facts` is a read-only transport mapping, not a new authority store or subsystem: it carries the already-loaded authoritative `work_unit`, `review_request`, `review_result`, `finding`, `remediation_authorization`, and `current_git` facts into this deterministic lifecycle function. `state` is the current authoritative STATE snapshot; the function returns a new state value and does not persist STATE.

**Authority and reconciliation contract:** A field stored in `ACTIVE_EXECUTION_SLOTS` is a current correlation/handoff fact; it never replaces the underlying authority source. Before `BLOCKED → ACTIVE`, Task 4 validates every slot correlation against its authoritative record. No slot correlation is a duplicate authority store.

| Causal fact | Authoritative source | Slot/current correlation | Required comparison | API resolution |
| --- | --- | --- | --- | --- |
| `work_unit_id` | authoritative Work Unit | slot `work_unit_id` | exact identity of the current Work Unit still bound to this slot/assignment | `authoritative_facts["work_unit"]` |
| `finding_ref` | durable Review Finding Result/Evidence | slot `finding_ref` | exact current finding reference | `authoritative_facts["finding"]` |
| `review_request_id` | governed Review Request / Instruction correlation | slot `review_request_id` | exact current review request for the reviewed milestone | `authoritative_facts["review_request"]` |
| `review_result_ref` | durable Review Result/Evidence | slot `review_result_ref` | exact current review result reference | `authoritative_facts["review_result"]` |
| `remediation_authorization_ref` | explicit GPT/User remediation authorization under the existing role protocol | slot `remediation_authorization_ref` | exact current authorization reference | `authoritative_facts["remediation_authorization"]`, which must match `authorization_ref` |
| `fix_instruction_id` | authoritative `FIX_INSTRUCTION` | slot `fix_instruction_id` | exact instruction identity plus `validate_instruction_authority(...)` success | `fix_instruction` argument |
| reviewed SHA | Review Result/Finding revision evidence | retained review/slot correlation where present | exact reviewed revision required by the current review chain | `authoritative_facts["review_result"]` / `authoritative_facts["finding"]` |
| current SHA | Git HEAD/ref/ancestry evidence at reconciliation | slot `current_head_sha` | exact current Git fact and required reviewed/current relation | `authoritative_facts["current_git"]` |
| `state_revision` | current authoritative `STATE.revision` | slot `state_revision` | `slot.state_revision == state.revision == expected_revision` | `state` plus `expected_revision` |

For every row, missing or contradictory required facts return `RECONCILIATION_REQUIRED`. A slot `work_unit_id` must match the supplied Work Unit and must not be inferred from chat, window, or branch names. A Review Result cannot repair a missing/mismatched Review Request. Reviewed SHA is taken from current Review Result/Finding evidence, never from a branch name, current HEAD alone, Resume, telemetry, or conversation memory. Current SHA is taken from reconciliation-time Git HEAD/ref/ancestry evidence; the slot's `current_head_sha` cannot override contradictory Git evidence, and Task 4 creates no second Git authority field. Reviewer prose, telemetry, Resume, Project Map, chat history, physical window state, or conversation memory are not substitutes for durable Result/Evidence, authorization, or Git facts. Finding/Review evidence is not remediation mutation authority; an identity-matching but invalid `FIX_INSTRUCTION`, or an authority-valid instruction with the wrong ID, likewise fails closed.

The authoritative source hierarchy is:

```text
STATE / ACTIVE_EXECUTION_SLOTS = authoritative current lifecycle record
Work Unit = authoritative governed assignment/scope fact
Instruction / explicit GPT/User authorization = authoritative execution/remediation authorization facts
Result/Evidence = authoritative review/finding evidence
Git = authoritative repository revision/ancestry evidence
slot correlation fields = durable current-assignment correlations only
Map / Resume = derived hints only
Telemetry = observation only
Physical window/chat = non-authoritative
```

`resume_authorized_remediation()` performs no hidden repository reads: it does not open repository files, query Git remote/network, search Evidence directories, discover Work Units, parse chat, or read telemetry. Existing orchestration/validation loads authoritative facts and retains persistence ownership; navigation-continuity consumes them for lifecycle reconciliation only.

- [ ] **Step 1: Write failing tests**

```python
def test_finding_blocks_but_does_not_authorize_mutation(self):
    slot = block_for_remediation(self.reviewing_state(), "S-1", "finding-1", "review-1", 7)["active_execution_slots"][0]
    self.assertEqual(slot["block_reason"], "AWAITING_REMEDIATION_AUTHORIZATION")

def test_reviewer_message_cannot_resume_blocked_slot(self):
    with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
        resume_authorized_remediation(
            self.blocked_state(), "S-1", None, None, 8,
            authoritative_facts=self.complete_authoritative_facts(),
        )

def test_remediation_resume_rejects_each_causal_mismatch(self):
    cases = (
        ("finding_ref mismatch", "finding_ref"),
        ("review_request_id mismatch", "review_request_id"),
        ("review_result_ref mismatch", "review_result_ref"),
        ("remediation_authorization_ref mismatch", "remediation_authorization_ref"),
        ("fix_instruction_id mismatch", "fix_instruction_id"),
        ("work_unit_id mismatch", "work_unit_id"),
        ("reviewed/current SHA mismatch", "reviewed_current_sha"),
        ("authoritative STATE revision mismatch", "state_revision"),
    )
    for label, mismatch in cases:
        with self.subTest(mismatch=label):
            # The fixture retains a valid causal chain except for this one fact.
            with self.assertRaisesRegex(ValueError, "^RECONCILIATION_REQUIRED$"):
                resume_authorized_remediation(
                    self.blocked_state(remediation_mismatch=mismatch),
                    "S-1",
                    "authorization-1",
                    self.valid_fix_instruction(),
                    8,
                    authoritative_facts=self.complete_authoritative_facts(),
                )

def test_authoritative_fact_bundle_cannot_disagree_with_complete_slot(self):
    with self.assertRaisesRegex(ValueError, "^RECONCILIATION_REQUIRED$"):
        resume_authorized_remediation(
            self.complete_blocked_state(),
            "S-1",
            "authorization-1",
            self.valid_fix_instruction("fix-instruction-1"),
            8,
            authoritative_facts=self.complete_authoritative_facts(
                finding=self.finding("finding-2"),  # contradictory durable source
            ),
        )

def test_incomplete_remediation_authority_cannot_resume(self):
    cases = (
        ("finding only", "finding_only"),
        ("Review Result only", "review_result_only"),
        ("remediation authorization only", "authorization_only"),
        ("FIX_INSTRUCTION only", "fix_instruction_only"),
        ("Reviewer message only", "reviewer_message_only"),
    )
    for label, authority_subset in cases:
        with self.subTest(authority_subset=label):
            # Each fixture retains only this named authority/evidence subset;
            # none supplies the complete current remediation causal chain.
            with self.assertRaisesRegex(ValueError, "^RECONCILIATION_REQUIRED$"):
                resume_authorized_remediation(
                    self.blocked_state(authority_subset=authority_subset),
                    "S-1",
                    self.authorization_for_subset(authority_subset),
                    self.fix_instruction_for_subset(authority_subset),
                    8,
                    authoritative_facts=self.authoritative_facts_for_subset(authority_subset),
                )

def test_complete_current_remediation_chain_resumes_blocked_slot(self):
    resumed = resume_authorized_remediation(
        self.blocked_state(
            work_unit_id="WU-1",
            finding_ref="finding-1",
            review_request_id="review-request-1",
            review_result_ref="review-result-1",
            remediation_authorization_ref="authorization-1",
            fix_instruction_id="fix-instruction-1",
            reviewed_current_sha="head-abc123",
            state_revision=8,
        ),
        "S-1",
        "authorization-1",
        self.valid_fix_instruction("fix-instruction-1"),
        8,
        authoritative_facts={
            "work_unit": self.work_unit("WU-1"),
            "review_request": self.review_request("review-request-1"),
            "review_result": self.review_result("review-result-1", reviewed_sha="head-abc123"),
            "finding": self.finding("finding-1", reviewed_sha="head-abc123"),
            "remediation_authorization": self.remediation_authorization("authorization-1"),
            "current_git": self.git_facts(head_sha="head-abc123"),
        },
    )
    self.assertEqual(resumed["active_execution_slots"][0]["status"], "ACTIVE")
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect missing causal APIs.
- [ ] **Step 3: Minimal implementation** — Use existing `validate_instruction_authority()` for `FIX_INSTRUCTION`. A finding/Reviewer message is never authority. Mismatched finding, review, authorization, Work Unit, SHA, or STATE revision fails closed.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect only explicit GPT/User authorization plus valid instruction resumes.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: govern slot remediation recovery"`

### Task 5: Add cold recovery, mismatch, and reviewer seriality

**Files:** Modify `.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/project_navigation.py`, and `.gpt-codex/tests/test_navigation_project_validation.py`.

**Interfaces:** Extend `load_continuity_resume(..., execution_slot_id: str|None=None) -> dict`; binding mismatch returns `status="EXECUTION_SLOT_MISMATCH"` and `reconciliation_required=True`. Add `validate_reviewer_assignment(slot, reviewer_ref, expected_revision) -> list[str]`.

**Mismatch and reconciliation contract:** A known actor/surface-to-durable-slot binding contradiction returns exactly `EXECUTION_SLOT_MISMATCH` with `reconciliation_required=True`; it permits no continuation, reassignment, STATE overwrite, or Git mutation. With no such binding contradiction, insufficient authoritative facts for exactly one safe continuation return exactly `RECONCILIATION_REQUIRED`, with the same no-mutation guarantees. A bound worktree identity mismatch is the former; a dirty or ambiguous current worktree is the latter. Binding disagreement for `base_sha`, `current_head_sha`, or `last_accepted_sha` is the former, while unavailable/contradictory Git ancestry or ref evidence without an actor binding claim is the latter. Branch names never substitute for SHA facts. A bound `state_revision` that disagrees with current authoritative `STATE.revision` is the former; inability to establish current authoritative STATE/current assignment is the latter. No second slot-local revision sequence exists.

**Failure precedence:**

```text
known actor-to-durable-slot binding contradiction
→ EXECUTION_SLOT_MISMATCH

no binding contradiction, but authoritative facts are insufficient for exactly one safe continuation
→ RECONCILIATION_REQUIRED

valid authoritative facts and only derived navigation/cache differences
→ do not fail merely because of Map / Resume / window (completed in C2)
```

**Authoritative cold recovery:** Project Map is a derived navigation aid, Resume is a derived continuity cache, and a physical window is not a logical execution slot. If CONTROL/repository binding, current authoritative STATE/revision, the matching `ACTIVE_EXECUTION_SLOTS` record, bound Work Unit, lifecycle-required Instruction/Result/Evidence correlations, stage-required Git branch/ref/HEAD/ancestry facts, and slot `next_action`/blocker facts are complete, current, mutually consistent, and yield exactly one safe continuation, recovery succeeds even when Project Map or Resume is missing/stale or the physical window is replaced. The recovery result is the already-authoritatively encoded safe continuation (for this RED fixture, `next_action="AWAIT_REVIEW"`), not a new generic lifecycle state.

When Map/Resume disagrees with that sufficient authority set, authoritative facts win and the derived artifact may be ignored or marked stale diagnostically. It must not cause a false slot mismatch, overwrite STATE/Git facts, change the Work Unit, or independently authorize continuation, reassignment, review, or remediation. Stale Resume is not an actor-to-slot binding contradiction. Likewise, a replacement window correctly bound to the durable existing `slot_id` is not a new slot claimant: it creates no slot, reassignment, Work Unit change, lifecycle change, or reconciliation requirement. Only an actual asserted conflicting slot binding produces `EXECUTION_SLOT_MISMATCH`.

Cold recovery never reconstructs authority from lost chat, physical-window identity, telemetry, or model memory. If durable authoritative facts cannot determine exactly one safe continuation, it returns `RECONCILIATION_REQUIRED`.

**Reviewer seriality:** Physical review window is not reviewer authority; multiple physical windows bound to the same logical reviewer neither create another reviewer nor require reassignment. Review Result/finding and telemetry are not reassignment authority. Only explicit, current, evidence-bound reassignment changes reviewer; timeout, inactivity, model/window change, and observation never reassign automatically.

- [ ] **Step 1: Write failing tests**

```python
def test_execution_slot_binding_mismatch_matrix(self):
    for field in (
        "project_context_id",
        "work_unit_id",
        "role",
        "primary_module",
        "branch",
        "worktree",
        "base_sha",
        "current_head_sha",
        "last_accepted_sha",
        "state_revision",
    ):
        with self.subTest(field=field):
            result = load_continuity_resume(
                self.slot_fixture(binding_mismatch=field),
                "repo-a",
                execution_slot_id="S-1",
            )
            self.assertEqual(result["status"], "EXECUTION_SLOT_MISMATCH")
            self.assertTrue(result["reconciliation_required"])

def test_unresolved_authoritative_repository_or_state_facts_require_reconciliation(self):
    for condition in (
        "missing_durable_fact",
        "dirty_worktree",
        "ambiguous_worktree",
        "unprovable_git_state",
        "authoritative_state_unavailable",
    ):
        with self.subTest(condition=condition):
            result = load_continuity_resume(
                self.slot_fixture(condition=condition),
                "repo-a",
                execution_slot_id="S-1",
            )
            self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
            self.assertTrue(result["reconciliation_required"])

def test_derived_continuity_artifacts_do_not_block_authoritative_recovery(self):
    for derived_condition in (
        "missing_project_map",
        "missing_resume",
        "stale_resume",
        "replacement_window",
    ):
        with self.subTest(derived_condition=derived_condition):
            result = load_continuity_resume(
                self.authoritative_recovery_fixture(
                    derived_condition=derived_condition,
                    slot_id="S-1",
                    next_action="AWAIT_REVIEW",
                ),
                "repo-a",
                execution_slot_id="S-1",
            )
            self.assertFalse(result["reconciliation_required"])
            self.assertNotIn(
                result.get("status"),
                ("EXECUTION_SLOT_MISMATCH", "RECONCILIATION_REQUIRED"),
            )
            self.assertEqual(result["next_action"], "AWAIT_REVIEW")

def test_missing_authoritative_fact_still_blocks_derived_recovery(self):
    result = load_continuity_resume(
        self.authoritative_recovery_fixture(
            derived_condition="stale_resume",
            missing_authoritative_fact="work_unit",
        ),
        "repo-a",
        execution_slot_id="S-1",
    )
    self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
    self.assertTrue(result["reconciliation_required"])

def test_second_reviewer_requires_explicit_reassignment(self):
    self.assertIn("RECONCILIATION_REQUIRED", validate_reviewer_assignment(self.reviewing_slot(), "reviewer-2", 9))

def test_reviewer_seriality_and_reassignment_evidence(self):
    self.assertEqual(validate_reviewer_assignment(self.reviewing_slot(), "reviewer-1", 9), [])
    self.assertEqual(validate_reviewer_assignment(self.reviewing_slot(reviewer_reassignment_ref="instruction-1"), "reviewer-2", 9), [])

def test_multiple_physical_review_windows_preserve_one_logical_reviewer(self):
    slot = self.reviewing_slot(
        reviewer_ref="reviewer-1",
        physical_review_windows=("window-a", "window-b"),
    )
    self.assertEqual(validate_reviewer_assignment(slot, "reviewer-1", 9), [])
    self.assertEqual(slot["reviewer_ref"], "reviewer-1")

def test_derived_reviewer_observations_cannot_reassign(self):
    for source in ("review_result_finding", "telemetry"):
        with self.subTest(source=source):
            errors = validate_reviewer_assignment(
                self.reviewing_slot(reviewer_reassignment_source=source),
                "reviewer-2",
                9,
            )
            self.assertIn("RECONCILIATION_REQUIRED", errors)
```

- [ ] **Step 2: Verify RED** — Run `python .gpt-codex/tests/test_navigation_project_validation.py`; expect keyword/helper absent.
- [ ] **Step 3: Minimal implementation** — Bind CONTROL, STATE slots, Work Unit, instruction/Result/Evidence, and Git facts before action. The Step 1 matrices distinguish every named actor/slot binding mismatch from missing durable facts, dirty/ambiguous worktree, unprovable Git state, and unavailable authoritative STATE/current assignment. Map/Resume only supply hints; when sufficient authoritative facts yield one safe continuation, missing/stale derived aids or a replacement physical window do not block it. Keep one reviewer; only evidence-bound reassignment is allowed; Reviewer Result/finding and telemetry never reassign.
- [ ] **Step 4: Verify GREEN** — Run the same test file; expect mismatch/cold recovery/seriality results to pass and derived navigation to remain non-authoritative.
- [ ] **Step 5: Commit** — `git add .gpt-codex/scripts/continuity_resume.py .gpt-codex/scripts/project_navigation.py .gpt-codex/tests/test_navigation_project_validation.py && git commit -m "feat: recover and review execution slots"`

### Task 6: Final cross-module verification only

**Files:** `MUTATION = NONE`. Verify only `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_release_packaging.py`, and `.gpt-codex/tests/test_publication_authority.py` in `MODE = VERIFY_ONLY_REGRESSION`; no Task 6 commit.

**Interfaces:** Verify that the established projection contract has `unknown = 0` and `missing required = 0`; any unexpected physical path stops for separate routing adjudication.

- [ ] **Step 1: Run projection verification** — `python .gpt-codex/scripts/validate_consumer_projection.py --root .`; do not edit the manifest.
- [ ] **Step 2: Run verify-only regressions** — Run the four named consumer/release test files and the final framework/project/full-suite commands.
- [ ] **Step 3: Stop without mutation** — Task 6 creates no path, edits no manifest, and creates no commit.

## Plan self-review

- Tasks 1–6 cover required fields, IDLE nullability, atomic reset/assignment, one-active-Work-Unit, blocked remediation, revision semantics, mismatch/cold recovery, reviewer seriality, P0-6 non-authority, and projection closure.
- Dependencies are ordered: contract, validator, assignment/reset, remediation, recovery/reviewer behavior, then final verification of pre-integrated projection state.
- Every referenced production path has a Registry owner; every behavior test uses the owned validator test asset.
- The Plan contains no unfinished markers, generic validation instructions, or omitted file paths.

## Plan-stage projection deviation

Do not edit the projection manifest in this Plan stage. The sole permitted stage-local debts are `docs/superpowers/specs/2026-09-13-framework-design-continuity-sufficiency-design.md` and `docs/superpowers/plans/2026-09-14-framework-design-continuity-sufficiency.md`.

`PROJECTION_STAGE_DEVIATION = DEFERRED_NONBLOCKING` until a separately authorized integration step closes it; Task 6 verifies only.

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

Recovery checks each SHA against Git facts; branch is never a SHA substitute. Task 5 RED coverage must separately assert `EXECUTION_SLOT_MISMATCH` or `RECONCILIATION_REQUIRED` for project context, Work Unit, role, primary module, branch, worktree, base/current/accepted SHA, and STATE revision mismatches; missing durable facts, dirty/ambiguous worktree, stale Resume, missing Map with sufficient authoritative facts, and physical-window replacement. Task 5 RED coverage must assert: same reviewer continuation allowed; second reviewer without evidence rejected; evidence-bound reassignment allowed; multiple windows do not allocate reviewers; Reviewer Result/finding and telemetry cannot reassign.

At Task 6, the manifest remains `MANAGEMENT_ONLY`; listed runtime paths remain `CONSUMER_REQUIRED`; validator/test assets remain `MANAGEMENT_ONLY`. The only new classifications are the Design and Plan as `DEVELOPMENT_HISTORY`. Final evidence records the numeric unittest output (`Ran <integer> tests`, `failures = 0`, `errors = 0`), `projection unknown = 0`, `projection missing required = 0`, and a clean worktree.
