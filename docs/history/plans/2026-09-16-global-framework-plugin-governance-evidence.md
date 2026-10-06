# Global Framework Plugin and Governance Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved governance hardening, global GPT–Codex Framework Plugin, evidence feedback bridge, distribution/manual, and self-hosting acceptance without adding a second governance system.

**Architecture:** The active released Framework remains authoritative. CAP-01 and CAP-02 harden existing Result/Evidence and review lifecycle contracts first; the external Plugin then provides entry/resume/routing, followed by evidence feedback and GitHub PR transport. Project state remains project-owned, and Plugin/Framework candidates cannot self-authorize.

**Tech Stack:** Python 3 standard library, JSON/JSON Schema, Git/GitHub, existing Framework validators/tests, OpenAI plugin manifest/marketplace formats supported at implementation time.

**Spec:** docs/superpowers/specs/2026-09-16-global-framework-plugin-governance-evidence-design.md

**Accepted Design Authority:** `ACCEPTED_DESIGN_REPOSITORY = xqc2098948451-byte/gpt-codex-framework`; `ACCEPTED_DESIGN_PATH = docs/superpowers/specs/2026-09-16-global-framework-plugin-governance-evidence-design.md`; `ACCEPTED_DESIGN_SHA = 7bdf0ff17d058100f832d7a2321ddc4276586e04`. Implementation argues from this exact SHA, not latest branch contents; later review-branch movement does not move Design authority.

## Global Constraints

```text
Framework module count = 7; Plugin is NOT an eighth Framework module.
Plugin routes. Framework governs. Project owns state. No authority -> no mutation.
Current released Framework governs successors; candidate Framework/Plugin cannot self-authorize.
INITIAL_PLUGIN_BOOTSTRAP = active released Framework + approved Design + approved Plan + existing lifecycle. No Plugin 0.
Plugin is not an unavoidable product hook; repository-native Framework is final fail-closed authority.
No database, second STATE, Work Unit system, review lifecycle, registry, context server, private reasoning archive, automatic learning/optimization, opaque score, or mandatory MCP.
Work Unit continuity != runtime-turn continuity. BLOCKED requires proven blocker. INCOMPLETE is incomplete evidence.
Every governed terminal event requires feedback CHECK; CHECK != evidence creation; intake != optimization approval; completion != feedback sync.
Plugin update != Framework adoption != Project migration.
Reviewable Design/Plan candidates are committed and pushed to the bound GitHub repository before formal GPT review. REMOTE_REVIEW_CANDIDATE != ACCEPTED_AUTHORITY; push makes reviewable, not accepted. GPT binds repository + artifact path + exact SHA; acceptance freezes only after GPT pass plus user approval. Remote failure is REMOTE_ARTIFACT_SYNC = SYNC_PENDING and ARTIFACT_REVIEW_READY = NO unless separately proven BLOCKED. User upload is exceptional recovery, never normal handoff; no second sync/state system.
```

## Remote artifact review continuity

Future persistence results return `REMOTE_REPOSITORY`, `REMOTE_BRANCH`,
`REMOTE_SHA`, `ARTIFACT_PATH`, `REMOTE_VERIFICATION`, and
`ARTIFACT_REVIEW_READY`; amendments also return prior/current candidate SHA.
Accepted references use `ACCEPTED_ARTIFACT_REPOSITORY`,
`ACCEPTED_ARTIFACT_PATH`, and `ACCEPTED_ARTIFACT_SHA` through existing artifact
refs, not an approval database. Normal Design and Plan loop is draft -> local
validation -> commit -> non-force push -> remote verification -> coordinates ->
GPT exact SHA/path review -> amend/re-push -> user approval -> exact-SHA freeze.

Before Task 5, re-check official OpenAI Plugin Management documentation.
Marketplace/release source must use approved immutable Plugin release/tag/commit.

## Planned File/Responsibility Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `.gpt-codex/scripts/publication_contract.py` | completion authority |
| Modify | `.gpt-codex/scripts/validate_project.py` | result/review composition |
| Modify | `.gpt-codex/schemas/result-envelope.schema.json` | bounded completion shape |
| Modify | `.gpt-codex/scripts/framework_feedback.py` | feedback candidate/sanitization/dedupe |
| Modify | `.gpt-codex/schemas/evidence.schema.json` | evidence-compatible package |
| Modify | `.gpt-codex/scripts/continuity_resume.py` | durable resume derivation |
| Modify | `.gpt-codex/scripts/git_continuity.py` | evidence branch/PR facts |
| Modify | `.gpt-codex/scripts/release_framework.py` | immutable Plugin release binding |
| Create | `.gpt-codex/scripts/framework_plugin_entry.py` | repository helper for Codex/local validation |
| Create | `plugins/gpt-codex-framework/` | verified Plugin package skills/resources only |
| Create | `plugins/gpt-codex-framework/.codex-plugin/plugin.json` | the sole native manifest |
| Create | `.agents/plugins/marketplace.json` | supported marketplace descriptor |
| Create | `docs/GPT_CODEX_FRAMEWORK_PLUGIN_USER_MANUAL.zh-CN.md` | Chinese manual |
| Test | `.gpt-codex/tests/test_result_contract_schema.py` | CAP-01 |
| Test | `.gpt-codex/tests/test_review_lifecycle.py` | CAP-02 |
| Create/Test | `.gpt-codex/tests/test_framework_plugin.py` | Plugin core |
| Create/Test | `.gpt-codex/tests/test_github_evidence_bridge.py` | bridge |
| Test | `.gpt-codex/tests/test_framework_feedback.py`, `test_release_packaging.py` | evidence/release |

Reuse existing Result/Evidence, Instruction Envelope, `validate_review_lifecycle`,
`framework_feedback`, Harvest, `load_continuity_resume`, Git continuity, and
release/projection. Only the thin adapter and bridge fixture lack present
owners; neither stores authority or state.

### Task 1: CAP-01 Completion Evidence Hardening

**Files:** Modify `publication_contract.py`, `validate_project.py`,
`result-envelope.schema.json`; test `test_result_contract_schema.py` and
`test_navigation_project_validation.py`; document none.

**Interfaces**
- Consumes: `validate_result_authority(result: Mapping[str, Any], verified_evidence_refs: set[str] | None = None) -> list[str]` and `validate_result_protocol(result)`.
- Produces: `validate_completion_evidence(result: Mapping[str, Any]) -> list[str]`, composed by `validate_result_protocol`.

The Result Envelope gains status `INCOMPLETE` without weakening existing
`PASS`, `FAIL`, `BLOCKED`, `PARTIAL`, or `LOCAL_COMPLETE`. Its frozen
`completion_evidence.execution_state` is exactly `COMPLETED | INCOMPLETE |
BLOCKED`; it has `process_completed: bool`, `exit_code: int | null`,
`intended_scope: list[str]`, `executed_scope: list[str]`,
`test_files_expected: int | null`, `test_files_executed: int | null`,
`test_count: int | null`, `failure_count: int | null`, `error_count: int | null`,
`validators_expected: list[str]`, `validators_completed: list[str]`, and
`blocker_evidence_refs: list[str]`. Validator lists are unique, bounded,
stable identifiers/commands. PASS requires COMPLETED, process true, exit 0,
exact scope, known required test coverage/count, zero failures/errors, and
completed validators exactly satisfying expected validators; both lists are []
when none are required. INCOMPLETE has missing facts; BLOCKED has BLOCKED state
and nonempty blocker refs. Existing remote/publication PASS rules remain.
CAP-01 tests use a completed Result with `remote_verification=VERIFIED` so a
RED result proves completion behavior, not existing publication requirements.

- [ ] Write failing tests `test_completion_evidence_denies_timeout_unknown_exit_partial_scope_and_unknown_count`, `test_completion_evidence_denies_known_failures_or_errors`, and `test_proven_blocker_is_blocked_not_pass`; cover complete exit-0 scope, timeout, unknown exit, partial files, unknown count, failures/errors, blocker, and continuing window.
- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py"`; expect missing completion-evidence validation.
- [ ] Add minimal schema/validator: PASS needs COMPLETED, known exit, equal declared/executed scope, known counts, zero failures/errors, and validators complete; all incomplete cases become INCOMPLETE; BLOCKED needs nonempty blocker refs.
- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py"`; expect GREEN.
- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p "test_navigation_project_validation.py"` as adjacent regression.
- [ ] Run `python .gpt-codex/scripts/validate_project.py .`.
- [ ] Run `git diff --check`.
- [ ] Obtain independent post-execution review.
- [ ] Commit `feat: harden completion evidence`.

### Task 2: CAP-02 Authority-Bounded Review / Adjudication

**Files:** Modify `validate_project.py`, and `instruction_envelope.py` only if existing Fix metadata requires extension; test `test_review_lifecycle.py` and `test_instruction_envelope.py`; document none.

**Interfaces**
- Consumes: `validate_review_lifecycle(...)`, `validate_review_result(result)`, `build_instruction_envelope(...)`.
- Produces: `validate_remediation_adjudication(decision_evidence: Mapping[str, Any], finding_result: Mapping[str, Any], resolved_basis: Mapping[str, Mapping[str, Any]]) -> list[str]`, called before a Fix Instruction is accepted.

The durable carrier is existing Evidence, referenced by
`FIX_INSTRUCTION.remediation_decision_ref`. Evidence uses
`subject = REMEDIATION_ADJUDICATION` and carries `finding_ids: list[str]`,
`decision: ACCEPT | REJECT | MODIFY`, `basis_type:
ACCEPTED_AUTHORITY_BASIS | CONCRETE_REGRESSION_EVIDENCE`, `basis_refs:
list[str]`, and `adjudicated_at_revision: int`. The existing Evidence schema
is changed only if its current `additionalProperties` validation cannot carry
these fields. The frozen validator is
the validator declared above; repository recovery resolves
the referenced durable Evidence before allowing a Fix.

- [ ] Write failing cases for Design/Plan/Work Unit basis, test/validator/contract regression basis, preference/refactor/unapproved criterion denial, REJECT denial, and valid MODIFY.
- [ ] Run `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`; expect unsupported finding-to-fix authorization.
- [ ] Require `ACCEPTED_AUTHORITY_BASIS` or `CONCRETE_REGRESSION_EVIDENCE` and bind ACCEPT/MODIFY to the new Fix Instruction; do not add a lifecycle.
- [ ] Add RED cases: missing durable ref, wrong finding ref, and REJECT deny; only ACCEPT/MODIFY with valid basis allow FIX.
- [ ] Assert `self.assertIn("REMEDIATION_BASIS_UNRESOLVED", validate_remediation_adjudication(decision, finding, {}))`; arbitrary, unrelated, stale/unaccepted authority, and non-failing regression refs DENY; resolved accepted authority and resolved failure evidence ALLOW.
- [ ] **RUN_EXACT_RED_COMMAND:** `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`.
- [ ] **CONFIRM_EXPECTED_RED_REASON:** missing durable basis resolution returns `REMEDIATION_BASIS_UNRESOLVED`.
- [ ] **IMPLEMENT_MINIMAL_PRODUCED_INTERFACE:** add only the frozen three-argument adjudication validator and repository ref resolution.
- [ ] **RUN_EXACT_GREEN_COMMAND:** rerun `python -m unittest discover -s .gpt-codex/tests -p "test_review_lifecycle.py"`.
- [ ] **RUN_EXACT_ADJACENT_REGRESSION:** `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py"`.
- [ ] **RUN_APPLICABLE_VALIDATORS:** `python .gpt-codex/scripts/validate_project.py .`.
- [ ] **RUN_GIT_DIFF_CHECK:** `git diff --check`.
- [ ] **OBTAIN_INDEPENDENT_POST_EXECUTION_REVIEW:** review durable finding/basis/ref correlation.
- [ ] **CREATE_FOCUSED_COMMIT:** `feat: bind remediation to authority evidence`.

### Phase-A Gate

Tasks 1–2 require independent review and integration with `CAP01 = CLOSED` and
`CAP02 = CLOSED`. An unresolved CRITICAL/IMPORTANT finding stops execution
before any Plugin activation work.

### Task 3: Global Plugin Core

**Precondition:** Re-check current official OpenAI Plugin Management format
before mutation. If it differs from this package boundary, stop for
reconciliation.

**Files:** Create `.gpt-codex/scripts/framework_plugin_entry.py`; create
`plugins/gpt-codex-framework/.codex-plugin/plugin.json` and only the supported
skills/resources beneath that root; modify `git_continuity.py` (derive/validate
remote artifact review Git facts), `continuity_resume.py`, `validate_project.py`; create `test_framework_plugin.py`; test
`test_continuity_resume.py`; document none.

**Interfaces**
- Consumes: `load_continuity_resume`, `build_project_handoff`, `validate_governed_mutation_entry`, Git facts.
- Produces: repository helper `plugin_entry_report(root: Path, role: str) -> dict[str, Any]` and `plugin_resume_report(root: Path, role: str) -> dict[str, str]`; Plugin skills read/interpret accessible durable authority but never assume ChatGPT executes local Python.

- [ ] **PLUGIN_FORMAT_PREFLIGHT:** re-check official format; material difference is STOP_FOR_RECONCILIATION.
- [ ] **WRITE_BASE_PLUGIN_RED_TESTS:** add enrolled/unmanaged/conflict/fresh-resume fixture assertions in `test_framework_plugin.py`.
- [ ] **WRITE_REMOTE_REVIEW_RED_TESTS:** add all bound/mismatch/missing/local/outage/moving-branch/frozen-ref/fresh-resume cases.
- [ ] **RUN_EXACT_RED_COMMAND:** `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin.py"`.
- [ ] **CONFIRM_EXPECTED_RED_REASON:** helper/package skill and remote fact derivation are absent.
- [ ] **IMPLEMENT_PLUGIN_ENTRY_AND_RESUME:** create helper/package separately; ChatGPT does not execute helper.
- [ ] **IMPLEMENT_REMOTE_REVIEW_COORDINATES:** use `git_continuity.py` and existing facts; candidate is not authority.
- [ ] **RUN_EXACT_GREEN_COMMAND:** rerun `test_framework_plugin.py`.
- [ ] **RUN_EXACT_ADJACENT_REGRESSION:** `python -m unittest discover -s .gpt-codex/tests -p "test_continuity_resume.py"`.
- [ ] **RUN_APPLICABLE_VALIDATORS:** `python .gpt-codex/scripts/validate_project.py .`.
- [ ] **RUN_GIT_DIFF_CHECK:** `git diff --check`.
- [ ] **OBTAIN_INDEPENDENT_POST_EXECUTION_REVIEW:** inspect surface split and fail-closed fallback.
- [ ] **CREATE_FOCUSED_COMMIT:** `feat: add governed plugin entry adapter`.

### Task 4: Framework Evidence Feedback + GitHub Evidence Bridge

**Files:** Modify `framework_feedback.py`, `evidence.schema.json`, `git_continuity.py`, `plugins/gpt-codex-framework/` routing resource, and `test_framework_feedback.py`; create `test_github_evidence_bridge.py`; document none.

**Interfaces**
- Consumes: `validate_framework_feedback`, terminal Work Unit result, Evidence refs, and Git remote facts.
- Produces: `build_framework_feedback_candidate(...) -> Mapping[str, Any]`, `sanitize_feedback_export(candidate) -> Mapping[str, Any] | None`, and `EvidencePublicationDecision(status: str, evidence_id: str, target_repository: str, target_branch: str, target_path: str, sync_status: str, requires_write_handoff: bool, reason: str)` as a frozen dataclass in `framework_feedback.py`.

Evidence branch is `framework-evidence/<source-project-id>/<evidence-id>` and
target path is `.gpt-codex/harvest/inbox/<project-id>/<evidence-id>.json` unless
current Harvest authority proves a different path. `framework_feedback.py` owns
candidate/sanitization/identity; `git_continuity.py` validates Git/GitHub facts;
Plugin routing hands write work to Codex; only Codex or an authorized
write-capable GitHub action creates branch, writes normalized evidence, pushes,
and creates PR under existing Instruction/Result authority.

`safe_project_id` and `evidence_id` reject `..`, `/`, `\\`, absolute paths,
and invalid Git-ref sequences before the Framework adds separators. Task 4 has
separate RED/GREEN assertions for safe branch derivation, safe target path,
duplicate identity, existing open branch/PR, unavailable GitHub -> SYNC_PENDING,
and direct consumer-main write -> DENY. ChatGPT produces a governed existing-
Instruction write handoff; Codex verifies handoff/branch/path/duplicates, writes
one normalized package, pushes the branch, opens PR, and returns Result/Evidence refs.

- [ ] Write failing cases for every terminal event, NONE, INCOMPLETE continuation, secret/private input denial, deterministic duplicate identity, unavailable transport/SYNC_PENDING, no main write, accepted-evidence-only intake, correction/retraction, and aging classifications.
- [ ] Run `test_framework_feedback.py` and `test_github_evidence_bridge.py`; expect missing candidate/bridge functions.
- [ ] Implement normalized project-owned feedback; sanitize before export; reuse Harvest/PR facts; route read-only ChatGPT to prepare/validate and Codex/authorized writer to branch/PR; intake never approves Framework change.
- [ ] Before PR creation check merged evidence, open evidence PR/branch, and duplicate `evidence_id`; consumer Projects never push Framework main.
- [ ] **WRITE_EXACT_RED_TEST:** assert terminal CHECK, NONE, INCOMPLETE continuation, sanitization denial, deterministic ID, unsafe IDs, safe branch/path, merged/open duplicates, unavailable sync, main denial, intake boundary, correction, and aging in the two focused test files.
- [ ] **RUN_EXACT_RED_COMMAND:** `python -m unittest discover -s .gpt-codex/tests -p "test_github_evidence_bridge.py"`.
- [ ] **CONFIRM_EXPECTED_RED_REASON:** candidate/sanitization/decision helpers are absent.
- [ ] **IMPLEMENT_MINIMAL_PRODUCED_INTERFACE:** add only `build_framework_feedback_candidate`, `sanitize_feedback_export`, and frozen `EvidencePublicationDecision`.
- [ ] **RUN_EXACT_GREEN_COMMAND:** rerun `test_github_evidence_bridge.py` and `test_framework_feedback.py`.
- [ ] **RUN_EXACT_ADJACENT_REGRESSION:** `python -m unittest discover -s .gpt-codex/tests -p "test_git_continuity.py"`.
- [ ] **RUN_APPLICABLE_VALIDATORS:** `python .gpt-codex/scripts/validate_project.py .`.
- [ ] **RUN_GIT_DIFF_CHECK:** `git diff --check`.
- [ ] **OBTAIN_INDEPENDENT_POST_EXECUTION_REVIEW:** inspect safe handoff and no-main-write proof.
- [ ] **CREATE_FOCUSED_COMMIT:** `feat: add governed framework evidence bridge`.

### Task 5: Plugin Distribution + Chinese User Manual

**Files:** Modify the existing `plugins/gpt-codex-framework/.codex-plugin/plugin.json`; create `.agents/plugins/marketplace.json` and `docs/GPT_CODEX_FRAMEWORK_PLUGIN_USER_MANUAL.zh-CN.md`; modify `release_framework.py`; test `test_release_packaging.py` and `test_framework_plugin.py`.

**Interfaces**
- Consumes: Task 3 adapter and approved immutable Plugin release source.
- Produces: `validate_plugin_release_binding(source_ref: str) -> list[str]`.

- [ ] Re-check official Plugin Management documentation and record supported manifest fields in task Evidence before tests.
- [ ] Write failing tests for immutable source, import/install validation, ChatGPT/Codex paths, no mandatory MCP, and Chinese new-window plus Framework-development commands.
- [ ] Run `test_release_packaging.py` and `test_framework_plugin.py`; expect missing manifests/manual/binding.
- [ ] Implement supported fields only; bind marketplace source immutably; write Chinese manual for installation, permissions, bootstrap/enrollment, roles, results, feedback/PR, SYNC_PENDING, upgrades, self-hosting, and recovery.
- [ ] Re-run focused tests, consumer/framework validators, diff check, independent review, and commit `docs: package plugin and add Chinese manual`.
- [ ] **PLUGIN_DISTRIBUTION_PREFLIGHT:** re-check official marketplace format; material difference is STOP_FOR_RECONCILIATION.
- [ ] **WRITE_EXACT_RED_TEST:** assert one package root, no root manifest, immutable marketplace source, no MCP, and all three copyable manual commands.
- [ ] **RUN_EXACT_RED_COMMAND:** `python -m unittest discover -s .gpt-codex/tests -p "test_release_packaging.py"`.
- [ ] **CONFIRM_EXPECTED_RED_REASON:** manifest binding/manual are absent.
- [ ] **IMPLEMENT_MINIMAL_PRODUCED_INTERFACE:** update Task-3 manifest only, create marketplace descriptor and immutable release binding.
- [ ] **CREATE_CHINESE_MANUAL:** write required installation, recovery, ChatGPT, Codex, and self-hosting commands.
- [ ] **CREATE_REMOTE_REVIEW_MANUAL_FLOW:** explain GitHub review branch, GPT exact SHA/path review, amendment/re-push, candidate versus frozen authority, SYNC_PENDING, and a copyable Chinese workflow without normal file upload.
- [ ] **RUN_EXACT_GREEN_COMMAND:** rerun `test_release_packaging.py`.
- [ ] **RUN_EXACT_ADJACENT_REGRESSION:** `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin.py"`.
- [ ] **RUN_APPLICABLE_VALIDATORS:** `python .gpt-codex/scripts/validate_framework.py`.
- [ ] **RUN_GIT_DIFF_CHECK:** `git diff --check`.
- [ ] **OBTAIN_INDEPENDENT_POST_EXECUTION_REVIEW:** inspect immutable distribution binding.
- [ ] **CREATE_FOCUSED_COMMIT:** `docs: package plugin and add Chinese manual`.

### Task 6: End-to-End Self-Hosting Acceptance and Activation

**Files:** Modify `test_framework_plugin.py`, `test_release_packaging.py`, `test_review_lifecycle.py`; create `docs/superpowers/reviews/2026-09-16-global-framework-plugin-self-hosting-acceptance.md`; document existing Evidence/Result/Work Unit refs; create no database.

**Interfaces**
- Consumes: Tasks 1–5, `plugin_entry_report`, review lifecycle, release binding.
- Produces: existing Evidence/Result refs proving `PLUGIN_RELEASE_CANDIDATE = VERIFIED` and `SELF_HOSTING_ACCEPTANCE = PASS`.

- [ ] **ACCEPTANCE_WORK_UNIT_PREPARATION:** authorize the bounded acceptance Work Unit.
- [ ] **FRESH_CHATGPT_ENTRY_RESUME:** invoke Plugin Entry/Resume in a fresh window.
- [ ] **REPOSITORY_ONLY_RECOVERY_VERIFICATION:** prove no transcript is an authority input.
- [ ] **FRESH_CODEX_IMPLEMENTER_LAUNCH:** use the authorized worktree.
- [ ] **ACCEPTANCE_RECORD_ONLY_MUTATION:** update only the acceptance record.
- [ ] **COMMIT_ACCEPTANCE_TARGET:** commit its target SHA.
- [ ] **PUSH_ACCEPTANCE_REMOTE_REVIEW_CANDIDATE:** normal non-force push.
- [ ] **VERIFY_ACCEPTANCE_REMOTE_SHA:** bind repository, branch, SHA, path, and remote verification.
- [ ] **FRESH_CHATGPT_FETCH_EXACT_REMOTE_ARTIFACT:** no user file upload.
- [ ] **VERIFY_NO_USER_FILE_TRANSFER:** durable `USER_FILE_TRANSFER_REQUIRED = NO`.
- [ ] **FRESH_ISOLATED_REVIEWER_LAUNCH:** open independent reviewer worktree.
- [ ] **EXACT_TARGET_SHA_VERIFICATION:** reviewer verifies committed target SHA.
- [ ] **CAP01_COMPLETION_EVIDENCE:** record complete verification evidence.
- [ ] **CAP02_ADJUDICATION_IF_FINDING:** execute only if an actual finding exists.
- [ ] **MANDATORY_FEEDBACK_CHECK:** record NONE or normalized candidate.
- [ ] **NORMAL_INTEGRATION:** use existing review/integration authority.
- [ ] **FULL_VERIFICATION:** run full suite and all three validators.
- [ ] **PLUGIN_RELEASE_CANDIDATE_VERIFICATION:** verify immutable candidate source.
- [ ] **FINALIZE_DURABLE_ACCEPTANCE_EVIDENCE:** bind remote coordinates, GPT_FETCHED_EXACT_REMOTE_ARTIFACT=YES, user-transfer NO, and continuity PASS before closure.
- [ ] **CREATE_FOCUSED_ACCEPTANCE_COMMIT:** finalize durable Evidence/Result refs.
- [ ] **EXPLICIT_USER_ACTIVATION_GATE:** NOT AUTHORIZED BY PLAN EXECUTION ALONE.

## Review, Full Verification, and Design Coverage

### Mandatory execution checklist for Tasks 2–6

For each Task N (2 through 6), its listed failing cases are implemented as the
separate exact test code step, followed by separate checkboxes: (1) write that
test, (2) run its listed focused unittest command, (3) confirm the listed
missing-interface RED reason, (4) implement its exact `Produces` interface,
(5) rerun that focused command GREEN, (6) run the adjacent regression named in
the Task, (7) run `python .gpt-codex/scripts/validate_project.py .` plus the
Task-specific consumer/framework validator, (8) run `git diff --check`, (9)
obtain independent post-execution review, and (10) create the Task's listed
focused commit. Task 5 separately verifies one Plugin package root, marketplace
released-source binding, manual recovery commands, and no MCP dependency. Task
6 separately verifies Work Unit setup, fresh ChatGPT recovery, fresh Codex
Implementer, acceptance-record-only mutation, exact-SHA Reviewer, CAP-01,
conditional CAP-02 finding path, feedback CHECK, integration, release-candidate
verification, and the explicit activation gate.

Each task uses PRE-EXECUTION REVIEW -> implementation -> POST-EXECUTION REVIEW
-> GPT adjudication -> focused remediation -> focused re-review. A failed test
does not create a Work Unit; a Work Unit may span turns. Every task executes
the listed RED command, minimal GREEN change, adjacent regression, validator,
diff check, independent review, and focused commit.

```text
python -m unittest discover -s .gpt-codex/tests -p "test_*.py"
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
git diff --check
```

Final evidence records exact test count/files/exit/failure/error counts,
validator results, HEAD, and worktree cleanliness; partial output never proves
PASS.

| Design requirement | Task or constraint |
|---|---|
| CAP-01 / CAP-02 | Tasks 1 / 2 |
| Entry, resume, bootstrap, active authority, surface limit | Task 3 |
| Feedback, sanitization, dedupe, bridge, intake, aging/correction | Task 4 |
| Distribution and Chinese manual | Task 5 |
| Real self-hosting acceptance and activation | Task 6 |
| Seven modules, no duplicate system, approval boundary | Global Constraints |
| REMOTE_ARTIFACT_REVIEW_CONTINUITY | Global Constraints, Tasks 3, 5, and 6 |

`IMPLEMENTED`, `VALIDATED`, `INTEGRATED`, `RELEASED`, and `ACTIVATED` differ.
No active Plugin exists before V1 activation; development `main` cannot become
active governance by its existence.
