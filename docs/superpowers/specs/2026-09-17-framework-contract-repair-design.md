# Framework Contract Repair Design

## 1. Context and observed evidence

This design is governed by released Framework 2.7.0 at `a112efcc24c969369224804a6fc1e5961626c05b`.  The candidate is a Framework repair only; it cannot govern its own creation, review, or acceptance.

The evidence inputs are `STATE-ORACLE-SCHEMA-REQUIRED-FIELDS-001`, `FIX-INSTRUCTION-FINDING-LIFECYCLE-CORRELATION-001`, `FIX-INSTRUCTION-SCHEMA-LIFECYCLE-COMPOSITION-TEST-GAP-001`, `CONTROL-PLANE-MUTATION-SCOPE-BINDING-001`, and `FUTURE-FIX-REVIEW-TARGET-FRESHNESS-REQUIRED-001`. They establish only the three defects below.

## 2. Problem statement

1. The canonical FIX lifecycle already requires and resolves `remediation_decision_ref`, but the instruction schema rejects it because its top-level object is closed. The builder and template cannot faithfully produce the same production-shaped FIX.
2. `validate_instruction_authority` compares a supplied `scope_paths` to `approved_scope`, but does nothing when the mutation action has no `scope_paths`. `evidence_requirements.files_changed` is declaration of expected evidence, not an authority boundary.
3. State and Work Unit transitions need bounded persistence, but ordinary Work Unit ownership cannot safely own `STATE`, its own authority artifact, or finding/adjudication records. Giving an implementation Work Unit those files would permit self-authorizing mutation.

## 3. Goals

- Make one production-shaped FIX consistent across schema, builder/template, role validation, review lifecycle, and the governed mutation gate.
- Make every newly evaluated mutating instruction carry explicit, durable, exact path authority and reject absence, emptiness, and expansion.
- Add one fail-closed, native control-plane route inside the existing instruction and validator architecture.
- Preserve the closed review/freshness lifecycle and historical readability.

## 4. Non-goals

This does not fix `STATE-ORACLE-SCHEMA-REQUIRED-FIELDS-001`; publish the preserved Baseline implementation; resume Task 3 Plugin; change Framework module count; add admin/root authority, a database, registry, queue, new control-plane subsystem, Framework release/activation, or a general role-system redesign.

## 5. Existing authority model

The Instruction Envelope binds target project, state revision, work unit, repository and roles. `CODEX_IMPLEMENTER` may have `MUTATE_APPROVED_SCOPE`; `CODEX_REVIEWER` is read/test/validate/report only and the validator rejects reviewer mutation. Pre-execution review correlates a `REVIEW_REQUEST` and a passing `REVIEW_RESULT` to an instruction's base SHA and project identity. The governed entry resolves a Work Unit at its immutable `target_work_unit_ref` and validates repository facts.

The current normal path derives `approved_scope` from the persisted Work Unit's `scope.owned_paths`, but its final authority comparison is optional. The current FIX lifecycle resolves remediation evidence at repository HEAD, ties it to current STATE revision, correlates finding/result/round/base SHA, and enforces reviewer freshness. It already expects instruction-side `remediation_decision_ref` even though the Envelope cannot serialize it.

## 6. Proven contract gaps

`instruction-envelope.schema.json` has `additionalProperties: false` and lacks `remediation_decision_ref` and `scope_paths`. `instruction_envelope.py` lacks both builder arguments, validation, serialization, and rendering. Its template lacks both fields. The role-contract tests assert the currently incomplete field set. Lifecycle tests construct an in-memory `remediation_decision_ref`, so they prove lifecycle behavior but not Envelope composition.

`validate_instruction_authority` only rejects a request when both `approved_scope` and `scope_paths` are supplied. `validate_governed_mutation_entry` calls it with a caller-provided scope; no shared check compares actual Git paths with authority. These are fail-open defects, not evidence-format defects.

## 7. Design invariants

`No authority => no mutation.` Plugin routes, Framework governs, and the Project owns state. Chat paths and evidence declarations never grant authority. `CODEX_REVIEWER` never mutates. An implementer never enlarges or edits the source of its own authority. Candidate rules are accepted only under current released 2.7.0. There is no eighth module and no generic bypass.

## 8. Alternatives considered

### A. Ordinary Work Unit ownership of control-plane files — rejected

Adding `STATE`, a Work Unit file, or evidence locations to the implementation Work Unit's `owned_paths` makes the executor able to alter its authority source or the authority record that authorizes it. A constrained form would still need an independent durable authority source, which is exactly the missing control-plane route.

### B. Bounded branch in existing instruction authority — chosen

Use `RECONCILIATION_REQUEST`, existing role protocol, pre-execution review, revision binding, user approval and `scope_paths`. Add a distinct control-plane rule in existing validators. It keeps one envelope, one State, one Work Unit format, and one governed entry.

### C. `USER_LOCAL` as executor — rejected as the native route

The current role contract gives `USER_LOCAL` `LOCAL_ACTION`, `READ`, and `REPORT`, not `MUTATE_APPROVED_SCOPE`; it has no durable scope or review/approval correlation contract. Manual local action alone is not authority. A user may approve the native route, but is not its mutation executor.

### D. One-time migration bridge — chosen only for this repair

Released 2.7.0 cannot itself start this repair: its closed Instruction Envelope cannot represent `scope_paths`, and durable main has no independently accepted Framework Contract Repair Work Unit.  Therefore the first repair cannot truthfully be described as an ordinary native mutation.  A narrow, externally recorded migration bridge is required to make native repaired authority durable; it is not a Framework control-plane route, a general bootstrap subsystem, or precedent for later work.

## 9. Chosen architecture

Add two Instruction Envelope fields and a validator-only control-plane branch:

| Concern | Durable source | Executor | Gate |
| --- | --- | --- | --- |
| Ordinary mutation | immutable target Work Unit `scope.owned_paths` | `CODEX_IMPLEMENTER` | existing governed entry plus required scope binding |
| FIX remediation | current STATE evidence referenced by `remediation_decision_ref` | `CODEX_IMPLEMENTER` | existing lifecycle plus Envelope composition |
| Control-plane transition | independently persisted control-plane authorization Work Unit, accepted design/plan, current STATE revision, and bound user approval result | `CODEX_IMPLEMENTER` | `RECONCILIATION_REQUEST` branch in the existing governed entry |
| First Framework Contract Repair | one-time immutable bridge authorization, independently reviewed before execution | `USER_LOCAL` | exact-path bridge procedure; native authority begins only after the repaired contracts are durable |

The control-plane authorization Work Unit is not the target being transitioned and may not be mutated by its executor. Its immutable reference, current authorized state, and accepted design/plan are resolved before execution. The request is issued by `GPT_ORCHESTRATOR`, executed by `CODEX_IMPLEMENTER`, independently pre-reviewed by `CODEX_REVIEWER`, and requires a durable `USER_APPROVER` approval result correlated to the request id, project/repository identity, expected state revision, exact `scope_paths`, and base SHA. Neither a chat declaration nor a bare approval is sufficient.

The bridge is intentionally outside that native row because it repairs the contracts required to create the native row.  It does not claim that the current fail-open behavior in `CONTROL-PLANE-MUTATION-SCOPE-BINDING-001` is authority.  Its only executor is the explicitly approving human in the `USER_LOCAL` role; `CODEX_IMPLEMENTER` has no bridge mutation permission and can only prepare/read/validate the candidate under a separate instruction.

## 10. Instruction Envelope changes

Add `scope_paths` as an optional Envelope property: an array of 1–100 unique repository-relative paths, each non-empty and matching the existing locator safety boundary (not absolute, drive-qualified, or containing `..`). Add `remediation_decision_ref` as an optional, non-empty instruction-side string.

Add conditional schema requirements:

- `EXECUTION_INSTRUCTION` and `FIX_INSTRUCTION` with `authorized_actions` containing `MUTATE_APPROVED_SCOPE` require non-empty `scope_paths`.
- A mutating `RECONCILIATION_REQUEST` requires non-empty `scope_paths`; only the dedicated control-plane validator branch may accept it.
- Existing read-only `RECONCILIATION_REQUEST` remains compatible without it. No other type gains mutating behavior unless its existing role protocol already allows `MUTATE_APPROVED_SCOPE`.

The builder accepts, validates, serializes, and renderer-emits both fields. The template displays both, with a real path-array placeholder. The schema does not encode FIX remediation lifecycle semantics beyond representability; the lifecycle remains the canonical owner of that correlation.

## 11. Mutation-scope binding

For ordinary Work Unit mutation, `approved_scope` is the persisted, immutable Work Unit resolved from `target_work_unit_ref`, specifically `scope.owned_paths`. It is never read from caller assertions or chat text.

When `MUTATE_APPROVED_SCOPE` is present, the authority validator must reject missing, non-array, empty, malformed, duplicate, or unowned `scope_paths` before review or mutation. It must require `scope_paths` to be a subset of that durable approved scope. A request with no scope therefore fails closed.

`evidence_requirements.files_changed` remains expected evidence. If declared, it must be a subset of `scope_paths`; it does not enlarge, replace, or infer authority.

The post-execution scope oracle is independent of `git diff BASE..HEAD`.  Before every `COMMIT` or `PUSH` publication boundary, the existing governed-mutation composition must normalize repository-relative paths and take the union of: (1) `git diff --name-only -z` for tracked unstaged changes, (2) `git diff --cached --name-only -z` for tracked staged changes, and (3) `git ls-files --others --exclude-standard -z` for untracked files created by execution.  It rejects the operation unless that union is a subset of the instruction's exact `scope_paths`; it must run even while `HEAD` remains the baseline.  After a commit, the same composition additionally compares the committed path set to `scope_paths` before a push.  This check belongs in `validate_project.py`/the existing governed mutation composition, not a new module.

## 12. Control-plane authority lifecycle

The control-plane branch applies only to a `RECONCILIATION_REQUEST` that requests `MUTATE_APPROVED_SCOPE` and declares an explicit control-plane intent. It uses the same repository/project binding, immutable target-work-unit reference, expected base SHA, exact expected State revision, pre-execution review, and post-execution changed-path enforcement as ordinary mutation, plus the controls below.

Eligible paths are exact repository-relative paths in these categories only:

1. the single `STATE` lifecycle record;
2. the current Work Unit's lifecycle metadata/state record;
3. one new Work Unit authority artifact named by the request;
4. only evidence/result artifacts needed to record the correlated review finding, adjudication, user approval, publication fact, or lifecycle transition.

The authorization Work Unit enumerates those eligible exact paths; no `.gpt-codex/**` glob is valid. Framework implementation, schemas, product/plugin code, general docs, release artifacts, and arbitrary project files are excluded. Such files require their own ordinary Work Unit and cannot be mixed into the control-plane request.

The independent authorization Work Unit is resolved at its immutable ref and must be `AUTHORIZED` at the exact current State revision. Its own file, STATE, and the target Work Unit are excluded from the executor's ordinary ownership and cannot appear as its self-owned authority. The validator rejects a request where authorization Work Unit equals the target transition Work Unit, where `scope_paths` attempts expansion, where an ineligible category occurs, or where a request combines normal implementation paths.

The native approval lifecycle is deliberately non-recursive:

1. **Approval creation:** `GPT_ORCHESTRATOR` issues an `APPROVAL_REQUEST` bound to the proposed reconciliation instruction. `USER_APPROVER` creates one production-shaped, immutable `APPROVAL_RESULT`; creation is a response, not a control-plane admission.
2. **Approval durability:** the result is written as a standalone immutable evidence artifact. Its identity and content are fixed before the later control-plane instruction is admitted. `CODEX_IMPLEMENTER` cannot create, rewrite, or select a substitute approval artifact.
3. **Approval admission:** the control-plane authority gate reads that already durable artifact, validates its complete correlation, then decides whether the proposed mutation may enter the native route. Admission does not require the native route to create the approval.
4. **STATE evidence projection:** only within the admitted, exact-path control-plane transition does the validator append the already-existing approval artifact reference to `STATE.evidence_refs` atomically with the transition. The projection records evidence; it neither creates approval nor grants it retrospectively.

The repair adds `APPROVAL_RESULT` rather than overloading a review result. It is mandatory in `.gpt-codex/schemas/result-envelope.schema.json`, `.gpt-codex/scripts/role_communication.py`, the result-envelope/taxonomy validation path, any result/template surface, focused result-taxonomy/schema tests, and composed control-plane lifecycle tests. The schema must close the `approved_instruction` object and require `instruction_id`, `expected_state_revision`, `expected_base_sha`, normalized `scope_paths`, project/repository identity, and the exact target Work Unit reference. It must also require `responder_role = USER_APPROVER`, `response_to_instruction_id` equal to the exact approval or reconciliation request, and `decision` equal to `APPROVE` or `REJECT`. `role_communication.py` must register `APPROVAL_RESULT` as a result message type and enforce that only `USER_APPROVER` produces it.

The same production-shaped result passes, in order: Result Envelope schema -> result-message taxonomy -> role/identity/correlation validation -> control-plane authority gate. The gate requires an `APPROVE` decision and rejects missing, stale, mismatched, non-approve, differently scoped, or mutable/local-only approval. Publication remains a separate action and is never authorized by this route.

Optimistic concurrency is required twice: request `expected_state_revision` equals current STATE revision before review, and the State revision is unchanged when the control-plane write is admitted. A newer revision invalidates review, approval, remediation basis, and authorization, producing `RECONCILIATION_REQUIRED` rather than retrying with widened scope.

## 13. FIX remediation lifecycle

`remediation_decision_ref` flows unchanged from schema through builder/template/rendering to `validate_review_lifecycle` and `validate_governed_mutation_entry`. For a FIX, lifecycle validation remains responsible for requiring it, resolving it only from evidence persisted at repository HEAD, and requiring the decision/adjudication basis to match the current STATE revision.

The existing freshness rules remain mandatory: FIX `expected_base_sha` equals finding `review_target_revision`; the finding's review target equals the authoritative current reviewed revision; adjudication and bases are current for the persisted State revision. Historical findings remain evidence, but stale findings or adjudications cannot grant mutation authority.

## 14. Self-hosting/bootstrap strategy

### 14.1 Why the bridge is necessary

Current released 2.7.0 cannot start this repair through a current-valid route. `instruction-envelope.schema.json` has `additionalProperties: false` and cannot represent `scope_paths`; durable main has no independently accepted Framework Contract Repair Work Unit. Consequently, an instruction asserting `MUTATE_APPROVED_SCOPE + scope_paths` is not a current 2.7.0 authority object. The bridge is the sole exception, fixed by this Design, and expires when the repaired native authority is durable.

### 14.2 Immutable bridge authorization, Work Unit creation, and exact scope

Before any local mutation, `USER_APPROVER` explicitly approves one canonical bridge authorization artifact published as an immutable, remote Git object outside the mutable candidate tree (a signed annotated tag or equivalent immutable remote object). It contains: repository identity; base SHA; the exact candidate branch; SHA-256 of the independently reviewed pre-execution review artifact; the full, closed `approved_instruction`-shaped object; the exhaustive exact path set below; a unique bridge id; `one_time: true`; and an expiry condition. It is durable before execution, cannot be rewritten by `CODEX_IMPLEMENTER`, and is not a chat message, in-memory record, or mutable local file.

The bridge itself creates and authorizes the single focused repair Work Unit at `.gpt-codex/work-units/framework-contract-repair-001.json`. That Work Unit records the bridge id, base SHA, immutable authorization object id, review-artifact hash, and the same exhaustive `owned_paths`; it is a durable output of the bridge, not the source of the bridge's authority. The bridge is therefore not self-authorization by the new schema or the new Work Unit.

The bridge can touch only these repair surfaces and their directly corresponding focused tests/templates:

- `.gpt-codex/schemas/instruction-envelope.schema.json`
- `.gpt-codex/schemas/result-envelope.schema.json`
- `.gpt-codex/scripts/instruction_envelope.py`
- `.gpt-codex/scripts/role_communication.py`
- `.gpt-codex/scripts/validate_project.py`
- `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`
- `.gpt-codex/work-units/framework-contract-repair-001.json`
- an existing result/template surface only if one is present and named in the immutable bridge artifact
- the exact existing focused instruction, result-schema/taxonomy, review-lifecycle, self-hosting/control-plane, and validator-context test files named in that artifact

It may not touch `STATE`, any pre-existing Work Unit, `CONTROL`, product files, Plugin files, release artifacts, or any schema other than the two named schemas. It creates no general bootstrap subsystem and performs no schema self-authorization beyond this exact repair candidate.

### 14.3 Bridge execution, review, publication, and expiry

`CODEX_REVIEWER` independently reviews the frozen base-SHA candidate and emits the review artifact before the user creates the immutable bridge authorization; the tag binds its SHA-256. `USER_LOCAL`, not `CODEX_IMPLEMENTER`, performs the local edits and stages only the exact bridge path set. The independent Git scope oracle in section 11 runs immediately before commit and again before push. The user then commits the exact reviewed candidate and pushes only its review branch; no main update, release, or activation is allowed. A second independent review of that exact remote commit is required before any later native authority action.

For the first native approval, the bridge's immutable authorization object is the durability source. The newly repaired native route then defines approval durability as a separately immutable approval artifact before admission; it must not pretend that current 2.7.0 already has a reusable `USER_LOCAL` publication authority. The bridge is the sole explicit exception for creating that first durable approval and focused Work Unit; later approvals are admitted only through the repaired schema/taxonomy/correlation route.

The bridge expires immediately when that remote commit makes the repaired native authority durable: it may not authorize a second commit, a rebase, a scope expansion, any control-plane mutation, or any later Work Unit. Any mismatch of base SHA, review hash, approved object, path union, or remote commit SHA fails with `RECONCILIATION_REQUIRED`; a new bridge cannot be inferred and requires a new explicit user approval and independent review.

## 15. Compatibility/migration

Newly evaluated instructions requesting mutation without `scope_paths` fail closed. Historical persisted instructions and evidence remain readable, but cannot authorize a new mutation. No migration is required merely to read history. Read-only instructions retain their current valid shape. This selects compatibility option A and forbids unsafe grandfathering.

## 16. Test-effectiveness design

Each critical test must include a sensitivity proof: alter the target fault and demonstrate the independent oracle fails, rather than treating a passing happy-path test as proof.

| Behavior | Independent oracle | Fault model | Required assertion/sensitivity proof |
| --- | --- | --- | --- |
| Valid production-shaped FIX | JSON schema, builder round trip, lifecycle, governed entry | remove only `remediation_decision_ref` | schema/builder composition and lifecycle/gate fail |
| FIX freshness | persisted STATE evidence and authoritative review context | stale finding review SHA; stale adjudication revision | lifecycle returns stale/reconciliation error |
| Ordinary scope | immutable resolved Work Unit | omit scope; add unowned path | authority/gate rejects before mutation |
| Evidence relation | normalized instruction scope | put `files_changed` outside scope | builder/validator rejects |
| Actual change relation | union of tracked unstaged, tracked staged, and untracked repository-relative paths | inject one outside-scope staged file, then one unstaged file, then one untracked file | each pre-publication oracle run rejects; restoring the exact authorized snapshot passes |
| Control-plane route | independent authorization WU, current STATE evidence, review and approval records | mix implementation path; target authority itself; expand scope; stale State; remove review/approval binding | branch rejects each case while the fully bound case passes |

The composed test matrix uses the same production-shaped instruction object for schema PASS, builder round-trip PASS, lifecycle PASS, and governed mutation PASS. It then proves removal of `remediation_decision_ref`, stale finding target, and stale adjudication each fail. For scope it proves owned exact paths pass; missing scope, unowned path, evidence outside scope, and actual Git change outside scope fail. The actual-diff suite injects each of staged, unstaged, and untracked out-of-scope files; each fails before commit/push, and restoring the exact authorized snapshot passes. For control-plane it proves only exact eligible paths plus current revision/review/approval pass; mixed implementation path, unbound STATE/WU transition, expansion, stale revision, and missing correlation fail. The approval suite proves the same `APPROVAL_RESULT` fails at schema, taxonomy, identity/correlation, and authority-gate layers when each binding is removed or changed.

## 17. Failure handling / fail-closed behavior

Malformed path syntax, duplicate or empty scope, missing immutable Work Unit, absent approval evidence, identity mismatch, base/review mismatch, stale State, stale remediation basis, ineligible control-plane path, self-targeting authorization, or any actual out-of-scope change returns an error and performs no mutation. The caller must reconcile and issue a fresh bounded instruction; no implicit retry, path inference, or administrator override exists.

## 18. Expected implementation footprint

Strongly indicated: `.gpt-codex/schemas/instruction-envelope.schema.json`, `.gpt-codex/schemas/result-envelope.schema.json`, `.gpt-codex/scripts/instruction_envelope.py`, `.gpt-codex/scripts/role_communication.py`, `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`, any existing result/template surface, and focused instruction, result-schema/taxonomy, review-lifecycle, self-hosting/control-plane, and validator-context tests. `role_communication.py` is mandatory because `APPROVAL_RESULT` is a result-taxonomy change. No new module is added; other existing tests change only where they prove the composed behavior.

## 19. Acceptance criteria

The implementation is acceptable only when `scope_paths` is the exact authority field; all new mutating instructions require it; ordinary scope originates from immutable Work Unit `owned_paths`; declared and actual changed paths are bounded by it; and a production-shaped FIX carries `remediation_decision_ref` through every layer. Control-plane mutation must identify independent durable authority, exact eligible paths, a complete durable approval result, review correlation, current revision, and self-authorization prevention. The one-time bridge must be externally immutable, user-approved, exact-path bounded, independently pre-execution reviewed, and terminated when repaired native authority is durable. All matrix fault models must demonstrably fail. Plugin remains deferred.

## 20. Explicit deferred work

Deferred: the STATE required-fields repair; publication of the preserved Baseline implementation; Task 3 Plugin; frozen revision-13 checkpoint; any new Framework version/release/activation; and any implementation or Plan until this Design receives GPT review and user approval.

## 21. Required amendment self-review

- **Can current released 2.7.0 actually start this repair?** YES, through the exact one-time migration bridge in section 14; no current-valid native route is claimed.
- **How is the first durable user approval created without already needing native control-plane authority?** `USER_APPROVER` first publishes the immutable, remote bridge authorization object containing the closed approval payload and bound review hash. Native `STATE.evidence_refs` projection happens later, only in the admitted native transition, so the approval does not require itself for creation or durability.
- **Can the chosen approval result pass both Result schema and role/message taxonomy?** YES. The repair makes `APPROVAL_RESULT`, its closed `approved_instruction`, and `USER_APPROVER` responder restriction mandatory in the Result Envelope, `role_communication.py`, validation path, templates where present, and composed tests.
- **Can actual out-of-scope staged, unstaged and untracked files all be detected before publication?** YES. The section 11 oracle unions the staged, unstaged, and untracked Git path sets before commit/push, with an independent failing injection for each and a restored exact-snapshot PASS case.

`DESIGN_BLOCKERS = NONE` for the Design: the one-time bridge is deliberately explicit, bounded, independently reviewed, durably recorded, non-reusable, and expires on durable native repair. Its use does not authorize a Plan or implementation.
