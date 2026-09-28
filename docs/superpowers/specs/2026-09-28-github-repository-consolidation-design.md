# GitHub Repository Consolidation Design — Rev002

STATUS = CANDIDATE_ONLY
EXECUTION_AUTHORIZED = NO

## 1. Authority and purpose

Repository: xqc2098948451-byte/gpt-codex-framework. Fresh fetch and remote ref check on 2026-09-28 both resolved main to b96e077362477ef697670ddc04f4e6c77c880271. That tree contains 364 tracked paths. Its .gpt-codex/STATE.json has revision 18, state AUTHORIZED, reconciliation null, and latest_synced_state_revision 18. VERSION and the consumer manifest both say 2.7.4. These are observation facts, not an execution grant. Sources: [main tree](https://github.com/xqc2098948451-byte/gpt-codex-framework/tree/b96e077362477ef697670ddc04f4e6c77c880271), [STATE](https://github.com/xqc2098948451-byte/gpt-codex-framework/blob/b96e077362477ef697670ddc04f4e6c77c880271/.gpt-codex/STATE.json), [manifest](https://github.com/xqc2098948451-byte/gpt-codex-framework/blob/b96e077362477ef697670ddc04f4e6c77c880271/.gpt-codex/release/consumer-projection-manifest.json).

The design consolidates GitHub repository responsibilities, removes proven duplicate semantics, normalizes repository directories and documentation, reconciles consumer projection, records public release deferral, cleans stale GitHub metadata under review, and freezes the repository structure. It does not authorize a Work Unit, Instruction, PR action, branch deletion, source mutation, or STATE change. The implementation must use the existing Framework governance path.

Stage order is GitHub Consolidation → GitHub Structure Freeze → Local Workspace Consolidation → Local Workspace Freeze → Post-P2 Foundation → Foundation Freeze → Framework 2.8.0 Release → P3 → P4.

## 2. Responsibility boundaries

One primary implementation owns each capability. Callers may validate their own input and output defensively.

| Capability | Primary owner | Boundary |
| --- | --- | --- |
| PROJECT_IDENTITY | context_binding.py | Project and context IDs |
| GITHUB_REPOSITORY_IDENTITY | github_repository_binding.py | Stable repository binding |
| IMMUTABLE_GIT_CONTINUITY | git_continuity.py | Git object and remote continuity |
| PROJECT_NAVIGATION | project_navigation.py | Derived map and location |
| RESUME_AND_RECOVERY | continuity_resume.py | Resume from current authority |
| PLUGIN_ADAPTER | framework_plugin_entry.py | Thin presentation and access adapter |
| INSTRUCTION_CONTRACT | instruction_envelope.py | Durable instruction syntax and resolution |
| ROLE_AND_ACTION_AUTHORITY | role_communication.py | Role taxonomy and action routing |
| RESULT_AUTHORITY_AND_PUBLICATION | publication_contract.py | Publication eligibility and Result/Evidence authority binding |
| RESULT_RETURN_RENDERING | result_return.py | Validated Result rendering and return transport only |
| PROJECT_GOVERNANCE_GATE | validate_project.py | Project mutation gates, scope and candidate tree |
| FRAMEWORK_CONFORMANCE | validate_framework.py | Framework structure and contract checks |
| CONSUMER_PROJECTION | consumer_projection.py | Manifest classification, inventory and boundary |
| RELEASE_BUILD_AND_PACKAGE | release_framework.py | Build and deterministic package orchestration |
| RELEASE_ARCHIVE_AND_RECORDS | release_archive.py | Release archive/record operations |
| RELEASE_VERSION_POLICY | release_archive.py | One pure Framework release-version parser/order policy shared by release consumers |

A TRUE_DUPLICATE implements the same rule twice with equivalent input and authority. VALID_DEFENSIVE_VALIDATION checks the same contract at a separate trust boundary and stays fail-closed. PRESENTATION_DUPLICATION repeats text or formatting without authority and may be simplified only when observable output remains stable. Fewer lines of code do not justify removing defensive checks.

The verified TRUE_DUPLICATE is release version syntax and ordering: release_framework.py has a SEMVER expression while release_archive.py has SEMVER_PATTERN and _version_key. Consolidate into a pure parser/comparison function owned by release_archive.py and imported by release_framework.py. Preserve strict three-component current VERSION validation and explicitly model any legacy two-component archive-name acceptance in one parser policy; do not silently broaden current VERSION. The repeated baseline/resume handling inside framework_plugin_entry.py is a candidate TRUE_DUPLICATE only after equivalence tests prove identical error/status behavior. Otherwise retain it as defensive validation or presentation logic. Do not create a version service, registry, database or module subsystem.

## 3. Authority path stability

Default KEEP_EXISTING_PATH applies to .gpt-codex/evidence/, evidence/instructions/, evidence/results/, work-units/, and schemas used by durable contracts. A move requires an inventory of current-tree references, schema/path validators, consumer references, and immutable commit:path or commit:path+blob locators, followed by a migration-safe proof. Existing immutable historical locators remain valid; do not rewrite their history. Update any current-tree links that point to moved files. Work Unit lifecycle should be logical state/archive classification at the existing path, not a mass physical active/archive move.

## 4. Repository and documentation model

The minimum target surface keeps current runtime scripts, schemas, authority artifacts, project templates, builtins, Plugin, release metadata, and generated distribution locations discoverable:

    .gpt-codex/{scripts,schemas,evidence,work-units,project-template,builtins,release,framework-modules}/
    plugins/gpt-codex-framework/
    releases/
    dist/
    docs/{architecture,decisions,plans,history/{designs,plans,amendments,reviews}}/
    docs/superpowers/    # existing legacy paths retained until reference-safe migration

docs/architecture states the current system; docs/decisions records why and freezes; docs/plans holds active near-term plans; docs/history holds completed development process. A concise current architecture index must link primary owners and current decisions so readers need not traverse dozens of historical plans. Do not create .gpt-codex/core/ or another abstract layer for appearance. docs/decisions/ is human-readable architecture/decision documentation and may point to governed authority; it is not a second machine execution-authority store and never replaces CONTROL, STATE, Work Units, Instructions, Results, Evidence, or immutable Git authority.

The following new directories are the only ones this candidate proposes. Each line is a directory declaration; approval of this Design is required before its corresponding governed Work Unit can create the prefix. The owner is the Framework maintenance Work Unit, lifetime is durable, consumer_visible=false, release_visible=false, and cleanup_policy=reviewed historical retention for every line. These shared fields are part of each declaration, not inherited authorization for arbitrary descendants.

| Path | Purpose | content_type | authority_type |
| --- | --- | --- | --- |
| docs/architecture/ | Current architecture entry point | Markdown architecture/index | Advisory navigation |
| docs/decisions/ | Accepted decisions and freezes | Markdown decision/evidence pointer | Accepted Design/Decision |
| docs/plans/ | Active near-term plan navigation | Markdown plan/index | Governed plan |
| docs/history/ | Completed process parent | Markdown history | Development history |
| docs/history/designs/ | Completed designs | Markdown design | Development history |
| docs/history/plans/ | Completed plans | Markdown plan | Development history |
| docs/history/amendments/ | Completed amendments | Markdown amendment | Development history |
| docs/history/reviews/ | Completed reviews and reports | Markdown review/report | Development history |

The six tracked .superpowers/sdd task reports have no observed production runtime, authority, consumer projection, or release dependency. The manifest and tests classify that prefix as DEVELOPMENT_HISTORY; the prior review recorded an unresolved reconstruction question. Therefore move them only after per-report reference and reconstruction checks. No future task-report process files belong in the active repository surface. The Plan specifies a bounded six-file move, with KEEP_IN_PLACE on any failed proof. No historical immutable locator is rewritten.

## 5. Consumer projection

The main-tree manifest has framework_version 2.7.4 and 204 explicit entries: 86 CONSUMER_REQUIRED, 90 MANAGEMENT_ONLY, 24 GENERATED_ARTIFACT, 2 LOCAL_ONLY, and 2 RELEASE_METADATA. Twenty-two explicit entries are absent from the current Git tree: one .superpowers/sdd .gitignore and 21 old dist files. None is classified CONSUMER_REQUIRED. Phase B may remove an absent entry only after proving the path is no longer a required consumer contract. If any allegedly stale path should exist, stop with FINDING and restore the missing file through separate authority. Passing a validator is not sufficient reason to delete a contract. Final gates: unknown paths 0, missing required 0, contamination 0, and no management files in the consumer package.

## 6. PR, branch and tag rules

Each open PR is classified MERGE, CLOSE_SUPERSEDED, or KEEP_OPEN from its current purpose, base/head, review authority, and relation to main. Never merge all open PRs by policy. Public GitHub currently shows one open draft PR, #15, for a Group B prerequisite PRE_EXECUTION coordination gate. Its old non-main base and plan head are superseded by the 2.7.4 main lineage, so its candidate decision is CLOSE_SUPERSEDED / DO_NOT_MERGE, conditional on a fresh Phase A check of conversation, refs and ongoing review. Closing it changes GitHub metadata, not main source. [PR list](https://github.com/xqc2098948451-byte/gpt-codex-framework/pulls), [PR #15](https://github.com/xqc2098948451-byte/gpt-codex-framework/pull/15).

Every remote branch is classified KEEP, DELETE_SAFE, or REVIEW_REQUIRED. DELETE_SAFE requires all of: not main, not protected, no active work or open PR need, no remote-review/bootstrap/authority continuity need, no sole reachable authority candidate, no current Evidence/Work Unit/Instruction dependency, and integrated/superseded or explicitly historical content. Ancestor-of-main alone is insufficient. A REVIEW_REQUIRED branch has an exact reason and a resolution test in the Plan; it is not deleted until promoted by fresh evidence. Before any PR close or branch delete, the exact decisions must be written to `.gpt-codex/evidence/GITHUB-REPOSITORY-CONSOLIDATION-REF-CLEANUP.json`, independently reviewed, integrated, and consumed only through its immutable Git locator. That ledger records exact PR/branch identities, observed head SHAs, predicates, reasons, review status, and retained reachability. No ref deletion may cause a current durable-authority commit to become unreachable from all retained remote refs. If reachability cannot be proven through main, a retained tag, or another retained authority ref, DELETE_SAFE is denied; a separately governed archival authority tag/ref may be created first when justified. Authority, release and bootstrap tags are DELETE = DENY. This phase deletes no authority tag.

## 7. Codex Directory Creation Contract

CREATE_DIRECTORY_DEFAULT = DENY. A new durable directory requires a declaration with path, purpose, owner, content_type, authority_type, lifetime, consumer_visible, release_visible, and cleanup_policy. Missing fields produce DIRECTORY_CREATION_DENIED. A new top-level directory additionally requires an explicit approved Architecture/Design authority and otherwise produces STRUCTURE_CHANGE_REQUIRED.

The gate compares BASE_GIT_TREE and CANDIDATE_GIT_TREE, derives every newly introduced directory prefix from tracked candidate paths, and checks each against authorized declarations and the Work Unit/Instruction scope. EXISTING_DIRECTORY_WRITE means writing a file beneath a prefix already present in the base tree; NEW_DIRECTORY_CREATION means introducing a prefix absent from it, even beneath an owned parent such as src/. Parent ownership never grants arbitrary descendants. Renames and deletions must not evade the comparison. Names must express semantic purpose; unapproved generic names such as new, final2, copy, backup, tmp, fix2 or latest-final are denied even if a declaration exists. Repo-local candidate workspaces, temporary ZIPs, unpacked archives, caches, scratch output, review copies and backups are denied; use an ephemeral workspace outside the repo.

Extend existing Work Unit, candidate scope/tree, framework/project validators, tests and AGENTS/bootstrap operating contract. Do not add a second directory manager or state store. The declaration is an authority assertion bounded by the accepted Work Unit and Design, not self-authorization.

## 8. Local worktree and release decisions

After GitHub Structure Freeze, local worktree layout is <WORKTREE_ROOT>/<repository-slug>/<work-unit-id>/; reviewer layout is <WORKTREE_ROOT>/<repository-slug>/review-<work-unit-id>/. Reject arbitrary final/fix2/latest/copy or date-final suffixes. Main checkout is INTEGRATION_AND_VERIFICATION_ONLY; ordinary implementation there is DENY. The later Local Workspace Design chooses the root without hard-coding this machine's Windows path.

PUBLIC_RELEASE = DEFERRED_BY_USER; PRIVATE_PLUGIN_USE = CONTINUE; RESUME_PUBLIC_RELEASE_REQUIRES_NEW_USER_AUTHORIZATION. The durable gap is one proposed .gpt-codex/evidence/POST-P2-PUBLIC-RELEASE-DEFERRAL.json. It records a decision only: it does not authorize execution, reopen the Public Release Work Unit, or change STATE merely by existing.

## 9. Scope and acceptance

Excluded: local workspace deletion/reorganization, Post-P2 Foundation implementation, Plugin expansion, Hooks, 2.8.0 bump/release, P3, P4, public Plugin release, MCP, second STATE, database, registry, queue, daemon, session manager, and automatic migration/adoption.

Acceptance requires the A–G Plan gates, preservation of immutable authority locators, projection closure, full validators/tests and clean-clone checks, and the exact durable Repository Structure Freeze artifact `.gpt-codex/evidence/GITHUB-REPOSITORY-STRUCTURE-FREEZE.json`. That artifact must bind the integrated commit SHA, STATE revision, capability-responsibility-matrix digest, directory-contract digest, canonical repository-tree digest, consumer-projection identity/hash, immutable ref-cleanup Evidence locator, remaining branch names and head SHAs, open-PR count/decisions, validator/full-test/clean-clone results, public-release deferral status, and `next_gate = LOCAL_WORKSPACE_CONSOLIDATION`. Until a governed implementation is separately authorized and verified, this document remains CANDIDATE_ONLY.
