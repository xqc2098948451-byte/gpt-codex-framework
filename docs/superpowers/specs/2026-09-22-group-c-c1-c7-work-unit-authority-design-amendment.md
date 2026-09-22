# Group C C1-C7 Work Unit Authority Design Amendment

## Purpose and trigger

This Design-only amendment defines the missing bounded authority-creation route for the Group C C1-C7 Work Unit. It does not implement C1-C7, create a Work Unit or bootstrap ref, mutate State/Evidence, or authorize publication, Plugin work, C8, or C9.

```
ROOT_CAUSE = GROUP_C_C1_C7_NATIVE_WORK_UNIT_CREATION_AUTHORITY_MISSING
SECONDARY_FINDING = INITIAL_GROUP_C_SCOPE_OVERBROAD
```

C0 passed. The accepted staged-closure Design and Master Plan retain their unchanged C1-C7 semantics. This amendment changes only the Group C C1-C7 Work Unit creation route and its exact minimum default mutation scope. It creates no governance subsystem or general bootstrap factory. Historical bootstraps are precedent only and never reusable authority.

The immutable authority basis remains:

- `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`
- `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`

## Fresh prerequisites

Before a Work Unit freeze or bootstrap review, independently observe `origin/main = e9be8754eced8bcce136515d85a8dfb7a8488ee5` for this Design baseline, `STATE.revision = 17`, `STATE.next_action = GROUP_C_PRE_EXECUTION_REOBSERVATION_REQUIRED`, and v2.7.3 `REMOTE_ACTIVE`. The durable v2.7.3 facts are `.gpt-codex/evidence/V2.7.3-REMOTE-PUBLICATION-VERIFICATION.json` and `.gpt-codex/evidence/results/RESULT-V2.7.3-PUBLICATION.json`. `.gpt-codex/work-units/framework-staged-closure-group-c-001.json` must be absent.

## Exact default C1-C7 Work Unit

```text
WORK_UNIT_ID = framework-staged-closure-group-c-001
WORK_UNIT_PATH = .gpt-codex/work-units/framework-staged-closure-group-c-001.json
basis_state_revision = 17
state = AUTHORIZED
```

The default owned mutation paths are exactly:

1. `.gpt-codex/scripts/framework_feedback.py`
2. `.gpt-codex/tests/test_framework_feedback.py`

Explicit excluded mutation paths are:

- `.gpt-codex/scripts/execution_telemetry.py`
- `.gpt-codex/tests/test_execution_telemetry.py`
- `.gpt-codex/STATE.json`
- `.gpt-codex/schemas/`
- `.gpt-codex/harvest/`
- `plugins/`
- `releases/`
- `dist/`

Permissions are exactly:

```text
authorized_actions = READ, TEST, VALIDATE, REPORT, MUTATE_APPROVED_SCOPE
forbidden_actions = COMMIT, PUSH, PUBLISH, AUTHORIZE, SCOPE_EXPANSION
```

`execution_telemetry.py` and its tests are read-only inputs under this default authority because C0 proved the needed observation, provenance, repeat, correlation, and ordering helpers already exist. If a later pre-Work-Unit minimum-delta proof demonstrates that either telemetry path truly requires mutation, do not silently expand the Work Unit: stop before freeze and classify the need. A later accepted amendment may authorize only a mechanical current-owner binding with unchanged semantics and authority. Behavior, authority, schema, or module semantic change is `AMENDMENT_REQUIRED`. After Work Unit bytes are frozen and integrated, telemetry scope expansion is forbidden.

## C1-C7 semantic and non-authority boundaries

| Item | Preserved meaning |
| --- | --- |
| C1 | bounded observable process evidence only |
| C2 | existing `ProcessReview` / `build_process_review` owner |
| C3 | existing `FrameworkFeedback` owner |
| C4 | minimum non-authorizing Improvement Candidate through the existing compatible `framework_feedback` owner only |
| C5 | deterministic recurrence, current-relevance, and resolution classification |
| C6 | Harvest remains separate; no automatic conversion or promotion |
| C7 | non-authorizing Framework-management review input |

Private reasoning, chain-of-thought, chat transcripts, raw full tool traces, credentials/secrets, unbounded telemetry content, automatic learning, automatic optimization, automatic mutation, automatic Design/Plan/Work Unit creation, opaque ranking/scoring, feedback-as-authority, candidate-as-authority, Harvest auto-promotion, new schema, new module, new database/service/queue, State mutation, C8/C9, v2.7.4 release/publication, and Plugin work are prohibited.

`framework_feedback_authorizes_mutation()` remains false. Feedback and an Improvement Candidate cannot be Work Unit, Instruction, mutation, publication, release, policy, or automatic-selection authority.

## Dedicated one-time CREATE_ONLY bootstrap

```text
BOOTSTRAP_ID = framework-group-c-c1-c7-work-unit-bootstrap-001
BOOTSTRAP_REF = refs/tags/bootstrap/framework-group-c-c1-c7-work-unit-001
EXECUTOR_ROLE = USER_LOCAL
OPERATION = CREATE_ONLY
ONE_TIME = true
MUTATION_SCOPE = only .gpt-codex/work-units/framework-staged-closure-group-c-001.json
```

The future frozen bootstrap payload must bind repository ID `1366213495`, repository full name `xqc2098948451-byte/gpt-codex-framework`, default branch `main`, the fresh exact post-Design-and-Plan-integrated main SHA, State revision `17`, accepted Design-amendment and Plan-amendment immutable commit:path references, the Group C Work Unit ID/path, canonical Work Unit SHA-256, exact one-path CREATE_ONLY scope, v2.7.3 REMOTE_ACTIVE facts, `operation = CREATE_ONLY`, `executor_role = USER_LOCAL`, and `one_time = true`.

The bootstrap does not authorize C1-C7 implementation, State mutation, or COMMIT/PUSH for `CODEX_IMPLEMENTER`. After exact Work Unit integration, `GROUP_C_BOOTSTRAP = TERMINATED` and `GROUP_C_BOOTSTRAP_REUSE = FORBIDDEN`. All historical bootstrap tags and seed authorities are forbidden from reuse.

## Authority ordering

```text
Design amendment candidate -> independent Design review -> GPT adjudication -> exact USER Design acceptance -> bounded USER_LOCAL Design integration -> independent remote verification
-> Plan amendment authoring -> independent Plan review -> GPT adjudication -> exact USER Plan acceptance -> bounded USER_LOCAL Plan integration -> independent remote verification
-> fresh State 17/base observation -> canonical Group C Work Unit bytes freeze -> canonical bootstrap payload freeze -> independent bootstrap PRE_EXECUTION review -> GPT adjudication -> exact USER bootstrap approval
-> USER_LOCAL annotated bootstrap tag creation -> remote bootstrap verification -> USER_LOCAL exact one-path Work Unit materialization/commit/candidate push -> independent remote candidate verification -> conditional exact main fast-forward -> independent main verification -> bootstrap TERMINATED
-> native C1-C7 EXECUTION_INSTRUCTION -> independent PRE_EXECUTION review -> GPT adjudication -> execution authority -> CODEX_IMPLEMENTER mutation only within exact Work Unit scope
```

No C1 mutation may begin before this sequence completes. This dedicated bootstrap cannot become a factory.

## C8/C9, release, and Plugin boundaries

The C1-C7 Work Unit authorizes neither C8 nor C9, v2.7.4 packaging/publication, or a v2.7.4 REMOTE_ACTIVE claim. C1-C7 completion itself does not make v2.7.4 REMOTE_ACTIVE. Plugin remains deferred, needs its own later reauthorization, and has a lifecycle gate separate from Group C completion.

## Failure rules

| Condition | Required outcome |
| --- | --- |
| State revision is not 17 before Work Unit creation | `RECONCILIATION_REQUIRED` |
| main/base changes after freeze | `RECONCILIATION_REQUIRED` |
| Group C Work Unit path unexpectedly preexists | `RECONCILIATION_REQUIRED` |
| bootstrap ref unexpectedly preexists | `RECONCILIATION_REQUIRED` |
| telemetry enters owned scope without accepted pre-freeze minimum-delta amendment | `FAIL / SCOPE_EXPANSION` |
| new schema or module is required | `AMENDMENT_REQUIRED` |
| C8/C9/release/Plugin path enters C1-C7 mutation scope | `FAIL` |
| CODEX_IMPLEMENTER receives COMMIT/PUSH | `ROLE_AUTHORITY_CONFLICT` |
| bootstrap is reused | `RECONCILIATION_REQUIRED` |
| automatic evolution or mutation authority appears | `FAIL` |

## Independent Design review criteria

The isolated reviewer must assess root-cause correctness, C1-C7 semantic preservation, default-scope minimality, telemetry read-only boundary, Work Unit and bootstrap exactness, authority ordering, role-protocol compatibility, no generic bootstrap, no schema change, no new module, Harvest/C8-C9/Plugin boundaries, REMOTE_ACTIVE prerequisite, failure rules, and absence of placeholders. Important or Critical findings follow the existing `REVIEW_FINDING` route without editing this Design during review.
