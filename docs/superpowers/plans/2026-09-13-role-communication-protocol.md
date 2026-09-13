# Role Communication Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved role-communication protocol as one explicit framework contract for role identity, Instruction/Result Envelope ownership, authority boundaries, review lifecycle, stage routing, and verifiable Git synchronization.

**Architecture:** Extend the existing envelopes, schemas, templates, validators, Git continuity seam, Handoff projection, routing documentation, and consumer-projection metadata. Keep one conceptual Protocol Message Taxonomy while exposing instruction-side classes only through `InstructionEnvelope.instruction_type` and result-side classes only through `ResultEnvelope.result_message_type`. Add one pure shared vocabulary/validation module. Do not add a message bus, message store, generic `message_type`, and a second authority system.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3 standard library, `unittest`, existing framework/project validators, Git continuity helpers, Markdown, and the consumer-projection manifest.

**Spec:** `docs/superpowers/specs/2026-09-13-role-communication-protocol-design.md` at reviewed revision `e005ccf97d4cb0b32a9c9f5176430e677ff0fafd`.

## Global Constraints

- Preserve Kernel `2.0.0`, schema-generation `1`, `CONTROL.json`, `STATE.json`, Result Envelope authority, publication contract, and current validator gates.
- The approved protocol role set is exactly: `GPT_ORCHESTRATOR`, `GPT_REVIEWER`, `CODEX_IMPLEMENTER`, `CODEX_REVIEWER`, `USER_APPROVER`, `USER_LOCAL`, and `INFORMATION_ONLY`.
- `PLAN_TASK`, `AGENT`, and `FRESH_REVIEWER` describe allocation and cadence, not executor identities. Preserve the execution-assignment semantics `PLAN_TASK != AGENT` and `PLAN_TASK != FRESH_REVIEWER`. Do not place any of these concepts in `ROLES`.
- One Work Unit has one persistent `CODEX_IMPLEMENTER`. Tasks execute serially; bounded batches are permitted. Task boundaries do not create agents and do not create Reviewer gates. `CODEX_REVIEWER` is assigned at explicit milestone/risk gates; the same reviewer re-reviews by default; fresh agents require explicit escalation.
- **Framework Execution Governance overrides generic workflow recommendations for agent allocation and review cadence.** Superpowers supplies planning, TDD, decomposition, and commit discipline; Framework Execution Governance controls allocation and review cadence.
- `InstructionEnvelope.instruction_type` accepts only `EXECUTION_INSTRUCTION`, `REVIEW_REQUEST`, `FIX_INSTRUCTION`, `APPROVAL_REQUEST`, `RECONCILIATION_REQUEST`, `INFORMATION_ONLY`, `PROJECT_CONTEXT_BOOTSTRAP`, and explicitly registered legacy instruction aliases.
- `ResultEnvelope.result_message_type` accepts result-side types including `REVIEW_RESULT`, `REVIEW_FINDING`, `IMPLEMENTATION_RESULT`, and registered protocol error/result classifications. Result-side values are rejected in `instruction_type`.
- No generic `message_type` exists. `instruction_type` belongs only to Instruction Envelope; `result_message_type` belongs only to Result Envelope.
- Preserve `REVIEW_FINDING → evidence returned to GPT/User → remediation decision → new FIX_INSTRUCTION → CODEX_IMPLEMENTER`; a finding never becomes executable.
- Every executable instruction has exactly one scalar executor. Missing, plural, compound, unknown, and ambiguous identity blocks execution. Role actions are checked against allowed/forbidden sets. Reviewers are non-mutating.
- DESIGN and PLAN require remote review visibility plus GPT review. IMPLEMENTATION keeps remote visibility optional and uses `CODEX_REVIEWER` for technical review.
- After a DESIGN/PLAN SHA is exposed for formal review, it is immutable evidence. Fixes use new descendant commits and fast-forward synchronization by default. Amend, rebase, history-removing reset, force push, branch replacement, merge main, tag, release, and publication are forbidden by default.
- A review-visibility push is not production publication. An unverified state and a mismatched remote state yield `RECONCILIATION_REQUIRED`.
- Creating or authorizing an instruction does not prove that the target executor received or executed it. Remote review visibility is not instruction delivery; instruction issuance is not execution confirmation; execution confirmation requires observable evidence from an authorized evidence source.
- Until direct GPT-to-Codex transport is governed, bootstrap uses explicit relay transport such as `GPT → User relay → Codex`. User relay is transport only: it does not change authority, authorize extra actions, modify the Instruction Envelope, or count as execution evidence.
- Bootstrap evidence states are conceptual only: `INSTRUCTION_ISSUED → EXECUTION_UNCONFIRMED → REMOTE_EVIDENCE_OBSERVED → EXECUTION_CONFIRMED`; no Kernel state machine and no terminology-only production schema field is added.
- Missing synchronization evidence maps to `LOCAL_COMPLETE / SYNC_PENDING`; conflicting or stale facts map to `RECONCILIATION_REQUIRED`. Missing evidence is not contradictory evidence.
- Result synchronization facts remain canonical lower-case Result Envelope properties. Uppercase names are derived GPT Return/Handoff labels only and do not create a second machine fact source.
- `publication_contract.py` remains an existing authority seam and is not modified by this protocol implementation.
- This current Work Unit is plan-only. No production implementation, schema change, Kernel change, and schema-generation change is performed now.

## Exact File Decisions

Repository inspection at the current branch confirmed the existing extension seams: envelope builders/renderers already exist in `instruction_envelope.py` and `result_return.py`; project authority checks live in `validate_project.py` and `publication_contract.py`; synchronization decisions live in `git_continuity.py`; Handoff is derived from Result Envelope; consumer scope is controlled by the exact-path projection manifest. The following decisions are locked before implementation.

### CREATE

- `CREATE: .gpt-codex/scripts/role_communication.py` — shared pure taxonomy, role, action, and stage predicates.
- `CREATE: .gpt-codex/tests/test_role_communication_taxonomy.py` — exact role/type taxonomy tests.
- `CREATE: .gpt-codex/tests/test_instruction_role_contract.py` — Instruction Envelope role and executor tests.
- `CREATE: .gpt-codex/tests/test_role_authority.py` — action and mutation authority tests.
- `CREATE: .gpt-codex/tests/test_review_lifecycle.py` — finding/decision/fix/re-review tests.
- `CREATE: .gpt-codex/tests/test_stage_review_routing.py` — stage routing tests.
- `CREATE: .gpt-codex/tests/test_review_history.py` — append-only history tests.
- `CREATE: .gpt-codex/tests/test_role_routing_docs.py` — routing documentation contract tests.
- `CREATE: .gpt-codex/tests/test_role_consumer_projection.py` — role protocol consumer projection tests.

### MODIFY

- `MODIFY: .gpt-codex/schemas/instruction-envelope.schema.json` — add explicit instruction-side role/action/causal fields and instruction-only type validation.
- `MODIFY: .gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json` — mirror the Instruction Envelope contract.
- `MODIFY: .gpt-codex/scripts/instruction_envelope.py` — build and render the locked Instruction Envelope fields.
- `MODIFY: .gpt-codex/tests/test_instruction_envelope.py` — preserve and extend existing builder/renderer coverage.
- `MODIFY: .gpt-codex/schemas/result-envelope.schema.json` — add result-only type and bounded result correlation fields.
- `MODIFY: .gpt-codex/project-template/RESULT_ENVELOPE.template.json` — mirror the Result Envelope contract.
- `MODIFY: .gpt-codex/scripts/result_return.py` — render explicit input/result type labels without a generic type label.
- `MODIFY: .gpt-codex/builtins/skills/handoff/SKILL.md` — document derived result projection and non-executable findings.
- `MODIFY: .gpt-codex/builtins/skills/handoff/manifest.json` — advance the Handoff contract version to `1.3.0` for the new derived fields.
- `MODIFY: .gpt-codex/tests/test_result_contract_schema.py` — extend result schema coverage.
- `MODIFY: .gpt-codex/tests/test_result_return.py` — extend renderer coverage.
- `MODIFY: .gpt-codex/tests/test_handoff_navigation_contract.py` — extend derived Handoff coverage.
- `MODIFY: .gpt-codex/scripts/validate_project.py` — enforce role identity, action authority, lifecycle, and stage gates.
- `NOT MODIFIED: .gpt-codex/scripts/publication_contract.py` — publication authority remains an existing seam; role protocol semantics stay in the shared helper, envelopes, project validator, Git continuity, and derived views.
- `MODIFY: .gpt-codex/tests/test_git_continuity.py` — extend existing synchronization seam coverage.
- `MODIFY: .gpt-codex/scripts/git_continuity.py` — add stage routing and append-only revision predicates.
- `MODIFY: AGENTS.md` — align human/agent labels and execution routing.
- `MODIFY: .gpt-codex/README.md` — align machine-authority and Handoff guidance.
- `MODIFY: .gpt-codex/BOOTSTRAP_PROMPT.md` — align authoritative bootstrap routing.
- `MODIFY: .gpt-codex/release/consumer-projection-manifest.json` — classify every new runtime path and preserve history exclusions.
- `MODIFY: .gpt-codex/tests/test_consumer_projection.py` — extend exact-path projection checks.
- `MODIFY: .gpt-codex/tests/test_consumer_runtime_closure.py` — extend runtime closure checks.

### TEST

- `TEST: .gpt-codex/tests/test_version_consistency.py` — run existing version compatibility assertions without modifying the file.
- `TEST: .gpt-codex/tests/test_publication_authority.py` — run existing publication-authority assertions without modifying the file.
- `TEST: .gpt-codex/tests/test_remote_verification.py` — run existing remote verification assertions without modifying the file.
- `TEST: .gpt-codex/tests/test_consumer_workspace.py` — run existing consumer workspace assertions without modifying the file.
- `TEST: complete .gpt-codex/tests suite` — run the full regression suite after every integrated milestone.

### NOT MODIFIED

- `NOT MODIFIED: .gpt-codex/KERNEL.md` — Kernel remains `2.0.0`.
- `NOT MODIFIED: schema-generation configuration and scripts` — schema generation remains `1`.
- `NOT MODIFIED: .gpt-codex/scripts/validate_framework.py` — current framework validator already discovers the bounded framework assets; no new validator authority is needed.
- `NOT MODIFIED: .gpt-codex/scripts/consumer_projection.py` — existing projection engine remains the sole projection mechanism.
- `NOT MODIFIED: .gpt-codex/scripts/release_framework.py` — release execution is outside this Implementation Work Unit.
- `NOT MODIFIED: .gpt-codex/scripts/release_archive.py` — release archival is outside this Implementation Work Unit.
- `NOT MODIFIED: VERSION` — version realization belongs to a separate Release/Publication Work Unit.
- `NOT MODIFIED: .gpt-codex/CHANGELOG.md` — release metadata is outside this Implementation Work Unit.
- `NOT MODIFIED: releases/records/v2.4.0.json` — release record creation is outside this Implementation Work Unit.
- `NOT MODIFIED: dist/*` — generated artifacts are outside this Implementation Work Unit.
- `NOT MODIFIED: CONTROL.json and STATE.json` — existing machine authority remains unchanged.

## Execution Model and Review Gates

One persistent `CODEX_IMPLEMENTER` executes the tasks in order. Tasks are independently testable and each has a local commit, but task completion is not a Reviewer gate. No fresh Implementer and Reviewer are created per task and per commit.

Review Gate A occurs after the integrated protocol contract and validation core, covering Tasks 1–4. Review Gate B occurs after all implementation and acceptance evidence, covering Tasks 5–8. These are the only default Reviewer gates.

The finding flow is `CODEX_REVIEWER → REVIEW_FINDING → GPT + USER remediation decision → FIX_INSTRUCTION → CODEX_IMPLEMENTER → same CODEX_REVIEWER re-review by default`. A fresh reviewer requires explicit escalation.

---

## Task 1: Add the exact seven-role taxonomy and authority predicates

**Files:** `CREATE: .gpt-codex/scripts/role_communication.py`; `CREATE: .gpt-codex/tests/test_role_communication_taxonomy.py`; `NOT MODIFIED: .gpt-codex/scripts/validate_framework.py`.

**Interfaces:** Define immutable `ROLES` containing exactly the approved seven roles and no `GPT_USER`, `PLAN_TASK`, `AGENT`, and `FRESH_REVIEWER`. Define `INSTRUCTION_TYPES`, `RESULT_MESSAGE_TYPES`, `ACTIONS`, and `ARTIFACT_STAGES`. Define `validate_executor_role(value: object) -> list[str]`, `validate_instruction_type(value: object) -> list[str]`, `validate_result_message_type(value: object) -> list[str]`, `allowed_actions_for_role(role: str) -> frozenset[str]`, and `validate_action_authority(role: str, authorized_actions: Sequence[str], forbidden_actions: Sequence[str]) -> list[str]`. `USER_LOCAL` and `USER_APPROVER` receive only their defined actions; `INFORMATION_ONLY` cannot execute mutation.

**Steps:**

- [ ] Write failing tests for exact role-set equality, allocation-concept exclusion, all instruction/result types, disjointness, registered legacy aliases, and stable executor/action error codes.
- [ ] Run `python -m unittest test_role_communication_taxonomy -v` from `.gpt-codex/tests`; confirm failure because the helper is absent.
- [ ] Implement the immutable constants and deterministic pure validators without dispatch, storage, and prose parsing.
- [ ] Run the focused suite and `python .gpt-codex/scripts/validate_framework.py`; confirm the role contract passes with Kernel/schema-generation versions unchanged.
- [ ] Commit `feat: add exact role communication taxonomy`.

## Task 2: Extend the Instruction Envelope

**Files:** `MODIFY: .gpt-codex/schemas/instruction-envelope.schema.json`; `MODIFY: .gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`; `MODIFY: .gpt-codex/scripts/instruction_envelope.py`; `MODIFY: .gpt-codex/tests/test_instruction_envelope.py`; `CREATE: .gpt-codex/tests/test_instruction_role_contract.py`.

**Interfaces:** Extend `build_instruction_envelope` with keyword-only `issuer_role`, `executor_role`, `return_role`, `authorized_actions`, `forbidden_actions`, `evidence_requirements`, `completion_gate`, `in_response_to_instruction_id`, `in_response_to_result_id`, `review_target_revision`, `finding_ids`, `fix_round`, and `artifact_stage`. Omit absent optional fields. Validate `instruction_type` against instruction-side taxonomy only. Require one scalar executor. Validate actions and bounded provenance. Registered legacy `[CODEX]` aliases map deterministically to one `CODEX_IMPLEMENTER`; unknown legacy forms fail closed.

**Steps:**

- [ ] Add failing schema, builder, renderer, and template tests for valid role-bearing instructions, invalid result-side types, every invalid executor shape, unauthorized actions, causal references, and fail-closed legacy `[CODEX]` handling.
- [ ] Run `python -m unittest test_instruction_envelope test_instruction_role_contract -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Add schema conditionals and builder/renderer validation while preserving existing Git identity fields.
- [ ] Run the focused instruction suites plus the framework validator; confirm valid serialization and protocol failures for invalid inputs.
- [ ] Commit `feat: make instruction envelope role explicit`.

## Task 3: Extend the Result Envelope and Handoff projection

**Files:** `MODIFY: .gpt-codex/schemas/result-envelope.schema.json`; `MODIFY: .gpt-codex/project-template/RESULT_ENVELOPE.template.json`; `MODIFY: .gpt-codex/scripts/result_return.py`; `MODIFY: .gpt-codex/builtins/skills/handoff/SKILL.md`; `MODIFY: .gpt-codex/builtins/skills/handoff/manifest.json`; `MODIFY: .gpt-codex/tests/test_result_contract_schema.py`; `MODIFY: .gpt-codex/tests/test_result_return.py`; `MODIFY: .gpt-codex/tests/test_handoff_navigation_contract.py`.

**Interfaces:** Add result-only `result_message_type` for `REVIEW_RESULT`, `REVIEW_FINDING`, `IMPLEMENTATION_RESULT`, and registered protocol error/result classes. Reject instruction-side values. Add bounded `response_to_instruction_id`, `responder_role`, `return_role`, `review_target_revision`, `finding_ids`, `fix_round`, `remediation_decision_ref`, `protocol_error`, `role_observation`, `artifact_stage`, `artifact_path`, `source_github_repository_full_name`, `current_remote_ref`, `local_head_sha`, `remote_head_sha`, `sync_status`, `push_status`, and `remote_verification`. Uppercase `REPOSITORY`, `BRANCH`, `BASE_SHA`, `HEAD_SHA`, `ARTIFACT_PATH`, `PUSH_STATUS`, and `REMOTE_VERIFICATION` are derived GPT Return/Handoff labels only. Render `INSTRUCTION_TYPE` and `RESULT_MESSAGE_TYPE` from their respective source fields; never render `MESSAGE_TYPE`. Handoff remains derived evidence and cannot authorize execution.

**Steps:**

- [ ] Add failing tests for result-side types, instruction-side rejection, correlation, findings, protocol errors, canonical synchronization facts, derived uppercase presentation labels, and absence of generic `message_type`.
- [ ] Run `python -m unittest test_result_contract_schema test_result_return test_handoff_navigation_contract -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Update schema, template, renderer, Handoff guidance, and manifest version with explicit result ownership and bounds.
- [ ] Run focused result/Handoff suites and the framework validator; confirm Result Envelope remains authoritative.
- [ ] Commit `feat: add result envelope message classification`.

## Task 4: Enforce role authority and the finding/fix lifecycle

**Files:** `MODIFY: .gpt-codex/scripts/validate_project.py`; `NOT MODIFIED: .gpt-codex/scripts/publication_contract.py`; `CREATE: .gpt-codex/tests/test_role_authority.py`; `CREATE: .gpt-codex/tests/test_review_lifecycle.py`; `TEST: .gpt-codex/tests/test_publication_authority.py`.

**Interfaces:** Add pure gates over parsed envelopes and current revision. Reject invalid executor identity, unauthorized action, reviewer mutation, scope expansion, stale review revision, and ambiguous identity with existing `FAIL`/`BLOCKED` outcomes plus stable protocol errors. Require findings to cite evidence and reviewed SHA without treating them as approval. Accept remediation only after explicit GPT/User decision and a new `FIX_INSTRUCTION` naming one implementer, approved scope, revision, and findings. Re-review points to the new result revision and retains original evidence references. Keep publication semantics in the existing unmodified publication contract.

**Steps:**

- [ ] Write failing tests for every role/action/identity violation, stale revision, ambiguous identity, reviewer mutation, finding-without-fix, approved fix, and re-review.
- [ ] Run `python -m unittest test_role_authority test_review_lifecycle -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Integrate shared predicates without mutating machine-authoritative artifacts and without adding Kernel states.
- [ ] Run focused suites and `python .gpt-codex/scripts/validate_project.py .`; confirm valid projects pass and invalid transitions block.
- [ ] Commit `feat: enforce role authority and review lifecycle`.

## Review Gate A: Integrated protocol contract and validation core

- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py' -q`, both validators, and inspect the Tasks 1–4 diff.
- [ ] Verify exact seven-role consistency, instruction/result disjointness, no generic `message_type`, no new Kernel state, and finding-as-evidence semantics.
- [ ] Have the assigned `CODEX_REVIEWER` review the integrated contract against the approved spec.
- [ ] Record any finding as evidence; require GPT/User remediation and a new `FIX_INSTRUCTION` before correction.
- [ ] Preserve the reviewed SHA as immutable evidence and use a new descendant commit for every approved correction.

## Task 5: Add stage routing and append-only Git history checks

**Files:** `MODIFY: .gpt-codex/scripts/git_continuity.py`; `MODIFY: .gpt-codex/tests/test_git_continuity.py`; `CREATE: .gpt-codex/tests/test_stage_review_routing.py`; `CREATE: .gpt-codex/tests/test_review_history.py`; `TEST: .gpt-codex/tests/test_remote_verification.py`.

**Interfaces:** Define `review_routing_for_stage(stage: str, remote_trigger: str | None = None) -> dict[str, str]`; `validate_review_revision(previous_reviewed_sha: str | None, candidate_sha: str, is_ancestor: Callable[[str, str], bool]) -> list[str]`; and `classify_review_sync(stage: str, push_status: str, remote_verification: str, remote_head_sha: str | None, expected_head_sha: str) -> str`. Compose existing sync seams. Classify valid local work with push not attempted, ordinary push failure without divergence, incomplete verification, and temporary remote unavailability as `LOCAL_COMPLETE / SYNC_PENDING`. Classify remote-head mismatch, divergence, invalid reviewed ancestry, stale state revision, and repository/ref identity conflict as `RECONCILIATION_REQUIRED`. Missing synchronization evidence is not contradictory synchronization evidence. Reject rewrite and publication operations after formal DESIGN/PLAN review; keep fast-forward synchronization as the default.

**Steps:**

- [ ] Add failing tests for the stage matrix, each independent `LOCAL_COMPLETE / SYNC_PENDING` condition, each independent `RECONCILIATION_REQUIRED` condition, descendant-only fixes, and every forbidden history/publication action.
- [ ] Run `python -m unittest test_stage_review_routing test_review_history test_git_continuity -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Implement predicates by composing existing `SyncSnapshot`, `SyncDecision`, and remote-verification logic.
- [ ] Run focused routing/history suites and `test_remote_verification`; confirm exact SHA and reconciliation behavior.
- [ ] Commit `feat: enforce stage review routing and history continuity`.

## Task 6: Align routing documentation and legacy behavior

**Files:** `MODIFY: AGENTS.md`; `MODIFY: .gpt-codex/README.md`; `MODIFY: .gpt-codex/BOOTSTRAP_PROMPT.md`; `CREATE: .gpt-codex/tests/test_role_routing_docs.py`.

**Interfaces:** Preserve `[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, and `[INFO]`; document that labels do not replace envelope fields. Document machine authority precedence, exact role set, explicit type ownership, no generic type, finding causal flow, derived Handoff behavior, and registered legacy aliases. Document fail-closed behavior for unknown legacy `[CODEX]` forms.

**Steps:**

- [ ] Add failing documentation tests for labels, precedence, exact roles, type ownership, causal finding flow, and legacy fail-closed mapping.
- [ ] Run `python -m unittest test_role_routing_docs -v` from `.gpt-codex/tests`; confirm expected failures.
- [ ] Update only authoritative routing sections while preserving unrelated project guidance.
- [ ] Run the documentation suite and inspect all `message_type`, `REVIEW_RESULT`, `REVIEW_FINDING`, `instruction_type`, and `result_message_type` occurrences for correct ownership.
- [ ] Commit `docs: align role communication routing guidance`.

## Task 7: Close consumer projection and runtime validation

**Files:** `MODIFY: .gpt-codex/release/consumer-projection-manifest.json`; `MODIFY: .gpt-codex/tests/test_consumer_projection.py`; `MODIFY: .gpt-codex/tests/test_consumer_runtime_closure.py`; `CREATE: .gpt-codex/tests/test_role_consumer_projection.py`; `TEST: .gpt-codex/tests/test_consumer_workspace.py`.

**Interfaces:** Classify every new consumer schema, template, helper, validator dependency, and Handoff contract exactly. Keep plans, specs, tests, and management identity outside runtime projection, including this plan as `DEVELOPMENT_HISTORY`. Preserve one manifest authority and exclude management-only strategy, scoring, registry, capability, alignment, and orchestration internals.

**Steps:**

- [ ] Add failing tests for new runtime paths, management exclusions, exact history classification, and runtime closure.
- [ ] Run focused consumer projection/runtime tests; confirm expected classification failures.
- [ ] Update exact manifest paths and closure assertions.
- [ ] Run focused projection tests, both validators, the consumer workspace suite, and the complete test suite.
- [ ] Commit `test: close role protocol consumer projection`.

## Task 8: Final Integration and Acceptance Evidence

**Files:** `TEST: .gpt-codex/tests/test_version_consistency.py`; `TEST: .gpt-codex/tests/test_publication_authority.py`; `TEST: .gpt-codex/tests/test_remote_verification.py`; `TEST: complete .gpt-codex/tests suite`; `NOT MODIFIED: VERSION`; `NOT MODIFIED: .gpt-codex/CHANGELOG.md`; `NOT MODIFIED: releases/records/v2.4.0.json`; `NOT MODIFIED: dist/*`.

**Interfaces:** Produce exact implementation evidence for causal lifecycle, type ownership, role/action authority, stage routing, append-only history, transport boundary, bootstrap evidence states, consumer projection, version compatibility, Kernel `2.0.0`, and schema generation `1`. The acceptance package contains test output, validator output, projection/runtime closure, `git diff --check`, exact implementation SHA, canonical Result Envelope facts (`source_github_repository_full_name`, `current_remote_ref`, `local_head_sha`, `remote_head_sha`, `sync_status`, `push_status`, `remote_verification`, `artifact_stage`, and `artifact_path`), changed paths, deviations, and blockers. Uppercase return labels are presentation derived from those facts.

**Steps:**

- [ ] Write final integration assertions for causal lifecycle, type ownership, role/action authority, stage routing, append-only history, consumer projection, version compatibility, and unchanged Kernel/schema-generation versions.
- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py' -q`, `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, consumer closure checks, and `git diff --check`.
- [ ] Confirm exact implementation evidence records the verified local SHA, remote SHA, artifact paths, and all acceptance commands.
- [ ] Have the same `CODEX_REVIEWER` complete Review Gate B and route every finding through GPT/User remediation and a new `FIX_INSTRUCTION` cycle.
- [ ] Deliver the acceptance package to GPT/User without changing version, generating artifacts, merging main, tagging, and publishing.

**Test boundary:** Implementation acceptance requires a clean, verified descendant branch, exact review SHA evidence, no forbidden history rewrite, no generic type authority, and no unresolved blocker.

## Review Gate B: Final integrated implementation before acceptance

- [ ] Confirm every post-review correction is a new descendant of the formally reviewed DESIGN/PLAN SHA.
- [ ] Confirm `git diff --check`, complete tests, validators, version compatibility, projection closure, and remote-head verification pass.
- [ ] Confirm exact implementation evidence and artifact paths are readable at the verified SHA.
- [ ] Have the same `CODEX_REVIEWER` re-review the integrated implementation and documentation against the approved spec.
- [ ] Do not provide an acceptance package while any blocker, reconciliation requirement, stale revision, unauthorized action, and unresolved finding remains.

## Implementation Acceptance Boundary

The Implementation Work Unit ends at `CODEX_REVIEWER` Final Gate PASS followed by GPT/User implementation acceptance. This Work Unit does not realize a version, release metadata, generated artifact, tag, main merge, and publication.

## Release/Publication Work Unit Boundary

Framework `2.4.0` remains the expected next minor release candidate conceptually. A separate future Release/Publication Work Unit owns `VERSION`, `.gpt-codex/CHANGELOG.md`, `releases/records/v2.4.0.json`, generated artifacts, tags, main integration, and publication after implementation acceptance. That future Work Unit requires separate authorization and separate verification.

## Definition of Done

- Instruction and Result Envelopes have separate schema-enforced type authorities with one conceptual taxonomy and no generic `message_type`.
- The role set contains exactly the seven approved protocol roles; allocation concepts are not executor identities.
- Every executable instruction has one authorized executor; actions are checked against role authority; reviewers cannot mutate.
- Findings are evidence only and execution requires GPT/User remediation plus a new `FIX_INSTRUCTION`.
- Stage routing, remote verification, append-only history, and fast-forward synchronization match the approved design.
- Kernel, schema-generation, machine authorities, Handoff derivation, and consumer projection invariants remain valid.
- Review Gates A and B have evidence, the complete test/validator suite is green, and the acceptance package is ready for GPT/User.
- No implementation task changes release/version metadata; external publication is also excluded.

## Self-Review Checklist

- [ ] The role set is exactly the seven approved roles; `GPT_USER`, `PLAN_TASK`, `AGENT`, and `FRESH_REVIEWER` are not roles.
- [ ] `PLAN_TASK != AGENT` and `PLAN_TASK != FRESH_REVIEWER` remain allocation semantics only.
- [ ] The plan uses `superpowers:executing-plans` and explicitly gives Framework Execution Governance control over allocation and review cadence.
- [ ] No fresh agent, per-task Reviewer, and per-commit Reviewer is recommended.
- [ ] Every create/modify/test action has an exact path decision; no file-placement choice is deferred.
- [ ] Instruction-only `instruction_type`, result-only `result_message_type`, and rejection of generic `message_type` are explicit throughout.
- [ ] Legacy `[CODEX]` behavior is deterministic and fail-closed.
- [ ] Reviewer mutation denial, finding causality, DESIGN/PLAN append-only history, and optional IMPLEMENTATION remote visibility are explicit.
- [ ] Task 8 contains implementation acceptance evidence only; version/release/publication work is assigned to a separate future Work Unit.
- [ ] No unfinished work item appears in the plan; Kernel and schema-generation versions remain unchanged.
