# GPT–Codex Framework — Role & Communication Protocol Design

## Status and decision

This document formalizes the approved P0 Role & Communication Protocol for
Framework v2.3.0. It is a design artifact only. It does not change production
behavior, Kernel files, schemas, templates, validators, release metadata, or
consumer artifacts in this Work Unit.

The design extends the existing instruction envelope, Result Envelope, Handoff
contract, AGENTS routing model, Work Unit authorization, evidence model, and
extension mechanisms. It does not introduce a second message bus, a competing
task protocol, or a role-specific exemption from governance.

Baseline:

- Framework: `2.3.0`
- Base SHA: `b1d1ba527e9867e6306218aee176820791c95ff6`
- Kernel: `2.0.0`
- Schema generation: `1`
- Existing release baseline `W`: `1c190e4cdbadf992247a188da174b116c373028d`

## 1. Problem and objectives

The current framework has transport routing (`[USER_LOCAL]`, `[CODEX]`,
`[RETURN_TO_GPT]`, and `[INFO]`), project/context identity binding, revision
checks, Work Unit permissions, and derived Handoff/return views. It does not
yet express, in one machine-checkable communication contract:

1. who issued a message;
2. which single role is authorized to execute it;
3. who receives the result;
4. which actions are allowed or forbidden for that role;
5. how an implementation, review finding, approval, and fix round are causally
   related; or
6. how a role-aware observation can later be analyzed without becoming policy.

The protocol closes those gaps while preserving these invariants:

1. Every executable instruction names exactly one authorized executor role.
2. Role selection occurs before executable action instructions are generated.
3. All Codex roles obey the same governance framework.
4. Roles differ by authority, not by exemption from governance.
5. A Reviewer identifies and verifies problems; a Reviewer does not authorize
   remediation.
6. GPT and the User decide remediation.
7. Only `CODEX_IMPLEMENTER` executes an approved fix.
8. The Reviewer re-validates the resulting revision.
9. Tactics may evolve from evidence; authority boundaries may not silently
   drift.
10. Neither Implementer nor Reviewer may promote observed tactics directly
    into Framework authority.

## 2. Existing assets reused

The protocol is a coordination layer over existing authority sources.

| Existing asset | Reuse in this design |
| --- | --- |
| `.gpt-codex/schemas/instruction-envelope.schema.json` | Remains the instruction wire contract. Existing `instruction_id`, `instruction_type`, project identity, expected revision, framework version, Work Unit, Git, and permission fields are retained and extended additively. |
| `.gpt-codex/scripts/instruction_envelope.py` | Remains the builder/renderer seam. It continues to generate the envelope first and preserve the human-facing `【执行策略】` and `【完成后是否需要批准】` declarations. |
| `.gpt-codex/schemas/result-envelope.schema.json` | Remains the machine-authoritative result contract. Role response metadata, review references, findings, and observation data are additional fields in this contract, not a second result system. |
| `.gpt-codex/scripts/result_return.py` | Continues to derive copyable GPT Return Text from one Result Envelope. Role and review fields may be rendered as additional sections without becoming authoritative. |
| Built-in `handoff` Skill and manifest | Continues to produce a compact, read-only, derived view. Handoff may project role, next executor, review round, or finding references, but must not grant authority or rewrite facts. |
| `AGENTS.md` execution routing | Existing routing labels remain the human-facing transport vocabulary. The protocol adds a machine role inside the routed envelope; `[CODEX]` alone is not a new authority source. |
| Work Unit schema/template and Kernel authority chain | Work Unit scope, selected extensions, permissions, state, basis revision, and evidence remain the upper bound for execution. An envelope can narrow this authority but cannot expand it. |
| CONTROL / required Guardrails | Project identity, enabled Guardrails, framework/project boundary, and capability selection remain authoritative for the project. |
| STATE revision and reconciliation | Stale state, stale reviewed revision, foreign context, or ambiguous project identity use the existing deny/reconciliation semantics. No protocol-specific state machine is added. |
| Evidence and `publication_contract.py` | Observed results and review evidence remain bound to project, revision, and artifact identity. Existing PASS/SYNCED/publication rules remain unchanged. |
| Extension contract | Role communication behavior can later be packaged as a Skill or Guardrail only through the existing extension lifecycle; no new extension kind is required. |

## 3. Role model and authority

The protocol defines these roles:

- `GPT_ORCHESTRATOR` — selects the executor, binds the instruction to the
  project and Work Unit, interprets evidence, and decides whether a remediation
  instruction should be issued. It does not impersonate a Codex mutation role.
- `GPT_REVIEWER` — performs an independent reasoning review of returned
  evidence and findings. It may recommend a decision, but recommendation is not
  authorization.
- `CODEX_IMPLEMENTER` — executes the authorized implementation or approved
  fix within the Work Unit scope, then reports evidence. It may mutate only
  when the envelope, Work Unit, Guardrails, and state permit it.
- `CODEX_REVIEWER` — reads, tests, validates, compares, and reports against a
  specified revision. It may not mutate the reviewed implementation, commit a
  fix, authorize a fix, push, publish, or silently expand scope.
- `USER_APPROVER` — supplies an explicit human approval when the completion
  gate or Guardrail requires it. The role does not become a machine executor
  for Codex file mutations.
- `USER_LOCAL` — performs a user-local action when the routed instruction
  explicitly requires it. It is not a substitute for `CODEX_IMPLEMENTER` in a
  Codex implementation flow.
- `INFORMATION_ONLY` — receives or emits non-executable information. It has no
  mutation authority and cannot be used to disguise an executable instruction.

The normative authority order is unchanged:

```text
Kernel bounds
  ⊇ project CONTROL / enabled Guardrails
    ⊇ Work Unit authorization
      ⊇ instruction authorized_actions
        ⊇ executor's actual actions
```

The role matrix is a protocol-level restriction, not a grant:

| Role | Default allowed actions | Always denied by this protocol |
| --- | --- | --- |
| `CODEX_IMPLEMENTER` | `READ`, `TEST`, `VALIDATE`, `REPORT`; `MUTATE_APPROVED_SCOPE` only when explicitly authorized | Actions outside Work Unit/Guardrail scope; remediation without an approved `FIX_INSTRUCTION`; silent scope expansion |
| `CODEX_REVIEWER` | `READ`, `TEST`, `VALIDATE`, `REPORT` | Mutating the reviewed implementation, committing fixes, authorizing fixes, pushing, publishing, scope expansion |
| `GPT_ORCHESTRATOR` | Route, bind, interpret, request approval, issue the next authorized message | Directly claiming Codex file mutation or treating a finding as approval |
| `GPT_REVIEWER` | Analyze evidence, verify claims, report findings/recommendations | Authorizing or executing remediation |
| `USER_APPROVER` | Approve or reject the explicitly presented remediation decision | Implicit approval through silence; changing the machine envelope invisibly |
| `USER_LOCAL` | The specifically routed local action | Unrelated local work or authority transfer by implication |
| `INFORMATION_ONLY` | Receive/display/report non-executable content | Any executable action |

An action is authorized only when all applicable sources allow it. In
particular, listing `MUTATE_APPROVED_SCOPE` in an envelope cannot override a
denying Guardrail, a stale revision, a foreign context, or a missing approval.

### 3.1 Execution assignment semantics

The protocol separates work decomposition from agent allocation:

```text
PLAN_TASK != AGENT
PLAN_TASK != FRESH_REVIEWER
```

A plan Task is a work decomposition unit. It must be independently testable
and independently traceable, but a Task boundary does not imply a new
`CODEX_IMPLEMENTER`, a fresh agent, a new `CODEX_REVIEWER`, or an independent
review cycle.

The governing invariant is:

> A plan task defines work, not agent allocation.

The default assignment is one persistent `CODEX_IMPLEMENTER` per Work Unit.
Related Tasks execute serially or in bounded batches in that same execution
context. `CODEX_REVIEWER` is assigned only at an explicit review gate, and a
re-review normally reuses the same Reviewer so that the reviewed revision and
finding context remain continuous. A fresh agent is an escalation for
isolation, expertise, failure recovery, or an explicit GPT/User decision; it
is not the default consequence of a Task boundary.

This is an execution-assignment policy, not Agent Budget. It does not define
budgets, token accounting, concurrency quotas, scheduling optimization, or
adaptive agent allocation.

### 3.2 Review-trigger semantics

Independent review is milestone/risk gated by default, not task gated.

The default independent-review triggers are:

- integrated milestone completion;
- architecture or contract change;
- release candidate;
- explicit GPT/User request; and
- risk escalation.

Starting another Task, creating another commit, or running another test cycle
is not sufficient by itself to trigger an independent review. A Task may still
be included in the next explicit gate, and a failing test or emerging risk may
escalate review immediately. The gate is determined by the Work Unit,
Guardrails, stage, milestone, and risk evidence—not by the number of Task
boundaries or commits.

### 3.3 Framework versus generic workflow precedence

The framework retains useful planning and TDD discipline, but precedence is
explicit:

> Superpowers provides planning and TDD discipline. Framework Execution Governance controls agent allocation and review cadence.

Generic workflow recommendations must not silently override Framework
execution policy. In particular, a generic recommendation to spawn an agent
per Task or review every commit is advisory only; the role assignment and
review cadence above remain the governing policy. This does not remove
planning, independent testability, red/green verification, or other useful
Superpowers practices within the authorized execution context.

## 4. Instruction envelope design

### 4.1 Canonical fields

The existing instruction envelope remains the single executable-instruction
contract. The future additive schema change should require the following for
new role-aware instructions:

| Field | Contract |
| --- | --- |
| `instruction_id` | Existing UUID. It is both the instruction ID and the protocol message ID; no second message-ID authority is introduced. |
| `issuer_role` | Exactly one role that issued the envelope. For executable Codex work this is normally `GPT_ORCHESTRATOR`; a `CODEX_REVIEWER` result is not an instruction issuer unless a separately authorized protocol action says so. |
| `executor_role` | Exactly one role. It is a scalar enum, never an array or compound value. This is the only role selected to execute the instruction. |
| `return_role` | Exactly one role or the existing return destination represented as a role. Normal Codex work returns to `GPT_ORCHESTRATOR`; a user approval request returns to `USER_APPROVER`. |
| `instruction_type` | Existing wire-level field for instruction-side types. It must be one of the instruction classes below or an explicitly registered legacy instruction alias. A separate generic `message_type` field must not be added. |
| Project binding fields | Existing `target_project_context_id`, `target_project_name`, optional GitHub repository identity, remote ref/head, and remote hint. Identity remains bound to CONTROL and repository Guardrails. |
| Work binding | Existing `target_work_unit` plus the Work Unit's scope and selected extension references where required. |
| `expected_state_revision` | Existing optimistic-concurrency precondition. A stale value yields reconciliation, never guessed execution. |
| `framework_version` | Existing adopted/evaluated framework compatibility fact. It does not grant a role or permission. |
| `authorized_actions` | New array from the finite action vocabulary. It states the maximum actions intended for this instruction and must be a subset of effective Work Unit authority. |
| `forbidden_actions` | New array of explicit denials for this instruction. It is useful for review boundaries and must not be used to remove a higher-level denial. |
| `evidence_requirements` | New structured requirement for files read/changed, tests, validation, findings, revision, and result references as applicable. It describes completion evidence, not permission. |
| `completion_gate` | Existing machine gate vocabulary (`NONE`, `GPT_DECISION`, `USER_APPROVAL`) reused at instruction time. It declares who must decide before the next state-changing step. |
| Correlation fields | New bounded references such as `in_response_to_instruction_id`, `in_response_to_result_id`, `review_target_revision`, `finding_ids`, and `fix_round`. They establish causality without creating a new task system. |

For bootstrap compatibility, existing special handling remains: an unbound
project may use `PROJECT_CONTEXT_BOOTSTRAP` with its current two-step
read-only/challenge-bound semantics. A challenge-bound bootstrap is identity
only and cannot carry a business task. Role fields may be required for the
new-format bootstrap after migration, but must not weaken the existing
challenge, replay, or project-ID checks.

### 4.2 Protocol Message Taxonomy and wire ownership

The protocol has one conceptual Protocol Message Taxonomy containing
instruction-side and result-side message classes. The taxonomy is shared for
causal tracing, but wire-level ownership is explicit and non-overlapping:

- `instruction_type` belongs to the Instruction Envelope only.
- `result_message_type` belongs to the Result Envelope only.
- A separate generic `message_type` field is not introduced.

The Instruction Envelope / `instruction_type` may contain only instruction-side
types:

- `EXECUTION_INSTRUCTION` — authorize a bounded implementation action.
  Existing `IMPLEMENTATION`/`WORK_UNIT` values remain recognized legacy
  instruction aliases.
- `REVIEW_REQUEST` — ask `CODEX_REVIEWER` to inspect a named revision and
  produce a Result Envelope.
- `FIX_INSTRUCTION` — a GPT-issued, approved remediation instruction to
  `CODEX_IMPLEMENTER`, referencing the finding, decision, target revision, and
  fix round.
- `APPROVAL_REQUEST` — request an explicit `USER_APPROVER` decision before a
  gated remediation or other gated action.
- `RECONCILIATION_REQUEST` — request resolution of stale or conflicting
  project, state, Work Unit, repository, or reviewed-revision facts. It is not
  permission to continue by guessing.
- `INFORMATION_ONLY` — non-executable information, with no mutation actions.
- `PROJECT_CONTEXT_BOOTSTRAP` — the existing governed identity/bootstrap
  instruction.
- Explicitly registered legacy instruction aliases, subject to their existing
  compatibility contracts.

The Result Envelope / `result_message_type` may contain only result-side types,
including:

- `REVIEW_RESULT` — a reviewer result stating that the requested review passed
  its checks and has no actionable finding.
- `REVIEW_FINDING` — a reviewer result describing one or more verified
  problems. It is evidence, not approval to fix.
- `IMPLEMENTATION_RESULT` — the implementation result classification, or the
  equivalent existing implementation-result classification retained by the
  adopted contract.
- Applicable protocol error/result classifications, including
  `INVALID_INSTRUCTION` and `ROLE_AUTHORITY_CONFLICT`.

Result-side types are never executable instructions. A `REVIEW_RESULT` or
`REVIEW_FINDING` can be returned as evidence in the causal conversation, but
cannot itself authorize or become a `FIX_INSTRUCTION`. A reviewer's report can
cause GPT to issue an `APPROVAL_REQUEST` or `FIX_INSTRUCTION`, but cannot issue
either on its own.

## 5. Instruction lifecycle

The lifecycle is ordered so role selection precedes executable text:

1. GPT classifies the requested outcome and selects exactly one executor role.
2. GPT resolves the project context, repository identity, Work Unit, expected
   state revision, effective permissions, completion gate, and required
   evidence.
3. GPT constructs the existing instruction envelope, including the role and
   correlation fields, then validates it before generating the copyable task
   body. Human-facing routing remains visible before the body.
4. The recipient validates identity, instruction type, executor cardinality,
   authority subset, revision, scope, and gate. Any failure stops execution.
5. The executor performs only the listed actions and records the required
   evidence. It returns a Result Envelope bound to `instruction_id`, the Work
   Unit, the project context, and the resulting revision/artifact.
6. The next action is chosen from the result and completion gate. A result is
   evidence for a decision, not an implicit instruction to mutate further.

### 5.1 Stage-specific review routing

Every design, plan, or implementation artifact is classified with the
conceptual `ARTIFACT_STAGE` value `DESIGN`, `PLAN`, or `IMPLEMENTATION`.
Stage classification selects review routing; it does not create a new Kernel
state or a new authority source.

| `ARTIFACT_STAGE` | `REMOTE_REVIEW_VISIBILITY` | `GPT_REVIEW` / technical review |
| --- | --- | --- |
| `DESIGN` | `REQUIRED` | `GPT_REVIEW = REQUIRED` |
| `PLAN` | `REQUIRED` | `GPT_REVIEW = REQUIRED` |
| `IMPLEMENTATION` | `OPTIONAL` | `TECHNICAL_REVIEW = CODEX_REVIEWER` |

The normative stage assignments are:

```text
DESIGN:
REMOTE_REVIEW_VISIBILITY = REQUIRED
GPT_REVIEW = REQUIRED

PLAN:
REMOTE_REVIEW_VISIBILITY = REQUIRED
GPT_REVIEW = REQUIRED

IMPLEMENTATION:
REMOTE_REVIEW_VISIBILITY = OPTIONAL
TECHNICAL_REVIEW = CODEX_REVIEWER
```

`DESIGN` and `PLAN` formal review means GPT reviews the exact artifact from the
designated GitHub-visible review branch. A local file that has not been
committed, pushed, and remotely verified is not ready for formal GPT review.
`IMPLEMENTATION` normally receives technical review through
`CODEX_REVIEWER`; remote GPT inspection is reserved for the explicit triggers
in section 5.4.

### 5.2 Design-stage synchronization

The design-stage synchronization contract is:

```text
CODEX_IMPLEMENTER
  → local edit
  → validation/self-review
  → git commit
  → push designated feature/review branch
  → verify remote branch HEAD
  → return repository + branch + HEAD_SHA + artifact path
  → GPT_REVIEWER reads artifact directly from GitHub
```

The design artifact is not ready for formal GPT review while it exists only
locally. A successful local commit without remote synchronization returns
`LOCAL_COMPLETE` with `SYNC_PENDING`. If the observed remote branch differs
from the expected pushed revision, the result is
`RECONCILIATION_REQUIRED`; Codex must not claim formal review visibility.

Feature/review branch push is permitted for this review-visibility purpose
when the instruction authorizes it. It remains bounded by the push authority
boundary in section 5.6.

### 5.3 Plan-stage synchronization

The same remote-review visibility contract applies to `PLAN` artifacts. A
plan must be committed, pushed to the designated review branch, and remotely
verified before GPT performs formal review. Local-only plan state is
`LOCAL_COMPLETE` / `SYNC_PENDING`; a remote branch mismatch is
`RECONCILIATION_REQUIRED`.

The plan's Tasks remain decomposition and traceability units. They do not
create per-Task agents or per-Task reviewers, and the plan's remote visibility
does not authorize implementation.

### 5.4 Implementation-stage behavior

Implementation does not require every change to be pushed for GPT inspection.
The default implementation flow remains:

```text
CODEX_IMPLEMENTER
  → implementation
  → tests/evidence
  → CODEX_REVIEWER
  → REVIEW_RESULT / REVIEW_FINDING
  → USER + GPT when decision/remediation is required
  → CODEX_IMPLEMENTER approved fix
  → CODEX_REVIEWER re-review
```

Remote GPT inspection during implementation is required only for:

- escalation;
- material architectural deviation;
- an Implementer/Reviewer dispute;
- a Critical/Important finding requiring GPT/User judgment;
- milestone or final acceptance; or
- explicit GPT/User request.

The technical Reviewer remains non-mutating regardless of whether GPT also
reviews remotely. Remote visibility is a review route, not a permission
expansion.

### 5.5 Revision-bound review

> Every GPT review of Design or Plan is bound to an exact GitHub-visible HEAD SHA.

If the artifact changes after review, the previous review is stale. Codex must
commit and push the new revision, verify the new remote branch HEAD, and GPT
must review the new HEAD. A branch name, local path, or mutable URL without an
exact SHA is insufficient review binding.

### 5.6 Git synchronization and push authority

Review artifacts use one authority path:

```text
local file
  → git commit
  → git push
  → GitHub-visible identical revision
```

The protocol explicitly rejects independent dual writes: there must not be one
local modification plus a separate GitHub file edit, and there must not be
independent local and remote authorities. The invariant is:

> Local and remote review artifacts are synchronized through Git commits, not duplicate writes.

Feature-branch push grants review visibility, not publication authority. A
DESIGN or PLAN push does not authorize merge to `main`, publish, release, tag,
or force-push. Those actions require their existing separate authorization and
Guardrail paths.

The protocol never infers an executor from the requested file, from the
presence of a finding, or from a role-like word in the task body. When the
executor is missing, plural, unknown, or not deterministically authorized, the
result is `INVALID_INSTRUCTION` and no action is executed.

## 6. Review and fix lifecycle

The required review flow is:

```text
CODEX_IMPLEMENTER
  → implementation Result Envelope
  → CODEX_REVIEWER / REVIEW_REQUEST
  → REVIEW_RESULT or REVIEW_FINDING
  → GPT_ORCHESTRATOR + USER decision
  → optional APPROVAL_REQUEST / approval
  → GPT_ORCHESTRATOR / FIX_INSTRUCTION
  → CODEX_IMPLEMENTER
  → CODEX_REVIEWER re-review
```

The causal rule for a finding is explicitly:

```text
REVIEW_FINDING
  → evidence returned to GPT/User
  → remediation decision
  → new FIX_INSTRUCTION
  → CODEX_IMPLEMENTER
```

`REVIEW_FINDING` is therefore a Result Envelope result-side type only. It
never itself becomes an executable Instruction Envelope.

The implementation result identifies the changed files, tests, evidence, base
SHA, resulting revision, and `fix_round` (zero for the initial implementation
unless the Work Unit explicitly defines another convention). The review
request identifies the exact implementation/result revision to inspect. The
reviewer must not silently inspect or report against a different revision; a
revision drift is reconciliation.

`result_message_type = REVIEW_RESULT` means the requested checks were
performed and no actionable finding remains within the requested scope.
`result_message_type = REVIEW_FINDING` identifies the problem, evidence,
severity/impact if available, and the exact reviewed revision. It may recommend
questions for GPT, but it must not contain an implicit approval, an
implementation patch, or a mutation claim. A Result Envelope is never
reinterpreted as an executable Instruction Envelope.

GPT and the User decide whether to accept, reject, defer, or refine a finding.
If a fix is approved, GPT issues a new `FIX_INSTRUCTION` with a new
`instruction_id`, a reference to the finding and approval decision, a new
expected revision, bounded authorized actions, and incremented `fix_round`.
The Implementer may then change only the approved scope. The reviewer receives
a new `REVIEW_REQUEST` for the resulting revision, even when the fix appears
small.

If a reviewer attempts mutation, commit, push, publish, authorization, or
scope expansion, the operation is stopped and returns
`ROLE_AUTHORITY_CONFLICT`. The reviewed implementation is not accepted based
on that attempt, and the conflict itself is evidence for GPT/user handling.

## 7. Validation and failure semantics

Validation is layered and fail-closed:

1. **Envelope shape:** required fields, UUID/enum/type constraints, exact
   scalar `executor_role`, valid `return_role`, supported message type, and
   correlation consistency.
2. **Identity:** target context and project name must bind to the authoritative
   CONTROL. GitHub repository identity must bind to the existing repository
   Guardrail. Ambiguous or foreign identity is never guessed.
3. **Revision:** `expected_state_revision` and any reviewed revision must still
   match the authoritative state/result being acted upon.
4. **Authority:** each authorized action must be allowed by the role matrix and
   must narrow, not expand, CONTROL, enabled Guardrails, Work Unit, and
   completion-gate authority.
5. **Scope:** the Work Unit's owned/excluded paths, selected extensions, and
   evidence requirements remain in force. `forbidden_actions` cannot be
   removed by task prose.
6. **Lifecycle:** a `FIX_INSTRUCTION` must reference a verified finding and an
   explicit GPT/user remediation decision as required; a review request must
   target a concrete result/revision; a reviewer result cannot authorize a fix.
7. **Completion:** state transitions continue through the Kernel's existing
   legal transitions and evidence rules. Role protocol fields do not permit a
   shortcut to `COMPLETE`, `PASS`, `SYNCED`, or publication authority.

Required failure mappings:

| Condition | Required outcome |
| --- | --- |
| Executable instruction has no executor, more than one executor, or an unknown executor | `INVALID_INSTRUCTION`; do not execute |
| Requested action is outside the executor's role authority or effective Work Unit authority | `ROLE_AUTHORITY_CONFLICT`; do not execute |
| `CODEX_REVIEWER` attempts unauthorized mutation or publication | `ROLE_AUTHORITY_CONFLICT`; preserve the reviewed revision and report the attempt |
| Project/context/repository identity is missing, foreign, stale, or ambiguous | Existing deny or `RECONCILIATION_REQUIRED` semantics; never guess execution |
| Expected state or reviewed revision is stale | Existing `RECONCILIATION_REQUIRED`; no overwrite |
| Required approval is absent | `AWAITING_APPROVAL`/`APPROVAL_REQUEST` according to the existing state/gate contract; no fix |
| Reviewer reports an issue | `REVIEW_FINDING`; this is evidence, not authorization |

`INVALID_INSTRUCTION` and `ROLE_AUTHORITY_CONFLICT` are protocol result
classifications. They do not add Kernel states. The durable Result Envelope
may represent the failure using the existing `FAIL` or `BLOCKED` status plus a
structured protocol error, while the copyable return preserves the existing
complete return sections.

## 8. Result Envelope and Handoff projections

The Result Envelope remains authoritative for machine facts. Proposed additive
role-aware fields are:

- `response_to_instruction_id`;
- `responder_role` and `return_role`;
- `result_message_type` (`REVIEW_RESULT`, `REVIEW_FINDING`,
  `IMPLEMENTATION_RESULT`, or an applicable protocol error/result
  classification);
- `review_target_revision`, `finding_ids`, `fix_round`, and
  `remediation_decision_ref` when applicable;
- `protocol_error` with a stable classification such as
  `INVALID_INSTRUCTION` or `ROLE_AUTHORITY_CONFLICT`; and
- optional `role_observation`, as defined in the next section.

For a `DESIGN` or `PLAN` return, the minimum derived/result contract is:

```text
REPOSITORY
ARTIFACT_STAGE
BRANCH
BASE_SHA
HEAD_SHA
ARTIFACT_PATH
PUSH_STATUS
REMOTE_VERIFICATION
DEVIATIONS
BLOCKERS
NEXT_GPT_ACTION
```

Formal GPT review is permitted only when `PUSH_STATUS = SUCCEEDED` and
`REMOTE_VERIFICATION = VERIFIED`, and the returned `HEAD_SHA` is the exact SHA
GPT reviews. `REPOSITORY` is the durable repository identity already bound by
CONTROL; `BRANCH` is the designated review branch; `ARTIFACT_PATH` is a
repository-relative path. These fields report synchronization facts and do
not grant merge or publication authority.

For `IMPLEMENTATION`, these fields remain optional unless an escalation or
explicit GPT/User request selects remote review. Existing local Result
Envelope status, evidence, Git, and completion-gate rules remain authoritative.

Existing `status`, `completion_gate`, state/revision, Git, evidence, remote
verification, and publication fields retain their current meanings and
conditionals. A role-aware field cannot make a local result a published result
or make a reviewer finding a fix authorization.

Handoff and GPT Return remain derived views. They may add:

- `ISSUER_ROLE`, `EXECUTOR_ROLE`, `RETURN_ROLE`;
- `INSTRUCTION_TYPE` and `RESULT_MESSAGE_TYPE` when the corresponding derived
  envelope is present;
- `REVIEW_TARGET_REVISION`, `FINDINGS`, and `FIX_ROUND`; and
- `NEXT_AUTHORIZED_ROLE` / `NEXT_GPT_ACTION`.

For DESIGN/PLAN handoffs, Handoff/GPT Return may render the minimum
repository/branch/HEAD/artifact/push/verification fields above, but they must
derive them from the Result Envelope and Git observations rather than inventing
them. A missing or mismatched field remains a failed review-visibility gate.

These are presentation and routing hints only. Handoff must continue to state
that CONTROL, STATE, Work Unit, Evidence, Result, source/tests, and Git/GitHub
facts are authoritative; derived role fields must not override them. Large
logs, raw telemetry, and intermediate reasoning remain evidence-on-demand,
not part of the compact return contract.

## 9. Minimal observation interface

The design exposes only a minimal role-aware observation shape for later,
data-driven improvement. It is an optional observation attached to the existing
Result/Evidence path, not a new authority source:

```json
{
  "role": "CODEX_REVIEWER",
  "instruction_id": "UUID",
  "work_unit": "WORK-001",
  "reviewed_revision": "REVISION_OR_SHA",
  "executed_revision": "REVISION_OR_SHA_OR_NONE",
  "files_read": ["relative/path"],
  "files_changed": [],
  "tests_run": ["command and outcome"],
  "findings": ["FINDING-001"],
  "fix_round": 1,
  "agent_spawns": 0,
  "result": "REVIEW_FINDING"
}
```

The fields are intentionally descriptive: role, instruction, Work Unit,
reviewed/executed revision, files read/changed, tests, findings, fix round,
agent spawns, and result. Collection must be bounded by the same project and
privacy rules as existing evidence. This Work Unit does not define scoring,
strategy classification, benchmarking, ranking, adaptive policy, or automatic
role/authority changes. Observations can inform a future design review but
cannot promote tactics to Kernel, CONTROL, Guardrails, or Work Unit authority.

## 10. Backward compatibility and migration

Compatibility is additive and staged:

1. Keep the current `instruction_type` wire field and current
   `PROJECT_CONTEXT_BOOTSTRAP` behavior. Treat `instruction_type` as the
   instruction-side type field and `result_message_type` as the Result
   Envelope's result-side type field; do not introduce a competing generic
   `message_type` field.
2. Keep all current identity, Git continuity, state revision, completion gate,
   Result status, Handoff, and GPT Return fields and semantics.
3. Continue accepting existing `[CODEX]` routing as a transport marker. A
   compatibility adapter may map it to a role only when the legacy instruction
   type and bounded context make the mapping deterministic: existing
   implementation/work-unit instructions map to `CODEX_IMPLEMENTER`, and an
   explicitly review-bound legacy instruction maps to `CODEX_REVIEWER`.
   `[CODEX]` alone never grants mutation authority.
4. If a legacy `[CODEX]` instruction cannot be mapped deterministically, return
   `INVALID_INSTRUCTION` or request reconciliation rather than guessing.
5. Preserve the Chinese execution strategy and approval declarations. They are
   human-facing routing information; the machine role and action arrays are
   the enforceable contract.
6. During migration, old envelopes may omit role fields only in an explicitly
   marked legacy compatibility mode. New role-aware message types require all
   role, action, evidence, gate, and correlation fields.
7. A project adopts the protocol through the existing compatibility scan and
   Framework upgrade evaluation. No project receives a role or permission
   merely because a Built-in exists; adoption remains explicit in CONTROL.
8. Existing consumers without role-aware fields remain valid and continue to
   use v2.3.0 routing/result behavior until they opt into the protocol. Once a
   consumer opts in, its validator requires the new fields for new-format
   messages while still accepting marked legacy messages.

This migration does not create a second role registry. The role enum, authority
matrix, and validation rules are the single protocol definition; CONTROL and
Work Units remain the single project-specific authority sources.

## 11. Consumer projection implications

When a later implementation is projected to consumers, include only generic,
consumer-safe protocol assets:

- updated instruction and Result Envelope schemas/templates;
- the role/message validation and builder/renderer behavior;
- the updated Handoff Skill/manifest and derived return projection rules;
- generic tests and migration guidance;
- any protocol Skill or Guardrail that is explicitly adopted and cataloged.

Do not project the framework-management project's CONTROL identity, STATE,
release evidence, SDD reports, branch data, or role observations containing
management-only paths or identities. The consumer projection validator and
runtime-closure tests remain the boundary. Role protocol assets must not make
the consumer depend on management-only release or publication tooling.

## 12. Testing strategy for a future implementation

The future implementation should add focused tests before implementation
changes, consistent with the repository's existing direct-file test pattern:

1. schema/template tests for every role, message type, action list, gate,
   correlation reference, and legacy alias;
2. exactly-one-executor tests for missing, scalar, array, compound, and unknown
   executor values;
3. authority-matrix tests proving reviewer mutation/commit/push/publish and
   authorization attempts return `ROLE_AUTHORITY_CONFLICT`;
4. tests proving action lists can narrow but cannot expand Work Unit,
   Guardrail, or Kernel authority;
5. identity, stale revision, foreign repository, and reconciliation tests;
6. causality tests for implementation → review → finding → approval → fix →
   re-review, including fix-round and reviewed-revision binding;
7. tests proving a `REVIEW_FINDING` never directly produces a fix and a
   Reviewer never authorizes remediation;
8. legacy `[CODEX]` compatibility tests, including ambiguous routing denial;
9. Result/Handoff tests proving the Result Envelope is the source and role
   fields in Handoff/GPT Return are derived;
10. observation-shape tests proving required fields are present while no
    scoring, ranking, or adaptive policy is performed; and
11. consumer projection/runtime-closure tests proving generic protocol assets
    are included and management identity is excluded.

The existing full suite is a baseline gate for this design branch; no new
production tests are added in this Work Unit because implementation is
explicitly out of scope.

## 13. Release, versioning, and migration implications

This design-only Work Unit does not change `VERSION`, release records, Kernel,
schema generation, or the v2.3.0 artifact. It therefore has no release claim.

If implemented as specified, the additive role/message contracts should be
planned as the next minor Framework release (for example, `2.4.0`) with an
explicit compatibility scan and migration notes. Kernel `2.0.0` and schema
generation `1` can remain the compatibility floor if the changes remain
additive, preserve existing conditionals, and keep legacy envelopes valid in
marked compatibility mode. Release metadata must record the exact consumer
projection and tests.

If implementation instead makes an existing accepted envelope invalid without
the compatibility adapter, changes the meaning of a canonical field, adds a
new Kernel state, or requires a new schema generation, implementation must stop
and report the incompatibility before editing those contracts. Such a change
would require a separately approved migration and version decision.

## 14. Why the Kernel remains unchanged

The protocol does not require a new universal execution state, a new evidence
source, a new permission rank, or a new extension kind. It can be expressed by:

- extending the existing instruction/result schemas and templates;
- validating a request-level role and action subset;
- reusing Work Unit permissions, Guardrails, revision checks, and existing
  reconciliation;
- updating the existing Handoff/return projection;
- optionally emitting a bounded observation attached to existing evidence; and
- adding a protocol Skill or Guardrail through the existing extension contract
  if repeated evidence later justifies it.

The Kernel remains the minimal governance substrate. Role communication is a
framework contract and routing concern, while project-specific permissions and
capabilities continue to live in CONTROL, Work Units, Guardrails, Skills, and
Fitness. Adding roles to Kernel would duplicate authority and violate the
Kernel exclusion test: the framework can guarantee governance correctness
without teaching Kernel every communication tactic or reviewer workflow.

## 15. Self-review and explicit non-goals

Self-review completed against the v2.3.0 contracts:

- There is one executable instruction contract, one machine Result Envelope,
  and one derived Handoff/return view; no competing message system was added.
- `instruction_id` remains the protocol message identity. `instruction_type`
  owns instruction-side types and `result_message_type` owns result-side types;
  no duplicate generic `message_type` authority exists.
- Envelope actions are a narrowing projection, not a new permission source.
- Reviewer authority is read/test/validate/report only; findings do not approve
  fixes, and GPT/user decisions precede every `FIX_INSTRUCTION`.
- Ambiguous identity and stale revisions use existing deny/reconciliation
  semantics rather than guessed execution or a new state.
- Result publication, `PASS`, `SYNCED`, `COMPLETE`, remote verification, and
  evidence rules remain intact.
- Legacy `[CODEX]` routing is preserved with deterministic mapping and
  fail-closed ambiguity handling.
- Plan Tasks are decomposition units, not agent or Reviewer allocations;
  independent review is milestone/risk gated rather than task gated.
- DESIGN and PLAN formal GPT review require an exact remotely verified branch
  HEAD; IMPLEMENTATION does not require per-change remote GPT review.
- Feature-branch push is limited to review visibility and cannot be confused
  with merge, publication, release, tag, or force-push authority.
- Telemetry is limited to the requested descriptive observation fields; there
  is no scoring, strategy intelligence, benchmark, adaptive policy, or agent
  budget.
- Consumer projection excludes management identity and development history.
- No changes are proposed to Kernel `2.0.0`, schema generation `1`, the
  Framework Module Registry, Capability & Permission Model, Framework State
  Machine, User Alignment, or unrelated v2.3 assets.

No open contradiction or unresolved authority duplication remains in this
design. The only implementation-time gate is the compatibility decision if
the additive adapter cannot preserve an existing legacy flow.
