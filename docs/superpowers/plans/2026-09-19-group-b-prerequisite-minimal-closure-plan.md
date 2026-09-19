# Group B Prerequisite Minimal Closure Plan

> **Status:** corrected amended-Plan candidate only. No execution authority.

**Goal:** complete the smallest valid closure from the current prerequisite-authority blocker to a fresh Group-B B0 result.

**Execution model:** GPT only prepares/reviews authority artifacts and adjudicates. All mutation is executed in the USER's local environment. Before `2.7.2+fix.2 REMOTE_ACTIVE`, mutation authority is the approved one-time `USER_LOCAL` bootstrap. After activation, native mutation uses local `CODEX_IMPLEMENTER` with a separate USER-started local `CODEX_REVIEWER`.

## 1. Normative immutable inputs

- prerequisite Design:
  `15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`
- prerequisite Plan:
  `36695832aa17198b217252077bcf70c6ba77c67a:docs/superpowers/plans/2026-09-19-group-b-prerequisite-contract-reconciliation-plan.md`
- bootstrap Design:
  `97afda5e716dea7b53724e3d2dbede977d4a669c:docs/superpowers/specs/2026-09-19-group-b-prerequisite-bootstrap-corrective-activation-design.md`
- finalization-Work-Unit Design amendment:
  `7e14c42fc731e0f63e2dcc35f87f8b14b3eb7023:docs/superpowers/specs/2026-09-19-group-b-prerequisite-fix2-finalization-work-unit-design-amendment.md`

The blocked Plan candidate `d636243b9ffa0ba2cdc1ace5f04b2e11827d092a` is historical finding evidence only and is not authority.

## 2. Frozen boundaries

```text
CORRECTIVE_BASELINE = 2.7.2+fix.2
GROUP_B_RELEASE = 2.7.3
GROUP_C_RELEASE = 2.7.4
TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO
PLUGIN_WORK_RESUMED = NO
BRIDGE_004_REUSE = FORBIDDEN
BRIDGE_005_CREATED = NO
B0_PASS_IS_B1_AUTHORITY = NO
GPT_IMPLEMENTATION = NO
```

No new module, State value, queue, daemon, database, workflow engine, or generic bootstrap subsystem.

## 3. Exact bootstrap mutation scope

The one-time bootstrap may mutate exactly these 32 paths and no others:

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
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
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

Required check:

```text
BOOTSTRAP_PATH_COUNT = 32
UNIQUE_BOOTSTRAP_PATH_COUNT = 32
```

A 33rd path is `AMENDMENT_REQUIRED`.

## 4. Phase A — freeze one bootstrap authority object

Freshly observe:
- `origin/main`;
- current `STATE.revision`;
- repository identity;
- accepted refs above;
- exact 32-path set.

Freeze one canonical authority core containing:
- bootstrap id `framework-group-b-prerequisite-bootstrap-001`;
- fresh base SHA;
- fresh State revision;
- the accepted immutable refs;
- exact 32 paths;
- candidate branch;
- `executor_role = USER_LOCAL`;
- `corrective_target_version = 2.7.2+fix.2`;
- `integration_mode = FAST_FORWARD_ONLY`;
- one-use expiry at `REMOTE_ACTIVE_2.7.2_FIX2_VERIFIED`.

Then:

```text
USER starts fresh local CODEX_REVIEWER
-> PASS on exact authority-core hash
-> GPT adjudication
-> USER exact bootstrap-wrapper approval
-> USER_LOCAL creates immutable annotated bootstrap tag
-> verify remote tag object
```

No working-tree mutation before the immutable bootstrap object is verified.

## 5. Phase B — execute only the accepted prerequisite repair

Under the verified bootstrap, execute the already accepted technical work in this order:

### B1. R0
Modify only `.gpt-codex/framework-modules/modules/role-communication.json`.

Required result:
- the five Task-2/3 test paths resolve to exactly `role-communication`;
- exactly two missing required tests are added;
- no routing/authority semantic change.

Commit `R0_SHA`.

USER starts a fresh local POST reviewer. PASS + GPT adjudication before B2.

### B2. Task 2
Execute accepted prerequisite Plan Task 2 unchanged:
- `scope_paths`;
- `remediation_decision_ref`;
- `approval_evidence_ref`;
- strict Instruction SemVer;
- accept `2.7.2+fix.1` and `2.7.2+fix.2`;
- no version-equality authority rule.

Commit `TASK2_SHA`.

Fresh local POST reviewer + GPT adjudication before B3.

### B3. Task 3
Execute accepted prerequisite Plan Task 3 unchanged:
- complete intrinsic `APPROVAL_RESULT`;
- `USER_APPROVER` authorship;
- full closed authority core;
- no type-token-only bypass;
- no weakening of execution/publication/State completion evidence.

Commit `TASK3_SHA`.

Fresh local POST reviewer + GPT adjudication before B4.

### B4. Task 4
Execute accepted prerequisite Plan Task 4 unchanged:
- closed Work Unit scope;
- non-empty unique `owned_paths`;
- optional unique `excluded_paths`;
- exclusion precedence;
- safe selectors.

Commit `TASK4_SHA`.

Fresh local POST reviewer + GPT adjudication before B5.

### B5. Create the one finalization Work Unit

Create:

```text
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
```

It must:
- be `AUTHORIZED`;
- have `basis_state_revision =` the frozen bootstrap State revision;
- own exactly:
  1. `.gpt-codex/STATE.json`
  2. `.gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json`
  3. `.gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json`
- have `excluded_paths = []`;
- not own itself;
- bind accepted immutable Design/Plan refs;
- forbid publication, scope expansion, bridge-005, B1, Plugin, Tasks 5–9.

Validate it with the repaired Work Unit schema.

## 6. Phase C — verify prerequisite closure and build fix2 candidate

Run the accepted prerequisite composition/full-verification requirements:
- focused RED/GREEN suites;
- sensitivity restoration;
- Framework validator;
- project validator;
- consumer projection validator;
- full unittest suite with zero failures/errors;
- `git diff --check`.

Then change only the approved fix2 release-source paths:
- `VERSION`
- `.gpt-codex/builtins/INDEX.json`
- `.gpt-codex/framework-modules/REGISTRY.json`
- `.gpt-codex/CHANGELOG.md`
- `.gpt-codex/README.md`
- `.gpt-codex/BOOTSTRAP_PROMPT.md`
- `AGENTS.md`
- `releases/INDEX.json`
- `releases/records/v2.7.2+fix.2.json`

Generate only the three approved fix2 dist outputs.

No `STATE.json` or fix2 publication-evidence file is created yet.

Record exact `FIX2_CANDIDATE_SHA`.

## 7. Phase D — final cumulative review and exact acceptance

USER starts a fresh local independent `CODEX_REVIEWER` for:

```text
fresh bootstrap base .. FIX2_CANDIDATE_SHA
```

Require:
- all tracked/untracked mutation within the exact 32-path bootstrap scope;
- R0 ordering preserved;
- Task-2/3/4 semantics unchanged;
- finalization Work Unit present and valid;
- fix2 release identity consistent;
- no State/fix2 publication-evidence mutation;
- no Tasks 5–9, Plugin, bridge-005, B1, Group C.

After PASS:
- GPT adjudicates;
- USER accepts exact `FIX2_CANDIDATE_SHA`.

No tracked mutation after that acceptance.

## 8. Phase E — exact fix2 activation and bootstrap termination

USER_LOCAL:
1. fast-forwards `main` to exactly `FIX2_CANDIDATE_SHA`;
2. creates/pushes `v2.7.2+fix.2` targeting exactly that SHA;
3. publishes the already-reviewed artifact;
4. returns observed remote main/tag/release/VERSION/artifact hash+size facts.

GPT verifies exact agreement.

Only then:

```text
2.7.2+fix.2 REMOTE_ACTIVE = VERIFIED
BOOTSTRAP = TERMINATED
```

The bootstrap can never be reused.

## 9. Phase F — native three-path publication-State finalization

After bootstrap termination, repaired native authority is active.

Use immutable Work Unit ref:

```text
target_work_unit =
framework-group-b-prerequisite-fix2-finalization-001

target_work_unit_ref =
FIX2_CANDIDATE_SHA:
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
```

Fresh current State revision must equal the Work Unit's `basis_state_revision`.

Native Instruction `scope_paths` must equal exactly the Work Unit's three paths.

Lifecycle:

```text
GPT prepares native Instruction
-> USER starts fresh local CODEX_REVIEWER PRE_EXECUTION
-> GPT adjudication
-> USER approval if required
-> USER runs local CODEX_IMPLEMENTER
-> USER starts separate local CODEX_REVIEWER POST_EXECUTION
-> GPT adjudication
-> USER exact finalization-candidate acceptance
-> fast-forward main
```

Finalization records only already-observed fix2 publication facts.

State:
- revision +1;
- append the two fix2 evidence refs;
- `latest_verified_remote_sha = FIX2_CANDIDATE_SHA`;
- `latest_synced_state_revision = new revision`;
- `last_verified_result_ref = .gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json`;
- `sync_status = SYNCED`;
- `next_action = GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED`.

After revision advances, the Work Unit is stale and cannot be reused.

## 10. Phase G — repeat B0 and stop

Freshly repeat Group-B B0.

Return only:

```text
B0 = PASS | AMENDMENT_REQUIRED | RECONCILIATION_REQUIRED
MIGRATION_AUTHORITY_REQUIRED = YES | NO | UNRESOLVED
B1_AUTHORIZED = NO
```

Stop there.

If migration authority is still needed, bridge-005/current successor starts a separate later lifecycle. This Plan does not create it.

## 11. Failure rule

Stop with `RECONCILIATION_REQUIRED` for stale base/State/SHA/review/release facts.

Stop with `AMENDMENT_REQUIRED` for any need to:
- add a 33rd bootstrap path;
- change Task-2/3/4 semantics;
- modify release tooling;
- add another Work Unit;
- start Tasks 5–9;
- create bridge-005;
- resume Plugin/Group C.

No implicit widening or retry.

## 12. Next gate

This Plan candidate grants no execution authority.

```text
Plan candidate
-> USER-started local CODEX_REVIEWER
-> GPT adjudication
-> USER exact Plan acceptance
-> immutable accepted Plan ref
-> Phase A bootstrap authority preparation
```

GPT does not execute implementation.
