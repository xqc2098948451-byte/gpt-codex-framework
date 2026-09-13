# Framework–Project Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the accepted P0-3 Framework–Project Separation contract so project-local authority and identity remain authoritative while Framework compatibility remains read-only until separately authorized adoption/mutation.

**Architecture:** `identity-context` remains the sole primary module and owns canonical project/repository identity and contamination decisions. Existing validation, navigation, Git, role, and projection layers consume that decision without acquiring identity authority. No mandatory persisted schema field or migration is introduced for valid v2.5.0 projects.

**Tech Stack:** Python 3 standard library, JSON Schema, unittest, existing GPT–Codex Framework governance/runtime modules

**Spec:** docs/superpowers/specs/2026-09-13-framework-project-separation-design.md

## Global Constraints

- Work from `feature/framework-project-separation-design` at accepted Design SHA `46471db2e242f1a31210f439e876468ed6cdf48d`; do not modify `main`.
- Preserve `Framework publishes; Project decides`, `Project root = authoritative`, and `Framework root = auxiliary / governed source`.
- `identity-context` is the sole primary module under the v2.5.0 responsibility-first Registry contract. No eighth module or fuzzy fallback is permitted.
- Do not add mandatory schema/template fields, change schema versions, change VERSION, mutate STATE/CONTROL as part of validation, or release/publish during this work unit.
- Project `CONTROL.json`, `STATE.json`, Work Units, Result/Evidence, repository identity, extensions, selected Built-ins, permissions, and configuration are authoritative in the Project root. Framework publications and Framework metadata are auxiliary/read-only inputs.
- Compatibility evaluation is read-only. Adoption/mutation requires the existing Project Work Unit, current state revision, Role Protocol authorization, and explicit mutation action.
- Ordinary consumers require Project `AUTHORITATIVE`, Framework `ADVISORY`, and Framework/Kernel/Built-ins `READ_ONLY`. Management/self-hosting requires explicit `FRAMEWORK_MANAGEMENT`, `framework_management_only`, and `SELF_MANAGED` markers.
- This Plan is remediation only. It does not modify the accepted Design, source code, schemas, templates, projection manifest, release metadata, STATE, CONTROL, or main.

---

## File Map

| Operation | Path | Responsibility | Contract or scope |
|---|---|---|---|
| MODIFY | `.gpt-codex/scripts/context_binding.py` | Canonical identity object, identity-first decision order, authority boundary, and contamination decisions. | `PROJECT_IDENTITY_CONTRACT`, `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`, `CONTEXT_CONTAMINATION_DECISION` |
| MODIFY | `.gpt-codex/scripts/github_repository_binding.py` | Repository ID authority and present contradictory full-name rejection; retain read-only scan. | `GITHUB_REPOSITORY_MISMATCH` |
| MODIFY | `.gpt-codex/scripts/validate_project.py` | Identity-first orchestration, compatibility evaluation, adoption validation, and downstream gate ordering. | `FRAMEWORK_COMPATIBILITY_EVALUATION`, project authority |
| MODIFY | `.gpt-codex/scripts/validate_framework.py` | Existing Framework management/self-hosting validation integration. | Management isolation |
| MODIFY | `.gpt-codex/release/consumer-projection-manifest.json` | Exact-path classification for Design, Plan, and the new focused test. | Projection closure |
| MODIFY | `.gpt-codex/README.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md` | Operational boundary, compatibility lifecycle, migration direction, and failure vocabulary. | Compatibility/migration contract |
| CREATE | `.gpt-codex/tests/test_framework_project_separation.py` | Focused tests for identity, authority, compatibility, adoption, and Registry non-authority. Classify as `MANAGEMENT_ONLY` in the projection manifest. | Cross-contract tests not owned by one existing fixture |
| TEST | `.gpt-codex/tests/test_context_binding.py`, `.gpt-codex/tests/test_github_repository_binding.py`, `.gpt-codex/tests/test_multi_project_github_isolation.py` | Existing context/repository positive and negative regression coverage. | Identity and contamination |
| TEST | `.gpt-codex/tests/test_validator_context_binding.py`, `.gpt-codex/tests/test_self_hosting_validator.py` | Validator and explicit management/self-hosting regression coverage. | Project authority boundary |
| TEST | `.gpt-codex/tests/test_project_navigation.py`, `.gpt-codex/tests/test_continuity_resume.py`, `.gpt-codex/tests/test_context_window_resume.py` | Derived Map/Resume behavior after identity validation. | Navigation continuity |
| TEST | `.gpt-codex/tests/test_instruction_role_contract.py`, `.gpt-codex/tests/test_git_continuity.py` | Role/action and Git/publish gates remain independent authority layers. | Role Protocol and Git continuity |
| TEST | `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_consumer_workspace.py` | Exact projection boundary and operational vocabulary. | Consumer projection |
| TEST | `.gpt-codex/tests/test_framework_module_validation.py`, `.gpt-codex/tests/test_framework_module_routing.py` | Registry metadata-only, responsibility-first, no-fallback regression coverage. | Registry boundary |
| NO CHANGE | `.gpt-codex/scripts/project_navigation.py` | Existing navigation API remains unchanged. | Frozen for P0-3 |
| NO CHANGE | `.gpt-codex/scripts/continuity_resume.py` | Existing Resume API remains unchanged and reloads Project CONTROL/STATE internally. | Frozen for P0-3 |
| NO CHANGE | `.gpt-codex/scripts/framework_module_routing.py` | P0-2 froze `RouteDecision`/Registry routing as metadata-only and responsibility-first. | Frozen for P0-3 |
| NO CHANGE | `.gpt-codex/scripts/consumer_projection.py` | Existing projection taxonomy and staging behavior remain the single projection policy. | Frozen for P0-3 |
| NO CHANGE | `.gpt-codex/scripts/validate_consumer_projection.py` | Existing projection validator remains unchanged; Task 6 tests exact manifest closure. | Frozen for P0-3 |
| NO CHANGE | `.gpt-codex/schemas/`, `.gpt-codex/project-template/` | No schema/template field or required authority mechanism is added. | Frozen for P0-3 |

The five NO CHANGE production surfaces are frozen because the accepted Design and current v2.5.0 implementation show no mandatory defect there. Regression tests and upstream orchestration cover them.

## Scope and Authority

- `PRIMARY_MODULE` = `identity-context`.
- `AFFECTED_MODULES` = `framework-validation`, `navigation-continuity`, `git-continuity`, `role-communication`, `release-projection`, and `framework-core`.
- `CONTRACTS_AFFECTED` = `PROJECT_IDENTITY_CONTRACT`, `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`, `FRAMEWORK_COMPATIBILITY_EVALUATION`, and `CONTEXT_CONTAMINATION_DECISION`.
- `INVARIANTS_AFFECTED` = Project-root authority, Framework-root advisory/read-only status, explicit management mode, local extension ownership, identity precedence, derived Map/Resume status, Registry metadata-only routing, explicit upgrade adoption, and fail-closed cross-project isolation.
- Cross-module change is required because identity must be checked before validation, navigation, Git, role, and projection decisions while those modules retain their existing execution authority. The implementation threads one identity decision through existing seams; it does not move authority into those consumers.

## Deterministic Decision Order

The first applicable condition wins. Framework metadata, Map, Resume, project name, and default branch cannot repair an earlier identity failure.

| Order | Condition | Result | Execution consequence |
|---:|---|---|---|
| 1 | Project-root CONTROL is missing, unreadable, non-object, or malformed. | `PROJECT_IDENTITY_INVALID` | Hard stop; no routing, evaluation, adoption, or mutation. |
| 2 | Authoritative project/context/roots/profile tuple is invalid. | `PROJECT_IDENTITY_INVALID` | Hard stop. |
| 3 | Supplied active/target context differs from authoritative `CONTROL.project_context_id`, including same-name/different-ID input. | `CROSS_PROJECT_CONTEXT_MISMATCH` | Deny executable action; analysis-only returns diagnostics only. |
| 4 | Repository ID differs, or a present non-empty observed full name contradicts CONTROL. | `GITHUB_REPOSITORY_MISMATCH` | Deny binding, mutation, publication, and adoption. |
| 5 | Consumer claims management/self-hosting, management identity enters consumer projection, or Framework metadata is treated as write authority. | `PROJECT_AUTHORITY_BOUNDARY_VIOLATION` | Hard stop. |
| 6 | Framework source is selected without explicit Project adoption authorization. | `FRAMEWORK_ADOPTION_NOT_AUTHORIZED` | Read-only evaluation may proceed; adoption/mutation is denied. |
| 7 | Exact Registry responsibility route is unavailable. | `MODULE_ROUTE_UNRESOLVED` | Fail closed; no fallback module. |
| 8 | Identity is valid and derived Map/Resume is missing, stale, partial, or contradictory. | Existing `MAP_MISSING`, `MAP_PARTIAL`, `MAP_MISS`, or `NAVIGATION_REPOSITORY_MISMATCH`. | Degrade only in the derived layer; never repair identity. |
| 9 | Identity is valid and Framework facts can be compared. | `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`. | Return read-only compatibility facts; never imply adoption. |

The authoritative tuple is `(project_id, project_context_id, repository_id, repository_full_name when present, project_root)`. An absent observed full name remains compatible when repository ID matches; a present contradictory full name is a mismatch.

## Implementation Tasks

### Task 1: Canonical Project identity model and precedence

**Files:** `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/tests/test_context_binding.py`, `.gpt-codex/tests/test_framework_project_separation.py`

- [ ] **Step 1: Add failing tests.** Add `test_identity_precedence_ignores_project_name_and_framework_version`, `test_malformed_control_identity_returns_project_identity_invalid`, `test_same_name_different_context_returns_cross_project_context_mismatch`, `test_matching_project_context_is_positively_accepted`, and `test_framework_root_is_never_project_authority`. Use a valid v2.5.0 CONTROL fixture; change only project name/Framework version in the precedence test; assert `ALLOW` for matching identity, `CROSS_PROJECT_CONTEXT_MISMATCH` for a different context, and `PROJECT_IDENTITY_INVALID` with `hard_stop is True` for malformed CONTROL.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected RED: `ProjectIdentity`, `load_project_identity`, and the canonical decision path do not yet exist; the old instruction mismatch assertion still reports `CROSS_PROJECT_INSTRUCTION_MISMATCH`.
- [ ] **Step 3: Implement the minimum behavior.** In `context_binding.py`, add frozen `ProjectIdentity` fields `project_id`, `project_context_id`, `repository_id`, `repository_full_name`, `default_branch`, `project_root`, `framework_root`, `management`, `project_role`, and `framework_role`. Add `load_project_identity(control, *, project_root=None, framework_root=None) -> ProjectIdentity` and `evaluate_project_identity(control, *, expected_project_id=None, expected_project_context_id=None, expected_repository_id=None, expected_repository_full_name=None) -> ContextDecision`. Validate existing fields only; malformed authoritative data raises `ValueError("PROJECT_IDENTITY_INVALID")`. Update instruction/return/bootstrap evaluation to use this path before freshness and role checks, with context mismatch normalized to `CROSS_PROJECT_CONTEXT_MISMATCH`.
- [ ] **Step 4: Run GREEN.** Run both Step 2 commands. Expected GREEN: all identity tests pass, matching context returns `ALLOW`, and no test emits `CROSS_PROJECT_INSTRUCTION_MISMATCH` for a context boundary.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: existing cross-project and validator behavior remains passing with the normalized failure name.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm identity comes from Project CONTROL, Framework root is never authoritative, no schema/template changes exist, no duplicate identity parser exists, and downstream callers receive the existing `ContextDecision` shape.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_framework_project_separation.py` followed by `git commit -m "feat: establish canonical project identity boundary"`.

### Task 2: Repository binding and cross-project contamination

**Files:** `.gpt-codex/scripts/github_repository_binding.py`, `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/tests/test_github_repository_binding.py`, `.gpt-codex/tests/test_multi_project_github_isolation.py`

- [ ] **Step 1: Add failing tests.** Add/update `test_repository_id_match_with_absent_observed_full_name_allows`, `test_present_contradictory_repository_full_name_denies`, `test_foreign_repository_id_denies_with_github_repository_mismatch`, `test_same_context_wrong_repository_denies_instruction`, `test_wrong_context_same_repository_denies_return`, and `test_repository_scan_is_read_only`. Also assert an existing valid repository binding remains valid with matching ID and matching full name.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'`. Expected RED: the current present-full-name contradiction fixture still returns `ALLOW` because only repository ID is compared.
- [ ] **Step 3: Implement the minimum behavior.** In `compare_repository_binding`, compare repository ID first, then compare a non-empty observed full name. Return `BindingDecision(decision="DENY", reason="GITHUB_REPOSITORY_MISMATCH", identity_match=False, mutation_allowed=False)` for either contradiction. Preserve an absent observed full name as ID-compatible and keep `scan_repository_compatibility` read-only. Thread canonical context decisions through instruction/return evaluation so context mismatch precedes repository mismatch.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'`. Expected GREEN: matching ID/full name and matching ID/absent full name allow; contradictions deny with `GITHUB_REPOSITORY_MISMATCH`.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_git_continuity.py'`. Expected: context decisions and Git continuity gates remain passing.
- [ ] **Step 6: Refactor/check contract consistency.** Verify repository binding never updates CONTROL, remotes, branches, sync state, or publication state; preserve canonical remote URL tests and all existing read-only scan classifications.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/github_repository_binding.py .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_github_repository_binding.py .gpt-codex/tests/test_multi_project_github_isolation.py` followed by `git commit -m "fix: fail closed on repository and context contamination"`.

### Task 3: Project authority boundary, read-only compatibility, and exact adoption authorization

**Files:** `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_framework_project_separation.py`, `.gpt-codex/tests/test_context_binding.py`, `.gpt-codex/tests/test_consumer_workspace.py`

- [ ] **Step 1: Add failing tests.** Add `test_project_authority_boundary_rejects_framework_write`, `test_compatibility_evaluation_returns_exact_classification_without_mutation`, `test_compatibility_result_does_not_authorize_adoption`, `test_conflict_is_read_only_and_cannot_be_adopted`, `test_foreign_work_unit_project_binding_returns_cross_project_context_mismatch`, `test_foreign_result_evidence_project_binding_returns_cross_project_context_mismatch`, `test_matching_project_context_and_repository_are_accepted`, and `test_valid_repository_binding_remains_valid`. Snapshot CONTROL before/after evaluation and assert byte-equivalent JSON.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected RED: no compatibility evaluator, authority-boundary evaluator, or adoption predicate exists; foreign Work Unit/Result assertions have no identity-first decision.
- [ ] **Step 3: Implement the minimum behavior.** Add `evaluate_project_authority_boundary(identity, *, source, operation, explicit_adoption=False) -> ContextDecision` to `context_binding.py`. In `validate_project.py`, add `evaluate_framework_compatibility(project_control, framework_facts) -> dict[str, Any]` and `validate_framework_adoption(project_control, instruction, work_unit, *, current_state_revision) -> list[str]`. Compatibility returns `classification`, `reason`, `mutated=False`, and `adoption_authorized=False` using only the five existing classifications. Adoption validates exactly: `control.project_id == work_unit.project_id`; `instruction.target_work_unit == work_unit.work_unit_id`; `work_unit.state == AUTHORIZED`; `instruction.expected_state_revision == work_unit.basis_state_revision == current_state_revision`; executor role passes the existing Role Protocol; and `role_communication.validate_action_authority(executor_role, authorized_actions, forbidden_actions)` accepts `MUTATE_APPROVED_SCOPE` in `authorized_actions`. Foreign Work Unit or Result/Evidence binding returns `CROSS_PROJECT_CONTEXT_MISMATCH`. The validator only validates existing facts: it creates no authority, adds no permissions, rewrites no Work Unit state, infers no authorization from identity, and treats compatibility classification as non-authoritative. Identity validity is necessary; Role Protocol + Work Unit + revision + explicit mutation authorization are separately necessary. Any failed predicate returns `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected GREEN: all five classifications are exact, evaluation snapshots are unchanged, matching identity is accepted, foreign Work Unit/Result/Evidence is rejected with `CROSS_PROJECT_CONTEXT_MISMATCH`, and adoption remains unauthorized without every predicate.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'`. Expected: existing context guardrail and compatibility vocabulary tests pass.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm `validate_project.py` reuses `role_communication.validate_action_authority` rather than defining a second permission mechanism; compatibility evaluation cannot mutate Project files; no schema/template field is added; and `CONFLICT` cannot be adopted.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_framework_project_separation.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_consumer_workspace.py` followed by `git commit -m "feat: enforce project authority and compatibility evaluation"`.

**Gate A — after Task 3**
- [ ] Review canonical `ProjectIdentity`, identity precedence, exact context/repository mismatch outcomes, authority boundary, all five compatibility outcomes, compatibility non-authority, exact adoption field mappings, Role Protocol reuse, Work Unit/revision reuse, and no schema/projection dependency.
- [ ] Confirm all focused tests for Tasks 1–3 pass before Task 4. Gate A has no projection-closure dependency.

### Task 4: Validator and explicit management/self-hosting integration

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/scripts/validate_framework.py`, `.gpt-codex/tests/test_validator_context_binding.py`, `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_framework_module_validation.py`, `.gpt-codex/tests/test_framework_module_routing.py`

`framework_module_routing.py` is NO CHANGE; P0-2 already froze Registry routing as metadata-only and responsibility-first.

- [ ] **Step 1: Add failing tests.** Add `test_project_validator_rejects_framework_metadata_as_authority`, `test_management_control_requires_explicit_management_profile`, `test_consumer_control_rejects_management_identity_and_self_managed_root`, `test_registry_route_describes_responsibility_without_execution_authority`, `test_registry_permissions_do_not_authorize_project_adoption`, `test_unresolved_registry_responsibility_returns_module_route_unresolved`, and `test_registry_does_not_offer_fuzzy_fallback_or_eighth_module`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py'`. Expected RED: validator orchestration does not yet invoke identity-first authority checks for all project validation paths; Registry production routing remains unchanged.
- [ ] **Step 3: Implement the minimum behavior.** Make `validate_project.py` load Project identity first, then validate existing CONTROL/STATE/Work Unit/Result and derived artifacts. Keep `validate_framework.py` as the Framework management-root validator. Management is valid only when `framework_management_only=True`, `governance_profile="FRAMEWORK_MANAGEMENT"`, and Framework root is `SELF_MANAGED`; consumers reject those markers and require Project `AUTHORITATIVE`, Framework `ADVISORY`, and read-only Framework/Kernel/Built-ins. Do not modify `framework_module_routing.py`; add only regression assertions against its existing metadata-only route.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py'`. Expected GREEN: management and consumer boundaries pass, Registry returns metadata only, and unresolved responsibility returns `MODULE_ROUTE_UNRESOLVED`.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py'` and `python .gpt-codex/scripts/validate_framework.py`. Expected: v2.5.0 Registry and Framework validation pass without a routing production diff.
- [ ] **Step 6: Refactor/check contract consistency.** Verify no Registry route output is copied into `authorized_actions`, mutation permission, role authority, or adoption consent; no fuzzy fallback or eighth module exists; and only listed MODIFY files have production changes.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/validate_project.py .gpt-codex/scripts/validate_framework.py .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_self_hosting_validator.py .gpt-codex/tests/test_framework_module_validation.py .gpt-codex/tests/test_framework_module_routing.py` followed by `git commit -m "feat: integrate management and registry authority boundaries"`.

### Task 5: Preserve derived navigation, Resume, Role, and Git authority

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_project_navigation.py`, `.gpt-codex/tests/test_continuity_resume.py`, `.gpt-codex/tests/test_context_window_resume.py`, `.gpt-codex/tests/test_instruction_role_contract.py`, `.gpt-codex/tests/test_git_continuity.py`

**NO API SIGNATURE CHANGE:** `.gpt-codex/scripts/project_navigation.py` remains unchanged with `validate_navigation_identity(navigation: dict[str, Any], control: dict[str, Any]) -> None`. `.gpt-codex/scripts/continuity_resume.py` remains unchanged with the existing `load_continuity_resume` API, which reloads Project CONTROL/STATE internally. Neither API receives a ProjectIdentity object and neither file has a planned production diff. Any future API change is outside this Plan.

- [ ] **Step 1: Add failing tests.** Add `test_project_identity_failure_prevents_map_success`, `test_matching_identity_permits_existing_navigation_flow`, `test_valid_identity_with_stale_map_returns_existing_map_result`, `test_resume_cannot_substitute_its_context_identity_for_control`, `test_navigation_repository_mismatch_remains_derived_result`, `test_role_protocol_remains_action_authority_after_identity_allow`, and `test_git_publish_gate_remains_separate_from_identity_decision`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_project_navigation.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_continuity_resume.py'`. Expected RED: new ordering assertions have no identity-first validation seam; navigation and Resume APIs remain unchanged.
- [ ] **Step 3: Implement the minimum behavior.** In `validate_project.py`, evaluate canonical identity first. Only when that decision is executable/allowed, call existing `validate_navigation_identity(navigation, control)` and `load_continuity_resume` using authoritative Project CONTROL and repository ID; never pass ProjectIdentity into either API. Preserve Map authority `DERIVED_NAVIGATION_INDEX` and Resume authority `DERIVED_CACHE`. Keep Role Protocol action authority and `git_continuity.evaluate_publish_gate` sync/attestation/remote/publication authority.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_project_navigation.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_continuity_resume.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_context_window_resume.py'`. Expected GREEN: identity failure blocks derived success, matching identity reaches existing APIs, stale Map yields existing `MAP_*` behavior, Resume cannot substitute CONTROL, and `NAVIGATION_REPOSITORY_MISMATCH` remains derived.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_instruction_role_contract.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_git_continuity.py'`. Expected: Role Protocol and Git publication gates remain independently authoritative.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm `project_navigation.py` and `continuity_resume.py` have no diff, identity failure cannot be downgraded by Map/Resume, and identity allow does not authorize role/action, commit, push, or publish.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_project_navigation.py .gpt-codex/tests/test_continuity_resume.py .gpt-codex/tests/test_context_window_resume.py .gpt-codex/tests/test_instruction_role_contract.py .gpt-codex/tests/test_git_continuity.py` followed by `git commit -m "test: preserve derived continuity and execution authorities"`.

### Task 6: Exact-path consumer projection manifest closure

**Files:** `.gpt-codex/release/consumer-projection-manifest.json`, `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_consumer_workspace.py`

Production scope is frozen: `.gpt-codex/scripts/consumer_projection.py` and `.gpt-codex/scripts/validate_consumer_projection.py` are NO CHANGE. Task 6 changes only the manifest and tests. RED fails because exact paths are absent or misclassified, not because a projection algorithm is missing.

- [ ] **Step 1: Add failing tests.** Add `test_projection_manifest_classifies_separation_design_as_development_history`, `test_projection_manifest_classifies_separation_plan_as_development_history`, `test_new_separation_test_is_management_only`, `test_consumer_required_projection_excludes_management_control`, `test_consumer_required_projection_excludes_registry_execution_metadata`, `test_projection_rejects_cross_project_management_identity_contamination`, and `test_runtime_closure_does_not_import_framework_management_authority`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'`. Expected RED: the Design and Plan exact paths are not both `DEVELOPMENT_HISTORY` and the new test path is not `MANAGEMENT_ONLY`.
- [ ] **Step 3: Implement the minimum behavior.** Modify only `.gpt-codex/release/consumer-projection-manifest.json`: add exact entries for `docs/superpowers/specs/2026-09-13-framework-project-separation-design.md` and `docs/superpowers/plans/2026-09-13-framework-project-separation.md` as `DEVELOPMENT_HISTORY`, and `.gpt-codex/tests/test_framework_project_separation.py` as `MANAGEMENT_ONLY`. The only newly created path authorized by this Plan is `.gpt-codex/tests/test_framework_project_separation.py`; no other new implementation, test, or documentation path is authorized. Keep management CONTROL, management-only Built-ins, release metadata, Framework operational state, and Registry metadata outside consumer-required content. Do not alter either projection script.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_runtime_closure.py'`. Expected GREEN: exact manifest paths resolve, projection unknown paths equal 0, and missing required paths equal 0.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'` and `python .gpt-codex/scripts/validate_consumer_projection.py --root .`. Expected: runtime closure and consumer validation pass without projection algorithm changes.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm only the manifest is a production MODIFY surface in this task, exact-path validation remains strict, management identity and cross-project Project CONTROL/STATE cannot enter consumer-required projection, and no projection script has a diff.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/tests/test_consumer_projection.py .gpt-codex/tests/test_consumer_runtime_closure.py .gpt-codex/tests/test_consumer_workspace.py` followed by `git commit -m "feat: enforce separation in consumer projection"`.

### Task 7: Operational docs, compatibility lifecycle, and migration direction

**Files:** `.gpt-codex/README.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md`, `.gpt-codex/tests/test_consumer_workspace.py`, `.gpt-codex/tests/test_context_binding.py`

- [ ] **Step 1: Add failing tests.** Add `test_operational_docs_state_framework_publishes_project_decides`, `test_operational_docs_state_upgrade_evaluation_is_not_adoption`, `test_operational_docs_list_exact_separation_failure_vocabulary`, `test_existing_v25_project_is_no_migration`, and `test_versioned_auxiliary_framework_folder_requires_explicit_migration_to_fixed_source`.
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'`. Expected RED: operational documents do not yet contain the complete separation lifecycle and corrected legacy-to-fixed migration direction.
- [ ] **Step 3: Implement the minimum behavior.** Update only the listed operational documents and tests. Include: “Valid v2.5.0 projects using the current fixed Framework source remain NO_MIGRATION. A legacy project still using a versioned auxiliary Framework folder requires an explicit project-local migration to the fixed unversioned Framework source folder. Framework publication or compatibility evaluation cannot perform that migration automatically.” State publication → read-only compatibility evaluation → explicit Project decision → separately authorized mutation. List `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, `MODULE_ROUTE_UNRESOLVED`, and derived `NAVIGATION_REPOSITORY_MISMATCH`. State project-local extensions/configuration remain local and P0-4 is interface-only.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'`. Expected GREEN: docs contain the exact lifecycle/vocabulary; valid v2.5.0 is `NO_MIGRATION` and versioned auxiliary source requires `EXPLICIT_MIGRATION`.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'`. Expected: management isolation and projection documentation checks remain passing.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm no wording says a project already using the fixed unversioned source requires migration; no automatic upgrade/propagation or P0-4 mechanism is described; and docs grant no execution authority to Framework metadata or Registry routing.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/README.md .gpt-codex/BOOTSTRAP_PROMPT.md .gpt-codex/tests/test_consumer_workspace.py .gpt-codex/tests/test_context_binding.py` followed by `git commit -m "docs: define framework project separation operations"`.

**Gate B — after Task 7**
- [ ] Review validator integration, management/self-hosting isolation, Registry non-authority, Map/Resume derived-only behavior, Role/Git authority preservation, exact projection closure, runtime closure, migration direction, docs/failure vocabulary, and P0-4 boundary.
- [ ] Require consumer projection unknown = 0 and missing required = 0 before Task 8.

### Task 8: Full regression and Result-Envelope-only verification

**Files:** all authorized implementation files in the File Map; no evidence file is authorized.

- [ ] **Step 1: Run the full test suite.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'`. Record the actual discovered test count and pass/fail result.
- [ ] **Step 2: Run Framework validation.** Run `python .gpt-codex/scripts/validate_framework.py` and record its exit/result.
- [ ] **Step 3: Run Project validation.** Run `python .gpt-codex/scripts/validate_project.py .` and record its exit/result.
- [ ] **Step 4: Run consumer projection validation.** Run `python .gpt-codex/scripts/validate_consumer_projection.py --root .`; record unknown paths = 0 and missing required paths = 0.
- [ ] **Step 5: Run scope and integrity checks.** Run `git diff --check`, `git status --short --branch`, and `git diff --name-only HEAD~7 HEAD` after the seven Task commits. Confirm every changed path is in the File Map and no schema/template, VERSION, STATE/CONTROL, release, or frozen NO CHANGE path changed.
- [ ] **Step 6: Record evidence in the Result Envelope.** No tracked evidence file is authorized by this Plan. Implementation verification evidence remains in the Result Envelope, including actual test count, validator results, projection counts, HEAD SHA, and clean-worktree status.
- [ ] **Step 7: Do not create a verification-only commit.** If all implementation files are already committed after Task 7, Task 8 performs verification only and returns results. No evidence file and no verification-only commit may be created.

## Plan-stage Projection Deviation

This Plan Fix Round changes only `docs/superpowers/plans/2026-09-13-framework-project-separation.md`. The Design and Plan paths may remain unclassified on this branch until implementation Task 6 updates the manifest:

- `docs/superpowers/specs/2026-09-13-framework-project-separation-design.md`
- `docs/superpowers/plans/2026-09-13-framework-project-separation.md`

`PROJECTION_STAGE_DEVIATION = DEFERRED_NONBLOCKING`. The manifest is not modified during this Plan Fix Round.

## Compatibility and Migration Contract

- Valid v2.5.0 projects using the current fixed Framework source remain `NO_MIGRATION`.
- A legacy project still using a versioned auxiliary Framework folder requires an explicit project-local migration to the fixed unversioned Framework source folder. This is `EXPLICIT_MIGRATION`, not automatic.
- Framework publication or compatibility evaluation cannot perform migration automatically.
- Existing project-context binding remains the first identity check; context boundary failures emit `CROSS_PROJECT_CONTEXT_MISMATCH`.
- Existing GitHub binding remains repository-ID authoritative; absent observed full name is compatible when ID matches, while a present contradictory full name emits `GITHUB_REPOSITORY_MISMATCH`.
- Existing Project Map and Resume remain derived and cannot repair CONTROL identity.
- Existing Role Protocol, Work Unit, CONTROL/STATE, Result/Evidence, Git continuity, publication, and projection contracts retain their authority.
- Project-specific extensions, selected Built-ins, permissions, and configuration remain local; Framework publication is advisory source material.
- No mandatory schema/template field, version bump, automatic migration, automatic upgrade, or automatic propagation is part of P0-3.

## P0-4 Boundary and Non-Goals

P0-4 is not implemented or pre-decided. P0-3 exposes only identity, authority, compatibility-result, and contamination interfaces for a future phase. The implementation must not add a central Framework service, automatic project synchronization, automatic upgrade propagation, shared mutable project state, cross-project write capability, Registry execution authority, release/publish behavior, or a new module.

## Required Self-Review

### Finding closure

- `PLAN-WRITING-PLANS-001` → CLOSED
- `PLAN-API-SEAM-001` → CLOSED
- `PLAN-WORK-UNIT-ROLE-001` → CLOSED
- `PLAN-REGISTRY-SCOPE-001` → CLOSED
- `PLAN-PROJECTION-SCOPE-001` → CLOSED
- `PLAN-MIGRATION-DIRECTION-001` → CLOSED
- `PLAN-EVIDENCE-SCOPE-001` → CLOSED

### Structure and consistency checks

- Required writing-plans header appears at the document start.
- Tasks 1–7 contain seven checkbox steps with actual test names, RED command/expected reason, implementation behavior, GREEN command, regression command, contract checks, and exact commit scope.
- Task 8 contains checkbox steps for full suite, all validators, projection counts, diff/status/scope checks, Result Envelope evidence, and no commit/evidence file.
- The placeholder scan returns zero matches.
- Every Task path agrees with the File Map; every NO CHANGE surface remains excluded from implementation modifications.
- No task changes an existing API signature unless the task explicitly lists that API as MODIFY; frozen navigation, Resume, Registry routing, and projection scripts have no planned production diff.
- Migration direction is versioned auxiliary Framework folder → fixed unversioned Framework source folder, with `EXPLICIT_MIGRATION` only for legacy projects.
- No tracked evidence file and no verification-only commit are permitted.

## Required Return Fields

The implementation result after executing this Plan must report:

`RESULT`, `WORK_UNIT`, `ARTIFACT_STAGE`, `FIX_ROUND`, `EXECUTION_SLOT_ID`, `ACCEPTED_DESIGN_SHA`, `PREVIOUS_REVIEWED_SHA`, `HEAD_SHA`, `ANCESTRY_VERIFICATION`, all seven finding closure fields, `WRITING_PLANS_CONFORMANCE`, `TASK_COUNT`, `GATE_A_AFTER_TASK`, `GATE_B_AFTER_TASK`, `FILE_MAP_RESULT`, `API_SEAM_RESULT`, `WORK_UNIT_ROLE_MAPPING_RESULT`, `REGISTRY_SCOPE_RESULT`, `PROJECTION_SCOPE_RESULT`, `MIGRATION_DIRECTION_RESULT`, `EVIDENCE_SCOPE_RESULT`, `TEST_COVERAGE_RESULT`, `PLACEHOLDER_SCAN_RESULT`, `SELF_REVIEW_RESULT`, `PROJECTION_STAGE_DEVIATION`, `FILES_CHANGED`, `WORKTREE_STATUS`, `PUSH_STATUS`, `REMOTE_HEAD_SHA`, `REMOTE_VERIFICATION`, `DEVIATIONS`, `BLOCKERS`, and `NEXT_GPT_ACTION`.
