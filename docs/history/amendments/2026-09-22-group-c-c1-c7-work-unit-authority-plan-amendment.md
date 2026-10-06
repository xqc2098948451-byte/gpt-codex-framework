# Group C C1-C7 Work Unit Authority Materialization Plan

**Purpose:** This Plan implements only the accepted authority-creation lifecycle needed to materialize the Group C C1-C7 Work Unit and reach native C1-C7 PRE_EXECUTION preparation. It does not plan or implement internal C1-C7 production code. C1-C7 behavioral semantics remain governed by the accepted staged-closure Master Plan and accepted authority Design; the later executable mutation is bounded by a native `EXECUTION_INSTRUCTION` and independent PRE_EXECUTION review.

**Authority basis:**

- Design amendment: `48e359de303135c24a551f1a3e87cfb685b0d1a9:docs/superpowers/specs/2026-09-22-group-c-c1-c7-work-unit-authority-design-amendment.md`
- Staged-closure Design: `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`
- Staged-closure Master Plan: `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`

## Global authority boundary

This Plan includes only Plan acceptance/integration; State/base freeze; canonical Work Unit and one-time CREATE_ONLY bootstrap construction; bootstrap review and explicit USER approval; USER_LOCAL tag and one-path Work Unit materialization; remote verification/termination; native Instruction preparation; independent PRE_EXECUTION review; GPT adjudication preparation; and a stop before implementation mutation.

It excludes C1-C7 production code, interfaces, RED/GREEN tests, a separate implementation Plan unless a later PRE review proves one necessary, C8/C9, v2.7.4 packaging/publication, State/schema/module/telemetry/Harvest/Plugin mutation, automatic evolution, and CODEX_IMPLEMENTER COMMIT/PUSH.

## Review focus

The independent Plan review tests exactly these authority risks:

1. State or main drifts after the authority freeze.
2. Canonical Work Unit bytes/hash differ from accepted approved bytes.
3. The bootstrap ref preexists or is reused.
4. Materialization changes anything except its exact one Work Unit path.
5. Native `EXECUTION_INSTRUCTION` exceeds the exact two implementation paths or grants CODEX_IMPLEMENTER Git transport authority.

## Task 1 — Plan acceptance and authority base freeze

**Files:** Modify only this Plan path. No Work Unit, bootstrap, State, production, schema, or test file is created or changed.

1. Independently review this candidate against all three immutable authority references and the accepted responsibility split: `WORK_UNIT_AND_BOOTSTRAP_AUTHORITY_ONLY` for this Plan; later C1-C7 execution under the accepted Master Plan and native Instruction.
2. GPT adjudicates the independent result. Only after exact USER Plan acceptance does USER_LOCAL fast-forward this Plan to `main`; independently verify the remote integration.
3. Define `ACCEPTED_PLAN_SHA` as the observed integrated 40-hex SHA, and set `GROUP_C_AUTHORITY_BASE_SHA = ACCEPTED_PLAN_SHA`. This is a runtime binding, not a guessed Plan literal.
4. Freshly require `origin/main == ACCEPTED_PLAN_SHA`, `STATE.revision == 17`, `STATE.next_action == GROUP_C_PRE_EXECUTION_REOBSERVATION_REQUIRED`, v2.7.3 `REMOTE_ACTIVE`, absent Group C Work Unit, and absent bootstrap ref. Any mismatch is `RECONCILIATION_REQUIRED`; do not freeze or mutate.

## Task 2 — canonical Work Unit builder and freeze

Use only the stdlib. Resolve `accepted_plan_sha` from the post-integration observation before calling this builder. This code is a Plan-contained canonical construction recipe, not a production C1-C7 interface and not a repository mutation.

```python
import json
import re


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def build_group_c_work_unit(
    *,
    accepted_plan_sha: str,
) -> dict[str, object]:
    if not isinstance(accepted_plan_sha, str) or not re.fullmatch(
        r"[0-9a-f]{40}", accepted_plan_sha
    ):
        raise ValueError("INVALID_ACCEPTED_PLAN_SHA")
    return {
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": "PRJ-FRAMEWORK-MANAGEMENT",
        "work_unit_id": "framework-staged-closure-group-c-001",
        "goal": (
            "Execute accepted Group C C1-C7 bounded evidence-to-management-review "
            "connections for v2.7.4 through the current framework_feedback owner without "
            "authorizing C8/C9, release, State mutation, Plugin, Harvest promotion, "
            "schema/module change, telemetry mutation, or automatic evolution."
        ),
        "scope": {
            "owned_paths": [
                ".gpt-codex/scripts/framework_feedback.py",
                ".gpt-codex/tests/test_framework_feedback.py",
            ],
            "excluded_paths": [
                ".gpt-codex/scripts/execution_telemetry.py",
                ".gpt-codex/tests/test_execution_telemetry.py",
                ".gpt-codex/STATE.json",
                ".gpt-codex/schemas/",
                ".gpt-codex/harvest/",
                "plugins/", "releases/", "dist/",
            ],
        },
        "acceptance": {
            "group": "C", "release": "2.7.4", "authority_scope": "C1_C7_ONLY",
            "requirements": [
                "v2.7.3 REMOTE_ACTIVE and State 17 prerequisite.",
                "C1 bounded observable process evidence only.",
                "C2 existing ProcessReview/build_process_review ownership.",
                "C3 existing FrameworkFeedback ownership.",
                "framework_feedback_authorizes_mutation() remains false.",
                "C4 Improvement Candidate is non-authorizing and remains in existing framework_feedback responsibility.",
                "C5 deterministic recurrence/current relevance/resolution classification; no opaque scoring.",
                "C6 Harvest remains a separate route; no automatic conversion/promotion.",
                "C7 emits non-authorizing Framework-management review input with NO_DECISION/NO_MUTATION default.",
                "execution_telemetry.py and its tests remain read-only.",
                "no new schema/module/database/service/queue.", "no State mutation.",
                "no C8/C9.", "no v2.7.4 release/publication.", "no Plugin.",
                "no automatic evolution/optimization.", "no CODEX_IMPLEMENTER COMMIT/PUSH.",
                "no scope expansion.",
            ],
        },
        "selected_extensions": {
            "skills": ["github-project-continuity"],
            "guardrails": ["universal-safety", "cross-project-context-binding", "github-repository-binding"],
            "fitness": [],
        },
        "permissions": {
            "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": ["COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION"],
        },
        "state": "AUTHORIZED", "basis_state_revision": 17,
        "evidence_refs": [
            ".gpt-codex/evidence/V2.7.3-REMOTE-PUBLICATION-VERIFICATION.json",
            ".gpt-codex/evidence/results/RESULT-V2.7.3-PUBLICATION.json",
        ],
        "artifact_refs": {
            "design": {
                "path": "docs/superpowers/specs/2026-09-22-group-c-c1-c7-work-unit-authority-design-amendment.md",
                "sha": "48e359de303135c24a551f1a3e87cfb685b0d1a9",
            },
            "plan": {
                "path": "docs/superpowers/plans/2026-09-22-group-c-c1-c7-work-unit-authority-plan-amendment.md",
                "sha": accepted_plan_sha,
            },
        },
    }
```

After Task 1's integration and fresh prerequisite pass, construct the object once, serialize with `canonical_json_bytes()`, and freeze `GROUP_C_WORK_UNIT_BYTE_COUNT`, `GROUP_C_WORK_UNIT_SHA256`, and `GROUP_C_WORK_UNIT_GIT_BLOB_SHA1`. Require UTF-8 without BOM, LF-only line endings, and no trailing whitespace. The freeze performs no repository mutation.

## Task 3 — canonical one-time bootstrap payload and freeze

Resolve all three arguments from current observations; do not serialize unresolved runtime placeholders.

```python
def build_group_c_bootstrap_payload(
    *,
    authority_base_sha: str,
    accepted_plan_sha: str,
    work_unit_sha256: str,
) -> dict[str, object]:
    for name, value, pattern in (
        ("authority_base_sha", authority_base_sha, r"[0-9a-f]{40}"),
        ("accepted_plan_sha", accepted_plan_sha, r"[0-9a-f]{40}"),
        ("work_unit_sha256", work_unit_sha256, r"[0-9a-f]{64}"),
    ):
        if not isinstance(value, str) or not re.fullmatch(pattern, value):
            raise ValueError(f"INVALID_{name.upper()}")
    if authority_base_sha != accepted_plan_sha:
        raise ValueError("AUTHORITY_BASE_PLAN_MISMATCH")
    return {
        "bootstrap_id": "framework-group-c-c1-c7-work-unit-bootstrap-001",
        "bootstrap_ref": "refs/tags/bootstrap/framework-group-c-c1-c7-work-unit-001",
        "repository_id": 1366213495,
        "repository_full_name": "xqc2098948451-byte/gpt-codex-framework",
        "default_branch": "main",
        "authority_base_sha": authority_base_sha,
        "expected_state_revision": 17,
        "group_c_work_unit_id": "framework-staged-closure-group-c-001",
        "group_c_work_unit_path": ".gpt-codex/work-units/framework-staged-closure-group-c-001.json",
        "group_c_work_unit_sha256": work_unit_sha256,
        "accepted_design_ref": {
            "commit_sha": "48e359de303135c24a551f1a3e87cfb685b0d1a9",
            "path": "docs/superpowers/specs/2026-09-22-group-c-c1-c7-work-unit-authority-design-amendment.md",
        },
        "accepted_plan_ref": {
            "commit_sha": accepted_plan_sha,
            "path": "docs/superpowers/plans/2026-09-22-group-c-c1-c7-work-unit-authority-plan-amendment.md",
        },
        "v2_7_3": {
            "release_phase": "REMOTE_ACTIVE",
            "finalization_main_sha": "e9be8754eced8bcce136515d85a8dfb7a8488ee5",
            "publication_work_sha": "fdcda12c6b0b94ac919d507ba8172ccce2f2dea2",
            "tag_object_sha": "66dcf92e418bf402183ab33ad545e632cff12e62",
            "tag": "v2.7.3", "tag_target_sha": "fdcda12c6b0b94ac919d507ba8172ccce2f2dea2",
            "release_id": 393538102, "asset_id": 580868060,
            "asset_name": "gpt-codex-framework-v2.7.3-bootstrap.zip",
            "asset_sha256": "8da1be98f9d7ea18fb3008685331956dfcb2232ac1ccfdf9085dd466a793a39d",
            "asset_size_bytes": 139774, "remote_version": "2.7.3",
            "state_sha256": "3fc78d5f71879ec4a79e518d0b853f6998c2cf54c3a8bc6d54af9260f079ebc3",
            "evidence_sha256": "5ad6cfc1b1c2a17853509d6c6991dd9625aacbe724b329417a0fc5f90ceb21ec",
            "result_sha256": "458e975331aefbe4473d74523aae6902effb21ee1ce9e8cd72f0da7984d28c4d",
        },
        "mutation_scope": [".gpt-codex/work-units/framework-staged-closure-group-c-001.json"],
        "operation": "CREATE_ONLY", "executor_role": "USER_LOCAL", "one_time": True,
    }
```

Serialize only with `canonical_json_bytes()`, then freeze `GROUP_C_BOOTSTRAP_PAYLOAD_BYTE_COUNT` and `GROUP_C_BOOTSTRAP_PAYLOAD_SHA256`. The annotated tag target is `authority_base_sha`; its message bytes are exactly the frozen payload bytes.

## Task 4 — bootstrap PRE review and explicit USER approval

Before any local tag or Work Unit write, a fresh independent reviewer verifies `origin/main == GROUP_C_AUTHORITY_BASE_SHA`; State 17; absent Work Unit/ref; exact accepted Design/Plan refs; exact Work Unit and bootstrap hashes; exact one-path scope; `CREATE_ONLY`; `USER_LOCAL`; `one_time`; no implementation authority; and no State/Plugin/C8/C9/release authority or historical reuse. GPT adjudicates the result.

Only an exact USER approval grants these bounded USER_LOCAL operations:

```text
USER_LOCAL_GROUP_C_BOOTSTRAP_TAG_CREATION_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_WU_COMMIT_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_WU_CANDIDATE_PUSH_AUTHORIZATION=APPROVE
USER_LOCAL_GROUP_C_WU_MAIN_FAST_FORWARD_AUTHORIZATION=APPROVE_IF_REMOTE_VERIFICATION_PASSES
```

These approvals neither grant C1-C7 implementation authority nor grant CODEX_IMPLEMENTER COMMIT/PUSH.

## Task 5 — USER_LOCAL Work Unit materialization and termination

After, and only after, Task 4's exact approval:

1. USER_LOCAL creates annotated `refs/tags/bootstrap/framework-group-c-c1-c7-work-unit-001` at `GROUP_C_AUTHORITY_BASE_SHA` with the exact frozen payload bytes. Freshly verify remote tag object, message, and target.
2. USER_LOCAL creates only `.gpt-codex/work-units/framework-staged-closure-group-c-001.json` with the frozen Work Unit bytes; makes a commit whose only changed path is that file and whose parent is `GROUP_C_AUTHORITY_BASE_SHA`; State remains unchanged.
3. USER_LOCAL non-force pushes candidate `governance/group-c-v2.7.4-work-unit-candidate-001`. An independent remote verification requires exact parent, exactly one changed path, frozen Work Unit SHA-256, State revision 17, unchanged publication facts, and unchanged bootstrap facts.
4. Only after PASS may USER_LOCAL fast-forward main. Independently verify `origin/main == WORK_UNIT_INTEGRATION_SHA`, exact Work Unit bytes/hashes, State 17, and no other mutation. Then record `GROUP_C_BOOTSTRAP = TERMINATED` and `GROUP_C_BOOTSTRAP_REUSE = FORBIDDEN`; the bootstrap cannot become a factory.

## Task 6 — native C1-C7 EXECUTION_INSTRUCTION preparation

Freshly inspect the then-current `.gpt-codex/schemas/instruction-envelope.schema.json`, `.gpt-codex/scripts/instruction_envelope.py`, and `.gpt-codex/scripts/role_communication.py` before construction. Use the native `build_instruction_envelope()` contract, not invented Python interfaces. The Instruction must be `EXECUTION_INSTRUCTION` with `issuer_role=GPT_ORCHESTRATOR`, scalar `executor_role=CODEX_IMPLEMENTER`, `return_role=GPT_ORCHESTRATOR`, `target_work_unit=framework-staged-closure-group-c-001`, `expected_state_revision=17`, `expected_base_sha=WORK_UNIT_INTEGRATION_SHA`, exact two `scope_paths`, the exact allowed and forbidden action lists from Task 2, and `completion_gate=GPT_DECISION`.

Bind exact Work Unit `target_work_unit_ref`, repository binding, accepted Design and Master Plan references where the current native contract supports them, plus evidence requirements. The bounded instruction text states that C1-C7 semantics derive from Master Plan §§C1-C7 and the accepted Design; telemetry is read-only; C8/C9/release/Plugin/State/schema/module changes are excluded; details resolve only in the existing two-path owner under this Instruction and PRE_EXECUTION review; and a separate implementation Plan is not required by default. It must not contain COMMIT/PUSH, telemetry mutation authority, or scope expansion.

## Task 7 — independent PRE_EXECUTION review and stop gate

A fresh CODEX_REVIEWER compares the exact native Instruction with the accepted authority Design, Master Plan C1-C7, exact Work Unit, State 17, current two mutable paths, telemetry read-only boundary, and production role protocol. If bounded, return `PRE_EXECUTION_REVIEW=PASS` and `NEXT=GPT_C1_C7_PREEXEC_ADJUDICATION`. If execution would require invented semantics, interfaces, or authority, return the complete `REVIEW_FINDING` to GPT and do not mutate. A separate detailed C1-C7 implementation Plan may be proposed only from that demonstrated finding. This Plan stops here; no C1-C7 mutation occurs under it.

## Failure and recovery rules

| Condition | Required outcome |
| --- | --- |
| State is not 17; main drifts after freeze; Work Unit/ref preexists; bootstrap reused | `RECONCILIATION_REQUIRED` |
| Work Unit candidate changes more than one path; Work Unit hash mismatch; State mutation; C8/C9/release/Plugin/automatic evolution authority | `FAIL` |
| Native Instruction scope is not exact two paths; telemetry mutation authority appears | `FAIL / SCOPE_EXPANSION` |
| CODEX_IMPLEMENTER receives COMMIT/PUSH | `ROLE_AUTHORITY_CONFLICT` |
| New schema/module authority appears | `AMENDMENT_REQUIRED` |

## Design coverage matrix

| Accepted authority-Design requirement | Plan section |
| --- | --- |
| Purpose/trigger; fresh prerequisites; authority ordering | Tasks 1, 4, 5, 7 |
| Exact default Work Unit; two-path scope; telemetry read-only | Task 2 and Task 6 |
| C1-C7 semantic boundaries | Work Unit acceptance in Task 2; native Instruction in Task 6; PRE review in Task 7 |
| One-time bootstrap; exact USER_LOCAL route; termination | Tasks 3–5 |
| C8/C9, release, Plugin, Harvest boundaries | Global boundary; Tasks 2, 5–7 |
| Failure rules | Failure and recovery rules |
| Staged-closure §§15–17 | Tasks 2, 6, 7: evidence-to-review flow, non-authority, Harvest separation |
| Staged-closure §§26–29 | Global boundary, Tasks 1–7, and failure rules: authority, sequencing, Plugin, deferred-work limits |

## Plan self-review, review, and push gate

Self-review requires `RESPONSIBILITY_SPLIT_CONSISTENT=YES`, no C1-C7 implementation code or TDD snippets, both builders complete, runtime bindings resolved before serialization, one authority ordering, native handoff complete, and no placeholders. Run:

```text
git diff --check
python -B .gpt-codex/scripts/validate_framework.py
python -B .gpt-codex/scripts/validate_project.py .
```

The diff from `origin/main` must be exactly this Plan path. Create exactly one local commit: `docs: plan group c c1-c7 authority materialization`.

Fresh independent review receives the accepted Design amendment, original staged-closure Design, Master Plan, current authority contracts, exact Plan candidate, and accepted USER responsibility split. It assesses: responsibility split, design coverage, Master Plan C1-C7 binding, ordering, both builder exactness/completeness, runtime binding, minimal scope, telemetry, USER gates, remote contract, termination, native handoff, PREEXEC stop, role protocol, non-authority/no-schema/no-module/Harvest/C8-C9/Plugin/no-State/failure/no-placeholder boundaries. It must not treat the explicit absence of downstream C1-C7 production code/TDD as a defect. Important or Critical findings stop without push.

Only if every dimension passes, non-force push `PLAN_SHA` to `governance/group-c-c1-c7-work-unit-authority-plan-amendment`; freshly verify its remote SHA, `origin/main == 48e359de303135c24a551f1a3e87cfb685b0d1a9`, and changed-path count 1. Record `PLAN_BLOB_SHA` and `PLAN_SHA256`.
