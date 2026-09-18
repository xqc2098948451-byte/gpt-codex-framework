# Group B Prerequisite Contract Reconciliation Design

## 1. Status and authority

**Status:** proposed Design candidate for independent review. It is not accepted Design, not a Work Unit, not an Instruction, and not implementation or migration authority.

**Purpose:** close the prerequisite-contract completeness gap discovered by the Group B B0 re-observation before inherited Contract Repair Tasks 5–9 may execute.

This candidate is subordinate to the current released Framework authority and preserves the accepted staged-closure architecture. It does not overwrite or reinterpret either accepted historical artifact.

Authoritative immutable references:

- staged-closure Design: `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`
- staged-closure Master Plan: `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`
- corrected historical Contract Repair Design: `135f1c06b205894f0e603b0fdbf34cc10ba6e3f6:docs/superpowers/specs/2026-09-17-framework-contract-repair-design.md`
- corrected historical Contract Repair Plan: `7f9c0cf46aee2b6bfdbadc36eb8d6373592d4a55:docs/superpowers/plans/2026-09-17-framework-contract-repair.md`

Current observation base:

- management `main`: `a0b5213959aaf92c9b3f72cd213e9d1264e7f5e6`
- active Group-A artifact/tag target: `b4bc96bcfebad941edf5a5c2ee5368e9e94045a6`
- active Framework version: `2.7.2+fix.1`
- State revision: `15`
- State next action: `GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED`

`2.7.2+fix.1` is treated only as the corrective Group-A active baseline. It does not move the Group-B release boundary: Group B remains `2.7.3`.

## 2. B0 observed finding

The B0 release prerequisite passes: remote branch/release/tag/version/artifact facts and repository State are consistent enough to begin Group-B re-observation.

The B0 interface-remap prerequisite does not pass.

The historical Phase-A checkpoint declared the Baseline Closure Prelude and Contract Repair Tasks 1–4 as the checkpoint foundation for later Tasks 5–9. Fresh inspection of current `main` shows only partial materialization of the accepted Task-2/3/4 contracts.

### Task 2 prerequisite contract

Accepted historical interface:

`build_instruction_envelope(..., scope_paths=None, remediation_decision_ref=None, approval_evidence_ref=None)`

with matching Instruction Envelope schema/template behavior, including the closed external approval-evidence locator shape.

Current observed state:

- `.gpt-codex/scripts/instruction_envelope.py` supports `scope_paths`.
- `.gpt-codex/schemas/instruction-envelope.schema.json` does not declare `scope_paths`.
- the current builder does not expose `remediation_decision_ref`.
- the current builder/schema do not expose `approval_evidence_ref`.
- the current Instruction template does not materialize the historical closed Task-2 contract.
- the current Instruction schema accepts only plain `x.y.z` in `framework_version`, while the active Framework identity is `2.7.2+fix.1`; by contrast, the existing release/Framework validators already use SemVer grammar that supports prerelease/build metadata. A fresh current-authority Instruction therefore cannot be represented faithfully without reconciling this field grammar.

Therefore Task 5 cannot safely treat the historical locator input contract as already closed.

### Task 3 prerequisite contract

Accepted historical interface:

`APPROVAL_RESULT` is an intrinsic Result type authored only by `USER_APPROVER`, carrying the closed approved instruction core, an explicit `APPROVE | REJECT` decision, two-hop correlation, `remote_verification = NOT_ATTEMPTED`, and `completion_evidence = null`.

Current observed state:

- `.gpt-codex/scripts/role_communication.py` recognizes the `APPROVAL_RESULT` taxonomy token.
- `.gpt-codex/schemas/result-envelope.schema.json` does not include `APPROVAL_RESULT` in `result_message_type`.
- the current Result schema does not close the historical `decision` and `approved_instruction` authority-core shape.
- the current generic PASS rules require remote verification/completion evidence in a way that does not yet express the historical intrinsic approval transaction contract.
- current tests preserve only a partial taxonomy/boundary fixture, not the accepted complete production-shaped Result contract.

Therefore Tasks 5 and 7 cannot consume an approval blob under the accepted historical semantics yet.

### Task 4 prerequisite contract

Accepted historical interface:

`scope.owned_paths` is a required, non-empty, unique selector array; `scope.excluded_paths` is optional; scope is closed; selectors are validated repository-relative exact paths or directory prefixes; `validate_instruction_authority` uses selector-aware coverage.

Current observed state:

- `.gpt-codex/scripts/validate_project.py` contains selector-aware requested-scope coverage.
- `.gpt-codex/schemas/work-unit.schema.json` does not close or validate the `scope` object.
- `.gpt-codex/project-template/WORK_UNIT.template.json` still presents an empty `owned_paths` example.
- the historical four-path seed exists, but it is a revision-12 historical artifact and is not reusable at State revision 15.

Therefore Task 7 cannot rely on the immutable Work Unit scope object as a fully schema-closed prerequisite, and Task 8 must still follow its future fresh authority lifecycle rather than replaying the old seed.

## 3. Classification

The finding is `AMENDMENT_REQUIRED` under the staged-closure Master Plan VI.3 because a mechanical B0 remap cannot honestly assert that every inherited authority/evidence prerequisite is already equivalent.

This is a **prerequisite completeness reconciliation**, not a reinterpretation of Tasks 5–9.

The amendment MUST preserve:

```text
TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO
GROUP_B_RELEASE = 2.7.3
PLUGIN_WORK_RESUMED = NO
BRIDGE_005_CREATED_BY_THIS_DESIGN = NO
BRIDGE_004_REUSE = FORBIDDEN
HISTORICAL_DESIGN_REWRITE = NO
HISTORICAL_PLAN_REWRITE = NO
NEW_AUTHORITY_SUBSYSTEM = NO
NEW_FRAMEWORK_MODULE = NO
```

## 4. Goals

1. Materialize the already-accepted historical Task-2 Instruction contract completely across schema, builder, template, and focused tests.
2. Materialize the already-accepted historical Task-3 `APPROVAL_RESULT` contract completely across schema, taxonomy/role validation, template/return surface where applicable, and focused tests.
3. Materialize the already-accepted historical Task-4 Work Unit scope contract completely across schema, template, existing validator coverage, and focused tests.
4. Align Instruction `framework_version` representation with the repository's already-active SemVer release grammar so `2.7.2+fix.1` can be represented without weakening identity checks.
5. Prove that these corrections do not change Group-A execution-reliability behavior.
6. Restore a valid B0 semantic-identity basis so the unchanged B1–B5 work can later receive its own Work Unit, PRE_EXECUTION review, and migration authority.

## 5. Non-goals

This Design does not:

- implement historical Tasks 5–9;
- add `resolve_approval_evidence_locator`;
- add the actual-Git mutation scope oracle;
- compose the native control-plane gate;
- create, prepare, approve, transport, or consume bridge-005;
- create or consume a new native seed;
- change any historical Task-5–9 semantic or acceptance criterion;
- resume Plugin work;
- change Group B from `2.7.3`;
- publish a release;
- modify `main`;
- add a new State, Work Unit model, authority subsystem, review lifecycle, module, database, queue, or daemon.

## 6. Chosen reconciliation architecture

The smallest safe correction is to complete the three historical prerequisite contracts in their existing owners and, as a separately classified current-baseline compatibility reconciliation, align Instruction version representation with the already-active repository SemVer grammar. No parallel compatibility layer is introduced.

### 6.1 Instruction contract completion

Existing owners remain:

- `.gpt-codex/schemas/instruction-envelope.schema.json`
- `.gpt-codex/scripts/instruction_envelope.py`
- `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`
- existing focused Instruction tests

Historical Task-2 residual closure is limited to the already-accepted Task-2 behavior:

- `scope_paths` is a non-empty, unique, safe repository-relative exact path list whenever a governed mutating instruction requires it.
- `remediation_decision_ref` is represented for the existing FIX lifecycle without changing its accepted lifecycle semantics.
- `approval_evidence_ref = {remote_ref, evidence_commit_sha, path, blob_sha}` is allowed only where the accepted mutating control-plane `RECONCILIATION_REQUEST` contract permits it.
- the external locator remains outside the approved authority core.
- malformed, partial, absolute, escaping, duplicate, or semantically ineligible shapes fail closed.
- legacy read-only/history parsing remains compatible; compatibility does not authorize new mutation without the current required fields.

The active-version SemVer issue is not historical Task-2 semantics; it is classified separately in section 6.4.

### 6.2 Approval Result contract completion

Existing owners remain:

- `.gpt-codex/schemas/result-envelope.schema.json`
- `.gpt-codex/scripts/role_communication.py`
- `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`
- `.gpt-codex/scripts/result_return.py` only if required to preserve an already-produced Result field
- existing focused Result/taxonomy tests

Required behavior is exactly the accepted historical Task-3 behavior:

- `result_id` is present as the intrinsic approval-result identity used by the accepted external evidence path.
- `result_message_type = APPROVAL_RESULT`.
- `responder_role = USER_APPROVER`.
- `status = PASS` means the approval transaction was formed correctly; `decision` alone distinguishes `APPROVE` from `REJECT`.
- `response_to_instruction_id` binds the `APPROVAL_REQUEST`.
- `approved_instruction` closes the accepted authority core.
- `evidence_refs = []`, `completion_gate = NONE`, `remote_verification = NOT_ATTEMPTED`, and `completion_evidence = null`.
- the intrinsic payload contains no self-addressing locator/commit/blob field.
- Result-shape validity does not itself prove correlation to the future execution request; exact correlation remains Task-7 responsibility.
- only `USER_APPROVER` authors the result; `USER_LOCAL` remains transport-only.

Any generic PASS/completion rule must be narrowed only enough to represent this already-accepted intrinsic non-execution transaction. Execution Results keep their current completion-evidence requirements.

### 6.3 Work Unit scope contract completion

Existing owners remain:

- `.gpt-codex/schemas/work-unit.schema.json`
- `.gpt-codex/project-template/WORK_UNIT.template.json`
- the current selector-aware path coverage in `.gpt-codex/scripts/validate_project.py`
- existing focused Work Unit/self-hosting/context-binding tests

Required behavior is exactly the accepted historical Task-4 behavior:

- `scope.additionalProperties = false`.
- `scope.owned_paths` is required, non-empty, unique.
- `scope.excluded_paths` is optional and unique.
- a selector is a safe repository-relative exact file path or a safe directory prefix ending in one `/`.
- absolute paths, drive-qualified paths, backslashes, `.`, `..`, empty components, empty strings, malformed suffixes, and duplicate selectors fail closed.
- requested exact paths are covered only by exact selector equality or a valid owned directory prefix.
- durable current Work Units must remain valid; if closing the schema exposes a real incompatible durable Work Unit, implementation stops as `DESIGN_RECONCILIATION_REQUIRED` rather than weakening the grammar.

The historical revision-12 seed remains historical evidence only. This reconciliation does not make it current or reusable.

### 6.4 Current active-version compatibility reconciliation

This subsection is a current B0 compatibility prerequisite, not part of the historical Task-2 semantic definition.

Current owners remain the existing Instruction Envelope version field, its schema validation, and focused Instruction/version tests. The correction reuses the SemVer identity grammar already enforced by current `release_framework.py` and `validate_framework.py`:

- `Instruction.framework_version` must be able to represent the exact active identity `2.7.2+fix.1`.
- valid SemVer prerelease/build metadata is representationally valid; arbitrary non-SemVer strings remain invalid.
- accepting the syntax does not grant authority, select a Framework version, or permit version substitution.
- this reconciliation adds no new version-equality authority gate. Existing project/repository/State/Instruction authority checks remain unchanged; `framework_version` grammar alignment is representational compatibility only.
- if a future task requires a new version-equality authorization rule, that is outside this amendment and requires separate governed authority rather than being inferred from SemVer acceptance.
- no historical Task-2, Task-5–9, release, or authority semantic is reclassified as a result of this compatibility fix.

## 7. Implementation ordering after Design/Plan acceptance

The future Plan amendment must keep the correction serial and bounded:

1. prerequisite P0 observation and exact-path binding;
2. Task-2 contract RED -> minimal GREEN -> sensitivity restoration;
3. independent post-review;
4. Task-3 contract RED -> minimal GREEN -> sensitivity restoration;
5. independent post-review;
6. Task-4 contract RED -> minimal GREEN -> sensitivity restoration;
7. independent post-review;
8. focused cross-contract composition proving the three prerequisites coexist;
9. full Framework/project/consumer validators and `git diff --check`;
10. independent final reconciliation review;
11. only then repeat B0 semantic-identity remap.

No B1–B5 implementation is mixed into this correction.

## 8. Test-effectiveness requirements

The Plan amendment must reuse the historical Task-2/3/4 fault models, not replace them with happy-path-only checks.

Minimum sensitivity matrix:

| Contract | Fault | Required oracle |
| --- | --- | --- |
| Instruction | empty/duplicate/absolute/escaping `scope_paths` | schema/builder reject |
| Instruction | malformed `approval_evidence_ref` | schema/builder reject |
| Instruction | locator on an ineligible instruction | contract rejects |
| Instruction | active `2.7.2+fix.1` framework identity | schema accepts exact valid SemVer identity |
| Instruction | arbitrary malformed/non-SemVer framework identity | schema rejects |
| FIX | missing/stale `remediation_decision_ref` where lifecycle requires it | existing lifecycle/gate rejects |
| Approval Result | missing/invalid `result_id` or wrong responder role | schema/role reject |
| Approval Result | missing/invalid decision or incomplete authority core | schema rejects |
| Approval Result | execution-style completion evidence or remote-verified-at-creation substitution | schema rejects |
| Approval Result | changed but still well-formed approved core | intrinsic schema may pass; future Task-7 exact correlation must reject |
| Work Unit | missing/empty/duplicate/malformed selector | schema rejects |
| Work Unit | uncovered requested path | existing authority comparison rejects |
| Work Unit | valid directory-prefix coverage | existing authority comparison passes |
| Work Unit | historical seed at current revision | remains non-current/non-reusable |

Every sensitivity case must demonstrate FAIL on the injected fault and PASS after exact restoration.

## 9. Group-A regression boundary

The correction must not weaken or replace Group-A v2.7.2+fix.1 reliability behavior.

At minimum, the implementation candidate must rerun the affected adjacent Group-A tests for:

- PRE_EXECUTION review binding;
- Result completion evidence for execution Results;
- continuity/resume;
- Git continuity;
- project validation;
- consumer projection/runtime validation.

Any requirement to alter Group-A semantics, Result execution semantics, release-state semantics, or the staged release boundaries returns `AMENDMENT_REQUIRED` again.

## 10. Authority and migration boundary

This Design candidate cannot authorize its own implementation.

Required lifecycle:

```text
Design candidate
-> independent CODEX_REVIEWER
-> GPT review/adjudication
-> exact candidate USER_APPROVER acceptance
-> immutable accepted Design ref
-> Plan amendment candidate
-> independent Plan review
-> GPT review/adjudication
-> exact Plan USER_APPROVER acceptance
-> immutable accepted Plan ref
-> separate bounded Work Unit + Instruction
-> independent PRE_EXECUTION review
-> implementation
```

Only after the accepted correction is implemented and independently verified may B0 be re-run.

A repeated `B0 = PASS` is a semantic/readiness result only. It is not B1 mutation authority and cannot be converted into an execution permission by inference.

The post-B0 sequence is explicitly:

```text
repeated B0 PASS
-> re-observe current accepted migration-authority requirement
-> if bridge-005/current successor migration authority remains required:
   prepare exact current base + exact scope + exact payload
-> independent PRE_EXECUTION review of that exact migration authority
-> USER_APPROVER exact-payload approval
-> remote immutable verification
-> separate B1 Work Unit / Instruction authority
-> B1
```

If current accepted authority supersedes the bridge-005 identifier with another governed migration mechanism, that substitution itself must be durably accepted before use; B0 cannot choose it informally.

Bridge-005 therefore remains a future separate migration-authority lifecycle under the currently frozen architecture. Nothing in this candidate prepares its payload, scope, review artifact, approval, transport, or remote object.

## 11. Independent review binding

Independent Design review is bound to the cumulative candidate, never merely the last authoring commit.

For each review invocation, the review request must record:

```text
base = exact immutable main/base SHA
candidate = exact immutable PR HEAD SHA
diff = base..candidate
changed_paths = complete cumulative changed-path set
```

For PR #10 at the time review is requested, the cumulative changed-path set must be exactly this Design file. The reviewer evaluates the complete file as it exists at the exact candidate SHA and the complete cumulative diff from base. Reviewing only `HEAD~1..HEAD`, only the most recent patch, or an earlier candidate SHA is insufficient.

Any authoring change after a review target is bound invalidates that target for acceptance. A new exact HEAD must be recorded and independently reviewed again before GPT adjudication or USER_APPROVER acceptance.

## 12. Acceptance criteria

This Design is acceptable only if independent review confirms all of the following:

1. it is a prerequisite reconciliation only;
2. Tasks 5–9 technical semantics are unchanged;
3. Group B remains release `2.7.3`;
4. `2.7.2+fix.1` is treated as the corrective active Group-A baseline, not a new Group;
5. no Plugin work or bridge-005 work begins;
6. the Task-2/3/4 contracts are restored in their existing owners;
7. the Instruction version field can represent the exact active `2.7.2+fix.1` identity using the repository's existing SemVer grammar without broadening authority or adding a new version-equality authorization gate, and this is explicitly classified as current compatibility reconciliation rather than historical Task-2 semantics;
8. independent review binds the complete cumulative `base..candidate` diff at an exact candidate SHA;
9. no new authority/state/review/module subsystem is introduced;
10. historical artifacts are not rewritten;
11. Group-A reliability behavior remains protected by regression tests;
12. repeated B0 PASS does not itself grant B1 mutation authority;
13. B1–B5 remain blocked until this reconciliation is accepted, planned, implemented, reviewed, B0 is repeated successfully, and any still-required migration authority is separately reviewed, exactly approved, and remotely verified.

## 13. Candidate self-review

- Capability-before-Design: PASS; existing owners were inspected before proposing structure.
- Historical semantics preserved: PASS; the candidate quotes the accepted Task-2/3/4 responsibilities and leaves Tasks 5–9 unchanged.
- SemVer classification: PASS; active-version compatibility is explicitly separate from historical Task-2 residual closure and introduces no version-equality authority rule.
- Review binding: PASS; independent review is defined over exact cumulative `base..candidate`, not the last commit only.
- B1 authority boundary: PASS; repeated B0 PASS remains non-authorizing and any required migration authority stays separately gated.
- Minimum structural delta: PASS; all changes stay in existing schema/builder/template/validator/test owners, including reuse of the already-existing Framework SemVer grammar for Instruction version representation.
- New module/state/authority subsystem: NONE.
- Plugin/bridge-005 work: NONE.
- Release-boundary change: NONE.
- Implementation authority granted by this document: NO.
