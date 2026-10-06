# Group C C8 Work Unit Authority Design Amendment

## Status and authority basis

This is a Design-only authority amendment. It is a candidate, not an
acceptance, Work Unit, Instruction, implementation, publication, or release
authority. It addresses only:

```text
ROOT_CAUSE = GROUP_C_C8_NATIVE_WORK_UNIT_CREATION_AUTHORITY_MISSING
```

The immutable semantic basis is preserved without reinterpretation:

- `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`
- `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`
- `48e359de303135c24a551f1a3e87cfb685b0d1a9:docs/superpowers/specs/2026-09-22-group-c-c1-c7-work-unit-authority-design-amendment.md`
- `9cc4875fb997d1c5b57eb58ea3e5e895329ce7e8:docs/superpowers/plans/2026-09-22-group-c-c1-c7-work-unit-authority-plan-amendment.md`

Fresh future preparation is bound to `origin/main =
b281c427345ece6caf165189c89e1ff97fcab73a`, State revision `17`, and the
remotely integrated C1-C7 Work Unit. The existing C1-C7 Work Unit remains
`C1_C7_ONLY`; it cannot be widened, reinterpreted, or used for C8.

## Future dedicated C8 Work Unit

The future Work Unit is exact and test-only:

```text
WORK_UNIT_ID = framework-staged-closure-group-c-c8-001
WORK_UNIT_PATH = .gpt-codex/work-units/framework-staged-closure-group-c-c8-001.json
KERNEL_VERSION = 2.0.0
SCHEMA_VERSION = 1
PROJECT_ID = PRJ-FRAMEWORK-MANAGEMENT
BASIS_STATE_REVISION = 17
STATE = AUTHORIZED
AUTHORITY_SCOPE = C8_ONLY
TEST_ONLY_SCOPE = YES
```

Its goal is to prove the accepted Group C C8 production-shaped
evidence-to-review loop and candidate non-authority using integrated C1-C7
behavior, without authorizing production-code mutation, C9, release, State
mutation, Harvest promotion, Plugin work, or automatic evolution.

Its default owned mutation paths are exactly:

1. `.gpt-codex/tests/test_framework_feedback.py`
2. `.gpt-codex/tests/test_windows_clean_room_e2e.py`

`.gpt-codex/tests/test_harness_handoff.py` is a read-only adjacent fixture
route. `.gpt-codex/scripts/framework_feedback.py`, telemetry, State, Work
Units, schemas, Harvest, VERSION, releases, dist, and plugins are read-only.
No production-code mutation is authorized merely to make C8 tests convenient.
If fresh preparation proves it necessary, execution stops as
`AMENDMENT_REQUIRED`.

Future permissions are exactly:

```text
authorized_actions = READ, TEST, VALIDATE, REPORT, MUTATE_APPROVED_SCOPE
forbidden_actions = COMMIT, PUSH, PUBLISH, AUTHORIZE, SCOPE_EXPANSION
```

Selected extensions follow the current framework conventions:
`github-project-continuity`, `universal-safety`,
`cross-project-context-binding`, and `github-repository-binding`.
Artifact references bind the immutable staged-closure Design and Master Plan
above.

## C8 proof boundary

The future test-only execution proves one production-shaped closed loop:

```text
real execution/process evidence
-> ProcessReview
-> FrameworkFeedback
-> Improvement Candidate
-> Framework-management review input
```

The bounded proof matrix covers complete evidence, duplicate/idempotent
evidence, stale or superseded evidence, explicit resolution, preservation
evidence, rejected candidate input, no-change, and incomplete or absent source
facts without inference. It separately proves that an Improvement Candidate
alone cannot create or authorize an Instruction, Work Unit, approved scope,
framework mutation, publication, or release. No fixture may mutate Framework
State.

`framework_feedback_authorizes_mutation()` remains false. Feedback,
ProcessReview, Improvement Candidate, Framework-management review input, and
test evidence are not authority.

C8 does not authorize automatic learning, optimization, action, Design, Plan,
Work Unit creation, mutation, release, policy update, opaque scoring, raw
private reasoning, chain-of-thought, chat transcripts, unrestricted raw tool
traces, credentials, secrets, State or schema mutation, a new module/service/
database/queue, Harvest promotion, Plugin work, C9, or v2.7.4
packaging/publication/release.

## Dedicated C8 materialization route

The C1-C7 bootstrap is historical precedent only and is terminated and reuse
forbidden. It cannot be reused or become a factory. A later accepted C8 Plan
must provide this dedicated one-time route:

```text
BOOTSTRAP_ID = framework-group-c-c8-work-unit-bootstrap-001
BOOTSTRAP_REF = refs/tags/bootstrap/framework-group-c-c8-work-unit-001
EXECUTOR_ROLE = USER_LOCAL
OPERATION = CREATE_ONLY
ONE_TIME = true
MUTATION_SCOPE = only .gpt-codex/work-units/framework-staged-closure-group-c-c8-001.json
```

This future bootstrap conveys no C8 implementation authority and no
`CODEX_IMPLEMENTER` COMMIT/PUSH authority. After exact C8 Work Unit
integration it is terminated and reuse is forbidden. This Design does not
freeze Work Unit JSON, bootstrap payload, hashes, or create a bootstrap ref;
those are later Plan/materialization responsibilities.

## Required authority ordering

```text
C8 authority Design candidate
-> independent Design review
-> GPT adjudication
-> exact USER Design acceptance
-> bounded USER_LOCAL Design integration
-> independent remote verification

-> C8 authority Plan authoring
-> independent Plan review
-> GPT adjudication
-> exact USER Plan acceptance
-> bounded USER_LOCAL Plan integration
-> independent remote verification

-> fresh State/base observation
-> canonical C8 Work Unit freeze
-> canonical one-time C8 bootstrap payload freeze
-> independent bootstrap PRE_EXECUTION review
-> GPT adjudication
-> exact USER bootstrap approval

-> USER_LOCAL bootstrap creation
-> exact one-path C8 Work Unit materialization
-> independent remote verification
-> conditional main fast-forward
-> bootstrap termination

-> native C8 EXECUTION_INSTRUCTION
-> independent PRE_EXECUTION review
-> GPT adjudication
-> C8 test-only execution

-> independent C8 post-execution/non-authority review
```

Only after C8 is complete and reviewed may a separate C9 authority gate be
considered. This amendment bundles neither C9 nor release authority.

## Failure rules and review criteria

- State revision other than `17`, main/base drift after a future freeze, an
  unexpected C8 Work Unit, an unexpected C8 bootstrap ref, or historical
  bootstrap reuse requires `RECONCILIATION_REQUIRED`.
- Owned paths beyond the exact two test paths require `FAIL / SCOPE_EXPANSION`.
- Production code or `test_harness_handoff.py` entering scope requires
  `AMENDMENT_REQUIRED`; schema/module/service/database/queue needs also require
  `AMENDMENT_REQUIRED`.
- State, Harvest, Plugin, C9, or release paths entering scope require `FAIL`.
- `CODEX_IMPLEMENTER` COMMIT/PUSH is `ROLE_AUTHORITY_CONFLICT`; automatic
  evolution or authority synthesis is `FAIL`.

Independent Design review verifies root-cause correctness, Master Plan C8
coverage, exact test-only scope, read-only harness-fixture boundary, candidate
non-authority proof, dedicated Work Unit/bootstrap identity, no bootstrap
factory behavior, authority ordering, State/base binding, role protocol,
failure rules, and absence of unresolved placeholders that impersonate frozen
runtime facts.
