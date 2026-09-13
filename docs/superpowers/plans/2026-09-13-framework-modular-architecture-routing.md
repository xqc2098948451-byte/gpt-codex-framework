# Framework Modular Architecture & Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. The framework execution model below is authoritative: Plan Tasks are not agent boundaries.

**Goal:** Implement the frozen P0-2 Framework Module Registry, deterministic responsibility-first routing, ownership/dependency validation, and compatible framework-management documentation and projection closure.

**Architecture:** Add one management-side Registry containing minimal module lookup entries and seven separate descriptors. Add one focused Python routing module that loads and validates those contracts, resolves ownership with bounded selectors, and returns deterministic route decisions. Existing Project Map, role/execution authority, validation orchestration, Git continuity, release authority, and consumer projection remain separate authorities.

**Tech Stack:** Python 3 standard library, JSON Schema draft 2020-12 documents, existing `unittest` suite, existing framework validators and consumer projection scripts, Git worktree/branch workflow.

**Spec:** `docs/superpowers/specs/2026-09-13-framework-modular-architecture-routing-design.md`, accepted and frozen at SHA `e6cd404aafb1c9122ad8f26ce7583aa3d73914ad`.

**Accepted Design SHA:** `e6cd404aafb1c9122ad8f26ce7583aa3d73914ad` (immutable; every implementation task is subordinate to this exact revision).

## Global Constraints

- The current branch is `feature/framework-modular-architecture-routing-design`, and the implementation must start from the accepted Design descendant that contains this Plan.
- `KERNEL_VERSION = 2.0.0` and `SCHEMA_GENERATION = 1` remain unchanged.
- The frozen Design is read-only; no implementation task may edit `docs/superpowers/specs/2026-09-13-framework-modular-architecture-routing-design.md`.
- This Plan authorizes planning only. Implementation begins only in a later P0-2 Implementation Work Unit after DESIGN and PLAN are both accepted/frozen.
- This FIX_INSTRUCTION remains a PLAN-stage correction: do not start implementation and do not modify production code, tests, schemas, Registry files, or the projection manifest during this fix.
- Do not modify `.gpt-codex/KERNEL.md`, `VERSION`, release realization records, or `dist/*`.
- The descriptor fields remain exactly `MODULE_ID`, `VERSION`, `PURPOSE`, `RESPONSIBILITIES`, `NON_RESPONSIBILITIES`, `OWNED_ASSETS`, `ENTRY_POINTS`, `INPUTS`, `OUTPUTS`, `DEPENDS_ON`, `USED_BY`, `INVARIANTS`, `PERMISSIONS`, `CHANGE_RISK`, `REQUIRED_TESTS`, and `RELATED_MODULES`.
- Registry authority is exactly `FRAMEWORK_MODULE_REGISTRY`.
- Registry status is exactly `ACTIVE` or `INACTIVE`; only `ACTIVE` modules are normal primary route targets.
- The GPT semantic proposal supplies both an existing module ID and one exact responsibility string declared by that module; missing or mismatched responsibility fails as `MODULE_ROUTE_UNRESOLVED`.
- `PERMISSIONS` is operational module metadata, never an execution authorization source.
- Each `OWNED_ASSETS` selector is exactly `{ "type": "EXACT_PATH | PATH_PREFIX | LOGICAL_ASSET", "value": "..." }`.
- `EXACT_PATH` and `PATH_PREFIX` values are normalized safe repository-relative paths; absolute paths and `..` traversal are rejected.
- The only ownership selector classes are `EXACT_PATH`, `PATH_PREFIX`, and `LOGICAL_ASSET`; no glob, regex, field-level DSL, or arbitrary expression language is added.
- One concrete governed asset has one primary owner; zero owners and multiple owners fail closed.
- `foo/bar` does not contain or match `foo/bar2`; matching uses path components.
- Initial Registry coverage may be incremental, but an unclassified asset never becomes implicitly owned by the candidate module.
- Routing outcomes remain `MODULE_ROUTE`, `CROSS_MODULE_CHANGE_REQUIRED`, and `MODULE_ROUTE_UNRESOLVED`.
- Failure classifications remain `MODULE_REGISTRY_INVALID`, `MODULE_DESCRIPTOR_INVALID`, `MODULE_NOT_REGISTERED`, `MODULE_ROUTE_UNRESOLVED`, `MODULE_OWNERSHIP_CONFLICT`, `CROSS_MODULE_CHANGE_REQUIRED`, and `MODULE_DEPENDENCY_INVALID`.
- No whole-framework scan or guessed fallback is allowed after an unresolved route.
- No scoring, ranking, confidence, probability, strategy adaptation, dynamic plugin loading, automatic module lifecycle, or automatic architecture refactoring is added.
- Project Map remains `DERIVED_NAVIGATION_INDEX` with `MAP_HIT`, `MAP_PARTIAL`, `MAP_MISS`, `MAP_MISSING` and `VERIFIED`, `STALE`, `UNKNOWN` unchanged.
- Registry data, module `PERMISSIONS`, and a successful route never grant execution authority; Kernel, CONTROL, Work Unit, Guardrails, Role Protocol, Git, and publication authority remain authoritative.
- Consumer projection remains independent. Management-only Registry assets are classified explicitly and are not projected as consumer runtime authority.
- Dependency references must resolve and `USED_BY`/`DEPENDS_ON` must agree, but the graph is not required to be a DAG.
- `validate_registry(...) -> list[str]` is the single structural/semantic validation model: it returns de-duplicated frozen failure codes and does not raise for invalid selectors, dependencies, ownership conflicts, or descriptor mismatches.
- `load_registry()` and `load_module_descriptor()` may raise `ModuleRoutingError` when their direct load operation cannot complete; `route_responsibility()` consumes `validate_registry()` first and raises the appropriate frozen code before routing.
- No P0-3 Framework–Project Separation, P0-4 Project Isolation, P0-5 Framework Development State, or P0-6 Execution Telemetry behavior is implemented.

## Execution Governance

The future Implementation Work Unit uses one persistent `CODEX_IMPLEMENTER`, multiple related Plan Tasks, and milestone/risk-gated review. The following invariant is mandatory:

```text
PLAN_TASK != AGENT
PLAN_TASK != FRESH_REVIEWER
```

The default execution model is:

```text
one persistent CODEX_IMPLEMENTER
multiple related Plan Tasks
milestone/risk-gated CODEX_REVIEWER
same Reviewer for remediation re-review by default
fresh Reviewer only on escalation
```

If an execution header is used, it binds the implementation session to
`superpowers:executing-plans`. A Plan Task does not authorize a new agent,
reviewer, permission, Work Unit, or scope. The existing role authority chain
remains the upper bound:

```text
Kernel
  ⊇ CONTROL / Guardrails
    ⊇ Work Unit
      ⊇ instruction authorized_actions
        ⊇ actual implementation actions
```

The `CODEX_REVIEWER` may `READ`, `TEST`, `VALIDATE`, `COMPARE`, and `REPORT`.
The Reviewer does not repair the reviewed revision. Gate A reviews the core
Registry/schema/ownership/routing contract after Task 4. Gate B reviews the
integrated implementation, validator integration, documentation, projection
closure, and full verification after Task 8. The same Reviewer handles both
gates and any remediation re-review unless GPT explicitly escalates.

## Exact file map

The implementation must use this file map. Each path has one purpose and every
created or modified path has a task below.

### Create

| Path | Purpose |
| --- | --- |
| `.gpt-codex/framework-modules/REGISTRY.json` | Minimal global Registry lookup contract for the seven initial modules. |
| `.gpt-codex/framework-modules/modules/framework-core.json` | Descriptor for Kernel and minimum framework governance. |
| `.gpt-codex/framework-modules/modules/identity-context.json` | Descriptor for project/repository identity and isolation. |
| `.gpt-codex/framework-modules/modules/role-communication.json` | Descriptor for role taxonomy and instruction/result protocol. |
| `.gpt-codex/framework-modules/modules/navigation-continuity.json` | Descriptor for Project Map, Resume, and continuation. |
| `.gpt-codex/framework-modules/modules/git-continuity.json` | Descriptor for revision and synchronization continuity. |
| `.gpt-codex/framework-modules/modules/release-projection.json` | Descriptor for consumer projection and release authority. |
| `.gpt-codex/framework-modules/modules/framework-validation.json` | Descriptor for validation orchestration only. |
| `.gpt-codex/schemas/framework-module-registry.schema.json` | JSON Schema for the minimal Registry document. |
| `.gpt-codex/schemas/framework-module.schema.json` | JSON Schema for the exact 17-field module descriptor. |
| `.gpt-codex/scripts/framework_module_routing.py` | Loader, structural validator, ownership resolver, route classifier, and required-test resolver. |
| `.gpt-codex/tests/test_framework_module_schemas.py` | Schema shape, authority, status, and exact descriptor-field tests. |
| `.gpt-codex/tests/test_framework_module_routing.py` | Registry loading, dependencies, selectors, ownership, route outcomes, and cross-module tests. |
| `.gpt-codex/tests/test_framework_module_validation.py` | `validate_framework.py`, Project Map, Role authority, documentation, and projection boundary regressions. |

### Modify

| Path | Purpose |
| --- | --- |
| `.gpt-codex/scripts/validate_framework.py` | Invoke Registry validation as framework validation without taking ownership of module rules. |
| `AGENTS.md` | Add responsibility-first Framework Registry routing guidance while preserving existing execution routing. |
| `.gpt-codex/README.md` | Document the Registry/Project Map boundary and deterministic route outcomes. |
| `.gpt-codex/release/consumer-projection-manifest.json` | Classify Design, Plan, Registry, descriptor, schema, routing, and new test paths explicitly. |
| `.gpt-codex/tests/test_consumer_projection.py` | Assert complete management-path classification and no accidental consumer projection. |
| `.gpt-codex/tests/test_consumer_runtime_closure.py` | Assert the projected runtime stays independent from management-only Registry assets. |
| `.gpt-codex/tests/test_navigation_schema.py` | Add a regression that Project Map authority remains derived. |
| `.gpt-codex/tests/test_role_authority.py` | Add a regression that Registry metadata cannot authorize execution. |

### Deliberately unchanged

`.gpt-codex/KERNEL.md`, `VERSION`, `.gpt-codex/CONTROL.json`,
`.gpt-codex/STATE.json`, `.gpt-codex/schemas/project-map.schema.json`,
`.gpt-codex/schemas/module-map.schema.json`, `.gpt-codex/scripts/project_navigation.py`,
`.gpt-codex/scripts/continuity_resume.py`, `.gpt-codex/scripts/validate_project.py`,
all existing release realization records, and `dist/*` remain unchanged. The
existing navigation and project validation contracts are tested for
compatibility rather than repurposed.

## Public implementation interfaces

Task 3 defines these exact names and signatures. Later tasks must use them
without renaming or adding speculative routing concepts:

```python
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ModuleRoutingError(ValueError):
    code: str
    details: dict[str, Any]

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None: pass


@dataclass(frozen=True)
class RouteDecision:
    outcome: str
    primary_module: str | None
    affected_modules: tuple[str, ...]
    why_cross_module: str | None
    contracts_affected: tuple[str, ...]
    invariants_affected: tuple[str, ...]
    required_tests: tuple[str, ...]


def load_registry(root: Path) -> dict[str, Any]: pass


def load_module_descriptor(root: Path, descriptor_path: str) -> dict[str, Any]: pass


def validate_registry(
    root: Path,
    registry: Mapping[str, Any] | None = None,
) -> list[str]: pass


def classify_changed_assets(
    root: Path,
    registry: Mapping[str, Any],
    planned_assets: Sequence[str],
) -> dict[str, tuple[str, ...]]: pass


def detect_cross_module_change(
    primary_module: str,
    affected_modules: Sequence[str],
    *,
    contracts_affected: Sequence[str] = (),
    invariants_affected: Sequence[str] = (),
) -> RouteDecision: pass


def required_tests_for_change(
    root: Path,
    registry: Mapping[str, Any],
    module_ids: Sequence[str],
) -> tuple[str, ...]: pass


def route_responsibility(
    root: Path,
    candidate_module_id: str,
    responsibility: str,
    *,
    planned_assets: Sequence[str] = (),
    contracts_affected: Sequence[str] = (),
    invariants_affected: Sequence[str] = (),
) -> RouteDecision: pass
```

`validate_registry` returns a de-duplicated list of the frozen failure codes
and never grants authority; it does not raise for invalid Registry content.
Direct loader calls and `route_responsibility` raise
`ModuleRoutingError(code, message, details mapping)` for a fail-closed
operation. `route_responsibility` requires `responsibility` to be an exact
member of the candidate descriptor's `RESPONSIBILITIES` after the candidate is
verified as registered and `ACTIVE`.
`classify_changed_assets` returns normalized asset keys mapped to the matching
primary-owner IDs; callers classify zero and multiple owners using the frozen
failure codes. `RouteDecision.outcome` is one of the three route outcomes.
`MODULE_ROUTE` represents a `SINGLE_MODULE_CHANGE` when exactly one owner and
one module boundary are involved.

## Task 1: Registry and descriptor schemas

**Files:**

- Create: `.gpt-codex/schemas/framework-module-registry.schema.json`
- Create: `.gpt-codex/schemas/framework-module.schema.json`
- Create: `.gpt-codex/tests/test_framework_module_schemas.py`
- Read-only reference: `.gpt-codex/schemas/project-map.schema.json`
- Read-only reference: `.gpt-codex/schemas/module-map.schema.json`

**Interfaces:**

- Consumes: JSON Schema draft 2020-12 conventions already used by the Project Map and Module Map schemas.
- Produces: two schema documents with exact IDs `gpt-codex/framework-module-registry-v1` and `gpt-codex/framework-module-v1`, consumed by Tasks 2–5.

- [ ] **Step 1: Write the failing schema tests.**

Create tests that fail while the two schema files are absent and then fail on
any contract drift. The tests must assert the following concrete properties:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / ".gpt-codex" / "schemas"
MODULE_FIELDS = frozenset({
    "MODULE_ID", "VERSION", "PURPOSE", "RESPONSIBILITIES",
    "NON_RESPONSIBILITIES", "OWNED_ASSETS", "ENTRY_POINTS", "INPUTS",
    "OUTPUTS", "DEPENDS_ON", "USED_BY", "INVARIANTS", "PERMISSIONS",
    "CHANGE_RISK", "REQUIRED_TESTS", "RELATED_MODULES",
})


def load_schema(name: str) -> dict[str, object]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def test_registry_schema_freezes_authority_and_status(self):
    schema = load_schema("framework-module-registry.schema.json")
    self.assertEqual(schema["$id"], "gpt-codex/framework-module-registry-v1")
    self.assertEqual(schema["properties"]["schema_version"], {"const": 1})
    self.assertEqual(
        schema["properties"]["authority"],
        {"const": "FRAMEWORK_MODULE_REGISTRY"},
    )
    self.assertEqual(
        schema["properties"]["modules"]["items"]["properties"]["status"]["enum"],
        ["ACTIVE", "INACTIVE"],
    )


def test_module_schema_has_exact_descriptor_fields(self):
    schema = load_schema("framework-module.schema.json")
    expected = {
        "MODULE_ID", "VERSION", "PURPOSE", "RESPONSIBILITIES",
        "NON_RESPONSIBILITIES", "OWNED_ASSETS", "ENTRY_POINTS", "INPUTS",
        "OUTPUTS", "DEPENDS_ON", "USED_BY", "INVARIANTS", "PERMISSIONS",
        "CHANGE_RISK", "REQUIRED_TESTS", "RELATED_MODULES",
    }
    self.assertEqual(set(schema["required"]), expected)
    self.assertEqual(set(schema["properties"]), expected)
    self.assertTrue(schema["additionalProperties"] is False)


def test_owned_asset_schema_is_exact_two_field_object(self):
    owned = load_schema("framework-module.schema.json")["properties"]["OWNED_ASSETS"]
    item = owned["items"]
    self.assertEqual(set(item["properties"]), {"type", "value"})
    self.assertEqual(item["required"], ["type", "value"])
    self.assertFalse(item["additionalProperties"])
    self.assertEqual(
        item["properties"]["type"]["enum"],
        ["EXACT_PATH", "PATH_PREFIX", "LOGICAL_ASSET"],
    )
```

- [ ] **Step 2: Run the schema tests and confirm the failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_schemas.py' -v
```

Expected: `FAIL` because the two schema files do not exist yet.

- [ ] **Step 3: Create the Registry schema.**

Use JSON Schema draft 2020-12 with `additionalProperties: false`. Define:

```text
required = ["schema_version", "authority", "framework_version", "modules"]
schema_version = const 1
authority = const FRAMEWORK_MODULE_REGISTRY
framework_version = non-empty SemVer string
modules = array of objects
module entry required = ["module_id", "descriptor", "status"]
module_id = non-empty string
descriptor = non-empty safe relative .json path string
status = enum ["ACTIVE", "INACTIVE"]
```

The schema describes shape. The Python validator in Task 3 enforces unique
module IDs, descriptor existence, path safety, descriptor identity, and
cross-document relationships.

- [ ] **Step 4: Create the descriptor schema.**

Use JSON Schema draft 2020-12 with exactly the 17 required properties and no
additional properties. Use these types:

```text
MODULE_ID, VERSION, PURPOSE, CHANGE_RISK = non-empty strings
RESPONSIBILITIES, NON_RESPONSIBILITIES, ENTRY_POINTS, INPUTS, OUTPUTS,
DEPENDS_ON, USED_BY, INVARIANTS, PERMISSIONS, REQUIRED_TESTS, RELATED_MODULES
  = arrays of strings
OWNED_ASSETS = array of exact two-field selector objects
```

`OWNED_ASSETS.items.properties.type` is the three-value enum and
`OWNED_ASSETS.items.properties.value` is a non-empty string. The schema must
not add lifecycle, maturity, scoring, owner-count, confidence, or field-level
ownership properties. `PERMISSIONS` is an array of strings and does not encode
execution actions.

- [ ] **Step 5: Run focused schema tests and the existing schema regressions.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_schemas.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_navigation_schema.py' -v
```

Expected: PASS with the new schema contract and unchanged Project Map authority
assertions.

- [ ] **Step 6: Commit the schema task.**

```bash
git add .gpt-codex/schemas/framework-module-registry.schema.json .gpt-codex/schemas/framework-module.schema.json .gpt-codex/tests/test_framework_module_schemas.py
git commit -m "feat: add framework module schemas"
```

## Task 2: Registry data and the seven initial descriptors

**Files:**

- Create: `.gpt-codex/framework-modules/REGISTRY.json`
- Create: `.gpt-codex/framework-modules/modules/framework-core.json`
- Create: `.gpt-codex/framework-modules/modules/identity-context.json`
- Create: `.gpt-codex/framework-modules/modules/role-communication.json`
- Create: `.gpt-codex/framework-modules/modules/navigation-continuity.json`
- Create: `.gpt-codex/framework-modules/modules/git-continuity.json`
- Create: `.gpt-codex/framework-modules/modules/release-projection.json`
- Create: `.gpt-codex/framework-modules/modules/framework-validation.json`
- Create: `.gpt-codex/tests/test_framework_module_routing.py`

**Interfaces:**

- Consumes: Task 1 schema IDs and exact field sets.
- Produces: one Registry object and exactly seven `ACTIVE` descriptor entries, later loaded by `load_registry` and `load_module_descriptor`.

- [ ] **Step 1: Write failing Registry data tests.**

Add tests that load the JSON files directly and assert exact initial coverage:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".gpt-codex" / "framework-modules" / "REGISTRY.json"


MODULE_FIELDS = frozenset({
    "MODULE_ID", "VERSION", "PURPOSE", "RESPONSIBILITIES",
    "NON_RESPONSIBILITIES", "OWNED_ASSETS", "ENTRY_POINTS", "INPUTS",
    "OUTPUTS", "DEPENDS_ON", "USED_BY", "INVARIANTS", "PERMISSIONS",
    "CHANGE_RISK", "REQUIRED_TESTS", "RELATED_MODULES",
})


def test_registry_has_exact_initial_module_ids(self):
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    self.assertEqual(registry["authority"], "FRAMEWORK_MODULE_REGISTRY")
    self.assertEqual(
        [entry["module_id"] for entry in registry["modules"]],
        [
            "framework-core", "identity-context", "role-communication",
            "navigation-continuity", "git-continuity", "release-projection",
            "framework-validation",
        ],
    )
    self.assertTrue(all(entry["status"] == "ACTIVE" for entry in registry["modules"]))


def test_each_registered_descriptor_has_exact_identity_and_fields(self):
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected = set(MODULE_FIELDS)
    for entry in registry["modules"]:
        descriptor = json.loads((ROOT / entry["descriptor"]).read_text(encoding="utf-8"))
        self.assertEqual(descriptor["MODULE_ID"], entry["module_id"])
        self.assertEqual(set(descriptor), expected)
```

- [ ] **Step 2: Run the Registry tests and confirm the failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v
```

Expected: `FAIL` because the Registry and descriptor files do not exist yet.

- [ ] **Step 3: Create the minimal Registry.**

Use this exact global shape; do not duplicate descriptor bodies:

```json
{
  "schema_version": 1,
  "authority": "FRAMEWORK_MODULE_REGISTRY",
  "framework_version": "2.4.0",
  "modules": [
    {"module_id": "framework-core", "descriptor": ".gpt-codex/framework-modules/modules/framework-core.json", "status": "ACTIVE"},
    {"module_id": "identity-context", "descriptor": ".gpt-codex/framework-modules/modules/identity-context.json", "status": "ACTIVE"},
    {"module_id": "role-communication", "descriptor": ".gpt-codex/framework-modules/modules/role-communication.json", "status": "ACTIVE"},
    {"module_id": "navigation-continuity", "descriptor": ".gpt-codex/framework-modules/modules/navigation-continuity.json", "status": "ACTIVE"},
    {"module_id": "git-continuity", "descriptor": ".gpt-codex/framework-modules/modules/git-continuity.json", "status": "ACTIVE"},
    {"module_id": "release-projection", "descriptor": ".gpt-codex/framework-modules/modules/release-projection.json", "status": "ACTIVE"},
    {"module_id": "framework-validation", "descriptor": ".gpt-codex/framework-modules/modules/framework-validation.json", "status": "ACTIVE"}
  ]
}
```

- [ ] **Step 4: Create the seven descriptors with the frozen field set.**

Every descriptor uses `VERSION: "1.0.0"`, exact uppercase field names, and the
selector object form from the Design. Populate the responsibility and primary
asset map below. The listed paths are concrete repository-relative assets;
use `EXACT_PATH` for a file, `PATH_PREFIX` only for a directory-owned family,
and `LOGICAL_ASSET` only for a named contract that has no natural path.

| Module | Responsibilities and primary assets |
| --- | --- |
| `framework-core` | Kernel, CONTROL/STATE/WORK_UNIT contracts, Kernel rules, minimal governance, and the Framework Module Registry/routing mechanism; `.gpt-codex/KERNEL.md`, `.gpt-codex/README.md`, `AGENTS.md`, `.gpt-codex/schemas/control.schema.json`, `.gpt-codex/schemas/state.schema.json`, `.gpt-codex/schemas/work-unit.schema.json`, `.gpt-codex/project-template/CONTROL.template.json`, `.gpt-codex/project-template/STATE.template.json`, `.gpt-codex/project-template/WORK_UNIT.template.json`, `.gpt-codex/scripts/kernel_rules.py`, `.gpt-codex/builtins/INDEX.json`, `.gpt-codex/framework-modules/REGISTRY.json`, `.gpt-codex/framework-modules/modules/`, `.gpt-codex/schemas/framework-module-registry.schema.json`, `.gpt-codex/schemas/framework-module.schema.json`, `.gpt-codex/scripts/framework_module_routing.py`. `CHANGE_RISK` is `HIGH`. |
| `identity-context` | Project identity, `project_context_id`, repository binding, cross-project isolation, bootstrap identity, reconciliation; `.gpt-codex/scripts/context_binding.py`, `.gpt-codex/scripts/github_repository_binding.py`, and the `cross-project-context-binding` and `github-repository-binding` guardrail asset families. |
| `role-communication` | Exact roles, instruction/result ownership, instruction authority, review/finding/fix lifecycle, reviewer boundary, role observation, Handoff projection; `.gpt-codex/scripts/role_communication.py`, `.gpt-codex/scripts/instruction_envelope.py`, `.gpt-codex/scripts/result_return.py`, `.gpt-codex/schemas/instruction-envelope.schema.json`, `.gpt-codex/schemas/result-envelope.schema.json`, `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`, `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`, and the `handoff` built-in asset family. |
| `navigation-continuity` | Project Map, derived Module Map, map routing/freshness, Resume, FAST_RESUME, DELTA_RESUME, RECONCILIATION_REQUIRED, COLD_RESUME, context-window recovery; `.gpt-codex/scripts/project_navigation.py`, `.gpt-codex/scripts/continuity_resume.py`, the three existing navigation/resume schemas, their navigation/continuity templates, and the `repository-discovery` built-in asset family. |
| `git-continuity` | Local/remote revision continuity, exact SHA review binding, sync classifications, review-stage synchronization, append-only reviewed history, remote verification; `.gpt-codex/scripts/git_continuity.py`. |
| `release-projection` | Consumer projection, runtime closure, release archive/framework/metadata, publication contract, release evidence boundary; `.gpt-codex/scripts/consumer_projection.py`, `.gpt-codex/scripts/validate_consumer_projection.py`, `.gpt-codex/scripts/release_framework.py`, `.gpt-codex/scripts/release_archive.py`, `.gpt-codex/scripts/publication_contract.py`, `.gpt-codex/release/consumer-projection-manifest.json`, `.gpt-codex/extensions/skills/framework-release/`, `VERSION`, `.gpt-codex/CHANGELOG.md`, and `releases/`. `dist/` remains outside this Work Unit. |
| `framework-validation` | Validation orchestration only, including `validate_framework.py`, `validate_project.py`, self-hosting validation, and cross-module validation entrypoints; `.gpt-codex/scripts/validate_framework.py`, `.gpt-codex/scripts/validate_project.py`, and the validation orchestration test families. |

The seven descriptors must use these exact responsibility and interface
identifiers. `contracts_affected` accepts only identifiers from the primary
module's `OUTPUTS`; the matching consumer rows below place those same exact
identifiers in `INPUTS`.

| Module | Exact `RESPONSIBILITIES` member used by routing | Exact `INPUTS` | Exact `OUTPUTS` |
| --- | --- | --- | --- |
| `framework-core` | `framework governance`, `framework module registry routing` | `KERNEL_GOVERNANCE_INPUT` | `FRAMEWORK_MODULE_REGISTRY_CONTRACT`, `FRAMEWORK_GOVERNANCE_CONTRACT` |
| `identity-context` | `project and repository identity` | `FRAMEWORK_GOVERNANCE_CONTRACT` | `PROJECT_IDENTITY_CONTRACT` |
| `role-communication` | `role communication and instruction authority` | `FRAMEWORK_GOVERNANCE_CONTRACT`, `PROJECT_IDENTITY_CONTRACT` | `ROLE_COMMUNICATION_CONTRACT` |
| `navigation-continuity` | `project navigation and continuity` | `FRAMEWORK_GOVERNANCE_CONTRACT`, `PROJECT_IDENTITY_CONTRACT` | `PROJECT_NAVIGATION_CONTRACT`, `CONTINUITY_RESUME_CONTRACT` |
| `git-continuity` | `revision and synchronization continuity` | `FRAMEWORK_GOVERNANCE_CONTRACT` | `GIT_CONTINUITY_CONTRACT` |
| `release-projection` | `consumer projection and release authority` | `FRAMEWORK_GOVERNANCE_CONTRACT`, `GIT_CONTINUITY_CONTRACT`, `FRAMEWORK_VALIDATION_CONTRACT` | `CONSUMER_PROJECTION_CONTRACT` |
| `framework-validation` | `framework validation orchestration` | `FRAMEWORK_MODULE_REGISTRY_CONTRACT`, `PROJECT_IDENTITY_CONTRACT`, `ROLE_COMMUNICATION_CONTRACT`, `PROJECT_NAVIGATION_CONTRACT`, `GIT_CONTINUITY_CONTRACT`, `CONSUMER_PROJECTION_CONTRACT` | `FRAMEWORK_VALIDATION_CONTRACT` |

Use these dependency/consumer relationships so every edge is reciprocal. A
relationship means contract consumption, not ownership transfer:

| Module | `DEPENDS_ON` | `USED_BY` |
| --- | --- | --- |
| `framework-core` | `[]` | `identity-context`, `role-communication`, `navigation-continuity`, `git-continuity`, `release-projection`, `framework-validation` |
| `identity-context` | `framework-core` | `role-communication`, `navigation-continuity`, `framework-validation` |
| `role-communication` | `framework-core`, `identity-context` | `framework-validation` |
| `navigation-continuity` | `framework-core`, `identity-context` | `framework-validation` |
| `git-continuity` | `framework-core` | `release-projection`, `framework-validation` |
| `release-projection` | `framework-core`, `git-continuity`, `framework-validation` | `framework-validation` |
| `framework-validation` | `framework-core`, `identity-context`, `role-communication`, `navigation-continuity`, `git-continuity`, `release-projection` | `release-projection` |

The release/validation cycle is representable because P0-2 validates references
and reciprocity but does not impose a DAG rule. Use nonempty
`RESPONSIBILITIES`, explicit `NON_RESPONSIBILITIES`, declared entry points and
interfaces, nonempty `REQUIRED_TESTS`, and the exact module-level
`PERMISSIONS` classifications `READ_ONLY_REFERENCE`, `CONSUMER_PROJECTED`,
`FRAMEWORK_DEVELOPMENT_ONLY`, and `RELEASE_MANAGED` only where applicable.

- [ ] **Step 5: Run Registry data and schema tests.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_schemas.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v
```

Expected: PASS with exactly seven registered descriptors, all `ACTIVE`, and no
duplicated descriptor body in `REGISTRY.json`.

- [ ] **Step 6: Commit the Registry data task.**

```bash
git add .gpt-codex/framework-modules .gpt-codex/tests/test_framework_module_routing.py
git commit -m "feat: register initial framework modules"
```

## Task 3: Structural validation, ownership, and dependency integrity

**Files:**

- Create: `.gpt-codex/scripts/framework_module_routing.py`
- Modify: `.gpt-codex/tests/test_framework_module_routing.py`

**Interfaces:**

- Consumes: Task 1 schemas and Task 2 Registry/descriptors.
- Produces: `ModuleRoutingError`, `load_registry`, `load_module_descriptor`, `validate_registry`, `classify_changed_assets`, and `required_tests_for_change` with the signatures in the Public implementation interfaces section.

- [ ] **Step 1: Write failing structural and ownership tests.**

Add tests for each required failure and selector rule. Use concrete temporary
Registry fixtures so every test can isolate one condition:

```python
import json
from collections.abc import Sequence
from pathlib import Path


def minimal_descriptor(
    module_id: str,
    *,
    owned_assets: tuple[dict[str, str], ...] = (),
    depends_on: tuple[str, ...] = (),
    used_by: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "MODULE_ID": module_id,
        "VERSION": "1.0.0",
        "PURPOSE": "fixture",
        "RESPONSIBILITIES": ["fixture responsibility"],
        "NON_RESPONSIBILITIES": ["fixture exclusion"],
        "OWNED_ASSETS": list(owned_assets),
        "ENTRY_POINTS": ["fixture entry"],
        "INPUTS": ["fixture input"],
        "OUTPUTS": ["fixture output"],
        "DEPENDS_ON": list(depends_on),
        "USED_BY": list(used_by),
        "INVARIANTS": ["fixture invariant"],
        "PERMISSIONS": ["READ_ONLY_REFERENCE"],
        "CHANGE_RISK": "LOW",
        "REQUIRED_TESTS": [".gpt-codex/tests/test_framework_module_routing.py"],
        "RELATED_MODULES": [],
    }


def write_registry_fixture(root: Path, descriptors: Sequence[dict[str, object]]) -> dict[str, object]:
    modules = []
    for descriptor in descriptors:
        module_id = str(descriptor["MODULE_ID"])
        relative = f".gpt-codex/framework-modules/modules/{module_id}.json"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(descriptor), encoding="utf-8")
        modules.append({"module_id": module_id, "descriptor": relative, "status": "ACTIVE"})
    return {
        "schema_version": 1,
        "authority": "FRAMEWORK_MODULE_REGISTRY",
        "framework_version": "2.4.0",
        "modules": modules,
    }


def test_missing_registry_raises_module_registry_invalid(self):
    with self.assertRaises(ModuleRoutingError) as caught:
        load_registry(self.root_without_registry)
    self.assertEqual(caught.exception.code, "MODULE_REGISTRY_INVALID")


def test_missing_descriptor_raises_module_descriptor_invalid(self):
    registry = {
        "schema_version": 1,
        "authority": "FRAMEWORK_MODULE_REGISTRY",
        "framework_version": "2.4.0",
        "modules": [{
            "module_id": "missing",
            "descriptor": ".gpt-codex/framework-modules/modules/missing.json",
            "status": "ACTIVE",
        }],
    }
    errors = validate_registry(self.root, registry)
    self.assertIn("MODULE_DESCRIPTOR_INVALID", errors)


def test_dependency_and_used_by_edges_must_be_reciprocal(self):
    registry = write_registry_fixture(
        self.root,
        [
            minimal_descriptor("a", depends_on=("b",)),
            minimal_descriptor("b"),
        ],
    )
    errors = validate_registry(self.root, registry)
    self.assertIn("MODULE_DEPENDENCY_INVALID", errors)


def test_zero_owner_is_unresolved_and_multiple_owners_conflict(self):
    no_owner = classify_changed_assets(self.root, self.registry, ["unregistered/file.json"])
    self.assertEqual(no_owner["unregistered/file.json"], ())
    with self.assertRaises(ModuleRoutingError) as caught:
        route_responsibility(
            self.root,
            "framework-core",
            "framework governance",
            planned_assets=["unregistered/file.json"],
        )
    self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")


def test_selector_paths_reject_absolute_and_parent_traversal(self):
    for value in ("/absolute/file", "C:/absolute/file", "safe/../file"):
        registry = write_registry_fixture(
            self.root,
            [minimal_descriptor(
                "a",
                owned_assets=({"type": "EXACT_PATH", "value": value},),
            )],
        )
        errors = validate_registry(self.root, registry)
        self.assertIn("MODULE_DESCRIPTOR_INVALID", errors)


def test_ownership_conflict_is_returned_by_validation(self):
    registry = write_registry_fixture(
        self.root,
        [
            minimal_descriptor(
                "a",
                owned_assets=({"type": "EXACT_PATH", "value": "shared/file.json"},),
            ),
            minimal_descriptor(
                "b",
                owned_assets=({"type": "EXACT_PATH", "value": "shared/file.json"},),
            ),
        ],
    )
    errors = validate_registry(self.root, registry)
    self.assertIn("MODULE_OWNERSHIP_CONFLICT", errors)


def test_registry_core_assets_have_exactly_framework_core_owner(self):
    assets = [
        ".gpt-codex/framework-modules/REGISTRY.json",
        ".gpt-codex/framework-modules/modules/framework-core.json",
        ".gpt-codex/schemas/framework-module-registry.schema.json",
        ".gpt-codex/schemas/framework-module.schema.json",
        ".gpt-codex/scripts/framework_module_routing.py",
    ]
    owners = classify_changed_assets(self.root, self.registry, assets)
    for asset in assets:
        self.assertEqual(owners[asset], ("framework-core",))
```

- [ ] **Step 2: Run the focused tests and confirm the failure.**

Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v`.

Expected: `FAIL` because `framework_module_routing.py` and its public
interfaces do not exist yet.

- [ ] **Step 3: Implement safe path normalization and selector matching.**

Implement private helpers that normalize `\` to `/`, reject absolute paths,
drive-prefixed paths, empty unsafe components, and any `..` component, and
compare path components rather than raw string prefixes. Implement exact
matching as equality and prefix matching as:

```python
candidate == prefix or candidate.startswith(prefix + "/")
```

after normalization, with the prefix itself normalized without a trailing
separator. For `LOGICAL_ASSET`, normalize the logical identifier as a stable
case-sensitive identifier and compare identifiers only; never infer physical
file overlap from it.

- [ ] **Step 4: Implement loader and structural validation.**

`load_registry(root)` reads `.gpt-codex/framework-modules/REGISTRY.json`,
requires an object with `authority == "FRAMEWORK_MODULE_REGISTRY"`,
`schema_version == 1`, and only `ACTIVE`/`INACTIVE` statuses. Invalid JSON or
shape raises `ModuleRoutingError("MODULE_REGISTRY_INVALID", "registry is invalid")`.

`load_module_descriptor(root, descriptor_path)` rejects unsafe paths, missing
files, invalid JSON, and non-object payloads with
`MODULE_DESCRIPTOR_INVALID`. `validate_registry(root, registry=None)` checks
the following conditions and returns a de-duplicated list of frozen failure
codes in this order; it does not raise for any of them:

```text
unique module_id
descriptor exists
descriptor module_id matches registry entry
descriptor has exactly the 17 fields
descriptor selector objects have exactly type/value
dependency references resolve
USED_BY / DEPENDS_ON consistency
ownership selector paths are safe
required-test references resolve to files or stable test identifiers
```

The implementation appends each code at most once, in the order
`MODULE_REGISTRY_INVALID`, `MODULE_DESCRIPTOR_INVALID`,
`MODULE_DEPENDENCY_INVALID`, and `MODULE_OWNERSHIP_CONFLICT`, while preserving
the frozen vocabulary. `MODULE_NOT_REGISTERED`, `MODULE_ROUTE_UNRESOLVED`, and
`CROSS_MODULE_CHANGE_REQUIRED` are route outcomes or route-time failures rather
than Registry-content validation errors. When `registry` is omitted and the
direct Registry loader raises `MODULE_REGISTRY_INVALID`, `validate_registry`
catches that loader error and returns the code in its list.

Missing Registry entries produce `MODULE_NOT_REGISTERED` at route lookup time;
missing descriptor files remain `MODULE_DESCRIPTOR_INVALID`. `INACTIVE` is
valid registered data but is not a normal route target.

- [ ] **Step 5: Implement ownership conflict detection.**

For different primary owners, return `MODULE_OWNERSHIP_CONFLICT` when any of
these component-aware conditions hold:

```text
EXACT_PATH(A) vs EXACT_PATH(A)
PATH_PREFIX(P) vs EXACT_PATH(X), X inside P
PATH_PREFIX(P1) vs PATH_PREFIX(P2), either prefix contains the other
LOGICAL_ASSET(L) vs LOGICAL_ASSET(L), normalized logical IDs identical
```

Do not conflict `foo/bar` with `foo/bar2`. Do not conflict physical paths
because a logical identifier happens to resemble a path. A same-owner repeated
selector does not create multi-owner ambiguity, but duplicate selector data
must remain normalized and deterministic.

`classify_changed_assets` returns all matching owner IDs for each planned asset.
For a planned framework mutation, exactly zero owners is
`MODULE_ROUTE_UNRESOLVED`, exactly one owner is eligible to continue, and more
than one owner is `MODULE_OWNERSHIP_CONFLICT`. Never assign an unclassified
asset to the candidate module. The initial Registry must resolve each new
Registry, descriptor-directory, Registry-schema, and routing-script asset to
the single `framework-core` owner; the focused test above proves this exact
coverage.

- [ ] **Step 6: Implement required-test resolution.**

`required_tests_for_change(root, registry, module_ids)` loads the listed
descriptors in stable module-ID order, unions `REQUIRED_TESTS`, normalizes
repository-relative paths, and returns a sorted tuple with no duplicates. A
missing or unsafe reference contributes `MODULE_DESCRIPTOR_INVALID` through
`validate_registry`; it is not silently ignored.

- [ ] **Step 7: Run ownership and dependency tests.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v
```

Expected: PASS, including absolute-path rejection, `..` rejection,
exact/exact conflict, exact-inside-prefix conflict, overlapping-prefix
conflict, component boundaries, logical-ID semantics, zero/multiple-owner
classification, reciprocal dependency checks, and required-test resolution.

- [ ] **Step 8: Commit the structural validation task.**

```bash
git add .gpt-codex/scripts/framework_module_routing.py .gpt-codex/tests/test_framework_module_routing.py
git commit -m "feat: validate framework module ownership"
```

## Task 4: Responsibility-first routing and cross-module classification

**Files:**

- Modify: `.gpt-codex/scripts/framework_module_routing.py`
- Modify: `.gpt-codex/tests/test_framework_module_routing.py`

**Interfaces:**

- Consumes: Task 3 loaders, validation, selector matching, owner resolution, and `RouteDecision`.
- Produces: `route_responsibility` and `detect_cross_module_change` with deterministic outcomes and required cross-module evidence fields.

- [ ] **Step 1: Write failing route tests.**

Add tests with a fixture containing one primary owner, two related modules, and
one consumed output contract:

```python
def test_single_module_route_is_returned_for_one_verified_owner(self):
    decision = route_responsibility(
        self.root,
        "framework-core",
        "framework governance",
        planned_assets=[".gpt-codex/KERNEL.md"],
    )
    self.assertEqual(decision.outcome, "MODULE_ROUTE")
    self.assertEqual(decision.primary_module, "framework-core")
    self.assertEqual(decision.affected_modules, ("framework-core",))


def test_missing_or_mismatched_responsibility_is_unresolved(self):
    for responsibility in ("", "not a declared responsibility"):
        with self.subTest(responsibility=responsibility):
            with self.assertRaises(ModuleRoutingError) as caught:
                route_responsibility(
                    self.root,
                    "framework-core",
                    responsibility,
                    planned_assets=[".gpt-codex/KERNEL.md"],
                )
            self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")


def test_reading_a_dependency_does_not_make_a_change_cross_module(self):
    decision = route_responsibility(
        self.root,
        "role-communication",
        "role communication and instruction authority",
        planned_assets=[".gpt-codex/scripts/role_communication.py"],
    )
    self.assertEqual(decision.outcome, "MODULE_ROUTE")


def test_consumed_output_contract_requires_cross_module_change(self):
    decision = route_responsibility(
        self.root,
        "role-communication",
        "role communication and instruction authority",
        planned_assets=[".gpt-codex/schemas/instruction-envelope.schema.json"],
        contracts_affected=["ROLE_COMMUNICATION_CONTRACT"],
    )
    self.assertEqual(decision.outcome, "CROSS_MODULE_CHANGE_REQUIRED")
    self.assertEqual(decision.primary_module, "role-communication")
    self.assertIn("role-communication", decision.affected_modules)
    self.assertIn("framework-validation", decision.affected_modules)
    self.assertEqual(decision.contracts_affected, ("ROLE_COMMUNICATION_CONTRACT",))
    self.assertTrue(decision.required_tests)


def test_undeclared_contract_does_not_guess_a_consumer(self):
    with self.assertRaises(ModuleRoutingError) as caught:
        route_responsibility(
            self.root,
            "role-communication",
            "role communication and instruction authority",
            planned_assets=[".gpt-codex/scripts/role_communication.py"],
            contracts_affected=["UNDECLARED_CONTRACT"],
        )
    self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")


def test_declared_output_without_consumers_remains_single_module(self):
    decision = route_responsibility(
        self.root,
        "navigation-continuity",
        "project navigation and continuity",
        planned_assets=[".gpt-codex/scripts/continuity_resume.py"],
        contracts_affected=["CONTINUITY_RESUME_CONTRACT"],
    )
    self.assertEqual(decision.outcome, "MODULE_ROUTE")
    self.assertEqual(decision.affected_modules, ("navigation-continuity",))


def test_inactive_or_unregistered_candidate_fails_closed(self):
    for candidate in ("inactive-module", "not-registered"):
        with self.assertRaises(ModuleRoutingError) as caught:
            route_responsibility(self.root, candidate, "unregistered responsibility")
        self.assertIn(caught.exception.code, {"MODULE_ROUTE_UNRESOLVED", "MODULE_NOT_REGISTERED"})
```

- [ ] **Step 2: Run route tests and confirm the failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v
```

Expected: `FAIL` because route classification has not been implemented.

- [ ] **Step 3: Implement `detect_cross_module_change`.**

`route_responsibility` matches each `contracts_affected` value exactly against
the primary descriptor's `OUTPUTS`. If an identifier is absent there, return
`MODULE_ROUTE_UNRESOLVED`. For every exact primary output match, collect
`ACTIVE` modules whose `INPUTS` contain the same identifier. Require each
consumer to list the primary module in `DEPENDS_ON`; an inconsistent consumer
relationship is reported by `validate_registry` before routing. Return
`RouteDecision.outcome == "CROSS_MODULE_CHANGE_REQUIRED"` only when at least
one consumer is found or a foreign owned asset is already in the affected set.
An empty consumer set with no foreign owned asset remains `MODULE_ROUTE`.
`invariants_affected` is evidence metadata only and never creates another
affected module. Pass the resolved affected-module IDs and exact contract IDs
to `detect_cross_module_change`, which only classifies the already-established
impact and does not perform additional guessing. Populate:

```text
PRIMARY_MODULE       → primary_module
AFFECTED_MODULES     → affected_modules
WHY_CROSS_MODULE     → why_cross_module
CONTRACTS_AFFECTED   → contracts_affected
INVARIANTS_AFFECTED  → invariants_affected
REQUIRED_TESTS       → required_tests
```

For a single-module route, return `MODULE_ROUTE`, one primary/affected module,
and the primary module's required tests. Read-only dependency use is not a
cross-module mutation. An internal implementation change that preserves a
consumed contract remains `MODULE_ROUTE` and represents
`SINGLE_MODULE_CHANGE`. The contract values in `RouteDecision` remain the
exact stable identifiers supplied by the caller, and affected modules are
deduplicated in stable module-ID order.

- [ ] **Step 4: Implement `route_responsibility`.**

The function must execute this bounded order:

```text
load_registry
→ validate_registry
→ nonempty validation errors → raise the first frozen code in validation order
→ verify candidate is registered
→ require candidate status ACTIVE
→ load candidate descriptor
→ require exact responsibility member
→ resolve planned asset owners
→ zero owners → MODULE_ROUTE_UNRESOLVED
→ multiple owners → MODULE_OWNERSHIP_CONFLICT
→ match declared output contracts to exact ACTIVE consumer inputs
→ classify single/cross-module outcome
```

GPT's candidate module ID is a proposal. The Registry verifies its existence,
status, descriptor identity, exact declared responsibility, ownership, and
dependency structure. The function must not scan unrelated repository
directories, rank candidates, infer a new module, score confidence, or
silently route an unclassified asset.

- [ ] **Step 5: Run route and cross-module tests.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_routing.py' -v
```

Expected: PASS for `MODULE_ROUTE`, `CROSS_MODULE_CHANGE_REQUIRED`,
`MODULE_ROUTE_UNRESOLVED`, inactive/unregistered behavior, required evidence
fields, and the no-scan/no-guess boundary.

- [ ] **Step 6: Commit the routing task.**

```bash
git add .gpt-codex/scripts/framework_module_routing.py .gpt-codex/tests/test_framework_module_routing.py
git commit -m "feat: route framework changes by module responsibility"
```

### Future P0-2 Implementation Work Unit declaration

The later implementation must be opened as one explicit cross-module Work Unit
with the following routing evidence. This declaration is planning data only and
does not authorize implementation in the current Plan fix.

```text
PRIMARY_MODULE:
framework-core

AFFECTED_MODULES:
framework-validation
release-projection

WHY_CROSS_MODULE:
framework-core introduces the Registry/routing authority; framework-validation integrates its checks; release-projection classifies and preserves its management/consumer boundary.

CONTRACTS_AFFECTED:
FRAMEWORK_MODULE_REGISTRY_CONTRACT

INVARIANTS_AFFECTED:
Registry does not grant execution authority
Project Map remains DERIVED_NAVIGATION_INDEX
consumer projection remains independent

REQUIRED_TESTS:
union the REQUIRED_TESTS from framework-core, framework-validation, and release-projection descriptors, then add:
.gpt-codex/tests/test_framework_module_schemas.py
.gpt-codex/tests/test_framework_module_routing.py
.gpt-codex/tests/test_framework_module_validation.py
.gpt-codex/tests/test_consumer_projection.py
.gpt-codex/tests/test_consumer_runtime_closure.py
.gpt-codex/tests/test_navigation_schema.py
.gpt-codex/tests/test_role_authority.py
```

`FRAMEWORK_MODULE_REGISTRY_CONTRACT` is the only contract in this Work Unit's
`CONTRACTS_AFFECTED`: it is an `OUTPUTS` identifier of `framework-core` and an
exact `INPUTS` identifier of `framework-validation`. `release-projection`
remains affected independently because the implementation mutates its foreign
owned asset `.gpt-codex/release/consumer-projection-manifest.json`; that asset
impact does not invent a `framework-core` output contract.

Repository inspection has already identified the other planned mutations:
framework-core owns the Registry mechanism and framework documentation,
framework-validation owns validator and compatibility checks, and
release-projection owns the manifest/projection boundary. If implementation
inspection finds an additional owned asset outside those three modules, the
Work Unit must add that module to `AFFECTED_MODULES` before mutation.

### Gate A: Core Registry/schema/ownership/routing review

At this point the persistent `CODEX_IMPLEMENTER` requests one milestone review.
The `CODEX_REVIEWER` reads the exact revision, runs the focused schema and
routing tests, validates the Registry, and compares the implementation against
the frozen Design SHA. The Reviewer reports findings only; the Reviewer does
not repair. Any remediation is a new governed fix instruction to the same
Implementer and the same Reviewer re-reviews the new descendant revision.

## Task 5: Existing framework validator integration

**Files:**

- Modify: `.gpt-codex/scripts/validate_framework.py`
- Create: `.gpt-codex/tests/test_framework_module_validation.py`
- Read-only reference: `.gpt-codex/scripts/validate_project.py`

**Interfaces:**

- Consumes: Task 3 `validate_registry`, current framework validator `ROOT`, existing `KERNEL_VERSION`/`SCHEMA_VERSION`, and current validation output conventions.
- Produces: one framework-validation invocation of Registry checks; `validate_project.py` remains independent and does not require management-only Registry files in consumer projects.

- [ ] **Step 1: Write failing validator integration tests.**

Add tests that run the framework validator and verify Registry failures are
reported through the existing framework-validation entrypoint:

```python
def test_validate_framework_accepts_the_initial_registry(self):
    result = subprocess.run(
        [sys.executable, str(ROOT / ".gpt-codex/scripts/validate_framework.py")],
        capture_output=True,
        text=True,
    )
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("RESULT: PASS", result.stdout)


def test_validate_project_does_not_require_management_registry(self):
    source = (ROOT / ".gpt-codex/scripts/validate_project.py").read_text(encoding="utf-8")
    self.assertNotIn("framework_module_routing", source)
    self.assertNotIn("framework-modules/REGISTRY.json", source)
```

- [ ] **Step 2: Run the validator tests and confirm the failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py' -v
```

Expected: the Registry acceptance test fails because `validate_framework.py`
does not invoke the new Registry yet.

- [ ] **Step 3: Integrate Registry validation in `validate_framework.py`.**

Invoke the new routing validator only for the framework-management root. Because
`validate_framework.py` is already `CONSUMER_REQUIRED`, do not add a static
local import of the management-only routing module: use a guarded
`runpy.run_path` loader that first checks for
`.gpt-codex/framework-modules/REGISTRY.json`, then loads
`.gpt-codex/scripts/framework_module_routing.py` and calls the returned
`validate_registry` function with the framework root. The dynamic branch is
never executed in an extracted consumer root without the Registry.
The management root adds the Registry, seven descriptors, two Registry schemas,
and routing script to its required-file checks; an extracted consumer root
without the Registry skips that branch. Append each returned code as
`MODULE_REGISTRY: <code>` to the existing `errors` list. Keep the existing
version, catalog, Kernel, publication, and navigation checks unchanged. Do not
load Registry validation from `validate_project.py`; a consumer project must
remain valid without management-only Registry files.

- [ ] **Step 4: Add validator coverage for all integrity checks.**

Test corrupted temporary fixtures for unique IDs, authority/status, descriptor
identity, dependency references, reciprocal `USED_BY`/`DEPENDS_ON`, ownership
conflicts, safe selectors, and required-test references. Add one fixture with a
dependency cycle and assert validation succeeds when all references and
reciprocity are valid.

- [ ] **Step 5: Run focused and existing validator tests.**

Run `python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py' -v`,
`python -m unittest discover -s .gpt-codex/tests -p 'test_navigation_project_validation.py' -v`,
`python -m unittest discover -s .gpt-codex/tests -p 'test_validator_context_binding.py' -v`, and
`python .gpt-codex/scripts/validate_framework.py`.

Expected: PASS; the framework validator reports the Registry checks, while
Project Map authority and project validation remain independent.

- [ ] **Step 6: Commit validator integration.**

```bash
git add .gpt-codex/scripts/validate_framework.py .gpt-codex/tests/test_framework_module_validation.py
git commit -m "feat: integrate framework module validation"
```

## Task 6: Documentation and compatibility regressions

**Files:**

- Modify: `AGENTS.md`
- Modify: `.gpt-codex/README.md`
- Modify: `.gpt-codex/tests/test_framework_module_validation.py`
- Modify: `.gpt-codex/tests/test_navigation_schema.py`
- Modify: `.gpt-codex/tests/test_role_authority.py`

**Interfaces:**

- Consumes: Task 4 route outcomes and Task 5 validation integration.
- Produces: human routing guidance and regression evidence without changing Kernel, Project Map scripts/schemas, or Role Protocol authority.

- [ ] **Step 1: Write failing documentation and authority-boundary tests.**

Add exact phrase assertions:

Place the documentation phrase method in the new
`FrameworkModuleValidationTests` class, whose `ROOT` points at the repository
root. Place the authority method in the existing `RoleAuthorityTests` class and
import `route_responsibility` from the new routing script in that test module;
that class already supplies `load_validator()` and `self.instruction()` helpers.

```python
def test_framework_docs_describe_responsibility_first_registry_routing(self):
    corpus = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    corpus += (ROOT / ".gpt-codex/README.md").read_text(encoding="utf-8")
    for phrase in (
        "responsibility first, files second",
        "FRAMEWORK_MODULE_REGISTRY",
        "MODULE_ROUTE",
        "CROSS_MODULE_CHANGE_REQUIRED",
        "MODULE_ROUTE_UNRESOLVED",
        "Project Map remains DERIVED_NAVIGATION_INDEX",
    ):
        self.assertIn(phrase, corpus)


def test_registry_metadata_does_not_authorize_role_actions(self):
    decision = route_responsibility(
        ROOT.parent,
        "framework-core",
        "framework governance",
        planned_assets=[".gpt-codex/KERNEL.md"],
    )
    self.assertEqual(decision.outcome, "MODULE_ROUTE")
    validator = load_validator()
    errors = validator.validate_instruction_authority(
        self.instruction(
            executor_role="CODEX_REVIEWER",
            authorized_actions=["MUTATE_APPROVED_SCOPE"],
        ),
        current_state_revision=8,
    )
    self.assertIn("ROLE_AUTHORITY_CONFLICT", errors)
    self.assertNotIn("MUTATE_APPROVED_SCOPE", decision.required_tests)
```

Extend `test_navigation_schema.py` to assert the existing schema authority is
still `DERIVED_NAVIGATION_INDEX`, and extend `test_role_authority.py` to prove
the Registry cannot make a Reviewer mutate or make `PERMISSIONS` replace
Work Unit/role authority.

- [ ] **Step 2: Run the compatibility tests and confirm the documentation failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_navigation_schema.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_role_authority.py' -v
```

Expected: the new documentation phrase test fails until the bounded guidance
is added; existing Project Map and Role Protocol tests remain green.

- [ ] **Step 3: Add bounded routing guidance to `AGENTS.md`.**

Add a short section adjacent to execution/map routing that says framework
changes classify responsibility before files, use the Framework Module
Registry as the structural ownership authority, preserve Project Map as
`DERIVED_NAVIGATION_INDEX`, and fail closed on unresolved/conflicting routes.
State explicitly that Registry `PERMISSIONS` does not grant execution
authority and that existing Kernel, CONTROL, Work Unit, Guardrails, and Role
Protocol contracts remain authoritative.

- [ ] **Step 4: Add the same boundary to `.gpt-codex/README.md`.**

Document the Registry route outcomes and the distinction:

```text
Framework Registry → responsibility / ownership / dependency
Project Map        → project-local navigation / location / freshness
```

Do not describe the Registry as a dynamic AI router, a permission source, or a
consumer runtime requirement.

- [ ] **Step 5: Run documentation and compatibility tests.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_framework_module_validation.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_navigation_schema.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_role_authority.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_role_communication_taxonomy.py' -v
```

Expected: PASS with Project Map authority, route/freshness vocabulary, and
Role Communication authority unchanged.

- [ ] **Step 6: Commit documentation and compatibility regressions.**

```bash
git add AGENTS.md .gpt-codex/README.md .gpt-codex/tests/test_framework_module_validation.py .gpt-codex/tests/test_navigation_schema.py .gpt-codex/tests/test_role_authority.py
git commit -m "docs: document framework module routing boundary"
```

## Task 7: Consumer projection and runtime closure

**Files:**

- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Modify: `.gpt-codex/tests/test_consumer_projection.py`
- Modify: `.gpt-codex/tests/test_consumer_runtime_closure.py`
- Modify: `.gpt-codex/tests/test_framework_module_validation.py`

**Interfaces:**

- Consumes: Task 1–6 paths, existing `consumer_projection.py`, `validate_consumer_projection.py`, release packaging tests, and the frozen consumer boundary.
- Produces: explicit classification for every new path and a consumer projection that excludes management-only Registry authority.

- [ ] **Step 1: Write failing projection-closure tests.**

Add assertions that the manifest contains these exact classifications:

```python
expected_management_paths = {
    "docs/superpowers/specs/2026-09-13-framework-modular-architecture-routing-design.md": "DEVELOPMENT_HISTORY",
    "docs/superpowers/plans/2026-09-13-framework-modular-architecture-routing.md": "DEVELOPMENT_HISTORY",
    ".gpt-codex/framework-modules/REGISTRY.json": "MANAGEMENT_ONLY",
    ".gpt-codex/schemas/framework-module-registry.schema.json": "MANAGEMENT_ONLY",
    ".gpt-codex/schemas/framework-module.schema.json": "MANAGEMENT_ONLY",
    ".gpt-codex/scripts/framework_module_routing.py": "MANAGEMENT_ONLY",
    ".gpt-codex/tests/test_framework_module_schemas.py": "MANAGEMENT_ONLY",
    ".gpt-codex/tests/test_framework_module_routing.py": "MANAGEMENT_ONLY",
    ".gpt-codex/tests/test_framework_module_validation.py": "MANAGEMENT_ONLY",
}
for module_id in INITIAL_MODULE_IDS:
    expected_management_paths[
        f".gpt-codex/framework-modules/modules/{module_id}.json"
    ] = "MANAGEMENT_ONLY"
for path, classification in expected_management_paths.items():
    self.assertEqual(manifest["paths"][path], classification)
```

The same test must assert `audit_projection_paths(ROOT, manifest)` returns no
unknown or missing paths after all files from Tasks 1–6 exist. Runtime closure
must assert `.gpt-codex/scripts/framework_module_routing.py` and the seven
management descriptors are not in the `CONSUMER_REQUIRED` inventory.

- [ ] **Step 2: Run projection tests and confirm the known failure.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_runtime_closure.py' -v
```

Expected before the manifest edit: `unknown_paths` includes the Plan and new
Registry/schema/script/test paths. Do not clear this failure by weakening the
projection validator or skipping tests.

- [ ] **Step 3: Add explicit manifest classifications.**

Add `DEVELOPMENT_HISTORY` entries for the frozen Design and this Plan. Add
`MANAGEMENT_ONLY` entries for `REGISTRY.json`, all seven descriptor files, both
Registry schemas, `framework_module_routing.py`, and all new framework-module
test files. Keep existing consumer-required navigation/Kernel/README/AGENTS
paths unchanged. If a modified existing test or documentation path is already
listed, preserve its existing classification.

The management-only choice follows the frozen Design: P0-2 does not assume the
entire Registry ships to consumer projects. A future explicit projection design
may classify a generic runtime-relevant descriptor, but P0-2 does not do so.

- [ ] **Step 4: Verify runtime closure and contamination boundaries.**

Run:

```bash
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_projection.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_consumer_runtime_closure.py' -v
python -m unittest discover -s .gpt-codex/tests -p 'test_release_packaging.py' -v
```

Expected: `RESULT: PASS`, no unknown paths, no missing required paths, no
management identities in projected bytes, and identical staged/archive bytes
in the release packaging tests. The tests may use temporary archives; do not
write release artifacts to `dist/*`.

- [ ] **Step 5: Commit projection closure.**

```bash
git add .gpt-codex/release/consumer-projection-manifest.json .gpt-codex/tests/test_consumer_projection.py .gpt-codex/tests/test_consumer_runtime_closure.py .gpt-codex/tests/test_framework_module_validation.py
git commit -m "test: close framework module projection boundary"
```

## Task 8: Integrated acceptance and evidence

**Files:**

- No source files; this task is verification and evidence only.

**Interfaces:**

- Consumes: all committed implementation tasks and the exact accepted Design SHA.
- Produces: full-suite, validator, projection, compatibility, and Git evidence for Gate B. This task does not authorize release or publication.

- [ ] **Step 1: Verify the accepted Design binding and immutable ancestry.**

Run:

```bash
git merge-base --is-ancestor e6cd404aafb1c9122ad8f26ce7583aa3d73914ad HEAD
git cat-file -e e6cd404aafb1c9122ad8f26ce7583aa3d73914ad:docs/superpowers/specs/2026-09-13-framework-modular-architecture-routing-design.md
```

Expected: both commands exit 0. The Design file at the accepted SHA remains
unchanged.

- [ ] **Step 2: Run the complete framework test suite.**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p 'test_*.py'
```

Expected: the command reports its complete test count followed by `OK`, with zero failures and
zero errors. The implementation terminal condition is a complete PASS; a
projection failure is not accepted as a known deviation after Task 7.

- [ ] **Step 3: Run all required validators and regressions.**

Run:

```bash
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python -m unittest discover -s .gpt-codex/tests -p 'test_*.py' -v
git diff --check
```

Expected: every command exits 0; `KERNEL_VERSION` remains `2.0.0`, schema
generation remains `1`, publication/remote verification remains governed by
existing contracts, Project Map remains derived, and Role Communication
remains authoritative for execution roles.

- [ ] **Step 4: Produce Gate B evidence and stop before release.**

Record the exact local HEAD, remote branch HEAD, test count, validator output,
projection audit, changed-path list, and `git status --short --branch`. Confirm
that implementation acceptance does not claim release/publication and that no
`VERSION`, release realization record, or `dist/*` path changed.

## Review strategy

Gate A occurs after Task 4 because the core Registry contract, descriptor
loading, ownership semantics, dependency integrity, route outcomes, and
cross-module evidence are then independently testable. Gate B occurs after
Task 8 because only then are validator integration, documentation, Project Map
and Role compatibility, consumer projection closure, and complete verification
available.

Both gates use the same `CODEX_REVIEWER` by default. The Reviewer may report a
finding, but a finding never authorizes a fix. GPT must issue a new fix
instruction bound to the reviewed SHA and Work Unit before the persistent
Implementer changes anything. A fresh Reviewer is used only for explicit
escalation or an objectively independent review requirement.

## Plan self-review checklist

Before committing this Plan, verify each item against the frozen Design and
repository inspection:

1. Spec coverage: every Design requirement maps to a task or explicit global constraint.
2. File-map closure: every CREATE, MODIFY, and TEST path has a purpose and task.
3. Incomplete-item scan: the Plan contains no unbounded implementation placeholder or unresolved prose.
4. Interface consistency: all tasks use the same public function names, parameters, return types, outcome strings, and failure codes.
5. Scope check: no P0-3/P0-4/P0-5/P0-6 behavior or future module is implemented.
6. Authority check: Registry status and `PERMISSIONS` never grant execution authority.
7. Ownership check: selector representation, path components, logical IDs, zero owners, multiple owners, and incremental coverage are explicit.
8. Projection check: Design, Plan, seven descriptors, Registry, schemas, routing script, and new tests all have explicit future classifications.
9. Test closure: Task 8 requires the complete suite and all named validators to pass.
10. Reviewer cadence: Gate A and Gate B are milestone gates, not per-task agent or reviewer boundaries.
11. Design binding: exact accepted Design SHA `e6cd404aafb1c9122ad8f26ce7583aa3d73914ad` is present in the header and acceptance commands.

## Implementation exclusions

The future implementation must not create or modify:

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
automatic module lifecycle
dynamic plugin loading
automatic cross-module planning
routing confidence scoring
.gpt-codex/KERNEL.md
VERSION
release realization records
dist/*
```

The Plan ends at implementation acceptance evidence. It does not authorize
release, publication, tagging, merging to `main`, or a later roadmap feature.
