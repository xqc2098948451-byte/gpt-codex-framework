# Group B Prerequisite Bootstrap Corrective-Activation Plan Amendment

> **For agentic workers:** this is a Plan amendment, not implementation authority. The USER executes all implementation locally. Use the accepted prerequisite Plan together with this amendment; where this file explicitly overrides ordering or authority, this file controls.

**Goal:** resolve the verified prerequisite-authority bootstrap circularity, execute the already-accepted prerequisite reconciliation under a one-time immutable bootstrap, activate `2.7.2+fix.2` remotely, terminate the bootstrap, then return to repaired native authority for publication-State finalization and repeated Group-B B0.

**Architecture:** keep the previously accepted Task-2/3/4 technical work unchanged. Replace only the impossible pre-R0 native-authority entry with a one-time immutable `USER_LOCAL` bootstrap wrapper, freeze an exact 31-path bootstrap mutation scope, preserve milestone reviews, publish an exact reviewed `2.7.2+fix.2` candidate, terminate the bootstrap on remote activation, and then perform the repository publication-State finalization through the newly active native authority.

**Tech Stack:** Git, Python 3 standard library, JSON Schema 2020-12, `unittest`, existing release/publication scripts, GitHub remote publication.

**Normative inputs:**
- accepted prerequisite Design: `15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`
- accepted prerequisite Plan: `36695832aa17198b217252077bcf70c6ba77c67a:docs/superpowers/plans/2026-09-19-group-b-prerequisite-contract-reconciliation-plan.md`
- accepted bootstrap Design amendment: `97afda5e716dea7b53724e3d2dbede977d4a669c:docs/superpowers/specs/2026-09-19-group-b-prerequisite-bootstrap-corrective-activation-design.md`

## 1. Amendment composition rule

The accepted prerequisite Plan remains normative for:
- R0 technical descriptor content;
- Task-2 Instruction closure;
- Task-3 `APPROVAL_RESULT` closure;
- Task-4 Work Unit effective-scope closure;
- cross-contract composition tests;
- full regression and clean-room sensitivity;
- repeated B0 semantic remap.

This amendment supersedes only:
1. the accepted Plan's assumption that R0 can begin under a native Work Unit + Instruction;
2. the execution-role wrapper before corrective activation;
3. the ordering of release activation and State/evidence finalization;
4. the exact corrective version target, `2.7.2+fix.2`.

No Task-5–9 technical behavior is pulled forward.

## 2. Global constraints

- `TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO`
- `GROUP_B_RELEASE = 2.7.3`
- `GROUP_C_RELEASE = 2.7.4`
- `CORRECTIVE_BASELINE = 2.7.2+fix.2`
- `PLUGIN_WORK_RESUMED = NO`
- `BRIDGE_004_REUSE = FORBIDDEN`
- `BRIDGE_005_CREATED_BY_THIS_PLAN = NO`
- `B0 PASS != B1 AUTHORITY`
- GPT does not execute implementation.
- Before `2.7.2+fix.2 REMOTE_ACTIVE`, bootstrap mutation authority is `USER_LOCAL`; local Codex may assist mechanically but is not the authority source.
- `CODEX_REVIEWER` is always a fresh USER-started local read-only session.
- After `2.7.2+fix.2 REMOTE_ACTIVE`, ordinary native mutation returns to `CODEX_IMPLEMENTER -> separate local CODEX_REVIEWER`.
- No GitHub Cloud Codex review is a required gate unless USER explicitly authorizes it.
- No new module, State value, database, queue, daemon, workflow engine, or standing bootstrap mechanism.

## 3. Exact bootstrap mutation path set

The immutable bootstrap authority core MUST contain this exact ordered set and no additional repository path.

```text
.gpt-codex/framework-modules/modules/role-communication.json
.gpt-codex/schemas/instruction-envelope.schema.json
.gpt-codex/scripts/instruction_envelope.py
.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json
.gpt-codex/tests/test_instruction_envelope.py
.gpt-codex/tests/test_instruction_role_contract.py
.gpt-codex/schemas/result-envelope.schema.json
.gpt-codex/scripts/role_communication.py
.gpt-codex/project-template/RESULT_ENVELOPE.template.json
.gpt-codex/scripts/result_return.py
.gpt-codex/scripts/publication_contract.py
.gpt-codex/tests/test_result_contract_schema.py
.gpt-codex/tests/test_role_communication_taxonomy.py
.gpt-codex/tests/test_result_return.py
.gpt-codex/tests/test_self_hosting_validator.py
.gpt-codex/tests/test_validator_context_binding.py
.gpt-codex/schemas/work-unit.schema.json
.gpt-codex/project-template/WORK_UNIT.template.json
.gpt-codex/scripts/validate_project.py
VERSION
.gpt-codex/builtins/INDEX.json
.gpt-codex/framework-modules/REGISTRY.json
.gpt-codex/CHANGELOG.md
.gpt-codex/README.md
.gpt-codex/BOOTSTRAP_PROMPT.md
AGENTS.md
releases/INDEX.json
releases/records/v2.7.2+fix.2.json
dist/gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip
dist/gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip.sha256
dist/gpt-codex-framework-v2.7.2+fix.2-release.json
```

Count must equal exactly `31`.

The following are expressly outside bootstrap scope:
- `.gpt-codex/STATE.json`
- `.gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json`
- `.gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json`
- all historical Task-5–9 implementation paths not already listed above
- `.gpt-codex/scripts/git_continuity.py`
- Plugin paths
- bridge-005 artifacts
- Group-C paths.

The first three excluded paths are handled only after corrective remote activation through repaired native authority.

## 4. Bootstrap authority core and immutable wrapper

### 4.1 Frozen authority core

GPT prepares a canonical UTF-8/LF JSON authority core after fresh preflight. It is not committed to the candidate branch.

Exact fields:

```text
bootstrap_id = framework-group-b-prerequisite-bootstrap-001
one_time = true
repository_id = 1366213495
repository_full_name = xqc2098948451-byte/gpt-codex-framework
fresh_base_sha = <fresh origin/main>
fresh_state_revision = <fresh STATE revision>
accepted_design_ref = 15263527...:<Design path>
accepted_plan_ref = 36695832...:<Plan path>
accepted_bootstrap_amendment_ref = 97afda5e...:<Amendment path>
accepted_amended_plan_ref = <future accepted amended-Plan SHA:path>
candidate_branch = bootstrap/group-b-prerequisite-fix2-001
exact_owned_paths = <the exact 31-path array above>
executor_role = USER_LOCAL
forbidden_roles_for_bootstrap_mutation = [CODEX_IMPLEMENTER, CODEX_REVIEWER]
corrective_target_version = 2.7.2+fix.2
integration_mode = FAST_FORWARD_ONLY
expiry_condition = REMOTE_ACTIVE_2.7.2_FIX2_VERIFIED
```

Canonicalization:
- JSON UTF-8 without BOM;
- LF line endings;
- sorted object keys;
- arrays preserve the defined order;
- compact separators `,` and `:`;
- SHA-256 over exact bytes.

Return:

```text
BOOTSTRAP_AUTHORITY_CORE_SHA256 = <64 hex>
```

### 4.2 PRE_EXECUTION review basis

The local independent Reviewer reviews the exact authority-core bytes identified by `BOOTSTRAP_AUTHORITY_CORE_SHA256` plus the accepted artifacts and fresh repository facts.

Reviewer returns the usual immutable target fields plus:

```text
REVIEWED_BOOTSTRAP_CORE_SHA256 =
<same 64 hex>
```

GPT persists the USER-provided local review result in a repository PR comment and records:
- comment id;
- SHA-256 of the exact persisted review-result body.

This persisted review-result comment is evidence, not authority.

### 4.3 Final immutable authorization wrapper

After GPT adjudication, GPT prepares the final wrapper:

```json
{
  "authority_core": <exact parsed authority-core object>,
  "authority_core_sha256": "<64 hex>",
  "pre_execution_review_ref": "github-pr-comment:<id>",
  "pre_execution_review_sha256": "<64 hex>",
  "gpt_adjudication_ref": "github-pr-comment:<id>"
}
```

The wrapper repeats no alternate authority fields outside `authority_core`.

USER_APPROVER approves the exact wrapper bytes.

Only after that approval may USER_LOCAL create the immutable remote bootstrap object:
- annotated tag name: `bootstrap/framework-group-b-prerequisite-bootstrap-001`;
- tag target: exact accepted amended-Plan commit SHA;
- tag message: exact canonical wrapper JSON bytes;
- record the annotated tag object SHA;
- verify the tag object and target are remotely reachable.

The tag name is a locator only. The immutable authority identity is the annotated tag object SHA plus the wrapper/core hashes.

No mutation begins if the remote tag object, wrapper bytes, core hash, review hash, base SHA, or State revision differs.

## 5. Phase P0 — fresh bootstrap preflight

USER_LOCAL/local tooling performs read-only checks:

```bash
git fetch origin --prune --tags
git rev-parse origin/main
git status --porcelain=v1
git rev-parse HEAD
```

Also read:
- `.gpt-codex/STATE.json`
- `.gpt-codex/CONTROL.json`
- Registry and the four accepted prerequisite module owners;
- accepted Design/Plan/amendment/amended-Plan objects.

Require:
- repository identity matches;
- worktree chosen for bootstrap is clean;
- fresh base is exact `origin/main`;
- State revision equals the authority-core revision before execution;
- no existing tag/ref named `bootstrap/framework-group-b-prerequisite-bootstrap-001`;
- the 31-path list still routes to the accepted owners or release surface classes without new semantic owner.

Any mismatch stops `RECONCILIATION_REQUIRED`.

## 6. Phase P1 — bootstrap review and approval

Sequence:

```text
freeze authority core bytes
-> USER starts fresh local CODEX_REVIEWER
-> reviewer PASS over exact core hash
-> GPT persists Result + adjudicates
-> GPT constructs final wrapper
-> USER exact wrapper approval
-> USER_LOCAL creates/pushes annotated bootstrap tag
-> remote tag-object verification
```

No repository working-tree mutation is allowed before the remote bootstrap object is verified.

## 7. Phase P2 — R0 durable ownership registration

Authority: verified bootstrap object / `USER_LOCAL`.

Technical mutation remains exactly accepted Plan Task 1:
- modify only `.gpt-codex/framework-modules/modules/role-communication.json`;
- add exactly the five Task-2/3 test paths to `OWNED_ASSETS`;
- add exactly `test_instruction_envelope.py` and `test_result_return.py` to `REQUIRED_TESTS`;
- preserve module id/responsibilities/dependencies/permissions/routing semantics.

Before mutation:
- prove all five test paths unresolved.

After mutation:
- Registry validation PASS;
- all five map to exactly `role-communication`;
- required Framework-core tests PASS.

Commit:

```bash
git add .gpt-codex/framework-modules/modules/role-communication.json
git diff --cached --check
git commit -m "chore: register role communication contract tests"
```

Record `R0_SHA`.

USER starts a fresh local independent POST reviewer against exact `R0_SHA`.

No P3 mutation until R0 POST review PASS and GPT adjudication.

## 8. Phase P3 — accepted prerequisite Task 2

Authority: same verified bootstrap object; descendant of reviewed R0.

Execute accepted prerequisite Plan Task 2 without semantic change:
- close `scope_paths`;
- add `remediation_decision_ref`;
- add closed `approval_evidence_ref`;
- strict SemVer 2.0.0 representation;
- accept exact `2.7.2+fix.1` and future `2.7.2+fix.2`;
- do not alter release parser;
- do not add version-equality authority.

Mutable paths are exactly the five Task-2 paths already present in the 31-path bootstrap list.

Run accepted RED -> GREEN -> sensitivity cycle and JSON parse gate.

Commit and record `TASK2_SHA`.

USER starts fresh independent POST reviewer; PASS + GPT adjudication required before P4.

## 9. Phase P4 — accepted prerequisite Task 3

Authority: same verified bootstrap object.

Execute accepted prerequisite Plan Task 3 without semantic change:
- complete intrinsic `APPROVAL_RESULT`;
- close approved authority core;
- enforce `USER_APPROVER`;
- preserve `PASS + NOT_ATTEMPTED + completion_evidence=null`;
- narrow `publication_contract.py` exception only to fully validated intrinsic approval;
- preserve execution/publication/State completion semantics;
- use already-owned framework-validation composition tests.

Mutable paths are exactly the Task-3 paths in the 31-path bootstrap list.

Run all focused + unchanged release-projection regression suites required by accepted Plan.

Commit and record `TASK3_SHA`.

USER starts fresh independent POST reviewer; PASS + GPT adjudication required before P5.

## 10. Phase P5 — accepted prerequisite Task 4

Authority: same verified bootstrap object.

Execute accepted prerequisite Plan Task 4 without semantic change:
- close Work Unit scope;
- require non-empty/unique `owned_paths`;
- optional unique `excluded_paths`;
- safe exact/directory-prefix selectors;
- exclusion precedence;
- preserve existing durable Work Units or stop `DESIGN_RECONCILIATION_REQUIRED`.

Mutable paths are exactly:
- `.gpt-codex/schemas/work-unit.schema.json`
- `.gpt-codex/project-template/WORK_UNIT.template.json`
- `.gpt-codex/scripts/validate_project.py`
- `.gpt-codex/tests/test_self_hosting_validator.py`
- `.gpt-codex/tests/test_validator_context_binding.py`

Commit and record `TASK4_SHA`.

USER starts fresh independent POST reviewer; PASS + GPT adjudication required before P6.

## 11. Phase P6 — composition and full regression

Execute accepted Plan Tasks 5 and 6.

No production path outside the existing 31-path bootstrap list may be added.

Require:
- prerequisite composition PASS;
- Framework validator PASS;
- project validator PASS;
- consumer projection validator PASS;
- full `unittest discover` zero failures / zero errors;
- four module owner-required suites recorded;
- clean-room fault matrix PASS;
- `git diff --check` PASS.

If a composition failure requires an unlisted production path, stop `AMENDMENT_REQUIRED`; do not expand bootstrap scope.

## 12. Phase P7 — prepare corrective release candidate

Still under the verified bootstrap.

Update only these tracked release/version paths:

```text
VERSION
.gpt-codex/builtins/INDEX.json
.gpt-codex/framework-modules/REGISTRY.json
.gpt-codex/CHANGELOG.md
.gpt-codex/README.md
.gpt-codex/BOOTSTRAP_PROMPT.md
AGENTS.md
releases/INDEX.json
releases/records/v2.7.2+fix.2.json
```

Required values:
- source/Registry/builtins/docs current version = `2.7.2+fix.2`;
- release record `version = 2.7.2+fix.2`;
- release record `previous_version = 2.7.2+fix.1`;
- release record/index artifact name = `gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip`;
- release is corrective prerequisite closure only; no Group-B Tasks 5–9 claim.

Do not modify:
- `.gpt-codex/scripts/release_framework.py`;
- release packaging tests;
- version-consistency test unless a real failing requirement proves the existing generic test is insufficient. Such a need is outside the frozen bootstrap scope and stops for amendment.

Generate runtime release outputs only at these paths:

```text
dist/gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip
dist/gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip.sha256
dist/gpt-codex-framework-v2.7.2+fix.2-release.json
```

Use the existing release script and current metadata-only retention contract.

Run:
- version consistency;
- release packaging;
- publication authority;
- consumer projection/runtime;
- Framework/project validators;
- full test suite;
- `git diff --check`.

Commit all tracked prerequisite + release-source changes into one final corrective candidate descendant chain. Dist outputs may remain runtime artifacts according to current retention policy.

Record `FIX2_CANDIDATE_SHA`.

## 13. Phase P8 — final cumulative implementation review

USER starts a fresh local independent `CODEX_REVIEWER` against:

```text
bootstrap fresh_base_sha .. FIX2_CANDIDATE_SHA
```

Reviewer must verify:
- cumulative changed tracked paths are a subset of the approved tracked portion of the 31-path list;
- no unapproved untracked path was created;
- R0 durability/order;
- accepted Task-2/3/4 semantics;
- full regression/sensitivity evidence;
- release identity exactly `2.7.2+fix.2`;
- no State/evidence finalization files are in the candidate;
- no Task-5–9, Plugin, bridge-005, Group-C work;
- no mutation after `FIX2_CANDIDATE_SHA`.

GPT adjudicates.

USER accepts the exact `FIX2_CANDIDATE_SHA`.

Any new tracked mutation after acceptance requires a new candidate + cumulative local review + USER exact acceptance.

## 14. Phase P9 — fast-forward integration and corrective publication

USER_LOCAL uses the existing bootstrap's publication phase.

Preflight:
- `origin/main` still equals the frozen bootstrap base expected for integration ancestry;
- `FIX2_CANDIDATE_SHA` descends from that base;
- local reviewed candidate clean;
- publication capabilities available;
- no tag/release conflict for `v2.7.2+fix.2`;
- generated artifact hash/size match release record/index.

Integrate:

```bash
git push origin FIX2_CANDIDATE_SHA:refs/heads/main
```

This must be a fast-forward to exactly the reviewed USER-accepted SHA.

Then create/push annotated release tag and publish the already-reviewed artifact according to current release mechanism:

```text
tag = v2.7.2+fix.2
tag target = FIX2_CANDIDATE_SHA
artifact = gpt-codex-framework-v2.7.2+fix.2-bootstrap.zip
```

No tracked file changes are permitted during publication.

## 15. Phase P10 — tool-observed remote-active verification and bootstrap termination

USER_LOCAL returns tool-observed facts:

```text
remote main SHA
annotated tag object SHA
tag target SHA
published release version/url
remote VERSION
artifact SHA-256
artifact size
```

GPT verifies:
- remote main == `FIX2_CANDIDATE_SHA`;
- tag target == `FIX2_CANDIDATE_SHA`;
- remote VERSION == `2.7.2+fix.2`;
- release/tag version == `v2.7.2+fix.2`;
- published artifact hash/size == reviewed record/index/runtime artifact.

Only then:

```text
2.7.2+fix.2 REMOTE_ACTIVE = VERIFIED
BOOTSTRAP framework-group-b-prerequisite-bootstrap-001 = TERMINATED
```

The annotated bootstrap tag object remains immutable historical evidence but has no further mutation authority.

No repository State/evidence file is written by the bootstrap after termination.

## 16. Phase P11 — native publication-State finalization after bootstrap termination

This is a **new native-authority lifecycle**, not bootstrap scope.

Because `2.7.2+fix.2` is now active, the repaired Instruction schema can represent:
- exact Framework version `2.7.2+fix.2`;
- bounded `scope_paths`.

GPT prepares a bounded native Work Unit / Instruction with exactly these mutation paths:

```text
.gpt-codex/STATE.json
.gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json
.gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json
```

Required lifecycle:

```text
fresh current main + State revision
-> bounded Work Unit + native Instruction
-> USER starts fresh local independent CODEX_REVIEWER PRE_EXECUTION
-> GPT adjudication
-> USER approval if current native control-plane lifecycle requires it
-> local CODEX_IMPLEMENTER executes
-> separate fresh local CODEX_REVIEWER POST_EXECUTION
-> GPT adjudication
-> USER exact finalization-candidate acceptance
-> fast-forward main
```

The finalization records actual observed remote facts; it must not predict tag object ids, artifact hashes, or remote SHAs before observation.

State transition:
- increment current revision exactly once through the governed native transition;
- append the two fix2 evidence refs;
- `continuity.latest_verified_remote_sha = FIX2_CANDIDATE_SHA`;
- `continuity.latest_synced_state_revision = new State revision`;
- `continuity.last_verified_result_ref = .gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json`;
- `continuity.sync_status = SYNCED`;
- `next_action = GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED`.

The post-activation finalization commit may place `main` one commit ahead of the release tag, matching the existing fix.1 State-finalization pattern. Active Framework identity remains the immutable release tag target `FIX2_CANDIDATE_SHA`; State records that exact verified active SHA.

## 17. Phase P12 — repeat Group-B B0

Only after native publication-State finalization completes and current State is coherent:

- fresh-read active release/tag/artifact;
- fresh-read main/State/Registry;
- re-run the accepted prerequisite Plan Task 7 B0 remap;
- compare immutable historical Tasks 5–9 to current owners.

Return:

```text
B0 = PASS | AMENDMENT_REQUIRED | RECONCILIATION_REQUIRED
B1_AUTHORIZED = NO
MIGRATION_AUTHORITY_REQUIRED = YES | NO | UNRESOLVED
```

Even `B0 = PASS` does not authorize B1.

If later migration authority is required, bridge-005/current successor gets a completely separate lifecycle.

## 18. Local role handoffs

### Bootstrap mutation phases P2–P10

Physical execution: USER's local environment.

Authority role:

```text
USER_LOCAL
```

Local Codex may:
- read;
- prepare patches;
- run tests;
- render commands/evidence.

It must not claim native `CODEX_IMPLEMENTER` authority for bootstrap mutations.

### Native phase P11 onward

Physical execution: USER's local environment.

Protocol chain:

```text
GPT_ORCHESTRATOR
-> local CODEX_IMPLEMENTER
-> USER-started separate local CODEX_REVIEWER
-> GPT adjudication
-> USER_APPROVER when required
```

## 19. Review focus

A Plan reviewer must explicitly challenge:

1. whether 31 is the exact bootstrap mutation path count;
2. whether any required tracked prerequisite/release path is missing;
3. whether any listed path broadens into historical Tasks 5–9;
4. whether State/evidence finalization is correctly excluded from bootstrap and deferred to repaired native authority;
5. whether the bootstrap core/review/wrapper construction avoids self-referential review evidence;
6. whether R0 is durable before dependent test mutation;
7. whether release publication can occur without tracked post-review changes;
8. whether fix2 remote verification is based on observations, not predicted evidence;
9. whether bootstrap termination occurs before native finalization;
10. whether native finalization can represent exact `2.7.2+fix.2` and exact 3-path scope;
11. whether post-finalization main-ahead-of-tag semantics remain consistent with current State's `latest_verified_remote_sha` model;
12. whether B0 remains non-authorizing.

## 20. Failure handling

Stop without further mutation if:
- accepted immutable refs do not resolve;
- fresh base/State differs after bootstrap approval;
- exact path set differs;
- bootstrap core/review/wrapper hashes differ;
- bootstrap tag already exists or remote object differs;
- any local Reviewer returns findings not yet adjudicated;
- R0 rewrite/rebase occurs;
- a required implementation path is outside the 31-path list;
- full/focused tests fail;
- final cumulative review target drifts;
- USER final candidate acceptance targets another SHA;
- main cannot fast-forward exactly;
- publication creates tracked changes;
- tag/release/version/artifact facts disagree;
- remote active verification fails;
- native finalization authority cannot be formed under active fix2;
- State finalization needs any fourth mutation path.

Use `RECONCILIATION_REQUIRED` for stale/current-fact mismatch and `AMENDMENT_REQUIRED` for genuine semantic/scope expansion.

## 21. Plan self-review

- Bootstrap circularity handled before R0: YES.
- Accepted prerequisite technical semantics copied by immutable reference without reinterpretation: YES.
- Exact bootstrap path list frozen: YES, 31.
- State/fix2 evidence excluded from bootstrap: YES.
- Post-activation native finalization defined: YES, exact three paths.
- Review-evidence self-reference avoided: YES; Reviewer reviews authority core hash, final wrapper binds persisted review evidence, USER approves wrapper.
- GPT implementation: NO.
- bridge-004 reuse: NO.
- bridge-005 creation/preparation: NO.
- Task-5–9 implementation: NO.
- Plugin resumed: NO.
- Group B moved from 2.7.3: NO.
- Group C moved from 2.7.4: NO.
- `B0 PASS -> B1` inference: FORBIDDEN.

## 22. Acceptance and next gate

This amended Plan candidate grants no execution authority.

Required next lifecycle:

```text
amended Plan candidate
-> USER starts fresh local independent CODEX_REVIEWER
-> GPT adjudication
-> USER exact amended-Plan acceptance
-> immutable accepted amended-Plan ref
-> fresh P0 observation
-> bootstrap authority-core preparation
-> local independent PRE_EXECUTION review
-> GPT adjudication
-> USER exact wrapper approval
-> USER_LOCAL bootstrap execution
```

GPT will not execute implementation.
