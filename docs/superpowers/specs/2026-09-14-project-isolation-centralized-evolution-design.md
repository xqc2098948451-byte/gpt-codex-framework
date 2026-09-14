# P0-4 Project Isolation and Centralized Evolution Design

- **Status:** Proposed design candidate
- **Work unit:** `project-isolation-centralized-evolution-design-001`
- **Baseline:** Framework `2.6.0`, commit `f49cd5afaa07aabaedac516d1c0e2c3524eef845`
- **Primary module:** `identity-context` — `project and repository identity`

## Decision

Adopt the smallest authority-preserving composition: a versioned, central **read-only Framework Evolution Source** plus an opt-in, centrally indexed **derived Project Evolution Observation**. A governed project evaluates the published source locally and decides locally. Its optional observation reports a minimized, non-authoritative fact to Framework management. No active coordinator, fleet job, batch mutation, or centrally writable project record is introduced by P0-4.

The central side is classified only as `READ_ONLY_EVOLUTION_SOURCE`, `FRAMEWORK_MANAGEMENT_METADATA`, or `DERIVED_OBSERVATION_ONLY`. It is never shared Project authority. The Project root remains authoritative; the Framework root remains an auxiliary governed source.

## Context

P0-3 separated Framework publication from Project-local authority. It established that Framework publishes while each Project decides, and that `CONTROL`, `STATE`, Work Units, Results, and Evidence are authoritative only in their Project root. P0-4 must make multiple governed Projects safely observable and independently evolvable without turning Framework metadata, a registry, a compatibility index, or a management workflow into an execution authority.

The existing Module Registry describes **what belongs where**. Kernel, `CONTROL`, Work Unit, and Role Protocol determine **who may do what**. P0-4 preserves that distinction.

## Problem, goals, and non-goals

### Goals

- Deny cross-Project use of authoritative or derived Project artifacts unless their complete strong identity binding matches.
- Permit a central Framework release/evolution source to be published and read without automatically changing any Project.
- Permit an explicitly enrolled Project to publish a privacy-minimized, derived compatibility observation for Framework-management visibility.
- Define local adoption, migration, reconciliation, staleness, rename, removal, and repository-transfer boundaries.
- Preserve current project-context binding, consumer projection, Git continuity, Project Map, Resume, Role Protocol, Registry, and v2.6.0 compatibility outcomes.

### Non-goals

- A central scheduler, daemon, agent, queue, batch, or service that changes Projects.
- A shared `CONTROL`, `STATE`, Work Unit, Result, Evidence, extension, Project Map, or Resume store.
- Automatic upgrade propagation, automatic migration, or identity-inference writes.
- A new Framework module, Registry execution authority, or consumer-projection manifest change.
- P0-5 slot lifecycle, P0-6 telemetry, and P1 agent/budget/capability/state redesign.

## Frozen P0-3 predecessor constraints

| Invariant | P0-4 consequence |
| --- | --- |
| Framework publishes; Project decides. | Publication and observation cannot authorize adoption or mutation. |
| Project root is authoritative; Framework root is auxiliary. | A central record cannot replace, repair, or overwrite a Project-local artifact. |
| `CONTROL`/`STATE`/Work Unit/Result/Evidence are Project-local. | Every read, write, and reference is identity-bound to exactly one Project root. |
| Registry describes placement, not authority. | Routing may identify `identity-context`; it cannot permit evaluation, adoption, or mutation. |
| Project Map and Resume are derived aids. | They are isolated and may be regenerated only locally after local authorization. |
| Strong identity is `project_id`, `project_context_id`, `repository_id`, and repository full name when present. | Display name, `project_name`, or repository full name alone never substitute for a binding. |
| Management/self-hosting identities do not leak. | `FRAMEWORK_MANAGEMENT` and `SELF_MANAGED` are management classifications only and are forbidden in consumer projections and ordinary Project authority fields. |

## Compared approaches

| Approach | Value | Authority and complexity cost | Decision |
| --- | --- | --- | --- |
| A. Versioned, read-only Framework Evolution Source; local evaluation and decision | Gives every Project one canonical published evolution input while retaining local control. | No Project mutation; requires only source provenance and local evaluation. | Required. |
| B. Centrally indexed, read-only Project compatibility/inventory observations | Gives management bounded fleet visibility and detects stale or conflicting enrollment. | Safe only as opt-in, minimized derived facts with no command channel. | Included as a bounded adjunct to A. |
| C. Active coordination, batch rollout, or central remediation | Could orchestrate a fleet. | Adds scheduling, execution, retry, authority delegation, and shared-state risks; unnecessary to satisfy P0-4. | Rejected and reserved for a future explicitly authorized design. |

Approach A alone does not provide an accountable view of explicitly participating Projects. Approach B alone cannot define a canonical evolution source. A+B is therefore the minimal complete boundary. C is not implied by A+B.

## Selected architecture and rationale

### Framework Evolution Source

Framework publishes a versioned `FRAMEWORK_EVOLUTION_SOURCE`: a read-only description of a Framework release, compatibility rules, migration availability, and source provenance. It is classified `READ_ONLY_EVOLUTION_SOURCE` and is Framework-managed. It may be fetched, copied, or manually made available to a Project, but it contains no Project-local authority, commands, credentials, or executable delegation.

The source has a Framework version and immutable provenance. A Project may read it only as external input, evaluate it in its own root, and produce its own compatibility outcome. Reading a source creates no enrollment, Work Unit, decision, or write.

### Project Evolution Observation

An explicitly enrolled Project may emit or make available a `PROJECT_EVOLUTION_OBSERVATION` after a local read-only evaluation. Framework management may index that observation as `DERIVED_OBSERVATION_ONLY`. The index is not a source of truth for the Project, cannot be used as an execution queue, and cannot cause any Project mutation.

An observation is limited to:

- stable `project_id`, `project_context_id`, and `repository_id`;
- repository full name only as an optional display/reconciliation field;
- explicit enrollment identifier and enrollment status;
- evaluated Framework source version and immutable provenance reference;
- local compatibility outcome and observed-at time;
- local authoritative revision reference or digest sufficient to detect staleness, not a copy of `CONTROL` or `STATE`;
- a bounded staleness classification and a local result/evidence reference when the Project elects to disclose it.

It must exclude prompts, reasoning, tokens, source contents, raw logs, credentials, secrets, private Work Unit payloads, raw `CONTROL`, raw `STATE`, raw Results, raw Evidence, and arbitrary extension configuration.

## Authority boundaries

| Actor or store | May do | Must not do |
| --- | --- | --- |
| Framework source | Publish immutable evolution inputs and validate its own governance. | Decide, authorize, or mutate a Project. |
| Framework management index | Retain enrollment metadata and derived observations; expose read-only aggregate status. | Store Project authority, create Work Units, issue executable instructions, or write Project roots. |
| Governed Project root | Evaluate source, decide adoption, create its Work Unit, migrate locally, and retain local Result/Evidence. | Treat an observation/index as authoritative instruction or another Project's state. |
| Role Protocol / Kernel / `CONTROL` | Authorize local Project actions according to existing rules. | Delegate authority merely because a source, Registry route, or index exists. |
| Registry | Describe ownership route and module boundaries. | Grant execution, enrollment, adoption, mutation, or projection authority. |
| Consumer projection | Receive only consumer-allowed assets. | Receive management identities, enrollment/index records, or a central execution channel. |

For a Framework-management/self-hosting repository, `FRAMEWORK_MANAGEMENT` and `SELF_MANAGED` identify its management posture. They do not make that repository authoritative over ordinary Projects. Its own Project-local lifecycle follows the same bound-action rules as any other Project; its management metadata is not consumer-projected.

## Identity and cross-Project resource boundary

Every P0-4 resource is bound to the tuple:

`(project_id, project_context_id, repository_id, repository_full_name_when_present)`.

The first three values are required strong identifiers. A full name, display label, or `project_name` may assist a human reconciliation but cannot create, restore, transfer, or substitute a binding. Missing, conflicting, or inferred strong identity is fail-closed.

`CROSS_PROJECT_RESOURCE_BOUNDARY` applies to each of the following separately: `CONTROL`, `STATE`, Work Units, instruction envelopes, Result envelopes, Evidence, repository bindings, project extensions/configuration, Project Maps, and Resume artifacts. A consumer may use one only when the resource's complete binding equals the active Project context. A mismatch is rejected before interpretation; a missing binding is not guessed.

| Condition | Observable disposition | Mutation | Recovery |
| --- | --- | --- | --- |
| Strong binding matches active Project | Read or locally authorized use. | Only Project-local rules may allow it. | Normal local lifecycle. |
| Binding differs, is partial, or conflicts | `CROSS_PROJECT_CONTEXT_MISMATCH` / `IDENTITY_INVALID`; reject and quarantine the reference. | Prohibited. | Re-bind or reconcile from the owning Project with its local authorization and evidence. |
| External artifact is unbound | Read-only diagnostic may record that it is unbound; it is not consumable. | No identity inference write. | Explicit local enrollment/binding only. |
| Index observation no longer agrees with local identity | `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT`; index becomes read-only conflict evidence. | No Project write and no central repair. | Project-authorized identity or repository-transfer reconciliation. |

Quarantine means an implementation must not execute, merge, copy into authoritative state, or use the artifact for Resume/navigation decisions. A quarantined item may be retained as bounded diagnostic evidence if privacy policy permits; it is never silently reconciled.

## Registration, discovery, retention, and transfer

Enrollment is explicit and Project-local: a Project authorizes publication of a minimum identity tuple and chooses a transport (manual export/import, Project-initiated push, or Project-initiated pull). Discovery is not enrollment. Framework management must not scrape a repository name, infer a Project from Git remote data, or create a record that represents Project authority.

The index may retain `FRAMEWORK_MANAGEMENT_METADATA` for an explicit enrollment: stable identifiers, enrollment timestamp/status, display label, and bounded repository display data. It may retain derived observations according to a published retention policy. Removing enrollment stops new observations and marks prior data retired; it does not delete or alter Project-local records. Renames update display metadata only after an identity-bound Project confirmation. Repository transfer requires a Project-authorized reconciliation with old and new repository identity evidence; a full-name change alone is insufficient.

Staleness is observable only. An observation is stale when its source provenance is superseded beyond the policy window, its reported local revision no longer corresponds to the local Project's published evaluation, or enrollment is retired/unknown. Staleness cannot schedule a migration or create a Work Unit.

## Evolution and adoption lifecycle

```text
Framework publishes immutable source
  -> Project reads source locally
  -> Project evaluates compatibility locally
  -> Project explicitly decides
  -> Project creates authorized Work Unit
  -> Project performs local migration or no-action
  -> Project records local revision, Result, and Evidence
  -> optional Project publishes derived observation
  -> Framework index presents read-only fleet fact
```

The only mutation stages are within the Project root, after explicit Project decision and existing Kernel/`CONTROL`/Work Unit/Role Protocol authorization. A source fetch, observation transport, or central batch list is not authorization. A future batch interface may list independently eligible Projects as information only; it may not carry action commands, mutation status, retries, or delegated authority.

## Compatibility and fleet outcomes

P0-4 preserves the existing local compatibility outcomes exactly:

| Outcome | Local meaning | Central meaning |
| --- | --- | --- |
| `NO_ACTION` | No local change is needed. | Derived report only. |
| `OPTIONAL_REUSE` | Project may elect reuse. | No recommendation command. |
| `RECOMMENDED_UPGRADE` | Project should evaluate an upgrade. | Visibility, not authorization. |
| `REQUIRED_MIGRATION` | Compatibility requires a local migration decision. | Visibility, not automatic migration. |
| `CONFLICT` | Local adoption cannot proceed until resolved. | Read-only conflict report. |

Additional P0-4 fleet-only classifications are not compatibility outcomes and never alter local decisions:

| Classification | Meaning |
| --- | --- |
| `PROJECT_EVOLUTION_OBSERVATION_CURRENT` | An explicit, identity-valid observation exists for its reported source/revision. |
| `PROJECT_EVOLUTION_OBSERVATION_STALE` | The last observation is beyond published freshness criteria or no longer represents the reported local revision. |
| `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT` | Enrollment metadata or observation identity conflicts with the Project-bound tuple. |
| `PROJECT_EVOLUTION_NOT_ENROLLED` | No explicit enrollment exists; absence is not noncompliance. |

## Module routing and cross-module effects

The v2.6.0 Registry routes the exact primary responsibility, **project and repository identity**, to `identity-context`; P0-4 therefore selects it as the sole primary module. No eighth module is inferred.

| Module | Status | P0-4 effect |
| --- | --- | --- |
| `identity-context` | Primary | Owns strong binding and cross-Project resource-boundary contract. |
| `framework-core` | Affected | Defines Framework-source governance and preserves Registry non-authority. |
| `role-communication` | Affected | Ensures source/observation envelopes cannot become executable authority. |
| `navigation-continuity` | Affected | Keeps Map/Resume derived, locally bound, and unusable across Projects. |
| `git-continuity` | Affected | Supplies repository/revision continuity evidence; remote identity remains insufficient by itself. |
| `release-projection` | Affected | Excludes management source/index/enrollment identities from consumer projection. |
| `framework-validation` | Affected | Orchestrates checks without owning, repairing, or authorizing Project state. |

Cross-module implementation would be required because the contract has consumers in all seven existing modules; that does not transfer ownership. `CROSS_MODULE_STATUS` is `DESIGN_CROSS_MODULE_REQUIRED`. The Registry remains descriptive and is not an execution authority.

## Producer/consumer contracts

| Contract | Producer | Consumers | Inputs | Outputs/classification | Failure | Mutations |
| --- | --- | --- | --- | --- | --- | --- |
| `CROSS_PROJECT_RESOURCE_BOUNDARY_CONTRACT` | `identity-context` | all modules | active tuple, artifact tuple/type | allow, reject, or quarantine; identity control | existing mismatch/identity errors | No. |
| `FRAMEWORK_EVOLUTION_SOURCE_CONTRACT` | Framework governance | Project local evaluator | immutable version/provenance/rules | `READ_ONLY_EVOLUTION_SOURCE` | `FRAMEWORK_SOURCE_INVALID` | Framework publication only; never Project. |
| `PROJECT_EVOLUTION_EVALUATION_CONTRACT` | Project-local evaluator | Project decision process; optional observation producer | source plus local authoritative context | existing local compatibility outcome | `ADOPTION_NOT_AUTHORIZED`, `AUTHORITY_VIOLATION`, identity failures | No. |
| `PROJECT_ADOPTION_DECISION_CONTRACT` | Project `CONTROL`/Work Unit/Role Protocol | Project-local migration executor | local evaluation and explicit decision | local authorized decision and Work Unit binding | `ADOPTION_NOT_AUTHORIZED` | Yes, only in owning Project root. |
| `PROJECT_EVOLUTION_OBSERVATION_CONTRACT` | Explicitly enrolled Project | Framework management index | minimized tuple, source, outcome, freshness | `DERIVED_OBSERVATION_ONLY` | observation stale/enrollment conflict | Project may publish derived fact; index may retain metadata only. |
| `FRAMEWORK_EVOLUTION_INDEX_CONTRACT` | Framework management | authorized management readers | enrollment metadata and observations | read-only aggregate | index conflict/stale classifications | No Project mutation; metadata retention only. |

`FRAMEWORK_SOURCE_INVALID` means a purported source lacks immutable Framework provenance or required read-only classification. Authority is Framework publication validation; Project adoption is prohibited. Recovery is to obtain a valid published source and re-evaluate locally. `PROJECT_EVOLUTION_OBSERVATION_STALE` is triggered by defined freshness/revision disagreement; its authority is observation reporting only, it causes no mutation, and recovery is a local re-evaluation followed by optional re-publication. `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT` is triggered by a nonmatching strong tuple; its authority is neither central nor automatic, it causes no mutation, and recovery is Project-authorized reconciliation. These codes supplement rather than replace existing `CROSS_PROJECT_CONTEXT_MISMATCH`, GitHub repository mismatch/conflict, `IDENTITY_INVALID`, `AUTHORITY_VIOLATION`, `ADOPTION_NOT_AUTHORIZED`, and `MODULE_ROUTE_UNRESOLVED` vocabulary.

## Contracts and invariants affected

Affected existing contracts are `PROJECT_IDENTITY_CONTRACT`, `FRAMEWORK_GOVERNANCE_CONTRACT`, `ROLE_COMMUNICATION_CONTRACT`, `PROJECT_NAVIGATION_CONTRACT`, `CONTINUITY_RESUME_CONTRACT`, `GIT_CONTINUITY_CONTRACT`, `CONSUMER_PROJECTION_CONTRACT`, and `FRAMEWORK_VALIDATION_CONTRACT`. P0-4 adds only the six bounded contracts named in the producer/consumer table; their future implementation must remain within the seven registered modules.

Affected invariants are: Project identity remains authoritative; cross-Project context is denied by default; Registry metadata does not authorize execution; Role Protocol remains authoritative; Project Map is a derived navigation index; Resume is derived continuity aid; reviewed Git history remains append-only; consumer projection remains independent; validation orchestrates without taking ownership; and management-only Registry assets never become consumer runtime authority.

## Failure vocabulary and fail-closed behavior

| Failure | Trigger | Authority | Mutation | Recovery |
| --- | --- | --- | --- | --- |
| `CROSS_PROJECT_CONTEXT_MISMATCH` | Any protected artifact tuple differs from active context. | `identity-context` denies use. | None. | Owning Project reconciles locally. |
| `GITHUB_REPOSITORY_MISMATCH` / `REPOSITORY_CONFLICT` | Repository binding conflicts with verified repository identity. | Existing repository-binding contract. | None. | Local verified binding/reconciliation. |
| `IDENTITY_INVALID` | Required strong identifier missing, partial, or inferred. | Existing identity contract. | None. | Explicit Project-local binding. |
| `AUTHORITY_VIOLATION` | Source/index/envelope attempts to act as authority. | Kernel/Role Protocol. | None. | Remove unauthorized action; use local authorization. |
| `ADOPTION_NOT_AUTHORIZED` | Migration or adoption lacks explicit local decision/Work Unit. | Project controls. | None. | Create authorized local decision and Work Unit. |
| `MODULE_ROUTE_UNRESOLVED` | Exact responsibility has no Registry owner. | Registry routing. | None. | Block for governance decision; do not invent a module. |
| `FRAMEWORK_SOURCE_INVALID` | Source lacks valid immutable provenance/classification. | Framework source validator. | No Project mutation. | Obtain valid source and re-evaluate. |
| `PROJECT_EVOLUTION_OBSERVATION_STALE` | Freshness/revision condition fails. | Observation contract. | No automatic action. | Local re-evaluate; optionally republish. |
| `PROJECT_EVOLUTION_ENROLLMENT_CONFLICT` | Enrollment/observation tuple conflicts. | Cross-project boundary. | No central repair. | Project-authorized transfer or reconciliation. |

## Security and privacy

Central data minimization is mandatory. The source is public only to its authorized Framework audience; the index is management-read-only and access-controlled. It retains only the identifiers and derived facts stated above. It does not collect prompts, reasoning traces, token counts, source files, logs, secrets, credentials, raw project state, raw evidence, or extension values. Enrollment removal and retention are explicit lifecycle operations over management metadata, not remote control of Project data.

An index response must be labeled derived and must include enough source/provenance/freshness context to prevent it being mistaken for Project authority. An ordinary consumer projection rejects all `FRAMEWORK_MANAGEMENT`, `SELF_MANAGED`, enrollment, index, and management-only source assets.

## Test and validation strategy

Future implementation tests must prove:

- each protected artifact class rejects a different Project tuple and accepts only a complete matching tuple;
- unbound data is diagnostic-only and cannot generate inferred identity writes;
- source evaluation does not create a Work Unit, mutate `CONTROL`/`STATE`, or alter Map/Resume;
- adoption mutation is rejected without Project-local decision, Work Unit, and Role authorization;
- explicit enrollment, rename, retirement, repository transfer, and stale observations never alter Project-local authority;
- management/self-hosting identities never appear in ordinary consumer projection;
- Registry routing selects `identity-context` for the primary responsibility yet grants no execution authority;
- an index/batch representation cannot carry actionable instructions or mutation status;
- Git continuity and repository binding remain independently verified; display fields cannot substitute for strong identity.

Design-stage validation runs Framework and Project validators, module tests, consumer-projection validation, whitespace checks, and one-path scope checks. The exact new Design path is expected to be projection-unknown until a later approved projection decision. Record `PROJECTION_STAGE_DEVIATION=DEFERRED_NONBLOCKING`; no projection manifest change is authorized in this stage.

## Migration and compatibility

Existing Projects remain valid without enrollment and receive no new central authority. A Project can adopt P0-4 incrementally by first evaluating a Framework source locally, then explicitly enrolling only if it wants management visibility. Existing local compatibility outcomes, project-context binding, repository binding, Role Protocol, Project Map, Resume, Git continuity, and consumer projection retain their current meanings.

No automatic backfill, identity inference, repository-name matching, source rewrite, `CONTROL`/`STATE` migration, or observation generation is allowed. Existing Framework-management/self-hosting records are classified management-only and excluded from ordinary consumer projections.

## Future-work exclusions and P0-4 boundary

P0-4 defines only the interface a later evolution mechanism may consume: immutable source provenance, explicit enrollment, derived observation, and fail-closed identity boundary. It does not choose or authorize P0-5 slot lifecycle mechanics, P0-6 telemetry mechanisms, P1 autonomous agents, budgets, capabilities, daemon operations, centralized state redesign, or active rollout coordination. Any such work needs a separate design, Registry responsibility check, and explicit authority decision.

## Open questions

None for this Design candidate. Transport details, retention duration, and freshness thresholds are deliberately bounded policy parameters to be set by a future approved implementation within this contract; they cannot change the authority model, data-minimization rules, or fail-closed behavior.
