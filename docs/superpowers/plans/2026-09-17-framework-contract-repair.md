# Framework Contract Repair Implementation Plan

> **For agentic workers:** implementation remains subject to Framework governance, PRE-EXECUTION review, the Accepted Design, and the one-time migration bridge. No task authorizes itself. Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` task-by-task; steps use checkbox syntax for tracking.

**Goal:** Close the proven Framework instruction, remediation, mutation-scope, approval, and control-plane authority defects without adding a subsystem.

**Architecture:** Reuse the Instruction, Result, Work Unit, Git continuity, and governed-mutation contracts. The bridge is a single user-approved bootstrap operation that creates the repair Work Unit and one seed Work Unit; native authority begins only after the exact reviewed repair is integrated, released, activated, and remotely verified.

**Tech Stack:** Python standard library, JSON Schema, Git, unittest, existing Framework validators and release tooling.

**Spec:** `docs/superpowers/specs/2026-09-17-framework-contract-repair-design.md@4bd838b9f79e1d7a56d9408210fbff6193e7d08d`

## Global Constraints

- CURRENT RELEASED AUTHORITY = Framework 2.7.0. Candidate rules are non-authoritative until reviewed, accepted, integrated, released, activated, and remote-verified.
- `scope_paths` is mutation authority; ordinary `scope_paths` is a subset of immutable Work Unit `scope.owned_paths`; `files_changed` is evidence only.
- Preserve `remediation_decision_ref`, FIX freshness, staged/unstaged/untracked pre-COMMIT and pre-PUSH scope checks, historical readability, no eighth module, and one governed entry.
- `APPROVAL_RESULT` uses `status = PASS`, `decision = APPROVE | REJECT`, `completion_gate = NONE`, and non-execution `completion_evidence = null`; status never encodes approval decision.
- Plugin is deferred. `PRESERVED_BASELINE_SOURCE` remains read-only and untouched; `BASELINE_CLOSURE_TARGET` remains exactly three paths and no other Baseline worktree path is admitted. Its manifest target bytes equal preserved-source bytes (`A7CAEC033DAA058877C7C24DD745FF3DCD36B51335C84CD4553C69ABA2DCC195`); its local-corrective target bytes equal preserved-source bytes (`AA5DBB9346E7DBBE47A27D4E300403485029CD00B40CE7A68E49387DA626AE98`); its consumer-projection target bytes are the accepted reconciled `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`, while preserved-source consumer-test bytes remain `E51159943EAC482F39F1C6A23665943AE22AB3228B4EF45BA990A388FDF240CC`. Any target-byte mismatch is `RECONCILIATION_REQUIRED`, never a redesign. `STATE-ORACLE-SCHEMA-REQUIRED-FIELDS-001` remains deferred until repaired native authority is active; Baseline lifecycle closure remains post-activation work.
- `CODEX_IMPLEMENTER` may read, test, validate, report, and mutate only under a future valid instruction; it never commits or pushes. `CODEX_REVIEWER` never mutates. `USER_APPROVER` authors approval semantics. `USER_LOCAL` performs bridge-authorized local mutation plus exact evidence transport and publication operations.
- Every implementation task ends with a reviewable report and a clean scope check; no task includes an implementer commit or push.

## File and interface map

| Responsibility | Files | Interface produced |
| --- | --- | --- |
| Instruction closure | `instruction-envelope.schema.json`, `instruction_envelope.py`, `INSTRUCTION_ENVELOPE.template.json` | `scope_paths`, `remediation_decision_ref`, `approval_evidence_ref` round-trip |
| Result and roles | `result-envelope.schema.json`, `role_communication.py`, `RESULT_ENVELOPE.template.json` | closed `APPROVAL_RESULT` payload and role taxonomy |
| Durable scopes | `work-unit.schema.json`, `validate_project.py` | immutable `target_work_unit_ref -> scope.owned_paths` source |
| Git evidence | `git_continuity.py`, `validate_project.py` | `resolve_approval_evidence_locator(locator) -> Mapping` |
| Governed entry | `validate_project.py` | fail-closed ordinary/FIX/control-plane composition |
| Bridge and seed | two Work Unit JSON files, release source/metadata/artifacts | one non-reusable bootstrap and exact revision-12 seed |
| Baseline release closure | `consumer-projection-manifest.json`, `test_consumer_projection.py`, `test_local_corrective_state.py` | exact content-locked `BASELINE_CLOSURE_TARGET` prerequisite |

## Frozen bridge authority

### BRIDGE_AUTHORIZED_PATHS

The one-time bridge may create or modify only this duplicate-free, repository-relative set; no glob, runtime expansion, or implied test path is valid:

1. `.gpt-codex/schemas/instruction-envelope.schema.json`
2. `.gpt-codex/schemas/result-envelope.schema.json`
3. `.gpt-codex/schemas/work-unit.schema.json`
4. `.gpt-codex/scripts/instruction_envelope.py`
5. `.gpt-codex/scripts/role_communication.py`
6. `.gpt-codex/scripts/result_return.py`
7. `.gpt-codex/scripts/git_continuity.py`
8. `.gpt-codex/scripts/validate_project.py`
9. `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`
10. `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`
11. `.gpt-codex/project-template/WORK_UNIT.template.json`
12. `.gpt-codex/work-units/framework-contract-repair-001.json`
13. `.gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json`
14. `.gpt-codex/tests/test_instruction_envelope.py`
15. `.gpt-codex/tests/test_instruction_role_contract.py`
16. `.gpt-codex/tests/test_result_contract_schema.py`
17. `.gpt-codex/tests/test_role_communication_taxonomy.py`
18. `.gpt-codex/tests/test_result_return.py`
19. `.gpt-codex/tests/test_self_hosting_validator.py`
20. `.gpt-codex/tests/test_validator_context_binding.py`
21. `.gpt-codex/tests/test_git_continuity.py`
22. `.gpt-codex/tests/test_review_lifecycle.py`
23. `.gpt-codex/tests/test_version_consistency.py`
24. `.gpt-codex/tests/test_release_packaging.py`
25. `VERSION`
26. `.gpt-codex/builtins/INDEX.json`
27. `.gpt-codex/CHANGELOG.md`
28. `releases/INDEX.json`
29. `releases/records/v2.7.1.json`
30. `dist/gpt-codex-framework-v2.7.1-bootstrap.zip`
31. `dist/gpt-codex-framework-v2.7.1-bootstrap.zip.sha256`
32. `dist/gpt-codex-framework-v2.7.1-release.json`
33. `dist/gpt-codex-framework-v2.7.0-bootstrap.zip` — `DELETE_ONLY`
34. `dist/gpt-codex-framework-v2.7.0-bootstrap.zip.sha256` — `DELETE_ONLY`
35. `dist/gpt-codex-framework-v2.7.0-release.json` — `DELETE_ONLY`
36. `.gpt-codex/release/consumer-projection-manifest.json`
37. `.gpt-codex/tests/test_consumer_projection.py`
38. `.gpt-codex/tests/test_local_corrective_state.py`

`actual created, modified, or deleted paths ⊆ BRIDGE_AUTHORIZED_PATHS`. `REPLACEMENT_BRIDGE_AUTHORIZED_PATH_COUNT = 38`; `DELETE_ONLY_PATH_COUNT = 3`; `BASELINE_CLOSURE_PATH_COUNT = 3`; no 39th path is authorized. The bridge authorization object carries this exact list and the `DELETE_ONLY` operation restriction. The repair Work Unit owns the applicable implementation, schema, template, test, and release paths; the seed Work Unit owns only its frozen four paths. Post-execution observed path union must equal the bridge object list intersected with paths actually changed, never a path inferred from a task. The 35-path `bridge/framework-contract-repair-001` is historical only: `OLD_BRIDGE_STATUS = SUPERSEDED_BEFORE_CONSUMPTION`; `OLD_BRIDGE_REPLAY = FORBIDDEN`. `framework-contract-repair-bridge-002` is historical predecessor evidence only: `BRIDGE_002_STATUS = SUPERSEDED_AFTER_PARTIAL_LOCAL_EXECUTION`; its partial Tasks 1–3 local execution produced no repair candidate commit, push, publication, or activation, and its bytes are immutable audit/provenance evidence, not bridge-003 completion evidence or replay authority.

### BRIDGE_AUTHORIZATION_OBJECT

`BRIDGE_OBJECT_TYPE = signed annotated Git tag`. `ACCEPTED_AMENDED_DESIGN_SHA = 4bd838b9f79e1d7a56d9408210fbff6193e7d08d`. `REPLACEMENT_BRIDGE_ID = framework-contract-repair-bridge-003`. `REPLACEMENT_BRIDGE_REMOTE_REF = refs/tags/bridge/framework-contract-repair-003`. `FINAL_ACCEPTED_AMENDED_PLAN_SHA = the exact remote Plan candidate SHA that received GPT review PASS and explicit USER_APPROVER approval`. `BRIDGE_OBJECT_TARGET = FINAL_ACCEPTED_AMENDED_PLAN_SHA`. `BRIDGE_OBJECT_IDENTITY = annotated tag object SHA returned by git rev-parse refs/tags/bridge/framework-contract-repair-003^{tag}` after creation; it is not embedded in the canonical payload. `BRIDGE_PAYLOAD_ENCODING = canonical UTF-8 JSON with sorted keys, trailing LF, stored as the annotated tag message`. `BRIDGE_APPROVAL_AUTHOR_ROLE = USER_APPROVER`. `BRIDGE_TAG_CREATOR_ROLE = USER_LOCAL`. `BRIDGE_TAG_PUSH_ROLE = USER_LOCAL`.

The successor bridge binds the fixed `ACCEPTED_AMENDED_DESIGN_SHA`, unresolved `FINAL_ACCEPTED_AMENDED_PLAN_SHA` and new PRE_EXECUTION review hash until their lifecycle gates complete, expected base SHA `a112efcc24c969369224804a6fc1e5961626c05b`, repository id/name, candidate branch `framework-contract-repair-implementation-002`, expected State revision 12, the exact 38-path list, three `DELETE_ONLY` restrictions, and these three `BASELINE_CLOSURE_TARGET` SHA-256 values: manifest `A7CAEC033DAA058877C7C24DD745FF3DCD36B51335C84CD4553C69ABA2DCC195`, consumer test `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`, and local-corrective test `AA5DBB9346E7DBBE47A27D4E300403485029CD00B40CE7A68E49387DA626AE98`; it also binds role bindings, signing requirements, release version `2.7.1`, seed contract, one-time semantics, and `repair_candidate_commit_limit = 1`. CODEX_REVIEWER independently reviews that frozen core, emits a new PRE_EXECUTION review artifact, reports its SHA-256, and is limited to read, test, validate, and report; it does not create, bind, form, finalize, authorize, or mutate the bridge approval payload. GPT_ORCHESTRATOR forms the new canonical UTF-8 approval payload, does not approve it, and performs no Git mutation. USER_APPROVER approves or rejects those exact canonical bytes and performs no Git mutation. USER_LOCAL verifies bytes unchanged, signing-key fingerprint `SHA256:0ImsetedRxfosXnnsRUP4bKncRJi6ccR/oARZzfv2KM`, and remote absence of `refs/tags/bridge/framework-contract-repair-003` before creation. bridge-002 review/payload evidence is predecessor history and cannot satisfy this gate.

USER_LOCAL must prove real signing, not merely configuration: it verifies the approved dedicated SSH signing identity fingerprint, performs an isolated disposable signed-tag probe in a temporary Git repository, and verifies that probe with `git verify-tag`. If the probe cannot be completed, actual replacement-tag signing failure returns `RECONCILIATION_REQUIRED` before bridge mutation. There is no unsigned fallback. After USER_APPROVER approval, USER_LOCAL verifies the exact bytes are unchanged, creates the signed annotated tag targeting `FINAL_ACCEPTED_AMENDED_PLAN_SHA`, pushes only `git push origin refs/tags/bridge/framework-contract-repair-003` (never `--force` or `--force-with-lease`), and verifies remote tag object SHA, peeled target, canonical payload hash, and new review-artifact hash. The peeled target must equal `FINAL_ACCEPTED_AMENDED_PLAN_SHA`. A preexisting ref, SHA mismatch, replacement, replay after consumption, or any target mismatch returns `RECONCILIATION_REQUIRED`. Consumption is recorded by the exact accepted remote repair SHA; expiry occurs only after remote active-authority verification, and the replacement tag cannot authorize a second mutation while pending.

### Pre-activation actor rule

Before `REMOTE_ACTIVE_AUTHORITY_VERIFICATION = PASS`, every repository mutation in the Baseline Closure Prelude and Tasks 1–10 has actor `USER_LOCAL_APPLY`. In every RED→GREEN cycle, `[CODEX_PREPARE]` writes the bounded failing-test/edit expectation and runs read-only RED observation; `[USER_LOCAL_APPLY]` makes the failing-fixture or minimal implementation mutation; `[CODEX_VERIFY]` runs and reports the focused GREEN or sensitivity observation. Non-TDD cycles use the same explicit PREPARE/APPLY/VERIFY order. `CODEX_PREPARE` is read/test/report only and `CODEX_VERIFY` is read/test/validate/report only. CODEX_IMPLEMENTER has zero governed-worktree mutation, commit, push, tag, or release steps before activation; before activation its mutation, commit, and push count is exactly zero. CODEX_REVIEWER is read/test/validate/report only. USER_APPROVER authors approval semantics only. After remote active-authority verification, repaired native authority may authorize CODEX_IMPLEMENTER mutation under a new valid instruction.

## Baseline Closure Prelude

**Lifecycle:** `REPLACEMENT_BRIDGE_AUTHORIZED -> BASELINE_CLOSURE_SNAPSHOT_APPLY -> BASELINE_CLOSURE_FOCUSED_VERIFY -> CLEAN_BASELINE_FULL_VERIFY -> Task 1`.

**Files:** Only `.gpt-codex/release/consumer-projection-manifest.json`, `.gpt-codex/tests/test_consumer_projection.py`, and `.gpt-codex/tests/test_local_corrective_state.py`.

- [ ] [CODEX_PREPARE] Verify clean `framework-contract-repair-implementation-002` is at exact base `a112efcc24c969369224804a6fc1e5961626c05b`; preserve dirty `framework-contract-repair-implementation-001` unchanged as bridge-002 audit evidence and do not copy, stage, commit, or count any of its bytes. Verify the preserved Baseline source worktree is unchanged and recompute all three historical source hashes. Reconstruct the canonical reconciled consumer test in `%TEMP%` and require SHA-256 `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`; calculate the exact three `BASELINE_CLOSURE_TARGET` paths; perform no repository mutation.
- [ ] [USER_LOCAL_APPLY] Copy manifest bytes and local-corrective-test bytes exactly from `PRESERVED_BASELINE_SOURCE` into `framework-contract-repair-implementation-002`; materialize the accepted canonical reconciled consumer-test bytes; make no manual normalization, reformatting, equivalent-content substitution, or commit. Verify the three `BASELINE_CLOSURE_TARGET` hashes exactly: manifest `A7CAEC033DAA058877C7C24DD745FF3DCD36B51335C84CD4553C69ABA2DCC195`, consumer test `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`, local-corrective test `AA5DBB9346E7DBBE47A27D4E300403485029CD00B40CE7A68E49387DA626AE98`. Verify only those three paths changed.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_consumer_projection.py" -v`, `python -m unittest discover -s .gpt-codex/tests -p "test_local_corrective_state.py" -v`, `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, and `git diff --check`; require PASS. The sensitivity oracle derives `durable_work_units` as the exact repository-relative `*.json` files under `.gpt-codex/work-units/` in the candidate snapshot: normal projection classifies every member `MANAGEMENT_ONLY` and excludes it from consumer inventory; removing the projection prefix makes observed unknown Work Unit paths equal that exact set; restoring the prefix returns PASS. No historical Work Unit count is authority. Verify `git diff --name-only` equals exactly the three Prelude paths.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_*.py"`, `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, and `git diff --check`; require complete output with known test count, zero failures/errors, and all validators PASS. A timeout or truncated output is `INCOMPLETE`, not PASS; use a method that lets the started local process complete and collect its full output. A reproducible failure after exact snapshot application is `RECONCILIATION_REQUIRED`; do not begin Task 1.

## Task 1: Freeze bridge authorization and operational boundaries

**Files:** Create `.gpt-codex/work-units/framework-contract-repair-001.json` and `.gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json`; modify only the exact bridge allowlist files declared by the bridge authorization, including release surfaces for `2.7.1`.

**Interfaces:** The bridge authorization object is an immutable remote signed tag/object containing `bridge_id`, repository id/name, base SHA, candidate branch, pre-execution review SHA-256, a closed approved authority core, exhaustive path list, `one_time: true`, and expiry. The seed has `work_unit_id = framework-baseline-checkpoint-control-plane-001`, `basis_state_revision = 12`, `state = AUTHORIZED`, and the four frozen paths from Task 8.

**Preconditions:** `framework-contract-repair-bridge-003` is authorized; `BASELINE_CLOSURE_SNAPSHOT_APPLY = PASS`; `BASELINE_CLOSURE_FOCUSED_VERIFY = PASS`; `CLEAN_BASELINE_FULL_VERIFY = PASS`; `framework-contract-repair-implementation-002` is the bridge-bound candidate branch at the clean base plus only the three Prelude paths; Accepted amended Plan is frozen at an exact SHA; USER_APPROVER has explicitly approved the replacement bridge object; CODEX_REVIEWER has independently reviewed the base-SHA candidate; `git status --short` contains only the three Prelude paths before the first RED fixture mutation.

- [ ] [CODEX_PREPARE] Define the absent-id, missing-Baseline-path, Plugin-path, 39th-arbitrary-path, and non-immutable replacement-bridge fixture RED expectation.
- [ ] [USER_LOCAL_APPLY] Write those failing fixtures in `.gpt-codex/tests/test_self_hosting_validator.py`.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v`; record the expected RED bridge-fixture failures.
- [ ] [CODEX_PREPARE] Bound the two Work Unit fixtures and validator inputs required by the bridge contract; the repair Work Unit remains bridge output, never authority source.
- [ ] [USER_LOCAL_APPLY] Add those two Work Unit fixtures and minimal validator inputs.
- [ ] [CODEX_VERIFY] Run the focused command; expect the exact 38-path replacement bridge PASS and each malformed bridge fixture FAIL.
- [ ] [CODEX_PREPARE] Define sensitivity cases for one missing Baseline closure path, one Plugin path, and one 39th arbitrary path, with exact-list restoration.
- [ ] [USER_LOCAL_APPLY] Independently remove one Baseline closure path, add `plugins/gpt-codex-framework/`, and add one arbitrary 39th path, restoring the exact 38-path list after each case.
- [ ] [CODEX_VERIFY] Record rejection for every altered list and PASS after restoration.

**Completion evidence:** bridge id, immutable object id, bound review hash, exact path list, and test output. **Handoff:** USER_LOCAL retains the only bridge execution/publishing authority; no CODEX commit or push.

## Task 2: Close the instruction-envelope contract with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/instruction-envelope.schema.json`, `.gpt-codex/scripts/instruction_envelope.py`, `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`; test `.gpt-codex/tests/test_instruction_envelope.py` and `.gpt-codex/tests/test_instruction_role_contract.py`.

**Interfaces:** `build_instruction_envelope(..., scope_paths: list[str] | None = None, remediation_decision_ref: str | None = None, approval_evidence_ref: dict[str, str] | None = None) -> dict`; `approval_evidence_ref` is permitted only on a mutating control-plane `RECONCILIATION_REQUEST` and is not part of the approved authority core.

**Preconditions:** Task 1 bridge path list includes these three files and named tests.

- [ ] [CODEX_PREPARE] Define parameterized RED cases for missing, empty, malformed, duplicate, or absolute/`..` `scope_paths`, plus production FIX and closed locator shapes.
- [ ] [USER_LOCAL_APPLY] Add those failing tests.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_role_contract.py" -v`; record expected schema/builder RED failures.
- [ ] [CODEX_PREPARE] Bound schema, builder, and template changes for the three fields.
- [ ] [USER_LOCAL_APPLY] Add the minimal schema conditions, builder validation/rendering, and template placeholders.
- [ ] [CODEX_VERIFY] Run the same command; expect all valid shapes PASS and every malformed shape FAIL.
- [ ] [CODEX_PREPARE] Define the two sensitivity substitutions and restoration.
- [ ] [USER_LOCAL_APPLY] Remove only `remediation_decision_ref` and replace one locator blob SHA with a non-SHA, then restore both.
- [ ] [CODEX_VERIFY] Record both failures and restored PASS.

**Completion evidence:** focused command output plus serialized template/render examples. **Handoff:** Task 3 consumes the production-shaped instruction and locator.

## Task 3: Define APPROVAL_RESULT and role taxonomy with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/result-envelope.schema.json`, `.gpt-codex/scripts/role_communication.py`, `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`, and `.gpt-codex/scripts/result_return.py`; test `.gpt-codex/tests/test_result_contract_schema.py`, `.gpt-codex/tests/test_role_communication_taxonomy.py`, and `.gpt-codex/tests/test_result_return.py`.

**Interfaces:** `APPROVAL_RESULT` intrinsic payload contains `result_id`, `responder_role = USER_APPROVER`, `status = PASS`, `decision`, `response_to_instruction_id`, closed `approved_instruction`, `evidence_refs = []`, `completion_gate = NONE`, `remote_verification = NOT_ATTEMPTED`, and `completion_evidence = null`. `validate_result_message_type("APPROVAL_RESULT")` recognizes it; only USER_APPROVER can author it.

**Preconditions:** Task 2 supplies a production-shaped approval request and authority core.

- [ ] [CODEX_PREPARE] Define RED schema/taxonomy cases for every listed invalid approval shape and transport field.
- [ ] [USER_LOCAL_APPLY] Add those failing schema/taxonomy tests.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_role_communication_taxonomy.py" -v`; record expected RED failures.
- [ ] [CODEX_PREPARE] Bound result type, closed decision/core, PASS exception, null evidence, and role enforcement changes.
- [ ] [USER_LOCAL_APPLY] Add the minimal result/taxonomy implementation.
- [ ] [CODEX_VERIFY] Run the focused command; expect intrinsic APPROVE and REJECT PASS and every invalid variation FAIL.
- [ ] [CODEX_PREPARE] Define an intrinsic-payload boundary fixture by changing `approved_instruction.scope_paths` to a different still-well-formed, non-empty selector array while preserving every Result-envelope shape requirement. This change is intentionally not an intrinsic schema/taxonomy error; request correlation belongs to Task 7.
- [ ] [USER_LOCAL_APPLY] Add the Task-3 schema/taxonomy fixture proving that the changed-but-well-formed `approved_instruction` remains intrinsically valid. Do not compare it to an execution request in Task 3.
- [ ] [CODEX_VERIFY] Run the focused Task-3 command; require the changed-but-well-formed payload to remain schema/taxonomy PASS, and preserve the fixture shape for Task-7 correlation sensitivity.

**Completion evidence:** schema validation results and role-taxonomy results. **Handoff:** Task 5 resolves the payload bytes, Task 7 validates its correlation.

## Task 4: Close Work Unit owned-path shape with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/work-unit.schema.json`, `.gpt-codex/scripts/validate_project.py`, and `.gpt-codex/project-template/WORK_UNIT.template.json`; test `.gpt-codex/tests/test_self_hosting_validator.py` and `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `scope.additionalProperties = false`; `scope.owned_paths` is required and is a non-empty, unique selector array; `scope.excluded_paths` is optional and a unique selector array. A selector is either an exact relative file path or a relative directory prefix ending in exactly one `/`. Reject absolute paths, drive-qualified paths, backslashes, `.` components, `..` components, empty components, and empty strings. `validate_instruction_authority` remains the authority entry for ordinary requested scope. When immutable `approved_scope` contains Work Unit selectors, each requested exact `scope_paths` entry is covered only if it equals an exact owned selector or starts with an owned directory-prefix selector ending in `/`; raw set membership alone is insufficient. This extends the existing authority comparison and does not create a second authority or permission system. `CONTROL_PLANE_APPROVED_SCOPE_SOURCE = target_work_unit_ref resolved at immutable Git SHA -> scope.owned_paths`. Existing Baseline and Task-3 Work Units remain valid compatibility fixtures: their `owned_paths` and `excluded_paths` shapes are preserved. The template changes to a non-empty owned-path example and preserves `excluded_paths`.

**Preconditions:** Task 1 fixture provides both bridge-created Work Units.

- [ ] [CODEX_PREPARE] Define RED fixtures for missing/empty/duplicate owned selectors; absolute, drive, backslash, `.`, `..`, and empty-component selectors; unexpected `scope` property; invalid directory suffix; and uncovered paths.
- [ ] [USER_LOCAL_APPLY] Add those failing fixtures to exactly `.gpt-codex/tests/test_self_hosting_validator.py` and `.gpt-codex/tests/test_validator_context_binding.py`.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v`; record that the currently open schema admits at least one invalid fixture.
- [ ] [CODEX_PREPARE] Bound the closed `scope` grammar and non-empty template example without changing durable Work Unit shapes; if this grammar proves incompatible with either durable fixture, stop with `DESIGN_RECONCILIATION_REQUIRED`.
- [ ] [USER_LOCAL_APPLY] Close the Work Unit `scope` schema and selector grammar; update the existing `validate_instruction_authority` path in `validate_project.py` with the minimal selector-aware approved-scope coverage rule; update `WORK_UNIT.template.json` with a non-empty `owned_paths` example while preserving `excluded_paths`.
- [ ] [CODEX_VERIFY] Run the focused command; expect malformed Work Units FAIL, ordinary/seed and existing Baseline/Task-3 Work Units PASS, `plugins/gpt-codex-framework/subpath.py` covered by `plugins/gpt-codex-framework/`, and `plugins/other/file.py` uncovered. Verify the seed owns exactly four file selectors, with no prefixes.
- [ ] [CODEX_PREPARE] Define fifth-seed-path sensitivity and restoration.
- [ ] [USER_LOCAL_APPLY] Append a fifth path to the seed fixture, then remove it.
- [ ] [CODEX_VERIFY] Record failure then restored PASS.

**Completion evidence:** validated seed JSON and test output. **Handoff:** Task 7 derives all native control-plane scope from this field.

## Task 5: Add external approval-evidence locator verification with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/git_continuity.py` and `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_git_continuity.py`, `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `resolve_approval_evidence_locator(repository_root: Path, locator: Mapping[str, str]) -> tuple[Mapping[str, object] | None, list[str]]` resolves `evidence_commit_sha:path`, computes the blob SHA, verifies remote reachability of the exact object, and returns `APPROVAL_EVIDENCE_*` errors without accepting a mutable ref head.

**Preconditions:** Task 3 fixed payload and Task 2 closed locator shape.

- [ ] [CODEX_PREPARE] Define RED Git cases for wrong commit, wrong blob, unreachable object, mutable-ref substitution, changed approval bytes, and byte-identical USER_LOCAL transport.
- [ ] [USER_LOCAL_APPLY] Add those failing monkeypatched Git tests.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_git_continuity.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v`; record missing-resolver RED failures.
- [ ] [CODEX_PREPARE] Bound exact-show, blob, fixed-SHA, and remote reachability checks without mutable-head authority.
- [ ] [USER_LOCAL_APPLY] Implement those minimal resolver checks.
- [ ] [CODEX_VERIFY] Run the focused command; expect every substitution fault FAIL and byte-identical transport PASS.
- [ ] [CODEX_PREPARE] Define mutable-ref substitution sensitivity and restoration.
- [ ] [USER_LOCAL_APPLY] Supply the current mutable ref with a different commit, then restore the bound commit.
- [ ] [CODEX_VERIFY] Record failure then PASS.

**Completion evidence:** locator tuple, returned error codes, and test output. **Handoff:** Task 7 calls the resolver before admitting control-plane mutation.

## Task 6: Enforce actual Git mutation scope with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_validator_context_binding.py` and `.gpt-codex/tests/test_self_hosting_validator.py`.

**Interfaces:** an internal changed-path oracle unions `git diff --name-only -z`, `git diff --cached --name-only -z`, and `git ls-files --others --exclude-standard -z`; before push it also reads the committed candidate path set. `validate_instruction_authority` and `validate_governed_mutation_entry` reject any path outside exact scope.

**Preconditions:** Task 2 and Task 4 are green.

- [ ] [CODEX_PREPARE] Define RED temporary-repository cases for outside-scope unstaged, staged, and untracked paths.
- [ ] [USER_LOCAL_APPLY] Add those failing tests while HEAD remains baseline.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v`; record expected untracked-path escape RED behavior.
- [ ] [CODEX_PREPARE] Bound NUL collection, normalization, union, subset, evidence, and committed-path checks.
- [ ] [USER_LOCAL_APPLY] Implement those minimal oracle checks.
- [ ] [CODEX_VERIFY] Run the focused command; expect each injected class FAIL and restored exact snapshot PASS.
- [ ] [CODEX_PREPARE] Define staged-output regression sensitivity.
- [ ] [USER_LOCAL_APPLY] Replace `git diff --cached --name-only -z` with empty mocked output while a staged file exists, then restore it.
- [ ] [CODEX_VERIFY] Record regression detection.

**Completion evidence:** each Git command result and fault matrix. **Handoff:** Task 7 uses this shared oracle for ordinary, FIX, and control-plane paths.

## Task 7: Compose the native control-plane authority gate with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_review_lifecycle.py`, `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `validate_governed_mutation_entry(...)` distinguishes ordinary Work Unit mutation, FIX remediation, and mutating `RECONCILIATION_REQUEST` while retaining one entry. The control-plane branch requires project/repository identity, immutable authorization Work Unit, matching basis State revision, exact scope equality for seed use, PRE_EXECUTION review, external locator resolution, two-hop approval correlation, self-authorization prevention, and Task 6 actual-path enforcement.

**Preconditions:** Tasks 2–6 are green and the current State revision is supplied by fixture, not changed on disk.

- [ ] [CODEX_PREPARE] Define RED composed fixtures for each listed locator, correlation, Work Unit, State, scope, and review fault.
- [ ] [USER_LOCAL_APPLY] Add those failing composed fixtures.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v`, `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py" -v`, and `python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v`; record missing-composition RED failures.
- [ ] [CODEX_PREPARE] Bound reconciliation branch/error codes and approved-core-only comparison.
- [ ] [USER_LOCAL_APPLY] Add the minimal dedicated reconciliation branch and error codes.
- [ ] [CODEX_VERIFY] Run the focused command; expect production-shaped chain PASS and every fault fixture FAIL.
- [ ] [CODEX_PREPARE] Define approved-core correlation sensitivity using the production-shaped valid chain: change only `APPROVAL_RESULT.approved_instruction.scope_paths` after approval while leaving the actual `RECONCILIATION_REQUEST` authority core unchanged; define exact restoration.
- [ ] [USER_LOCAL_APPLY] Apply that mutation only to the composed Task-7 fixture, then restore the exact approved core.
- [ ] [CODEX_VERIFY] Run the focused Task-7 command; require the mutated approved core to fail exact correlation and the restored chain to PASS.
- [ ] [CODEX_PREPARE] Define missing-locator sensitivity and restoration.
- [ ] [USER_LOCAL_APPLY] Remove only `approval_evidence_ref` from the valid request, then restore it.
- [ ] [CODEX_VERIFY] Record failure then PASS.

**Completion evidence:** single-chain fixture JSON and complete error matrix. **Handoff:** Task 8 supplies the first seed; Task 9 performs end-to-end composed tests.

## Task 8: Materialize and constrain the first native seed

**Files:** Create `.gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json`; test `.gpt-codex/tests/test_self_hosting_validator.py`.

**Interfaces:** seed `scope.owned_paths` equals exactly: `.gpt-codex/STATE.json`; `.gpt-codex/work-units/framework-baseline-stabilization-001.json`; `.gpt-codex/evidence/results/RESULT-BASELINE-STABILIZATION-POSTEXEC-FINDING.json`; `.gpt-codex/evidence/results/RESULT-FIX-REMEDIATION-LIFECYCLE-CONTRACT-RECONCILIATION.json`. Its own path is excluded. It is invalid after State revision 12.

**Preconditions:** Tasks 4 and 7 are green; bridge authorization contains this exact file and four-path list.

- [ ] [CODEX_PREPARE] Define RED seed fixtures for missing/replaced/fifth/self-owned paths and revision-13 reuse.
- [ ] [USER_LOCAL_APPLY] Add those failing fixtures.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v`; record expected absent-seed and invalid-shape RED failures.
- [ ] [CODEX_PREPARE] Bound the closed seed and revision-12-only control-plane enforcement.
- [ ] [USER_LOCAL_APPLY] Create the closed seed Work Unit and minimal enforcement.
- [ ] [CODEX_VERIFY] Run the focused command; expect exact seed PASS and all five faults FAIL.
- [ ] [CODEX_PREPARE] Define result-path swap sensitivity and restoration.
- [ ] [USER_LOCAL_APPLY] Swap the two result paths in a fixture, then restore the frozen list.
- [ ] [CODEX_VERIFY] Record rejection then PASS.

**Completion evidence:** immutable Work Unit ref, four-path list, revision-12 fixture output. **Handoff:** Task 9 consumes this seed once.

## Task 9: Prove production-shaped composed lifecycles

**Files:** Modify `.gpt-codex/tests/test_review_lifecycle.py`, `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_validator_context_binding.py`; modify validators only if a composed test exposes a missing Task 2–8 interface.

**Interfaces:** production FIX flow is `schema -> builder -> role/instruction validation -> review lifecycle -> governed entry`; control-plane flow is `instruction schema -> immutable scope -> PRE_EXECUTION review -> locator -> APPROVAL_RESULT -> authority gate -> actual-Git scope`.

**Preconditions:** Tasks 2–8 focused suites are green.

- [ ] [CODEX_PREPARE] Define RED composed cases for each listed single-field fault.
- [ ] [USER_LOCAL_APPLY] Add those red composed tests.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py" -v`, `python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v`, and `python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v`; record targeted RED failures before composition fixes connect.
- [ ] [CODEX_PREPARE] Bound only missing calls among existing builders, validators, resolver, and governed entry.
- [ ] [USER_LOCAL_APPLY] Wire only those missing calls.
- [ ] [CODEX_VERIFY] Run the same command; expect each valid production chain PASS.
- [ ] [CODEX_PREPARE] Define independent-fault sensitivity/restoration observations.
- [ ] [USER_LOCAL_APPLY] Inject each listed fault independently, then restore the exact fixture.
- [ ] [CODEX_VERIFY] Record FAIL then PASS for each, labeled sensitivity rather than original RED.

**Completion evidence:** fixture identifiers, failure codes, restored PASS output. **Handoff:** Task 10 runs framework-wide verification.

## Task 10: Close release candidate at version 2.7.1 before final review

**Files:** Modify `VERSION`, `.gpt-codex/builtins/INDEX.json`, `.gpt-codex/CHANGELOG.md`, `releases/INDEX.json`, `releases/records/v2.7.1.json`; create current `dist/gpt-codex-framework-v2.7.1-bootstrap.zip`, `.sha256`, and `-release.json`; delete only `dist/gpt-codex-framework-v2.7.0-bootstrap.zip`, `.sha256`, and `-release.json`; test `.gpt-codex/tests/test_version_consistency.py`, `.gpt-codex/tests/test_release_packaging.py`.

**Interfaces:** `VERSION = 2.7.1`; `v2.7.1` is the immutable tag name; `FRAMEWORK_ACTIVE_SHA` is its target and must equal final reviewed `main` SHA. Existing `release_framework.py` consumes `VERSION` and produces the canonical artifact and sidecars.

**Preconditions:** Baseline Closure Prelude is green; Tasks 2–9 pass; SemVer history shows current `VERSION = 2.7.0`, so 2.7.1 is the minimal patch release; all source, metadata, and generated artifact paths are within the replacement bridge allowlist before post-execution review. `release_framework.py` consumes the already-corrected consumer-projection state in this same uncommitted final candidate; no separate Baseline commit is authorized.

- [ ] [CODEX_PREPARE] Define RED version/release cases for missing `2.7.1` index, changelog, record, artifact metadata, retained v2.7.0 current outputs, and missing v2.7.1 outputs.
- [ ] [USER_LOCAL_APPLY] Add those failing version-consistency and release-packaging assertions.
- [ ] [CODEX_VERIFY] Run `python -m unittest discover -s .gpt-codex/tests -p "test_version_consistency.py" -v` and `python -m unittest discover -s .gpt-codex/tests -p "test_release_packaging.py" -v`; record expected RED failures until every version surface agrees.
- [ ] [CODEX_PREPARE] Bound the 2.7.1 source/metadata update, exactly three canonical v2.7.1 output creations, and exactly three `DELETE_ONLY` v2.7.0 output deletions.
- [ ] [USER_LOCAL_APPLY] Set source values to `2.7.1`, run `python .gpt-codex/scripts/release_framework.py`, retain only the three canonical v2.7.1 outputs, and delete only the three listed v2.7.0 outputs.
- [ ] [CODEX_VERIFY] Run the focused command; expect release source/metadata/ZIP/hash PASS and the changed-path oracle to include all three creations and all three deletions.
- [ ] [CODEX_PREPARE] Define release-hygiene sensitivity cases for a retained old output, a missing new output, and an unauthorized deletion.
- [ ] [USER_LOCAL_APPLY] Independently introduce each hygiene fault in fixtures, then restore the exact output set.
- [ ] [CODEX_VERIFY] Record FAIL for every hygiene fault and restored PASS.

**Completion evidence:** release command output, artifact SHA-256/size, version-consistency output. **Handoff:** independent post-execution review receives the final candidate with every tracked activation file already included.

## Task 11: Perform final verification and review gates

**Files:** No new source files beyond Task 1–10 scope; test all `.gpt-codex/tests/test_*.py` and existing validators.

**Interfaces:** final candidate facts include exact `BASELINE_CLOSURE_TARGET` bytes + Contract Repair Tasks 1–10 + 2.7.1 release surfaces, exact base SHA, authorized changed paths, full test count discovered from complete command output, zero failures/errors, validator outputs, unchanged Plugin candidate hashes, manifest/local-corrective target hashes equal their preserved-source hashes, reconciled consumer-test target hash equal `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`, and preserved-source Baseline worktree hashes byte-identical to its before snapshot.

**Preconditions:** Task 10 green; USER_LOCAL has not committed or pushed; bridge allows no second implementation commit.

- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'`; expect exit 0 and record actual test count, failures 0, errors 0.
- [ ] Run `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, and `git diff --check`; expect each exit 0.
- [ ] Run the Task 6 path oracle and `git diff --name-only`; expect every changed path to be in the bridge allowlist.
- [ ] Run hashes for the implementation-002 three-file `BASELINE_CLOSURE_TARGET`: require manifest and local-corrective target equality to their preserved-source bytes, reconciled consumer-test target equality to `BD69FF61E50ED4E3818A2F61BA49C6AC9790192D8E94B1DCCA747F50AF34A2DF`, and preserved-source consumer-test equality to `E51159943EAC482F39F1C6A23665943AE22AB3228B4EF45BA990A388FDF240CC`; independently run hashes for the preserved source Baseline three-file snapshot and Task-3 Plugin candidate before/after the task, expecting byte-identical source/preserved values.
- [ ] Sensitivity proof: use an isolated test fixture to add an unauthorized untracked file; expect the path oracle FAIL; remove it and expect PASS.

**Completion evidence:** full-suite counts, validator logs, exact changed-path list, preservation hashes. **Handoff:** CODEX_REVIEWER conducts independent POST_EXECUTION review; no commit or push by CODEX_IMPLEMENTER.

## USER_LOCAL publication and activation operations

**Files:** No implementation change is authorized here; this is a separate human-controlled operation after independent post-execution review and explicit user acceptance.

**Preconditions:** exact candidate SHA has passed Task 11, exact-SHA independent review is PASS, and the user accepts that reviewed SHA.

- [ ] Fast-forward `main` to the exact reviewed SHA; reject merge commits, another SHA, rebase, or force push.
- [ ] Create immutable `v2.7.1` at that exact `main` SHA; publish the already-reviewed canonical 2.7.1 release artifact through the existing release contract.
- [ ] Verify `FINAL_REVIEWED_SHA = main head = v2.7.1 tag target = FRAMEWORK_ACTIVE_SHA` with remote observations.
- [ ] Mark the bridge terminated only after this remote active-authority verification; it cannot authorize another mutation while pending review, acceptance, or activation.
- [ ] Execute the one-time revision-12 seed checkpoint, then return to the blocked Baseline Work Unit, issue fresh State Oracle REVIEW_FINDING/basis/adjudication, and issue the State Oracle FIX under repaired native authority.

**Completion evidence:** remote refs, tag target, release asset facts, bridge termination record, seed-consumption result. **Handoff:** Plugin remains deferred.

## USER_LOCAL post-activation approval evidence transport

`refs/heads/gpt-codex-approval-evidence` is protected operationally by the fail-closed Git-continuity rule: USER_LOCAL observes its exact remote head before writing, every non-initial evidence commit must descend from that observed head, push is fast-forward only, and any non-fast-forward, force, force-with-lease, missing remote object, or ancestry mismatch returns `RECONCILIATION_REQUIRED`. Its mutable head is discovery/reachability only and never authority.

1. USER_APPROVER emits canonical immutable `APPROVAL_RESULT` bytes.
2. USER_LOCAL receives the bytes and verifies their SHA-256 before and after storage; any byte change fails.
3. USER_LOCAL fetches and observes `refs/heads/gpt-codex-approval-evidence`.
4. On first transport, USER_LOCAL creates an orphan evidence commit containing only `approvals/<result_id>.json`, records its commit SHA, and pushes without force.
5. On each subsequent transport, USER_LOCAL creates the evidence commit with the verified current evidence commit as parent.
6. USER_LOCAL pushes with `git push origin HEAD:refs/heads/gpt-codex-approval-evidence`; no force option is permitted.
7. USER_LOCAL re-observes the exact remote ref, verifies pushed-commit reachability, resolves `git show <commit>:approvals/<result_id>.json`, computes blob SHA and payload SHA-256, and compares them to the original bytes.
8. USER_LOCAL returns `approval_evidence_ref = {remote_ref, evidence_commit_sha, path, blob_sha}`.
9. GPT_ORCHESTRATOR may insert only that locator into the `RECONCILIATION_REQUEST`; it cannot alter the closed approved authority core.

Sensitivity fixtures cover non-fast-forward update, force-update attempt, ref advance after locator issuance where the old bound tuple remains valid, and a different blob at the same path on a newer ref that cannot substitute authority.

## Lifecycle checkpoints

Amended Design accepted -> amended Plan draft -> remote amended Plan review candidate -> GPT exact-SHA Plan review -> user amended Plan approval -> replacement bridge preparation -> new independent PRE_EXECUTION review -> USER_APPROVER approval of new exact payload -> remote replacement bridge verification -> REPLACEMENT_BRIDGE_AUTHORIZED -> Baseline Closure Prelude -> Tasks 1–10 -> task verification -> composed final verification -> independent POST_EXECUTION review -> one integrated remote repair candidate -> independent exact-SHA review -> user acceptance -> exact main fast-forward -> 2.7.1 tag/publication -> remote active-authority verification -> replacement bridge terminated -> first native Baseline control-plane checkpoint -> blocked Baseline Work Unit -> fresh State Oracle REVIEW_FINDING -> fresh basis/adjudication -> State Oracle FIX.

## Plan self-review

### Spec coverage

| Accepted Design sections | Plan coverage |
| --- | --- |
| 1–4 | Global Constraints; Tasks 1, 10, 11 |
| 5–8 | Tasks 1, 2, 4, 7 |
| 9–12 | Tasks 2, 3, 5, 6, 7 |
| 13 | Tasks 2 and 9 |
| 14.1–14.4 | Tasks 1, 8, 10, 11 and USER_LOCAL operations |
| 15 | Tasks 2, 3, 4 and 7 |
| 16–19 | Tasks 3, 5, 6, 7, 8, 9, 11 |
| 20 | Global Constraints and Lifecycle checkpoints |
| 21 | Tasks 1, 3, 5, 8, 10 and USER_LOCAL operations |

All 21 sections have at least one implementation or operational checkpoint.

### Interface consistency

The plan uses `scope_paths`, `remediation_decision_ref`, `approval_evidence_ref`, `APPROVAL_RESULT`, `approved_instruction`, `framework-contract-repair-001`, and `framework-baseline-checkpoint-control-plane-001` with the Accepted Design spellings. The locator is only `RECONCILIATION_REQUEST.approval_evidence_ref`; it is not part of the approval payload or approved authority core.

### Authority and scope review

No candidate rule authorizes its own implementation. No task grants CODEX_IMPLEMENTER commit, push, bridge, integration, tag, or publication authority. The Plan has no Plugin work, State Oracle implementation repair, or unrelated Framework refactor.

### Amendment consistency review

`REPLACEMENT_BRIDGE_AUTHORIZED_PATHS` contains exactly 38 entries: 35 prior repair paths plus exactly three content-locked `BASELINE_CLOSURE_TARGET` paths; the existing three are explicitly `DELETE_ONLY` v2.7.0 outputs. The historical 35-path bridge is superseded-before-consumption and forbidden to replay; bridge-002 is superseded after partial local Tasks 1–3 execution and is preserved solely as immutable predecessor/audit evidence. Baseline Closure Prelude and Tasks 1–10 mutate only bridge-003 paths on clean `framework-contract-repair-implementation-002`; all pre-activation mutation steps are `USER_LOCAL_APPLY`, and every CODEX step is PREPARE or VERIFY. Task 1 starts only after complete clean-baseline verification; Tasks 2–9 retain their architecture; the final candidate has exactly one repair candidate commit, not a Prelude/Baseline commit. The bridge binds `FINAL_ACCEPTED_AMENDED_PLAN_SHA`; `BRIDGE_PAYLOAD_BINDER_ROLE = GPT_ORCHESTRATOR`; `CODEX_REVIEWER_AUTHORITY_BINDING = NO`; and approval author, tag creator, and tag pusher are respectively USER_APPROVER, USER_LOCAL, and USER_LOCAL. Approval evidence retains the explicit orphan-first, parent-on-subsequent, fast-forward-only exact-tuple transport procedure above. `GLOBAL_OPTIMUM_OVER_LOCAL_OPTIMUM` remains deferred post-Contract-Repair optimization work.

## Lifecycle amendment: 2.7.1 Phase A and 2.7.2 Phase B

This amendment supersedes the earlier Task 10, Task 11, publication, and lifecycle-checkpoint sequencing wherever they require Tasks 5–9 for `2.7.1`, describe `2.7.1` as full Contract Repair completion, or leave bridge-003 usable after Phase-A publication. Tasks 1–4 remain technically unchanged.

### Phase A — Framework 2.7.1 checkpoint/stabilization release

`2.7.0` remains the released baseline. `2.7.1` contains only the Baseline Closure Prelude, Tasks 1–4, and only the version/release surfaces necessary to publish that exact tested state. It is not evidence of external approval-evidence locator completion, actual-Git scope-oracle completion, native control-plane authority composition, first native seed completion/consumption, or full Contract Repair completion.

The executable order is: Baseline Closure Prelude; Tasks 1–4; Phase-A final verification; `2.7.1` release-candidate preparation; independent `POST_EXECUTION` review; exact-SHA USER_APPROVER acceptance; USER_LOCAL publication and remote verification; STOP/PAUSE FEATURE DEVELOPMENT. The Phase-A candidate must pass Prelude, Tasks 1–4, the full test suite, `validate_framework.py`, `validate_project.py .`, `validate_consumer_projection.py --root .`, `git diff --check`, and authorized changed-path verification before independent review. Publication is permitted only for the exact accepted candidate SHA.

Bridge `framework-contract-repair-bridge-003` is limited to the Phase-A candidate under its existing exact 38-path authority and its one repair-candidate commit limit. After exact `2.7.1` publication and remote active-authority verification, it is consumed and terminated. It cannot authorize Tasks 5–9, any second repair candidate commit, or other mutation.

### Phase B — Framework 2.7.2

Former Tasks 5–9 are deferred to `2.7.2` with their technical semantics retained: external approval-evidence locator verification, actual Git mutation-scope oracle, native control-plane authority composition, first native seed completion/consumption as applicable, and production-shaped composed lifecycles. Phase B begins only after `2.7.1` is remotely active, and it must not claim self-authorization because Phase A does not complete native repair authority.

The Phase-B order is: future bridge-004 lifecycle; Tasks 5–9; `2.7.2` release preparation; full final verification; independent review; exact-SHA acceptance; publication; activation. `framework-contract-repair-bridge-004` is a future, separately reviewed and USER_APPROVER-approved migration authority. Its payload and scope must be prepared later, after `2.7.1` is remotely active; this Plan neither creates bridge-004 nor authorizes its creation. `STATE-ORACLE-SCHEMA-REQUIRED-FIELDS-001`, Plugin work, `GLOBAL_OPTIMUM_OVER_LOCAL_OPTIMUM`, and unrelated Framework refactors remain deferred.
