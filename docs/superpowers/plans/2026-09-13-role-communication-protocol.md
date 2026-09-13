# Role Communication Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved role-communication protocol design as one explicit framework contract for role identity, Instruction/Result Envelope ownership, authority boundaries, review lifecycle, stage routing, and verifiable Git synchronization.

**Architecture:** Extend existing envelopes, schemas, templates, validators, Git continuity, Handoff projection, documentation, and consumer metadata. Keep one conceptual Protocol Message Taxonomy, while exposing instruction-side classes only through `InstructionEnvelope.instruction_type` and result-side classes only through `ResultEnvelope.result_message_type`. Add one small pure shared vocabulary/validation module; do not add a message bus, message store, generic `message_type`, or a second authority system.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3 standard library, `unittest`, existing framework/project validators, Git continuity helpers, Markdown, and the consumer-projection manifest.

**Spec:** `docs/superpowers/specs/2026-09-13-role-communication-protocol-design.md` at reviewed revision `e005ccf97d4cb0b32a9c9f5176430e677ff0fafd`.

## Global Constraints

- Preserve Kernel `2.0.0`, schema-generation `1`, `CONTROL.json`, `STATE.json`, Result Envelope authority, publication contract, and current validator gates.
- Keep roles explicit: `GPT_ORCHESTRATOR`, `CODEX_IMPLEMENTER`, `CODEX_REVIEWER`, `GPT_REVIEWER`, `GPT_USER`, `PLAN_TASK`, and `FRESH_REVIEWER`. `PLAN_TASK` is not an executor, `CODEX_IMPLEMENTER`, or `FRESH_REVIEWER`.
- One Work Unit has one persistent `CODEX_IMPLEMENTER`; related implementation tasks run serially or in bounded batches. `CODEX_REVIEWER` reviews only at explicit milestone/risk gates and re-reviews unless escalation is recorded.
- `instruction_type` accepts only `EXECUTION_INSTRUCTION`, `REVIEW_REQUEST`, `FIX_INSTRUCTION`, `APPROVAL_REQUEST`, `RECONCILIATION_REQUEST`, `INFORMATION_ONLY`, `PROJECT_CONTEXT_BOOTSTRAP`, and explicitly registered legacy instruction aliases.
- `result_message_type` accepts result-side types including `REVIEW_RESULT`, `REVIEW_FINDING`, `IMPLEMENTATION_RESULT`, and registered protocol error/result classifications. Result-side values are rejected in `instruction_type`.
- No generic `message_type` exists. `instruction_type` belongs only to Instruction Envelope; `result_message_type` belongs only to Result Envelope.
- Preserve `REVIEW_FINDING → evidence returned to GPT/User → remediation decision → new FIX_INSTRUCTION → CODEX_IMPLEMENTER`; a finding never becomes executable.
- Every executable instruction has exactly one scalar executor. Missing, plural, compound, unknown, or ambiguous identity blocks execution; role actions are checked against allowed/forbidden sets; reviewers are non-mutating.
- DESIGN and PLAN require remote review visibility plus GPT review; IMPLEMENTATION makes remote visibility optional and uses `CODEX_REVIEWER` for technical review.
- After a DESIGN/PLAN SHA is exposed for formal review, it is immutable evidence. Fixes use new descendant commits and fast-forward synchronization by default. Amend, rebase, history-removing reset, force push, branch replacement, merge main, tag/release, and publish are forbidden by default.
- A review-visibility push is not production publication. Unverified or mismatched remote state yields `RECONCILIATION_REQUIRED`.
- This current Work Unit is plan-only; no production implementation, schema change, Kernel change, or schema-generation change is performed now.

## File Map

The future implementation is bounded to these paths. The current Work Unit creates only this plan and its `DEVELOPMENT_HISTORY` manifest entry.

| Area | Files |
|---|---|
| Shared taxonomy | `.gpt-codex/scripts/role_communication.py` (new); `.gpt-codex/tests/test_role_communication_taxonomy.py` (new) |
| Instruction contract | `.gpt-codex/schemas/instruction-envelope.schema.json`; `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`; `.gpt-codex/scripts/instruction_envelope.py`; existing instruction tests; `.gpt-codex/tests/test_instruction_role_contract.py` (new) |
| Result/Handoff contract | `.gpt-codex/schemas/result-envelope.schema.json`; `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`; `.gpt-codex/scripts/result_return.py`; Handoff skill/manifest; existing result/Handoff tests |
| Role/lifecycle gates | `.gpt-codex/scripts/validate_project.py`; `publication_contract.py` only if existing Result authority needs the fields; `.gpt-codex/tests/test_role_authority.py` and `test_review_lifecycle.py` (new) |
| Routing/history | `.gpt-codex/scripts/git_continuity.py` or bounded `review_history.py`; `test_stage_review_routing.py` and `test_review_history.py` (new) |
| Documentation | `AGENTS.md`; `.gpt-codex/README.md`; bootstrap prompt only if its authoritative text needs this protocol; `test_role_routing_docs.py` (new) |
| Consumer closure | `.gpt-codex/release/consumer-projection-manifest.json`; consumer projection/runtime closure tests |
| Candidate release | `VERSION`; `.gpt-codex/CHANGELOG.md`; `releases/records/v2.4.0.json`; generated output only through the existing release command |

## Execution Model and Review Gates

One persistent `CODEX_IMPLEMENTER` executes tasks in order. Tasks are independently testable and each has a local commit, but task completion is not a reviewer gate. No fresh subagent is created per task.

1. **Review Gate A — Integrated protocol contract and validation:** after Tasks 1–4, `CODEX_REVIEWER` checks taxonomy ownership, both envelopes, role/action gates, causal review behavior, and machine-authority compatibility. The same reviewer continues unless escalation is recorded.
2. **Review Gate B — Final integrated implementation before acceptance/release:** after Tasks 5–8, the same reviewer re-reviews the full implementation, tests, synchronization, consumer closure, and acceptance boundary.

`GPT_REVIEWER` remains formal reviewer for DESIGN/PLAN artifacts. A reviewer finding is evidence; GPT/User remediation must produce a new `FIX_INSTRUCTION` before implementation.

---

## Task 1: Add shared taxonomy and authority predicates

**Files:** Create `.gpt-codex/scripts/role_communication.py` and `.gpt-codex/tests/test_role_communication_taxonomy.py`; update `validate_framework.py` only if its required-file inventory needs the helper.

**Interfaces:** Define immutable `ROLES`, `INSTRUCTION_TYPES`, `RESULT_MESSAGE_TYPES`, `ACTIONS`, `ARTIFACT_STAGES`; `validate_executor_role(value: object) -> list[str]`; `validate_instruction_type(value: object) -> list[str]`; `validate_result_message_type(value: object) -> list[str]`; `allowed_actions_for_role(role: str) -> frozenset[str]`; and `validate_action_authority(role: str, authorized_actions: Sequence[str], forbidden_actions: Sequence[str]) -> list[str]`. Return stable ordered protocol error codes. Keep the module pure: no dispatch, storage, prose parsing, or second authority.

**Steps:**

- [ ] Write failing tests for all seven roles, every instruction/result type, disjointness, registered legacy aliases, and missing/plural/compound/unknown executor errors.
- [ ] Run `python -m unittest test_role_communication_taxonomy -v` from `.gpt-codex/tests`; confirm failure because the helper is absent.
- [ ] Implement constants and deterministic validators with no external dependency.
- [ ] Run the focused suite and `python .gpt-codex/scripts/validate_framework.py`; confirm pass and unchanged Kernel/schema-generation versions.
- [ ] Commit `feat: add role communication taxonomy predicates`.

## Task 2: Extend Instruction Envelope role, action, and causal fields

**Files:** Modify instruction schema/template/builder and existing instruction tests; create `.gpt-codex/tests/test_instruction_role_contract.py`.

**Interfaces:** Extend `build_instruction_envelope` with keyword-only `issuer_role`, `executor_role`, `return_role`, `authorized_actions`, `forbidden_actions`, `evidence_requirements`, `completion_gate`, `in_response_to_instruction_id`, `in_response_to_result_id`, `review_target_revision`, `finding_ids`, `fix_round`, and `artifact_stage`, each typed as specified by the existing Python conventions. Omit absent optional fields rather than emitting null. Validate `instruction_type` only against instruction taxonomy; require one scalar executor; validate actions and bounded provenance; map legacy aliases deterministically to `[CODEX]` and one `CODEX_IMPLEMENTER`.

**Steps:**

- [ ] Add failing schema/builder/renderer/template tests for valid role-bearing instructions, invalid executor shapes, result-side instruction types, unauthorized actions, provenance, and legacy mapping.
- [ ] Run `python -m unittest test_instruction_envelope test_instruction_role_contract -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Add schema conditionals, template fields, and builder/renderer validation while preserving existing Git identity fields.
- [ ] Run focused instruction suites and the framework validator; confirm valid serialization and protocol failures for invalid cases.
- [ ] Commit `feat: make instruction envelope role explicit`.

## Task 3: Extend Result Envelope and Handoff result-only ownership

**Files:** Modify result schema/template/renderer, Handoff skill and manifest if a version advance is required, and existing result/Handoff tests.

**Interfaces:** Add result-only `result_message_type` for `REVIEW_RESULT`, `REVIEW_FINDING`, `IMPLEMENTATION_RESULT`, and registered error/result classes. Reject instruction-side values. Add bounded `response_to_instruction_id`, `responder_role`, `return_role`, `review_target_revision`, `finding_ids`, `fix_round`, `remediation_decision_ref`, `protocol_error`, `role_observation`, `artifact_stage`, `REPOSITORY`, `BRANCH`, `HEAD_SHA`, `ARTIFACT_PATH`, `PUSH_STATUS`, and `REMOTE_VERIFICATION`. Preserve existing status/publication authority. Render `INSTRUCTION_TYPE` and `RESULT_MESSAGE_TYPE` from their respective sources; never render or accept generic `MESSAGE_TYPE`. Handoff remains derived from Result Envelope and cannot authorize execution.

**Steps:**

- [ ] Add failing tests for result types, instruction-side rejection, correlation, findings, protocol errors, sync fields, and absence of generic `message_type`.
- [ ] Run `python -m unittest test_result_contract_schema test_result_return test_handoff_navigation_contract -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Update schema/template/renderer/Handoff contract with explicit result ownership and bounds.
- [ ] Run focused result/Handoff suites and the framework validator; confirm Result Envelope remains authoritative.
- [ ] Commit `feat: add result envelope message classification`.

## Task 4: Enforce role authority and finding/fix lifecycle

**Files:** Modify `validate_project.py`; modify `publication_contract.py` only if required by existing authority checks; create `test_role_authority.py` and `test_review_lifecycle.py`.

**Interfaces:** Add pure gates over parsed envelopes and current revision. Reject invalid executor identity, unauthorized action, reviewer mutation, scope expansion, stale revision, and ambiguous identity with existing `FAIL`/`BLOCKED` outcomes plus stable protocol errors. Require findings to cite evidence/review SHA but never treat them as approval. Accept remediation only after explicit GPT/User decision and a new `FIX_INSTRUCTION` naming one implementer, approved scope, revision, and findings. Re-review points to the new result revision and retains original evidence references.

**Steps:**

- [ ] Write failing tests for every role/action/identity violation, stale revision, reviewer mutation, finding-without-fix, approved fix, and re-review.
- [ ] Run `python -m unittest test_role_authority test_review_lifecycle -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Integrate shared predicates without mutating machine-authoritative artifacts or adding Kernel states.
- [ ] Run focused suites and `python .gpt-codex/scripts/validate_project.py .`; confirm valid existing projects pass and invalid transitions block.
- [ ] Commit `feat: enforce role authority and review lifecycle`.

## Review Gate A: Integrated protocol contract and validation milestone

- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py' -q`, both validators, and inspect the integrated Tasks 1–4 diff.
- [ ] Verify instruction/result disjointness, no generic `message_type`, no new Kernel state, and finding-as-evidence semantics.
- [ ] Have the assigned `CODEX_REVIEWER` review Tasks 1–4 against the approved spec.
- [ ] Record any finding as evidence; require GPT/User remediation and a new `FIX_INSTRUCTION` before correction.
- [ ] Preserve the reviewed SHA as immutable evidence and use a new descendant commit for every approved correction.

## Task 5: Add stage routing and append-only Git history checks

**Files:** Modify `git_continuity.py` or create bounded `review_history.py`; create `test_stage_review_routing.py` and `test_review_history.py`.

**Interfaces:** Define `review_routing_for_stage(stage: str, remote_trigger: str | None = None) -> dict[str, str]`; `validate_review_revision(previous_reviewed_sha: str | None, candidate_sha: str, is_ancestor: Callable[[str, str], bool]) -> list[str]`; and `classify_review_sync(stage: str, push_status: str, remote_verification: str, remote_head_sha: str | None, expected_head_sha: str) -> str`. Compose existing sync seams. Return `LOCAL_COMPLETE`, `SYNC_PENDING`, `REMOTE_VERIFIED`, or `RECONCILIATION_REQUIRED` as applicable. Reject rewrite/publication operations after formal DESIGN/PLAN review; distinguish visibility from production publication.

**Steps:**

- [ ] Add failing tests for stage matrix, local implementation completion, remote mismatch, descendant-only fixes, and each forbidden rewrite/publication action.
- [ ] Run `python -m unittest test_stage_review_routing test_review_history -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Implement predicates by composing existing `SyncSnapshot`, `SyncDecision`, and remote-verification logic.
- [ ] Run focused suites plus `test_git_continuity` and `test_remote_verification`.
- [ ] Commit `feat: enforce stage review routing and history continuity`.

## Task 6: Align routing documentation and legacy handling

**Files:** Modify `AGENTS.md` and `.gpt-codex/README.md`; modify bootstrap prompt only if authoritative; create `test_role_routing_docs.py`.

**Interfaces:** Preserve `[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, `[INFO]`; document that labels do not replace envelope fields, machine authority precedes project-local routing, and project-local instructions stay in scope. State explicit field ownership, no generic type, finding causal rule, derived Handoff behavior, and registered legacy instruction aliases.

**Steps:**

- [ ] Add failing documentation tests for labels, precedence, roles, type ownership, causal finding flow, and legacy mapping.
- [ ] Run `python -m unittest test_role_routing_docs -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Update only authoritative routing sections.
- [ ] Run the documentation suite and inspect `rg -n -i 'message_type|REVIEW_RESULT|REVIEW_FINDING|instruction_type|result_message_type'` occurrences for correct ownership.
- [ ] Commit `docs: align role communication routing guidance`.

## Task 7: Close consumer projection and validator coverage

**Files:** Modify consumer-projection manifest and relevant projection/runtime closure tests; add a focused role projection test if needed.

**Interfaces:** Classify every new consumer schema/template/helper/validator dependency exactly. Keep plans/specs/tests/management identity outside runtime projection, including this plan as `DEVELOPMENT_HISTORY`. Preserve one manifest authority and exclude management-only strategy, scoring, registry, capability, alignment, and orchestration internals.

**Steps:**

- [ ] Add failing tests for new runtime paths, management exclusions, exact history classification, and runtime closure.
- [ ] Run focused consumer projection/runtime tests; confirm expected missing-classification failures.
- [ ] Update exact manifest paths and closure assertions.
- [ ] Run focused projection tests, both validators, and the complete test suite.
- [ ] Commit `test: close role protocol consumer projection`.

## Task 8: Final integration, candidate versioning, and acceptance

**Files:** After acceptance authorization only, modify `VERSION` to additive candidate `2.4.0`, `.gpt-codex/CHANGELOG.md`, and create `releases/records/v2.4.0.json`; generate output only through the existing release command.

**Interfaces:** Keep Kernel/schema-generation versions unchanged. Record type separation, legacy compatibility, exact SHA, validation evidence, projection status, and publication status. A review-visibility push is not a publication claim. No main merge, tag, or external publication occurs without separate authorization.

**Steps:**

- [ ] Write final assertions for causal lifecycle, ownership, authority, routing, append-only history, projection, and version consistency.
- [ ] Run the complete test suite, both validators, and version checks; confirm all pass.
- [ ] Change release metadata only after acceptance inputs and explicit authorization are present, then rerun all checks.
- [ ] Have the same `CODEX_REVIEWER` complete Review Gate B; route any finding through a new `FIX_INSTRUCTION` cycle.
- [ ] Commit `release: record role communication protocol candidate` only when authorized and green.

## Review Gate B: Final integrated implementation before acceptance/release

- [ ] Confirm every post-review correction is a new descendant of the formally reviewed DESIGN/PLAN SHA.
- [ ] Confirm `git diff --check`, complete tests, validators, version consistency, projection closure, and remote-head verification pass.
- [ ] Confirm exact artifact paths are readable at the verified SHA.
- [ ] Have the same reviewer re-review the integrated implementation and documentation against the spec.
- [ ] Do not accept or prepare release metadata while any blocker, reconciliation requirement, stale revision, unauthorized action, or unresolved finding remains.

## Definition of Done

- Separate schema-enforced instruction/result type authorities exist with one conceptual taxonomy and no generic `message_type`.
- Every executable instruction has one authorized executor; actions are checked against role authority.
- Findings are evidence only and execution requires GPT/User remediation plus a new `FIX_INSTRUCTION`.
- Stage routing, remote verification, append-only review history, and fast-forward synchronization match the spec.
- Kernel, schema-generation, machine authorities, Handoff derivation, and consumer projection invariants remain valid.
- Both milestone gates have evidence and the complete test/validator suite is green.
- Candidate `2.4.0` metadata changes only when authorized; this Work Unit does not merge, push main, or publish.

## Self-Review Checklist

- [ ] Every future task specifies files, interfaces, failure cases, focused tests, verification commands, and a concrete commit.
- [ ] No unfinished work item, vague deferred action, or unnamed authority remains in the plan.
- [ ] The plan preserves instruction-only `instruction_type` and result-only `result_message_type` ownership.
- [ ] The plan explicitly rejects a third generic `message_type` authority.
- [ ] The plan preserves the causal finding flow and never makes a finding executable.
- [ ] The plan uses milestone gates only, with one persistent implementer and no fresh agent per task.
- [ ] The plan accounts for append-only history, descendant fixes, fast-forward synchronization, and remote verification.
