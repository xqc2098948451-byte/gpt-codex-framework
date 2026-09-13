# GPT–Codex Framework — Framework–Project Separation Design

## Status and decision

- Status: DESIGN CANDIDATE for P0-3 review.
- Baseline: Framework v2.5.0 at `9d09c69eec0a9fe6ae3eac0ad4e73934e3a3dc88`.
- Approved approach: Approach A — an identity-context-centered separation contract.
- Primary module: `identity-context`.
- No eighth Framework module is introduced.
- This document defines interfaces and invariants only. It does not implement schemas, scripts, runtime behavior, or the P0-4 mechanism.

## Context

The v2.5.0 Framework is a governed source that publishes a Kernel, Built-ins, contracts, release metadata, and management tooling. A governed Project consumes that source from a project-local Framework root while retaining its own `CONTROL.json`, `STATE.json`, Work Units, Result/Evidence, repository binding, Project Map, Resume data, and extensions.

The v2.5.0 Framework Module Registry already separates structural responsibility, ownership, and dependency. The Registry is a Framework-management description of what belongs where. It is not an execution authority. Existing project-context binding, GitHub repository binding, Git continuity, role communication, consumer projection, and Project Map contracts must remain compatible with that boundary.

## Problem

Without one explicit separation contract, a Framework update can be mistaken for a project decision, a Framework metadata identity can be copied into a consumer project, or a stale derived navigation artifact can be treated as authoritative. The same ambiguity can allow a Result, Work Unit, repository, or instruction from another project to enter the current project context.

P0-3 must make these boundaries mechanically testable while leaving the centralized evolution mechanism to P0-4.

## Goals

1. Define the authority of every relevant Framework and Project artifact.
2. Define a stable identity tuple and the identity contradictions that fail closed.
3. Keep ordinary consumer projects separate from the Framework-management/self-hosting project.
4. Make Framework compatibility evaluation, Project adoption, migration, and mutation distinct operations.
5. Preserve current context binding, repository binding, Git continuity, Project Map, Role Protocol, consumer projection, and v2.5.0 Registry behavior.
6. Define bounded failure vocabulary and a future validation surface.

## Non-Goals

This design does not implement or pre-decide:

- the P0-4 Project Isolation / Centralized Evolution architecture;
- a central service, Registry service, sync daemon, multi-repository orchestrator, writable shared state, or automatic propagation topology;
- P0-5 execution-slot continuity or P0-6 execution telemetry;
- P1 Agent Budget, Capability & Permission, or State Machine redesign;
- automatic project upgrades, automatic project mutation, or automatic project-local extension replacement;
- a new Framework module;
- Registry-based execution authority;
- release, publication, or Framework release-state changes.

## Existing v2.5.0 Constraints

The following contracts are frozen inputs to this design:

- `KERNEL_VERSION = 2.0.0` and schema generation is `1`.
- Framework source publishes; the Project decides.
- Project root is `AUTHORITATIVE`; the Framework root is auxiliary governed source.
- `CONTROL.json` is project governance configuration; `STATE.json` is project machine state.
- `project_context_id` is required for current context binding, and mismatches are denied or quarantined according to the existing context contract.
- `CONTROL.github.repository_id` is the durable repository binding. Repository full name is not a silent substitute for that stronger identifier.
- Project Map has authority `DERIVED_NAVIGATION_INDEX`; Resume is a derived continuity aid.
- The seven-module `FRAMEWORK_MODULE_REGISTRY` describes responsibility, ownership, and dependency. Its `PERMISSIONS` field does not grant execution authority.
- Consumer projection excludes Framework-management identities, release tooling, Registry internals, and management evidence from ordinary consumer runtime.
- Role, action, project binding, state revision, and evidence fields are authoritative; human transport labels are not a replacement for them.

## Approved Approach

Approach A puts the separation boundary in the existing `identity-context` responsibility. It introduces no new runtime authority. `identity-context` produces the project/repository identity and contamination decisions consumed by the existing validation, navigation, continuity, role, and projection contracts.

The boundary is evaluated in this order:

```text
observe current Project root and Framework root
        ↓
bind and validate Project identity and repository identity
        ↓
evaluate Framework compatibility as read-only information
        ↓
require an explicit Project Work Unit / authority decision for adoption
        ↓
perform any separately authorized Project mutation locally
```

The Framework may publish a version, contract, capability, migration note, or compatibility input. None of those facts changes Project state by itself.

## Authority Model

| Surface | Authority classification | Normative rule |
|---|---|---|
| Project `CONTROL.json` | Project-local authoritative governance state | Defines project identity, repository binding, governance profile, enabled extensions, and permissions. Framework metadata cannot overwrite it. |
| Project `STATE.json` | Project-local authoritative machine state | Defines revision, state, blockers, active Work Unit, evidence references, and continuity. Framework reads it through the Project boundary and does not replace it. |
| Work Unit | Project-local authoritative unit of authorized work | Defines scope, role, action, target, and expected state revision. Framework publication does not create or replace a Project Work Unit. |
| Result / Evidence | Project-local authoritative record of an evaluated or executed action | Origin, project binding, repository binding, revision, and evidence are checked before use. A Framework release record is not a Project Result. |
| `project_id` | Stable logical Project identity | Must be read from the authoritative Project `CONTROL.json`; it is not inferred from a Framework repository or Project Map. |
| `project_context_id` | Stable bound context identity for one Project context | Must match the active Project context for instructions and returns. It is not replaceable by a project name or repository full name. |
| Repository binding | Project-local binding to an external repository | `repository_id` is the strong stable identifier. `repository_full_name` and `default_branch` are checked metadata; contradictions fail closed. |
| Project-local extensions/configuration | Project-owned authoritative inputs | Skills, guardrails, fitness, templates, and local configuration remain local. Framework comparison may report, but cannot silently enable, disable, replace, delete, or promote them. |
| Project root | Authoritative source for Project work | Project-local `CONTROL`, `STATE`, Work Units, Result/Evidence, and extensions are read and mutated only under Project authority. |
| Framework root | Auxiliary governed source | Supplies read-only Framework contracts, Built-ins, compatibility inputs, and release information to the Project. |
| Framework release metadata | Framework-management record | Describes what Framework version was published and verified. It does not decide Project adoption or mutation. |
| Framework Module Registry | Framework responsibility/ownership/dependency metadata | Describes WHAT belongs where. It does not decide WHO may execute, approve, adopt, mutate, or publish. |
| Project Map | `DERIVED_NAVIGATION_INDEX` | Locates Project assets and candidate module maps. It cannot override identity, repository binding, adoption, execution, or version authority. |
| Resume / continuity cache | Derived continuity aid | Helps resume known context and freshness checks. It cannot override `CONTROL`, `STATE`, Work Unit, Result/Evidence, or identity decisions. |

The governing rule is:

```text
CONTROL / STATE / Work Unit / Result / Evidence = Project-local authority
Framework Registry = Framework responsibility / ownership / dependency metadata
Project Map = DERIVED_NAVIGATION_INDEX
Resume = derived continuity aid
```

## Identity Model

The separation contract evaluates the following identity surfaces together; no weaker display field silently substitutes for a stronger identity field.

| Surface | Classification | Relationship and rule |
|---|---|---|
| `project_id` | Stable logical identity | Identifies the governed Project in its authoritative `CONTROL.json`. A mismatch is a Project identity conflict. |
| `project_context_id` | Stable context-binding identity | Identifies the active context used by instruction/return binding. It must be a canonical UUID and must match the active Project context. |
| `project_name` | Display metadata | Useful for human context only. It cannot authorize a mutation or resolve an identity conflict. |
| `github.repository_id` | Stable repository identity | Strong repository binding used by current repository validation. It must match the observed/bound repository ID. |
| `github.repository_full_name` | Repository display/binding metadata | Must not contradict the bound repository ID. Full name alone cannot replace an available repository ID. |
| `github.default_branch` | Repository metadata | Records the observed default branch; it is not the Project identity and does not authorize a push or merge. |
| Project root path | Runtime/local-only surface | Identifies where the authoritative Project files are found in the current machine. It is not copied into Framework authority or used as a portable identity. |
| Framework root path | Runtime/local-only surface | Locates the auxiliary governed Framework source. It cannot become the Project root. |
| Project Map / Resume | Derived context | May locate or resume context only after authoritative identity validation. |

The effective identity tuple is:

```text
(project_id, project_context_id, repository_id,
 repository_full_name when present, project_root authority)
```

`project_name`, `default_branch`, Framework version, Project Map, and Resume can enrich the tuple but cannot replace its authoritative components. A missing optional display or derived field is distinct from an identity mismatch. A missing required identity field produces the existing bootstrap/invalid-identity outcome and never authorizes mutation.

## Framework–Project Boundary

The Framework can publish:

- versioned Kernel, Built-ins, schemas, and governance contracts;
- compatibility and migration information;
- capability availability and release metadata;
- read-only evaluation inputs.

The Project remains the decision and mutation boundary. Framework publication cannot:

- adopt a Framework version for a Project;
- overwrite `CONTROL.json`, `STATE.json`, Work Units, Result/Evidence, or repository binding;
- replace Project-local extensions or configuration;
- change role execution authority, approval, or state revision;
- promote a Project-local configuration to Framework authority.

The fixed Framework source folder may be replaced as an auxiliary source only through a separately authorized Project operation. Such replacement is not adoption and does not mutate Project-local authority.

## Management/Self-Hosting Exception

The Framework-management repository is an explicit management context using `FRAMEWORK_MANAGEMENT` / `SELF_MANAGED`. That profile is not inherited by ordinary consumer Projects and is not inferred from the presence of Framework files.

Only the explicit management context may own Framework release metadata, release tooling, Registry internals, publication evidence, and self-managed Framework authority. An ordinary consumer Project must never receive or treat the management Project's `project_id`, `project_context_id`, `repository_id`, management-only assets, publication authority, or self-hosting profile as its own.

The exception narrows the management boundary; it does not grant management authority to consumers and does not make the Registry an execution authority.

## Upgrade/Adoption Model

Framework upgrade and Project adoption are separate lifecycles:

1. Framework publishes version `N` and its release/compatibility metadata.
2. The Project performs a read-only compatibility evaluation against its authoritative `CONTROL`, local extensions, state, and current Framework source.
3. The evaluation returns one of the existing bounded outcomes: `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`.
4. The Project explicitly decides whether to adopt, using a Project-authorized Work Unit and Role Protocol action.
5. A separately authorized Project mutation performs adoption or migration, records the new revision and evidence, and preserves local authority.

An evaluation result is information, not mutation authority. There is no “latest version wins” rule, automatic propagation, silent Framework replacement, or automatic local extension replacement. A customized local Built-in remains Project-owned; comparison may report a normalized delta or conflict without rewriting it.

## Registry Boundary

The v2.5.0 `FRAMEWORK_MODULE_REGISTRY` may answer:

- which Framework module owns an asset;
- which responsibility belongs to a module;
- which contracts connect Framework modules;
- which tests apply to a Framework change.

It may not answer:

- whether a Project adopts a release;
- who may mutate a Project;
- whether publication is authorized;
- whether a Role may execute an action;
- which user approval exists;
- whether Project state may be overwritten.

The exact boundary is:

```text
Registry describes WHAT.
Kernel / CONTROL / Work Unit / Role Protocol govern WHO may do WHAT.
```

If a requested Framework route does not match the Registry's exact responsibility contract, routing fails with `MODULE_ROUTE_UNRESOLVED`; no alternate module is guessed and no Project authority is inferred.

## Project Map Boundary

Project Map remains `DERIVED_NAVIGATION_INDEX`. It may locate `CONTROL`, `STATE`, Work Units, module maps, and continuity artifacts after identity binding. It cannot become Project identity authority, repository authority, adoption authority, execution authority, or Framework version authority.

Stale navigation is classified separately using existing navigation outcomes such as `MAP_MISSING`, `MAP_MISS`, or `MAP_PARTIAL`. A stale or missing Map can require bounded discovery or reconciliation, but it cannot permit cross-project mutation. Resume is similarly derived and cannot override authoritative Project state.

## Cross-Project Contamination

The identity-context boundary evaluates every instruction, return, state reference, Work Unit, Result/Evidence item, repository observation, and local artifact against the current authoritative Project tuple.

| Contamination fact | Required outcome |
|---|---|
| `project_context_id` mismatch | `CROSS_PROJECT_CONTEXT_MISMATCH`; quarantine/deny mutation and preserve the current Project context. Analysis-only inspection may report the mismatch without execution. |
| `repository_id` mismatch | `GITHUB_REPOSITORY_MISMATCH`; deny repository-bound action and quarantine the packet. |
| Contradictory repository full name | `GITHUB_REPOSITORY_MISMATCH` or `PROJECT_IDENTITY_INVALID`, depending on whether the contradiction is repository observation or malformed Project identity; never substitute the full name. |
| `project_id` mismatch | `PROJECT_IDENTITY_INVALID`; reject the foreign Project state or artifact. |
| Framework-management identity in an ordinary consumer | `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`; reject the management identity and preserve the consumer boundary. |
| Wrong Project-local `CONTROL` / `STATE` root | `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`; do not use Framework or foreign Project metadata as a fallback. |
| Result/Evidence from another context or repository | Reuse `CROSS_PROJECT_CONTEXT_MISMATCH` or `GITHUB_REPOSITORY_MISMATCH` as applicable; quarantine evidence and require reconciliation. |
| Work Unit bound to another Project | `CROSS_PROJECT_CONTEXT_MISMATCH` or `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`; do not execute it in the current Project. |
| Framework adoption without an authorized Project action | `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`; report the evaluation and leave Project state unchanged. |
| No exact Framework module responsibility/ownership route | `MODULE_ROUTE_UNRESOLVED`; stop routing and request explicit review. |

These outcomes are distinct from:

- missing optional context, which can produce a bounded `BOOTSTRAP_REQUIRED` or read-only result;
- stale derived navigation, which produces `MAP_*` outcomes and may require reconciliation;
- stale authoritative state revision, which uses the existing `STALE_INSTRUCTION` / `STALE_STATE_REVISION` semantics.

No contamination response performs destructive rollback. Reconciliation or an explicit GPT/User decision is required before a denied identity or repository action can be retried.

## Module Routing

`identity-context` is the sole primary module because “project and repository identity” is an exact match for its v2.5.0 responsibility. The expected cross-module status is `EXPECTED`; affected modules are consumers of the boundary, not co-primary owners.

| Module | Why affected | Boundary retained |
|---|---|---|
| `identity-context` | Owns Project/repository binding and cross-project isolation. | Produces the authoritative identity and contamination decisions. |
| `framework-core` | Defines Kernel authority, read-only Framework source rules, and baseline invariants. | Supplies global governance constraints; it does not own Project state. |
| `framework-validation` | Must validate identity tuple consistency, authority boundaries, adoption authorization, and management/consumer separation. | Reports bounded validation outcomes; it does not mutate Projects. |
| `navigation-continuity` | Project Map and Resume must remain derived and identity-bound. | Locates and resumes context only after authoritative identity checks. |
| `git-continuity` | Git remote/ref verification and W/P publication facts depend on the bound repository and Project state revision. | Verifies repository continuity; it does not redefine Project identity. |
| `role-communication` | Instruction/Result roles and authorized actions must carry the current Project identity and cannot override it. | Role Protocol determines WHO may act; identity-context determines WHICH Project is bound. |
| `release-projection` | Consumer projection must exclude management identity, Registry internals, release tooling, and publication evidence. | Projects receive the consumer-safe projection; release metadata remains management-only. |

No additional module is inferred. A route that cannot be resolved through the exact Registry responsibility/ownership contract fails closed as `MODULE_ROUTE_UNRESOLVED`.

## Contracts

### `PROJECT_IDENTITY_CONTRACT`

- Producer: `identity-context`.
- Consumers: `framework-validation`, `role-communication`, `navigation-continuity`, `git-continuity`.
- Purpose: establish the current Project identity and repository binding before any state read, return acceptance, repository action, or mutation.
- Inputs: authoritative Project `CONTROL.json`; active `project_context_id`; `project_id`; repository observations; Project root and Framework root locations; optional Map/Resume references.
- Outputs: validated identity tuple, repository-binding decision, and explicit identity/repository failure classification.
- Failure semantics: invalid or contradictory identity denies or quarantines the action; missing required identity requests bootstrap; missing optional derived context does not become an identity match.
- Authority semantics: the Project `CONTROL.json` and observed repository binding are authoritative; Framework metadata, Map, Resume, and display names are advisory inputs.
- Compatibility: existing valid v2.5.0 Projects continue to use their current fields without reinterpretation.

### `PROJECT_AUTHORITY_BOUNDARY_CONTRACT`

- Producer: `identity-context`, constrained by `framework-core` authority rules.
- Consumers: `framework-validation`, `release-projection`, `role-communication`, and future adoption/migration work.
- Purpose: distinguish read-only Framework reference from Project-local authority and mutation.
- Inputs: source root classification, Project identity decision, requested operation, Work Unit/Role authorization, and current state revision.
- Outputs: `READ_ONLY_REFERENCE`, `PROJECT_MUTATION_AUTHORIZED`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, or `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`.
- Failure semantics: Framework-originated or unauthorized Project mutation is denied; state remains unchanged and evidence records the reason.
- Authority semantics: a Framework release or Registry entry cannot grant mutation authority. Kernel, `CONTROL`, Work Unit, Role Protocol, and state revision remain authoritative.
- Compatibility: existing read-only Framework source use remains valid; adoption requires explicit project-local authorization.

### `FRAMEWORK_COMPATIBILITY_EVALUATION`

- Producer: `framework-validation`, using the identity result from `identity-context`.
- Consumer: the current Project's GPT/Codex governance flow and an explicitly authorized adoption Work Unit.
- Purpose: compare a published Framework against the current Project without mutating it.
- Inputs: Framework version/contracts/capabilities, current Project `CONTROL` and extension snapshot, current Framework source facts, and repository/context identity.
- Outputs: exactly one bounded evaluation outcome: `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`, with evidence and affected local surfaces.
- Failure semantics: identity conflict or inconsistent input produces a conflict/reconciliation result; the evaluation never writes Project state.
- Authority semantics: the output is advisory decision input, not adoption or execution permission.
- Compatibility: absent optional evaluation metadata uses the existing v2.5.0 fields and yields a bounded read-only result; it does not reinterpret existing identity.

### `CONTEXT_CONTAMINATION_DECISION`

- Producer: `identity-context`.
- Consumers: `role-communication`, `git-continuity`, `navigation-continuity`, `framework-validation`, and `release-projection`.
- Purpose: classify whether an instruction, return, artifact, repository, or state reference belongs to the current Project.
- Inputs: identity tuple, envelope origin/target fields, repository binding, authoritative root, and optional derived source.
- Outputs: allow, analysis-only, quarantine, deny, bootstrap, or reconciliation decision with an exact failure vocabulary.
- Failure semantics: mismatch fails closed; no foreign state is merged into current state and no destructive rollback is performed.
- Authority semantics: authoritative Project identity wins over all derived or Framework metadata.
- Compatibility: reuses existing `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, bootstrap, and stale-revision outcomes.

### Existing contract interactions

- Repository binding continues to use `repository_id` as the strong identity and rejects contradictions.
- Project-context binding continues to require matching context IDs and state revisions for executable instructions and returns.
- Git continuity continues to decide sync, ancestry, publication, and reconciliation from verified repository/ref facts; it does not authorize Project adoption.
- Role Protocol continues to determine role/action authority; identity-context supplies the bound Project, not permission to act.
- Consumer projection continues to classify exact paths and reject unknown or management-contaminated runtime content.
- Framework validation continues to validate the Registry and separation invariants without treating the Registry as an execution source.

## Invariants

1. Framework publishes; Project decides.
2. Project root is authoritative; Framework root is auxiliary governed source.
3. Project `CONTROL`, `STATE`, Work Unit, Result, and Evidence remain project-local authoritative governance state.
4. `project_id`, `project_context_id`, and repository identity cannot be silently replaced by display metadata, Map, Resume, or Framework metadata.
5. A context or repository mismatch fails closed before mutation or execution.
6. Framework compatibility evaluation never mutates Project state and never grants adoption authority.
7. Project-local extensions remain Project-owned; `Preinstalled != Enabled` remains true.
8. Framework-management/self-hosting authority is explicit and is never inherited by ordinary consumers.
9. The Registry describes WHAT; Kernel, `CONTROL`, Work Unit, and Role Protocol determine WHO may do WHAT.
10. Project Map remains `DERIVED_NAVIGATION_INDEX`, and Resume remains derived; neither overrides authoritative Project state.
11. Consumer projection contains no Framework-management identity, publication authority, or management-only runtime asset.
12. Existing valid v2.5.0 Projects remain valid without silent identity reinterpretation.

## Failure Semantics

The bounded vocabulary is:

| Failure | Trigger | Evidence and fail-closed behavior | Retry / decision |
|---|---|---|---|
| `CROSS_PROJECT_CONTEXT_MISMATCH` | Envelope, Result, Work Unit, or artifact context differs from the active Project context. | Record observed source/target context; quarantine or deny executable use; do not mutate current state. | Retry only after correct context is explicitly rebound; reconciliation is required for an attempted mutation. |
| `GITHUB_REPOSITORY_MISMATCH` | Repository ID differs, or repository metadata contradicts the bound repository. | Record bound and observed repository facts; deny repository-bound action. | Retry after repository binding is verified; no full-name substitution. |
| `PROJECT_IDENTITY_INVALID` | Missing, malformed, or contradictory authoritative Project identity. | Preserve existing authoritative files; request bootstrap or reconciliation. | GPT/User decision or explicit migration; no automatic rewrite. |
| `PROJECT_AUTHORITY_BOUNDARY_VIOLATION` | Framework/foreign source attempts to act as Project authority, or management identity enters a consumer. | Reject the operation/artifact and record the source/root classification. | Requires an explicitly authorized Project-local correction. |
| `FRAMEWORK_ADOPTION_NOT_AUTHORIZED` | Compatibility result is treated as adoption or mutation authority without a Project Work Unit/Role authorization. | Return evaluation-only result; leave `CONTROL`, `STATE`, extensions, and Work Units unchanged. | Explicit Project decision and separately authorized mutation. |
| `MODULE_ROUTE_UNRESOLVED` | Requested Framework responsibility/ownership route has zero, multiple, or mismatched exact Registry candidates. | Stop routing and report the Registry evidence; do not guess another module. | GPT review or Registry-governed future change. |

Missing optional Map/Resume data and stale derived navigation are not identity mismatches. They use existing bootstrap or `MAP_*` outcomes and may request bounded discovery/reconciliation. Stale authoritative state uses existing stale-revision failures. This distinction prevents a navigation cache from either authorizing contamination or causing an unnecessary identity rewrite.

## Consumer Projection

The separation contract preserves the existing exact-path consumer projection:

- `CONSUMER_REQUIRED`: generic Kernel, project templates, context/repository binding runtime, Project validation/runtime helpers, role protocol runtime, and other consumer-safe contracts needed by an ordinary governed Project.
- `MANAGEMENT_ONLY`: Framework Module Registry and module descriptors, Registry schemas, framework-management `STATE`, release tooling, release metadata/evidence, management tests, and management repository identity.
- `LOCAL_ONLY`: local `.gitignore` and worktree material; project-local runtime state and local configuration remain in the Project workspace rather than becoming Framework source.

Ordinary consumer runtime must not require the Framework-management Registry internals, release publication evidence, management `STATE`, release tooling, management repository identity, or self-managed Framework profile. The projection audit must continue to report zero unknown and missing paths and no management identities. P0-3 adds boundary requirements; it does not weaken projection closure.

## Compatibility / Migration

Compatibility classification for existing valid v2.5.0 consumer Projects is `NO_MIGRATION` for the separation contract. Existing `CONTROL`, `STATE`, repository binding, Project Map authority, Resume semantics, extensions, and consumer projection remain valid.

Projects lacking optional derived Map/Resume or future evaluation metadata continue through bounded bootstrap, discovery, or compatibility evaluation. They are not silently assigned new identity values. Existing `project_id`, `project_context_id`, and repository binding are preserved exactly.

If a Project still uses a versioned auxiliary Framework folder, the established one-time explicit migration to a fixed Framework source folder remains an `EXPLICIT_MIGRATION`; it is not automatic propagation and does not rewrite Project authority. A customized local extension remains local during any Framework comparison. Contradictory identity or repository facts produce `CONFLICT`/reconciliation rather than silent repair.

The Framework-management Project remains a special explicit `FRAMEWORK_MANAGEMENT` / `SELF_MANAGED` context. Its metadata is not a migration template for ordinary consumers.

## Validation Strategy

P0-3 defines tests; it does not implement them. The future validation surface must include:

1. A correctly bound Project context is accepted for a matching instruction and return.
2. A wrong `project_context_id` is rejected as `CROSS_PROJECT_CONTEXT_MISMATCH`.
3. A wrong `repository_id` is rejected as `GITHUB_REPOSITORY_MISMATCH`.
4. A contradictory repository full name is rejected without replacing the repository ID.
5. A management identity or management-only asset is rejected in an ordinary consumer projection.
6. An ordinary consumer cannot become `SELF_MANAGED` implicitly.
7. A Framework compatibility evaluation cannot mutate `CONTROL`, `STATE`, Work Units, or extensions.
8. A Registry route cannot grant execution, adoption, publication, or user approval authority.
9. Project Map and Resume remain derived and cannot override authoritative state or identity.
10. A valid existing v2.5.0 Project remains compatible with no identity rewrite.
11. Consumer projection remains closed with zero unknown/missing paths and zero management identities.
12. An unresolved exact Registry route returns `MODULE_ROUTE_UNRESOLVED` rather than guessing.
13. The authorized P0-4 interface can consume an evaluation result and explicit adoption authorization without requiring a centralized mechanism in P0-3.

## P0-4 Interface Boundary

P0-3 exposes only the interface P0-4 may later consume:

```text
Project identity and repository binding are independently authoritative.
Framework compatibility is read-only evaluation.
Adoption requires explicit Project authority.
Project mutation is separately authorized and locally evidenced.
Cross-project context cannot be mixed.
```

P0-4 may later choose how isolated Projects and centralized Framework evolution interact. P0-3 does not choose a service, synchronization, propagation, shared-state, or orchestration mechanism. Any P0-4 mechanism must preserve the above interface and invariants.

## Alternatives Rejected

### New eighth Framework module

Rejected because the v2.5.0 Registry has an exact `identity-context` responsibility for project and repository identity. A new module would fragment the existing ownership boundary and violate the no-eighth-module constraint.

### Registry as Project execution authority

Rejected because the Registry describes Framework responsibility, ownership, and dependency only. Making it decide adoption, mutation, approval, or role execution would violate the Kernel/CONTROL/Work Unit/Role Protocol authority model.

### Automatic Framework propagation

Rejected because it would allow publication facts to overwrite Project-local authority, extensions, or state without an explicit Project decision and migration action.

### Project Map as identity or adoption authority

Rejected because Map freshness is derived and can be stale. It may locate authoritative files but cannot define their identity or authorize mutation.

## Risks / Tradeoffs

- Repeating identity fields across envelopes, `CONTROL`, navigation, and evidence creates contradiction checks. The cost is intentional: stronger fail-closed isolation is preferable to guessing.
- Keeping Framework and Project metadata separate requires compatibility evaluation and explicit adoption steps. The additional step prevents silent mutation and makes governance evidence durable.
- The management/self-hosting exception requires explicit profile checks. The narrow exception is safer than generalizing management authority to every consumer.
- Derived Map/Resume can become stale and require reconciliation. Treating staleness distinctly from identity mismatch avoids both unsafe fallback and unnecessary project reset.
- Cross-module consumers must honor one identity contract. The Registry's exact route and `MODULE_ROUTE_UNRESOLVED` outcome prevent an ambiguous consumer from selecting a convenient but wrong owner.

## Open Questions

There are no blocking normative questions for P0-3. The following decisions are frozen by this design:

- primary ownership is `identity-context`;
- affected modules remain consumers of the boundary and no eighth module is added;
- Framework publication never becomes Project adoption authority;
- Project Map and Resume remain derived;
- ordinary consumers never inherit Framework-management/self-hosting authority;
- P0-4 selects its future isolation/evolution mechanism while preserving the P0-3 interface.

## Decision Summary

P0-3 adopts Approach A: `identity-context` owns the Project/repository identity and cross-project separation contract; `framework-validation`, `framework-core`, `navigation-continuity`, `git-continuity`, `role-communication`, and `release-projection` are affected consumers with explicit reasons and preserved boundaries.

The Project remains authoritative for identity, governance state, Work Units, evidence, repository binding, and local extensions. The Framework publishes governed source and compatibility information. The Registry describes Framework responsibility and ownership but grants no execution authority. Project Map and Resume remain derived. All identity, repository, management-boundary, adoption, and module-routing conflicts fail closed with bounded vocabulary. The design is additive for valid v2.5.0 Projects, defines only the interface P0-4 may consume, and excludes all implementation and future roadmap work outside P0-3.
