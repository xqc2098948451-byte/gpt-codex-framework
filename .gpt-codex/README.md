# GPT–Codex Framework v2.12.0

v2.0 is a **minimal Kernel + curated Built-ins + project extensions + evidence-based Harvest** framework.

It is intentionally smaller than v1.7. v1.x accumulated useful operating capabilities; v2.0 keeps only the contracts that every governed project needs and moves technology/project-specific behavior out of Kernel.

The v2.1.0 baseline remains the compatibility floor for existing projects.

## Recommended dual-root workspace

```text
workspace/
├── project/
│   ├── ... project files ...
│   └── .gpt-codex/
│       ├── PROJECT.md
│       ├── CONTROL.json
│       ├── STATE.json
│       ├── work/
│       ├── evidence/
│       └── extensions/
│           ├── skills/
│           ├── guardrails/
│           └── fitness/
│
└── gpt-codex-framework/
    └── .gpt-codex/
        ├── KERNEL.md
        ├── builtins/
        ├── harvest/
        ├── schemas/
        └── scripts/
```

`project/` is the project source of truth. The framework is advisory and reusable. Normal project execution does not modify framework Kernel or Built-ins.

## Consumer Workspace Setup

Use a fixed, unversioned Framework Source Folder beside each consumer project. `Project is authoritative.` `Framework is advisory.` Recommended fixed names are `gpt-codex-framework` or `framework-source`.

Do not bind a long-lived consumer workspace to `gpt-codex-framework-v2.0.2-bootstrap`, `gpt-codex-framework-v2.0.3-bootstrap`, or another versioned folder. The Framework version comes from `VERSION`, release metadata, and compatibility information; a Framework upgrade replaces the contents of the fixed folder in place.

During ordinary project development:

- `Framework Kernel` → `READ ONLY`.
- `Framework Built-ins` → `READ ONLY`.
- When a project adopts a Built-in, copy the versioned snapshot into the project-owned `.gpt-codex/extensions/` directory using the existing rules.
- Framework upgrades do not automatically modify the project.

Before any adoption or migration, run the read-only Framework Compatibility Scan. Continue to use only these results: `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`.

If a consumer currently uses a versioned source folder, migrate once: remove the old versioned auxiliary folder, add the fixed `framework-source` folder, save the Codex project configuration, and keep using that fixed folder for later Framework upgrades.

## Built-in adoption into the project

The framework catalog is a reusable source, not the project's live configuration. When GPT selects a Built-in, Codex normally copies a versioned snapshot into:

```text
PROJECT_ROOT/.gpt-codex/extensions/<kind>/<id>/
```

`CONTROL.json` records its Built-in origin/version/path/checksum. The project copy becomes the project's execution input, so the project remains self-contained. Framework upgrades later compare the project snapshot with newer Built-ins and recommend only relevant adoption changes. If a project materially customizes an adopted Built-in, treat the customized copy as project-local governance and export its normalized delta/semantics to Harvest when appropriate.

## What the Kernel knows

The Kernel knows only:

1. project adaptation;
2. Work Units;
3. state + revision;
4. authority / least privilege;
5. evidence + provenance;
6. Skill / Guardrail / Fitness contracts;
7. governance compilation/validation;
8. reconciliation;
9. progressive disclosure;
10. governance complexity control;
11. version compatibility and migration.

The Kernel does **not** know how Git, Docker, React, PostgreSQL, Prometheus, deployment platforms, or project-specific tests work. Those belong to Built-ins or project extensions.

## First project bootstrap

1. Place the project root and this framework root beside each other.
2. Give GPT `.gpt-codex/KERNEL.md`, `.gpt-codex/BOOTSTRAP_PROMPT.md`, and project requirements.
3. GPT asks Codex to run read-only repository discovery using the Built-in catalog.
4. GPT generates project `PROJECT.md`, `CONTROL.json`, and `STATE.json` using `.gpt-codex/project-template/`.
5. GPT produces a Built-in Reuse Report before creating any project-local extension.
6. If a real capability gap remains, GPT must pass the Extension Admission Gate before creating a project extension.
7. Project-local extensions are exported to the current project's Harvest Inbox namespace as normalized candidates.
8. Governance compile validation must pass before the project enters `AUTHORIZED`.

For v2.1.0, bootstrap generates an authoritative `PROJECT_CONTEXT_ID` in `CONTROL.json` and records the project name. The required `cross-project-context-binding` Guardrail is enabled only in `CONTROL.extensions.guardrails[]`. An unbound first bootstrap is read-only and returns a challenge; only the exact second challenge-bound request may create identity and then hard-stop before business work. See `MIGRATION_v2.0_to_v2.1.md` for legacy migration and cross-project protections.

For v2.2.1 GitHub continuity, an adopting project also records exactly three
durable `CONTROL.github` fields: `repository_id`, `repository_full_name`, and
`default_branch`. The local remote name is never project identity. New work
requires clean/synced preflight. An already-authorized active work unit may
continue locally during a remote outage and returns `LOCAL_COMPLETE` with
`SYNC_PENDING`; formal `PASS` requires the bounded W/P publication protocol
and live `TOOL_OBSERVED` verification of the remote ref head. A publication
candidate cannot claim `PASS`, `SYNCED`, or authoritative `COMPLETE`; the
management-only project uses `FRAMEWORK_MANAGEMENT` / `SELF_MANAGED` and may
self-host only cataloged Framework Built-ins.

## Map-first maintenance

For an existing governed project, Project Map = where to look, Resume = what is already known, and Git delta = what may be stale. Bind identity, use `PROJECT_MAP.json` to select candidate module maps, validate the Resume checkpoint and relevant Git delta, then read only the required files. Use Repository Discovery only for initial bootstrap, `MAP_MISS` scoped discovery, `MAP_PARTIAL` bounded discovery, or an explicit material re-baseline—not normal maintenance rediscovery.

## Framework module routing

For framework changes, responsibility first, files second. The
`FRAMEWORK_MODULE_REGISTRY` records structural responsibility, ownership, and
dependency. Route outcomes are `MODULE_ROUTE` for a bounded module change,
`CROSS_MODULE_CHANGE_REQUIRED` when more than one module boundary is affected,
and `MODULE_ROUTE_UNRESOLVED` when ownership or responsibility cannot be
resolved safely.

```text
Framework Registry → responsibility / ownership / dependency
Project Map        → project-local navigation / location / freshness
```

Project Map remains DERIVED_NAVIGATION_INDEX. Registry `PERMISSIONS` !=
execution authorization; execution authority stays with the Kernel, CONTROL,
Work Unit, Guardrails, and Role Protocol contracts.

## Framework upgrade

When the framework root changes from e.g. v2.0 to v2.1, the project is **not** automatically migrated. GPT asks Codex to run a read-only compatibility evaluation and returns one of:

- `NO_ACTION`
- `OPTIONAL_REUSE`
- `RECOMMENDED_UPGRADE`
- `REQUIRED_MIGRATION`
- `CONFLICT`

`last_evaluated_version` may advance without changing `adopted_version`.

## Harvest and Built-in promotion

New project extensions are developed and fixed in their source project. The source project then exports a normalized Harvest Candidate into:

```text
framework/.gpt-codex/harvest/inbox/<project_id>/
```

Framework maintenance compares candidates across real projects. Candidates may become `SHARED_CANDIDATE` and then `BUILTIN` only through framework-maintenance review. Rejected candidates can be deleted from Harvest without deleting source-project extensions.

**Generalize after repetition, not before.**

## Machine authority

- `CONTROL.json` = project governance configuration and enabled extensions.
- `STATE.json` = current machine state, revision, blockers, and active Work Unit reference.
- Work Unit / Evidence / Extension / Result JSON = scoped machine contracts.
- Markdown = human explanation and project intent.
- Handoff = generated/derived view, not a source of truth.

Use `.gpt-codex/scripts/validate_framework.py` for framework/package validation and `.gpt-codex/scripts/validate_project.py` for a bootstrapped project's mechanical governance validation.

## Role communication and routing

`[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, and `[INFO]` are transport/routing hints, not machine authority; they do not replace envelope fields. The machine role, `authorized_actions`, project binding, state revision, and evidence are the enforceable contract.

The exact seven roles are `GPT_ORCHESTRATOR`, `GPT_REVIEWER`, `CODEX_IMPLEMENTER`, `CODEX_REVIEWER`, `USER_APPROVER`, `USER_LOCAL`, and `INFORMATION_ONLY`. `instruction_type` is owned by the Instruction Envelope; `result_message_type` is owned by the Result Envelope. No generic `message_type` exists.

The causal review lifecycle is `REVIEW_FINDING` → GPT/User decision → new `FIX_INSTRUCTION` → `CODEX_IMPLEMENTER` → `REVIEW_RESULT` re-review. Findings are evidence only and do not authorize fixes. Instruction issuance is not execution confirmation, and remote review visibility is not instruction delivery.

Legacy `[CODEX]` compatibility is bounded and fail-closed. Only an explicitly deterministic implementation/work-unit or review-bound context maps to one Codex role; unknown or ambiguous forms are rejected. Handoff remains a derived view of the Result Envelope and cannot authorize execution.

## Maintenance cadence

## Framework–Project separation

Framework publishes; Project decides. Framework publication flows to read-only compatibility evaluation, then an explicit Project decision, then separately authorized local mutation or migration. Compatibility evaluation never adopts or mutates. Project-local extensions and configuration remain Project-owned. Valid v2.5.0 projects using the current fixed Framework source remain `NO_MIGRATION`; a legacy project using a versioned auxiliary Framework folder requires `EXPLICIT_MIGRATION` to the fixed unversioned Framework source. No automatic propagation, adoption, or P0-4 mechanism exists. Fail-closed vocabulary: `CROSS_PROJECT_CONTEXT_MISMATCH`, `GITHUB_REPOSITORY_MISMATCH`, `PROJECT_IDENTITY_INVALID`, `PROJECT_AUTHORITY_BOUNDARY_VIOLATION`, `FRAMEWORK_ADOPTION_NOT_AUTHORIZED`, `MODULE_ROUTE_UNRESOLVED`, and `NAVIGATION_REPOSITORY_MISMATCH`.

See `MAINTENANCE.md`. The recommended default is a semiannual Harvest/Built-in/Kernel review rather than continuous framework churn.

## Framework management release packaging

The framework management project includes the project-local `framework-release` Skill at `.gpt-codex/extensions/skills/framework-release/`. `VERSION` is the release-version source of truth. Run `python .gpt-codex/scripts/release_framework.py` only after source changes are complete; it validates the framework/tests and writes the release ZIP, SHA-256 file, and release manifest to `dist/`. This Skill is management-only and is not copied into ordinary projects as a Built-in.

## Lightweight release archive

The framework management project keeps `releases/INDEX.json` and `releases/records/` as lightweight release history. Old ZIP binaries are intentionally not nested inside later releases. The release Skill cleans stale generated artifacts from `dist/` and emits only the current release ZIP, SHA-256 sidecar, and release manifest. Source history remains in Git/docs; release metadata survives even if old local ZIP copies are removed.

## Stage 1 workflow helpers (v2.9.0)

The helpers extend existing owners; they create no second STATE, approval registry, transport or Connector. Import them from `.gpt-codex/scripts` in the local governed execution context:

| Existing owner | Helper | Output and boundary |
| --- | --- | --- |
| instruction_envelope | build_work_unit_candidate | Native-schema DRAFT, local canonical bytes/size/hash; no execution authorization |
| instruction_envelope | build_pre_execution_review_request | Correlated request with exact mutation base revision, validated by shared request checks; no PASS |
| result_return | build_finding_result | Native Finding envelope with evidence and exact revision; no remediation decision |
| instruction_envelope | build_fix_instruction | Correlated FIX candidate after explicit accepted decision/basis; native execution re-resolves durable adjudication |
| instruction_envelope | render_compact_codex_handoff | One copy block, immutable Instruction locator and full identity/scope/STOP binding |
| git_continuity | plan_management_transaction / build_validation_plan | Bounded metadata/risk advice; no authority, cached exemption or review judgment |
| validate_project | validate_lightweight_management_transaction | Existing native entry/PRE plus committed authority, clean Git and live bound remote preflight |

For Work Unit materialization provide only the new semantic decision (goal, scope, acceptance, declared directories and immutable design/plan refs), current CONTROL/STATE and an immutable predecessor. Generate locally, inspect the candidate, apply explicit authorization through the existing project path, then dispatch machine-built PRE. The predecessor's approval never authorizes its successor; writing candidates to project files is itself governed. No long JSON transfer or manually supplied byte count/hash is needed.

A lightweight management bundle uses the already-authorized Work Unit and Instruction. Validate once before writing, retain one transaction evidence record, independently review the exact output, then publish/verify under existing publication authority. No successor cleanup bundle is required merely to tidy its own evidence. Source/authority creation and ref deletion use their existing explicit paths.

For Findings retain the original reproduction and immutable target; record the explicit accepted adjudication in STATE-registered evidence before FIX execution. A fresh implementer fixes the bounded path, then the reviewer checks original reproduction, related regression and touched invariants. Nonblocking issues may be recorded as ACCEPTED_LIMITATION with their practical effect.

Count review gates, newly required governance artifacts, human-mediated dispatches and repeated unchanged validation within a named comparable flow boundary. Report measured values separately from contract-derived baseline estimates. Do not imply that local Consumer acceptance is an adoption or verified publication of the Consumer business main.

### Bounded authority reuse (v2.10.0)

The existing native scripts offer `capture_authority_snapshot`, `reuse_authority_snapshot`, `reference_verified_evidence`, `validate_incremental_governed_entry`, `build_state_sync_finalization`, `verify_work_publication` and `plan_low_risk_correction`. Snapshots/attestations are immutable process-local derived objects. Supply the exact immutable EXEC Instruction locator, canonical PRE request/result paths and named evidence; no implicit active-Work-Unit discovery is used. An unchanged attestation avoids repeated authority parsing and native validation while still checking candidate freshness and live remote identity/head. A changed input rejects the old proof; re-enter without it to perform fresh native validation. FIX and reconciliation continue through their existing complete lifecycle entry.

Evidence reuse returns immutable references, not a copied authority store. W/P finalization builds a candidate only after independent POST and real remote W; explicit closure and actual remote P verification are separate steps. The real `price-action-learning` acceptance branch records successful reuse and invalidation, unchanged business regression, truthful measured counts and retained remote checks. That Stage 2 release added no daemon, generic cache or Connector.


### Machine-first bounded context (v2.12.0)

The existing `continuity_resume.py` now offers a read-only CLI and `route_project_context`. It derives Framework management / Consumer / Unbound modes from native identity and the actual Git root, verifies live bound remote identity and W/P continuity, and returns one deterministic route, minimal read plan and matching human handoff. NORMAL_BOUND enters existing Core gates; all routes report `mutation_authorized: false`.

Normal resume excludes HISTORY_CONTEXT and PROGRAM_CONTEXT before reading their bytes. Pass only exact task-needed references with `--task-context-ref`, `--program-context-ref` or `--history-context-ref`; Consumer cannot select management-only context. `RECOVERY_INDEX` maps known problems to existing gates and carries no independent facts or authority. Findings require the exact committed STATE-owned Result; unresolved or conflicting identities fail closed. Unbound routing returns the existing read-only bootstrap challenge and preserves phase-two business hard-stop without enrolling a project.

Real GitHub-bound Consumer and fresh Unbound paths, controlled stale/finding/reconciliation fixtures, bounded history-growth measurements and genuine independent reviews are recorded in Stage 3 evidence. Historical counters unavailable before this work are NOT_OBSERVABLE. Stage 1 builders and Stage 2 process-local proof reuse remain valid; changed context/routing markers invalidate old proof. No registry, database, daemon, Connector or Stage 4 feature is added.
