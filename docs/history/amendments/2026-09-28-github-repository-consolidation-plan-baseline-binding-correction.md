# GitHub Repository Consolidation Plan Baseline-Binding Correction

```text
STATUS = PLAN_CORRECTION_CANDIDATE_ONLY
EXECUTION_AUTHORITY = NONE
FINDING = GC-PRE-001
DESIGN_CHANGE = NO
```

This candidate corrects one baseline-binding rule in the Rev002 Plan. It has no effect until independently reviewed, accepted, and durably integrated through the existing governance path. It does not execute GitHub Repository Consolidation Phase A.

## 1. Immutable predecessor and accepted finding

```text
PREDECESSOR_PLAN_COMMIT =
6663e46ed210ec33354e5c1c5462d34205d77ae1

PREDECESSOR_PLAN_PATH =
docs/superpowers/plans/2026-09-28-github-repository-consolidation-plan.md

PREDECESSOR_WORK_UNIT_ID =
github-repository-consolidation-ref-cleanup-ledger-001

PREDECESSOR_WORK_UNIT_REF =
5486e920828008a74aac98af47ca204fa68b97d3:
.gpt-codex/work-units/github-repository-consolidation-ref-cleanup-ledger-001.json
```

Native PRE returned `REVIEW_FINDING` with finding ID `GC-PRE-001`. The Rev002 Plan recorded its authoring-time snapshot as `main = b96e077362477ef697670ddc04f4e6c77c880271`, 364 tracked files, 90 remote heads, and 37 tags. Native PRE subsequently observed `main = 5486e920828008a74aac98af47ca204fa68b97d3`, 367 tracked files, 91 remote heads, 37 tags, one open PR, and STATE revision 18. The intervening two governance materialization commits added the Rev002 Design, Rev002 Plan, and predecessor Work Unit `-001`; they did not mutate STATE, CONTROL, source, VERSION, or release artifacts. The finding is a Plan baseline-binding contradiction, not a Phase A PASS.

## 2. The one superseded semantic rule

**OLD RULE:** Treat the Rev002 authoring-time `b96e077... / 90 heads / 364 tracked files` observation as a permanently fixed runtime baseline for future Phase A execution. Any difference triggers `CONSOLIDATION_DESIGN_PLAN_REMOTE_DRIFT` and stops, even when the difference consists solely of required governance materialization.

**CORRECTED RULE:** The Rev002 `b96e077... / 90 heads / 364 tracked files / 37 tags` values are a historical observation snapshot. They are not the future execution baseline. After all required governance artifacts have been accepted and durably integrated, and after the applicable successor Work Unit has been materialized, freshly observe the repository immediately before native PRE and canonical execution-payload formation. Bind the resulting exact main SHA, STATE revision, remote heads, tags, tracked-file count, PR identities, and other required remote facts to the exact Execution Instruction and PRE review target under the successor Work Unit's immutable ID/ref. Do not amend the successor Work Unit in place with post-materialization observations. The exact execution base is frozen at that binding, before the execution decision. Only subsequent material drift against that frozen target triggers `CONSOLIDATION_DESIGN_PLAN_REMOTE_DRIFT` or the applicable `RECONCILIATION_REQUIRED` outcome. No “latest main” substitution, automatic rebase, or recomputation may replace a frozen execution base.

The STATE rule remains exact. `basis_state_revision = 18` is valid only while the authoritative STATE still has revision 18; this correction neither changes STATE nor treats a later revision as interchangeable. A STATE mismatch requires reconciliation rather than an automatic new basis.

Freshly enumerate remote heads, tags, and tracked files for the successor Phase A attempt. The Rev002 Plan's `KEEP=1 / DELETE_SAFE=0 / REVIEW_REQUIRED=89` is the fail-closed initial classification of its old 90-head snapshot, not a fixed count for a later remote set. Recompute every actual classification count from the fresh remote set, preserving the existing per-ref proof and review rules.

```text
SEMANTIC_CORRECTION_COUNT = 1
AUTO_REBASE = NO
```

## 3. Design and Phase A invariants preserved

The Rev002 Design at `6663e46ed210ec33354e5c1c5462d34205d77ae1:docs/superpowers/specs/2026-09-28-github-repository-consolidation-design.md` already labels the `b96e077...` baseline values as observation facts rather than an execution grant. This correction removes only the Plan's contradictory treatment of that snapshot as a future runtime stop baseline.

```text
DESIGN_CHANGE = NO
```

The repository consolidation architecture, Phase A ledger goal, `DELETE_SAFE` predicates, retained-authority reachability invariant, PR #15 classification rules, authority/release/bootstrap tag retention, Codex Directory Creation Contract, phases B–G, Framework version, STATE, and CONTROL are unchanged. In particular, ancestor-of-main alone never proves `DELETE_SAFE`, unknown predicates remain `REVIEW_REQUIRED` or `KEEP`, and no ref deletion may make a current durable-authority commit unreachable from all retained remote refs.

## 4. Required successor Work Unit and fresh PRE

The predecessor `github-repository-consolidation-ref-cleanup-ledger-001` remains an immutable historical Work Unit. Do not amend it in place or reuse its failed PRE result. After this correction has been independently reviewed, accepted, durably integrated, and remotely verified, prepare a separately governed successor:

```text
WORK_UNIT_ID = github-repository-consolidation-ref-cleanup-ledger-002
PREDECESSOR_WORK_UNIT_MUTATION = NO
PREVIOUS_PRE_REUSE = NO
AUTO_REBASE = NO
```

The successor must preserve `-001`'s Phase A goal, owned and excluded scope, permissions, selected Skill and Guardrails, and acceptance semantics. It must keep `artifact_refs.design` bound to the immutable Rev002 Design ref. Its `artifact_refs.plan` must bind the future **accepted and integrated immutable ref** of this correction, which incorporates the predecessor Plan except for the one superseded rule. No candidate path or unintegrated commit is that ref.

Set `basis_state_revision = 18` only if STATE is still revision 18 when the successor is prepared. Keep `implementation_authorized = false`, `implementation_start_allowed = false`, and the next gate as native `GITHUB_CONSOLIDATION_REF_LEDGER_NATIVE_PRE`. The successor must not inherit `-001`'s PRE result or its old `expected_base_sha`. After successor materialization, freshly observe `origin/main` and form a new exact Execution Instruction and PRE target. An independent native PRE must run again against those exact bindings. A PRE `PASS`, if obtained, remains only the normal execution gate under the existing authority chain; this candidate itself does not authorize `-002` or Phase A.

## 5. Current evidence is not future execution authority

The accepted PRE observation is:

```text
CURRENT_OBSERVED_MAIN =
5486e920828008a74aac98af47ca204fa68b97d3

CURRENT_OBSERVED_STATE_REVISION = 18
CURRENT_OBSERVED_HEADS = 91
CURRENT_OBSERVED_TAGS = 37
CURRENT_OBSERVED_TRACKED_FILES = 367
CURRENT_OBSERVED_OPEN_PRS = 1
FUTURE_SUCCESSOR_EXECUTION_BASE_PREDETERMINED = NO
```

Correction acceptance and integration will change `main` again. Only after acceptance, integration, and remote verification may the successor authority be prepared from another fresh observation. These current values are evidence for `GC-PRE-001`; they are not pre-frozen values for a future successor Execution Instruction.

Other Phase A revalidation inputs from native PRE are: PR #15 was open and draft; the remote branch set had 91 heads and 37 tags; the branch-protection API reported `protected=false` for every observed branch; and `framework-staged-closure-master-plan-001` was the sole retained remote carrier of a master-plan immutable locator. While that dependency remains, and unless another retained authority ref is established, that branch cannot be `DELETE_SAFE`. All these findings require fresh verification at the successor PRE and per-ref decision gates; none is a permanent hard-coded classification.

## 6. Explicit non-authority

This candidate does not execute Phase A, produce the formal cleanup ledger, close or merge a PR, delete or create a branch or tag, modify a Work Unit, change STATE or CONTROL, or authorize `-002`. It does not permit skipping the new native PRE, treating `GC-PRE-001` as a PASS, or using a current observation as a substitute for future exact authority. Any later PR or ref mutation retains the Rev002 Design and Plan's independent review, immutable ledger locator, USER_LOCAL authority, reachability proof, and fresh per-ref revalidation requirements.

## 7. Candidate self-review

```text
semantic correction count = 1
Design semantics changed = NO
historical snapshot rewritten = NO
predecessor Plan modified in place = NO
predecessor Work Unit modified in place = NO
Phase A scope expanded = NO
DELETE_SAFE rule weakened = NO
reachability invariant weakened = NO
STATE rule changed = NO
PR/tag mutation authority added = NO
successor Work Unit required = YES
fresh PRE required = YES
```
