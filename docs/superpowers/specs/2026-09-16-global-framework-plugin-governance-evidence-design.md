# Global Framework Plugin and Governance Evidence Design

## Status and governing authority

```text
USER_DIRECTION = ACCEPTED
DESIGN_STATUS = PERSISTED_FOR_USER_REVIEW
IMPLEMENTATION_AUTHORIZED = NO
PLAN_AUTHORIZED = NO
PLUGIN_IMPLEMENTATION_AUTHORIZED = NO
FRAMEWORK_RELEASE_AUTHORIZED = NO
PLUGIN_RELEASE_AUTHORIZED = NO
CURRENT_FRAMEWORK_VERSION = 2.7.0
BASE_AUTHORITY_SHA = efba38d1e72ad690fca41a8cbac3861f8ee39b7e
```

The integrated Framework at `BASE_AUTHORITY_SHA` governs this Design. These
candidate rules are not active authority and cannot govern their own
acceptance, implementation, release, activation, or validation. This document
persists the user-approved architecture only; it creates no implementation
Plan and authorizes no plugin, runtime, schema, module, or release change.

```text
Preserve capability, compress structure.
Preserve the closed loop, remove duplication.

Plugin routes.
Framework governs.
Project owns state.

No authority -> no mutation.

Current released Framework governs development of its successor.
Candidate Framework rules cannot govern their own acceptance.
Current active Plugin governs development of its successor.
Candidate Plugin cannot govern its own activation.
Project evidence informs Framework evolution but never becomes Framework authority automatically.
Framework optimization is evidence-first and user-approved.
```

## Four-layer model and ownership boundary

Authority flows downward through exactly four layers:

```text
Layer 1 — Installed Enforcement
Global GPT–Codex Framework Plugin

Layer 2 — Active Released Framework
Kernel / Built-ins / validators / compatibility

Layer 3 — Project Authority
Each project's PROJECT / CONTROL / STATE /
Work Unit / Design / Plan / Evidence

Layer 4 — Execution
GPT / Codex Implementer / Codex Reviewer / Git
```

The following are forbidden: Project mutation of active Framework authority;
execution rewriting Plugin authority; candidate Framework self-activation;
candidate Plugin self-activation; and ordinary consumer Project mutation of
Framework Kernel/Built-ins.

Each governed Project remains independent and owns its repository, project and
repository identity, `PROJECT`, `CONTROL`, `STATE`, Work Units, Design/Plan,
project Evidence, extensions, and adopted Framework version. The Plugin stores
no shared Project state; the Framework-management repository does not own
consumer Projects.

The Plugin governs only explicit Framework enrollment/project identity:

```text
ENROLLED_PROJECT -> mandatory Framework Entry Gate
UNMANAGED_REPOSITORY -> no project mutation, no feedback export, no Framework assumption
```

Bootstrap into Framework governance is explicit. The Design conceptually
distinguishes `INSTALLED_PLUGIN_VERSION`, `ACTIVE_PLUGIN_VERSION`,
`AVAILABLE_FRAMEWORK_VERSION`, `ACTIVE_RELEASED_FRAMEWORK_VERSION`, and
`PROJECT_ADOPTED_FRAMEWORK_VERSION`; it must derive rather than prematurely
add Project-state fields. A Plugin update implies neither Framework adoption,
Project migration, nor Project-state mutation. A Framework release does not
imply Project adoption.

`ACTIVE_RELEASED_FRAMEWORK_AUTHORITY` is conceptually bound to verified
released Framework identity, immutable release SHA/ref, release metadata, and
a verified release/activation fact. `ACTIVE_PLUGIN_AUTHORITY` is conceptually
bound to installed/activated released Plugin identity, immutable Plugin
source/release identity, and a verified activation fact. These are derivable
authority facts, not new Project-state or schema fields; a later Plan must
prove any added persistence is necessary.

Consequently repository `main`/`HEAD` may hold Framework `N+1` candidate while
`ACTIVE_RELEASED_FRAMEWORK_AUTHORITY` remains Framework `N`, until `N+1` is
accepted, validated, integrated, released, and activated. A Plugin candidate
source likewise does not become `ACTIVE_PLUGIN_AUTHORITY`. Marketplace or
distribution content must bind to approved released Plugin content, never an
arbitrary development `main` snapshot. This adds no release subsystem.

## Plugin V1 boundary

Plugin V1 has exactly these responsibilities:

```text
FRAMEWORK_ENTRY
PROJECT_RESUME
WORKFLOW_ROUTING
FRAMEWORK_FEEDBACK_CHECK
FRAMEWORK_FEEDBACK_EXPORT
FRAMEWORK_OPTIMIZATION_REVIEW
SELF_HOSTING_GUARD
```

It is an enforcement/routing adapter, not an eighth Framework module. It must
not implement a second `STATE`, Work Unit system, review lifecycle, Git
continuity system, project registry, database, conversation store, authority
store, or parallel governance store.

Before any governed mutation, `FRAMEWORK_ENTRY` establishes project identity,
repository identity, enrollment, adopted Framework version, active Framework
authority, installed/active Plugin compatibility, current role, current Work
Unit, repository root, physical worktree when applicable, git-dir, common-dir,
branch/ref, `HEAD`, and next authorized action. Any unresolved or conflicting
fact yields `ANALYSIS_ONLY` or `RECONCILIATION_REQUIRED`, never mutation.
Framework-management/self-hosting work receives no bypass.

### Product-surface limitation and repository-native closure

The installed Plugin is a proactive entry, resume, routing, and enforcement
adapter; it is not an unbypassable product hook and is not promised to execute
automatically in every ChatGPT window, Codex task, or product surface. The
repository-native Framework is the final fail-closed governance authority.

```text
PLUGIN_ACTIVE_AND_INVOKED
-> FRAMEWORK_ENTRY must pass before Plugin-authorized mutation

PLUGIN_NOT_INVOKED
PLUGIN_UNAVAILABLE
PLUGIN_NOT_SUPPORTED_ON_SURFACE
-> does NOT make project mutation valid
-> repository-native authority still applies
```

Repository-native protection includes applicable `KERNEL`, `AGENTS`,
`PROJECT`/`CONTROL`/`STATE`, Work Unit authority, Instruction/Result contracts,
Guardrails, validators, and Git/review authority. The Plugin reduces
orchestration escape risk; repository governance prevents escaped execution
from becoming valid governed completion. No product-level interception claim is
made.

## Resume, Work Unit continuity, and new windows

New ChatGPT and Codex sessions must not depend on conversation history. The
required recovery order is:

```text
PROJECT
-> STATE
-> CONTROL
-> active Work Unit
-> accepted Design / Plan
-> current Instruction / Result / Evidence
-> Resume / Project Map
-> relevant Git facts
```

The compact resume report includes:

```text
PROJECT_IDENTITY
ROLE
CURRENT_STAGE
CURRENT_WORK_UNIT
ACTIVE_FRAMEWORK_VERSION
AUTHORITATIVE_SHA
NEXT_AUTHORIZED_ACTION
BLOCKERS_OR_RECONCILIATION
```

Unreleased candidate rules cannot be loaded as active governance. Work Unit
continuity is not Codex conversation-turn continuity: a Work Unit may span
multiple batches/windows. Window end is not automatically `BLOCKED`, a new
Work Unit, Design, or Plan. Incomplete execution returns `INCOMPLETE` and
continues under the same valid Work Unit unless authority changed.

The user-facing resume command is:

```text
使用 GPT–Codex Framework Plugin 恢复这个项目，
从当前已激活 Framework authority 和项目仓库 durable authority
继续当前开发。
在 Entry Gate 通过前不要修改项目。
```

For Framework self-development:

```text
使用当前已发布并激活的 Framework 版本治理正在开发的下一版本。
候选版本中的新增规则在完成批准、验证、发布和激活前
不得作为当前 authority。
```

The Plugin expands either command internally into the full resume contract.

## CAP-01 — Completion Evidence

CAP-01 is a fail-closed closure contract that reuses current
Result/Evidence/Fitness contracts. `PASS` is allowed only when applicable
evidence proves:

```text
execution_state = COMPLETED
process completion known
exit code known
intended verification scope known
executed scope complete
test files / cases complete when declared
failure count known
error count known
required validators completed
```

Timeout, command-window expiration, a running process, unknown exit code,
partial output, partial test-file execution, or an unknown mandatory test
count are `INCOMPLETE`, never `PASS`, unless there is a separately proven
blocker. `BLOCKED` requires a proven blocker; `INCOMPLETE` means execution
evidence is incomplete. This adds no completion database, process telemetry
database, or new state subsystem.

## CAP-02 — Authority-bounded review and GPT adjudication

Reviewer findings are evidence, not remediation authority. Each accepted or
modified finding must bind to `ACCEPTED_AUTHORITY_BASIS`—an accepted Design
clause, accepted Plan clause, authorized Work Unit acceptance, or existing
governed contract—or `CONCRETE_REGRESSION_EVIDENCE`: failing test, failing
validator, proven capability regression, or proven governed-contract
violation.

Reviewer preference, optional refactoring, future best practice, stronger
unapproved test style, and a new criterion invented in review do not authorize
remediation by themselves. The required chain is:

```text
REVIEW_FINDING
-> GPT adjudication
-> authority/evidence binding
-> ACCEPT / REJECT / MODIFY
-> only ACCEPT/MODIFY may authorize FIX_INSTRUCTION
```

This extends/reuses `validate_review_lifecycle` and creates no second review
lifecycle. Existing runtime freshness, role-input allowlists, and review
isolation remain intact.

## Self-hosting and activation

The Framework-management repository is a governed Project. During Framework
`N+1` development, active Plugin `N` plus active released Framework `N` govern
the candidate. Candidate Framework `N+1` remains non-authoritative until
accepted, validated, integrated, released, and activated. On failure, active
Framework authority remains `N`.

### Initial Plugin bootstrap

`INITIAL_PLUGIN_BOOTSTRAP` applies only when no `ACTIVE_PLUGIN_AUTHORITY`
exists. In that state, current active released Framework plus a user-approved
Plugin Design, user-approved Plugin Plan, and the existing Framework governance
lifecycle govern Plugin V1 development:

```text
no ACTIVE_PLUGIN
-> active released Framework
+ user-approved Plugin Design
+ user-approved Plugin Plan
+ existing Framework governance lifecycle
-> govern Plugin V1
```

Plugin V1 has `NO ACTIVE ENFORCEMENT AUTHORITY` until it is accepted,
validated, integrated, released/imported, and explicitly activated. `Plugin 0`,
an implicit predecessor Plugin, and candidate Plugin authority are prohibited;
they must not be invented or assumed. This bootstrap is not circular because
the released Framework and its established lifecycle, rather than V1, are the
governing authority.

### Plugin upgrade after activation

Candidate Plugin `N+1` is developed under active Plugin `N` and active
released Framework authority; it cannot alter active enforcement until
accepted, validated, integrated, released/imported, and activated.

## Framework feedback and Project-owned evidence

Every governed Work Unit terminal event requires
`FRAMEWORK_FEEDBACK_CHECK = REQUIRED`; every governed Project closure also
requires `FRAMEWORK_FEEDBACK_CHECK = REQUIRED`. The required Work Unit terminal
events include `COMPLETE`, `BLOCKED`, `RECONCILIATION_REQUIRED`, and
user-directed termination after actual governed execution.

`INCOMPLETE` while a Work Unit continues across a runtime turn/window is not a
Work Unit terminal event and does not force a closure feedback package merely
because that window ended. If incomplete execution itself exposes observable
Framework-level failure and the current workflow explicitly records feedback,
it may still produce evidence under existing authority.

Mandatory means perform the check; mandatory does not mean manufacture
evidence. A valid check result is `NONE` or one or more normalized Framework
evidence candidates. The check concerns observable Framework-level evidence:

```text
OBSERVED_GAP
OBSERVED_FRICTION
REPEATED_WORKAROUND
VALIDATOR_FALSE_POSITIVE
ROLE_ORCHESTRATION_FAILURE
RECOVERY_FAILURE
RELEASE_OR_SYNC_FAILURE
CAPABILITY_REUSE_SUCCESS
PRESERVATION_EVIDENCE
```

Successful capabilities require evidence as well as failures. No private
reasoning is collected. Original evidence remains owned by its source Project;
the export is a normalized package, not a complete evidence store. Where
available it binds:

```text
evidence_id
source_project_id
source_repository_id
source_commit_sha
source_work_unit_id
framework_version_used
plugin_version_used
observed_at
evidence_type
observed_fact
impact
root_cause_status
workaround_summary
existing_capability_used
supporting_evidence_refs_or_hashes
preservation_evidence
```

### Sanitization, sync pending, and deduplication

Before export, the Plugin rejects or sanitizes secrets, tokens, credentials,
personal/sensitive data, unnecessary business source, unsanitized full logs,
raw prompts, conversation transcripts, private reasoning, scratchpads, and
private agent summaries. Default export is minimal observable facts plus
provenance references/hashes. If sanitization cannot be proven,
`EVIDENCE_EXPORT = DENIED`.

Publication is separate from Project completion. A complete Project with
unavailable transport has `PROJECT_CLOSURE = PASS` and
`FRAMEWORK_FEEDBACK_SYNC = SYNC_PENDING`. A durable project-owned outbox is
allowed only when existing Evidence/Harvest mechanisms support it. There is no
message queue, daemon, database, or background service; retry occurs during a
later Plugin entry/closure.

Every package has deterministic or durable `evidence_id`:

```text
same source project
+ same Work Unit
+ same source revision
+ same evidence kind/fact identity
-> same evidence identity
```

Before a GitHub PR, check already-merged inbox evidence, open evidence PRs,
and known accepted/rejected identity. Git/GitHub facts suffice; no central
registry database is introduced.

## GitHub Evidence Bridge and intake

Ordinary Projects must not write Framework `main`. The approved path is:

```text
Project
-> normalized evidence package
-> evidence branch
-> PR into Framework repository
-> Evidence Intake Review
-> merge into Framework Harvest/Feedback inbox
```

The target reuses current Harvest semantics, such as
`.gpt-codex/harvest/inbox/<project_id>/`; its final exact path follows current
repository authority. PR acceptance means `VALID EVIDENCE ACCEPTED`, not
`FRAMEWORK CHANGE APPROVED`.

Standard ChatGPT GitHub connection is read-only for repository content
workflows. ChatGPT may prepare/validate a package and inspect permitted
content, then routes write-required publication to Codex. Codex performs the
governed Git/GitHub write workflow. A future configured write-capable GitHub
app may use the same authority and provider/workspace permissions. V1 neither
requires custom MCP nor a mandatory Desktop-only MCP dependency.

Evidence Intake Review checks only schema, provenance, sanitization,
deduplication, and target namespace; it does not decide whether Framework
change is warranted. Historical evidence is append-only: a proven error gets a
linked `CORRECTION` or `RETRACTION`, not deletion. Optimization Review classifies
history as `ACTIVE_GAP`, `REPEATED_ACTIVE_GAP`,
`RESOLVED_BY_CURRENT_FRAMEWORK`, `SUPERSEDED`, `INVALIDATED`, or
`PRESERVATION_EVIDENCE`.

## Optimization approval gate

Optimization Review occurs only on explicit user request or a Plugin suggestion
that sufficient evidence exists. Suggestion alone cannot mutate Framework. It
validates accepted evidence provenance/current relevance, deduplicates, groups
root cause, compares current Framework, preserves successful capability
evidence, and presents:

```text
REQUIRED_OPTIMIZATIONS
HIGH_VALUE_OPTIMIZATIONS
OPTIONAL_OPTIMIZATIONS
ALREADY_RESOLVED
DO_NOT_CHANGE
```

Every candidate has observable evidence and minimum closure; there is no opaque
automatic scoring engine. The required evolution path is:

```text
Accumulated Evidence
-> Optimization Review
-> User approval of selected candidate
-> capability-before-Design
-> Design
-> user approval
-> Plan
-> review
-> implementation
-> verification
-> release
-> activation
```

No user approval means no Framework mutation.

## Packaging, Chinese manual, and self-hosting acceptance

The future Plugin is intended for ChatGPT and Codex where product availability
permits, and may contain skills, connected-app references, and supporting
resources. Later GitHub-hosted distribution may use the supported marketplace.
This Work Unit creates neither packaging nor plugin files,
`.agents/plugins/marketplace.json`, MCP configuration, or a plugin release.

Future implementation is incomplete without
`docs/GPT_CODEX_FRAMEWORK_PLUGIN_USER_MANUAL.zh-CN.md`. It must explain the
Plugin, installation, required GitHub connection/permissions, new Project
bootstrap, existing Project enrollment, daily development, GPT orchestration,
Codex Implementer/Reviewer workflows, finding/remediation, completion evidence,
feedback, Evidence Bridge, optimization review, Framework/Plugin upgrade, new
ChatGPT/Codex resume, `SYNC_PENDING`, `INCOMPLETE`, `BLOCKED`,
`RECONCILIATION_REQUIRED`, troubleshooting, and Framework self-hosting. It
includes copyable Chinese resume instructions for ChatGPT and Codex.

Final Plugin acceptance requires one real Framework self-development cycle in
a fresh ChatGPT window and fresh Codex task: Plugin Entry Gate,
repository-only recovery, current released Framework authority, Work Unit
continuation, Implementer execution, independent Reviewer, completion
evidence, Framework feedback capture, and normal integration. Tests alone are
insufficient and no previous chat history may be needed.

## Structural non-goals and phased delivery

This Design rejects an eighth Framework module, new database, conversation
database, central Project-state store, second state machine, agent/reviewer
registry, session manager, context server, private reasoning store, raw-prompt
archive, automatic learning, automatic Framework optimization, automatic
strategy switching, opaque scoring engine, resource/token scheduler, custom
evidence server for V1, and mandatory MCP server for V1. Framework module count
remains seven; the Plugin is external distribution/enforcement integration.

No Plan is created by this Design. A separately authorized Plan must preserve
the following order:

```text
PHASE A — Governance Hardening
- CAP-01 Completion Evidence
- CAP-02 Authority-Bounded Review / GPT Adjudication

PHASE B — Global Plugin Core
- Entry
- Resume
- Workflow routing
- Self-hosting/version guard

PHASE C — Framework Evidence Feedback
- Feedback check
- Evidence package
- sanitization
- dedupe
- outbox/sync pending
- GitHub Evidence Bridge
- intake review

PHASE D — Plugin Distribution + Chinese User Manual

PHASE E — End-to-End Self-Hosting Acceptance
```

Phase B cannot activate against an unclosed Phase A contract. Plugin
release/activation follows governed acceptance only. This specification has no
unresolved design decision required for Plan creation. Existing
`docs/superpowers/** -> DEVELOPMENT_HISTORY` projection coverage applies, so
no projection-manifest change is required.
