# Group C C8 Work Unit Authority Materialization Plan

> **Status:** Review-only candidate. This Plan is not acceptance, integration,
> Work Unit, bootstrap, Instruction, implementation, release, or mutation
> authority. It implements only the accepted C8 Design's future authority
> materialization lifecycle and stops before C8 test mutation.

**Goal:** Create a later, review-gated route to materialize one exact C8
test-only Work Unit and one dedicated, one-time bootstrap without granting
implementation, production-mutation, C9, release, State, Harvest, or Plugin
authority.

**Authority basis:**

- Accepted C8 Design: `bce6633c5bc8fca797efbf036303a92f7d5418d7:docs/superpowers/specs/2026-09-23-group-c-c8-work-unit-authority-design-amendment.md`.
- Staged-closure Design: `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`.
- Staged-closure Master Plan: `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`.
- C1-C7 authority precedent only: `48e359de303135c24a551f1a3e87cfb685b0d1a9:docs/superpowers/specs/2026-09-22-group-c-c1-c7-work-unit-authority-design-amendment.md` and `9cc4875fb997d1c5b57eb58ea3e5e895329ce7e8:docs/superpowers/plans/2026-09-22-group-c-c1-c7-work-unit-authority-plan-amendment.md`.
- C1-C7 completed base: `b281c427345ece6caf165189c89e1ff97fcab73a`.

The accepted C8 Design is bound to Git blob
`2affec3ea4c2be502295b9b8b85588ee2c7851ed` and SHA-256
`efa00287106dee38c1ef1ddc92f87950a247e06f1b970c59329d90dc217d2675`.

## Global authority constraints

This Plan's responsibility is `WORK_UNIT_AND_BOOTSTRAP_AUTHORITY_MATERIALIZATION_ONLY`.
C8 implementation responsibility is a later native `EXECUTION_INSTRUCTION`.
No separate C8 implementation Plan is required by default. If current
inspection proves new semantics, production mutation, a new
schema/module/service/database/queue, or broader scope, stop with
`AMENDMENT_REQUIRED`.

The C8 Work Unit is exactly
`framework-staged-closure-group-c-c8-001` at
`.gpt-codex/work-units/framework-staged-closure-group-c-c8-001.json`.
Its only mutable paths are:

1. `.gpt-codex/tests/test_framework_feedback.py`
2. `.gpt-codex/tests/test_windows_clean_room_e2e.py`

`.gpt-codex/tests/test_harness_handoff.py`,
`.gpt-codex/scripts/framework_feedback.py`, and all production code remain
read-only. The Plan never authorizes commit or push by `CODEX_IMPLEMENTER`.
It never authorizes C9, release, State mutation, Harvest mutation, Plugin
activity, schema/module work, automatic learning, optimization, evolution, or
authority synthesis.

All values explicitly named as future bindings below are unresolved until the
specified later gate. In particular, this candidate does not claim an
`ACCEPTED_PLAN_SHA`, `GROUP_C_C8_AUTHORITY_BASE_SHA`, Work Unit byte count,
Work Unit SHA-256, Work Unit Git blob SHA-1, bootstrap byte count, bootstrap
SHA-256, or `C8_WORK_UNIT_INTEGRATION_SHA`.

## Task 1 — Plan acceptance and authority-base freeze

After an independent Plan review PASS, GPT adjudication, exact USER acceptance,
an exact single-file `USER_LOCAL` Plan integration, and independent remote
verification, observe the integrated Plan commit as `ACCEPTED_PLAN_SHA` and
set `GROUP_C_C8_AUTHORITY_BASE_SHA = ACCEPTED_PLAN_SHA`. Do not guess either
value before that integration.

Immediately re-observe all of the following:

- `origin/main == ACCEPTED_PLAN_SHA`;
- `STATE.revision == 17`;
- the C8 Work Unit is absent; and
- `refs/tags/bootstrap/framework-group-c-c8-work-unit-001` is absent.

Any mismatch is `RECONCILIATION_REQUIRED`. Historical/C1-C7 bootstrap facts
are precedent only and cannot be reused.

## Task 2 — Freeze the canonical C8 Work Unit bytes

At the successful Task 1 gate, use only this deterministic stdlib-only recipe.
Before freezing, validate the resulting object against the then-current Work
Unit schema. Construct it exactly once, serialize it only with
`canonical_json_bytes`, require UTF-8 without BOM, LF-only line endings, and
no trailing whitespace, then freeze `C8_WORK_UNIT_BYTE_COUNT`,
`C8_WORK_UNIT_SHA256`, and `C8_WORK_UNIT_GIT_BLOB_SHA1`. These are runtime
facts; do not serialize unresolved placeholders.

```python
import json
import re


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_group_c_c8_work_unit(*, accepted_plan_sha: str) -> dict[str, object]:
    if not isinstance(accepted_plan_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", accepted_plan_sha):
        raise ValueError("INVALID_ACCEPTED_PLAN_SHA")
    return {
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": "PRJ-FRAMEWORK-MANAGEMENT",
        "work_unit_id": "framework-staged-closure-group-c-c8-001",
        "goal": ("Prove the accepted Group C C8 production-shaped closed evidence-to-management-review loop and candidate non-authority through test-only coverage of integrated C1-C7 behavior, without authorizing production-code mutation, C9, release, State mutation, Harvest promotion, Plugin work, schema/module change, or automatic evolution."),
        "scope": {
            "owned_paths": [".gpt-codex/tests/test_framework_feedback.py", ".gpt-codex/tests/test_windows_clean_room_e2e.py"],
            "excluded_paths": [".gpt-codex/tests/test_harness_handoff.py", ".gpt-codex/scripts/framework_feedback.py", ".gpt-codex/scripts/execution_telemetry.py", ".gpt-codex/STATE.json", ".gpt-codex/work-units/", ".gpt-codex/schemas/", ".gpt-codex/harvest/", "VERSION", "plugins/", "releases/", "dist/"],
        },
        "acceptance": {
            "group": "C", "task": "C8", "release": "2.7.4", "authority_scope": "C8_ONLY", "test_only_scope": True,
            "requirements": [
                "State revision 17 prerequisite.", "C1-C7 completed and integrated before C8 authority preparation.",
                "prove one production-shaped evidence -> ProcessReview -> FrameworkFeedback -> Improvement Candidate -> Framework-management review input loop.",
                "cover complete, duplicate/idempotent, stale or superseded, explicitly resolved, preservation, rejected-candidate, no-change, and incomplete/absent-source cases without inference.",
                "separate negative proves an Improvement Candidate alone cannot create or authorize Instruction, Work Unit, approved scope, framework mutation, publication, or release.",
                "framework_feedback_authorizes_mutation() remains false.", "no fixture mutates Framework State.",
                "test_harness_handoff.py remains read-only.", "framework_feedback.py and production helpers remain read-only.",
                "no production-code mutation.", "no State mutation.", "no schema/module/service/database/queue.",
                "no Harvest promotion.", "no Plugin.", "no C9.", "no v2.7.4 packaging/publication/release.",
                "no automatic learning/optimization/evolution/authority synthesis.", "no CODEX_IMPLEMENTER COMMIT/PUSH.", "no scope expansion.",
            ],
        },
        "selected_extensions": {"skills": ["github-project-continuity"], "guardrails": ["universal-safety", "cross-project-context-binding", "github-repository-binding"], "fitness": []},
        "permissions": {"authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"], "forbidden_actions": ["COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION"]},
        "state": "AUTHORIZED", "basis_state_revision": 17,
        "evidence_refs": [".gpt-codex/evidence/V2.7.3-REMOTE-PUBLICATION-VERIFICATION.json", ".gpt-codex/evidence/results/RESULT-V2.7.3-PUBLICATION.json"],
        "artifact_refs": {
            "design": {"path": "docs/superpowers/specs/2026-09-23-group-c-c8-work-unit-authority-design-amendment.md", "sha": "bce6633c5bc8fca797efbf036303a92f7d5418d7"},
            "plan": {"path": "docs/superpowers/plans/2026-09-23-group-c-c8-work-unit-authority-plan-amendment.md", "sha": accepted_plan_sha},
        },
    }
```

## Task 3 — Freeze the dedicated one-time bootstrap payload

Only after Task 2 succeeds, resolve every parameter at runtime and use this
complete deterministic recipe. Require `authority_base_sha == accepted_plan_sha`.
Freeze `C8_BOOTSTRAP_PAYLOAD_BYTE_COUNT` and `C8_BOOTSTRAP_PAYLOAD_SHA256` only
after canonical serialization. The annotated tag target is `authority_base_sha`;
its message bytes equal the frozen canonical payload bytes exactly. This task
does not itself create the tag or write a Work Unit.

```python
def build_group_c_c8_bootstrap_payload(*, authority_base_sha: str, accepted_plan_sha: str, work_unit_sha256: str) -> dict[str, object]:
    for name, value, pattern in (("authority_base_sha", authority_base_sha, r"[0-9a-f]{40}"), ("accepted_plan_sha", accepted_plan_sha, r"[0-9a-f]{40}"), ("work_unit_sha256", work_unit_sha256, r"[0-9a-f]{64}")):
        if not isinstance(value, str) or not re.fullmatch(pattern, value):
            raise ValueError(f"INVALID_{name.upper()}")
    if authority_base_sha != accepted_plan_sha:
        raise ValueError("AUTHORITY_BASE_PLAN_MISMATCH")
    return {
        "bootstrap_id": "framework-group-c-c8-work-unit-bootstrap-001",
        "bootstrap_ref": "refs/tags/bootstrap/framework-group-c-c8-work-unit-001",
        "repository_id": 1366213495, "repository_full_name": "xqc2098948451-byte/gpt-codex-framework", "default_branch": "main",
        "authority_base_sha": authority_base_sha, "expected_state_revision": 17,
        "group_c_c8_work_unit_id": "framework-staged-closure-group-c-c8-001",
        "group_c_c8_work_unit_path": ".gpt-codex/work-units/framework-staged-closure-group-c-c8-001.json",
        "group_c_c8_work_unit_sha256": work_unit_sha256,
        "accepted_design_ref": {"commit_sha": "bce6633c5bc8fca797efbf036303a92f7d5418d7", "path": "docs/superpowers/specs/2026-09-23-group-c-c8-work-unit-authority-design-amendment.md"},
        "accepted_plan_ref": {"commit_sha": accepted_plan_sha, "path": "docs/superpowers/plans/2026-09-23-group-c-c8-work-unit-authority-plan-amendment.md"},
        "c1_c7_completion_ref": {"commit_sha": "b281c427345ece6caf165189c89e1ff97fcab73a", "work_unit_path": ".gpt-codex/work-units/framework-staged-closure-group-c-001.json"},
        "mutation_scope": [".gpt-codex/work-units/framework-staged-closure-group-c-c8-001.json"],
        "operation": "CREATE_ONLY", "executor_role": "USER_LOCAL", "one_time": True,
    }
```

## Task 4 — Independent bootstrap PRE review and USER gate

Before any tag or Work Unit write, an independent review verifies exact main and
authority base, State 17, absent Work Unit/ref, exact accepted Design/Plan refs,
exact Work Unit and bootstrap bytes/hashes, one-path `CREATE_ONLY` scope,
`USER_LOCAL`, one-time behavior, no historical bootstrap reuse, and no C8
implementation, production, State, Harvest, Plugin, C9, release, or
`CODEX_IMPLEMENTER` COMMIT/PUSH authority. Only a PASS, GPT adjudication, and
exact USER approval may grant the later permissions:

```text
USER_LOCAL_GROUP_C_C8_BOOTSTRAP_TAG_CREATION_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_C8_WU_COMMIT_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_C8_WU_CANDIDATE_PUSH_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_C8_WU_MAIN_FAST_FORWARD_AUTHORIZATION=APPROVE_IF_REMOTE_VERIFICATION_PASSES
```

Those permissions grant no C8 implementation authority.

## Task 5 — USER_LOCAL Work Unit materialization and bootstrap termination

After Task 4's exact gate only, `USER_LOCAL` creates the dedicated annotated
bootstrap tag at the authority base and independently verifies its remote
target, message, and payload. It then materializes exactly the C8 Work Unit
file, creates a commit whose parent is `ACCEPTED_PLAN_SHA` and whose only
changed path is that file, and non-force pushes a dedicated candidate branch.

Independent remote verification must confirm parent, one changed path, Work
Unit SHA-256, Git blob SHA-1, State 17, unchanged Design/Plan facts, and
unchanged bootstrap facts. Only then may main fast-forward. Independently
verify the exact remote main identity, terminate bootstrap authority, and mark
reuse forbidden. Force push is never authorized.

## Task 6 — Native C8 EXECUTION_INSTRUCTION preparation

Only after Work Unit integration, freshly inspect
`.gpt-codex/schemas/instruction-envelope.schema.json`,
`.gpt-codex/scripts/instruction_envelope.py`, and
`.gpt-codex/scripts/role_communication.py`; use their current native builder,
not an invented interface. The later Instruction binds:

```text
message_type=EXECUTION_INSTRUCTION
issuer_role=GPT_ORCHESTRATOR
executor_role=CODEX_IMPLEMENTER
return_role=GPT_ORCHESTRATOR
target_work_unit=framework-staged-closure-group-c-c8-001
expected_state_revision=17
expected_base_sha=C8_WORK_UNIT_INTEGRATION_SHA
scope_paths=.gpt-codex/tests/test_framework_feedback.py,.gpt-codex/tests/test_windows_clean_room_e2e.py
completion_gate=GPT_DECISION
```

Its allowed and forbidden actions exactly equal the Work Unit permissions. It
states the accepted Design/Master Plan C8 derivation, exact two test paths,
read-only handoff fixture and production boundary, closed-loop proof,
candidate-non-authority negative, no State-mutating fixture, all excluded
authorities, and no `CODEX_IMPLEMENTER` COMMIT/PUSH or scope expansion.

## Task 7 — Independent C8 PRE_EXECUTION stop gate

A fresh `CODEX_REVIEWER` compares the exact accepted C8 Design, Master Plan
C8, integrated Work Unit, native Instruction, State 17, exact two-path scope,
read-only production boundary, role protocol, and non-authority invariants. If
bounded, return `PRE_EXECUTION_REVIEW = PASS` and
`NEXT = GPT_C8_PREEXEC_ADJUDICATION`. If production mutation, handoff-fixture
mutation, a new schema/module/service/database/queue, new semantics, wider
scope, or C9/release authority is needed, return `REVIEW_FINDING` and stop;
those needed changes are `AMENDMENT_REQUIRED`.

This authority Plan stops before C8 mutation. A later GPT adjudication may
permit `CODEX_IMPLEMENTER` to modify only the two owned test paths; future
post-execution review checks candidate identity and the non-authority proof.
C8 completion never authorizes C9, which needs a separate authority gate.

## Task 8 — Required C8 proof boundary

The later two-test-path execution proves one production-shaped chain:

```text
real execution/process evidence -> ProcessReview -> FrameworkFeedback -> Improvement Candidate -> Framework-management review input
```

It covers complete evidence, duplicate/idempotent input, stale/superseded
input, explicit resolution, preservation evidence, rejected candidate,
no-change, and incomplete/absent source without inference. A separate negative
proves an Improvement Candidate alone cannot create or authorize an
Instruction, Work Unit, approved scope, framework mutation, publication, or
release. `framework_feedback_authorizes_mutation()` remains false.

## Task 9 — Failure and recovery rules

| Condition | Required outcome |
| --- | --- |
| State != 17 before freeze; main/base drift; unexpected Work Unit/ref; historical bootstrap reuse; terminated bootstrap reuse | `RECONCILIATION_REQUIRED` |
| Work Unit candidate changes more than one path; Work Unit hash mismatch; bootstrap payload/hash mismatch | `FAIL` |
| C8 execution scope differs from the exact two test paths | `FAIL / SCOPE_EXPANSION` |
| Production or handoff-fixture mutation; schema/module/service/database/queue requirement | `AMENDMENT_REQUIRED` |
| State/Harvest/Plugin/C9/release authority; automatic authority/evolution | `FAIL` |
| `CODEX_IMPLEMENTER` COMMIT/PUSH | `ROLE_AUTHORITY_CONFLICT` |

## Task 10 — Candidate validation and non-authorizing transport

Before Plan acceptance, require this candidate's only repository delta to be
this Plan path, then run:

```text
git diff --check
python -B .gpt-codex/scripts/validate_framework.py
python -B .gpt-codex/scripts/validate_project.py .
```

Freeze `PLAN_BYTE_COUNT`, `PLAN_SHA256`, `PLAN_GIT_BLOB_SHA1`,
`PLAN_UTF8_NO_BOM`, `PLAN_LF_ONLY`, and `PLAN_TRAILING_WHITESPACE_FREE`.
The authoring lifecycle may create one candidate commit with parent
`bce6633c5bc8fca797efbf036303a92f7d5418d7` and only this changed path, then
non-force push it to
`governance/group-c-c8-work-unit-authority-plan-candidate-001`. It must not
update main. The candidate means `PLAN_CANDIDATE_PUBLISHED = YES`, but
`PLAN_ACCEPTED = NO`, `PLAN_AUTHORITY = NO`, `WORK_UNIT_AUTHORITY = NO`, and
`IMPLEMENTATION_AUTHORITY = NO`.

Independently verify the remote candidate head, exact parent, one changed path,
remote Plan SHA-256, remote Plan Git blob, remote main at the required base,
remote State 17, and absence of tag, release, Work Unit, and State mutation.
Any mismatch is `REMOTE_VERIFICATION_FAILED`; do not repair by modifying main.

## Design coverage matrix

| Accepted Design concern | Plan section |
| --- | --- |
| Purpose and missing C8 Work Unit authority root cause | Goal and global constraints |
| Exact Work Unit and test-only owned paths | Tasks 2 and 8 |
| Read-only production and handoff-fixture boundary | Global constraints; Tasks 2, 6, and 7 |
| Closed-loop semantics and candidate non-authority negative | Task 8 |
| Dedicated one-time bootstrap and authority ordering | Tasks 1, 3, 4, and 5 |
| Role protocol and no implementer commit/push | Tasks 4, 6, and 7 |
| C9/release/State/Harvest/Plugin exclusions | Global constraints; Tasks 2, 4, and 9 |
| Failure rules and no false runtime freeze | Global constraints; Tasks 1, 2, 3, and 9 |
