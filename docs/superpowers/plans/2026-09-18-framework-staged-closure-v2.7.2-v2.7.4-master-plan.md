# Framework staged closure v2.7.2–v2.7.4 Master Execution Plan

> **For governed executors:** this is a Plan candidate; it is not yet accepted and is not execution authority. Before any implementation task, use the current Framework's normal Work Unit, Instruction, PRE_EXECUTION review, Result/Evidence, and POST_EXECUTION review contracts. A task may be started only when its observed prerequisites and its release gate are true.

**Goal:** deliver three independently reviewed and remotely activated releases: Group A execution reliability in 2.7.2, the unchanged accepted Contract Repair Tasks 5–9 in 2.7.3, and a bounded evidence-to-improvement review loop in 2.7.4.

**Architecture:** retain the v2.7.1 Kernel, State, Work Unit, Instruction/Result, review, Resume/Handoff, Git continuity, release/publication, Harvest, and telemetry/feedback owners. Group A adds only minimum, responsibility-local reliability bindings; Group B is a release wrapper around immutable Contract Repair semantics; Group C connects existing bounded observations to non-authorizing management review. No task creates a parallel lifecycle, authority system, database, service, queue, module, State machine, Resume type, or automatic evolution path.

**Current authority:** released Framework `2.7.1`; active base `6600a55ace1faf160309c82a1e5e2663c22d3dc6`; accepted staged-closure Design commit `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546`, Design blob `2bf4e96b1a6c030d844dd6f0734b017e78e81b00`, and accepted Design SHA-256 `8821a913f38d80a1081d235c07cd47b19ea4a75a8cc56818e62ca5b65c979b6e`.

**Authoritative references:** `AGENTS.md`; `.gpt-codex/KERNEL.md`; `VERSION`; `.gpt-codex/CONTROL.json`; `.gpt-codex/STATE.json`; `.gpt-codex/CHANGELOG.md`; the active Work Unit; current Result/Evidence; release records; the accepted Design above; and, by immutable Git object, the corrected accepted Contract Repair Design `135f1c06b205894f0e603b0fdbf34cc10ba6e3f6:docs/superpowers/specs/2026-09-17-framework-contract-repair-design.md` (blob `905be2ba58da02ae41900526ee7db4d397c081db`) and corrected accepted Plan `7f9c0cf46aee2b6bfdbadc36eb8d6373592d4a55:docs/superpowers/plans/2026-09-17-framework-contract-repair.md` (blob `7c775f12b2c8fcf102afb2f9c2c64c4634071958`). A mutable branch/ref is discovery only; it never substitutes for these objects.

## Global constraints and invariants

- `GROUP_A_RELEASE = 2.7.2`; `GROUP_B_RELEASE = 2.7.3`; `GROUP_C_RELEASE = 2.7.4`. A+B and B+C combined releases are forbidden.
- Group B starts only after fresh tool-observed `2.7.2 REMOTE_ACTIVE`; Group C starts only after fresh tool-observed `2.7.3 REMOTE_ACTIVE`.
- `TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO`; `FUTURE_BRIDGE_005_LIFECYCLE_PRESERVED = YES`; `PLUGIN_WORK_RESUMED = NO`; `BRIDGE_005_CREATED_BY_PLAN = NO`; `IMPLEMENTATION_AUTHORIZED_BY_PLAN_CANDIDATE = NO`.
- The one lifecycle is: `CURRENT AUTHORITY / STATE -> EXISTING CAPABILITY CHECK -> minimum delta -> authorized mutation -> PRE_EXECUTION review -> execution -> POST_EXECUTION review`. A plan/review/Result/Handoff finding is evidence, not mutation authority.
- The Kernel's State values, revision binding, evidence source restrictions, and `RECONCILIATION_REQUIRED` remain authoritative. Task-local outcome labels are derived observations, never new State values.
- Existing `continuity_resume.py`, `git_continuity.py`, `result_return.py`, Result/Handoff, Evidence, publication contract, release package/record, and State finalization remain the sole continuity and publication routes. Handoff is a derived view, never an authority source.
- Existing `execution_telemetry.py` and `framework_feedback.py` remain observation-only/non-authorizing. Harvest remains a separate evidence-based reusable-extension route.
- No candidate, package, local commit, tag, test pass, chat message, or reviewer visibility alone is `REMOTE_ACTIVE`.
- No historical Design, Plan, evidence, or release record is edited to make surfaces agree. Do not touch Plugin files, bridge-005, `dist/`, a release, `main`, or an implementation file while authoring/reviewing this Plan.

## Common task protocol

Every execution task below uses this protocol in addition to its stated details.

1. The executor reads current `CONTROL`, `STATE`, active Work Unit, current release facts, relevant immutable Design/Plan ref, latest Result/Evidence, and relevant Git/remote facts. It records the base identity and observed State revision before mutation.
2. It maps the requirement to the named existing owner. If the owner, exact interface, or exact changed path has legitimately drifted after a prior release, it records a mechanical binding only after proving unchanged behavior, authority, acceptance, security boundary, and evidence contract. It does not invent a path.
3. It derives the minimum exact scope in a current Work Unit/Instruction, checks capabilities, and obtains an independently produced passing PRE_EXECUTION review. `CODEX_IMPLEMENTER` and `CODEX_REVIEWER` remain separate contexts.
4. It follows RED→GREEN in focused tests, retains bounded/redacted execution evidence, validates the actual changed-path scope, and produces a Result/Handoff through existing contracts. A failing or stale condition stops at the existing blocked/reconciliation route.
5. An independent POST_EXECUTION review precedes any next mutation/release gate. A finding follows the existing `REVIEW_FINDING -> GPT/User decision -> FIX_INSTRUCTION -> re-review` lifecycle; it does not self-authorize a repair.

**Shared interruption rule:** an interruption records no inferred progress. A fresh session uses current repository facts to derive `NOT_STARTED`, `PARTIAL`, `READY_TO_CONTINUE`, `ALREADY_COMPLETE`, `FAILED`, or `RECONCILIATION_REQUIRED`, then follows the next authorized action. Valid identity, scope, base, State revision, and durable evidence are required for continuation. Ambiguous, destructive, remote, or approval side effects fail closed. The task's completion evidence and next gate below are the recovery inputs; no new Resume artifact is created.

---

# PART I — Authority, provenance, recovery, and sequencing

## I.1 Durable Plan/Design reachability before Group A

Before A0 implementation, the current integration/publication authority must make both the accepted Design and accepted Master Plan durably resolvable by immutable repository commit/path/blob references. The accepted Design content is not edited; its SHA-256 must remain `8821a913f38d80a1081d235c07cd47b19ea4a75a8cc56818e62ca5b65c979b6e`. This uses existing reviewed integration/Git-continuity/publication facts, not an acceptance database. Until both refs are durable, A0 is analysis-only.

## I.2 Release fact model

| Fact | Existing source and required meaning |
| --- | --- |
| `CANDIDATE` | Candidate Result/Evidence and local Git identity; not publication authority. |
| `LOCALLY_VERIFIED` | Local tests/validators and independent review bound to the exact candidate. |
| `PUBLISHED` | Existing publication authority plus independently observed remote publication facts. |
| `REMOTE_ACTIVE` | Observed remote branch/tag/release/version/SHA facts are bound to the exact reviewed candidate, then existing State/continuity finalization records them. |

Packaging is source version, canonical artifact, manifest/record, artifact integrity, and local validation. Publication/activation is the remote identity of the exact reviewed candidate. The finalization mechanism must record observations rather than synthesizing or rewriting historical evidence.

## I.3 Cold recovery record derivation

A fresh executor derives only this view from `AGENTS.md -> repository identity -> VERSION/release -> CONTROL -> STATE -> active Work Unit -> immutable Design/Plan refs -> latest Result/Evidence -> Git/GitHub facts`:

`PROJECT_IDENTITY`, `ACTIVE_FRAMEWORK_VERSION`, `ACTIVE_FRAMEWORK_SHA`, `CURRENT_GROUP`, `CURRENT_TARGET_RELEASE`, `CURRENT_WORK_UNIT`, `LAST_COMPLETED_TASK`, `LATEST_REVIEW_STATE`, `BLOCKERS`, `NEXT_AUTHORIZED_ACTION`, `DESIGN_REF`, and `PLAN_REF`.

Each field must carry its durable source. Missing, stale, conflicting, or multiply authoritative facts return `RECONCILIATION_REQUIRED`; chat memory, an editable note, and a local-only artifact cannot fill a missing fact.

## I.4 Amendment rule

Only mechanical rebinding after fresh observation is permitted when behavior, authority, acceptance, security boundary, and evidence contract are unchanged. Stop as `AMENDMENT_REQUIRED` before mutation for semantic/authority changes, any schema or module requirement, expanded scope, irreversible operation, Tasks 5–9 reinterpretation, or a release-boundary change. The unresolved Group A Result/Evidence/Handoff schema-fit question is specifically an amendment trigger, not authority to add a field.

---

# PART II — Group A: v2.7.2 Stabilization / Execution Reliability

## A0 — Fresh baseline and capability mapping

- **Goal:** establish a v2.7.1 remote-active, reproducible baseline and map every Group A requirement to an existing owner before any mutation.
- **Observed prerequisite:** immutable accepted Design/Plan refs are durable; fresh remote identity confirms `2.7.1 REMOTE_ACTIVE`; repository ID/default branch, active SHA, State revision, Work Unit, release record, and latest Result/Evidence agree.
- **Reuse and scope:** reuse `CONTROL`, `STATE`, Registry/project-map routing, `git_continuity.py`, release records, and current test owners. Read current runtime/script/test ownership; derive a bounded owned-path list only after this observation. Forbidden: any mutation, release, Plugin work, bridge-005, or speculative owner/module.
- **Executor / verification:** `CODEX_IMPLEMENTER` performs read-only mapping; `CODEX_REVIEWER` independently checks the mapping and exact pre-execution scope. Verify repository/release identity with local Git plus remote observation, inspect PowerShell/Python/Git/auth capability, and map Design sections 9–11 and 19–22 to actual current owners/tests.
- **Completion / recovery / next gate:** evidence is a dated capability-and-owner map, observed command identities/versions, exact base/remote facts, and a proposed minimal scope. Capability/identity conflict is `RECONCILIATION_REQUIRED`; missing capability is `BLOCKED`; no mutation has occurred. Next gate: authorized A1–A7 Work Unit/Instruction and PRE_EXECUTION review.

## A1 — Runtime environment contract and capability discovery

- **Goal:** add a minimum preflight projection that selects only observed supported PowerShell, Python, Git, encoding/path, authentication, and executable capabilities before mutation.
- **Observed prerequisite:** A0 mapping identifies current execution callers and test owners; a valid Group A Work Unit and passing PRE_EXECUTION review bind the exact implementation scope.
- **Reuse and scope:** reuse current command/execution callers and `git_continuity.py`; extend their existing preflight/result boundary only. The executor binds exact file/test paths after A0, likely current execution/continuity and focused test owners, but must not assume a fixed `pwsh` path or `gh`. Forbidden: generic environment manager, implicit fallback, credential capture, unbounded probing, or publication-channel selection.
- **Executor / verification:** `CODEX_IMPLEMENTER`; tests inject supported PowerShell 7, incompatible shell, supported/absent Python and Git, Unicode/Chinese path/encoding cases, tool-present and tool-absent paths, and authentication/capability unavailable paths. Each unavailable required capability fails before a mutation sentinel; discovery records selected executable/version and reason.
- **Completion / recovery / next gate:** bounded/redacted result includes command identity, selected capability, unsupported/blocked reason, and proof of zero mutation before denial. A stale capability observation is re-observed; an unavailable required capability is `BLOCKED`; ambiguous executable/auth facts are `RECONCILIATION_REQUIRED`. Next: A2/A3 can consume the preflight result.

## A2 — Deterministic Git and EOL execution facts

- **Goal:** make relevant validation/rehearsal Git facts canonical and independent of incidental user `core.autocrlf` while preserving user configuration.
- **Observed prerequisite:** A0 identifies current Git/release validation callers; A1 has demonstrated the supported Git/runtime path.
- **Reuse and scope:** reuse existing Git continuity/release validation and repository-local text handling. Bind only the minimal relevant implementation/config/test paths after observation. Forbidden: global Git configuration rewrite, wholesale line-ending rewrite, unobserved normalization rule, or changes outside the Group A Work Unit.
- **Executor / verification:** run isolated repositories/worktrees with contrasting `core.autocrlf` settings and a Chinese/Unicode path. Prove equivalent canonical inputs produce the same relevant changed-path/rehearsal facts; prove an intentionally noncanonical fixture is rejected or explicitly classified. Confirm user global settings are unchanged.
- **Completion / recovery / next gate:** evidence records repository-local/rehearsal configuration, observed settings, canonical outputs, and Unicode fixture results. An inability to establish equivalent facts is `FAILED`/`RECONCILIATION_REQUIRED`, never a silent setting override. Next: A3 and A8 consume canonical Git facts.

## A3 — Subprocess diagnostic contract

- **Goal:** ensure relevant existing command results retain bounded command identity, exit code, stdout, and stderr under existing redaction/evidence rules.
- **Observed prerequisite:** A0 identifies the actual subprocess owner(s); A1 identifies supported invocation and redaction boundary.
- **Reuse and scope:** extend the current command/execution result owner; reuse Result/Evidence bounds. Exact locations are bound after observation. Forbidden: execution-log database, raw full tool trace, secret retention, alternative logging system, or changing command semantics solely for diagnostics.
- **Executor / verification:** focused unit/integration tests cover success, non-zero exit, thrown launch error, bounded truncation, redaction, Unicode output, and preservation of both output streams. Assert the failure Result is sufficient to diagnose without exposing excluded data.
- **Completion / recovery / next gate:** completion evidence contains redacted bounded samples and test outputs. Missing diagnostics after a failure is `FAILED`; a redaction/bounds conflict is `RECONCILIATION_REQUIRED`. Next: A4/A8 use these result facts.

## A4 — Resumability and idempotency projection

- **Goal:** derive `NOT_STARTED`, `PARTIAL`, `READY_TO_CONTINUE`, `ALREADY_COMPLETE`, `FAILED`, and where appropriate `RECONCILIATION_REQUIRED` from existing durable facts without changing Kernel State semantics.
- **Observed prerequisite:** A0 maps State/Work Unit/Result/Evidence/Resume owners; A1–A3 provide observed preflight and command facts.
- **Reuse and scope:** reuse `continuity_resume.py`, State revision rules, immutable Work Unit refs, Result/Evidence, Handoff, and Git continuity. Bind only existing derivation/test surfaces after observation. Forbidden: new State value, workflow engine, separate Resume record, automatic retry, continuation across invalid authority, or treating a local inference as completion.
- **Executor / verification:** regression fixtures prove no durable start, valid partial, safe matching postcondition, command failure, stale State/base/scope, and ambiguous/destructive side effect. A continuation must require still-valid authority and refreshed PRE_EXECUTION review where current lifecycle requires it; a safe completed operation re-observes as `ALREADY_COMPLETE` without replay.
- **Completion / recovery / next gate:** evidence names each source fact and derived outcome. Ambiguity is fail-closed `RECONCILIATION_REQUIRED`; failed command is `FAILED`; capability loss is `BLOCKED`. Next: A5/A6/A8 consume the projection only as a derived view.

## A5 — Release, State, and metadata finalization consistency

- **Goal:** close the observed mismatch class among `VERSION`, package/release metadata, CONTROL/STATE, publication facts, and remote-active facts by the smallest existing-owner finalization mechanism.
- **Observed prerequisite:** A0 has mapped current release/publication records; A4 establishes durable status derivation; the executor has a current exact candidate identity for test fixtures.
- **Reuse and scope:** reuse `release_framework.py`, `publication_contract.py`, `git_continuity.py`, release records, Result/Evidence, and State finalization. First map every required fact to existing Result/Evidence/Handoff fields. Forbidden: historical rewrite, new release ledger, claim from package to activation, or schema expansion without amendment.
- **Executor / verification:** focused tests distinguish package/candidate, locally verified, published, and remote active; inject mismatched VERSION/record/manifest/State/remote SHA cases. Verify only independently observed remote identity can support `REMOTE_ACTIVE`. Validate compatibility/consumer projection for any reused metadata representation.
- **Schema decision:** if existing Result/Evidence/Handoff can express all fact bindings, use them. If a necessary fact cannot be represented compatibly, stop this task as `AMENDMENT_REQUIRED` with the field, owner, consumer-projection impact, and migration facts; do not add a schema field.
- **Completion / recovery / next gate:** evidence is a source-to-fact matrix and passing mismatch matrix. Conflicting remote/release facts reconcile; no historic record changes. Next: A9 release finalization uses this mapping.

## A6 — Machine-readable review and handoff transport

- **Goal:** make review-required artifacts available through a bounded existing machine route so `USER_IS_NOT_ARTIFACT_TRANSPORT_LAYER` is a regression invariant.
- **Observed prerequisite:** A0 maps current Result, compact return, Handoff, Resume, Git continuity, reviewer boundaries, and size/redaction rules; the actual Design-cycle inaccessible-local-artifact failure is recorded as a regression case.
- **Reuse and scope:** reuse `result_return.py`, Result Envelope/Handoff, immutable Git refs, and current remote continuity where separately authorized. Bind the smallest existing return/validation/test paths after observation. Forbidden: file-sharing subsystem, document DB, conversation store, local-path-only review dependency, silent main push, or user upload/copy as normal transport.
- **Executor / verification:** prove a complete bounded artifact is included in governed return data when it fits; otherwise prove an authorized immutable review ref resolves remote content. Test inaccessible local artifact, missing/ref-mismatch artifact, oversized bounded route behavior, redaction, and reviewer consuming the machine transport. The transport is presentation/evidence only, not approval or publication authority.
- **Completion / recovery / next gate:** evidence includes the complete transported test artifact or immutable resolver tuple and reviewer-access result. Inaccessible local-only content fails closed and asks the existing authority route to provide a bounded machine representation; it never shifts transport to the user. Next: A8/A9 and future Plan review use this invariant.

## A7 — Manifest-based destructive filesystem safety

- **Goal:** apply existing operational safety primitives to any authorized cleanup-like operation: exact target, allowed root, canonical containment, reparse/symlink/junction handling, action classification, and KEEP/DELETE evidence.
- **Observed prerequisite:** A0 identifies existing filesystem operation owner and current safety checks; a specific authorized operational action supplies a finite manifest.
- **Reuse and scope:** reuse current command/filesystem safety utilities and Work Unit scope. Bind exact implementation/tests only after the owner is observed. Forbidden: disk-cleanup governance authority, glob/broad root deletion, bypassing canonical containment, following reparse points, or treating an inferred target as authorized.
- **Executor / verification:** fixtures cover exact in-root DELETE, KEEP, outside root, `..`, absolute/drive paths, symlink/junction/reparse traversal, missing target, duplicate target, and manifest/action mismatch. Prove no filesystem mutation occurs in every rejected case.
- **Completion / recovery / next gate:** retained evidence contains manifest digest, allowed root, canonical target classification, and action decision. Interrupted/destructive ambiguity is `RECONCILIATION_REQUIRED`; safe observed postcondition can be `ALREADY_COMPLETE`. Next: A8 validates the end-to-end boundary.

## A8 — Group A clean-room Windows E2E

- **Goal:** demonstrate Group A's bounded reliability closure in a real clean-room Windows environment without claiming Contract Repair Tasks 5–9 closure.
- **Observed prerequisite:** A1–A7 focused work is independently reviewed and current candidate facts remain bound to its Work Unit/State/base.
- **Reuse and scope:** reuse existing clean-room/harness, release, continuity, Result/Evidence, and consumer-projection validation routes. Exact harness/fixture paths are discovered from current ownership; no production framework scope expands merely for test convenience. Forbidden: bridge-005, Plugin task, live destructive cleanup, and assertion that B is complete.
- **Executor / verification:** evidence matrix covers PowerShell 7 supported; unsupported shell before mutation; Python/Git present and absent; Chinese/Unicode repository/path; divergent user EOL settings; tool present/absent; interrupted run; valid resumed run; `ALREADY_COMPLETE`; subprocess diagnostics; inaccessible-local artifact machine handoff; release-state finalization; and remote-active distinct from packaging. Each case records command/result/evidence classification, redaction, and whether a mutation sentinel was reached.
- **Completion / recovery / next gate:** completion is a bounded clean-room evidence bundle with all required rows passed or explicitly stopped through existing reconciliation. Environment instability is not masked; it returns `BLOCKED`/`FAILED` with retained diagnostics. Next: A9.

## A9 — v2.7.2 final verification, review, and release

- **Goal:** produce and activate exactly v2.7.2 after Group A's bounded closure.
- **Observed prerequisite:** A0–A8 completion evidence, exact reviewed candidate, valid current authority/State/Work Unit, and no unresolved amendment/reconciliation.
- **Reuse and scope:** existing full Framework tests, project and consumer projection validators, release packaging, independent review, publication contract, Git continuity, and State finalization. Exact release files are derived by the current release owner from `VERSION`; no paths are invented now. Forbidden: B/C work, combined release, historical rewrite, self-review, remote activation claim before observation.
- **Executor / verification:** run focused Group A suites, full Framework suite, project validation, consumer projection/runtime validation, release validation, `git diff --check`, actual authorized-path verification, and clean-room evidence review. An independent CODEX post-review checks exact candidate identity; a finding goes to GPT adjudication and current fix lifecycle. USER_APPROVER accepts that exact reviewed candidate. Existing governed publication then obtains tool-observed remote branch/tag/release/version/SHA equality and finalizes State/continuity.
- **Completion / recovery / next gate:** evidence binds tests, validators, review, acceptance, package, publication, and remote observation to the exact SHA. Only then write/derive `2.7.2 REMOTE_ACTIVE`; otherwise remain at the last durable fact. Next: B0, and only after fresh re-observation.

---

# PART III — Group B: v2.7.3 inherited Contract Repair Tasks 5–9

## B0 — Re-observe v2.7.2 and prepare future migration authority

- **Goal:** after v2.7.2 activation, rebind only mechanics necessary to execute immutable Contract Repair Tasks 5–9.
- **Observed prerequisite:** tool-observed, State-finalized `2.7.2 REMOTE_ACTIVE`; the exact active SHA/ref/release and current CONTROL/STATE/native authority agree.
- **Reuse and scope:** read the immutable historical Design/Plan refs listed in this Plan, current `validate_project.py`, schemas, role communication, Git continuity, and test ownership. Compare historical semantic requirements with actual post-A interfaces. Forbidden: rewriting Tasks 5–9, creating/preparing/approving bridge-005, using bridge-004, Plugin work, or treating a plan as migration authority.
- **Executor / verification:** produce a mechanical interface/path remap table with old immutable requirement, current owner, unchanged semantic proof, and proposed exact future scope. Review each row independently. Any difference in authority, semantics, security, evidence, or acceptance is `AMENDMENT_REQUIRED`.
- **Completion / recovery / next gate:** evidence includes current v2.7.2 remote facts and remap table. Future bridge-005, if necessary, is separately prepared from fresh facts, exact-scoped, independently PRE_EXECUTION reviewed, exact-payload USER_APPROVER approved, remotely verified, non-self-authorized, and single-purpose; this Plan neither creates nor authorizes it. Next: only a separately authorized B1–B5 Work Unit.

## B1 — Inherited Task 5: external approval-evidence locator verification

- **Goal:** execute historical Task 5 exactly: validate immutable external approval evidence locator content and remote reachability.
- **Observed prerequisite:** B0 semantic identity proof and separate current execution authority.
- **Reuse and scope:** historical Task 5 technical source is immutable Design section 12 and historical Plan Task 5; use current locator/result/schema/Git continuity owners after B0 remap. Preserve `evidence_commit_sha + path + blob_sha`; mutable ref head remains discovery/reachability only. Forbidden: locator semantic redesign, local-only approval substitution, mutable-head authority, or transport by implementer.
- **Executor / verification:** use historical focused RED→GREEN and negative locator tests: missing object/path, wrong blob, malformed result, non-approval, non-reachable commit, and ref advance that cannot replace the tuple. Verify the exact tuple resolves remotely and remains byte/content-addressed.
- **Completion / recovery / next gate:** Result includes immutable locator tuple and test matrix. Missing/mismatched/remote-unreachable tuple fails closed; no retry uses a substituted ref. Next: B2 after independent review.

## B2 — Inherited Task 6: actual Git mutation scope oracle

- **Goal:** execute historical Task 6 exactly: enforce actual Git paths as scope authority before commit/push.
- **Observed prerequisite:** B0 mapping and B1 only where composed flow needs locator; separate authority remains valid.
- **Reuse and scope:** historical Design section 11/Plan Task 6 and current `validate_project.py` governed mutation composition. Preserve normalized union of `git diff --name-only -z`, `git diff --cached --name-only -z`, `git ls-files --others --exclude-standard -z`, plus committed candidate path set before `PUSH`. Forbidden: caller declarations/evidence `files_changed` as authority, diff-only approximation, scope expansion, or skipped untracked/staged checks.
- **Executor / verification:** isolated repositories inject outside-scope tracked unstaged, tracked staged, untracked, committed-candidate, malformed, Unicode, and in-scope cases. Require rejection before COMMIT/PUSH for every actual-path escape and pass after exact restoration.
- **Completion / recovery / next gate:** evidence preserves command outputs/path sets and exact rejection reasons. A repository/path ambiguity is reconciliation, not a permissive subset decision. Next: B3.

## B3 — Inherited Task 7: native control-plane authority composition

- **Goal:** execute the historical Task 7 native control-plane route without changing its authority core.
- **Observed prerequisite:** B0 semantic identity, B1 locator, B2 oracle, valid independent authorization Work Unit, exact State/base/review facts, and separately authorized execution.
- **Reuse and scope:** historical Design sections 9–13/Plan Task 7 plus current Instruction/Result schemas, role communication, `validate_project.py`, immutable Work Unit resolution, review lifecycle, and Git continuity. Preserve immutable authorization Work Unit; project/repository identity; State revision; exact scope; PRE_EXECUTION review/freshness; immutable external approval locator; anti-self-authorization; one governed entry; fail closed.
- **Required correlation:** preserve `APPROVAL_REQUEST.in_response_to_instruction_id = RECONCILIATION_REQUEST.instruction_id`; `APPROVAL_RESULT.response_to_instruction_id = APPROVAL_REQUEST.instruction_id`; and `APPROVAL_RESULT.approved_instruction.instruction_id = RECONCILIATION_REQUEST.instruction_id`. Compare the complete approved authority core exactly with actual request: identity, revision, base SHA, normalized scope, issuer/executor roles, action, and immutable target Work Unit. The locator is not an approved-core field.
- **Executor / verification:** production-shaped composed fixtures independently fault each correlation, State/base/review freshness, Work Unit independence, scope, locator, role, approval decision, and actual Git path. Each fault rejects and exact restored chain passes.
- **Completion / recovery / next gate:** evidence includes closed authority-core identity, locator tuple, review/result chain, State revision, and actual-path proof. Any stale/mismatched fact is `RECONCILIATION_REQUIRED`; no actor can repair authority within the same request. Next: B4.

## B4 — Inherited Task 8: first native seed materialization and bounded consumption

- **Goal:** execute the historical closed seed semantics exactly once and only within its accepted use.
- **Observed prerequisite:** B3 native gate is proven and a separately accepted seed/bridge lifecycle exists from fresh facts.
- **Reuse and scope:** historical Design section 14/Plan Task 8 and current Work Unit/State/result owners. Bind exact seed artifact, exact allowed paths, and revision constraints only from the immutable historical authority plus fresh accepted migration authority. Forbidden: general bootstrap authority, seed reuse, seed self-ownership, path substitution, or this Plan creating bridge-005.
- **Executor / verification:** retain historical missing/replaced/fifth/self-owned path, revision-reuse, and result-path-swap sensitivity cases. Prove exact closed seed passes once and each broadened/replayed fixture fails.
- **Completion / recovery /next gate:** evidence binds immutable seed ref, exact path list, State revision, consumption Result, and remote facts where current authority requires. Interrupted/uncertain consumption is reconciliation; it is never replayed speculatively. Next: B5.

## B5 — Inherited Task 9: production-shaped composed lifecycle proof

- **Goal:** prove the accepted composed FIX and control-plane lifecycles, not isolated test doubles.
- **Observed prerequisite:** B1–B4 independently pass and current B authority remains valid.
- **Reuse and scope:** historical Design section 16/Plan Task 9 and the current schemas/builders/role validation/review/governed-entry/validator suites after B0 remap. Preserve FIX flow `schema -> builder -> role/instruction validation -> review lifecycle -> governed entry`; preserve control-plane flow `instruction schema -> immutable scope -> PRE_EXECUTION review -> locator -> APPROVAL_RESULT -> authority gate -> actual-Git scope`. Forbidden: in-memory shortcut as proof, omitted production interface, semantic reinterpretation, or release activation.
- **Executor / verification:** run valid chains and one-fault-at-a-time negative/sensitivity cases for every required binding, then exact restoration. A composed failure may add only a missing call proven necessary by current behavior; broader redesign is amendment-required.
- **Completion / recovery / next gate:** evidence has fixture identities, command output, fault matrix, and restored pass chain. Failure carries exact failing boundary; no partial composition is marked complete. Next: B6.

## B6 — v2.7.3 clean-room composed verification

- **Goal:** prove Tasks 5–9 under current v2.7.2-derived facts and prove legacy migration authority is not normal post-native authority.
- **Observed prerequisite:** B1–B5 reviewed candidate and current v2.7.2-derived identity/State facts.
- **Reuse and scope:** existing clean-room/harness/Git continuity/test routes and immutable historical semantics. Exact fixtures are bound after fresh observation. Forbidden: bridge reuse, normal legacy authority, Plugin work, or acceptance based only on isolated units.
- **Executor / verification:** clean-room valid composed flow plus absent/malformed locator, changed mutable ref, stale State/base/review, scope escape, non-approve, self-authority, seed replay, and post-native legacy bridge use. Require production-shaped success and fail-closed negatives.
- **Completion / recovery / next gate:** bounded evidence matrix distinguishes current native authority from historical migration evidence. Any inability to establish current native closure remains blocked/reconciliation. Next: B7.

## B7 — v2.7.3 final verification, review, and release

- **Goal:** publish and activate exactly v2.7.3 after unchanged Contract Repair closure.
- **Observed prerequisite:** B0–B6 evidence and exact candidate pass; no amendment/reconciliation; independent review and exact candidate identity are available.
- **Reuse and scope:** same existing full suite, validators, consumer projection, review, publication, remote verification, and State finalization as A9. Exact release surface derives from current release owner. Forbidden: Group C work, combined release, bridge reuse, historical semantic changes, or self-publication.
- **Executor / verification:** full suite, project/framework/consumer validators, composed Task 5–9 proof, `git diff --check`, actual-path verification, independent POST_EXECUTION review, GPT adjudication for a finding, exact candidate USER acceptance, governed publication, and tool-observed remote-active equality/state finalization.
- **Completion / recovery / next gate:** only exact verified remote evidence creates `2.7.3 REMOTE_ACTIVE`. Any failed acceptance/publication remains a non-active durable state. Next: C0 after fresh observation.

---

# PART IV — Group C: v2.7.4 optimization closed loop

## C0 — Current capability remap

- **Goal:** after v2.7.3 activation, confirm minimum missing connections rather than assume pre-A/B file locations.
- **Observed prerequisite:** tool-observed, State-finalized `2.7.3 REMOTE_ACTIVE` and current repository identity.
- **Reuse and scope:** inspect `execution_telemetry.py`, `framework_feedback.py`, Result/Evidence, Harness process/feedback records, Harvest, Framework-management workflow, Registry, and tests. Derive current responsibility/path mapping. Forbidden: mutation, new module, telemetry database, or automatic learning.
- **Executor / verification:** read-only map identifies source facts, bounds/redaction, existing ProcessReview/FrameworkFeedback interfaces, persistence owner, management review route, and Harvest boundary. Independent review rejects any invented owner.
- **Completion / recovery / next gate:** durable mapping and minimum-delta hypothesis; capability conflict is amendment/reconciliation. Next: authorized C1–C7 Work Unit and PRE_EXECUTION review.

## C1 — Durable bounded iteration/process evidence

- **Goal:** persist valid observable process evidence through existing Evidence/Harness responsibility.
- **Observed prerequisite:** C0 proves a compatible current persistence owner and schema representation.
- **Reuse and scope:** reuse existing Evidence/Harness/Result boundaries, telemetry normalization/provenance/redaction/idempotency helpers. Bind paths after C0. Forbidden: private reasoning, chat transcript, raw full tool trace, new telemetry database, unbounded content, or authority fields.
- **Executor / verification:** valid records carry provenance, source project/work unit/revision where applicable, evidence refs, bounded content, redaction, and idempotency. Tests reject missing provenance, private-reasoning-like fields, oversized/raw trace data, invalid reference, duplicate, and unauthorized fields.
- **Completion / recovery / next gate:** Result reports content bounds and source evidence refs. Incomplete evidence is bounded uncertainty/excluded, never filled by inference. Schema incompatibility is amendment-required. Next: C2/C3.

## C2 — Production ProcessReview derivation

- **Goal:** connect current counters/observations to a real production `ProcessReview` derivation path.
- **Observed prerequisite:** C1 valid persisted records and C0-confirmed `framework_feedback.py` owner.
- **Reuse and scope:** reuse `ProcessReview`, `build_process_review`, current strategy/process record validators, and Result/Evidence links. Forbidden: competing ProcessReview subsystem, automatic action, opaque derived authority, or unbounded aggregation.
- **Executor / verification:** valid complete input creates bounded review; incomplete evidence is marked/excluded; duplicate/idempotent input does not double count; success/preservation evidence and failure/friction evidence both remain visible. Test provenance and result-ref preservation.
- **Completion / recovery / next gate:** evidence binds review to input record IDs/refs and derivation version/current strategy. Missing/inconsistent inputs do not fabricate totals; they remain incomplete/reconciliation per existing owner. Next: C3.

## C3 — Production FrameworkFeedback derivation

- **Goal:** normalize process evidence into non-authorizing FrameworkFeedback for observed gap, friction, workaround, orchestration/recovery failure, release/sync failure, validator false positive, capability-reuse success, and preservation evidence.
- **Observed prerequisite:** C2 production ProcessReview and existing feedback validation/evolution boundary remain current.
- **Reuse and scope:** reuse `FrameworkFeedback`, validation, and `framework_feedback_authorizes_mutation` boundary. Bind only compatible existing owners after observation. Forbidden: feedback authorization, automatic fix/release, new policy engine, or generic recommendation store.
- **Executor / verification:** test each valid evidence class, malformed/missing provenance, duplicate, and feedback attempting authority fields. Require normalization links to ProcessReview/Evidence and prove feedback cannot pass as mutation authority.
- **Completion / recovery / next gate:** completion Result contains feedback IDs, source refs, validation output, and explicit non-authorizing status. Invalid feedback is retained only as bounded invalid/retracted evidence when current policy allows. Next: C4/C5.

## C4 — Improvement Candidate representation

- **Goal:** represent the minimum evidence-linked decision-support candidate for Framework-management review.
- **Observed prerequisite:** C3 valid feedback and C0 proof that existing responsibility can represent the contract.
- **Reuse and scope:** reuse existing Evidence/Result/feedback/management-review representation where possible. A candidate may contain identity, source refs, subject/problem class, recurrence/current relevance, existing capability/reuse facts, preservation constraints, management question/status. Forbidden: mutation permission, approved scope, release status, Work Unit substitute, automatic selection, or new Framework module.
- **Executor / verification:** test valid candidates, missing source evidence, authority-shaped fields, invalid bounded content, duplicate identity, and consumer/management boundary. `NEW_FRAMEWORK_MODULE_REQUIRED = NO`; if no existing compatible owner can represent the minimum contract, stop amendment-required with proof.
- **Completion / recovery / next gate:** candidate links are immutable/validated evidence refs and explicit non-authority proof. Next: C5.

## C5 — Recurrence, current relevance, and resolution classification

- **Goal:** deterministically group evidence into single current, repeated current, already resolved, superseded, invalidated/retracted, and preservation evidence without scoring.
- **Observed prerequisite:** C1–C4 bounded source/feedback/candidate identities are valid.
- **Reuse and scope:** reuse telemetry subject/correlation/order helpers and existing feedback owner after C0 remap. Forbidden: opaque numeric scoring/ranking engine, model-only recurrence inference, or treating age alone as resolution.
- **Executor / verification:** fixtures cover one current observation, repeated matching evidence, stale/superseded source, explicit resolution by current framework evidence, retraction/invalidity, preservation success, duplicate/idempotent input, and conflicting correlation. Require deterministic grouping and source refs for each classification.
- **Completion / recovery / next gate:** evidence includes grouping inputs/rules/output and no-change result. Conflict/missing current authority is uncertainty or reconciliation, never a high-priority assertion. Next: C6/C7.

## C6 — Harvest boundary

- **Goal:** preserve the distinction between Framework/process feedback and a reusable project-extension Harvest candidate.
- **Observed prerequisite:** C3–C5 feedback/candidates and current Harvest contract have been re-observed.
- **Reuse and scope:** use existing Harvest admission/evidence routes only when evidence supports reusable extension generalization. Forbidden: automatic feedback-to-Harvest conversion, Built-in promotion, Framework mutation, or conflating defect report with reusable capability.
- **Executor / verification:** test feedback with no reuse semantics remains outside Harvest; qualifying repeated project-extension evidence may reference existing Harvest procedure but still obtains its normal authorization; candidate alone cannot promote anything. Include preservation evidence and rejected/no-change cases.
- **Completion / recovery / next gate:** Result identifies whether a Harvest relationship exists and why, with source refs. Ambiguous generalization remains feedback only. Next: C7.

## C7 — Framework-management review input

- **Goal:** emit decision-ready non-authorizing input: `Evidence -> ProcessReview -> FrameworkFeedback -> Improvement Candidate -> Framework-management review -> USER decision`.
- **Observed prerequisite:** C1–C6 valid bounded chain and C0 maps current GPT/User management route.
- **Reuse and scope:** reuse existing Result/Handoff/management review and normal Framework evolution lifecycle. Forbidden: user decision synthesis, automatic Work Unit/Design/Plan creation, mutation, release, Plugin work, or bypassing capability-before-Design.
- **Executor / verification:** produce complete bounded review input containing evidence/candidate refs, classification, existing capability/reuse, preservation constraints, management question, and explicit `NO_DECISION/NO_MUTATION` default. Test a rejection and no-change result. A selected improvement must still enter existing `capability-before-Design -> Design -> Plan -> Work Unit -> review -> implementation -> verification -> release`.
- **Completion / recovery / next gate:** evidence proves a review consumer can inspect machine-provided content without local-file/user transport and that no output authorizes mutation. Next: C8.

## C8 — Closed-loop clean-room proof

- **Goal:** demonstrate one production-shaped closed evidence-to-review loop and separately prove candidate non-authority.
- **Observed prerequisite:** C1–C7 reviewed candidate and current v2.7.3-derived facts.
- **Reuse and scope:** reuse existing harness/process evidence, feedback, Result/Evidence, management input, and clean-room test routes. Exact fixtures are bound after current observation. Forbidden: automatic learning/action, raw traces, user artifact transport, or a candidate mutation fixture that actually mutates framework state.
- **Executor / verification:** clean-room flow proves `real execution/process evidence -> ProcessReview -> Feedback -> candidate -> management review input`; cases include duplicate evidence, stale evidence, resolved evidence, preservation evidence, rejected candidate, and no-change. A separate negative proves candidate alone cannot produce an Instruction, Work Unit, scope, mutation, publication, or release.
- **Completion / recovery / next gate:** bounded evidence matrix and independent review of non-authority proof. Any absent source remains incomplete, not inferred. Next: C9.

## C9 — v2.7.4 final verification, review, and release

- **Goal:** publish and activate exactly v2.7.4 with the minimum closed-loop connection.
- **Observed prerequisite:** C0–C8 complete/reviewed evidence, exact candidate, no amendment/reconciliation, and valid current authority.
- **Reuse and scope:** existing suites/validators/consumer projection/release/publication/State finalization. Exact release paths derive from current release owner. Forbidden: automatic optimization authority, Group B replay, Plugin work, combined release, or remote-active claim before observation.
- **Executor / verification:** full suite, validators, clean-room loop E2E, actual-path/diff checks, independent POST_EXECUTION review, GPT adjudication of any finding, exact candidate USER acceptance, governed publication, tool-observed remote identity verification, and State/continuity finalization.
- **Completion / recovery / next gate:** only matching exact remote facts create `2.7.4 REMOTE_ACTIVE`. The resulting loop continues to generate review input only; a future change still needs normal capability/design/plan/work-unit authority.

---

# PART V — Per-release verification, review, acceptance, and activation

For 2.7.2, 2.7.3, and 2.7.4 independently, apply this release gate after that Group's final task:

1. Re-observe repository identity, current remote base, State revision, Work Unit, exact candidate SHA, authorized exact paths, and immutable Design/Plan refs.
2. Run the Group's focused suites and clean-room proof; then full Framework tests, `validate_framework.py`, `validate_project.py .`, current consumer projection/runtime validation, release validation, and `git diff --check`. Record commands, exit status, test counts, bounded outputs, and artifact facts.
3. Use the actual-Git scope check where applicable; compare all candidate changes to authorized exact scope. Any untracked/staged/committed escape blocks commit/push under existing authority.
4. Independent `CODEX_REVIEWER` reviews the exact candidate, not a moving branch. A finding takes the existing GPT adjudication/FIX/re-review route. The author does not self-review.
5. `USER_APPROVER` accepts the exact reviewed candidate. Plan acceptance is distinct from execution PRE_EXECUTION and POST_EXECUTION review; user acceptance does not retroactively authorize a different SHA.
6. Existing publication authority publishes only the accepted candidate. Remote verification independently binds branch/tag/release/version/SHA to the reviewed candidate; package bytes alone cannot do so.
7. Existing State/continuity finalization records tool-observed remote facts. Only then may the next Group's A/B/C release gate open.

Failure at any step preserves the last durable state and returns the existing blocked/reconciliation Result. It never advances a group on a local candidate, a package, a review-only artifact, or chat assertion.

---

# PART VI — Cold recovery, interruption continuation, and amendments

## VI.1 Per-task continuation algorithm

For every task A0–C9: read the Part I cold recovery inputs; verify current release gate; locate the current Work Unit and Result/Evidence by immutable reference; re-observe State/base/repository/remote/capabilities; compare actual postcondition and exact scope. Return `NOT_STARTED` only with no durable start; `PARTIAL`/`READY_TO_CONTINUE` only with valid authority and compatible partial evidence; `ALREADY_COMPLETE` only with matching safe postcondition and evidence; `FAILED` for retained command/test failure; `BLOCKED` for unavailable capability; and `RECONCILIATION_REQUIRED` for identity/revision/scope/base/release/approval/side-effect conflict. The next authorized action is the task-specific next gate in Parts II–IV.

## VI.2 Review transport and fresh windows

All review-required artifacts use bounded complete governed return content or a separately authorized immutable remote resolver tuple. Reviewers must never need author-local disk access; the user is not the normal artifact transport layer. A new chat/window is merely a new reader of durable facts and does not create a task, approval, Work Unit, review pass, or execution authority.

## VI.3 Explicit amendment boundary

An executor stops and returns `AMENDMENT_REQUIRED` with observed evidence before any mutation if a mechanical remap would alter semantics/authority/security/evidence; if Group A needs an additive schema; if Group C needs a new module; if a task expands scope/irreversibility; if historical Task 5–9 semantics need reinterpretation; or if a group/release boundary changes. The amendment follows the existing capability-before-Design and Design/Plan review/acceptance lifecycle, then becomes a new immutable reference; it does not overwrite this Plan or accepted Design.

---

# PART VII — Plan self-review and acceptance criteria

## VII.1 Design coverage matrix

| Accepted Design sections | Master Plan responsibility |
| --- | --- |
| 1–8 | Part I global authority/provenance/invariants and A0 |
| 9–11, 19–22 | A1–A9 and Part V |
| 12–14 | B0–B7 with immutable historical references |
| 15–17 | C0–C8 and Harvest boundary |
| 18, 23–25 | Parts I, V, and VI |
| 26–29 | global invariants, B0, C6–C9, and amendment rule |
| 30 | this Part VII and independent Plan review |

## VII.2 Candidate self-review checklist

- Every accepted Design section maps to a Plan responsibility above; Group A is bounded reliability only and does not claim Tasks 5–9 closure.
- Existing State, Work Unit, Instruction/Result, review, Resume/Handoff, Git continuity, release/publication, Harvest, telemetry, and feedback behavior are referenced as existing authority rather than redefined.
- Group B references immutable accepted Contract Repair Design/Plan and preserves Task 5–9 semantics exactly; bridge-004 is not reusable, and bridge-005 remains future/separate.
- The three Design-review concerns remain closed: authority precedence is explicit, user artifact transport is prohibited as normal flow, and cold recovery is repository-only.
- No task starts Plugin work, creates a new module/State/Resume/review lifecycle/authority system, adds automatic optimization authority, or silently authorizes schema expansion.
- The document contains no unresolved placeholder; future exact paths are expressly derived by required fresh observation rather than invented.
- Before review, run `git diff --check` and compare the candidate against `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546`; the sole changed path must be this Master Plan artifact.

## VII.3 Plan acceptance lifecycle and effect

`PLAN_AUTHOR -> independent CODEX_REVIEWER -> GPT_REVIEWER -> USER_APPROVER -> immutable accepted Plan ref` is required. The reviewer receives the complete Plan via the bounded machine return (or immutable authorized ref), not a request for the user to upload/copy it. Acceptance makes the Plan durably reviewable; it does **not** implement any Group, create bridge-005, resume Plugin work, publish a release, or authorize mutation. Group A still requires a current normal Work Unit and PRE_EXECUTION review under the then-active Framework.
