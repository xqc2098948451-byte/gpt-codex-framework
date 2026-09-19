# Group B Prerequisite Bootstrap Finalization Correction Design

## 1. Status and scope

Status: proposed Design correction candidate.

This document corrects only the publication/finalization boundary of the already accepted prerequisite-bootstrap amendment at commit 97afda5e716dea7b53724e3d2dbede977d4a669c.

It does not change prerequisite repair semantics, path owners, role separation, corrective target version, Group-B release, Group-C release, Plugin deferral, bridge-005 reservation, or the B0/B1 authority boundary.

## 2. Observed contradiction

The accepted bootstrap amendment combines four requirements:

1. the final reviewed and USER-accepted release SHA becomes remote main;
2. tag v2.7.2+fix.2 targets that same active SHA;
3. tracked State/evidence durably records remote publication facts;
4. no tracked mutation occurs after final review.

Remote publication facts exist only after publication. Putting those facts into the same commit whose SHA they describe creates a Git self-reference: changing the evidence bytes changes the commit SHA.

The successful v2.7.2+fix.1 history already shows the repository's working pattern:

    release/active commit R =
    b4bc96bcfebad941edf5a5c2ee5368e9e94045a6

    management finalization commit F =
    a0b5213959aaf92c9b3f72cd213e9d1264e7f5e6

    tag v2.7.2+fix.1 -> R
    final main -> F
    STATE.latest_verified_remote_sha -> R

The finalization commit changes only management continuity/evidence after remote publication is known.

## 3. Corrected activation architecture

The v2.7.2+fix.2 bootstrap uses the same two-phase shape, strengthened so both tracked revisions are independently reviewed and exactly USER-accepted.

### Phase A — release candidate R

R contains:

- all prerequisite reconciliation implementation bytes;
- exact source/version metadata for v2.7.2+fix.2;
- release index/record values including the exact artifact SHA-256 and size;
- no post-publication verification evidence;
- no State claim that remote publication already occurred.

Before publication:

    R
    -> fresh local independent cumulative CODEX_REVIEWER
    -> GPT adjudication
    -> USER_APPROVER exact R acceptance

Then USER_LOCAL may:

1. fast-forward main to exact R;
2. create annotated tag v2.7.2+fix.2 targeting exact R;
3. publish the exact artifact bound to R metadata;
4. freshly verify remote main/tag/release/artifact/version facts for R.

At this point:

    FRAMEWORK_ACTIVE_SHA = R
    TAG_TARGET_SHA = R
    REMOTE_RELEASE_VERIFIED = YES

R is the active Framework authority for v2.7.2+fix.2.

### Phase B — management finalization candidate F

Only after Phase-A remote facts exist may USER_LOCAL prepare F as a descendant of R.

F may modify exactly these three management-only paths:

    .gpt-codex/STATE.json
    .gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json
    .gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json

The new verification evidence records the already-observed release facts for R.

The publication Result records R as the verified release/active SHA.

State advances by exactly one revision and records:

- latest_verified_remote_sha = R;
- last_verified_result_ref = .gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json;
- sync_status = SYNCED;
- the current finalization revision;
- next_action = GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED.

No consumer/runtime/framework implementation byte changes between R and F.

Before F is integrated:

    F
    -> fresh local independent CODEX_REVIEWER
    -> verify F descends linearly from R
    -> verify changed paths equal exactly the three finalization paths
    -> verify F evidence matches fresh remote facts for R
    -> GPT adjudication
    -> USER_APPROVER exact F acceptance

Then USER_LOCAL may fast-forward main from R to exact F.

## 4. Active Framework SHA versus management HEAD

After finalization:

    FRAMEWORK_ACTIVE_SHA = R
    TAG_TARGET_SHA = R
    REMOTE_MANAGEMENT_HEAD = F
    F descends from R

This is not an authority mismatch.

R is the immutable release/tag target whose consumer-visible Framework bytes were reviewed, accepted, published, and remotely verified.

F is a management-only continuity/evidence descendant. It does not redefine release bytes or move the release tag.

The current v2.7.2+fix.1 repository already uses this distinction.

Repeated B0 uses:

- active Framework release/tag authority from R;
- current management State/continuity facts from F.

Neither source substitutes for the other.

## 5. No unreviewed tracked mutation

The earlier phrase "no tracked mutation after final review" is replaced by:

    NO UNREVIEWED TRACKED MUTATION

There are two separately governed tracked candidates:

1. release candidate R;
2. management finalization candidate F.

Each receives:

    exact candidate freeze
    -> USER-started local independent CODEX_REVIEWER
    -> GPT adjudication
    -> USER exact acceptance
    -> only then fast-forward integration

Any change after review makes that candidate's review stale.

No third tracked commit is authorized by this bootstrap lifecycle.

## 6. Artifact generation boundary

The amended Plan must not run release_framework.py against repository dist/ because its current cleanup step deletes prior gpt-codex-framework-v*-* files.

For v2.7.2+fix.2 packaging, USER_LOCAL uses an output directory outside the repository working tree, such as a temporary directory.

Generated artifact files are external publication artifacts, not tracked bootstrap mutation paths.

The Plan must verify:

- ZIP integrity;
- deterministic regeneration;
- artifact SHA-256 and size;
- release record/index equality to that SHA;
- exact published asset equality after remote publication.

This preserves the current METADATA_ONLY retention policy and avoids deleting retained historical dist files.

## 7. Bootstrap termination

The bootstrap does not terminate immediately after R publication.

It terminates only after:

1. R is remotely published and verified;
2. F is independently reviewed;
3. GPT adjudicates F;
4. USER exactly accepts F;
5. USER_LOCAL fast-forwards main R -> F;
6. remote main is verified at exact F;
7. F is proven to change only the three management finalization paths and retain the exact active R ancestor/tag relationship.

After termination, the bootstrap cannot authorize further tracked mutation.

## 8. Exact amended lifecycle

    accepted bootstrap Design correction
    -> accepted amended Plan
    -> immutable one-time bootstrap authorization
    -> local PRE_EXECUTION review
    -> GPT adjudication
    -> USER exact bootstrap approval
    -> USER_LOCAL prerequisite implementation milestones
    -> local independent milestone POST reviews
    -> build external fix.2 artifact
    -> release candidate R
    -> local independent cumulative R review
    -> GPT adjudication
    -> USER exact R acceptance
    -> USER_LOCAL FF main -> R
    -> tag v2.7.2+fix.2 -> R
    -> publish exact artifact
    -> remote verify R
    -> prepare three-path finalization F
    -> local independent F review
    -> GPT adjudication
    -> USER exact F acceptance
    -> USER_LOCAL FF main R -> F
    -> remote verify F management head + R active tag ancestry
    -> bootstrap terminated
    -> repeat Group-B B0 read-only

## 9. Preserved boundaries

Unchanged:

    CORRECTIVE_BASELINE_VERSION = 2.7.2+fix.2
    GROUP_B_RELEASE = 2.7.3
    GROUP_C_RELEASE = 2.7.4
    TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO
    PLUGIN_WORK_RESUMED = NO
    BRIDGE_004_REUSE = FORBIDDEN
    BRIDGE_005_CREATED = NO
    B0_PASS_DOES_NOT_AUTHORIZE_B1 = YES
    GPT_IMPLEMENTATION_ACTIVITY = NO

The release/finalization correction does not enlarge prerequisite implementation scope.

## 10. Failure handling

Stop fail-closed if:

- R is not the exact reviewed and USER-accepted release candidate;
- main cannot fast-forward exactly to R;
- tag target differs from R;
- published artifact hash/size differs from R metadata;
- remote verification cannot prove R;
- F does not descend from R;
- F changes any path outside the exact three finalization paths;
- F evidence does not match observed R publication facts;
- F review/acceptance targets another SHA;
- main cannot fast-forward R -> F;
- final main does not equal F;
- tag target no longer equals R;
- any consumer/runtime byte changes in F.

No force push, tag retargeting, evidence fabrication, commit self-reference, or informal latest-HEAD substitution is allowed.

## 11. Lifecycle and acceptance

This correction follows the existing Design lifecycle:

    Design correction candidate
    -> USER starts fresh local independent CODEX_REVIEWER
    -> GPT adjudication
    -> USER exact correction acceptance
    -> immutable accepted correction ref
    -> amended Plan candidate
    -> local independent Plan review
    -> GPT adjudication
    -> USER exact amended-Plan acceptance

Only after that lifecycle may the bootstrap authorization payload be prepared.

## 12. Acceptance criteria

This correction is acceptable only if independent review confirms:

1. the single-commit publication/finalization shape is self-referential and not executable;
2. the two-phase R -> F pattern matches existing repository precedent;
3. both R and F require independent review and exact USER acceptance;
4. active Framework SHA remains R/tag target;
5. final management HEAD is F and descends from R;
6. F is limited to exactly three management-only finalization paths;
7. no consumer/runtime byte changes in F;
8. packaging occurs outside repository dist/;
9. no unreviewed tracked mutation occurs;
10. bootstrap terminates only after F remote verification;
11. all earlier bootstrap/Group-B/bridge boundaries remain unchanged.

## 13. Candidate self-review

- Fixes only publication/finalization boundary: YES.
- Changes prerequisite implementation semantics: NO.
- Adds a third implementation phase: NO; F is management-only finalization.
- Matches fix.1 repository precedent: YES.
- Removes Git self-reference: YES.
- Permits unreviewed tracked mutation: NO.
- Changes active release identity from R after finalization: NO.
- Reuses bridge-004/bridge-005: NO.
- Changes Group B / Group C versions: NO.
- Authorizes GPT implementation: NO.
