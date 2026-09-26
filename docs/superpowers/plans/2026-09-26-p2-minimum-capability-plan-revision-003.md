# P2 Minimum Capability Revision 003 Implementation Plan Amendment

> **For agentic workers:** This is an append-only amendment candidate to Revision 002. Use the accepted Design and Revision 002 together with this amendment after independent review and acceptance. Implementation remains separately governed.

**Status:** CANDIDATE_FOR_INDEPENDENT_REVIEW  
**Implementation authorized:** NO

**Base Plan:** `7ac219d15269bdc68d66f07cfe85b044fef35279:docs/superpowers/plans/2026-09-26-p2-minimum-capability-plan-revision-002.md`  
**Accepted Design:** `91b485c6c93584ef2f89c459c10e488750f5801f:docs/superpowers/specs/2026-09-26-p2-minimum-capability-design-revision-002.md`  
**Review Finding target:** `edbc92d7834874c34fe70a6cacc7ab74091a19e7`

## Purpose and precedence

Revision 002 Task 1 treats `build_project_handoff(...)` as a general P2 resume/handoff basis. The current function requires `active_execution_slots`, and its slot recovery requires `slot.work_unit_id == STATE.active_work_unit`. Framework-management STATE revision 17 has `active_work_unit = framework-staged-closure-group-a-001` and no `active_execution_slots`. Revision 002 therefore has not demonstrated P2 resume/handoff for this legitimate slotless STATE.

This amendment changes only the Resume/Handoff technical plan. Where Revision 002 Tasks 1–7 assume slot-only Result or handoff discovery, the provisions below control. All other Revision 002 boundaries remain in force, including the four capabilities, Change Notification, Evidence Feedback Routing, Core-owned validation, Plugin packaging, E2E acceptance, and separate implementation authority. This amendment does not alter the accepted Design.

## Two distinct recovery levels

**Repository-level resume/handoff** is available to every enrolled Project through repository-native continuity. It does not assert execution-slot authority. `load_continuity_resume(...)`, called without `execution_slot_id`, is the baseline resume entry. Its returned STATE, continuity, Project Map, checkpoint, and next-action information remain derived information. A synced status alone does not authorize execution or prove a current Result handoff. Required remote re-verification and exact authority checks still apply.

**Execution-slot-aware resume/handoff** is conditional enrichment. Use `build_project_handoff(...)` only when current STATE contains complete, valid execution-slot authority; the selected non-idle slot is unique; the slot matches project context, current STATE revision, `STATE.active_work_unit`, Work Unit and lifecycle records; and its Git and continuity checks pass. An explicit slot ID must identify that unique valid slot. If slot data is present but malformed, ambiguous, stale, or conflicting, return `RECONCILIATION_REQUIRED`; do not reinterpret it as a slotless Project. A legitimate STATE with no execution slots uses the repository-level compatibility path.

Neither path may invent or add slots, overwrite `STATE.active_work_unit`, change the STATE schema, or declare that a slotless Project has slot authority.

## Repository-level durable handoff compatibility path

Implement the minimum compatibility path within the existing `.gpt-codex/scripts/continuity_resume.py` responsibility. It composes the repository baseline resume, existing immutable artifact resolution, Work Unit/Instruction/Result validation, Evidence references, and Git facts. The Plugin adapter receives its derived result; it must not replicate STATE parsing or Result discovery.

Plan a repository-native helper with an explicit interface equivalent to:

`build_repository_handoff(root, selected_repository_id, target_work_unit_id, instruction_locator, expected_state_revision, observed_remote_head_sha=None) -> dict[str, Any]`

The helper may use existing validators and smaller private helpers in `continuity_resume.py`. Its exact implementation signature may be narrowed during authorized implementation, but these inputs and checks must remain explicit. It must not infer the target P2 Work Unit from the legacy `STATE.active_work_unit` value. The target comes from the exact governed Instruction and immutable Work Unit reference, then is independently checked against current Work Unit and STATE-revision authority. `STATE.active_work_unit` remains an observed STATE fact; it is not silently replaced or reinterpreted.

A baseline resume may exist before a durable Instruction or Result exists. A **Result handoff** is ready only after one unique durable continuation is established. Absence of a uniquely provable continuation returns `RECONCILIATION_REQUIRED`, not a fabricated pending Result, success, or executable next action.

Before returning `HANDOFF_READY`, verify all of the following from durable repository facts:

1. Project ID and project context ID agree across CONTROL, Work Unit, Instruction, Result, and the selected repository context.
2. Repository ID and full repository name agree with CONTROL and observed Git repository identity.
3. Current STATE revision is the exact expected revision; stale, missing, or conflicting revisions reconcile.
4. The exact target Work Unit ID and immutable Work Unit reference resolve and agree with the Instruction and Result. A historical Result for another Work Unit is never selected merely because STATE continuity names it.
5. Accepted Design and Plan refs resolve as exact commit/path/blob artifacts. Apply the ultimately accepted Plan revision reference when the future implementation Work Unit is frozen; do not silently substitute Revision 002 for Revision 003.
6. The Instruction ID and immutable Instruction locator resolve to the expected bytes and bind the target Work Unit, project/context, repository, role, scope, and current STATE revision under existing authority.
7. Exactly one Result ID and Result locator correspond to that Instruction and Work Unit. Discover candidates only through the existing project-owned Result/Evidence surface; reject duplicate IDs, duplicate matching continuations, missing objects, and conflicting locators.
8. Result `work_unit_id` and `state_revision` equal the exact target and expected current revision.
9. Result `response_to_instruction_id` equals the resolved Instruction ID. Where the existing Result contract expresses the response binding through another validated field, use that contract without weakening the equality check.
10. Result Evidence refs are present, permitted, and resolvable in the authoritative repository context.
11. The authoritative Git SHA is exact, object-resolvable, and consistent with current repository/continuity facts and the Result's Git binding. A branch name, unverified local HEAD, or presentation hint is insufficient. Existing permitted attestation rules may establish a verified later head; otherwise SHA disagreement reconciles.

Any missing, ambiguous, stale, foreign, or conflicting required fact returns `RECONCILIATION_REQUIRED` with a bounded reason. No private GPT/Codex conversation, prompt, scratchpad, transcript, hidden reasoning, raw log, or Reviewer-private context enters either handoff response. `NEXT_GPT_ACTION` and `next_action_hint` remain presentation hints; execution requires independent current authority validation.

## Task 1 amendment: native recovery and thin entry adapter

**Files:**
- Modify: `.gpt-codex/scripts/continuity_resume.py`
- Add focused tests: `.gpt-codex/tests/test_continuity_resume.py`
- Create as in Revision 002: `.gpt-codex/scripts/framework_plugin_entry.py`
- Create as in Revision 002: `.gpt-codex/tests/test_framework_plugin.py`

Revision 002's `continuity_resume.py` read-only/Test-dependency classification is replaced by **minimum necessary Modify** scope. The focused test file may grow. No STATE/CONTROL or schema change is authorized by this plan.

1. Write focused RED tests for slotless/legacy repository baseline resume; repository-level handoff with an exact target Work Unit distinct from a legacy `STATE.active_work_unit`; existing valid slot-aware handoff; and the distinction between the two results.
2. Add RED failure tests for wrong project/context or repository, stale STATE revision, Instruction locator/ID mismatch, duplicate Result, Result Work Unit mismatch, Result-to-Instruction correlation mismatch, Git SHA mismatch, missing or ambiguous durable continuation, malformed or ambiguous slot authority, and private-context exclusion.
3. Implement the smallest native compatibility path in `continuity_resume.py`. Preserve existing `load_continuity_resume(...)` baseline behavior and valid `build_project_handoff(...)` slot-aware behavior. Do not make the Plugin adapter responsible for recovery rules.
4. Make `build_plugin_resume(root, selected_repository_id, execution_slot_id=None)` call repository baseline resume first. Use slot-aware enrichment only when the complete unique slot conditions above hold. For legitimate slotless STATE, expose only verified repository-level facts; use the native repository handoff helper when an exact Instruction/Result continuation is requested and available. Any conflict returns reconciliation.
5. Run focused continuity, Plugin, and Result tests. Review the response shape to confirm no field asserts slot authority on the slotless path and no `next_authorized_action` is produced.

## Task 2 amendment: Instruction resolution

Keep Revision 002's deterministic Instruction artifact preparation, existing Evidence-surface location, immutable commit/path/blob locator, and authority validation.

Add tests and adapter checks that the resolved Instruction supplies the **exact** target Work Unit, Instruction ID, project/context, repository, and expected STATE revision used by repository-level handoff. A slotless STATE does not require a slot locator. Where valid slot authority exists, its existing constraints still apply. An Instruction visibility or publication event is not authorization or proof of Result continuation. On mismatch, return reconciliation before any Result discovery is treated as usable.

## Task 3 amendment: Codex-to-GPT Result/Evidence handoff

Replace the Revision 002 dependency on `build_project_handoff` alone with the two-path native recovery model:

- For complete, unique, valid matching slot authority, use existing slot-aware handoff.
- For legitimate slotless STATE, use repository-level durable handoff from `continuity_resume.py`.
- For malformed or conflicting slot authority, reconcile; never fall back silently.

`build_plugin_result_handoff(...)` remains a thin presentation adapter over the selected native result. Its Result ID/ref, STATE revision, exact Git SHA, Evidence refs, blockers, and hint must come from the validated native handoff. The adapter neither scans Result files independently nor creates a Result store or completion state.

Test both valid paths and all Task 1 handoff failures. In particular, an unrelated `continuity.last_verified_result_ref` must not be presented as the target Work Unit's Result. Result `PASS` remains distinct from Work Unit `COMPLETE`.

## Task 4 amendment: capability requests and validation

Keep the exact four fixed capability names and existing Core-owned validators. Request validation consumes the repository-level baseline and, where relevant, the validated native handoff. Do not require slot authority for a legitimate slotless Project. Do require exact current Work Unit, Instruction, role/action, STATE revision, Guardrail, repository, and Git bindings before an executable request reaches Core. If slot authority is present, apply its complete existing checks as additional constraints. A resume or handoff status never grants permission.

## Task 5 amendment: feedback and Change Notification

Keep P1 Evidence Feedback Routing and the transport-neutral marker comparator. Derive marker facts from verified repository-level resume/handoff for slotless Projects and from verified slot-aware enrichment when applicable. A marker change means only `DURABLE_AUTHORITY_MAY_HAVE_CHANGED`; it triggers fresh native resume and validation. Do not turn marker differences, polling, or notifications into Result discovery authority. Feedback remains bound to the exact Project, Work Unit, Instruction/Result where applicable, revision, and provenance.

## Task 6 amendment: Plugin package

Keep the skills-only portable package and Revision 002 packaging boundaries. The Plugin skill must instruct a fresh context to perform repository-level baseline resume for every enrolled Project, then use conditional slot-aware enrichment or the native slotless compatibility handoff. It must describe the distinction plainly and must not claim slot authority for a slotless Project. Package tests must reject Plugin-owned STATE parsing, Result scanning, recovery rules, new stores, queue, registry, daemon, or MCP service. No committed marketplace or release/publication change is introduced.

## Task 7 amendment: validation and E2E acceptance

Retain Revision 002's full source validation, local installation, independent review, P1 effectiveness evidence, and acceptance boundary. Extend the fresh-session scenario to exercise both:

1. A legitimate slotless/legacy enrolled Project: baseline repository resume, exact durable Instruction resolution, governed execution, native repository-level unique Result/Evidence/Git handoff, and fresh GPT recovery without transcript copying. The scenario must not create a slot or modify `STATE.active_work_unit`.
2. A Project with complete valid slot authority: baseline resume followed by slot-aware enrichment and existing handoff, with no regression.

Repeat failure acceptance cases for exact Work Unit target mismatch, Instruction mismatch, STATE revision mismatch, duplicate Result, Result Work Unit mismatch, Result response correlation mismatch, Git SHA mismatch, and no unique durable continuation. Confirm each produces reconciliation and no executable context. Inspect both returned views for private-context leakage. Plugin-unavailable repository-native operation remains viable.

## Scope and unchanged boundaries

This amendment plans no production or test mutation now. A later separately authorized implementation may make only the minimum `continuity_resume.py` change and focused tests necessary for the dual-path model, plus the already planned thin adapter and related Task 2–7 changes within an appropriately amended Work Unit scope.

It does not authorize invented execution slots, automatic slot addition, changes to `STATE.active_work_unit`, STATE schema or CONTROL mutation, a second STATE, a new Result store, session registry, message queue, Plugin-owned Core recovery, Plugin release, Framework release, Work Unit creation, bootstrap creation, or implementation start.

The Work Unit Authority Design candidate at the Review Finding target remains blocked until this Plan amendment is independently reviewed and adjudicated. Its currently stated path scope does not itself authorize modifying `continuity_resume.py`; future implementation authority must account for the accepted amendment through the normal governance path.

## Definition of Done for this amendment

Independent Plan review can accept Revision 003 only if it confirms: repository baseline resume is universal for enrolled Projects; slot-aware handoff is conditional; slotless handoff is implemented in the existing continuity responsibility; all listed durable facts and failure tests are covered; Task 2–7 assumptions align with the two paths; the Plugin remains thin; and accepted Design semantics and all other Revision 002 boundaries remain unchanged.

Plan acceptance does not authorize implementation.
