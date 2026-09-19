# Group B Prerequisite fix2 Finalization Work Unit Design Amendment

## 1. Status and authority

**Status:** proposed Design amendment candidate.

This document does not authorize implementation, bootstrap execution, publication, State mutation, bridge-005, B1, or merge.

It supplements, but does not rewrite, these accepted immutable artifacts:

- prerequisite reconciliation Design:
  `15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`
- prerequisite reconciliation Plan:
  `36695832aa17198b217252077bcf70c6ba77c67a:docs/superpowers/plans/2026-09-19-group-b-prerequisite-contract-reconciliation-plan.md`
- prerequisite bootstrap corrective-activation Design amendment:
  `97afda5e716dea7b53724e3d2dbede977d4a669c:docs/superpowers/specs/2026-09-19-group-b-prerequisite-bootstrap-corrective-activation-design.md`

The trigger for this amendment is the USER-started local independent Plan review of candidate `d636243b9ffa0ba2cdc1ace5f04b2e11827d092a`, whose blocking authority finding was accepted by GPT adjudication in PR #13 comment `5739680847`.

## 2. Finding

The blocked amended Plan correctly moved publication-State finalization outside bootstrap and into repaired native authority after `2.7.2+fix.2 REMOTE_ACTIVE`.

However, that later native Instruction still requires an immutable Work Unit whose effective scope covers exactly:

```text
.gpt-codex/STATE.json
.gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json
.gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json
```

No reusable current Work Unit owns exactly these paths:
- the current Group-A Work Unit does not cover the complete fix2 finalization scope;
- historical bridge/seed Work Units are revision-bound historical artifacts and are not reusable;
- creating a new Work Unit after bootstrap termination would itself require already-valid native authority.

Classification:

```text
RESULT = AMENDMENT_REQUIRED
ROOT_CAUSE = POST_ACTIVATION_NATIVE_FINALIZATION_WORK_UNIT_MISSING
```

## 3. Chosen correction

The bootstrap must create exactly one future native finalization Work Unit **after Task-4 has closed the Work Unit scope contract and before the final cumulative fix2 review**.

Canonical path:

```text
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
```

Canonical id:

```text
framework-group-b-prerequisite-fix2-finalization-001
```

This adds exactly one bootstrap mutation path.

Therefore:

```text
BOOTSTRAP_EXACT_PATH_COUNT =
32
```

The previously reviewed 31-path amended Plan candidate is stale for acceptance after this authority-scope change.

## 4. Finalization Work Unit contract

The Work Unit is a durable future native authority artifact created by the bootstrap, not a source of bootstrap authority.

Required semantic shape:

```json
{
  "kernel_version": "2.0.0",
  "schema_version": 1,
  "project_id": "PRJ-FRAMEWORK-MANAGEMENT",
  "work_unit_id": "framework-group-b-prerequisite-fix2-finalization-001",
  "goal": "Finalize tool-observed v2.7.2+fix.2 remote publication facts into repository State and durable publication evidence after corrective activation.",
  "scope": {
    "owned_paths": [
      ".gpt-codex/STATE.json",
      ".gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json",
      ".gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json"
    ],
    "excluded_paths": []
  },
  "acceptance": {
    "purpose": "V2.7.2_FIX2_PUBLICATION_STATE_FINALIZATION",
    "requirements": [
      "Record only tool-observed v2.7.2+fix.2 remote publication facts.",
      "Mutate exactly the three owned paths.",
      "Preserve B0 as the next read-only gate.",
      "Do not authorize B1, bridge-005, Plugin, release publication, or prerequisite implementation."
    ]
  },
  "selected_extensions": {
    "skills": ["github-project-continuity"],
    "guardrails": [
      "universal-safety",
      "cross-project-context-binding",
      "github-repository-binding"
    ],
    "fitness": []
  },
  "permissions": {
    "authorized_actions": [
      "READ",
      "TEST",
      "VALIDATE",
      "REPORT",
      "MUTATE_APPROVED_SCOPE"
    ],
    "forbidden_actions": [
      "PUBLISH",
      "AUTHORIZE",
      "SCOPE_EXPANSION"
    ]
  },
  "state": "AUTHORIZED",
  "basis_state_revision": "<fresh bootstrap State revision>",
  "evidence_refs": [],
  "artifact_refs": {
    "design": {
      "path": "docs/superpowers/specs/2026-09-19-group-b-prerequisite-fix2-finalization-work-unit-design-amendment.md",
      "sha": "<immutable accepted SHA for this amendment>"
    },
    "plan": {
      "path": "docs/superpowers/plans/2026-09-19-group-b-prerequisite-bootstrap-corrective-activation-plan.md",
      "sha": "<immutable accepted corrected amended-Plan SHA>"
    }
  }
}
```

The corrected amended Plan must materialize the complete shape above and may only add top-level fields if the then-active Work Unit schema requires them. Any such required field must be non-authorizing or further narrow authority; it may not add an action, path, lifecycle permission, or publication capability beyond this Design.

## 5. Exact scope semantics

The finalization Work Unit owns exactly three mutation paths and no fourth path.

It does not own its own Work Unit path.

It does not own:
- `VERSION`;
- release/tag/index/record paths;
- prerequisite implementation paths;
- any Task-5–9 implementation path;
- bridge-005;
- Plugin;
- Group C;
- another Work Unit path;
- arbitrary evidence directories.

Its `scope.excluded_paths` is exactly `[]`.

After Task-4 is implemented, this Work Unit must validate under the repaired closed Work Unit scope grammar before the fix2 candidate can reach final cumulative review.

## 6. Creation authority and ordering

The Work Unit file is created under the one-time bootstrap authority while the bootstrap is still active.

The corrected sequence is:

```text
R0
-> Task 2
-> Task 3
-> Task 4
-> validate repaired Work Unit schema
-> create finalization Work Unit
-> validate finalization Work Unit under repaired schema
-> prerequisite composition / full regression
-> prepare fix2 release surfaces
-> final cumulative review
-> USER exact final-candidate acceptance
-> fast-forward + fix2 publication
-> tool-observed 2.7.2+fix.2 REMOTE_ACTIVE
-> bootstrap TERMINATED
-> native finalization using immutable Work Unit ref
-> repeat B0
```

The Work Unit must be part of the exact reviewed fix2 candidate.

No finalization Work Unit may be created after bootstrap termination.

## 7. Bootstrap path-set amendment

The bootstrap exact path set from the corrected amended Plan must equal the previously reviewed 31 paths plus exactly:

```text
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
```

No other scope addition is authorized by this amendment.

The corrected amended Plan must explicitly prove:

```text
BOOTSTRAP_PATH_COUNT = 32
UNIQUE_BOOTSTRAP_PATH_COUNT = 32
```

Any 33rd path returns `AMENDMENT_REQUIRED`.

## 8. State-revision binding and one-use behavior

At bootstrap preparation time, the fresh current `STATE.revision` is frozen into:
- the bootstrap authority core;
- the finalization Work Unit `basis_state_revision`.

The bootstrap itself does not mutate State before or during fix2 activation.

Therefore, immediately after `2.7.2+fix.2 REMOTE_ACTIVE` and bootstrap termination, the finalization Work Unit's `basis_state_revision` must still equal current State revision.

The native finalization Instruction must use that exact current revision.

Successful finalization increments State revision once through the governed native transition. The Work Unit's fixed `basis_state_revision` then becomes stale automatically.

That staleness is the one-use expiry mechanism:

```text
FIRST VALID FINALIZATION =
possible at matching basis State revision

SECOND USE =
rejected because basis_state_revision != current State revision
```

No new explicit Work Unit state value or reuse flag is introduced.

## 9. Immutable native binding after fix2 activation

After tool-observed `2.7.2+fix.2 REMOTE_ACTIVE` and bootstrap termination, the native Instruction must bind the Work Unit by exact immutable locator:

```text
target_work_unit =
framework-group-b-prerequisite-fix2-finalization-001

target_work_unit_ref.path =
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json

target_work_unit_ref.sha =
FIX2_CANDIDATE_SHA
```

The Work Unit must resolve byte-identically at:

```text
FIX2_CANDIDATE_SHA:
.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json
```

A branch name, current HEAD, tag name, or conversation memory cannot replace that immutable ref.

## 10. Native P11 authority chain

Once fix2 is active, native finalization follows the repaired authority lifecycle.

Required chain:

```text
fresh current main / State observation
-> exact finalization Work Unit immutable ref
-> native EXECUTION_INSTRUCTION
-> exact scope_paths = the Work Unit's three owned paths
-> expected_state_revision = Work Unit basis_state_revision = current State revision
-> USER starts fresh local independent CODEX_REVIEWER PRE_EXECUTION
-> GPT adjudication
-> USER approval when the active native lifecycle requires it
-> local CODEX_IMPLEMENTER executes
-> fresh separate local CODEX_REVIEWER POST_EXECUTION
-> GPT adjudication
-> USER exact finalization candidate acceptance
-> fast-forward main
```

The finalization Instruction cannot mutate the Work Unit itself.

## 11. Finalization contents

The three-path native mutation records only already-observed remote facts.

### Remote publication verification evidence

`.gpt-codex/evidence/V2.7.2-FIX2-REMOTE-PUBLICATION-VERIFICATION.json` records tool-observed:
- repository identity;
- remote main at `FIX2_CANDIDATE_SHA` at the time fix2 was activated;
- annotated tag object SHA;
- tag target `FIX2_CANDIDATE_SHA`;
- published release identity;
- remote `VERSION = 2.7.2+fix.2`;
- artifact SHA-256 and size;
- PASS verification matrix.

### Publication Result

`.gpt-codex/evidence/results/RESULT-V2.7.2-FIX2-PUBLICATION.json` records a production-shaped publication Result consistent with current publication authority semantics.

### State

`.gpt-codex/STATE.json`:
- increments revision exactly once;
- appends the two fix2 evidence refs;
- sets `continuity.latest_verified_remote_sha = FIX2_CANDIDATE_SHA`;
- sets `continuity.latest_synced_state_revision` to the new revision;
- sets `continuity.last_verified_result_ref` to the fix2 publication Result path;
- preserves `continuity.sync_status = SYNCED`;
- sets `next_action = GROUP_B_PRE_EXECUTION_REOBSERVATION_REQUIRED`.

The finalization commit may place `main` one commit ahead of the release tag, as in the current fix.1 finalization pattern. The active Framework release SHA remains the verified fix2 tag target.

## 12. Non-goals

This amendment does not:
- authorize bootstrap execution;
- authorize native finalization execution;
- create the Work Unit now;
- change Task-2/3/4 technical semantics;
- implement Task 5, 6, 7, 8, or 9;
- create or authorize bridge-005;
- resume Plugin work;
- change Group B from `2.7.3`;
- change Group C from `2.7.4`;
- add a new module, State value, authority subsystem, queue, daemon, database, workflow engine, or standing bootstrap path.

## 13. Failure handling

Stop fail-closed if:
- the finalization Work Unit is not in the exact reviewed fix2 candidate;
- its path was not in the approved 32-path bootstrap set;
- its scope differs from the exact three paths;
- its `basis_state_revision` differs from the frozen bootstrap/current pre-finalization State revision;
- its artifact refs do not resolve to accepted immutable Design/Plan artifacts;
- it does not pass the repaired Work Unit schema;
- fix2 activation changes State revision before native finalization authority is formed;
- the native Instruction targets a different Work Unit ref or scope;
- finalization attempts a fourth path;
- Work Unit reuse is attempted after State revision advances.

Use `RECONCILIATION_REQUIRED` for current-fact drift and `AMENDMENT_REQUIRED` for scope/semantic expansion.

## 14. Review binding

Independent review binds this complete amendment candidate against accepted bootstrap Design `97afda5e716dea7b53724e3d2dbede977d4a669c`.

The expected cumulative changed-path set is exactly this one Design amendment file.

Any authoring change after review creates a new exact candidate and makes the old review stale.

GitHub Cloud Codex is supplemental only unless USER explicitly authorizes it. Required review is a USER-started fresh local independent `CODEX_REVIEWER`.

## 15. Acceptance criteria

This amendment is acceptable only if independent review confirms:

1. the missing finalization Work Unit is a real native-authority blocker;
2. bootstrap creation of one future native Work Unit is the minimum valid correction;
3. the Work Unit path is exactly `.gpt-codex/work-units/framework-group-b-prerequisite-fix2-finalization-001.json`;
4. bootstrap exact path count changes only `31 -> 32`;
5. Work Unit scope is exactly the three finalization paths and excludes its own file;
6. Work Unit is created after Task-4 repairs Work Unit scope semantics and before final cumulative review;
7. `basis_state_revision` binds the fresh bootstrap State revision;
8. bootstrap performs no State mutation, so the Work Unit remains current immediately after fix2 activation;
9. successful native finalization advances State revision and thereby makes the Work Unit non-reusable;
10. native Instruction binds `FIX2_CANDIDATE_SHA:path`, not a mutable ref;
11. bootstrap terminates before native finalization execution;
12. local CODEX_IMPLEMENTER and local independent CODEX_REVIEWER remain distinct after activation;
13. no bridge-005, B1, Tasks 5–9, Plugin, or Group-C authority is added;
14. `B0 PASS != B1 AUTHORITY` remains unchanged.

## 16. Candidate self-review

- Minimum authority delta: one Work Unit path.
- Bootstrap path-count change: exactly 31 -> 32.
- New generic mechanism: NO.
- Work Unit self-owned: NO.
- State mutated during bootstrap: NO.
- Future native authority bound immutably: YES.
- One-use behavior derives from State revision: YES.
- bridge-005 changed: NO.
- Tasks 5–9 semantics changed: NO.
- Plugin resumed: NO.
- GPT implementation: NO.
- Implementation authority granted by this document: NO.
