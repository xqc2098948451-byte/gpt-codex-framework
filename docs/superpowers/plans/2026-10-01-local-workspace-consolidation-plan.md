# Local Workspace Consolidation Plan — candidate v2

**Status:** ANALYSIS_ONLY; repository-external plan candidate. It does not authorize execution, create a Work Unit, bind a root, normalize a checkout, remove a worktree, delete a file, or start Local Workspace Freeze. Companion documents: `LOCAL-WORKSPACE-CONSOLIDATION-DESIGN-CANDIDATE-v2.md`, `LOCAL-WORKSPACE-INVENTORY-v2.json`, and `LOCAL-WORKSPACE-BLOCKER-RESOLUTION.json`.

## Common authority gate

Before **each** later governed phase, reverify `origin/main=734839ac8a45f10661a2fa08fec4d4bd257ad0b9` or reconcile any new authorized baseline; STATE revision 25 / AUTHORIZED / SYNCED and exact next action; zero open PRs; Phase G Freeze `{2ee02c659ed4922ffe6ac28646d0ca498ca39004, .gpt-codex/evidence/GITHUB-REPOSITORY-STRUCTURE-FREEZE.json, 653506a44eefb949d4e6f26dec0d1e3f8a55c9ae}`; and the accepted Repository Consolidation Design. Every mutation needs a separately issued bounded Work Unit/Instruction and applicable PRE review. A candidate, pathname, branch or this plan grants no authority. Capture a fresh path/registration/ref/status snapshot before and after every mutation phase. Any drift, ambiguity, missing authorization or failed review stops for reconciliation.

The evidence boundary is 156 prior entries: 103 target-owned, 48 project artifacts, 2 proven unrelated and 3 ownership-unresolved. Mutation planning excludes the unrelated entries and leaves unresolved ones untouched. A phase may proceed without solving arbitrary adjacent directories. There are 57 registered worktrees, 56 with role unresolved for execution, 13 dirty registered worktrees, two target local-only registered HEADs, one dirty integration checkout, four synthetic bare fixture repositories, and zero current DELETE_SAFE candidates.

## L0 — Authority and ownership lock

- **Input authority:** Fresh remote/STATE/Freeze, accepted Design section 8, inventory v1/v2 and raw Git/fixture evidence.
- **Exact mutation class:** `NO_MUTATION`; read-only verification of identity, scope, registration, remote refs, artifact links and per-entry ownership.
- **Preconditions:** GitHub and repository ID match; each proposed target has a positive ownership signal; mixed parents are decomposed by child; unrelated and unresolved rows are excluded from proposed changes.
- **Rollback:** None; preserve the starting snapshots.
- **Independent review:** Separate reviewer checks the 103/48/2/3 partition and all exact source-to-authority links, especially the two marketplace checkouts and three empty paths.
- **Stop condition:** Authority drift, unexplained path/registration difference, or a proposed mutation target without positive ownership proof.

## L1 — Local-only preservation

- **Input authority:** Reviewed L0 matrix, exact Git HEAD/ref/working status, 23-item resolution, bare fixture history, and external artifact lifecycle evidence.
- **Exact mutation class:** `LOCAL_PRESERVATION_ONLY` under later explicit authority: reviewed refs/archives/manifests outside the repository; no cleanup or remote mutation by default.
- **Preconditions:** Preserve `f6d319f...` and `a48d87c...` plus all uncommitted tracked/staged/untracked/ignored bytes and any necessary synthetic bare fixture or PRE/POST bytes. Record SHA-256/Git object hashes, source path and private handling. Prove the archive/ref can be read independently before touching source.
- **Rollback:** Source stays intact; discard only a failed new preservation copy after independent review.
- **Independent review:** Reviewer verifies manifests, content/commit reachability and restoration sample; no name-only claim suffices.
- **Stop condition:** Unmapped unique content, unresolved local-only tip, missing archive integrity, secret-handling issue or an unfinished authority dependency.

## L2 — Path-layout authority resolution

- **Input authority:** Accepted full-ID Design sentence, frozen tree max 122, Phase F path evidence, and L0/L1 findings.
- **Exact mutation class:** `NO_MUTATION`; resolve the design review decision only. Current candidate says full ID is feasible under 240 because 171 fixture characters belong to a separate temp root.
- **Preconditions:** Independently reproduce `D:\=236`, `D:\w=238`, `D:\wt=239` worst review paths with 83-character ID, 7-character prefix and 19-character slug; verify ordinary generated paths do not exceed the observed 122 expansion; keep ephemeral validation root separate.
- **Rollback:** None; an unaccepted candidate leaves the accepted full-ID sentence in force and worktree operations stopped.
- **Independent review:** Reviewer checks source tree/API, fixture location, formula, Windows setting and validator/tool compatibility. If a new safety reserve or longer required ordinary path invalidates full-ID feasibility, return for a separately accepted Design amendment; no automatic hash leaf.
- **Stop condition:** Path estimate above 240, unproved in-worktree generated path, or unresolved disagreement about the accepted layout.

## L3 — WORKTREE_ROOT binding

- **Input authority:** Reviewed L2 decision and current-machine evidence for D: capacity, ACL, collisions, aliases and backup.
- **Exact mutation class:** `LOCAL_BINDING_AND_OPTIONAL_EMPTY_ROOT_CREATION_ONLY` under separate future authority; no repository policy path or worktree move.
- **Preconditions:** Select `D:\w` provisionally, prove path/ACL/Git feasibility by an authorized bounded probe, check case-insensitive canonical paths, junctions, branch occupancy, target ownership and exact per-entry path budget. Never use suffixes to evade collision.
- **Rollback:** Restore previous local binding; remove only an empty newly created root if specifically authorized and independently proven empty.
- **Independent review:** Reviewer validates root selection, probe, no repo diff and path margin per planned ID.
- **Stop condition:** Collision, alias, permission failure, unproven tool compatibility or any target above 240.

## L4 — Main integration checkout normalization

- **Input authority:** Reviewed L1 preservation of four modified tracked paths and three duplicate external release files; current main checkout HEAD/branch/status and fresh remote main.
- **Exact mutation class:** `MAIN_CHECKOUT_RECONCILIATION_ONLY` under later bounded authority; no ordinary implementation in main.
- **Preconditions:** Independently verify no staged paths, all seven dirty paths, exact duplicate hashes for three release files, and durable retention of four unique tracked files before any switch/reset/cleanup. Select exact integration baseline and role through a governed instruction.
- **Rollback:** Preserve original branch/HEAD, working bytes and verified archive; restore them if normalization fails, then stop.
- **Independent review:** Separate reviewer checks byte-level preservation, clean final status, correct remote relation and integration-only activity.
- **Stop condition:** Any dirty path unaccounted for, missing preservation, changed remote authority or failed clean/role verification.

## L5 — Worktree consolidation

- **Input authority:** Reviewed L0–L4, bound root, exact per-worktree Work Unit/Instruction/role/ref/HEAD, and fresh remote reachability.
- **Exact mutation class:** `GIT_AWARE_MOVE_OR_RECREATE_NAMED_WORKTREE_ONLY`; one named worktree per reviewed decision, no arbitrary directory renames.
- **Preconditions:** Resolve each of 56 non-main registered roles; check existence, lock/prunable state, status including ignored, process use, branch occupancy, target collision and full path. MOVE retains local identity/content; RECREATE_FROM_REMOTE requires a retained remote commit and no unique local data. Dirty/local-only/unresolved worktrees stay put until L1 proof is accepted.
- **Rollback:** Retain old source/registration or verified archive until target HEAD/ref/status/path and `git worktree list --porcelain` pass; reverse only the failed item and halt batch.
- **Independent review:** Per-entry reviewer approves MOVE versus RECREATE and verifies post-state separately from implementer.
- **Stop condition:** Any unmapped role, local-only content, stale authority, over-budget path, occupied branch, in-use directory or mismatch.

## L6 — Proven stale workspace removal

- **Input authority:** Reviewed L0–L5 outcomes and separate exact-path deletion authorization. Current `DELETE_SAFE=0`.
- **Exact mutation class:** `DELETE_EXACT_APPROVED_LOCAL_PATH_ONLY`; never derive targets from names, UNKNOWN labels or prunable status.
- **Preconditions:** Every Design v2 DELETE_SAFE criterion passes for that exact owned/artifact path, including inactivity, zero unique content/refs/dependencies, reproducibility or durable preservation, recoverable snapshot and independent pre-delete approval. Nested workspaces and mixed parents receive separate proof.
- **Rollback:** Restore the verified snapshot and reconcile Git registration; stop all later removals after any mismatch.
- **Independent review:** Reviewer approves each proof bundle and checks post-removal topology/registry.
- **Stop condition:** No individually approved candidates, changed bytes/refs/status, missing proof, or unresolved owner/dependency. With current evidence this phase performs no removal.

## L7 — Independent verification

- **Input authority:** Exact authorized phase records, starting snapshots, current remote/STATE/Freeze and retention manifests.
- **Exact mutation class:** `NO_MUTATION`; independent read-only verification.
- **Preconditions:** Recompute owned/artifact/out-of-scope set, remote refs, local refs, worktree registry and statuses, root paths and depth, main checkout integration role, external artifact hashes and rollback sources.
- **Rollback:** If verification fails, retain all sources and route to the specific phase rollback under its authority; no automatic cleanup.
- **Independent review:** Reviewer with separate context signs exact before/after identities and explains every intended difference.
- **Stop condition:** Any unexplained topology, remote, STATE, ref, byte, role or path-depth difference.

## L8 — Local Workspace Freeze

- **Input authority:** Independently accepted L0–L7 evidence, fresh remote STATE and immutable Phase G Freeze.
- **Exact mutation class:** `FREEZE_EVIDENCE_ONLY` if and only if a later governed Freeze instruction authorizes it; no automatic deletion or new worktree.
- **Preconditions:** All changed target entries reviewed, unrelated/unresolved paths excluded, local-only data durably preserved, main clean and integration-only, root/layout accepted, registration reconciled, external dependencies retained, DELETE_SAFE proofs complete and L7 no-drift PASS.
- **Rollback:** Keep prior snapshots and source/archives; if Freeze evidence fails review, remain pre-Freeze and reconcile without overwriting STATE.
- **Independent review:** Separate POST/Freeze reviewer checks exact authority, evidence and acceptance criteria.
- **Stop condition:** Any unmet criterion, new authority drift, failed review or request to infer execution permission from this candidate.
