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

  ~~~python
  VALID_CONTEXT_ID = "11111111-1111-4111-8111-111111111111"
  FOREIGN_CONTEXT_ID = "22222222-2222-4222-8222-222222222222"

  def valid_control() -> dict[str, object]:
      return {
          "project_id": "PRJ-001",
          "project_context_id": VALID_CONTEXT_ID,
          "project_name": "Example Project",
          "framework": {
              "adopted_version": "2.5.0",
              "last_evaluated_version": "2.5.0",
              "evaluation_result": "NO_ACTION",
          },
          "github": {
              "repository_id": "123",
              "repository_full_name": "owner/repo",
              "default_branch": "main",
          },
          "roots": {
              "project_role": "AUTHORITATIVE",
              "framework_role": "ADVISORY",
              "framework_kernel_access": "READ_ONLY",
              "framework_builtins_access": "READ_ONLY",
          },
          "extensions": {
              "guardrails": [{
                  "id": "cross-project-context-binding",
                  "source": "builtin",
                  "version": "1.0.0",
                  "enabled": True,
              }]
          },
      }

  def test_identity_precedence_ignores_project_name_and_framework_version(self):
      control = valid_control()
      control["project_name"] = "Wrong display name"
      control["framework"]["last_evaluated_version"] = "9.9.9"
      decision = evaluate_project_identity(
          control,
          expected_project_id="PRJ-001",
          expected_project_context_id=VALID_CONTEXT_ID,
          expected_repository_id="123",
      )
      self.assertEqual(decision.decision, "ALLOW")
      self.assertTrue(decision.identity_match)

  def test_malformed_control_identity_returns_project_identity_invalid(self):
      control = valid_control()
      control["project_context_id"] = "not-a-uuid"
      decision = evaluate_project_identity(control)
      self.assertEqual(decision.decision, "DENY")
      self.assertEqual(decision.reason, "PROJECT_IDENTITY_INVALID")
      self.assertTrue(decision.hard_stop)

  def test_same_name_different_context_returns_cross_project_context_mismatch(self):
      decision = evaluate_project_identity(
          valid_control(),
          expected_project_context_id=FOREIGN_CONTEXT_ID,
      )
      self.assertEqual(decision.decision, "DENY")
      self.assertEqual(decision.reason, "CROSS_PROJECT_CONTEXT_MISMATCH")

  def test_matching_project_context_is_positively_accepted(self):
      decision = evaluate_project_identity(
          valid_control(),
          expected_project_context_id=VALID_CONTEXT_ID,
      )
      self.assertEqual(decision.decision, "ALLOW")
      self.assertTrue(decision.action_executable)
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected RED: `ProjectIdentity`, `load_project_identity`, and the canonical decision path do not yet exist; the old instruction mismatch assertion still reports `CROSS_PROJECT_INSTRUCTION_MISMATCH`.
- [ ] **Step 3: Implement the minimum behavior.** In `context_binding.py`, add frozen `ProjectIdentity` fields `project_id`, `project_context_id`, `repository_id`, `repository_full_name`, `default_branch`, `project_root`, `framework_root`, `management`, `project_role`, and `framework_role`. Add `load_project_identity(control, *, project_root=None, framework_root=None) -> ProjectIdentity` and `evaluate_project_identity(control, *, expected_project_id=None, expected_project_context_id=None, expected_repository_id=None, expected_repository_full_name=None) -> ContextDecision`. Validate existing fields only; malformed authoritative data raises `ValueError("PROJECT_IDENTITY_INVALID")`. Update instruction/return/bootstrap evaluation to use this path before freshness and role checks, with context mismatch normalized to `CROSS_PROJECT_CONTEXT_MISMATCH`.

  ~~~python
  @dataclass(frozen=True)
  class ProjectIdentity:
      project_id: str
      project_context_id: str
      repository_id: str
      repository_full_name: str
      default_branch: str
      project_root: Path | None
      framework_root: Path | None
      management: bool
      project_role: str
      framework_role: str

  def load_project_identity(
      control: Mapping[str, Any],
      *,
      project_root: Path | None = None,
      framework_root: Path | None = None,
  ) -> ProjectIdentity:
      github = control.get("github")
      roots = control.get("roots")
      project_id = control.get("project_id")
      context_id = control.get("project_context_id")
      if (
          not isinstance(project_id, str) or not project_id.strip()
          or not is_valid_project_context_id(context_id)
          or not isinstance(github, Mapping)
          or not all(isinstance(github.get(key), str) and github.get(key).strip()
                     for key in ("repository_id", "repository_full_name", "default_branch"))
          or not isinstance(roots, Mapping)
      ):
          raise ValueError("PROJECT_IDENTITY_INVALID")
      management = control.get("framework_management_only") is True
      project_role = roots.get("project_role")
      framework_role = roots.get("framework_role")
      ordinary = project_role == "AUTHORITATIVE" and framework_role == "ADVISORY"
      self_hosted = management and project_role == "AUTHORITATIVE" and framework_role == "SELF_MANAGED"
      if not (ordinary or self_hosted):
          raise ValueError("PROJECT_IDENTITY_INVALID")
      return ProjectIdentity(
          project_id=project_id.strip(),
          project_context_id=context_id,
          repository_id=github["repository_id"].strip(),
          repository_full_name=github["repository_full_name"].strip(),
          default_branch=github["default_branch"].strip(),
          project_root=project_root,
          framework_root=framework_root,
          management=management,
          project_role=project_role,
          framework_role=framework_role,
      )

  def evaluate_project_identity(
      control: Mapping[str, Any],
      *,
      expected_project_id: str | None = None,
      expected_project_context_id: str | None = None,
      expected_repository_id: str | None = None,
      expected_repository_full_name: str | None = None,
  ) -> ContextDecision:
      try:
          identity = load_project_identity(control)
      except (TypeError, ValueError, KeyError):
          return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
      if expected_project_id is not None and expected_project_id != identity.project_id:
          return _decision("DENY", "PROJECT_IDENTITY_INVALID", hard_stop=True)
      if expected_project_context_id is not None and expected_project_context_id != identity.project_context_id:
          return _decision("DENY", "CROSS_PROJECT_CONTEXT_MISMATCH", packet_status="QUARANTINED")
      if expected_repository_id is not None and expected_repository_id != identity.repository_id:
          return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", packet_status="QUARANTINED")
      if (
          expected_repository_full_name is not None
          and expected_repository_full_name != identity.repository_full_name
      ):
          return _decision("DENY", "GITHUB_REPOSITORY_MISMATCH", packet_status="QUARANTINED")
      return _decision(
          "ALLOW",
          "IDENTITY_MATCH",
          identity_match=True,
          freshness_match=True,
          action_executable=True,
          authority="CURRENT_PROJECT_PATH",
      )
  ~~~
- [ ] **Step 4: Run GREEN.** Run both Step 2 commands. Expected GREEN: all identity tests pass, matching context returns `ALLOW`, and no test emits `CROSS_PROJECT_INSTRUCTION_MISMATCH` for a context boundary.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`. Expected: existing cross-project and validator behavior remains passing with the normalized failure name.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm identity comes from Project CONTROL, Framework root is never authoritative, no schema/template changes exist, no duplicate identity parser exists, and downstream callers receive the existing `ContextDecision` shape.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_framework_project_separation.py` followed by `git commit -m "feat: establish canonical project identity boundary"`.

### Task 2: Repository binding and cross-project contamination

**Files:** `.gpt-codex/scripts/github_repository_binding.py`, `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/tests/test_github_repository_binding.py`, `.gpt-codex/tests/test_multi_project_github_isolation.py`

- [ ] **Step 1: Add failing tests.** Add/update `test_repository_id_match_with_absent_observed_full_name_allows`, `test_present_contradictory_repository_full_name_denies`, `test_foreign_repository_id_denies_with_github_repository_mismatch`, `test_same_context_wrong_repository_denies_instruction`, `test_wrong_context_same_repository_denies_return`, and `test_repository_scan_is_read_only`. Also assert an existing valid repository binding remains valid with matching ID and matching full name.

  ~~~python
  CONTROL = {
      "github": {
          "repository_id": "repo-1",
          "repository_full_name": "owner/project",
          "default_branch": "main",
      }
  }

  def test_repository_id_match_with_absent_observed_full_name_allows(self):
      observed = ObservedRepository("repo-1", None, "origin", "github:owner/project")
      decision = compare_repository_binding(CONTROL, observed)
      self.assertEqual(decision, BindingDecision("ALLOW", "GITHUB_REPOSITORY_ID_MATCH", True, True))

  def test_present_contradictory_repository_full_name_denies(self):
      observed = ObservedRepository("repo-1", "other/project", "origin", "github:other/project")
      decision = compare_repository_binding(CONTROL, observed)
      self.assertEqual(decision.decision, "DENY")
      self.assertEqual(decision.reason, "GITHUB_REPOSITORY_MISMATCH")
      self.assertFalse(decision.identity_match)
      self.assertFalse(decision.mutation_allowed)

  def test_foreign_repository_id_denies_with_github_repository_mismatch(self):
      observed = ObservedRepository("repo-2", "owner/project", "origin", "github:owner/project")
      decision = compare_repository_binding(CONTROL, observed)
      self.assertEqual(decision, BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False))
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'`. Expected RED: the current present-full-name contradiction fixture still returns `ALLOW` because only repository ID is compared.
- [ ] **Step 3: Implement the minimum behavior.** In `compare_repository_binding(control: Mapping[str, Any], observed: ObservedRepository) -> BindingDecision`, compare repository ID first, then compare a non-empty observed full name.

  ~~~python
  binding = _binding_from_control(control)
  if binding is None:
      return BindingDecision("DENY", "REPOSITORY_CONFLICT", False, False)
  if str(observed.repository_id) != binding.repository_id:
      return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
  if (
      observed.repository_full_name not in (None, "")
      and str(observed.repository_full_name).strip() != binding.repository_full_name
  ):
      return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
  return BindingDecision("ALLOW", "GITHUB_REPOSITORY_ID_MATCH", True, True)
  ~~~

  Preserve an absent observed full name as ID-compatible and keep `scan_repository_compatibility` read-only. Thread canonical context decisions through instruction/return evaluation so context mismatch precedes repository mismatch.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_github_repository_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_multi_project_github_isolation.py'`. Expected GREEN: matching ID/full name and matching ID/absent full name allow; contradictions deny with `GITHUB_REPOSITORY_MISMATCH`.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_git_continuity.py'`. Expected: context decisions and Git continuity gates remain passing.
- [ ] **Step 6: Refactor/check contract consistency.** Verify repository binding never updates CONTROL, remotes, branches, sync state, or publication state; preserve canonical remote URL tests and all existing read-only scan classifications.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/github_repository_binding.py .gpt-codex/scripts/context_binding.py .gpt-codex/tests/test_github_repository_binding.py .gpt-codex/tests/test_multi_project_github_isolation.py` followed by `git commit -m "fix: fail closed on repository and context contamination"`.

### Task 3: Project authority boundary, read-only compatibility, and exact adoption authorization

**Files:** `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_framework_project_separation.py`, `.gpt-codex/tests/test_context_binding.py`, `.gpt-codex/tests/test_consumer_workspace.py`

- [ ] **Step 1: Add failing tests.** Add `test_project_authority_boundary_rejects_framework_write`, `test_compatibility_evaluation_returns_exact_classification_without_mutation`, `test_compatibility_result_does_not_authorize_adoption`, `test_conflict_is_read_only_and_cannot_be_adopted`, `test_foreign_work_unit_project_binding_returns_cross_project_context_mismatch`, `test_foreign_result_context_returns_cross_project_context_mismatch`, `test_matching_result_context_is_accepted`, `test_matching_evidence_project_id_is_accepted`, `test_foreign_evidence_project_id_returns_project_identity_invalid`, `test_evidence_validation_does_not_mutate_project_state`, `test_evidence_cannot_grant_adoption_authority`, `test_matching_project_context_and_repository_are_accepted`, and `test_valid_repository_binding_remains_valid`. Put Result Envelope tests in existing `test_context_binding.py` and Evidence tests in the new focused test file. Snapshot CONTROL before/after evaluation and assert byte-equivalent JSON.

  ~~~python
  def complete_result(source_context_id: str) -> dict[str, object]:
      return {
          "source_project_context_id": source_context_id,
          "source_github_repository_id": "123",
          "source_github_repository_full_name": "owner/repo",
          "status": "PASS",
          "work_unit_id": "WU-001",
          "state_revision": 6,
      }

  def test_foreign_result_context_returns_cross_project_context_mismatch(self):
      decision = evaluate_return(
          complete_result(FOREIGN_CONTEXT_ID),
          active_context_id=VALID_CONTEXT_ID,
          current_state_revision=6,
          project_control=valid_control(),
          local_repository_id="123",
      )
      self.assertEqual(decision.decision, "DENY")
      self.assertEqual(decision.reason, "CROSS_PROJECT_CONTEXT_MISMATCH")

  def test_matching_result_context_is_accepted(self):
      decision = evaluate_return(
          complete_result(VALID_CONTEXT_ID),
          active_context_id=VALID_CONTEXT_ID,
          current_state_revision=6,
          project_control=valid_control(),
          local_repository_id="123",
      )
      self.assertEqual(decision.decision, "ALLOW")
      self.assertTrue(decision.action_executable)

  def test_foreign_evidence_project_id_is_rejected(self):
      evidence = {
          "kernel_version": "2.0.0",
          "schema_version": 1,
          "evidence_id": "EVIDENCE-1",
          "project_id": "PRJ-FOREIGN",
          "source": "TOOL_OBSERVED",
          "subject": "verification",
          "state_revision": 6,
          "result": "PASS",
      }
      errors = validate_evidence_project_binding(
          evidence,
          valid_control(),
          current_state_revision=6,
      )
      self.assertEqual(errors, ["PROJECT_IDENTITY_INVALID"])

  def test_matching_evidence_project_id_is_accepted(self):
      evidence = {
          "kernel_version": "2.0.0",
          "schema_version": 1,
          "evidence_id": "EVIDENCE-1",
          "project_id": "PRJ-001",
          "source": "TOOL_OBSERVED",
          "subject": "verification",
          "state_revision": 6,
          "result": "PASS",
      }
      control = valid_control()
      before = json.dumps(control, sort_keys=True)
      errors = validate_evidence_project_binding(evidence, control, current_state_revision=6)
      after = json.dumps(control, sort_keys=True)
      self.assertEqual(errors, [])
      self.assertEqual(before, after)

  def test_compatibility_result_does_not_authorize_adoption(self):
      result = evaluate_framework_compatibility(
          valid_control(),
          {
              "evaluated_version": "2.6.0",
              "compatible": True,
              "reusable": False,
              "requires_migration": False,
          },
      )
      self.assertEqual(result["classification"], "RECOMMENDED_UPGRADE")
      self.assertFalse(result["mutated"])
      self.assertFalse(result["adoption_authorized"])

  def test_evidence_cannot_grant_adoption_authority(self):
      evidence = {
          "project_id": "PRJ-001",
          "evidence_id": "EVIDENCE-1",
          "source": "TOOL_OBSERVED",
          "subject": "compatibility",
          "state_revision": 6,
          "result": "PASS",
      }
      self.assertEqual(validate_evidence_project_binding(evidence, valid_control()), [])
      self.assertEqual(
          validate_framework_adoption(valid_control(), {}, {"project_id": "PRJ-001"}, current_state_revision=6),
          ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
      )

  def test_project_authority_boundary_rejects_framework_write(self):
      identity = load_project_identity(valid_control())
      decision = evaluate_project_authority_boundary(
          identity,
          source="framework",
          operation="WRITE",
      )
      self.assertEqual(decision.decision, "DENY")
      self.assertEqual(decision.reason, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION")
      self.assertTrue(decision.hard_stop)

  def test_compatibility_evaluation_returns_exact_classification_without_mutation(self):
      control = valid_control()
      before = json.dumps(control, sort_keys=True)
      result = evaluate_framework_compatibility(
          control,
          {
              "evaluated_version": "2.5.0",
              "compatible": True,
              "reusable": False,
              "requires_migration": False,
          },
      )
      self.assertEqual(result["classification"], "NO_ACTION")
      self.assertEqual(result["reason"], "ADOPTED_VERSION_MATCH")
      self.assertFalse(result["mutated"])
      self.assertFalse(result["adoption_authorized"])
      self.assertEqual(json.dumps(control, sort_keys=True), before)

  def test_adoption_requires_every_existing_authority_predicate(self):
      instruction = {
          "target_work_unit": "WU-001",
          "expected_state_revision": 6,
          "executor_role": "CODEX_IMPLEMENTER",
          "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
          "forbidden_actions": [],
      }
      work_unit = {
          "project_id": "PRJ-001",
          "work_unit_id": "WU-001",
          "state": "AUTHORIZED",
          "basis_state_revision": 6,
      }
      self.assertEqual(
          validate_framework_adoption(valid_control(), instruction, work_unit, current_state_revision=6),
          [],
      )
      instruction["authorized_actions"] = ["READ"]
      self.assertEqual(
          validate_framework_adoption(valid_control(), instruction, work_unit, current_state_revision=6),
          ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
      )
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected RED: no compatibility evaluator, authority-boundary evaluator, or adoption predicate exists; foreign Work Unit/Result assertions have no identity-first decision.
- [ ] **Step 3: Implement the minimum behavior.** Add the four bounded APIs below. Result context is handled by existing `context_binding.evaluate_return`; Evidence handling is separate and does not accept context/repository fields.

  ~~~python
  def evaluate_project_authority_boundary(
      identity: ProjectIdentity,
      *,
      source: str,
      operation: str,
      explicit_adoption: bool = False,
  ) -> ContextDecision:
      if source == "framework" and operation in {"WRITE", "MUTATE"}:
          return _decision("DENY", "PROJECT_AUTHORITY_BOUNDARY_VIOLATION", hard_stop=True)
      if source == "framework" and operation == "ADOPT" and not explicit_adoption:
          return _decision("DENY", "FRAMEWORK_ADOPTION_NOT_AUTHORIZED")
      return _decision(
          "ALLOW",
          "PROJECT_AUTHORITY_BOUNDARY_VALID",
          identity_match=True,
          action_executable=source == "project",
          authority="CURRENT_PROJECT_PATH" if source == "project" else "FRAMEWORK_AUXILIARY_READ",
      )

  def evaluate_framework_compatibility(
      project_control: Mapping[str, Any],
      framework_facts: Mapping[str, Any],
  ) -> dict[str, Any]:
      if framework_facts.get("identity_conflict") or framework_facts.get("authority_conflict"):
          classification, reason = "CONFLICT", "FRAMEWORK_PROJECT_CONFLICT"
      elif framework_facts.get("evaluated_version") == project_control.get("framework", {}).get("adopted_version"):
          classification, reason = "NO_ACTION", "ADOPTED_VERSION_MATCH"
      elif framework_facts.get("requires_migration"):
          classification, reason = "REQUIRED_MIGRATION", "EXPLICIT_MIGRATION_REQUIRED"
      elif framework_facts.get("compatible") and framework_facts.get("reusable"):
          classification, reason = "OPTIONAL_REUSE", "COMPATIBLE_REUSE_AVAILABLE"
      elif framework_facts.get("compatible"):
          classification, reason = "RECOMMENDED_UPGRADE", "COMPATIBLE_NEWER_FRAMEWORK"
      else:
          classification, reason = "CONFLICT", "FRAMEWORK_COMPATIBILITY_CONFLICT"
      return {
          "classification": classification,
          "reason": reason,
          "mutated": False,
          "adoption_authorized": False,
      }

  def validate_framework_adoption(
      project_control: Mapping[str, Any],
      instruction: Mapping[str, Any],
      work_unit: Mapping[str, Any],
      *,
      current_state_revision: int,
  ) -> list[str]:
      if project_control.get("project_id") != work_unit.get("project_id"):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      if instruction.get("target_work_unit") != work_unit.get("work_unit_id"):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      if work_unit.get("state") != "AUTHORIZED":
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      if not (
          instruction.get("expected_state_revision")
          == work_unit.get("basis_state_revision")
          == current_state_revision
      ):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      executor_role = instruction.get("executor_role")
      authorized_actions = instruction.get("authorized_actions")
      forbidden_actions = instruction.get("forbidden_actions")
      if validate_executor_role(executor_role):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      if "MUTATE_APPROVED_SCOPE" not in (authorized_actions or []):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      if validate_action_authority(executor_role, authorized_actions, forbidden_actions):
          return ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"]
      return []

  def validate_evidence_project_binding(
      evidence: Mapping[str, Any],
      project_control: Mapping[str, Any],
      *,
      current_state_revision: int | None = None,
  ) -> list[str]:
      if evidence.get("project_id") != project_control.get("project_id"):
          return ["PROJECT_IDENTITY_INVALID"]
      return []
  ~~~

  Extend the existing import in `validate_project.py` to include `evaluate_return`, `evaluate_project_identity`, and the new bounded helpers; no Result identity validator is created. The existing Result Envelope seam is `context_binding.evaluate_return(envelope, active_context_id, current_state_revision=None, analysis_only=False, project_control=None, local_repository_id=None) -> ContextDecision`. The current Evidence schema requires a non-negative integer `state_revision` but does not require equality with the current state revision. Existing schema validation owns that type/range rule; this helper compares only `project_id` and does not reject historical evidence for being older. `current_state_revision` remains an accepted diagnostic argument without an equality check. `validate_framework_adoption` validates adoption only; it does not accept Result or Evidence. Every failed adoption predicate returns `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, while foreign Result context returns `CROSS_PROJECT_CONTEXT_MISMATCH` and foreign Evidence `project_id` returns `PROJECT_IDENTITY_INVALID`.

  Use the existing durable-reference traversal in `validate_project.py` with an explicit branch:

  ~~~python
  candidate = load(result_path)
  if isinstance(candidate, dict) and "status" in candidate:
      durable_results[ref] = candidate
      errors.extend(f"RESULT {ref}: {error}" for error in validate_result_authority(candidate))
      errors.extend(f"RESULT_PROTOCOL {ref}: {error}" for error in validate_result_protocol(candidate))
      if "source_project_context_id" in candidate:
          decision = evaluate_return(
              candidate,
              control.get("project_context_id"),
              state.get("revision"),
              project_control=control,
              local_repository_id=(control.get("github") or {}).get("repository_id"),
          )
          if decision.decision != "ALLOW":
              errors.append(f"RESULT {ref}: {decision.reason}")
  elif isinstance(candidate, dict) and "evidence_id" in candidate:
      errors.extend(
          f"EVIDENCE {ref}: {error}"
          for error in validate_evidence_project_binding(
              candidate,
              control,
              current_state_revision=state.get("revision"),
          )
      )
  ~~~
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_project_separation.py'`. Expected GREEN: all five classifications are exact, evaluation snapshots are unchanged, matching Project identity is accepted, foreign Work Unit Project binding is rejected according to its defined Project/context binding rule, foreign Result Envelope `source_project_context_id` is rejected with `CROSS_PROJECT_CONTEXT_MISMATCH`, foreign Evidence `project_id` is rejected with `PROJECT_IDENTITY_INVALID`, compatibility evaluation remains read-only, and adoption remains unauthorized unless every existing authority predicate passes.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'`. Expected: existing context guardrail and compatibility vocabulary tests pass.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm `validate_project.py` reuses `role_communication.validate_action_authority` rather than defining a second permission mechanism; compatibility evaluation cannot mutate Project files; no schema/template field is added; and `CONFLICT` cannot be adopted.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/context_binding.py .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_framework_project_separation.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_consumer_workspace.py` followed by `git commit -m "feat: enforce project authority and compatibility evaluation"`.

**Gate A — after Task 3**
- [ ] Review canonical `ProjectIdentity`, identity precedence, exact context/repository mismatch outcomes, authority boundary, all five compatibility outcomes, compatibility non-authority, exact adoption field mappings, Role Protocol reuse, Work Unit/revision reuse, and no schema/projection dependency.
- [ ] Confirm Result Envelope context binding through `evaluate_return`: foreign `source_project_context_id` yields `CROSS_PROJECT_CONTEXT_MISMATCH`, while matching Result context yields `ALLOW`.
- [ ] Confirm Evidence `project_id` binding through `validate_evidence_project_binding`: foreign Evidence yields `PROJECT_IDENTITY_INVALID`, while matching Evidence yields no binding error.
- [ ] Confirm all focused tests for Tasks 1–3 pass before Task 4. Gate A has no projection-closure dependency.

### Task 4: Validator and explicit management/self-hosting integration

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/scripts/validate_framework.py`, `.gpt-codex/tests/test_validator_context_binding.py`, `.gpt-codex/tests/test_self_hosting_validator.py`, `.gpt-codex/tests/test_framework_module_validation.py`, `.gpt-codex/tests/test_framework_module_routing.py`

`framework_module_routing.py` is NO CHANGE; P0-2 already froze Registry routing as metadata-only and responsibility-first.

- [ ] **Step 1: Add failing tests.** Add `test_project_validator_rejects_framework_metadata_as_authority`, `test_management_control_requires_explicit_management_profile`, `test_consumer_control_rejects_management_identity_and_self_managed_root`, `test_registry_route_describes_responsibility_without_execution_authority`, `test_registry_permissions_do_not_authorize_project_adoption`, `test_unresolved_registry_responsibility_returns_module_route_unresolved`, and `test_registry_does_not_offer_fuzzy_fallback_or_eighth_module`.

  ~~~python
  def test_consumer_control_rejects_management_identity_and_self_managed_root(self):
      control = valid_control()
      control["framework_management_only"] = True
      control["governance_profile"] = "FRAMEWORK_MANAGEMENT"
      control["roots"]["framework_role"] = "SELF_MANAGED"
      errors = validate_project_identity_boundary(control, consumer=True)
      self.assertIn("PROJECT_AUTHORITY_BOUNDARY_VIOLATION", errors)

  def test_management_control_requires_explicit_management_profile(self):
      control = valid_control()
      control["framework_management_only"] = True
      control["roots"]["framework_role"] = "SELF_MANAGED"
      control["governance_profile"] = "FRAMEWORK_MANAGEMENT"
      self.assertEqual(validate_project_identity_boundary(control, consumer=False), [])

  def test_registry_route_describes_responsibility_without_execution_authority(self):
      decision = route_responsibility(
          ROOT,
          "identity-context",
          "project and repository identity",
      )
      self.assertEqual(decision.primary_module, "identity-context")
      self.assertFalse(hasattr(decision, "authorized_actions"))

  def test_unresolved_registry_responsibility_returns_module_route_unresolved(self):
      with self.assertRaises(ModuleRoutingError) as raised:
          route_responsibility(ROOT, "identity-context", "unregistered responsibility")
      self.assertEqual(raised.exception.code, "MODULE_ROUTE_UNRESOLVED")

  def test_registry_permissions_do_not_authorize_project_adoption(self):
      decision = route_responsibility(ROOT, "identity-context", "project and repository identity")
      self.assertNotIn("MUTATE_APPROVED_SCOPE", decision.contracts_affected)
      self.assertNotIn("MUTATE_APPROVED_SCOPE", decision.invariants_affected)
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py'`. Expected RED: validator orchestration does not yet invoke identity-first authority checks for all project validation paths; Registry production routing remains unchanged.
- [ ] **Step 3: Implement the minimum behavior.** Make `validate_project.py` load Project identity first, then validate existing CONTROL/STATE/Work Unit/Result and derived artifacts. Keep `validate_framework.py` as the Framework management-root validator. Management is valid only when `framework_management_only=True`, `governance_profile="FRAMEWORK_MANAGEMENT"`, and Framework root is `SELF_MANAGED`; consumers reject those markers and require Project `AUTHORITATIVE`, Framework `ADVISORY`, and read-only Framework/Kernel/Built-ins. Do not modify `framework_module_routing.py`; add only regression assertions against its existing metadata-only route.

  ~~~python
  def validate_project_identity_boundary(
      control: Mapping[str, Any],
      *,
      consumer: bool,
  ) -> list[str]:
      management = control.get("framework_management_only") is True
      roots = control.get("roots") or {}
      explicit_management = (
          management
          and control.get("governance_profile") == "FRAMEWORK_MANAGEMENT"
          and roots.get("framework_role") == "SELF_MANAGED"
      )
      ordinary_consumer = (
          not management
          and control.get("governance_profile") != "FRAMEWORK_MANAGEMENT"
          and roots.get("project_role") == "AUTHORITATIVE"
          and roots.get("framework_role") == "ADVISORY"
          and roots.get("framework_kernel_access") == "READ_ONLY"
          and roots.get("framework_builtins_access") == "READ_ONLY"
      )
      if consumer and not ordinary_consumer:
          return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
      if not consumer and not explicit_management:
          return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
      return []

  identity_decision = evaluate_project_identity(control)
  if identity_decision.decision != "ALLOW":
      errors.append(identity_decision.reason)
  else:
      errors.extend(validate_optional_navigation_and_resume(root, gov, control))
  ~~~

  The management validator keeps the explicit three-marker branch in `validate_framework.py`:

  ~~~python
  management_markers = (
      control.get("framework_management_only") is True,
      control.get("governance_profile") == "FRAMEWORK_MANAGEMENT",
      (control.get("roots") or {}).get("framework_role") == "SELF_MANAGED",
  )
  if any(management_markers) and not all(management_markers):
      errors.append("PROJECT_AUTHORITY_BOUNDARY_VIOLATION")
  ~~~
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_self_hosting_validator.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py'`. Expected GREEN: management and consumer boundaries pass, Registry returns metadata only, and unresolved responsibility returns `MODULE_ROUTE_UNRESOLVED`.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py'` and `python .gpt-codex/scripts/validate_framework.py`. Expected: v2.5.0 Registry and Framework validation pass without a routing production diff.
- [ ] **Step 6: Refactor/check contract consistency.** Verify no Registry route output is copied into `authorized_actions`, mutation permission, role authority, or adoption consent; no fuzzy fallback or eighth module exists; and only listed MODIFY files have production changes.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/validate_project.py .gpt-codex/scripts/validate_framework.py .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_self_hosting_validator.py .gpt-codex/tests/test_framework_module_validation.py .gpt-codex/tests/test_framework_module_routing.py` followed by `git commit -m "feat: integrate management and registry authority boundaries"`.

### Task 5: Preserve derived navigation, Resume, Role, and Git authority

**Files:** `.gpt-codex/scripts/validate_project.py`, `.gpt-codex/tests/test_project_navigation.py`, `.gpt-codex/tests/test_continuity_resume.py`, `.gpt-codex/tests/test_context_window_resume.py`, `.gpt-codex/tests/test_instruction_role_contract.py`, `.gpt-codex/tests/test_git_continuity.py`

**NO API SIGNATURE CHANGE:** `.gpt-codex/scripts/project_navigation.py` remains unchanged with `validate_navigation_identity(navigation: dict[str, Any], control: dict[str, Any]) -> None`. `.gpt-codex/scripts/continuity_resume.py` remains unchanged with its current `load_resume_checkpoint(gov: Path) -> dict[str, Any] | None` helper and the established `load_continuity_resume` contract name; the Resume flow reloads Project CONTROL/STATE internally. Neither API receives a ProjectIdentity object and neither file has a planned production diff. Any future API change is outside this Plan.

- [ ] **Step 1: Add failing tests.** Add `test_project_identity_failure_prevents_map_success`, `test_matching_identity_permits_existing_navigation_flow`, `test_valid_identity_with_stale_map_returns_existing_map_result`, `test_resume_cannot_substitute_its_context_identity_for_control`, `test_navigation_repository_mismatch_remains_derived_result`, `test_role_protocol_remains_action_authority_after_identity_allow`, and `test_git_publish_gate_remains_separate_from_identity_decision`.

  ~~~python
  def test_project_identity_failure_prevents_map_success(self):
      control = valid_control()
      control["project_context_id"] = FOREIGN_CONTEXT_ID
      with patch("validate_project.validate_optional_navigation_and_resume") as derived:
          errors = validate_identity_before_derived(
              ROOT,
              ROOT / ".gpt-codex",
              control,
              active_context_id=VALID_CONTEXT_ID,
              local_repository_id="123",
          )
      self.assertEqual(errors, ["CROSS_PROJECT_CONTEXT_MISMATCH"])
      derived.assert_not_called()

  def test_matching_identity_permits_existing_navigation_flow(self):
      with patch(
          "validate_project.validate_optional_navigation_and_resume",
          return_value=[],
      ) as derived:
          errors = validate_identity_before_derived(
              ROOT,
              ROOT / ".gpt-codex",
              valid_control(),
              active_context_id=VALID_CONTEXT_ID,
              local_repository_id="123",
          )
      self.assertEqual(errors, [])
      derived.assert_called_once()

  def test_valid_identity_with_stale_map_returns_existing_map_result(self):
      self.assertEqual(
          classify_map_route(["identity-context"], ["identity-context"], map_exists=True),
          "MAP_PARTIAL",
      )

  def test_navigation_repository_mismatch_remains_derived_result(self):
      navigation = {
          "project_id": "PRJ-001",
          "project_context_id": VALID_CONTEXT_ID,
          "repository_id": "foreign-repository",
      }
      with self.assertRaisesRegex(ValueError, "NAVIGATION_REPOSITORY_MISMATCH"):
          validate_navigation_identity(navigation, valid_control())
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_project_navigation.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_continuity_resume.py'`. Expected RED: new ordering assertions have no identity-first validation seam; navigation and Resume APIs remain unchanged.
- [ ] **Step 3: Implement the minimum behavior.** In `validate_project.py`, evaluate canonical identity first. Only when that decision is executable/allowed, call existing `validate_navigation_identity(navigation, control)` and `load_continuity_resume` using authoritative Project CONTROL and repository ID; never pass ProjectIdentity into either API. Preserve Map authority `DERIVED_NAVIGATION_INDEX` and Resume authority `DERIVED_CACHE`. Keep Role Protocol action authority and `git_continuity.evaluate_publish_gate` sync/attestation/remote/publication authority.

  ~~~python
  def validate_identity_before_derived(
      root: Path,
      gov: Path,
      control: Mapping[str, Any],
      *,
      active_context_id: str,
      local_repository_id: str,
  ) -> list[str]:
      decision = evaluate_project_identity(
          control,
          expected_project_context_id=active_context_id,
          expected_repository_id=local_repository_id,
      )
      if decision.decision != "ALLOW":
          return [decision.reason]
      return validate_optional_navigation_and_resume(root, gov, control)
  ~~~

  This is the upstream ordering fragment only. The existing navigation and Resume implementations remain untouched and reload authoritative Project CONTROL/STATE through their current APIs.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_project_navigation.py'`, `python -m unittest discover -s .gpt-codex/tests -p 'test_continuity_resume.py'`, and `python -m unittest discover -s .gpt-codex/tests -p 'test_context_window_resume.py'`. Expected GREEN: identity failure blocks derived success, matching identity reaches existing APIs, stale Map yields existing `MAP_*` behavior, Resume cannot substitute CONTROL, and `NAVIGATION_REPOSITORY_MISMATCH` remains derived.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_instruction_role_contract.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_git_continuity.py'`. Expected: Role Protocol and Git publication gates remain independently authoritative.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm `project_navigation.py` and `continuity_resume.py` have no diff, identity failure cannot be downgraded by Map/Resume, and identity allow does not authorize role/action, commit, push, or publish.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/scripts/validate_project.py .gpt-codex/tests/test_project_navigation.py .gpt-codex/tests/test_continuity_resume.py .gpt-codex/tests/test_context_window_resume.py .gpt-codex/tests/test_instruction_role_contract.py .gpt-codex/tests/test_git_continuity.py` followed by `git commit -m "test: preserve derived continuity and execution authorities"`.

### Task 6: Exact-path consumer projection manifest closure

**Files:** `.gpt-codex/release/consumer-projection-manifest.json`, `.gpt-codex/tests/test_consumer_projection.py`, `.gpt-codex/tests/test_consumer_runtime_closure.py`, `.gpt-codex/tests/test_consumer_workspace.py`

Production scope is frozen: `.gpt-codex/scripts/consumer_projection.py` and `.gpt-codex/scripts/validate_consumer_projection.py` are NO CHANGE. Task 6 changes only the manifest and tests. RED fails because exact paths are absent or misclassified, not because a projection algorithm is missing.

- [ ] **Step 1: Add failing tests.** Add `test_projection_manifest_classifies_separation_design_as_development_history`, `test_projection_manifest_classifies_separation_plan_as_development_history`, `test_new_separation_test_is_management_only`, `test_consumer_required_projection_excludes_management_control`, `test_consumer_required_projection_excludes_registry_execution_metadata`, `test_projection_rejects_cross_project_management_identity_contamination`, and `test_runtime_closure_does_not_import_framework_management_authority`.

  ~~~json
  {
    "docs/superpowers/specs/2026-09-13-framework-project-separation-design.md": "DEVELOPMENT_HISTORY",
    "docs/superpowers/plans/2026-09-13-framework-project-separation.md": "DEVELOPMENT_HISTORY",
    ".gpt-codex/tests/test_framework_project_separation.py": "MANAGEMENT_ONLY"
  }
  ~~~

  ~~~python
  manifest = load_projection_manifest(ROOT)
  paths = manifest["paths"]
  self.assertEqual(
      paths["docs/superpowers/specs/2026-09-13-framework-project-separation-design.md"],
      "DEVELOPMENT_HISTORY",
  )
  self.assertEqual(
      paths["docs/superpowers/plans/2026-09-13-framework-project-separation.md"],
      "DEVELOPMENT_HISTORY",
  )
  self.assertEqual(paths[".gpt-codex/tests/test_framework_project_separation.py"], "MANAGEMENT_ONLY")
  audit = audit_projection_paths(ROOT, manifest)
  self.assertEqual(audit["unknown_paths"], [])
  self.assertEqual(audit["missing_required_paths"], [])
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'`. Expected RED: the Design and Plan exact paths are not both `DEVELOPMENT_HISTORY` and the new test path is not `MANAGEMENT_ONLY`.
- [ ] **Step 3: Implement the minimum behavior.** Modify only `.gpt-codex/release/consumer-projection-manifest.json`: add exact entries for `docs/superpowers/specs/2026-09-13-framework-project-separation-design.md` and `docs/superpowers/plans/2026-09-13-framework-project-separation.md` as `DEVELOPMENT_HISTORY`, and `.gpt-codex/tests/test_framework_project_separation.py` as `MANAGEMENT_ONLY`. The only newly created path authorized by this Plan is `.gpt-codex/tests/test_framework_project_separation.py`; no other new implementation, test, or documentation path is authorized. Keep management CONTROL, management-only Built-ins, release metadata, Framework operational state, and Registry metadata outside consumer-required content. Do not alter either projection script.
- [ ] **Step 4: Run GREEN.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py'` and `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_runtime_closure.py'`. Expected GREEN: exact manifest paths resolve, projection unknown paths equal 0, and missing required paths equal 0.
- [ ] **Step 5: Run the relevant regression subset.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'` and `python .gpt-codex/scripts/validate_consumer_projection.py --root .`. Expected: runtime closure and consumer validation pass without projection algorithm changes.
- [ ] **Step 6: Refactor/check contract consistency.** Confirm only the manifest is a production MODIFY surface in this task, exact-path validation remains strict, management identity and cross-project Project CONTROL/STATE cannot enter consumer-required projection, and no projection script has a diff.
- [ ] **Step 7: Commit the exact task files.** Run `git add .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/tests/test_consumer_projection.py .gpt-codex/tests/test_consumer_runtime_closure.py .gpt-codex/tests/test_consumer_workspace.py` followed by `git commit -m "feat: enforce separation in consumer projection"`.

### Task 7: Operational docs, compatibility lifecycle, and migration direction

**Files:** `.gpt-codex/README.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md`, `.gpt-codex/tests/test_consumer_workspace.py`, `.gpt-codex/tests/test_context_binding.py`

- [ ] **Step 1: Add failing tests.** Add `test_operational_docs_state_framework_publishes_project_decides`, `test_operational_docs_state_upgrade_evaluation_is_not_adoption`, `test_operational_docs_list_exact_separation_failure_vocabulary`, `test_existing_v25_project_is_no_migration`, and `test_versioned_auxiliary_framework_folder_requires_explicit_migration_to_fixed_source`.

  ~~~python
  SEPARATION_PARAGRAPH = (
      "Valid v2.5.0 projects using the current fixed Framework source remain NO_MIGRATION. "
      "A legacy project still using a versioned auxiliary Framework folder requires an "
      "explicit project-local migration to the fixed unversioned Framework source folder. "
      "Framework publication or compatibility evaluation cannot perform that migration automatically."
  )

  def test_operational_docs_state_framework_publishes_project_decides(self):
      text = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
      self.assertIn("Framework publishes; Project decides", text)

  def test_operational_docs_state_upgrade_evaluation_is_not_adoption(self):
      text = (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8")
      self.assertIn("read-only compatibility evaluation", text)
      self.assertIn("explicit Project decision", text)

  def test_operational_docs_list_exact_separation_failure_vocabulary(self):
      text = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
      for failure in (
          "CROSS_PROJECT_CONTEXT_MISMATCH",
          "GITHUB_REPOSITORY_MISMATCH",
          "PROJECT_IDENTITY_INVALID",
          "PROJECT_AUTHORITY_BOUNDARY_VIOLATION",
          "FRAMEWORK_ADOPTION_NOT_AUTHORIZED",
          "MODULE_ROUTE_UNRESOLVED",
          "NAVIGATION_REPOSITORY_MISMATCH",
      ):
          self.assertIn(failure, text)

  def test_versioned_auxiliary_framework_folder_requires_explicit_migration_to_fixed_source(self):
      text = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
      self.assertIn(SEPARATION_PARAGRAPH, text)
  ~~~
- [ ] **Step 2: Run RED.** Run `python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_workspace.py'`. Expected RED: operational documents do not yet contain the complete separation lifecycle and corrected legacy-to-fixed migration direction.
- [ ] **Step 3: Implement the minimum behavior.** Update only the listed operational documents and tests. Insert the exact `SEPARATION_PARAGRAPH` text shown in Step 1. State publication → read-only compatibility evaluation → explicit Project decision → separately authorized mutation. List `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, `MODULE_ROUTE_UNRESOLVED`, and derived `NAVIGATION_REPOSITORY_MISMATCH`. State project-local extensions/configuration remain local and P0-4 is interface-only.
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
- `PLAN-RESULT-EVIDENCE-API-001` → CLOSED
- `PREVIOUSLY_CLOSED_FINDINGS` → ALL REMAIN CLOSED: `PLAN-API-SEAM-001`, `PLAN-WORK-UNIT-ROLE-001`, `PLAN-REGISTRY-SCOPE-001`, `PLAN-PROJECTION-SCOPE-001`, `PLAN-MIGRATION-DIRECTION-001`, and `PLAN-EVIDENCE-SCOPE-001`

### Structure and consistency checks

- Required writing-plans header appears at the document start.
- Tasks 1–7 contain seven checkbox steps with actual test names, RED command/expected reason, implementation behavior, GREEN command, regression command, contract checks, and exact commit scope.
- Tasks 1–7 each contain concrete Python, JSON, or Markdown snippets with fixtures, assertions, decisive production branches, exact RED/GREEN commands, and exact task commit paths.
- Task 8 contains checkbox steps for full suite, all validators, projection counts, diff/status/scope checks, Result Envelope evidence, and no commit/evidence file.
- The placeholder scan returns zero matches.
- Every Task path agrees with the File Map; every NO CHANGE surface remains excluded from implementation modifications.
- No task changes an existing API signature unless the task explicitly lists that API as MODIFY; frozen navigation, Resume, Registry routing, and projection scripts have no planned production diff.
- Migration direction is versioned auxiliary Framework folder → fixed unversioned Framework source folder, with `EXPLICIT_MIGRATION` only for legacy projects.
- No tracked evidence file and no verification-only commit are permitted.

## Required Return Fields

The implementation result after executing this Plan must report:

`RESULT`, `WORK_UNIT`, `ARTIFACT_STAGE`, `FIX_ROUND`, `EXECUTION_SLOT_ID`, `ACCEPTED_DESIGN_SHA`, `PREVIOUS_REVIEWED_SHA`, `HEAD_SHA`, `ANCESTRY_VERIFICATION`, `PLAN_WRITING_PLANS_001_STATUS`, `PLAN_RESULT_EVIDENCE_API_001_STATUS`, `RESULT_ENVELOPE_SEAM`, `EVIDENCE_BINDING_SEAM`, `EVIDENCE_FAILURE_CLASSIFICATION`, `WRITING_PLANS_CONFORMANCE`, `CONCRETE_SNIPPET_REVIEW`, `TASK_1_SNIPPET_RESULT`, `TASK_2_SNIPPET_RESULT`, `TASK_3_SNIPPET_RESULT`, `TASK_4_SNIPPET_RESULT`, `TASK_5_SNIPPET_RESULT`, `TASK_6_SNIPPET_RESULT`, `TASK_7_SNIPPET_RESULT`, `PREVIOUSLY_CLOSED_FINDINGS_STATUS`, `TASK_COUNT`, `GATE_A_AFTER_TASK`, `GATE_B_AFTER_TASK`, `GATE_A_READINESS`, `GATE_B_READINESS`, `FILE_MAP_RESULT`, `API_CONTRACT_RESULT`, `TEST_COVERAGE_RESULT`, `PLACEHOLDER_SCAN_RESULT`, `SELF_REVIEW_RESULT`, `PROJECTION_STAGE_DEVIATION`, `FILES_CHANGED`, `WORKTREE_STATUS`, `PUSH_STATUS`, `REMOTE_HEAD_SHA`, `REMOTE_VERIFICATION`, `DEVIATIONS`, `BLOCKERS`, and `NEXT_GPT_ACTION`.
