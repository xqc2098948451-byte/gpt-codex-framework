# GPT–Codex Framework — Modular Architecture & Routing Design

## Status and decision

This document formalizes the approved P0-2 design for Framework Modular
Architecture & Routing. It is a design artifact only. It does not create the
Framework Module Registry, schemas, resolver, validators, tests, consumer
projection changes, runtime behavior, or a release.

The current DESIGN stage authorizes design review only; it does not authorize
implementation now. After DESIGN is accepted/frozen and PLAN is
accepted/frozen, a separate P0-2 Implementation Work Unit may create or modify
the Registry, module descriptors, schemas, routing implementation, validators,
and tests within the approved Plan. The verification surface in this document
is not, by itself, permission to modify tests during DESIGN.

The design introduces one future authoritative concept: the **Framework Module
Registry**. It is independent from the Project Map and from execution
governance. Its purpose is to make framework responsibility, ownership,
interfaces, dependencies, constraints, risk, and verification surfaces
explicit so that future routing can be deterministic and bounded.

Baseline:

- Framework baseline: `v2.4.0`
- Base SHA: `243a65c1f33c2f8ef04fc876dea9cf213dfc3432`
- `KERNEL_VERSION`: `2.0.0`
- `SCHEMA_GENERATION`: `1`
- Publication attestation: present at the baseline commit and recorded by
  `releases/records/v2.4.0.json`

No version, Kernel contract, schema generation, release metadata, or consumer
artifact is changed by this design.

## 1. Problem and objectives

The v2.4.0 framework has strong contracts for Kernel governance, Work Units,
role communication, identity, navigation/resume, Git continuity, validation,
consumer projection, and release. It does not yet have one explicit authority
that answers which framework module owns a responsibility or concrete asset.
Without that authority, responsibility may be inferred from directory layout,
the Project Map may be overloaded, and a change that crosses a module boundary
may be mistaken for a local change.

P0-2 defines a bounded architecture that will allow a future implementation to:

1. classify a requested outcome by responsibility before selecting files;
2. identify one primary framework module and load its descriptor;
3. read only the owned assets and dependencies necessary for the request;
4. distinguish a single-module change from an explicit cross-module change;
5. reject unresolved, conflicting, malformed, or unsafe routing closed; and
6. expose a stable module identity that future P0 work may reference without
   turning the Registry into project-management state.

The governing principle is:

> Responsibility first, files second.

The Registry is a structural authority and verifier. It is not an AI intent
inference engine.

## 2. Authority model and existing contracts

The Framework Module Registry is authoritative only for framework modular
architecture: responsibility boundaries, ownership, module relationships, and
the structural facts required to verify a route.

It does not replace or weaken the following v2.4.0 authorities:

| Existing contract | Boundary preserved by this design |
| --- | --- |
| Kernel | Continues to define the framework governance bounds and Kernel rules. |
| `CONTROL` | Continues to bind project identity, enabled extensions, and project/framework context. |
| Work Unit | Continues to authorize the concrete goal, scope, acceptance, permissions, and evidence. |
| Guardrails | Continue to constrain execution and fail-closed behavior. |
| Role Communication Protocol | Continues to define message roles, authority, instruction/result ownership, and review lifecycle. |
| Git continuity | Continues to determine revision, ancestry, synchronization, review binding, and remote verification. |
| Publication authority | Continues to govern release evidence, runtime closure, and publication. |
| Project Map / Module Map | Continue as derived project-local navigation and freshness indexes. |
| Built-ins catalog | Continues to describe required/optional skills, guardrails, fitness, and adoption behavior. |

The Registry answers:

> What belongs where?

Execution governance answers:

> Who may do what now?

Registry membership, module `PERMISSIONS` metadata, and a successful route must
never be interpreted as execution authorization. The existing authority chain
remains independently authoritative.

## 3. Project Map and Built-ins boundaries

The existing project-local navigation assets remain a
`DERIVED_NAVIGATION_INDEX`:

```text
.gpt-codex/navigation/PROJECT_MAP.json
.gpt-codex/navigation/modules/<module-id>.json
```

They describe project-local location, architecture hints, navigation, and
freshness. They do not become Framework Module authority. Their route states
remain conceptually distinct:

```text
MAP_HIT
MAP_PARTIAL
MAP_MISS
MAP_MISSING
```

Their freshness values remain:

```text
VERIFIED
STALE
UNKNOWN
```

The Registry and Project Map have separate authority and lifecycle:

```text
Framework Registry → framework responsibility / ownership / dependency
Project Map        → project-local navigation / location / freshness
```

Therefore:

```text
Registry missing  != Project Map invalid
Project Map stale != Registry stale
```

A future Project Map may optionally record Framework module IDs as navigation
metadata, but that reference must not merge authorities or make the Project
Map a governance source.

`.gpt-codex/builtins/INDEX.json` remains the catalog for required and optional
skills, guardrails, fitness, and adoption behavior. It is not the Framework
Module Registry and does not acquire module ownership semantics in this work.

## 4. Approved architecture

The future Registry is an explicit independent layer:

```text
Framework Module Registry
        |
        +-- module identity / purpose
        +-- responsibility / non-responsibility
        +-- owned assets
        +-- entry points / inputs / outputs
        +-- dependencies / consumers
        +-- invariants / module constraints
        +-- change risk
        +-- required tests
```

The conceptual route is:

```text
requested outcome
    ↓
classify responsibility
    ↓
identify one primary module
    ↓
load module descriptor
    ↓
read only necessary owned assets / dependencies
    ↓
MODULE_ROUTE with SINGLE_MODULE_CHANGE
or
CROSS_MODULE_CHANGE_REQUIRED
or
MODULE_ROUTE_UNRESOLVED
```

GPT may semantically propose a candidate module from the requested outcome.
The Registry/resolver verifies that the candidate is registered with
`status = ACTIVE`, has a valid descriptor, and structurally covers the proposed
responsibility. A registered `status = INACTIVE` module is not eligible as a
primary route target and fails closed if selected/requested. The model does not
get authority to invent a module, bypass ownership, or broaden the read set.

The design explicitly prohibits routing by directory scan or by unverified
file-path guessing as the primary semantic mechanism.

## 5. Future repository structure

The minimal conceptual repository structure is:

```text
.gpt-codex/
  framework-modules/
    REGISTRY.json
    modules/
      <module-id>.json

  schemas/
    framework-module-registry.schema.json
    framework-module.schema.json

  scripts/
    framework_module_routing.py
```

This is a future implementation proposal, not authorization to create these
files during the current DESIGN stage.

### 5.1 Registry model

`REGISTRY.json` contains only the global facts required to resolve descriptors:

```text
schema_version
authority
framework_version
modules
```

Each `modules` entry contains the minimum lookup information:

```text
module_id
descriptor
status
```

The Registry machine contract freezes:

```text
authority = FRAMEWORK_MODULE_REGISTRY
status ∈ { ACTIVE, INACTIVE }
```

`ACTIVE` means the registered module is eligible for normal module routing.
`INACTIVE` means the module remains registered but is not eligible as a primary
route target; selecting or requesting it fails closed. P0-2 does not introduce
lifecycle transition machinery, maturity levels, automatic activation or
deactivation, or status scoring.

The Registry must not duplicate complete descriptor content. The descriptor is
the canonical location for the module's bounded responsibility and ownership
facts. `authority` identifies the document as Framework Module Registry
authority; it must not be conflated with execution authority.

## 6. Module descriptor contract

The first implementation is bounded to exactly these descriptor fields:

```text
MODULE_ID
VERSION
PURPOSE
RESPONSIBILITIES
NON_RESPONSIBILITIES
OWNED_ASSETS
ENTRY_POINTS
INPUTS
OUTPUTS
DEPENDS_ON
USED_BY
INVARIANTS
PERMISSIONS
CHANGE_RISK
REQUIRED_TESTS
RELATED_MODULES
```

No additional descriptor field is justified unless a demonstrated closure
requirement cannot be satisfied by these fields.

Field semantics are:

- `MODULE_ID` is the stable, unique module identity.
- `VERSION` identifies the descriptor contract version for that module.
- `PURPOSE` is the concise reason the module exists.
- `RESPONSIBILITIES` states what the module owns conceptually.
- `NON_RESPONSIBILITIES` states adjacent concerns that must remain elsewhere.
- `OWNED_ASSETS` identifies governed concrete assets using the bounded selector
  classes in Section 7.
- `ENTRY_POINTS`, `INPUTS`, and `OUTPUTS` describe the module boundary.
- `DEPENDS_ON` names modules whose contracts or assets are consumed.
- `USED_BY` names modules that consume this module's contract or assets.
- `INVARIANTS` states constraints that must remain true for the module.
- `PERMISSIONS` records bounded module-level operational classifications only.
- `CHANGE_RISK` records the module's change-risk classification.
- `REQUIRED_TESTS` names the verification surface required for changes.
- `RELATED_MODULES` records relevant relationships that are not dependency or
  consumer edges.

`PERMISSIONS` is not a grant. It may contain classifications such as:

```text
READ_ONLY_REFERENCE
CONSUMER_PROJECTED
FRAMEWORK_DEVELOPMENT_ONLY
RELEASE_MANAGED
```

It must not become an execution authorization source, a replacement for Work
Unit permissions, or a role-selection mechanism.

## 7. Ownership semantics and selectors

The Registry uses one primary owner per framework-managed concrete asset. There
is no default multi-owner model. A module relationship is expressed through
`DEPENDS_ON`, `USED_BY`, or `RELATED_MODULES`; those relationships do not
transfer ownership.

True shared assets still have one primary owner and one or more consumers. A
new shared/core module may be proposed only after evidence shows a stable,
independent shared responsibility. A generic `common` dumping-ground module is
not part of this design.

The first implementation recognizes only three owned-asset selector classes:

```text
EXACT_PATH
PATH_PREFIX
LOGICAL_ASSET
```

Every `OWNED_ASSETS` entry uses exactly this minimal object form:

```json
{
  "type": "EXACT_PATH | PATH_PREFIX | LOGICAL_ASSET",
  "value": "..."
}
```

The object has no selector-specific ownership fields beyond `type` and
`value`. For `EXACT_PATH` and `PATH_PREFIX`, `value` is a normalized,
repository-relative path. Absolute paths and any `..` traversal are invalid.

Ownership matching is component-aware. The following different-owner matches
are conflicts:

```text
EXACT_PATH(A) vs EXACT_PATH(A)
→ MODULE_OWNERSHIP_CONFLICT

PATH_PREFIX(P) vs EXACT_PATH(X), where X is inside P
→ MODULE_OWNERSHIP_CONFLICT

PATH_PREFIX(P1) vs PATH_PREFIX(P2), where either prefix contains the other
→ MODULE_OWNERSHIP_CONFLICT
```

Containment uses path-component boundaries. A raw string prefix accident such
as `foo/bar` matching `foo/bar2` is not containment and does not create a
conflict. For `LOGICAL_ASSET`, normalized logical identifiers are compared;
identical identifiers with different owners conflict, and a logical identifier
does not imply physical-file overlap.

For a planned framework mutation, ownership resolution is complete only when
there is exactly one matching primary owner:

```text
zero matching primary owners
→ MODULE_ROUTE_UNRESOLVED

more than one matching primary owner
→ MODULE_OWNERSHIP_CONFLICT
```

Only exactly one owner may proceed to single-module or cross-module
classification. Initial Registry coverage may be incremental, but an
unclassified asset never becomes implicitly owned by the candidate module.

Examples:

```text
EXACT_PATH  .gpt-codex/KERNEL.md
PATH_PREFIX .gpt-codex/release/
LOGICAL_ASSET framework-release
```

`LOGICAL_ASSET` is rare. It is used only when the governed contract does not
naturally map to a repository path, such as a named built-in behavior or
contract surface. It must not become an arbitrary expression language.

The design does not include glob DSLs, regex ownership rules, field-level
ownership DSLs, or arbitrary selector expressions. Active ownership that maps
the same concrete asset to different primary modules is invalid and must
produce `MODULE_OWNERSHIP_CONFLICT`.

## 8. Responsibility-first routing

Routing is deterministic after GPT's semantic proposal has been verified:

1. Read the requested outcome and classify the responsibility.
2. Select one candidate primary module.
3. Resolve the candidate's registered descriptor.
4. Verify descriptor identity, status, responsibility coverage, and ownership
   structure.
5. Read the minimum necessary owned assets and declared dependencies.
6. Determine whether the requested mutation is local to the primary module or
   crosses an owned contract/asset boundary.
7. Return one of the bounded outcomes below.

The bounded outcomes are:

### `MODULE_ROUTE`

The primary module is structurally valid and the requested change can remain
inside its responsibility boundary. The route carries the primary module and
the change scope `SINGLE_MODULE_CHANGE`.

An internal implementation change in Module A that preserves Module B's
consumed contract remains a single-module change even if Module B is read.
Read-only use of another module is not a cross-module mutation.

### `CROSS_MODULE_CHANGE_REQUIRED`

The requested mutation changes another module-owned concrete asset or a
contract consumed by another module. Cross-module work is permitted, but it
must be surfaced explicitly rather than hidden inside a local route.

### `MODULE_ROUTE_UNRESOLVED`

No candidate can be structurally verified, the responsibility is ambiguous,
the module is missing or inactive, or the route would require unsafe or
conflicting ownership assumptions. The resolver fails closed.

The Registry does not produce confidence scores, rankings, probabilistic
routes, adaptive strategies, or automatic architecture decisions. GPT
proposes; the Registry verifies.

The following fallback is forbidden:

```text
route unresolved
→ scan the whole framework
→ guess a module
```

## 9. Cross-module semantics

Cross-module work is explicit at the governed change boundary. At minimum,
the route/evidence must surface:

```text
PRIMARY_MODULE
AFFECTED_MODULES
WHY_CROSS_MODULE
CONTRACTS_AFFECTED
INVARIANTS_AFFECTED
REQUIRED_TESTS
```

Examples:

- Changing Module A's internal implementation while preserving Module B's
  consumed output contract is `MODULE_ROUTE` with `SINGLE_MODULE_CHANGE`.
- Changing Module A's output contract consumed by Module B is
  `CROSS_MODULE_CHANGE_REQUIRED`.
- Changing an asset whose primary owner is Module B is
  `CROSS_MODULE_CHANGE_REQUIRED`, even if the initiating request was first
  classified under Module A.

The route classification does not itself authorize the mutation. The existing
Work Unit, role, Guardrails, state, Git, review, and publication contracts
continue to decide whether and how the change may execute.

## 10. Extending a module versus creating a module

The default decision is:

```text
EXTEND_EXISTING_MODULE
```

A new module is justified only when an existing responsibility cannot naturally
contain the capability and the new responsibility has an independent set of
all four properties:

```text
purpose
owned assets
interface/boundary
verification surface
```

If any of these are missing, the capability remains in an existing module or
the route remains unresolved pending a governed design decision. This rule
prevents unnecessary module proliferation. No automatic module creation or
deletion is designed.

## 11. Failure semantics

The initial failure vocabulary is deliberately small:

```text
MODULE_REGISTRY_INVALID
MODULE_DESCRIPTOR_INVALID
MODULE_NOT_REGISTERED
MODULE_ROUTE_UNRESOLVED
MODULE_OWNERSHIP_CONFLICT
CROSS_MODULE_CHANGE_REQUIRED
MODULE_DEPENDENCY_INVALID
```

The system fails closed:

- malformed global Registry data produces `MODULE_REGISTRY_INVALID`;
- malformed or mismatched descriptor data produces
  `MODULE_DESCRIPTOR_INVALID`;
- a missing Registry entry produces `MODULE_NOT_REGISTERED`;
- missing or ambiguous responsibility produces `MODULE_ROUTE_UNRESOLVED`;
- a registered `INACTIVE` module selected as a primary route target produces
  `MODULE_ROUTE_UNRESOLVED`;
- duplicate active ownership by different primary owners produces
  `MODULE_OWNERSHIP_CONFLICT`;
- a mutation across an owned contract or asset boundary produces
  `CROSS_MODULE_CHANGE_REQUIRED`;
- a missing or invalid dependency reference produces
  `MODULE_DEPENDENCY_INVALID`.

No failure path scans the whole framework and guesses a module. No unresolved
route silently degrades into an implementation route.

## 12. Validation model

Future Framework validation may integrate Registry checks into the existing
validation orchestration. The validation module invokes the rules owned by
each module; it does not become the owner of every framework rule.

At minimum, Registry validation must check:

```text
unique module_id
descriptor exists
descriptor module_id matches registry entry
dependency references resolve
used_by / depends_on consistency
ownership conflicts rejected
owned paths are safe relative paths
required-test references resolve sufficiently
```

Safe relative paths are normalized, repository-relative paths that are not
absolute and do not escape through parent traversal. Selector validation must
apply the same safety rule to every path-bearing selector.

The validator checks reference and semantic integrity but does not require the
dependency graph to be a strict DAG in P0. Cycles are not prohibited without
future evidence that a cycle rule is necessary. Dependency references must
resolve and `USED_BY`/`DEPENDS_ON` relationships must agree, while legitimate
cyclic relationships remain representable.

`REQUIRED_TESTS` must resolve sufficiently to the repository's verification
surface, such as an existing test path or stable test identifier recognized by
the future validator. A descriptor cannot claim a required test that the
validation model cannot locate or interpret.

## 13. Initial framework module decomposition

The initial Registry freezes exactly these seven modules:

```text
framework-core
identity-context
role-communication
navigation-continuity
git-continuity
release-projection
framework-validation
```

No module is created solely to reserve a future roadmap capability.

### 13.1 `framework-core`

Purpose: own the minimum framework governance and Kernel contract.

Responsibilities:

- Kernel;
- `CONTROL` / `STATE` / `WORK_UNIT` core contracts;
- Kernel rules; and
- minimal framework governance.

Representative owned assets:

```text
.gpt-codex/KERNEL.md
.gpt-codex/schemas/control.schema.json
.gpt-codex/schemas/state.schema.json
.gpt-codex/schemas/work-unit.schema.json
.gpt-codex/project-template/CONTROL.template.json
.gpt-codex/project-template/STATE.template.json
.gpt-codex/project-template/WORK_UNIT.template.json
.gpt-codex/scripts/kernel_rules.py
```

`CHANGE_RISK = HIGH`.

This module does not own Role Protocol, Git continuity, navigation, or
release.

### 13.2 `identity-context`

Purpose: establish which project and repository a governed action belongs to.

Responsibilities:

- project identity and `project_context_id`;
- repository binding;
- cross-project context isolation;
- bootstrap identity binding; and
- identity reconciliation.

Representative owned assets:

```text
.gpt-codex/scripts/context_binding.py
.gpt-codex/scripts/github_repository_binding.py
cross-project-context-binding guardrail
github-repository-binding guardrail
```

It answers:

> Which project / which repository?

It does not own Git revision synchronization.

### 13.3 `role-communication`

Purpose: own the exact role taxonomy, instruction/result contracts, and
review/fix communication lifecycle.

Responsibilities:

- exact role taxonomy;
- instruction/result message ownership;
- instruction authority contract;
- review/finding/fix lifecycle;
- reviewer non-mutation boundary;
- role observation; and
- Handoff role projection.

Representative owned assets:

```text
.gpt-codex/scripts/role_communication.py
.gpt-codex/scripts/instruction_envelope.py
.gpt-codex/scripts/result_return.py
instruction-envelope schema/template
result-envelope schema/template
handoff skill
role protocol tests
```

The module owns the communication contracts, not execution authority outside
the existing role and Work Unit model.

### 13.4 `navigation-continuity`

Purpose: keep project navigation and continuation context together initially.

Responsibilities:

- Project Map;
- derived Module Map;
- map routing states and freshness;
- Resume;
- `FAST_RESUME`;
- `DELTA_RESUME`;
- `RECONCILIATION_REQUIRED`;
- `COLD_RESUME`; and
- context-window recovery.

Representative owned assets:

```text
.gpt-codex/scripts/project_navigation.py
.gpt-codex/scripts/continuity_resume.py
.gpt-codex/schemas/project-map.schema.json
.gpt-codex/schemas/module-map.schema.json
.gpt-codex/schemas/resume.schema.json
.gpt-codex/project-template/navigation/*
.gpt-codex/project-template/continuity/*
```

The invariant is:

```text
navigation-continuity != Framework Module Registry
```

The observed gap that Project Map/Resume can preserve project navigation and
context but does not yet sufficiently preserve framework-development
continuation across a fresh ChatGPT conversation remains in this module
temporarily. It is evidence for future P0-5 Framework Design Continuity &
Sufficiency Control, not a reason to create an eighth module.

### 13.5 `git-continuity`

Purpose: determine whether the governed revision and synchronization state are
the right ones.

Responsibilities:

- local/remote revision continuity;
- exact SHA review binding;
- synchronization classifications;
- review-stage synchronization;
- append-only reviewed history; and
- remote verification.

Representative primary asset:

```text
.gpt-codex/scripts/git_continuity.py
```

and its focused tests.

The identity distinction is explicit:

```text
identity-context → this is the right repository
git-continuity   → this is the right revision/synchronization state
```

### 13.6 `release-projection`

Purpose: own the boundary that turns framework authority into a verified
consumer release projection.

Responsibilities:

- consumer projection;
- runtime closure;
- release archive;
- release framework;
- release metadata;
- publication contract; and
- release evidence boundary.

Representative owned assets:

```text
.gpt-codex/scripts/consumer_projection.py
.gpt-codex/scripts/validate_consumer_projection.py
.gpt-codex/scripts/release_framework.py
.gpt-codex/scripts/release_archive.py
.gpt-codex/scripts/publication_contract.py
.gpt-codex/release/*
releases/*
framework-release extension
```

Packaging a module does not transfer ownership of that module's contract to
`release-projection`.

### 13.7 `framework-validation`

Purpose: own validation orchestration only.

Responsibilities:

```text
validate_framework.py
validate_project.py
self-hosting validation orchestration
cross-module validation entrypoints
```

The correct model is:

```text
module owns rule
→ validation module invokes/checks rule
```

The incorrect model is:

```text
framework-validation owns every framework rule
```

A change to another module plus a global validator entrypoint may legitimately
be a cross-module change. A plugin validator architecture is not introduced in
P0-2.

## 14. Built-ins and shared schemas

There is no standalone `builtins` module in the initial Registry. A built-in
skill, guardrail, or fitness asset belongs to the module whose responsibility
it implements:

```text
handoff
→ role-communication

cross-project-context-binding
→ identity-context

framework-release
→ release-projection
```

`.gpt-codex/builtins/INDEX.json` may initially be owned by `framework-core` as
the catalog contract. A `capability-catalog` module is not created; that
decision belongs to future Capability & Permission work if evidence justifies
it.

Schemas that carry concerns from multiple modules still have one primary
owner. For example:

```text
instruction-envelope.schema.json → role-communication
```

Other modules constrain that schema through dependencies and invariants. There
is no field-level ownership model. If a role-communication change alters
identity semantics, it is `CROSS_MODULE_CHANGE_REQUIRED`; adding a role-specific
field without changing identity semantics is `SINGLE_MODULE_CHANGE`.

## 15. Consumer projection boundary

Registry membership does not imply consumer projection. Consumer runtime
projection remains controlled by the existing consumer projection authority.

Generic runtime-relevant descriptors may eventually be projected when the
projection contract requires them. Framework-development-only architecture
metadata may remain management-only. The entire Framework Module Registry must
not be assumed to ship to consumer projects.

This preserves the existing distinction between:

```text
Framework management authority
consumer runtime projection
```

Any future projection of module metadata must preserve the source module's
ownership and must not expose management metadata as consumer execution
authority.

## 16. Boundaries with future P0 work

P0-2 identifies framework ownership and routing. It does not implement the
following later decisions:

- **P0-3 Framework–Project Separation** determines where framework ownership
  ends and consumer-project ownership begins. P0-2 does not implement a
  deployment boundary or project-domain separation policy.
- **P0-4 Project Isolation & Centralized Framework Evolution** determines which
  project may mutate or evolve shared framework authority. P0-2 does not
  implement centralized evolution permissions.
- **P0-5 Framework Design Continuity & Sufficiency Control** governs
  authoritative development state such as active module, accepted design SHA,
  accepted plan SHA, active Work Unit, gate status, open decisions, and next
  governed action. P0-2 may provide stable module identity but is not a
  project-management or development-state database.
- **P0-6 Execution Telemetry Foundation** may later use
  `PRIMARY_MODULE`, `AFFECTED_MODULES`, and `CROSS_MODULE_CHANGE` as telemetry
  dimensions. P0-2 does not collect, score, or adapt from telemetry.

## 17. Explicit non-goals

The following are outside this design:

```text
Framework–Project Separation policy
Project Isolation policy
Framework Development State
Execution Telemetry
Capability/Permission Model
Invariant Registry
Agent Budget
Strategy Intelligence
Failure Pattern Registry
User Alignment
Maturity Model
Migration Intelligence
automatic module creation
automatic module deletion
automatic dependency scoring
routing confidence scoring
dynamic plugin loading
automatic architecture refactoring
automatic cross-module implementation planning
```

No module is created solely to reserve any of these future roadmap capabilities.

## 18. Design acceptance invariants

This design is sufficient only while all of these remain true:

1. There is one canonical Framework Module Registry/descriptor system.
2. Project Map remains `DERIVED_NAVIGATION_INDEX`.
3. Each governed concrete asset has one primary owner.
4. Responsibility classification precedes file routing.
5. Cross-module mutation is explicit.
6. The Registry never grants execution authority.
7. Existing modules are extended before a new module is created.
8. Unresolved or conflicting routing fails closed rather than scanning or
   guessing.
9. The consumer projection boundary remains independent.
10. v2.4.0 Kernel, Role Protocol, Project Map/Resume, publication authority,
    and Git continuity contracts remain compatible unless a future explicit
    cross-module decision changes them.

These invariants define sufficiency for P0-2. They do not authorize speculative
optimizations or additional architecture.

## 19. Future implementation acceptance surface

Without prescribing implementation task decomposition, a future plan must be
able to identify the following from this document:

- the two Registry/descriptor documents and their schemas;
- the bounded routing seam;
- the seven initial descriptors;
- the existing scripts, schemas, templates, built-ins, tests, and release
  assets that should be reused as module-owned seams;
- the distinction between authoritative Registry data and derived Project Map
  data;
- the single-owner and selector rules;
- the route and cross-module classifications;
- the fail-closed failure vocabulary;
- the validation integrity checks;
- the independent consumer projection boundary; and
- the contracts that cannot be repurposed.

Future verification should cover at least:

1. valid Registry and descriptor loading;
2. unique module IDs and matching descriptor identities;
3. missing descriptor and unregistered-module failures;
4. dependency resolution and `USED_BY`/`DEPENDS_ON` consistency;
5. ownership conflict detection;
6. safe relative path selectors;
7. sufficient required-test reference resolution;
8. responsibility-first `MODULE_ROUTE` behavior;
9. explicit cross-module classification and required evidence fields;
10. fail-closed unresolved routing without whole-framework scan fallback;
11. preserved Project Map route/freshness semantics;
12. preserved execution authority boundaries; and
13. preserved consumer projection and v2.4.0 compatibility behavior.

This is a verification surface, not an implementation plan and not, by itself,
permission to modify tests during the DESIGN stage. Test changes belong to the
separate P0-2 Implementation Work Unit after DESIGN and PLAN are both
accepted/frozen, and only within the approved Plan.

## 20. Decision summary

P0-2 establishes a single explicit Framework Module Registry with seven initial
modules and a bounded descriptor contract. It keeps navigation, built-ins,
execution authority, Git continuity, release projection, and validation
orchestration distinct while making their framework ownership explicit.

The durable routing rule is:

```text
GPT proposes
Registry verifies
authority contracts authorize execution
```

The durable ownership rule is:

```text
one governed concrete asset → one primary module owner
```

The durable safety rule is:

```text
unresolved or conflicting route → fail closed
```
