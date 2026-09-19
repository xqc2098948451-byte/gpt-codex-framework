# Group B Prerequisite Bootstrap Corrective-Activation Design Amendment

## 1. Status and authority

**Status:** proposed Design amendment candidate. It is not accepted Design, not an implementation Plan, not a Work Unit, not an Instruction, not bootstrap execution authority, and not publication authority.

**Purpose:** close the execution-bootstrap circularity discovered only after the previously accepted prerequisite reconciliation Design and Plan reached fresh Task-0 execution preflight.

This amendment **does not rewrite** the already accepted artifacts. It overlays one narrowly bounded bootstrap path needed to make those accepted prerequisite corrections executable.

Accepted immutable inputs:

- accepted prerequisite reconciliation Design:
  `15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`
- accepted prerequisite reconciliation Plan:
  `36695832aa17198b217252077bcf70c6ba77c67a:docs/superpowers/plans/2026-09-19-group-b-prerequisite-contract-reconciliation-plan.md`
- staged-closure Design:
  `e5fe291c243d0e2bc18e3e5a3cd905e6aa223546:docs/superpowers/specs/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-design.md`
- staged-closure Master Plan:
  `94eb80869f43800c1c6b1a53d7393b90b4e7433b:docs/superpowers/plans/2026-09-18-framework-staged-closure-v2.7.2-v2.7.4-master-plan.md`
- corrected historical Contract Repair Design:
  `135f1c06b205894f0e603b0fdbf34cc10ba6e3f6:docs/superpowers/specs/2026-09-17-framework-contract-repair-design.md`
- corrected historical Contract Repair Plan:
  `7f9c0cf46aee2b6bfdbadc36eb8d6373592d4a55:docs/superpowers/plans/2026-09-17-framework-contract-repair.md`

Fresh Task-0 observation at amendment authoring time:

```text
main =
a0b5213959aaf92c9b3f72cd213e9d1264e7f5e6

STATE.revision =
15

STATE.next_action =
GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED

active Framework =
2.7.2+fix.1
```

These author-time values are evidence, not future execution constants. The amended Plan must re-observe them immediately before bootstrap preparation.

## 2. Observed bootstrap circularity

The accepted prerequisite Plan requires:

```text
accepted Design + accepted Plan
-> bounded Work Unit + Instruction
-> independent PRE_EXECUTION review
-> R0
-> Task 2
-> Task 3
-> Task 4
...
```

Fresh execution preflight proves current released authority cannot form the required first mutating Instruction faithfully:

1. current `.gpt-codex/schemas/instruction-envelope.schema.json` has `additionalProperties = false`;
2. it does not declare `scope_paths`;
3. current `instruction_envelope.py` can emit `scope_paths`, so such an envelope is schema-invalid;
4. current Instruction schema accepts only plain `x.y.z`;
5. the exact active Framework identity is `2.7.2+fix.1`.

Therefore R0 cannot be started through a current-valid native mutation Instruction without doing at least one forbidden thing:

- omit bounded `scope_paths`;
- emit a schema-invalid authority object;
- substitute `2.7.2` for the exact active identity;
- use candidate/future schema bytes to validate the authority that permits those same bytes to become active.

The last option is self-authorization. The first three weaken or falsify current authority.

Classification:

```text
RESULT = AMENDMENT_REQUIRED
ROOT_CAUSE = PREREQUISITE_AUTHORITY_BOOTSTRAP_CIRCULARITY
```

## 3. Design choice

Use the repository's already-established **one-time immutable bootstrap-bridge pattern**, but create a new, separately reviewed prerequisite-bootstrap instance.

Canonical identifier:

```text
PREREQUISITE_BOOTSTRAP_ID =
framework-group-b-prerequisite-bootstrap-001
```

This identifier is deliberately **not** `bridge-004` or `bridge-005`.

```text
BRIDGE_004_REUSE = FORBIDDEN
BRIDGE_005_CREATED_BY_THIS_AMENDMENT = NO
BRIDGE_005_RESERVED_FOR_POST_B0_MIGRATION = YES
NEW_AUTHORITY_SUBSYSTEM = NO
NEW_FRAMEWORK_MODULE = NO
```

The bootstrap is an instance of the previously accepted external immutable bootstrap pattern. It does not create a generic mechanism, queue, daemon, database, new Kernel State, or standing bypass.

## 4. Corrective release boundary

The prerequisite reconciliation must become an actual active Framework authority before repeated Group-B B0.

Corrective target:

```text
CORRECTIVE_BASELINE_VERSION =
2.7.2+fix.2
```

Meaning:

- `2.7.2+fix.2` is a corrective pre-Group-B active baseline;
- it does not reopen Group A feature scope;
- it does not become Group B;
- Group B remains exactly `2.7.3`;
- Group C remains exactly `2.7.4`;
- Tasks 5–9 semantics remain unchanged;
- Plugin work remains deferred.

A prerequisite implementation commit on a review branch is not sufficient. Repeated B0 is prohibited until the existing release contract verifies `2.7.2+fix.2 REMOTE_ACTIVE`.

## 5. Bootstrap authority object

Before any bootstrap mutation, a new immutable remote authorization object must be created and independently reviewed.

Its minimum closed payload contains:

```text
bootstrap_id
one_time = true
repository_id
repository_full_name
fresh_base_sha
fresh_state_revision
accepted_design_ref
accepted_plan_ref
accepted_bootstrap_amendment_ref
accepted_amended_plan_ref
candidate_branch
exact_owned_paths[]
pre_execution_review_ref
pre_execution_review_hash
executor_role = USER_LOCAL
forbidden_roles_for_bootstrap_mutation = [CODEX_IMPLEMENTER, CODEX_REVIEWER]
corrective_target_version = 2.7.2+fix.2
integration_mode = FAST_FORWARD_ONLY
expiry_condition = REMOTE_ACTIVE_2.7.2_FIX2_VERIFIED
```

The amended Plan must enumerate the exhaustive exact `exact_owned_paths` list after fresh module/owner observation. A path category, glob, directory-wide inference, or “same as Design” reference cannot substitute for the exact list.

The immutable object must be remotely reachable before execution and must receive:

```text
USER-started local independent CODEX_REVIEWER PRE_EXECUTION PASS
-> GPT adjudication
-> USER_APPROVER exact-payload approval
```

Only then may the bootstrap mutation begin.

## 6. Local execution role boundary

The user has explicitly selected local execution.

That physical choice does not change protocol roles.

Before native Instruction authority is repaired and remotely activated:

- `GPT_ORCHESTRATOR` may author Design/Plan/bootstrap packages and adjudicate returned evidence;
- a local Codex session may be used as a **mechanical preparation / testing aid** under the user's local environment;
- bootstrap mutation authority itself remains `USER_LOCAL`, matching the already-established historical bootstrap pattern;
- `CODEX_IMPLEMENTER` must not be asserted as the source of bootstrap mutation authority;
- `CODEX_REVIEWER` remains independent and read-only.

After `2.7.2+fix.2 REMOTE_ACTIVE` is verified, ordinary subsequent mutation returns to the native role chain:

```text
GPT_ORCHESTRATOR
-> local CODEX_IMPLEMENTER
-> USER-started separate local CODEX_REVIEWER
-> GPT adjudication
-> USER_APPROVER where required
```

No GitHub Cloud Codex review is used as a required gate unless USER explicitly authorizes that mode.

## 7. Bootstrap mutation sequence

The bootstrap exists only to materialize and activate the already accepted prerequisite correction.

The amended Plan must freeze a linear, no-history-rewrite sequence with these logical milestones:

```text
P0  fresh observation + exact bootstrap payload
P1  immutable bootstrap PRE_EXECUTION review + USER exact approval
P2  R0 descriptor-only ownership registration
P3  Task-2 Instruction contract + strict active-version representation
P4  Task-3 APPROVAL_RESULT + production Result consumers
P5  Task-4 Work Unit effective scope
P6  prerequisite composition + full/clean-room verification
P7  final independent cumulative implementation review
P8  USER exact final candidate acceptance
P9  fast-forward integration + 2.7.2+fix.2 publication
P10 remote-active verification + bootstrap termination
P11 repeat Group-B B0 read-only
```

Each milestone may have a distinct commit where required by the accepted Design's durable-base rules. In particular:

- R0 must be durable before any Task-2/3 test path registered by R0 is mutated;
- later commits must descend from the reviewed R0 commit;
- no rebase, amend, force push, or history replacement is permitted after a milestone is used as authority/evidence;
- each accepted Plan task retains the required local independent POST review before the next mutation task.

The bootstrap authorization object may authorize the entire **exact pre-approved path set and ordered milestone sequence** once. It cannot be expanded after approval. A later need for any unlisted path returns `AMENDMENT_REQUIRED` / `RECONCILIATION_REQUIRED`, not implicit scope growth.

## 8. Exact implementation scope classes

The Design does not itself enumerate the future exhaustive path list; the amended Plan must do so from fresh current ownership facts.

Permitted classes are limited to existing owners already named by the accepted prerequisite Design:

1. `framework-core`
   - R0 role-communication descriptor;
   - Work Unit schema/template.
2. `role-communication`
   - Instruction/Result schemas;
   - instruction builder;
   - role taxonomy;
   - result rendering;
   - Instruction/Result templates;
   - exactly the five R0-registered Task-2/3 tests.
3. `framework-validation`
   - existing project validator;
   - already-owned composed validation tests.
4. `release-projection`
   - existing publication Result consumer;
   - existing unchanged required release-projection tests.
5. existing corrective-release surfaces required by the current release contract for exactly `2.7.2+fix.2`.
6. only the minimal existing evidence/State finalization paths required by the current release contract to record the remotely verified corrective activation.

Forbidden:

- historical Task-5–9 implementation;
- `git_continuity.py` Task-5 locator implementation;
- Task-6 actual-Git mutation oracle;
- Task-7 native control-plane composition;
- Task-8 seed work;
- Task-9 production composition;
- Plugin implementation;
- bridge-005 payload/evidence;
- Group-C implementation;
- unrelated cleanup/refactor.

If fresh ownership observation requires any production owner not justified by these accepted prerequisite semantics, execution stops for amendment rather than expanding this list informally.

## 9. Review and evidence boundaries

### 9.1 Pre-bootstrap review

A fresh local independent `CODEX_REVIEWER` reviews:

- exact immutable bootstrap payload;
- fresh base SHA;
- fresh State revision;
- exact path list;
- accepted artifact refs;
- ordered milestones;
- corrective target `2.7.2+fix.2`;
- no bridge-005 overlap;
- no Task-5–9 or Plugin scope.

### 9.2 Milestone POST reviews

After every mutation milestone required by the accepted Plan, USER starts a separate local independent Reviewer session against the exact milestone commit.

Reviewer PASS is evidence only. It is never mutation authority or USER acceptance.

### 9.3 Final cumulative review

Before integration/publication, a fresh local independent Reviewer must inspect the complete cumulative implementation diff from the frozen bootstrap base to the exact final corrective candidate.

The final review must prove:

- all prerequisite tests/validators and sensitivity oracles pass;
- only exact approved paths changed;
- no Task-5–9, bridge-005, Plugin, or Group-C work entered the candidate;
- release surfaces consistently identify `2.7.2+fix.2`;
- no mutation occurred after the reviewed final SHA.

### 9.4 User final acceptance

Final candidate acceptance binds the exact reviewed candidate SHA. It does not accept “latest branch HEAD”.

## 10. Integration, publication, and activation

After final local review PASS, GPT adjudication, and USER exact final-candidate acceptance, the bootstrap's already-approved publication phase may perform only the existing release contract's required actions.

Requirements:

- integration to `main` is fast-forward-only to the exact reviewed and USER-accepted SHA;
- no merge commit, rebase, cherry-pick substitution, amend, or force push;
- annotated/immutable release tag for `v2.7.2+fix.2` points at that exact active SHA as required by current release conventions;
- canonical artifact/sidecar/record values correspond to the exact reviewed candidate;
- remote verification proves `refs/heads/main`, tag target, release record/artifact, VERSION, and State continuity facts agree as required by the current release contract;
- a tracked mutation after final review invalidates acceptance and requires a new final candidate/review.

Only successful remote verification yields:

```text
2.7.2+fix.2 REMOTE_ACTIVE
```

## 11. Bootstrap expiry

The bootstrap is one-use.

It terminates only after tool-observed remote-active verification succeeds.

After termination it cannot:

- authorize a second corrective mutation;
- create another Work Unit;
- mutate State;
- authorize B1;
- substitute for bridge-005;
- authorize Task 5–9;
- authorize Plugin or Group C;
- publish another release.

Any failed/mismatched activation leaves the bootstrap non-reusable; recovery requires explicit reconciliation, not replay or widening.

## 12. Repeated B0 boundary

Only after `2.7.2+fix.2 REMOTE_ACTIVE` may Group-B B0 run again.

Repeated B0 remains read-only and must compare immutable historical Tasks 5–9 against the then-current active owners.

```text
B0 PASS
!=
B1 AUTHORITY
```

If B0 passes, GPT freshly determines whether the separately reserved migration authority still requires bridge-005/current successor mechanism.

If bridge-005 is still required, it receives its own later lifecycle:

```text
fresh active 2.7.2+fix.2 facts
-> exact B1 migration payload/scope
-> local independent PRE_EXECUTION review
-> GPT adjudication
-> USER exact approval
-> immutable remote verification
-> separate B1 Work Unit / Instruction
-> B1
```

Nothing in this bootstrap amendment creates, pre-approves, or consumes that object.

## 13. Failure handling

Return `RECONCILIATION_REQUIRED` or `AMENDMENT_REQUIRED` as appropriate and perform no further mutation when any of the following occurs:

- base or State revision drifts before bootstrap execution;
- accepted artifact ref cannot resolve;
- bootstrap authorization object is not remotely immutable/reachable;
- exact path set changes;
- module ownership/routing changes materially;
- milestone commit is rewritten after review;
- R0 is not durable before dependent test mutation;
- required RED/GREEN/sensitivity evidence is missing;
- final candidate contains unapproved paths;
- final review or USER acceptance targets another SHA;
- main cannot fast-forward exactly;
- release/tag/artifact/version facts disagree;
- remote-active verification fails.

No implicit retry, role substitution, scope inference, or branch-name authority is allowed.

## 14. Amendment lifecycle

This amendment follows the existing Design lifecycle:

```text
Design amendment candidate
-> USER starts fresh local independent CODEX_REVIEWER
-> GPT adjudication
-> USER exact amendment acceptance
-> immutable accepted amendment ref
-> Plan amendment candidate
-> USER starts fresh local independent CODEX_REVIEWER
-> GPT adjudication
-> USER exact amended-Plan acceptance
-> immutable accepted amended-Plan ref
-> bootstrap authorization payload
-> local independent PRE_EXECUTION review
-> GPT adjudication
-> USER exact bootstrap approval
-> USER_LOCAL bootstrap execution
```

GPT does not execute implementation. The user's local environment performs execution.

## 15. Acceptance criteria

This amendment is acceptable only if independent review confirms:

1. the observed circularity is real under current `2.7.2+fix.1` authority;
2. the solution reuses the historical one-time immutable bootstrap pattern rather than inventing a new subsystem;
3. bootstrap id is distinct from bridge-004 and bridge-005;
4. `2.7.2+fix.2` is only a corrective active baseline and does not move Group B from `2.7.3`;
5. exact bootstrap scope is frozen later in the amended Plan/payload and cannot expand;
6. R0 becomes durable before Task-2/3 test mutation;
7. bootstrap mutation authority is `USER_LOCAL`, not falsely attributed to unavailable native `CODEX_IMPLEMENTER` authority;
8. local Codex Reviewer sessions remain independent/read-only and user-started;
9. final activation is exact-SHA, fast-forward-only, remotely verified, and no post-review tracked mutation is allowed;
10. bootstrap terminates after `2.7.2+fix.2 REMOTE_ACTIVE`;
11. bootstrap cannot authorize B1 or substitute for bridge-005;
12. Tasks 5–9 semantics, Plugin deferral, Group B `2.7.3`, and Group C `2.7.4` remain unchanged;
13. repeated B0 remains non-authorizing.

## 16. Candidate self-review

- Root cause addressed: YES; the amendment solves the pre-native authority circularity rather than bypassing it.
- Historical bootstrap pattern reused: YES.
- New generic authority mechanism: NO.
- Accepted Design/Plan rewritten: NO.
- bridge-004 reused: NO.
- bridge-005 created/prepared: NO.
- Tasks 5–9 semantics changed: NO.
- Group B version changed: NO.
- Plugin resumed: NO.
- GPT implementation activity authorized: NO.
- Native CODEX_IMPLEMENTER authority falsely assumed before fix.2: NO.
- Local execution responsibility preserved: YES; execution remains in USER's local environment.
- Implementation authority granted by this document: NO.
