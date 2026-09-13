# Framework–Project Separation Implementation Plan

**Required sub-skill:** `superpowers:executing-plans`

**Goal:** Implement the accepted P0-3 Framework–Project Separation contract so project-local CONTROL/STATE/Work Units and repository identity remain authoritative while Framework metadata is advisory, read-only, explicitly evaluated, and never implicitly adopted.

**Architecture:** `identity-context` remains the sole primary module and owns the canonical project/repository identity tuple and contamination decisions. Existing validation, navigation, Git continuity, role protocol, and consumer-projection surfaces consume that decision; the Framework Module Registry continues to describe responsibility and dependency only. All decisions are in-memory until an already-authorized project mutation writes existing optional evaluation metadata, and no new mandatory schema field is introduced.

**Tech Stack:** Python 3 standard library, `unittest`, JSON schemas/templates, Git worktrees, existing `.gpt-codex` validators and projection tooling.

**Spec:** `docs/superpowers/specs/2026-09-13-framework-project-separation-design.md` at accepted SHA `46471db2e242f1a31210f439e876468ed6cdf48d`.

## Global Constraints

- Work only from `feature/framework-project-separation-design` at the accepted Design SHA. Implementation work must begin from this Plan and must not modify `main`.
- Preserve `Framework publishes; Project decides`, `Project root = authoritative`, and `Framework root = auxiliary / governed source`.
- Use the v2.5.0 responsibility-first Registry route. `identity-context` is primary because it owns project and repository identity; no eighth module may be inferred or added.
- Do not add required schema/template fields, change schema versions, change VERSION, mutate STATE/CONTROL during this planning task, or release/publish from the implementation work until its own release authorization exists.
- Framework metadata, Framework version, project name, default branch, Project Map, and Resume may not repair or replace an invalid authoritative identity tuple.
- Framework compatibility evaluation is read-only. Adoption requires an existing project Work Unit, current state revision, role/action authorization, and explicit project decision; there is no automatic propagation, synchronization service, central state store, or P0-4 implementation.
- Keep management/self-hosting explicit through the existing `FRAMEWORK_MANAGEMENT` profile, `framework_management_only`, and `SELF_MANAGED` root authority. Ordinary consumer projects remain `AUTHORITATIVE` for Project and `ADVISORY`/`READ_ONLY` for Framework.
- Keep project-specific extensions, selected Built-ins, configuration, permissions, and Work Unit scope in the project root. Framework publications may be evaluated as available source material, but may not overwrite `CONTROL.extensions`, project-local configuration, STATE, or Work Units.
- Use the existing Python modules and test files where they already own the behavior. Add one focused cross-boundary test module only for the new in-memory contracts that do not belong to a single existing test fixture.

## File Map

| Operation | Path | Responsibility | Design contract covered |
|---|---|---|---|
| MODIFY | `.gpt-codex/scripts/context_binding.py` | Define the canonical identity value/decision model, precedence, context binding, authority boundary, and fail-closed contamination decisions. | `PROJECT_IDENTITY_CONTRACT`, `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`, `CONTEXT_CONTAMINATION_DECISION` |
| MODIFY | `.gpt-codex/scripts/github_repository_binding.py` | Make observed repository contradictions deterministic while preserving local remote-name diagnostics and read-only scanning. | Repository identity, `GITHUB_REPOSITORY_MISMATCH` |
| MODIFY | `.gpt-codex/scripts/validate_project.py` | Orchestrate identity-first validation, read-only Framework compatibility evaluation, explicit adoption authorization, and existing navigation/Resume checks. | `FRAMEWORK_COMPATIBILITY_EVALUATION`, project authority boundary |
| MODIFY | `.gpt-codex/scripts/validate_framework.py` | Keep management/self-hosting validation and Registry validation explicit about metadata-only routing and forbidden consumer management identity. | Management/self-hosting and Registry non-authority boundary |
| MODIFY | `.gpt-codex/scripts/framework_module_routing.py` | Expose/validate Registry responsibility and dependency metadata without returning an executable authority or permission. | Registry describes WHAT; Kernel/CONTROL/Work Unit/Role Protocol decide WHO/WHAT |
| MODIFY | `.gpt-codex/release/consumer-projection-manifest.json` | Classify the new implementation history and test/doc paths without projecting management-only authority into consumers. | Consumer projection impact |
| MODIFY | `.gpt-codex/README.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md` | Document the boundary, upgrade evaluation lifecycle, identity precedence, and failure vocabulary at the operational entry points. | Compatibility and migration contract |
| TEST | `.gpt-codex/tests/test_context_binding.py` | Lock identity precedence, exact context mismatch vocabulary, and authority decisions at the existing context seam. | Identity and contamination |
| TEST | `.gpt-codex/tests/test_github_repository_binding.py` | Lock repository ID authority, present full-name contradiction behavior, absent full-name compatibility, and read-only scans. | Repository identity |
| TEST | `.gpt-codex/tests/test_multi_project_github_isolation.py` | Lock cross-project context/repository rejection for instruction and return paths. | Cross-project isolation interface |
| TEST | `.gpt-codex/tests/test_framework_project_separation.py` | Focused tests for the new identity object, authority boundary, compatibility result, adoption gate, and Registry non-authority. | Cross-contract behavior not owned by one legacy fixture |
| TEST | `.gpt-codex/tests/test_validator_context_binding.py`, `.gpt-codex/tests/test_self_hosting_validator.py` | Verify validator integration and explicit management/self-hosting compatibility. | Project authority and management mode |
| TEST | `.gpt-codex/tests/test_project_navigation.py`, `.gpt-codex/tests/test_continuity_resume.py`, `.gpt-codex/tests/test_context_window_resume.py` | Verify Map/Resume remain derived and cannot repair identity or authority. | Navigation continuity |
| TEST | `.gpt-codex/tests/test_instruction_role_contract.py`, `.gpt-codex/tests/test_git_continuity.py` | Verify role/action and publish/sync decisions remain the execution authority after identity validation. | Role Protocol and Git continuity |
| TEST | `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_consumer_workspace.py` | Verify management identities, Framework source, and implementation history stay outside consumer-required projections while compatibility vocabulary remains exact. | Consumer projection |
| TEST | `.gpt-codex/tests/test_framework_module_validation.py`, `.gpt-codex/tests/test_framework_module_routing.py` | Verify the v2.5.0 Registry route is responsibility-first and cannot grant execution authority. | Registry boundary |

## Deterministic Decision Table

Every implementation entry point must evaluate these conditions in order and return the first applicable result. No later Framework or derived value may downgrade an earlier identity failure.

| Order | Condition | Decision/reason | Authority consequence |
|---:|---|---|---|
| 1 | Project-root `CONTROL.json` is missing, unreadable, or not an object | `PROJECT_IDENTITY_INVALID` | Hard stop; no routing, evaluation, adoption, or mutation |
| 2 | `project_id` is missing/blank, `project_context_id` is required but malformed, or roots/profile contradict the v2.5.0 authority model | `PROJECT_IDENTITY_INVALID` | Hard stop |
| 3 | A supplied active/target project context ID differs from authoritative `CONTROL.project_context_id`, including same-name/different-ID input | `CROSS_PROJECT_CONTEXT_MISMATCH` | Deny executable action; analysis-only may return diagnostics only |
| 4 | A supplied repository ID differs from `CONTROL.github.repository_id`, or a supplied non-empty full name contradicts `CONTROL.github.repository_full_name` | `GITHUB_REPOSITORY_MISMATCH` | Deny binding, mutation, publication, and adoption |
| 5 | A consumer claims `FRAMEWORK_MANAGEMENT`/`SELF_MANAGED`, a management identity appears in a consumer projection, or Framework metadata is treated as a write authority | `PROJECT_AUTHORITY_BOUNDARY_VIOLATION` | Hard stop |
| 6 | A Framework source is selected for a project without an explicit project adoption authorization | `FRAMEWORK_ADOPTION_NOT_AUTHORIZED` | Read-only evaluation may proceed; adoption/mutation is denied |
| 7 | The responsibility does not match an exact v2.5.0 Registry descriptor | `MODULE_ROUTE_UNRESOLVED` | Fail closed; do not select a fallback module |
| 8 | Identity is valid; Map/Resume is absent, stale, partial, or non-authoritative | Existing derived result: `MAP_MISSING`, `MAP_PARTIAL`, `MAP_MISS`, or `NAVIGATION_REPOSITORY_MISMATCH` | No identity mutation; navigation may degrade to the documented derived result |
| 9 | Identity is valid and Framework facts can be compared | One of `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, `CONFLICT` | Return a read-only compatibility result; never imply adoption |

The canonical identity tuple is `(project_id, project_context_id, repository_id, repository_full_name when present, project_root)`. `project_name`, `default_branch`, Map, Resume, and Framework version are diagnostic or derived values only. An absent observed repository full name remains compatible when the authoritative repository ID matches; a present contradictory full name is a mismatch.

## Module and Contract Scope

- `PRIMARY_MODULE`: `identity-context` — owns project/repository identity, context binding, authority-boundary decisions, and contamination fail-closed behavior.
- `AFFECTED_MODULES`: `framework-validation`, `navigation-continuity`, `git-continuity`, `role-communication`, `release-projection`, and `framework-core`.
- `CONTRACTS_AFFECTED`: `PROJECT_IDENTITY_CONTRACT`, `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`, `FRAMEWORK_COMPATIBILITY_EVALUATION`, and `CONTEXT_CONTAMINATION_DECISION`.
- `INVARIANTS_AFFECTED`: Project-root authority, Framework-root advisory/read-only status, explicit management mode, local extension ownership, identity precedence, derived Map/Resume status, Registry metadata-only routing, explicit upgrade adoption, and fail-closed cross-project isolation.

Cross-module change is required because identity is checked before navigation, Git, role, validation, and projection decisions, while those modules must retain their existing execution authority. The plan threads one identity decision through existing seams; it does not transfer authority to those consumers and does not infer an additional module.

## Implementation Tasks

### Task 1: Add the canonical project identity model and identity-first precedence

**Files:** `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/tests/test_context_binding.py`, `.gpt-codex/tests/test_framework_project_separation.py`

**TDD — RED:** Add these tests before changing production code:

- `test_identity_precedence_ignores_project_name_and_framework_version`
- `test_malformed_control_identity_returns_project_identity_invalid`
- `test_same_name_different_context_returns_cross_project_context_mismatch`
- `test_framework_root_is_never_project_authority`

Use a minimal valid v2.5.0 CONTROL mapping and assert the exact fields of the returned decision. The first test must pass a different `project_name` and `framework_version` while keeping the tuple unchanged and assert `ALLOW`; the malformed fixture must assert `PROJECT_IDENTITY_INVALID` and `hard_stop is True`.

**Implementation:** In `context_binding.py`, add a frozen `ProjectIdentity` dataclass with these exact fields: `project_id`, `project_context_id`, `repository_id`, `repository_full_name`, `default_branch`, `project_root`, `framework_root`, `management`, `project_role`, and `framework_role`. Add:

```python
def load_project_identity(
    control: Mapping[str, Any],
    *,
    project_root: Path | None = None,
    framework_root: Path | None = None,
) -> ProjectIdentity:
    """Return validated project identity or raise ValueError("PROJECT_IDENTITY_INVALID")."""

def evaluate_project_identity(
    control: Mapping[str, Any],
    *,
    expected_project_id: str | None = None,
    expected_project_context_id: str | None = None,
    expected_repository_id: str | None = None,
    expected_repository_full_name: str | None = None,
) -> ContextDecision:
    """Return the first applicable identity decision from the deterministic table."""
```

Validate the existing v2.5.0 fields without adding schema fields. `load_project_identity` raises `ValueError("PROJECT_IDENTITY_INVALID")` only for malformed authoritative data. `evaluate_project_identity` applies the decision-table order and returns the existing `ContextDecision` shape with `authority`, `hard_stop`, and `action_executable` populated consistently. The returned identity object must not be reconstructed from `project_name`, Map, Resume, or Framework metadata.

Update `evaluate_instruction`, `evaluate_return`, and `evaluate_bootstrap` to call the canonical identity path before their existing freshness/role checks. Normalize an instruction context mismatch to the accepted exact vocabulary `CROSS_PROJECT_CONTEXT_MISMATCH`; update the legacy assertion for `CROSS_PROJECT_INSTRUCTION_MISMATCH` rather than retaining two names for the same boundary failure.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_context_binding .gpt-codex.tests.test_framework_project_separation
```

**Commit:** `git add .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_framework_project_separation.py; git commit -m "feat: establish canonical project identity boundary"`

### Task 2: Make repository binding and cross-project contamination fail closed

**Files:** `.gpt-codex/scripts/github_repository_binding.py`, `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/tests/test_github_repository_binding.py`, `.gpt-codex/tests/test_multi_project_github_isolation.py`

**TDD — RED:** Add or update these exact tests:

- `test_repository_id_match_with_absent_observed_full_name_allows`
- `test_present_contradictory_repository_full_name_denies`
- `test_foreign_repository_id_denies_with_github_repository_mismatch`
- `test_same_context_wrong_repository_denies_instruction`
- `test_wrong_context_same_repository_denies_return`
- `test_repository_scan_is_read_only`

Replace the current expectation that a differing present full name is always allowed. Preserve a separate absent-observation case so the diagnostic/local compatibility rule remains explicit.

**Implementation:** Update `compare_repository_binding` to compare repository ID first, then compare a non-empty observed full name against the bound full name. Return `BindingDecision(decision="DENY", reason="GITHUB_REPOSITORY_MISMATCH", identity_match=False, mutation_allowed=False)` for either contradiction. An absent observed full name may retain the existing ID-based allow result. Keep `scan_repository_compatibility` read-only and preserve its existing classifications.

Thread the canonical identity decision through instruction and return evaluation. A context mismatch always wins over repository comparison when the context tuple is invalid; a valid context with a foreign repository returns `GITHUB_REPOSITORY_MISMATCH`. No repository binding function may update CONTROL, remotes, branches, or publication state.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_github_repository_binding .gpt-codex.tests.test_multi_project_github_isolation .gpt-codex.tests.test_context_binding
```

**Commit:** `git add .gpt-codex/scripts/github_repository_binding.py .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_github_repository_binding.py .gpt-codex/tests/test_multi_project_github_isolation.py; git commit -m "fix: fail closed on repository and context contamination"`

### Task 3: Implement the project authority boundary and read-only Framework compatibility evaluation

**Files:** `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_framework_project_separation.py`, `.gpt-codex/tests/test_consumer_workspace.py`

**TDD — RED:** Add these tests:

- `test_project_authority_boundary_rejects_framework_write`
- `test_consumer_cannot_claim_framework_management`
- `test_compatibility_evaluation_returns_exact_classification_without_mutation`
- `test_compatibility_result_does_not_authorize_adoption`
- `test_unauthorized_adoption_returns_framework_adoption_not_authorized`
- `test_conflict_is_read_only_and_cannot_be_adopted`

Snapshot the supplied CONTROL mapping before and after evaluation and assert byte-equivalent JSON. Assert that `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, and `CONFLICT` are the only classifications. Assert that compatibility output contains `adoption_authorized is False` for every classification.

**Implementation:** In `context_binding.py`, add:

```python
def evaluate_project_authority_boundary(
    identity: ProjectIdentity,
    *,
    source: str,
    operation: str,
    explicit_adoption: bool = False,
) -> ContextDecision:
    """Return the authority decision without changing Project or Framework files."""
```

It must allow Project-root reads and explicitly authorized Project mutations, allow Framework-root reads as auxiliary source, deny Framework-root writes, deny Framework metadata as a replacement for Project state, and return `PROJECT_AUTHORITY_BOUNDARY_VIOLATION` or `FRAMEWORK_ADOPTION_NOT_AUTHORIZED` according to the decision table.

In `validate_project.py`, add the framework-validation seam:

```python
def evaluate_framework_compatibility(
    project_control: Mapping[str, Any],
    framework_facts: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a read-only compatibility classification and authority flags."""

def validate_framework_adoption(
    project_control: Mapping[str, Any],
    instruction: Mapping[str, Any],
    work_unit: Mapping[str, Any],
    *,
    current_state_revision: int,
) -> list[str]:
    """Return validation errors for an explicitly authorized adoption request."""
```

`evaluate_framework_compatibility` reads only supplied facts and current Project metadata. It returns `classification`, `reason`, `mutated=False`, and `adoption_authorized=False\); it uses `NO_ACTION` when the evaluated version is already adopted, `OPTIONAL_REUSE` for compatible reusable content, `RECOMMENDED_UPGRADE` for a compatible newer Framework, `REQUIRED_MIGRATION` for a valid project requiring an explicit migration, and `CONFLICT` for identity/authority incompatibility. `validate_framework_adoption` must require matching `project_id`, an `AUTHORIZED` Work Unit, matching `basis_state_revision`, matching `target_work_unit`, a role-valid instruction, and an existing `authorized_actions` entry `MUTATE_APPROVED_SCOPE`; otherwise return `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`. It must not write evaluation metadata. `CONFLICT` is never adoptable.

**Gate A — after Task 3:** Review the identity tuple, precedence table, authority boundary, exact failure vocabulary, no-mutation guarantee, and all five compatibility classifications. Do not proceed to integration until the focused tests and the three prior task suites pass.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_framework_project_separation .gpt-codex.tests.test_consumer_workspace .gpt-codex.tests.test_context_binding
```

**Commit:** `git add .gpt-codex/scripts/context_binding.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_framework_project_separation.py .gpt-codex/tests/test_consumer_workspace.py; git commit -m "feat: enforce project authority and compatibility evaluation"`

### Task 4: Integrate identity-first validation with management/self-hosting and Registry routing

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/scripts/validate_framework.py`, `.gpt-codex/scripts/framework_module_routing.py`, `.gpt-codex/tests/test_validator_context_binding.py`, `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_framework_module_validation.py`, `.gpt-codex/tests/test_framework_module_routing.py`

**TDD — RED:** Add these tests:

- `test_project_validator_rejects_framework_metadata_as_authority`
- `test_management_control_requires_explicit_management_profile`
- `test_consumer_control_rejects_management_identity_and_self_managed_root`
- `test_registry_route_describes_responsibility_without_execution_authority`
- `test_unresolved_registry_responsibility_returns_module_route_unresolved`

**Implementation:** Make `validate_project.main` and its helpers load the project-root identity first, then validate existing CONTROL/STATE/Work Unit/Result, navigation, and Resume checks. Keep existing schema field requirements unchanged. A consumer is valid only with Project `AUTHORITATIVE`, Framework `ADVISORY`, Framework/Kernel/Built-ins `READ_ONLY`, and a non-management profile. Management is valid only when all existing management markers agree: `framework_management_only=True`, `governance_profile="FRAMEWORK_MANAGEMENT"`, and Framework root `SELF_MANAGED`; ordinary consumers may not inherit any of these markers.

Keep `validate_framework.py` as the management-root validator and make its Registry call validate metadata only. In `framework_module_routing.py`, ensure the route result contains responsibility/module information only and cannot be passed as `authorized_actions`, mutation permission, role authority, or adoption consent. A responsibility with no exact descriptor must produce `MODULE_ROUTE_UNRESOLVED`; do not route to a “closest” module or invent a new module.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_validator_context_binding .gpt-codex.tests.test_self_hosting_validator .gpt-codex.tests.test_framework_module_validation .gpt-codex.tests.test_framework_module_routing
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
```

**Commit:** `git add .gpt-codex/scripts/validate_project.py .gpt-codex/scripts/validate_framework.py .gpt-codex/scripts/framework_module_routing.py .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_self_hosting_validator.py .gpt-codex/tests/test_framework_module_validation.py .gpt-codex/tests/test_framework_module_routing.py; git commit -m "feat: integrate management and registry authority boundaries"`

### Task 5: Preserve derived navigation, Resume, role, and Git continuity authority

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_project_navigation.py`, `.gpt-codex/tests/test_continuity_resume.py`, `.gpt-codex/tests/test_context_window_resume.py`, `.gpt-codex/tests/test_instruction_role_contract.py`, `.gpt-codex/tests/test_git_continuity.py`

**TDD — RED:** Add these tests:

- `test_project_map_cannot_repair_project_identity_mismatch`
- `test_resume_cannot_replace_authoritative_project_context`
- `test_role_protocol_remains_action_authority_after_identity_allow`
- `test_git_publish_gate_remains_separate_from_identity_decision`
- `test_valid_identity_with_stale_map_degrades_without_project_mutation`

**Implementation:** At the validation seam, pass the accepted `ProjectIdentity` into existing `validate_navigation_identity` and `continuity_resume` checks. Keep Project Map authority exactly `DERIVED_NAVIGATION_INDEX` and Resume authority exactly `DERIVED_CACHE`; stale or absent derived artifacts produce their existing derived outcomes after identity succeeds. Do not let a Map/Resume project ID, name, repository, or Framework version override CONTROL.

Keep `role_communication.validate_action_authority` responsible for role/action permission and `git_continuity.evaluate_publish_gate` responsible for ancestry, sync, attestation, remote verification, and publication. Identity allow is necessary but never sufficient for mutation or publication. A failed identity decision must prevent those downstream gates from being treated as executable success.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_project_navigation .gpt-codex.tests.test_continuity_resume .gpt-codex.tests.test_context_window_resume .gpt-codex.tests.test_instruction_role_contract .gpt-codex.tests.test_git_continuity
```

**Commit:** `git add .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_project_navigation.py .gpt-codex/tests/test_continuity_resume.py .gpt-codex/tests/test_context_window_resume.py .gpt-codex/tests/test_instruction_role_contract.py .gpt-codex/tests/test_git_continuity.py; git commit -m "test: preserve derived continuity and execution authorities"`

### Task 6: Integrate the separation boundary with consumer projection

**Files:** `.gpt-codex/release/consumer-projection-manifest.json`, `.gpt-codex/scripts/consumer_projection.py`, `.gpt-codex/scripts/validate_consumer_projection.py`, `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_consumer_workspace.py`

**TDD — RED:** Add these tests:

- `test_consumer_required_projection_excludes_management_control`
- `test_consumer_required_projection_excludes_registry_execution_metadata`
- `test_projection_manifest_classifies_separation_plan_and_design_as_development_history`
- `test_projection_rejects_cross_project_management_identity_contamination`
- `test_runtime_closure_does_not_import_framework_management_authority`

**Implementation:** Extend the existing manifest with exact classifications for the implementation artifacts: the accepted Design and this Plan are `DEVELOPMENT_HISTORY`; management CONTROL, management-only Built-ins, release metadata, and Framework operational state remain non-consumer-required according to the existing manifest contract. If `consumer_projection.py` needs a code change, limit it to applying the existing classifications to identity/management paths; do not add a second projection policy. Preserve `stage_consumer_projection`, `scan_consumer_boundary`, and zip equality behavior.

The consumer projection may contain consumer-safe identity/context fields required by the existing schemas, but it must not contain Framework management identity, self-hosting authority, project-local CONTROL/STATE from another project, or Registry-derived execution permissions. A mismatch or ambiguous ownership must fail closed with the existing projection error path rather than silently omitting evidence.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_consumer_projection .gpt-codex.tests.test_consumer_runtime_closure .gpt-codex.tests.test_consumer_workspace
python .gpt-codex/scripts/validate_consumer_projection.py --root .
```

**Commit:** `git add .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/scripts/consumer_projection.py .gpt-codex/scripts/validate_consumer_projection.py .gpt-codex/tests/test_consumer_projection.py .gpt-codex/tests/test_consumer_runtime_closure.py .gpt-codex/tests/test_consumer_workspace.py; git commit -m "feat: enforce separation in consumer projection"`

### Task 7: Document migration, upgrade evaluation, and operational failure handling

**Files:** `.gpt-codex/README.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md`, `.gpt-codex/tests/test_consumer_workspace.py`, `.gpt-codex/tests/test_context_binding.py`

**TDD — RED:** Add these tests:

- `test_operational_docs_state_framework_publishes_project_decides`
- `test_operational_docs_state_upgrade_evaluation_is_not_adoption`
- `test_operational_docs_list_exact_separation_failure_vocabulary`
- `test_existing_v25_project_is_no_migration`
- `test_legacy_fixed_folder_migration_requires_explicit_project_decision`

**Implementation:** Add concise operational guidance to the existing README and bootstrap prompt. State the identity tuple and precedence, ordinary versus management mode, the publication → read-only evaluation → explicit decision → separately authorized mutation lifecycle, and all seven boundary failure names: `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, `MODULE_ROUTE_UNRESOLVED`, and the existing derived navigation mismatch name `NAVIGATION_REPOSITORY_MISMATCH`.

Document migration classification exactly: valid v2.5.0 projects are `NO_MIGRATION`; older projects using the existing fixed unversioned Framework source folder require an explicit project-local migration decision and validation; no automatic rewrite or upgrade is specified. Keep P0-4 as a future consumer of the interface/invariants only and do not describe a central service, automatic synchronization, or centralized evolution mechanism as decided.

**Gate B — after Task 7:** Review all cross-module consumers, management/consumer projection boundaries, migration language, and exact failure names. Confirm the Registry is metadata-only and that every mutation path still requires Project authority plus Role Protocol/Work Unit authorization.

**Verify:**

```powershell
python -m unittest .gpt-codex.tests.test_consumer_workspace .gpt-codex.tests.test_context_binding .gpt-codex.tests.test_self_hosting_validator
```

**Commit:** `git add .gpt-codex/README.md .gpt-codex/BOOTSTRAP_PROMPT.md .gpt-codex/tests/test_consumer_workspace.py .gpt-codex/tests/test_context_binding.py; git commit -m "docs: define framework project separation operations"`

### Task 8: Run full regression, validators, and evidence closure

**Files:** all implementation files in the File Map; no additional source or schema file is authorized.

**TDD/verification:** Run the complete suite and validators after Task 7. Do not weaken tests, delete existing assertions, or change expected failure names to make the suite pass.

```powershell
python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
python .gpt-codex/scripts/validate_consumer_projection.py --root .
git diff --check
git status --short
```

Record the actual discovered test count and each validator result in the implementation evidence. Re-run the focused suites for any failure, classify the cause, and fix only within this P0-3 scope. Confirm the worktree is clean, repository/project identity is unchanged, no project-local CONTROL/STATE was overwritten, no schema version changed, and no release/publish occurred. Commit the final verification evidence only if the implementation workflow requires a tracked evidence file already authorized by its Work Unit; otherwise leave evidence in the result envelope.

Do not create a verification-only commit when no authorized evidence file changed; report the full-suite and validator evidence in the result envelope.

## Compatibility and Migration Contract

- Existing valid v2.5.0 projects remain compatible and classify as `NO_MIGRATION`.
- Existing project-context binding remains the required first identity check; the instruction mismatch reason is normalized to `CROSS_PROJECT_CONTEXT_MISMATCH`.
- Existing GitHub binding remains repository-ID authoritative. An absent observed full name is tolerated when the ID matches; a present contradictory full name fails closed.
- Existing Project Map and Resume files remain derived artifacts. Their identity checks and route classifications continue to run only after authoritative identity validation.
- Existing Role Protocol, Work Unit, CONTROL/STATE, result-envelope, Git continuity, publication, and consumer-projection contracts remain authoritative in their current layers.
- Existing fixed-folder Framework compatibility remains read-only and advisory. Evaluation can report `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`; only an explicit project-authorized Work Unit can permit a subsequent mutation.
- No new required schema/template field, version bump, or automatic migration is part of P0-3.

## Contracts, Invariants, and Failure Vocabulary

**Contracts affected:** `PROJECT_IDENTITY_CONTRACT`, `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`, `FRAMEWORK_COMPATIBILITY_EVALUATION`, and `CONTEXT_CONTAMINATION_DECISION`.

**Invariants affected:** one authoritative project identity tuple per project; Project root remains authoritative; Framework root remains auxiliary/read-only for consumers; management/self-hosting is explicit and non-inheritable; Registry is metadata-only; Map/Resume are derived; Framework upgrades are evaluated but not propagated; cross-project context or repository contamination fails closed; role/action, Work Unit, Git continuity, and publication remain separate authority gates.

**Failure vocabulary:** `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, `MODULE_ROUTE_UNRESOLVED`, and existing derived `NAVIGATION_REPOSITORY_MISMATCH`. Existing low-level names not in this vocabulary must not be emitted for these boundary decisions.

## P0-4 Boundary and Non-Goals

P0-4 is not implemented or pre-decided. P0-3 exposes only the identity, authority, compatibility-result, and contamination interfaces that a future isolation/evolution phase may consume. The implementation must not add a centralized Framework service, automatic project synchronization, automatic upgrade propagation, shared mutable project state, cross-project write capability, new execution authority to the Registry, release/publish behavior, or a new module.

## Final Review Checklist

- [ ] Every production change is in the File Map and belongs to an existing affected module.
- [ ] Every behavior change has RED → GREEN → REFACTOR tests with exact names and commands.
- [ ] Gate A passed after Task 3 before cross-module integration.
- [ ] Gate B passed after Task 7 before final regression.
- [ ] Full test discovery and all three validators pass with recorded evidence.
- [ ] Consumer projection manifest is updated only during implementation Task 6 and validates cleanly.
- [ ] No schema/template required field, VERSION, STATE/CONTROL authority, or release artifact was changed outside explicit project authorization.
- [ ] Worktree is clean and the implementation branch is pushed without amend, rebase, or force-push.
