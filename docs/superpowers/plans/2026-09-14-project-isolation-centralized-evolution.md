# Project Isolation & Centralized Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement P0-4 project isolation and centralized Framework evolution as an immutable read-only source plus explicit, privacy-minimized derived observations, without centralizing Project authority.

**Architecture:** `identity-context` remains the primary module for the strong Project/repository tuple and cross-Project resource decisions. `framework-core` publishes and validates a pure read-only evolution-source mapping; Projects evaluate it locally and may construct an explicit derived observation. The Framework-management index is a read-only aggregation of supplied enrollment/observation mappings: it owns neither a Project store nor an action channel.

**Tech Stack:** Python 3 standard library, dataclasses, JSON-compatible mappings, JSON Schema, unittest, existing GPT–Codex Framework governance modules.

**Spec:** docs/superpowers/specs/2026-09-14-project-isolation-centralized-evolution-design.md

## Global Constraints

- Begin implementation only after GPT verifies canonical `main` has not advanced incompatibly beyond `f49cd5afaa07aabaedac516d1c0e2c3524eef845`; never silently rebase the accepted Design/Plan lineage.
- Preserve `Framework publishes; Project decides`, Project-root authority, Framework-root auxiliary/read-only status, and Registry metadata-only routing.
- `PRIMARY_MODULE` is `identity-context` with exact responsibility `project and repository identity`; all seven existing modules are consumers or physical owners, and no eighth module is created.
- The authoritative identity tuple is `project_id`, `project_context_id`, `repository_id`, and `repository_full_name` when present. A display label, `project_name`, full name alone, Git remote alone, or filesystem presence cannot infer identity or enrollment.
- Use only `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, and `MODULE_ROUTE_UNRESOLVED` for frozen P0-3 semantics. Do not reintroduce any deprecated alias.
- `FRAMEWORK_SOURCE_INVALID`, `PROJECT_EVOLUTION_OBSERVATION_CURRENT`, `PROJECT_EVOLUTION_OBSERVATION_STALE`, `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT`, and `PROJECT_EVOLUTION_NOT_ENROLLED` are bounded P0-4 source/observation classifications only; they never alter a local compatibility outcome.
- No central Project `STATE`, shared `CONTROL`, shared Work Unit authority, batch mutation, automatic adoption/migration, retry queue, scheduler, daemon, central writable Project registry, slot lifecycle, or execution telemetry is permitted.
- Framework source/index/enrollment data must exclude raw `CONTROL`, `STATE`, Work Units, Result/Evidence contents, prompts, reasoning, credentials, tokens, source contents, environments, arbitrary logs, and extension payloads.
- `FRAMEWORK_MANAGEMENT` and `SELF_MANAGED` remain management-context classifications. They grant no authority over ordinary Projects and cannot enter consumer projection.
- Project Map remains `DERIVED_NAVIGATION_INDEX`; Resume remains a derived cache. Neither establishes identity, repairs a conflict, authorizes adoption, or authorizes execution.
- Every production task follows RED → minimal implementation → GREEN → regression → commit. Do not modify `STATE`, `CONTROL`, `VERSION`, release artifacts, tags, or publication metadata during implementation.

---

## File Map and module ownership

Every `MUTATED_ASSET` below resolves to one existing Registry module through an `OWNED_ASSETS` exact path or a unique `REQUIRED_TESTS` entry. The `Projection` column is the canonical v2.6.0 manifest classification to retain at implementation time. A code contract's classification is distinct from runtime record content: a `CONSUMER_REQUIRED` module can recognize a management classification, while a projected runtime management record is still rejected by Task 7.

| Exact path | Change type | Registry owner | Owning responsibility | Task(s) | Focused tests | Projection |
| --- | --- | --- | --- | --- | --- | --- |
| `.gpt-codex/scripts/context_binding.py` | MUTATED_ASSET | `identity-context` | Project/repository tuple, resource boundary, enrollment, observation, and index aggregation. | 1, 5, 6 | `test_context_binding.py`, `test_multi_project_github_isolation.py` | CONSUMER_REQUIRED |
| `.gpt-codex/scripts/github_repository_binding.py` | MUTATED_ASSET | `identity-context` | Verified repository mismatch and transfer binding. | 1, 6 | `test_github_repository_binding.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_context_binding.py` | MUTATED_ASSET | `identity-context` | Identity/resource/enrollment/index behavioral regression. | 1, 5, 6 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_github_repository_binding.py` | MUTATED_ASSET | `identity-context` | Repository binding and transfer regression. | 1, 6 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_multi_project_github_isolation.py` | MUTATED_ASSET | `identity-context` | Cross-Project identity/enrollment isolation regression. | 1, 5 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/kernel_rules.py` | MUTATED_ASSET | `framework-core` | Immutable read-only source classification and provenance rules. | 2 | `test_kernel_conformance.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_kernel_conformance.py` | MUTATED_ASSET | `framework-core` | Framework Evolution Source unit behavior. | 2 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/validate_framework.py` | MUTATED_ASSET | `framework-validation` | Framework-side source/index orchestration without Project ownership. | 2, 7 | `test_self_hosting_validator.py` | CONSUMER_REQUIRED |
| `.gpt-codex/scripts/validate_project.py` | MUTATED_ASSET | `framework-validation` | Local evaluation/adoption orchestration and exact failure propagation. | 3, 7 | `test_validator_context_binding.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_validator_context_binding.py` | MUTATED_ASSET | `framework-validation` | Local evolution/adoption and observation-as-instruction regression. | 3, 5, 7 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_self_hosting_validator.py` | MUTATED_ASSET | `framework-validation` | Source-validator integration and management/self-hosting non-expansion. | 2, 3, 7 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/role_communication.py` | MUTATED_ASSET | `role-communication` | Metadata cannot acquire instruction/action authority. | 4 | `test_role_authority.py` | CONSUMER_REQUIRED |
| `.gpt-codex/scripts/instruction_envelope.py` | MUTATED_ASSET | `role-communication` | Reject executable source/index metadata in instruction rendering. | 4 | `test_instruction_role_contract.py` | CONSUMER_REQUIRED |
| `.gpt-codex/scripts/result_return.py` | MUTATED_ASSET | `role-communication` | Preserve result authority boundary for evolution metadata. | 4 | `test_result_contract_schema.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_role_authority.py` | MUTATED_ASSET | `role-communication` | Metadata authority denial. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_instruction_role_contract.py` | MUTATED_ASSET | `role-communication` | Instruction envelope authority regression. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_result_contract_schema.py` | MUTATED_ASSET | `role-communication` | Result envelope authority regression. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/project_navigation.py` | MUTATED_ASSET | `navigation-continuity` | Derived Map identity boundary. | 4 | `test_project_navigation.py` | CONSUMER_REQUIRED |
| `.gpt-codex/scripts/continuity_resume.py` | MUTATED_ASSET | `navigation-continuity` | Derived Resume identity boundary. | 4 | `test_continuity_resume.py`, `test_context_window_resume.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_project_navigation.py` | MUTATED_ASSET | `navigation-continuity` | Foreign/ambiguous Map failure. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_continuity_resume.py` | MUTATED_ASSET | `navigation-continuity` | Foreign/ambiguous Resume failure. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_context_window_resume.py` | MUTATED_ASSET | `navigation-continuity` | Valid local derived-continuity regression. | 4 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/git_continuity.py` | MUTATED_ASSET | `git-continuity` | Independent old/new repository evidence for transfer. | 6 | `test_git_continuity.py`, `test_remote_verification.py` | CONSUMER_REQUIRED |
| `.gpt-codex/tests/test_git_continuity.py` | MUTATED_ASSET | `git-continuity` | Repository-transfer evidence requirement. | 6 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_remote_verification.py` | MUTATED_ASSET | `git-continuity` | Remote evidence stays non-authoritative. | 6 | self | MANAGEMENT_ONLY |
| `.gpt-codex/scripts/consumer_projection.py` | MUTATED_ASSET | `release-projection` | Structured management-record rejection. | 7 | `test_consumer_projection.py` | MANAGEMENT_ONLY |
| `.gpt-codex/release/consumer-projection-manifest.json` | MUTATED_ASSET | `release-projection` | Exact Design/Plan classification closure; manifest self-classification remains management-only. | 7 | `test_consumer_projection.py`, `test_consumer_runtime_closure.py` | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_consumer_projection.py` | MUTATED_ASSET | `release-projection` | Management-record projection rejection. | 7 | self | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_consumer_runtime_closure.py` | MUTATED_ASSET | `release-projection` | Consumer inventory closure. | 7 | self | MANAGEMENT_ONLY |

### Verify-only regression assets

| Exact path | Change type | Execution purpose | Command | Projection |
| --- | --- | --- | --- | --- |
| `.gpt-codex/tests/test_framework_module_validation.py` | VERIFY_ONLY_REGRESSION | Existing cross-module Framework-validation regression; no mutation target and no Registry owner is inferred. | `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py'` | MANAGEMENT_ONLY |
| `.gpt-codex/tests/test_framework_project_separation.py` | VERIFY_ONLY_REGRESSION | Existing historical separation regression; no mutation target and no Registry owner is inferred. | `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'` | MANAGEMENT_ONLY |

No schema or template file is changed: P0-4 uses additive, in-memory JSON-compatible contract mappings and existing Project-local authority structures. `framework_module_routing.py` is not changed; its responsibility-first route remains descriptive, never executable.

## Shared interfaces and decision order

The implementation introduces only the following interfaces. `Mapping[str, Any]` values are transport-neutral data; the functions never read/write a Project root unless the existing caller already owns that Project-local action.

```python
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class ProjectResourceBinding:
    project_id: str
    project_context_id: str
    repository_id: str
    repository_full_name: str | None
    resource_type: str

@dataclass(frozen=True)
class EvolutionSourceDecision:
    classification: str
    reason: str
    source: dict[str, Any] | None

def evaluate_cross_project_resource_boundary(
    active_identity: ProjectIdentity,
    resource: Mapping[str, Any],
    *, resource_type: str, analysis_only: bool = False,
) -> ContextDecision: ...

def validate_framework_evolution_source(
    source: Mapping[str, Any],
) -> EvolutionSourceDecision: ...

def evaluate_project_evolution(
    project_control: Mapping[str, Any], source: Mapping[str, Any],
) -> dict[str, Any]: ...

def build_project_evolution_observation(
    project_control: Mapping[str, Any], evaluation: Mapping[str, Any],
    enrollment: Mapping[str, Any], *, observed_at: str, local_revision_ref: str,
) -> dict[str, Any]: ...

def classify_framework_evolution_index(
    enrollments: Sequence[Mapping[str, Any]], observations: Sequence[Mapping[str, Any]],
    *, now: str, stale_after_seconds: int,
) -> list[dict[str, Any]]: ...
```

The first applicable condition wins: malformed/missing/inferred strong identity returns `PROJECT_IDENTITY_INVALID`; a complete foreign context returns `CROSS_PROJECT_CONTEXT_MISMATCH`; a verified repository contradiction returns `GITHUB_REPOSITORY_MISMATCH`; attempted use of source/index/foreign metadata as local authority returns `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`; and an adoption lacking local decision/Work Unit/Role authority returns `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`. Derived Map/Resume and fleet observations are evaluated only after those checks.

## Mandatory Implementation Baseline Preflight

This hard execution gate is not a production Task and does not change `TASK_COUNT = 7`. Before Task 1, the executor must run:

```bash
git fetch origin
git rev-parse origin/main
git rev-parse HEAD
git merge-base --is-ancestor 8125e13958e548ed24c53a978c8d86602d69c253 HEAD
git merge-base --is-ancestor 37f9fdcc481ba6943efe184eb533bd3823b32bc8 HEAD
python -c "from pathlib import Path; import runpy; routing = runpy.run_path('.gpt-codex/scripts/framework_module_routing.py'); decision = routing['route_responsibility'](Path('.'), 'identity-context', 'project and repository identity', planned_assets=['.gpt-codex/scripts/context_binding.py', '.gpt-codex/scripts/github_repository_binding.py', '.gpt-codex/scripts/kernel_rules.py', '.gpt-codex/scripts/validate_framework.py', '.gpt-codex/scripts/validate_project.py', '.gpt-codex/scripts/role_communication.py', '.gpt-codex/scripts/instruction_envelope.py', '.gpt-codex/scripts/result_return.py', '.gpt-codex/scripts/project_navigation.py', '.gpt-codex/scripts/continuity_resume.py', '.gpt-codex/scripts/git_continuity.py', '.gpt-codex/scripts/consumer_projection.py', '.gpt-codex/release/consumer-projection-manifest.json']); print(decision.outcome, decision.primary_module, ','.join(decision.affected_modules))"
git status --short
```

Record `accepted_design_sha=8125e13958e548ed24c53a978c8d86602d69c253`, `accepted_plan_sha=37f9fdcc481ba6943efe184eb533bd3823b32bc8`, `observed_origin_main_sha`, `expected_canonical_base_sha`, `design_plan_ancestry_result`, `registry_route_result`, `changed_contract_conflict_result`, `worktree_status`, and `blockers`. The expected canonical base is `f49cd5afaa07aabaedac516d1c0e2c3524eef845`. The route call receives only mutated production assets; the File Map's unique `REQUIRED_TESTS` ownership is the separate test-path evidence.

If `origin/main` equals that SHA, accepted Design/Plan ancestry is intact, Registry routing returns only `identity-context` for `project and repository identity`, the Design/Plan diff contains no contradictory contract drift, and the worktree is clean, set `BASELINE_PRECHECK = PASS`. GPT must independently verify the recorded evidence and `BLOCKERS = NONE` before Task 1 starts; `GPT_BASELINE_VERIFICATION = REQUIRED`.

If `origin/main` differs from the expected SHA, if either ancestry check fails, or if a contradictory Registry/contract change is found, stop with `RESULT = RECONCILIATION_REQUIRED`. No production Task executes; Codex must not decide that a newer `main` is compatible, and may not silently rebase, merge, or rewrite accepted history.

## Implementation Tasks

### Task 1: Strong identity and cross-Project resource boundary foundation

**Files:**
- Modify: `.gpt-codex/scripts/context_binding.py`
- Modify: `.gpt-codex/scripts/github_repository_binding.py`
- Modify: `.gpt-codex/tests/test_context_binding.py`
- Modify: `.gpt-codex/tests/test_github_repository_binding.py`
- Modify: `.gpt-codex/tests/test_multi_project_github_isolation.py`

**Interfaces:**
- Produces `ProjectResourceBinding` and `evaluate_cross_project_resource_boundary(active_identity, resource, *, resource_type, analysis_only=False) -> ContextDecision`.
- Accepts `resource_type` exactly from `CONTROL`, `STATE`, `WORK_UNIT`, `INSTRUCTION`, `RESULT`, `EVIDENCE`, `REPOSITORY_BINDING`, `EXTENSION_CONFIGURATION`, `PROJECT_MAP`, and `RESUME`.
- Returns `ALLOW` only for a complete matching binding; foreign complete context returns `CROSS_PROJECT_CONTEXT_MISMATCH`; malformed/partial/conflicting/inferred binding returns `PROJECT_IDENTITY_INVALID`; repository contradiction returns `GITHUB_REPOSITORY_MISMATCH`. Rejected resources have `packet_status="QUARANTINED"`; analysis-only returns a non-executable diagnostic.

- [ ] **Step 1: Write failing behavioral tests.** Add a parameterized `test_resource_boundary_rejects_foreign_or_ambiguous_authority_resources` in `test_context_binding.py` for all ten exact `resource_type` values. Assert a matching tuple is `ALLOW` and non-executable; replace just `project_context_id` with the foreign UUID and assert `CROSS_PROJECT_CONTEXT_MISMATCH` plus `QUARANTINED`; remove `repository_id` and assert `PROJECT_IDENTITY_INVALID`; replace the verified full name while retaining the ID and assert `GITHUB_REPOSITORY_MISMATCH`. In `test_github_repository_binding.py`, assert a malformed CONTROL binding returns `PROJECT_IDENTITY_INVALID`, not the legacy generic repository-conflict code.

```python
decision = evaluate_cross_project_resource_boundary(
    load_project_identity(valid_control()),
    {"project_id": "PRJ-001", "project_context_id": FOREIGN_CONTEXT_ID,
     "repository_id": "123", "repository_full_name": "owner/repo"},
    resource_type="STATE",
)
self.assertEqual((decision.reason, decision.packet_status),
                 ("CROSS_PROJECT_CONTEXT_MISMATCH", "QUARANTINED"))
```

- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'`. Expected: import failure for `evaluate_cross_project_resource_boundary` and assertion failure for the legacy generic repository-conflict branch.
- [ ] **Step 3: Implement the minimum boundary.** Add the immutable binding dataclass and evaluation function to `context_binding.py`; do not accept display names, Git remotes, or paths as identity. Normalize `github_repository_binding._binding_from_control` failure and `scan_repository_compatibility` malformed configured identity to `PROJECT_IDENTITY_INVALID`; retain `GITHUB_REPOSITORY_MISMATCH` only when observed repository data contradicts valid binding.
- [ ] **Step 4: Run GREEN.** Run the two RED commands again. Expected: PASS with no resource copied, merged, executed, or used as local authority.
- [ ] **Step 5: Run identity regressions.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected: PASS; legacy identity and repository behavior retain the frozen exact codes.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/scripts/github_repository_binding.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_github_repository_binding.py .gpt-codex/tests/test_multi_project_github_isolation.py` then `git commit -m "feat: enforce cross-project resource boundaries"`.

### Task 2: Immutable read-only Framework Evolution Source

**Files:**
- Modify: `.gpt-codex/scripts/kernel_rules.py`
- Modify: `.gpt-codex/tests/test_kernel_conformance.py`
- Modify: `.gpt-codex/scripts/validate_framework.py`
- Modify: `.gpt-codex/tests/test_self_hosting_validator.py`

**Interfaces:**
- Produces `validate_framework_evolution_source(source) -> EvolutionSourceDecision`.
- Valid source requires `classification == "READ_ONLY_EVOLUTION_SOURCE"`, nonempty `framework_version`, immutable `source_provenance` mapping containing `commit_sha`, `compatibility_rules` mapping, and boolean `migration_available`.
- Invalid/missing/mutable/action-bearing source returns `FRAMEWORK_SOURCE_INVALID`; the returned decision has no Project action, Work Unit, `STATE`, extension, or Role authorization field.

- [ ] **Step 1: Write failing behavioral tests.** Add `test_framework_evolution_source_is_read_only_and_provenance_bound` and `test_action_bearing_or_incomplete_evolution_source_is_invalid` to `test_kernel_conformance.py`. Use a valid mapping and a mapping containing `target_work_unit`; assert the first returns `READ_ONLY_EVOLUTION_SOURCE` and the second returns `FRAMEWORK_SOURCE_INVALID`.

```python
source = {"classification": "READ_ONLY_EVOLUTION_SOURCE", "framework_version": "2.6.0",
          "source_provenance": {"commit_sha": "a" * 40},
          "compatibility_rules": {"minimum_project_version": "2.0.0"},
          "migration_available": False}
self.assertEqual(validate_framework_evolution_source(source).classification,
                 "READ_ONLY_EVOLUTION_SOURCE")
```

- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_kernel_conformance.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'`. Expected: import failure for `validate_framework_evolution_source` and missing Framework-validator source integration assertion.
- [ ] **Step 3: Implement the minimum source validator.** In `kernel_rules.py`, add `EvolutionSourceDecision`, a frozen allowed-key set, and `validate_framework_evolution_source`. Reject unknown keys that imply execution (`authorized_actions`, `target_work_unit`, `state_revision`, `command`, `retry`, `queue`) and reject absent/invalid provenance. In `validate_framework.py`, validate only Framework-owned source fixtures when present; it reports invalid source but never creates one.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_kernel_conformance.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'`. Expected: PASS.
- [ ] **Step 5: Run governance regressions.** Run `python .gpt-codex/scripts/validate_framework.py` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py'`. Expected: PASS; the latter is VERIFY_ONLY_REGRESSION, Registry routing and Framework version remain unchanged.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/kernel_rules.py .gpt-codex/scripts/validate_framework.py .gpt-codex/tests/test_kernel_conformance.py .gpt-codex/tests/test_self_hosting_validator.py` then `git commit -m "feat: validate read-only framework evolution sources"`.

### Task 3: Local evaluation and explicit adoption decision boundary

**Files:**
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/tests/test_validator_context_binding.py`
- Modify: `.gpt-codex/tests/test_self_hosting_validator.py`

**Interfaces:**
- Produces `evaluate_project_evolution(project_control, source) -> dict[str, Any]` with `classification`, `reason`, `mutated=False`, `adoption_authorized=False`, and source provenance reference.
- Keeps `evaluate_framework_compatibility` as the compatibility classifier and preserves exactly `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, and `CONFLICT`.
- Extends `validate_framework_adoption(project_control, instruction, work_unit, *, current_state_revision, source=None) -> list[str]`; it accepts migration only after valid identity, valid source, matching Project Work Unit/revision, and Role Protocol action authority. Otherwise it returns the exact first applicable frozen failure.

- [ ] **Step 1: Write failing behavioral tests.** In `test_validator_context_binding.py`, add `test_project_evolution_evaluation_is_read_only` and `test_adoption_requires_local_authority_not_source_or_observation`. Assert source evaluation returns `mutated is False` and all five compatibility outcomes remain possible; assert an instruction carrying `FRAMEWORK_EVOLUTION_SOURCE` classification but no authorized local Work Unit yields `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`; assert a foreign `project_context_id` yields `CROSS_PROJECT_CONTEXT_MISMATCH`.

```python
source = {"classification": "READ_ONLY_EVOLUTION_SOURCE", "framework_version": "2.6.0",
          "source_provenance": {"commit_sha": "a" * 40},
          "compatibility_rules": {"compatible": True, "reusable": False},
          "migration_available": False}
evaluation = evaluate_project_evolution(valid_control(), source)
self.assertFalse(evaluation["mutated"])
self.assertFalse(evaluation["adoption_authorized"])
self.assertIn(evaluation["classification"], {
    "NO_ACTION", "OPTIONAL_REUSE", "RECOMMENDED_UPGRADE",
    "REQUIRED_MIGRATION", "CONFLICT",
})
```

- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: import failure for `evaluate_project_evolution` and failed adoption boundary assertions.
- [ ] **Step 3: Implement the minimum local-only evaluation.** In `validate_project.py`, call `load_project_identity` and `validate_framework_evolution_source` before compatibility classification. Map malformed identity to `PROJECT_IDENTITY_INVALID`, foreign context to `CROSS_PROJECT_CONTEXT_MISMATCH`, verified repository contradiction to `GITHUB_REPOSITORY_MISMATCH`, and action-bearing external metadata to `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`. Do not write CONTROL/STATE or construct a Work Unit. Extend adoption validation only to verify an already supplied local Work Unit and Role authority; it must never create either.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: PASS.
- [ ] **Step 5: Run management and historical regressions.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected: PASS; self-hosting does not expand ordinary authority and the latter remains VERIFY_ONLY_REGRESSION.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_self_hosting_validator.py` then `git commit -m "feat: keep framework evolution evaluation project-local"`.

### Task 4: Role, instruction/result, Project Map, and Resume non-authority

**Files:**
- Modify: `.gpt-codex/scripts/role_communication.py`
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Modify: `.gpt-codex/scripts/result_return.py`
- Modify: `.gpt-codex/scripts/project_navigation.py`
- Modify: `.gpt-codex/scripts/continuity_resume.py`
- Modify: `.gpt-codex/tests/test_role_authority.py`
- Modify: `.gpt-codex/tests/test_instruction_role_contract.py`
- Modify: `.gpt-codex/tests/test_result_contract_schema.py`
- Modify: `.gpt-codex/tests/test_project_navigation.py`
- Modify: `.gpt-codex/tests/test_continuity_resume.py`
- Modify: `.gpt-codex/tests/test_context_window_resume.py`

**Interfaces:**
- Produces `validate_evolution_metadata_authority(metadata: Mapping[str, object]) -> list[str]` in `role_communication.py`; it returns `PROJECT_AUTHORITY_BOUNDARY_VIOLATION` for `READ_ONLY_EVOLUTION_SOURCE`, `DERIVED_OBSERVATION_ONLY`, or `FRAMEWORK_MANAGEMENT_METADATA` presented with executable actions, Work Unit targets, state revision commands, or local mutation claims.
- `validate_navigation_identity` and `load_continuity_resume` call the Task 1 boundary evaluator for Project Map/Resume mappings and propagate frozen failures rather than treating derived data as a repair path.

- [ ] **Step 1: Write failing behavioral tests.** Add a test in `test_role_authority.py` that passes `{ "classification": "DERIVED_OBSERVATION_ONLY", "authorized_actions": ["MUTATE_APPROVED_SCOPE"] }` and expects `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`. Add Map and Resume fixtures with a foreign context in `test_project_navigation.py` and `test_continuity_resume.py`; assert each fails closed with `CROSS_PROJECT_CONTEXT_MISMATCH`, not a route or cache repair.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_role_authority.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_project_navigation.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_continuity_resume.py'`. Expected: missing metadata validator and derived artifacts not yet rejected through the P0-4 boundary.
- [ ] **Step 3: Implement the minimum non-authority checks.** Add the metadata validator and invoke it from instruction/result builders before rendering an executable action. In navigation/Resume, create a resource mapping from existing identity fields and call the Task 1 evaluator before module routing, hot-file selection, or resume mode. Preserve existing `DERIVED_NAVIGATION_INDEX` and `DERIVED_CACHE` classifications; do not add adoption, execution, or repair behavior.
- [ ] **Step 4: Run GREEN.** Run the three RED commands again plus `python -m unittest discover -s .gpt-codex/tests -p 'test_instruction_role_contract.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_result_contract_schema.py'`. Expected: PASS.
- [ ] **Step 5: Run continuity regression.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_window_resume.py'`. Expected: PASS; a valid local Resume remains derived optimization only.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/role_communication.py .gpt-codex/scripts/instruction_envelope.py .gpt-codex/scripts/result_return.py .gpt-codex/scripts/project_navigation.py .gpt-codex/scripts/continuity_resume.py .gpt-codex/tests/test_role_authority.py .gpt-codex/tests/test_instruction_role_contract.py .gpt-codex/tests/test_result_contract_schema.py .gpt-codex/tests/test_project_navigation.py .gpt-codex/tests/test_continuity_resume.py .gpt-codex/tests/test_context_window_resume.py` then `git commit -m "feat: keep derived evolution metadata non-authoritative"`.

### Task 5: Explicit enrollment and privacy-minimized Project Evolution Observation

**Files:**
- Modify: `.gpt-codex/scripts/context_binding.py`
- Modify: `.gpt-codex/tests/test_context_binding.py`
- Modify: `.gpt-codex/tests/test_multi_project_github_isolation.py`
- Modify: `.gpt-codex/tests/test_validator_context_binding.py`

**Interfaces:**
- Produces `validate_project_evolution_enrollment(project_control, enrollment) -> ContextDecision` and `build_project_evolution_observation(project_control, evaluation, enrollment, *, observed_at, local_revision_ref) -> dict[str, Any]`.
- Enrollment requires `explicit_enrollment is True`, the complete strong tuple, and `transport` exactly `MANUAL`, `PROJECT_PUSH`, or `PROJECT_PULL`. Discovery-like fields alone deny with `PROJECT_IDENTITY_INVALID`.
- Observation has classification `DERIVED_OBSERVATION_ONLY` and only identity tuple, source version/provenance digest, local compatibility outcome, observed time, local revision reference, and bounded result/evidence reference. It contains neither action fields nor prohibited raw/sensitive fields.

- [ ] **Step 1: Write failing behavioral tests.** Add `test_explicit_enrollment_is_not_discovery` and `test_observation_is_minimized_and_non_authoritative` in `test_context_binding.py`, with cross-Project transport assertions in `test_multi_project_github_isolation.py` and validation orchestration assertion in `test_validator_context_binding.py`. Use `{ "repository_full_name": "owner/repo" }` without `explicit_enrollment` and assert `PROJECT_IDENTITY_INVALID`; for valid enrollment, assert the observation key set excludes `control`, `state`, `work_unit`, `result`, `evidence`, `prompt`, `reasoning`, `credential`, `token`, `source_content`, `environment`, `log`, and `extensions`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: imports for enrollment/observation interfaces do not exist.
- [ ] **Step 3: Implement the minimum enrollment/observation constructors.** In `context_binding.py`, validate explicit identity-bound enrollment without I/O or auto-registration. Build a new mapping only from Design-approved fields; reject action-bearing input with `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`. Never read Git remote, scan the filesystem, mutate CONTROL/STATE, or retain arbitrary payloads.
- [ ] **Step 4: Run GREEN.** Run the three RED commands again. Expected: PASS.
- [ ] **Step 5: Run isolation regression.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'`. Expected: PASS; foreign and partial enrollment remain non-authoritative diagnostics only.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_multi_project_github_isolation.py .gpt-codex/tests/test_validator_context_binding.py` then `git commit -m "feat: add bounded project evolution observations"`.

### Task 6: Management index, staleness, rename, retirement, and repository transfer

**Files:**
- Modify: `.gpt-codex/scripts/context_binding.py`
- Modify: `.gpt-codex/scripts/github_repository_binding.py`
- Modify: `.gpt-codex/scripts/git_continuity.py`
- Modify: `.gpt-codex/tests/test_context_binding.py`
- Modify: `.gpt-codex/tests/test_github_repository_binding.py`
- Modify: `.gpt-codex/tests/test_git_continuity.py`
- Modify: `.gpt-codex/tests/test_remote_verification.py`

**Interfaces:**
- Produces `classify_framework_evolution_index(enrollments, observations, *, now, stale_after_seconds) -> list[dict[str, Any]]` and `validate_repository_transfer(old_enrollment, new_enrollment, *, old_repository_evidence, new_repository_evidence) -> ContextDecision`.
- Index output is `FRAMEWORK_MANAGEMENT_METADATA` plus a derived classification: `PROJECT_EVOLUTION_OBSERVATION_CURRENT`, `PROJECT_EVOLUTION_OBSERVATION_STALE`, `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT`, or `PROJECT_EVOLUTION_NOT_ENROLLED`.
- Rename changes optional display metadata only after the same strong tuple is supplied. Retirement marks enrollment retired and accepts no new observation. Transfer requires complete old/new tuples plus independent old/new Git continuity evidence; repository full-name change alone returns `PROJECT_IDENTITY_INVALID`.

- [ ] **Step 1: Write failing behavioral tests.** Add tests for current/stale/conflicting/not-enrolled index rows to `test_context_binding.py`; add `test_repository_transfer_requires_old_and_new_repository_evidence` to `test_git_continuity.py`. Assert an old timestamp becomes `PROJECT_EVOLUTION_OBSERVATION_STALE` with no `mutated` or action field; assert conflicting tuple becomes `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT`; assert missing enrollment becomes `PROJECT_EVOLUTION_NOT_ENROLLED`; assert full-name-only transfer is `PROJECT_IDENTITY_INVALID`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_git_continuity.py'`. Expected: missing index/transfer interfaces.
- [ ] **Step 3: Implement the minimum read-only aggregation.** In `context_binding.py`, aggregate supplied mappings deterministically without file/database/network writes. In `github_repository_binding.py` and `git_continuity.py`, require valid identity-bound repository evidence for both transfer endpoints. A stale/conflict row has no recovery command, retry, mutation, Work Unit, or authoritative Project payload.
- [ ] **Step 4: Run GREEN.** Run the two RED commands again and `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'`. Expected: PASS.
- [ ] **Step 5: Run Git continuity regression.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_remote_verification.py'`. Expected: PASS; remote verification remains evidence, not identity inference or Project authority.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/scripts/github_repository_binding.py .gpt-codex/scripts/git_continuity.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_github_repository_binding.py .gpt-codex/tests/test_git_continuity.py .gpt-codex/tests/test_remote_verification.py` then `git commit -m "feat: classify bounded evolution observations"`.

### Task 7: Validation orchestration and consumer-projection closure

**Files:**
- Modify: `.gpt-codex/scripts/validate_framework.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/scripts/consumer_projection.py`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Modify: `.gpt-codex/tests/test_validator_context_binding.py`
- Modify: `.gpt-codex/tests/test_self_hosting_validator.py`
- Modify: `.gpt-codex/tests/test_consumer_projection.py`
- Modify: `.gpt-codex/tests/test_consumer_runtime_closure.py`

**Interfaces:**
- `validate_project.py` calls Task 1 identity boundary before local evolution evaluation/adoption and returns exact frozen failures.
- `validate_framework.py` validates source/index classifications without acquiring Project ownership.
- `consumer_projection.scan_consumer_boundary(staging_root, manifest)` parses projected JSON records and reports a management source/index/enrollment record as `management_identity_hits` when it has `framework_management_only: true`, `governance_profile: "FRAMEWORK_MANAGEMENT"`, `classification: "FRAMEWORK_MANAGEMENT_METADATA"`, or an enrollment/observation record classification. Python source code containing a classification constant is not itself a management record. The manifest classifies P0-4 Design/Plan/test artifacts as `DEVELOPMENT_HISTORY` or `MANAGEMENT_ONLY` exactly.

**Deterministic manifest changes:**

| Path set | Manifest action | Classification |
| --- | --- | --- |
| `docs/superpowers/specs/2026-09-14-project-isolation-centralized-evolution-design.md` | Add one entry. | DEVELOPMENT_HISTORY |
| `docs/superpowers/plans/2026-09-14-project-isolation-centralized-evolution.md` | Add one entry. | DEVELOPMENT_HISTORY |
| Every pre-existing path in the complete File Map | Do not rewrite its manifest entry because contents changed. | Classification unchanged from the File Map. |
| `.gpt-codex/release/consumer-projection-manifest.json` | Retain its own existing entry. | MANAGEMENT_ONLY |
| Project Evolution Source, enrollment, and index runtime data | Add no manifest entry: no persistent P0-4 data file exists. | Not a projection asset. |

- [ ] **Step 1: Write failing behavioral tests.** In `test_consumer_projection.py`, construct staged JSON files representing a `FRAMEWORK_MANAGEMENT` CONTROL record, a `FRAMEWORK_MANAGEMENT_METADATA` index record, and a `DERIVED_OBSERVATION_ONLY` observation record; assert `management_identity_hits` contains each path. Also stage a Python file that merely defines `FRAMEWORK_MANAGEMENT_METADATA` as a string and assert it is not a hit. In `test_consumer_runtime_closure.py`, assert consumer inventory excludes every P0-4 management-only asset. In `test_validator_context_binding.py`, assert a validation attempt to use an observation as an instruction returns `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_runtime_closure.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: management evolution records are not yet rejected in projection scanning and validator integration is incomplete.
- [ ] **Step 3: Implement the minimum closure.** Extend `scan_consumer_boundary` with JSON-record inspection for the three exact management-record shapes from Step 1, while preserving byte-level secret scanning and existing manifest forbidden values. In the manifest, add exactly `docs/superpowers/specs/2026-09-14-project-isolation-centralized-evolution-design.md` and `docs/superpowers/plans/2026-09-14-project-isolation-centralized-evolution.md` as `DEVELOPMENT_HISTORY`. Do not rewrite entries for any existing path: every existing production script retains the File Map classification, every existing test retains `MANAGEMENT_ONLY`, and the manifest retains `MANAGEMENT_ONLY`. Update validators to orchestrate preceding interfaces only. Do not project index/enrollment records, do not add a consumer runtime command, and do not update VERSION/release assets.
- [ ] **Step 4: Run GREEN.** Run the three RED commands again plus `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'`. Expected: PASS.
- [ ] **Step 5: Run final implementation verification.** Run `python .gpt-codex/scripts/validate_framework.py`; `python .gpt-codex/scripts/validate_project.py .`; `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'`; `python .gpt-codex/scripts/validate_consumer_projection.py --root .`; `git diff --check`; and `git status --short`. Expected: zero test failures/errors, projection unknown = 0, projection missing required = 0, whitespace check passes, and no uncommitted files after the commit step.
- [ ] **Step 6: Commit.** Run `git add .gpt-codex/scripts/validate_framework.py .gpt-codex/scripts/validate_project.py .gpt-codex/scripts/consumer_projection.py .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_self_hosting_validator.py .gpt-codex/tests/test_consumer_projection.py .gpt-codex/tests/test_consumer_runtime_closure.py` then `git commit -m "feat: close evolution projection and validation boundaries"`. Re-run the final implementation verification after the commit; do not create a verification-only commit.

## Implementation acceptance and boundaries

Implementation acceptance requires all Task commits plus the final verification in Task 7: full unittest suite has zero failures/errors, both validators pass, projection unknown and missing-required counts equal zero, `git diff --check` passes, and the worktree is clean. Result/Evidence stays in each Project's existing local protocol; no shared evidence artifact is created.

P0-5 remains excluded: no `ACTIVE_EXECUTION_SLOTS`, slot lifecycle, window recovery, reviewer seriality, slot reassignment, or restart semantics. P0-6 remains excluded: no event stream, idempotency key, ordering mechanism, telemetry collector, retention, or scoring. A Project Evolution Observation is a bounded compatibility report and is not execution telemetry.

## Plan-stage projection deviation

This Plan creation changes only `docs/superpowers/plans/2026-09-14-project-isolation-centralized-evolution.md`. The stage-local allowed projection debt is exactly:

- `docs/superpowers/specs/2026-09-14-project-isolation-centralized-evolution-design.md`
- `docs/superpowers/plans/2026-09-14-project-isolation-centralized-evolution.md`

`PROJECTION_STAGE_DEVIATION = DEFERRED_NONBLOCKING`. Task 7 closes both paths and all implementation-path projection debt before implementation acceptance.

## Plan self-review

- Full Design coverage: Tasks 1–7 cover every producer/consumer contract, the ten protected resource classes, source, local evaluation, adoption, explicit enrollment, observation/index lifecycle, consumer isolation, validation, and migration compatibility.
- Exact files: the mutation-path union equals the `MUTATED_ASSET` File Map rows; each has one existing Registry owner. `test_framework_module_validation.py` and `test_framework_project_separation.py` are `VERIFY_ONLY_REGRESSION` and are absent from all Task Modify lists and commit commands.
- Interface consistency: Task 1 identity decision feeds Tasks 3–6; Task 2 source decision feeds Task 3; Task 5 observation feeds Task 6; Task 7 only orchestrates and filters those interfaces.
- RED/GREEN correctness: every task starts with named behavioral tests and an exact expected missing/incorrect behavior, then reruns the same command after the smallest change.
- Failure vocabulary: no alias is used as a code token; all frozen and P0-4-specific conditions preserve their distinct triggers.
- Authority and privacy: no task persists a central Project record, creates a command queue, infers identity/enrollment, or centralizes sensitive Project payloads.
- P0-5/P0-6 separation: slot lifecycle and telemetry mechanisms are explicitly absent from all tasks and interfaces.
- Projection closure: only the Design/Plan pair is deferred at Plan stage; Task 7's deterministic manifest table adds those two development-history entries, retains every existing File Map classification unchanged, and resolves unknown/missing paths to zero.
- Baseline execution gate: the mandatory preflight is outside the seven Tasks, records all required evidence, requires GPT verification before Task 1, and stops for `RECONCILIATION_REQUIRED` on canonical-main, ancestry, Registry-route, contract-drift, or worktree failure.
- Required-marker scan: returns zero prohibited marker matches.
