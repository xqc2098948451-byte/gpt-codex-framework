# Local Workspace Consolidation Design — candidate v2

**Status:** ANALYSIS_ONLY. This is a repository-external review candidate. It grants no Work Unit, PRE/POST, checkout, worktree, deletion, remote, or Freeze execution authority. Source observations: `LOCAL-WORKSPACE-INVENTORY.json` (v1) and `LOCAL-WORKSPACE-INVENTORY-v2.json`. Reverify every mutable observation before a later authorized phase.

## 1. Immutable authority and scope

Target repository: `xqc2098948451-byte/gpt-codex-framework` (GitHub repository ID `1366213495`). Fresh `origin/main` was `734839ac8a45f10661a2fa08fec4d4bd257ad0b9`; its `.gpt-codex/STATE.json` blob was `a4759f123b1d7ed6ed6fccee1c9d2b4e8f44f705` with revision 25, `AUTHORIZED`, `SYNCED`, `next_action=LOCAL_WORKSPACE_CONSOLIDATION_REQUIRED`. Open PR count was zero. Phase G Repository Structure Freeze has immutable locator `{commit: 2ee02c659ed4922ffe6ac28646d0ca498ca39004, path: .gpt-codex/evidence/GITHUB-REPOSITORY-STRUCTURE-FREEZE.json, blob: 653506a44eefb949d4e6f26dec0d1e3f8a55c9ae}`. The frozen repository tree is `bc18d6e842fb919c7f90ff5a6835f8f71b3af5ee`.

The accepted Repository Consolidation Design remains `{commit: 6663e46ed210ec33354e5c1c5462d34205d77ae1, path: docs/superpowers/specs/2026-09-28-github-repository-consolidation-design.md, blob: 42210b3d2b86a6b4e28fc737fed92d312355ec5f}`. Section 8 supplies the full Work Unit ID layout. This candidate proposes **no amendment** to that sentence; `DESIGN_AMENDMENT_REQUIRED=NO` under the evidenced separation of ordinary worktree and ephemeral validation paths.

### Project ownership boundary

Of the 156 original inventory rows (nested directories count as separate rows): 103 are `PROJECT_OWNED`, 48 are `PROJECT_ARTIFACT`, 2 are `UNRELATED_PROVEN`, and 3 are `OWNERSHIP_UNRESOLVED`. Positive signals are target Git origin, target registered worktree or common-dir, exact Framework marker, exact project PRE/POST or release artifact, or the known test fixture generator. The two marketplace Git checkouts have a different origin and are outside this repository's consolidation mutation scope. The three empty/unproved directories (`D:\pfr-p`, `D:\pfr-x`, `D:\通用开发框架管理\c9-phase-a-review-simulation`) stay untouched. The mixed `.gpt-codex-transport` parent must never be treated as homogeneous because it contains separate marketplace repositories. A later phase needs to resolve ownership only for an entry it proposes to change; unrelated and unresolved adjacent directories do not block target work.

## 2. PORTABLE_FRAMEWORK_POLICY

`WORKTREE_ROOT` is a local, repository-external binding, not an absolute path stored in Framework policy. The verified repository slug is `gpt-codex-framework`. Preserve the accepted layouts:

- Implementation: `<WORKTREE_ROOT>/gpt-codex-framework/<exact-work-unit-id>/`.
- Review: `<WORKTREE_ROOT>/gpt-codex-framework/review-<exact-work-unit-id>/`.
- Main checkout: `INTEGRATION_AND_VERIFICATION_ONLY`; ordinary implementation there is denied.

The exact full Work Unit ID from durable authority is the directory leaf and remains the governance identity. Reject `final`, `fix2`, `latest`, `copy`, date, or similar ad hoc suffixes. A directory/branch name is only an inference: bind an implementation or review role to an exact current Work Unit, Instruction, ref, HEAD and lifecycle evidence before moving or recreating it. All 56 non-main registered worktrees remain `ROLE_UNRESOLVED` for execution decisions despite useful names and remote reachability observations.

### Separate validation checkout policy

Full clean-clone validation may use an explicitly authorized, short, detached, ephemeral checkout and a **separate** short external TEMP/TMP/TMPDIR/log root. Phase F used `C:\f1v930a` and `C:\f1t930a`, each 10 characters. That validation checkout is not the ordinary implementation/review worktree. Its baseline, tests, logs, package outputs, hashes and lifecycle must be recorded. Creation or cleanup is a later governed action. Do not add its fixture path expansion to an ordinary worktree path unless a future test proves the fixture is created there.

## 3. CURRENT_MACHINE_BINDING and path proof

`D:\w` remains the provisional local root, uncreated and unbound. It is a dedicated short namespace on the same D: NTFS volume; its parent permissions, Git behavior, collisions, in-use state and backup coverage still require an authorized probe and independent review. `D:\` is the shortest mathematically feasible candidate but would put the repository slug directly at the volume root. `D:\wt` is one character longer than `D:\w`. No root is created by this analysis. Windows `LongPathsEnabled=0`; no design claim depends on changing that setting or assuming every validator supports long paths.

The frozen tree's longest tracked repository-relative path is **122** characters (GitHub recursive tree at `bc18d6e...`, 505 entries, not truncated). No required ordinary in-worktree generated path longer than that was established in the inspected test calls; ordinary checkout planning therefore uses the **observed 122-character expansion**, with a fail-closed per-operation preflight for every actual generated path. Phase F's **171-character external temp-root expansion** came from its 181-character fixture maximum minus its separate 10-character temp root. It is an ephemeral-validation requirement, not a component of the ordinary worktree estimate. Longest current durable Work Unit ID: **83** characters; reviewer prefix: **7** characters; slug: **19** characters. The 240-character Phase F preflight cap is the chosen conservative Windows budget.

| Root | Worst full-ID review path | Margin to 240 |
| --- | ---: | ---: |
| `D:\` | 236 | 4 |
| `D:\w` | 238 | 2 |
| `D:\wt` | 239 | 1 |

For `D:\w`: `4 + 1 + 19 + 1 + 7 + 83 + 1 + 122 = 238`. `FULL_ID_LAYOUT_FEASIBLE=YES` for the current frozen tree, so no hash-leaf amendment is proposed or implemented. The two-character residual margin is narrow. Any new Work Unit ID, tracked path, in-worktree generated path, tool output path, or validator change must be measured against 240 before target creation; exceeding it stops the operation for a separately reviewed design decision. The previous 286/-46 result combined two independent filesystem roots and is not the ordinary worktree estimate. An additional 20-character reserve *inside* the 240-character cap is not accepted authority; imposing it later would require a new layout decision.

## 4. Local content and Git preservation

The exact main/integration checkout is `D:\通用开发框架管理\gpt-codex-framework`, HEAD `026798892bfe11858add7fb2b068f1ce75cba7c6` on `refs/heads/group-b/b2-task6`, with no configured upstream. That HEAD is an ancestor of verified remote main; staleness alone is not destructive evidence. Seven paths are dirty: four modified tracked files with Git blobs different from their remote-main counterparts, and three untracked `v2.7.2+fix.2` release files. The three release files have exact SHA-256 matches in `fix2-release-output-c893c728ac4d42b7ae719f423ea10fd2`; their external retention still requires review. The four tracked files remain unique local content. No paths are staged. `MAIN_CLEANUP_BLOCKED=YES` until a reviewed preservation/disposition precedes checkout normalization.

Among the previous 23 preservation/ref-review rows, primary classification is: 1 local-only target commit, 11 with uncommitted tracked/staged content, 6 with untracked content, 4 reproducible synthetic bare test repositories, and 1 different-repository row excluded from target scope with content retention unresolved. At workspace level there are zero purely remote-durable or fully proven duplicate-durable rows; three *main checkout files* have exact external duplicates. Categories are primary labels and do not erase secondary ignored, staged, or untracked content. The inventory keeps every source row and its per-entry evidence. A separate registered worktree at `.../.worktrees/group-c-c1-c7-work-unit-authority-plan-amendment` has local-only HEAD `f6d319f...` outside the previous 23 and also requires preservation. The detached `p2-minimum-capability-implementation` HEAD `a48d87c...` is the local-only HEAD inside that set. GitHub did not know either SHA. Keep both until a reviewed durable preservation ref or archive exists.

Four bare repositories under `D:\pfr-tmp` have no origin and one local `refs/heads/main` each. Their exact tips and availability are in inventory v2. Their history is independently generated by `.gpt-codex/tests/test_self_hosting_validator.py` for synthetic approval evidence; each target GitHub commit lookup returned 422. Classify their ref tips `NOT_TARGET_REPOSITORY`, not target remote-reachable, while preserving their local-only fixture bytes pending artifact retention review. No fetch, prune, push or ref deletion follows from this classification.

Repository-external PRE/POST, release, validation, archive, transport, log and fixture artifacts stay outside the repository. Keep exact bytes while an unfinished gate, immutable locator, result, review or rollback depends on them. A generated label alone never proves disposal. Treat ignored files as unassessed until a private content/hash review resolves them. Do not copy sensitive content into this public candidate or the repository.

## 5. Future MOVE, RECREATE_FROM_REMOTE, deletion, rollback

A future **MOVE** requires exact target ownership, current authorized role/Work Unit/ref/HEAD, clean or fully preserved status including ignored files, in-use check, path/collision preflight and Git-aware worktree operation. Preserve old registration/path and a recoverable snapshot until target identity, status and registration pass independent verification. A future **RECREATE_FROM_REMOTE** requires the exact commit reachable from a retained remote ref, no local-only commit or unique file, verified artifact dependencies, reproducible checkout and a separately reviewed target. A standalone clone is never silently converted merely because its origin matches. Otherwise disposition is KEEP or ARCHIVE_REVIEW_REQUIRED.

`DELETE_SAFE` requires all: project ownership/artifact proof; inactivity; no unique tracked, staged, untracked or ignored content; no local-only commit or unresolved ref; no unfinished PRE/POST or authority locator dependency; exact reproducibility or durable preservation; independent review of the exact path and future removal; and a recoverable rollback snapshot. Current candidate count is **zero**. Unrelated and ownership-unresolved entries are never deletion candidates. No deletion is authorized now.

Rollback keeps each source until the proposed target has independently verified HEAD/ref, bytes, status and Git registration. On any mismatch stop the batch and restore from the retained source or verified archive; never delete after a failed move/recreate. Record before/after topology and remote ref snapshots. Local Workspace Freeze requires fresh Phase G/STATE authority, reviewed ownership boundary and every changed entry, all unique content durably retained, resolved local-only refs, accepted path budget/root, clean integration-only main checkout, reconciled worktree registrations and external artifact dependencies, zero unresolved delete proof, independent verification and no drift. This candidate does not begin Freeze.
