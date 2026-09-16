# Framework Contract Repair Implementation Plan

> **For agentic workers:** implementation remains subject to Framework governance, PRE-EXECUTION review, the Accepted Design, and the one-time migration bridge. No task authorizes itself. Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` task-by-task; steps use checkbox syntax for tracking.

**Goal:** Close the proven Framework instruction, remediation, mutation-scope, approval, and control-plane authority defects without adding a subsystem.

**Architecture:** Reuse the Instruction, Result, Work Unit, Git continuity, and governed-mutation contracts. The bridge is a single user-approved bootstrap operation that creates the repair Work Unit and one seed Work Unit; native authority begins only after the exact reviewed repair is integrated, released, activated, and remotely verified.

**Tech Stack:** Python standard library, JSON Schema, Git, unittest, existing Framework validators and release tooling.

**Spec:** `docs/superpowers/specs/2026-09-17-framework-contract-repair-design.md@3ab2ffdcdda4c3dac43dc59e9dee3a5a0ee11eda`

## Global Constraints

- CURRENT RELEASED AUTHORITY = Framework 2.7.0. Candidate rules are non-authoritative until reviewed, accepted, integrated, released, activated, and remote-verified.
- `scope_paths` is mutation authority; ordinary `scope_paths` is a subset of immutable Work Unit `scope.owned_paths`; `files_changed` is evidence only.
- Preserve `remediation_decision_ref`, FIX freshness, staged/unstaged/untracked pre-COMMIT and pre-PUSH scope checks, historical readability, no eighth module, and one governed entry.
- `APPROVAL_RESULT` uses `status = PASS`, `decision = APPROVE | REJECT`, `completion_gate = NONE`, and non-execution `completion_evidence = null`; status never encodes approval decision.
- Plugin is deferred. The Baseline local implementation is preserved and untouched. `STATE-ORACLE-SCHEMA-REQUIRED-FIELDS-001` is deferred until the repair is active.
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

`actual changed paths ⊆ BRIDGE_AUTHORIZED_PATHS`. The bridge authorization object carries this exact list. The repair Work Unit owns the applicable implementation, schema, template, test, and release paths; the seed Work Unit owns only its frozen four paths. Post-execution observed path union must equal the bridge object list intersected with paths actually changed, never a path inferred from a task.

### BRIDGE_AUTHORIZATION_OBJECT

`BRIDGE_OBJECT_TYPE = signed annotated Git tag`. `BRIDGE_REMOTE_REF = refs/tags/bridge/framework-contract-repair-001`. `BRIDGE_OBJECT_TARGET = Accepted Plan SHA 905a2a32f98e285b21f4ce36e5139d71c858b9df`. `BRIDGE_OBJECT_IDENTITY = annotated tag object SHA returned by git rev-parse refs/tags/bridge/framework-contract-repair-001^{tag}`. `BRIDGE_PAYLOAD_ENCODING = canonical UTF-8 JSON with sorted keys, trailing LF, stored as the annotated tag message`. `BRIDGE_CREATOR_ROLE = USER_APPROVER`.

The reviewed bridge authority core is canonical JSON excluding the review-artifact locator. CODEX_REVIEWER first emits the independent review artifact; USER_APPROVER then creates the outer signed annotated tag binding that artifact SHA-256 without changing the reviewed core. Before creation USER_LOCAL verifies the ref has no remote output using `git ls-remote origin refs/tags/bridge/framework-contract-repair-001`. USER_LOCAL preflights signing with `git config --get user.signingkey` and `git tag -s --help`; an unavailable signing capability returns `RECONCILIATION_REQUIRED`, with no unsigned fallback. USER_APPROVER creates the tag locally, USER_LOCAL pushes only `git push origin refs/tags/bridge/framework-contract-repair-001`, never `--force` or `--force-with-lease`, then verifies remote tag object SHA, tag target, canonical payload hash, and review-artifact hash. A preexisting ref, SHA mismatch, replacement, replay after consumption, or a tag target other than the Accepted Plan SHA returns `RECONCILIATION_REQUIRED`. Consumption is recorded by the exact accepted remote repair SHA; expiry occurs only after remote active-authority verification, and the tag cannot authorize a second mutation while pending.

### Pre-activation actor rule

Before `REMOTE_ACTIVE_AUTHORITY_VERIFICATION = PASS`, every repository mutation in Tasks 1–10 has actor `USER_LOCAL_APPLY`. `CODEX_PREPARE` reads, tests without governed mutation, produces the bounded edit/failing-test expectation, validates, and reports. `CODEX_VERIFY` runs or reads focused verification and reports. CODEX_IMPLEMENTER has zero governed-worktree mutation, commit, push, tag, or release steps before activation. CODEX_REVIEWER is read/test/validate/report only. USER_APPROVER authors approval semantics only. After remote active-authority verification, repaired native authority may authorize CODEX_IMPLEMENTER mutation under a new valid instruction.

## Task 1: Freeze bridge authorization and operational boundaries

**Files:** Create `.gpt-codex/work-units/framework-contract-repair-001.json` and `.gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json`; modify only the exact bridge allowlist files declared by the bridge authorization, including release surfaces for `2.7.1`.

**Interfaces:** The bridge authorization object is an immutable remote signed tag/object containing `bridge_id`, repository id/name, base SHA, candidate branch, pre-execution review SHA-256, a closed approved authority core, exhaustive path list, `one_time: true`, and expiry. The seed has `work_unit_id = framework-baseline-checkpoint-control-plane-001`, `basis_state_revision = 12`, `state = AUTHORIZED`, and the four frozen paths from Task 8.

**Preconditions:** Accepted Plan is frozen at an exact SHA; USER_APPROVER has explicitly approved the bridge object; CODEX_REVIEWER has independently reviewed the base-SHA candidate; `git status --short` is empty before work.

- [ ] Write a failing fixture in `.gpt-codex/tests/test_self_hosting_validator.py` with an absent bridge id, a bridge whose path list includes Plugin content, and a bridge whose object is not immutable.
- [ ] Run `python -m unittest .gpt-codex.tests.test_self_hosting_validator -v`; expect bridge-fixture assertions to fail because no bridge validation exists.
- [ ] Add the two Work Unit fixtures and validator inputs required by the bridge contract; keep the repair Work Unit as output of the bridge, never as its authority source.
- [ ] Run `python -m unittest .gpt-codex.tests.test_self_hosting_validator -v`; expect valid bridge fixture PASS and each malformed bridge fixture FAIL.
- [ ] Sensitivity proof: change one allowed path to `plugins/gpt-codex-framework/` and verify rejection; restore the original exact list and verify PASS.

**Completion evidence:** bridge id, immutable object id, bound review hash, exact path list, and test output. **Handoff:** USER_LOCAL retains the only bridge execution/publishing authority; no CODEX commit or push.

## Task 2: Close the instruction-envelope contract with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/instruction-envelope.schema.json`, `.gpt-codex/scripts/instruction_envelope.py`, `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`; test `.gpt-codex/tests/test_instruction_envelope.py` and `.gpt-codex/tests/test_instruction_role_contract.py`.

**Interfaces:** `build_instruction_envelope(..., scope_paths: list[str] | None = None, remediation_decision_ref: str | None = None, approval_evidence_ref: dict[str, str] | None = None) -> dict`; `approval_evidence_ref` is permitted only on a mutating control-plane `RECONCILIATION_REQUEST` and is not part of the approved authority core.

**Preconditions:** Task 1 bridge path list includes these three files and named tests.

- [ ] Add parameterized failing tests for a mutating instruction with missing, empty, malformed, duplicate, or absolute/`..` `scope_paths`; add a production-shaped FIX with `remediation_decision_ref`; add a control-plane request with closed `{remote_ref,evidence_commit_sha,path,blob_sha}` locator.
- [ ] Run `python -m unittest .gpt-codex.tests.test_instruction_envelope .gpt-codex.tests.test_instruction_role_contract -v`; expect schema/builder failures for fields rejected by the closed envelope.
- [ ] Add schema properties and conditional requirements; validate and render all three fields in `build_instruction_envelope`; add the template placeholders.
- [ ] Run the same command; expect all valid shapes PASS and every malformed shape FAIL.
- [ ] Sensitivity proof: remove only `remediation_decision_ref` from the FIX fixture and replace one locator blob SHA with a non-SHA; both fail, then restoration passes.

**Completion evidence:** focused command output plus serialized template/render examples. **Handoff:** Task 3 consumes the production-shaped instruction and locator.

## Task 3: Define APPROVAL_RESULT and role taxonomy with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/result-envelope.schema.json`, `.gpt-codex/scripts/role_communication.py`, `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`, and `.gpt-codex/scripts/result_return.py`; test `.gpt-codex/tests/test_result_contract_schema.py`, `.gpt-codex/tests/test_role_communication_taxonomy.py`, and `.gpt-codex/tests/test_result_return.py`.

**Interfaces:** `APPROVAL_RESULT` intrinsic payload contains `result_id`, `responder_role = USER_APPROVER`, `status = PASS`, `decision`, `response_to_instruction_id`, closed `approved_instruction`, `evidence_refs = []`, `completion_gate = NONE`, `remote_verification = NOT_ATTEMPTED`, and `completion_evidence = null`. `validate_result_message_type("APPROVAL_RESULT")` recognizes it; only USER_APPROVER can author it.

**Preconditions:** Task 2 supplies a production-shaped approval request and authority core.

- [ ] Add failing schema/taxonomy tests for unknown `APPROVAL_RESULT`, a non-USER_APPROVER responder, `status = REJECT`, decision omitted, execution-style completion evidence, and any payload containing its final transport commit/blob SHA.
- [ ] Run `python -m unittest .gpt-codex.tests.test_result_contract_schema .gpt-codex.tests.test_role_communication_taxonomy -v`; expect failures at current taxonomy and PASS-completion rules.
- [ ] Add the result type, closed decision and `approved_instruction` conditions, the PASS exception allowing `NOT_ATTEMPTED`, the null completion-evidence rule, and role enforcement.
- [ ] Run the focused command; expect the intrinsic APPROVE and REJECT payloads PASS while every invalid variation FAILS.
- [ ] Sensitivity proof: mutate `approved_instruction.scope_paths` after approval and verify the Task 7 composition fixture rejects it; restore exact core and verify PASS.

**Completion evidence:** schema validation results and role-taxonomy results. **Handoff:** Task 5 resolves the payload bytes, Task 7 validates its correlation.

## Task 4: Close Work Unit owned-path shape with RED→GREEN

**Files:** Modify `.gpt-codex/schemas/work-unit.schema.json`; test `.gpt-codex/tests/test_self_hosting_validator.py` and `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `scope.owned_paths` is a non-empty, unique list of safe repository-relative paths. `CONTROL_PLANE_APPROVED_SCOPE_SOURCE = target_work_unit_ref resolved at immutable Git SHA -> scope.owned_paths`.

**Preconditions:** Task 1 fixture provides both bridge-created Work Units.

- [ ] Add failing Work Unit fixtures with no owned paths, duplicates, an absolute path, and `a/../b`.
- [ ] Run `python -m unittest .gpt-codex.tests.test_self_hosting_validator .gpt-codex.tests.test_validator_context_binding -v`; expect currently open `scope` schema behavior to admit at least one invalid fixture.
- [ ] Close the Work Unit schema `scope` object and `owned_paths` item pattern; use the same safe relative-path convention as Instruction Envelope.
- [ ] Run the focused command; expect all malformed Work Units FAIL and valid ordinary/seed Work Units PASS.
- [ ] Sensitivity proof: append a fifth path to the seed fixture; verify failure; remove it and verify PASS.

**Completion evidence:** validated seed JSON and test output. **Handoff:** Task 7 derives all native control-plane scope from this field.

## Task 5: Add external approval-evidence locator verification with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/git_continuity.py` and `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_git_continuity.py`, `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `resolve_approval_evidence_locator(repository_root: Path, locator: Mapping[str, str]) -> tuple[Mapping[str, object] | None, list[str]]` resolves `evidence_commit_sha:path`, computes the blob SHA, verifies remote reachability of the exact object, and returns `APPROVAL_EVIDENCE_*` errors without accepting a mutable ref head.

**Preconditions:** Task 3 fixed payload and Task 2 closed locator shape.

- [ ] Add failing monkeypatched Git tests for wrong commit, right commit/wrong blob, unreachable object, mutable-ref substitution, payload bytes changed after approval, and a byte-identical USER_LOCAL transport.
- [ ] Run `python -m unittest .gpt-codex.tests.test_git_continuity .gpt-codex.tests.test_validator_context_binding -v`; expect missing resolver failures.
- [ ] Implement exact `git show <commit>:<path>`, blob hashing, fixed-SHA comparison, and explicit remote object/reachability checks; never derive authority from `refs/heads/gpt-codex-approval-evidence` head.
- [ ] Run the focused command; expect every substitution fault FAIL and byte-identical transport PASS.
- [ ] Sensitivity proof: provide the current mutable ref with an otherwise valid but different commit; verify failure; restore the bound commit and verify PASS.

**Completion evidence:** locator tuple, returned error codes, and test output. **Handoff:** Task 7 calls the resolver before admitting control-plane mutation.

## Task 6: Enforce actual Git mutation scope with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_validator_context_binding.py` and `.gpt-codex/tests/test_self_hosting_validator.py`.

**Interfaces:** an internal changed-path oracle unions `git diff --name-only -z`, `git diff --cached --name-only -z`, and `git ls-files --others --exclude-standard -z`; before push it also reads the committed candidate path set. `validate_instruction_authority` and `validate_governed_mutation_entry` reject any path outside exact scope.

**Preconditions:** Task 2 and Task 4 are green.

- [ ] Add failing temporary-repository tests injecting one outside-scope unstaged file, one staged file, and one untracked file while HEAD remains the baseline.
- [ ] Run `python -m unittest .gpt-codex.tests.test_validator_context_binding .gpt-codex.tests.test_self_hosting_validator -v`; expect at least the untracked fixture to escape current authority checking.
- [ ] Implement NUL-delimited path collection, safe repository-relative normalization, set union, subset enforcement, `files_changed` subset enforcement, and committed-path verification before push.
- [ ] Run the focused command; expect each injected path class FAIL and the restored exact snapshot PASS.
- [ ] Sensitivity proof: replace `git diff --cached --name-only -z` with an empty mocked output while a staged file exists; verify the test detects the regression.

**Completion evidence:** each Git command result and fault matrix. **Handoff:** Task 7 uses this shared oracle for ordinary, FIX, and control-plane paths.

## Task 7: Compose the native control-plane authority gate with RED→GREEN

**Files:** Modify `.gpt-codex/scripts/validate_project.py`; test `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_review_lifecycle.py`, `.gpt-codex/tests/test_validator_context_binding.py`.

**Interfaces:** `validate_governed_mutation_entry(...)` distinguishes ordinary Work Unit mutation, FIX remediation, and mutating `RECONCILIATION_REQUEST` while retaining one entry. The control-plane branch requires project/repository identity, immutable authorization Work Unit, matching basis State revision, exact scope equality for seed use, PRE_EXECUTION review, external locator resolution, two-hop approval correlation, self-authorization prevention, and Task 6 actual-path enforcement.

**Preconditions:** Tasks 2–6 are green and the current State revision is supplied by fixture, not changed on disk.

- [ ] Add failing composed fixtures for missing locator, approval result correlated directly to reconciliation, locator core mismatch, authorization Work Unit equal to target, State mismatch, implementation path in control-plane scope, and missing pre-execution review.
- [ ] Run `python -m unittest .gpt-codex.tests.test_self_hosting_validator .gpt-codex.tests.test_review_lifecycle .gpt-codex.tests.test_validator_context_binding -v`; expect missing composition failures.
- [ ] Add the dedicated reconciliation branch and explicit error codes; compare the approved authority core only, never the externally added locator.
- [ ] Run the focused command; expect the production-shaped control-plane chain PASS and every fault fixture FAIL.
- [ ] Sensitivity proof: remove only `approval_evidence_ref` from the valid request; expect failure; restore and expect PASS.

**Completion evidence:** single-chain fixture JSON and complete error matrix. **Handoff:** Task 8 supplies the first seed; Task 9 performs end-to-end composed tests.

## Task 8: Materialize and constrain the first native seed

**Files:** Create `.gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json`; test `.gpt-codex/tests/test_self_hosting_validator.py`.

**Interfaces:** seed `scope.owned_paths` equals exactly: `.gpt-codex/STATE.json`; `.gpt-codex/work-units/framework-baseline-stabilization-001.json`; `.gpt-codex/evidence/results/RESULT-BASELINE-STABILIZATION-POSTEXEC-FINDING.json`; `.gpt-codex/evidence/results/RESULT-FIX-REMEDIATION-LIFECYCLE-CONTRACT-RECONCILIATION.json`. Its own path is excluded. It is invalid after State revision 12.

**Preconditions:** Tasks 4 and 7 are green; bridge authorization contains this exact file and four-path list.

- [ ] Add failing fixtures for a missing path, either result path replaced, a fifth path, seed self-ownership, and reuse when State revision is 13.
- [ ] Run `python -m unittest .gpt-codex.tests.test_self_hosting_validator -v`; expect the absent seed and invalid shape fixtures to fail.
- [ ] Create the closed seed Work Unit and enforce exact four-path equality plus revision-12-only use in the control-plane branch.
- [ ] Run the focused command; expect the exact seed PASS and all five faults FAIL.
- [ ] Sensitivity proof: swap the two result paths in a fixture; verify rejection; restore the frozen list and verify PASS.

**Completion evidence:** immutable Work Unit ref, four-path list, revision-12 fixture output. **Handoff:** Task 9 consumes this seed once.

## Task 9: Prove production-shaped composed lifecycles

**Files:** Modify `.gpt-codex/tests/test_review_lifecycle.py`, `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_validator_context_binding.py`; modify validators only if a composed test exposes a missing Task 2–8 interface.

**Interfaces:** production FIX flow is `schema -> builder -> role/instruction validation -> review lifecycle -> governed entry`; control-plane flow is `instruction schema -> immutable scope -> PRE_EXECUTION review -> locator -> APPROVAL_RESULT -> authority gate -> actual-Git scope`.

**Preconditions:** Tasks 2–8 focused suites are green.

- [ ] Add red composed tests that mutate one field at a time: missing `remediation_decision_ref`, stale finding SHA, stale adjudication revision, missing scope, unowned path, approval core mismatch, wrong blob, and untracked outside-scope file.
- [ ] Run `python -m unittest .gpt-codex.tests.test_review_lifecycle .gpt-codex.tests.test_self_hosting_validator .gpt-codex.tests.test_validator_context_binding -v`; expect targeted failures before all composition fixes are connected.
- [ ] Wire only missing calls among the existing builders, role validator, lifecycle validator, locator resolver, and governed entry.
- [ ] Run the same command; expect each valid production chain PASS.
- [ ] Sensitivity proof: inject each listed fault independently, record FAIL, restore the exact fixture, and record PASS; label these as sensitivity checks rather than original RED cases.

**Completion evidence:** fixture identifiers, failure codes, restored PASS output. **Handoff:** Task 10 runs framework-wide verification.

## Task 10: Close release candidate at version 2.7.1 before final review

**Files:** Modify `VERSION`, `.gpt-codex/builtins/INDEX.json`, `.gpt-codex/CHANGELOG.md`, `releases/INDEX.json`, `releases/records/v2.7.1.json`; create current `dist/gpt-codex-framework-v2.7.1-bootstrap.zip`, `.sha256`, and `-release.json`; test `.gpt-codex/tests/test_version_consistency.py`, `.gpt-codex/tests/test_release_packaging.py`.

**Interfaces:** `VERSION = 2.7.1`; `v2.7.1` is the immutable tag name; `FRAMEWORK_ACTIVE_SHA` is its target and must equal final reviewed `main` SHA. Existing `release_framework.py` consumes `VERSION` and produces the canonical artifact and sidecars.

**Preconditions:** Tasks 2–9 pass; SemVer history shows current `VERSION = 2.7.0`, so 2.7.1 is the minimal patch release; all source, metadata, and generated artifact paths are within the bridge allowlist before post-execution review.

- [ ] Add failing version-consistency and release-packaging assertions for `2.7.1` absent from the index, changelog, record, and artifact metadata.
- [ ] Run `python -m unittest .gpt-codex.tests.test_version_consistency .gpt-codex.tests.test_release_packaging -v`; expect failures until every version surface agrees.
- [ ] Set all release source values to `2.7.1`, run `python .gpt-codex/scripts/release_framework.py`, and retain only its canonical current artifact, SHA sidecar, and manifest.
- [ ] Run the focused command; expect release source, metadata, ZIP integrity, and artifact hash assertions PASS.
- [ ] Sensitivity proof: change only `.gpt-codex/builtins/INDEX.json` back to `2.7.0`; expect version consistency FAIL; restore `2.7.1` and expect PASS.

**Completion evidence:** release command output, artifact SHA-256/size, version-consistency output. **Handoff:** independent post-execution review receives the final candidate with every tracked activation file already included.

## Task 11: Perform final verification and review gates

**Files:** No new source files beyond Task 1–10 scope; test all `.gpt-codex/tests/test_*.py` and existing validators.

**Interfaces:** final candidate facts include exact base SHA, authorized changed paths, full test count discovered from command output, zero failures/errors, validator outputs, unchanged Plugin candidate hashes, and unchanged Baseline three-file snapshot.

**Preconditions:** Task 10 green; USER_LOCAL has not committed or pushed; bridge allows no second implementation commit.

- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'`; expect exit 0 and record actual test count, failures 0, errors 0.
- [ ] Run `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, `python .gpt-codex/scripts/validate_consumer_projection.py --root .`, and `git diff --check`; expect each exit 0.
- [ ] Run the Task 6 path oracle and `git diff --name-only`; expect every changed path to be in the bridge allowlist.
- [ ] Run hashes for the preserved Baseline three-file snapshot and the Task-3 Plugin candidate before/after the task; expect byte-identical values.
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

Accepted Design -> Plan draft -> remote Plan review candidate -> GPT Plan review -> user Plan approval -> Accepted Plan frozen at exact SHA -> bridge authorization preparation -> independent PRE_EXECUTION review -> explicit user bridge approval -> one-time bridge execution -> Tasks 2–10 -> task verification -> composed final verification -> independent POST_EXECUTION review -> remote repair candidate -> independent exact-SHA review -> user acceptance -> exact main fast-forward -> release/tag/publication -> remote active-authority verification -> bridge terminated -> first native Baseline control-plane checkpoint -> blocked Baseline Work Unit -> fresh State Oracle REVIEW_FINDING -> fresh basis/adjudication -> State Oracle FIX.

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

Tasks 1–10 mutate only `BRIDGE_AUTHORIZED_PATHS`; all pre-activation mutation steps are `USER_LOCAL_APPLY`, and every CODEX step is PREPARE or VERIFY. Task 4 closes `scope` as `additionalProperties = false` with required `owned_paths` and optional compatible `excluded_paths`, both unique safe repository-relative arrays. The existing Baseline and Task-3 Work Units are compatibility fixtures; `WORK_UNIT.template.json` changes because its empty `owned_paths` would violate the new minimum. The bridge has one signed annotated-tag representation, and approval evidence has the explicit creation/update procedure above.
