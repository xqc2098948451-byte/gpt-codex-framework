# AGENTS.md — GPT–Codex Framework v2.7.0

This repository is the **universal framework root**, not a business-project root.

## Ordinary project workspace

Expected layout:

```text
workspace/
├── project/                  # authoritative project root
└── gpt-codex-framework/      # auxiliary framework root
```

## Consumer Workspace Setup

Use one fixed, unversioned auxiliary Framework Source Folder for the lifetime of a consumer workspace:

```text
workspace/
├── project/                  # Project is authoritative.
└── gpt-codex-framework/      # Framework is advisory.
```

`gpt-codex-framework` and `framework-source` are stable folder-name examples. Do not bind a long-lived project configuration to `gpt-codex-framework-v2.0.2-bootstrap`, `gpt-codex-framework-v2.0.3-bootstrap`, or any other versioned Framework Source Folder; those names are not recommended for consumer bindings. Version and compatibility are read from `VERSION`, release metadata, and the compatibility scan.

Every v2.1.0 project also binds GPT instructions and Codex returns to the authoritative `project_context_id` in `CONTROL.json`. After identity migration, `cross-project-context-binding` is a required safety guardrail selected only through `CONTROL.extensions.guardrails[]`. Foreign or stale context is denied or analysis-only.

GitHub-continuity projects additionally bind exactly one stable
`CONTROL.github.repository_id`, with `repository_full_name` and
`default_branch` as durable metadata. `remote_name` is local runtime
observation or an instruction hint only. New mutating Work Units require
`NEW_WORK_PREFLIGHT=CLEAN_SYNCED`; an already-authorized active Work Unit may
degrade locally after temporary remote loss but can return only
`LOCAL_COMPLETE`/`SYNC_PENDING` until reconnect and live remote verification.

During ordinary project development, `Framework Kernel` and `Framework Built-ins` are `READ ONLY`. When a project adopts a Built-in, copy a versioned snapshot into the project's own `.gpt-codex/extensions/` directory according to the existing rules. A Framework upgrade updates the fixed source folder but does not automatically modify the project.

Before adopting or migrating, run the read-only Framework Compatibility Scan. Its result is one of `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`.

If a project is currently bound to a versioned folder, perform one migration: remove the old versioned auxiliary folder, add the fixed `framework-source` folder, save the Codex project configuration, and use that fixed folder for future Framework upgrades.

During ordinary project work:

- `project/` is authoritative and may be changed only within active authorization.
- `.gpt-codex/kernel/` and `.gpt-codex/builtins/` in the framework root are read-only.
- The current project may write only to `.gpt-codex/harvest/inbox/<project_id>/` in the framework root.
- Project Codex must never promote a Harvest Candidate to Built-in.
- Changes to project-local Skill / Guardrail / Fitness are made in the source project first, then exported as a normalized Harvest Candidate.

## Built-in adoption defaults to a **versioned snapshot copy into the project root**. GPT selects the useful Built-in; Codex copies its manifest/instructions into `project/.gpt-codex/extensions/<kind>/<id>/` and records framework origin/version in `CONTROL.json`. The framework copy remains immutable during ordinary project work.

Before creating any project extension

GPT/Codex must follow this order:

1. reuse a suitable Built-in;
2. reuse an existing project-native mechanism;
3. configure an existing capability;
4. compose existing capabilities;
5. degrade safely if the requirement still remains satisfied;
6. only then pass the Extension Admission Gate and create the smallest project-local extension.

Default decision: **DO NOT ADD**.

## Execution routing

Every requested action must identify its executor: `[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, or `[INFO]`. Unlabeled explanatory prose is not executable.

Before any copyable Codex execution instruction, GPT must show human-facing routing:

```text
【执行策略】<当前实际策略，例如：串行 / 并行>
【完成后是否需要批准】不需要 | 需要 GPT 判断 | 需要用户批准
```

Machine approval semantics remain `NONE | GPT_DECISION | USER_APPROVAL`. Returning evidence to GPT is not the same as user approval.

### Framework module routing

For framework maintenance, responsibility first, files second. Use the
`FRAMEWORK_MODULE_REGISTRY` as the structural authority for responsibility,
ownership, and dependency. A bounded route is reported as `MODULE_ROUTE`; a
change crossing module boundaries is `CROSS_MODULE_CHANGE_REQUIRED`; an
unknown or conflicting route is `MODULE_ROUTE_UNRESOLVED` and must fail closed.

The Framework Registry describes responsibility / ownership / dependency.
Project Map remains DERIVED_NAVIGATION_INDEX and describes project-local
navigation, location, and freshness. Registry `PERMISSIONS` != execution
authorization. Execution authority remains bounded by the Kernel, CONTROL,
Work Unit, Guardrails, and Role Protocol contracts.

### Role communication contract

`[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, and `[INFO]` are transport/routing hints, not machine authority; they do not replace envelope fields. The machine role, `authorized_actions`, project binding, state revision, and evidence remain authoritative.

The exact seven protocol roles are `GPT_ORCHESTRATOR`, `GPT_REVIEWER`, `CODEX_IMPLEMENTER`, `CODEX_REVIEWER`, `USER_APPROVER`, `USER_LOCAL`, and `INFORMATION_ONLY`. `instruction_type` belongs to the Instruction Envelope and `result_message_type` belongs to the Result Envelope. No generic `message_type` is used.

The finding lifecycle is `REVIEW_FINDING` evidence → GPT/User decision → new `FIX_INSTRUCTION` → `CODEX_IMPLEMENTER` → `REVIEW_RESULT` re-review. A finding never authorizes execution. Instruction issuance is not execution confirmation, and remote review visibility is not instruction delivery.

Legacy `[CODEX]` compatibility is bounded and fail-closed: only a deterministic implementation/work-unit or explicitly review-bound context maps to one Codex role; unknown or ambiguous legacy forms are rejected. Handoff is a derived view of Result Envelope evidence, not a source of authority.

## Kernel invariants

- Project is authoritative; Framework is advisory.
- Preinstalled does not mean enabled.
- Generalize after repetition, not before.
- Framework upgrades are evaluated, not propagated.
- A stale state revision must reconcile rather than overwrite.
- Model inference may guide investigation but must not impersonate authoritative evidence.
- Child execution permissions may narrow but never silently expand parent authorization.
- A project-specific capability does not belong in Kernel merely because it is useful.

## Map-first maintenance

- Project Map = where to look.
- Resume = what is already known.
- Git delta = what may be stale.
- For existing governed projects, bind identity, route through the Project Map and relevant module maps, validate Resume and the relevant Git delta, then read only required files.
- Repository Discovery is for initial bootstrap, `MAP_MISS` scoped discovery, `MAP_PARTIAL` bounded discovery, or explicit material re-baseline; it is not normal maintenance rediscovery.
