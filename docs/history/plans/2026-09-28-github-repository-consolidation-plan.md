# GitHub Repository Consolidation Plan — Rev002

STATUS = CANDIDATE_ONLY
EXECUTION_AUTHORIZED = NO

## 0. Baseline, method and stop rule

Target repository: xqc2098948451-byte/gpt-codex-framework. The 2026-09-28 fresh fetch and remote ref check resolve origin/main to b96e077362477ef697670ddc04f4e6c77c880271; STATE revision 18 is AUTHORIZED with reconciliation null and latest_synced_state_revision 18. The observed tree has 364 tracked files; remote refs contain 90 heads and 37 distinct tags (74 ls-remote tag lines including annotated-tag peeled refs); public GitHub has one open PR. Recheck these facts immediately before governed execution. Drift returns CONSOLIDATION_DESIGN_PLAN_REMOTE_DRIFT and stops.

No step below is authorized by this candidate. A future executor needs the existing Work Unit, exact Instruction/role/scope, applicable Guardrails and PRE_EXECUTION review. Record each phase's evidence and obtain its required independent review before moving to its successor. Do not use a dirty local checkout as the canonical source. Candidate paths are docs/superpowers/specs/2026-09-28-github-repository-consolidation-design.md and docs/superpowers/plans/2026-09-28-github-repository-consolidation-plan.md.

## Phase A — GitHub metadata classification and durable ref-cleanup ledger

1. Reobserve all remote heads and tags with git ls-remote, GitHub protection/branch metadata, open PRs, current Work Units, Instructions, Evidence, immutable refs and active review contexts. Bind each decision to exact PR/branch name, head SHA, observed remote state and current main. This subphase is non-destructive: do not close a PR or delete a branch while classification remains transient.
2. Reopen [PR #15](https://github.com/xqc2098948451-byte/gpt-codex-framework/pull/15), verify its draft status, old Group B coordination purpose, base/head, current discussion and absence of an active review dependency. Classify MERGE, CLOSE_SUPERSEDED, or KEEP_OPEN. Current candidate remains CLOSE_SUPERSEDED / DO_NOT_MERGE if the fresh evidence still agrees.
3. Use the branch ledger below. Initial fail-closed result is KEEP=1 (main), DELETE_SAFE=0, REVIEW_REQUIRED=89. For each REVIEW_REQUIRED entry, perform its legend's exact resolution test and promote to DELETE_SAFE only when every Design section 6 predicate is evidenced. `git merged` or ancestor-of-main is not sufficient by itself.
4. For every proposed DELETE_SAFE branch, enumerate current durable-authority commits referenced by Evidence, Work Units, Instructions, remote-review/bootstrap continuity or accepted immutable locators and prove each remains reachable from at least one retained remote ref after the proposed deletion: main, a retained tag, or another retained authority ref. Enforce `NO_REF_DELETION_MAY_CAUSE_A_CURRENT_DURABLE_AUTHORITY_COMMIT_TO_BECOME_UNREACHABLE_FROM_ALL_RETAINED_REMOTE_REFS`. If the proof fails or is unknown, decision = KEEP/REVIEW_REQUIRED. A separately governed archival authority tag/ref may establish retained reachability when justified; this Plan never deletes authority/release/bootstrap tags.
5. Materialize the exact classification and decision ledger at `.gpt-codex/evidence/GITHUB-REPOSITORY-CONSOLIDATION-REF-CLEANUP.json`. It must record repository/context and main SHA, each open PR decision, every branch name/head SHA, KEEP/DELETE_SAFE/REVIEW_REQUIRED decision, ancestor/protection/open-PR/active-work/authority-reference/remote-review/bootstrap predicates, retained-reachability evidence, decision reason, and review status. The ledger itself grants no deletion authority.
6. Independently review the exact ledger candidate. After PASS and normal governed integration, consume only its immutable `<commit>:<path>+blob` locator for the metadata action. Reobserve each PR/branch immediately before acting and require its identity/head SHA still matches the ledger. Then USER_LOCAL may close only PRs marked CLOSE_SUPERSEDED and delete only exact branches marked DELETE_SAFE, one by one, non-force. Any drift stops that action. Unresolved entries remain.
7. Record the resulting open-PR and remote-branch set. Branch/PR metadata mutation and source-tree mutation remain separate transactions.

Exit: exact ref-cleanup decisions are durable before destructive metadata action, all authority-class tags remain, no unreviewed deletion occurred, and every deleted branch satisfied retained-authority reachability.

## Phase B — Durable decisions and consumer projection

1. Create the single decision Evidence at .gpt-codex/evidence/POST-P2-PUBLIC-RELEASE-DEFERRAL.json under governed authority. Bind user decision, date, repository/context, and exact semantics: PUBLIC_RELEASE=DEFERRED_BY_USER, PRIVATE_PLUGIN_USE=CONTINUE, RESUME_PUBLIC_RELEASE_REQUIRES_NEW_USER_AUTHORIZATION. State explicitly that the Evidence is non-executable, opens no Work Unit and does not by itself mutate STATE.
2. Recompute manifest entries against the candidate Git tree. Current observed stale set is exactly the following 22 MANAGEMENT/LOCAL/GENERATED entries, none CONSUMER_REQUIRED:

    .superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/.gitignore
    dist/gpt-codex-framework-v2.2.1-bootstrap.zip
    dist/gpt-codex-framework-v2.2.1-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.2.1-release.json
    dist/gpt-codex-framework-v2.2.2-local.1-bootstrap.zip
    dist/gpt-codex-framework-v2.2.2-local.1-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.2.2-local.1-release.json
    dist/gpt-codex-framework-v2.4.0-bootstrap.zip
    dist/gpt-codex-framework-v2.4.0-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.4.0-release.json
    dist/gpt-codex-framework-v2.6.0-bootstrap.zip
    dist/gpt-codex-framework-v2.6.0-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.6.0-release.json
    dist/gpt-codex-framework-v2.7.0-bootstrap.zip
    dist/gpt-codex-framework-v2.7.0-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.7.0-release.json
    dist/gpt-codex-framework-v2.7.1-bootstrap.zip
    dist/gpt-codex-framework-v2.7.1-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.7.1-release.json
    dist/gpt-codex-framework-v2.7.3-bootstrap.zip
    dist/gpt-codex-framework-v2.7.3-bootstrap.zip.sha256
    dist/gpt-codex-framework-v2.7.3-release.json

3. For each entry, check release metadata and consumer contract. Remove it from explicit manifest paths only if absent and no longer required; prefix classification of future files remains intact. If a required file is actually missing, return FINDING and restore through separate authority instead of deleting its entry. Keep the manifest version at 2.7.4; this phase is no version bump.
4. Run validate_consumer_projection.py and inspect inventory and contamination, not just exit code. Expected after correction: unknown_paths=[], missing_required_paths=[], contamination=[], and no management file in the staged consumer projection.

## Phase C — Codex Directory Creation Contract

1. Specify optional directory_creations declarations in the existing Work Unit schema/validation: path, purpose, owner, content_type, authority_type, lifetime, consumer_visible, release_visible, cleanup_policy. Bind each declaration to Work Unit scope and an accepted Design/Architecture locator for any new top-level directory.
2. Extend validate_project.py candidate Git scope validation to enumerate tracked paths of BASE_GIT_TREE and CANDIDATE_GIT_TREE, derive every candidate-only directory prefix, and distinguish EXISTING_DIRECTORY_WRITE from NEW_DIRECTORY_CREATION. Reject undeclared, out-of-scope and generic-purpose directories with DIRECTORY_CREATION_DENIED; reject unauthorized top-level prefixes with STRUCTURE_CHANGE_REQUIRED. Check rename/add paths and existing prefix reuse. A broad parent selector does not authorize new descendants.
3. Extend validate_framework.py and existing projection/scope tests to enforce the declaration and repo-external ephemeral-output rule. Add tests for nested new directories under owned src/, allowed existing-directory writes, authorized declared nested/top-level paths, missing declaration fields, renamed paths, generic names and scratch/ZIP/cache output.
4. Update AGENTS.md and Bootstrap instructions to state the same operating contract and deterministic future worktree layout, without implementing local workspace moves now. Do not create a second manager, registry or STATE.

Exit: tests show an unauthorized new Git directory prefix fails closed even when no mkdir command appears. The following documentation normalization phase must itself use this newly enforced contract for every new docs/ prefix.

## Phase D — Documentation and history normalization

1. Build a current-tree reference inventory for every candidate source path using Git tree, repository text links, schema paths, release records and consumer manifest/tests. Identify any immutable commit:path or commit:path+blob references and preserve their historical meaning.
2. MOVE_SET, conditional on per-file reference and reconstruction proof: the six tracked .superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-{1,3,4,6,11,12}-report.md files to docs/history/reviews/2026-09-12-v2.3.0-project-map-context-resume/ with the same basenames. If any report's proof fails, place that file in KEEP_IN_PLACE_SET and record why; do not delete it.
3. KEEP_IN_PLACE_SET initially includes all .gpt-codex/evidence/, evidence/instructions/, evidence/results/, work-units/, durable schemas, releases/records/, and existing docs/superpowers/specs/, plans/ and reviews/ files pending individual reference checks. The existing docs/superpowers tree is a legacy history surface, not the current architecture entry point. DELETE_SET = empty for tracked documents.
4. Under the accepted Design declarations and the Phase C mechanical gate, add only the declared docs/architecture, docs/decisions, docs/plans and docs/history prefixes needed by this migration. Add a small current architecture index, human-readable decision/freeze pointers, and a current-plan pointer. `docs/decisions/` is documentation and authority pointers only; it must not become a second machine execution-authority store. Update all live current-tree links and tests touched by the six moves; retain immutable historical locators unchanged. Do not require bulk migration of the legacy spec/plan/review files. Do not create new .superpowers/sdd task reports.

Exit: live links resolve, no authority path break, the new directories were created only through the Phase C contract, and a maintainer can find active architecture and plans without reading historical plans.

## Phase E — Proven duplicate semantics

1. Add focused tests to test_release_archive.py and release packaging/version tests for strict current VERSION parsing, legacy archive acceptance if presently supported, prerelease order, invalid strings, artifact names and unchanged release metadata. Confirm the current observable behavior before refactor.
2. Make release_archive.py own the single pure Framework release-version parser/key policy; have release_framework.py import it and remove its independent SEMVER rule. `RELEASE_VERSION_POLICY` has exactly one primary owner. release_framework.py remains only RELEASE_BUILD_AND_PACKAGE; release_archive.py remains RELEASE_ARCHIVE_AND_RECORDS plus the shared pure version policy. No version service or new subsystem.
3. Compare each framework_plugin_entry.py baseline/resume branch and status/error shape. Consolidate only identical boilerplate into a private helper if regression tests prove P2 observable semantics unchanged. If not equivalent, classify it VALID_DEFENSIVE_VALIDATION or PRESENTATION_DUPLICATION, leave behavior intact, and issue a separate finding for any desired later change.
4. Run affected release, Plugin and result-handoff tests. Do not implement Foundation capabilities or expand Plugin surface.

## Phase F — Full validation and clean clone

Run validate_framework.py, validate_project.py, validate_consumer_projection.py, the full unittest suite and git diff --check on the reviewed candidate. In a clean clone at the exact candidate commit, repeat consumer staging, bootstrap/static structural checks, Plugin fallback sanity and release dry-run/package validation, with ephemeral output outside the repository. Inspect current-tree links, every preserved immutable authority locator, package inventory, missing/unknown projection paths, contamination and management-file exclusion. Recheck that every current durable-authority commit affected by ref cleanup remains reachable from retained remote refs. A failure returns FINDING; repair under the existing review lifecycle and repeat the affected gate plus full final suite.

## Phase G — Repository Structure Freeze

After all earlier phases pass, create exactly `.gpt-codex/evidence/GITHUB-REPOSITORY-STRUCTURE-FREEZE.json` through governed review. It must bind: repository/project/context identity; the exact integrated commit SHA and STATE revision; capability-responsibility-matrix digest; directory-creation-contract digest/version; canonical repository-tree digest; consumer-projection path/hash/version and zero-error inventory; immutable locator of `.gpt-codex/evidence/GITHUB-REPOSITORY-CONSOLIDATION-REF-CLEANUP.json`; remaining branch names and exact head SHAs; open PR count and decisions; authority-tag preservation status; validator/full-suite/git-diff/clean-clone results; immutable-path/reachability audit; PUBLIC_RELEASE=DEFERRED_BY_USER; PRIVATE_PLUGIN_USE=CONTINUE; and `next_gate = LOCAL_WORKSPACE_CONSOLIDATION`. Independently review and integrate this exact freeze artifact. The immutable locator of the integrated Freeze artifact becomes the only cross-context authority for the later Local Workspace Consolidation gate. Freeze does not itself authorize local cleanup.

## Branch review ledger at observed main

Each line is REVIEW_REQUIRED today. M means the head is an ancestor of main (56 lines): verify protection, active work, PR/review/bootstrap/authority references and historical supersession; only then consider promotion. U means the head is not an ancestor of main (26 lines): inspect main...head diff and sole-reachable authority content, then all M checks. E means an unmerged framework-evidence ref (5 lines): additionally verify durable evidence/review continuity and retention. P means an unmerged PR base/head (2 lines): keep through PR #15 decision and verify no remote-review dependency before reassessment. These codes give each named branch its specific reason and required decision method. The only KEEP branch is main; DELETE_SAFE remains empty until the checks complete.

    M | baseline-stabilization-bootstrap-001
    M | bootstrap/p2-finding-004-provenance-fix-001
    M | bootstrap/p2-finding-004-remediation-authority-001
    M | candidates/p2-plugin-public-release-preparation-001
    M | design/global-framework-plugin-governance-evidence
    M | governance/b7-publication-packaging-authority-design-correction
    M | governance/b7-publication-packaging-authority-plan-correction
    M | governance/b7-publication-packaging-work-unit-candidate-001
    M | governance/b7-release-authority-design
    M | governance/b7-release-authority-design-base-correction
    M | governance/b7-release-authority-plan-r3
    M | governance/b7-release-work-unit-candidate-001
    M | governance/b7-v2.7.3-publication-finalization-authority-design
    M | governance/b7-v2.7.3-publication-finalization-authority-plan
    M | governance/b7-v2.7.3-publication-finalization-candidate-001
    M | governance/b7-v2.7.3-publication-finalization-wu-candidate-001
    M | governance/group-c-c1-c7-work-unit-authority-design-amendment
    M | governance/group-c-c1-c7-work-unit-authority-plan-amendment
    M | governance/group-c-c8-implementation-candidate-001
    M | governance/group-c-c8-work-unit-authority-design-candidate-001
    M | governance/group-c-c8-work-unit-authority-plan-candidate-001
    M | governance/group-c-c8-work-unit-candidate-001
    M | governance/group-c-c9-v2.7.4-authority-design-candidate-001
    M | governance/group-c-c9-v2.7.4-authority-plan-candidate-001
    M | governance/group-c-c9-v2.7.4-authority-plan-fix1-candidate-001
    M | governance/group-c-c9-v2.7.4-authority-plan-fix2-candidate-001
    M | governance/group-c-c9-v2.7.4-bootstrap-authority-mapping-plan-fix2-candidate-001
    M | governance/group-c-c9-v2.7.4-packaging-bootstrap-reconciliation-design-candidate-001
    M | governance/group-c-c9-v2.7.4-packaging-bootstrap-reconciliation-plan-candidate-001
    M | governance/group-c-c9-v2.7.4-packaging-bootstrap-reconciliation-plan-candidate-002
    M | governance/group-c-c9-v2.7.4-packaging-bootstrap-reconciliation-plan-candidate-003
    M | governance/group-c-c9-v2.7.4-packaging-candidate-003
    M | governance/group-c-c9-v2.7.4-packaging-work-unit-candidate-003
    M | governance/group-c-c9-v2.7.4-phase-a-source-candidate-002
    M | governance/group-c-c9-v2.7.4-phase-a-validation-order-amendment-candidate-001
    M | governance/group-c-c9-v2.7.4-release-work-unit-candidate-001
    M | governance/group-c-c9-v2.7.4-release-work-unit-candidate-002
    M | governance/group-c-c9-v2.7.4-runtime-scope-correction-design-candidate-001
    M | governance/group-c-c9-v2.7.4-runtime-scope-correction-plan-candidate-001
    M | governance/group-c-v2.7.4-c1-c7-candidate-001
    M | governance/group-c-v2.7.4-work-unit-candidate-001
    M | governance/p2-minimum-capability-design-revision-002-candidate-001
    M | governance/p2-minimum-capability-plan-revision-002-candidate-001
    M | governance/p2-minimum-capability-plan-revision-003-candidate-001
    M | governance/p2-rev002-implementation-work-unit-candidate-001
    M | governance/p2-rev002-work-unit-authority-design-candidate-002
    M | governance/p2-rev002-work-unit-authority-plan-candidate-001
    M | group-b/b1-task5
    M | group-b/b2-task6
    M | group-b/b3-task7
    M | group-b/b4-task8
    M | group-b/b5-task9
    M | migration/framework-contract-repair-bridge-005
    M | release/v2.7.3-group-b-candidate-001
    M | release/v2.7.3-publication-packaging-w-candidate-001
    M | task3-global-plugin-core-001

    U | artifact/bridge-004-approval-payload-001
    U | design/group-b-prerequisite-bootstrap-amendment-001
    U | design/group-b-prerequisite-bootstrap-finalization-correction-001
    U | design/group-b-prerequisite-contract-reconciliation-001
    U | design/group-b-prerequisite-finalization-work-unit-amendment-001
    U | framework-contract-repair-design-001
    U | framework-contract-repair-plan-001
    E | framework-evidence/prj-framework-management/1682c2984f185114
    E | framework-evidence/prj-framework-management/5439535fffca9227
    E | framework-evidence/prj-framework-management/806a00166c852950
    E | framework-evidence/prj-framework-management/c86c2d5217b966b8
    E | framework-evidence/prj-framework-management/d00d7f11cfc80c63
    U | framework-group-b-prerequisite-bootstrap-amendment-accepted-001
    U | framework-group-b-prerequisite-bootstrap-design-accepted-001
    U | framework-group-b-prerequisite-contract-reconciliation-design-accepted-001
    U | framework-group-b-prerequisite-contract-reconciliation-plan-001
    U | framework-group-b-prerequisite-contract-reconciliation-plan-accepted-001
    P | framework-group-b-prerequisite-finalization-work-unit-design-accepted-001
    U | framework-group-b-prerequisite-minimal-closure-plan-accepted-001
    U | framework-staged-closure-design-001
    U | framework-staged-closure-master-plan-001
    U | governance/b7-release-authority-plan
    U | governance/b7-release-authority-plan-r2
    U | governance/group-c-c9-v2.7.4-finalization-authority-amendment-001
    U | governance/group-c-c9-v2.7.4-finalization-history-001
    U | governance/group-c-c9-v2.7.4-finalization-history-002
    U | governance/group-c-c9-v2.7.4-finalization-work-unit-candidate-003
    U | governance/group-c-c9-v2.7.4-packaging-work-unit-candidate-001
    U | governance/group-c-c9-v2.7.4-packaging-work-unit-candidate-002
    U | governance/group-c-c9-v2.7.4-phase-a-source-candidate-001
    U | governance/p2-rev002-work-unit-authority-design-candidate-001
    U | plan/group-b-prerequisite-bootstrap-corrective-activation-001
    P | plan/group-b-prerequisite-minimal-closure-001

## Hard exclusions and handoff

No local workspace cleanup, Post-P2 Foundation implementation, Plugin capability expansion, Hooks, Framework 2.8.0 bump/release, P3, P4, public Plugin release, MCP, second STATE, database, registry, queue, daemon, session manager or automatic migration/adoption. This Plan is CANDIDATE_ONLY and needs GPT review, then normal governed authorization before any phase executes.
