# AGENTS.md — GPT–Codex Framework v2.13.0

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

### Governed mutation entry

For Framework-governed work, durable mutation requires the existing project identity/state, authorized Work Unit and Instruction, applicable Guardrails, and a passing PRE-EXECUTION review before Execution Window A. Failure is `ANALYSIS_ONLY / DENY_MUTATION`; `IMPLEMENTER_CONTEXT != REVIEWER_CONTEXT` remains required. The current accepted Framework governs its self-modification, while a proposed rule is non-retroactive until its governed acceptance, validation, and integration lifecycle. Ordinary projects may provide execution, review, and feedback evidence but cannot evolve global Framework policy. The existing POST-EXECUTION `REVIEW_FINDING -> GPT/User decision -> FIX_INSTRUCTION -> re-review` lifecycle remains authoritative.

### Directory creation contract

`CREATE_DIRECTORY_DEFAULT = DENY`. Compare tracked directory prefixes in `BASE_GIT_TREE` and `CANDIDATE_GIT_TREE`. An existing prefix is `EXISTING_DIRECTORY_WRITE`; every candidate-only prefix is `NEW_DIRECTORY_CREATION`, including rename destinations. Deletions alone do not create directories. A broad parent scope never authorizes a new descendant.

Each new durable prefix requires a complete optional Work Unit `directory_creations` declaration and Work Unit plus Instruction scope for its tracked files. The declaration has `path`, `purpose`, `owner`, `content_type`, `authority_type`, `lifetime`, `consumer_visible`, `release_visible`, and `cleanup_policy`; it is not execution authorization. A new top-level prefix additionally requires accepted immutable Architecture/Design authority naming and justifying that semantic path. Missing or malformed authority yields `DIRECTORY_CREATION_DENIED` or `STRUCTURE_CHANGE_REQUIRED`.

Generic names (`new`, `final2`, `copy`, `backup`, `tmp`, `fix2`, `latest-final`) and repo-local candidate workspaces, temporary ZIP or unpacked archives, cache, scratch, and review output are denied as durable structure unless the accepted Design explicitly justifies the exact semantic path. Put ephemeral build and review output outside the repository.

After the later local workspace consolidation gate, the deterministic layout is `<WORKTREE_ROOT>/<repository-slug>/<work-unit-id>/` for implementation and `<WORKTREE_ROOT>/<repository-slug>/review-<work-unit-id>/` for independent review. `CURRENT_PHASE_DOES_NOT_MOVE_LOCAL_WORKSPACES`.

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

### Stage 1 execution shortcuts

Use the existing native builders in `instruction_envelope.py` and `result_return.py` to construct Work Unit candidates, PRE requests, Finding Results, correlated FIX Instructions and one compact immutable-locator handoff. Dry-validate construction before dispatch. A Work Unit candidate is DRAFT with execution denied; local canonical bytes, byte count and hashes are computed after generation. Explicit project authorization and genuine independent PRE remain necessary before durable materialization or execution.

For existing-authority metadata bundles use the Kernel Lightweight Management Transaction policy and `validate_lightweight_management_transaction`. Reuse one Work Unit and one PRE/POST pair; closure does not recursively create another cleanup Work Unit. Use risk-based focused/affected checks and actual user-path acceptance before release's single full suite. Include Codex self-proof for independent review; machine-built requests never issue PASS.

Deliver one self-contained human-readable Codex copy block with project/context, role, Work Unit, STATE revision, immutable Instruction locator, goal, scope, STOP conditions and return requirement. The block is presentation only; fresh resume and native gate still determine authority.

### Stage 2 incremental governance verification

Use `capture_authority_snapshot` / `reuse_authority_snapshot` for bounded verified resume facts and `validate_incremental_governed_entry` for an exact existing EXECUTION_INSTRUCTION plus genuine PRE. First verification uses the accepted native resolver, envelope/completion contracts, mutation entry and live bound GitHub remote. Reuse is process-local, DERIVED and REBUILDABLE; persisted JSON is never accepted as proof. The exact repository root/ID, HEAD, index, actual candidate bytes, CONTROL/STATE, relevant scope, extension/navigation sources, validator source and named evidence must match. Stale supplied proof fails closed; explicitly call fresh native verification to rebuild it. Changed running validator code requires a fresh process.

Executable entry always performs live remote identity and head verification, including reuse. `reference_verified_evidence` returns an immutable locator for committed unchanged named evidence; it grants no PASS or completion decision. Record local validation evidence once per exact relevant input and reuse its reference only while those inputs remain unchanged. Keep focused affected safety checks, real acceptance and independent POST; release still requires one full suite.

`build_state_sync_finalization` generates a STATE candidate only after exact-W independent POST and live verified W. It does not write STATE or complete a Work Unit. Apply explicit authorized closure to the same Work Unit, validate the resulting metadata bundle, publish P with a normal push, then call `verify_work_publication` for actual remote P and preserved W/P boundaries. Low-risk correction planning is advice for already owned docs/named evidence; candidate changes still invalidate proof and require native verification. Stage 2 reuse alone grants no permission to enter a later stage.

### Stage 3 machine-first context and recovery routing

Start a bounded read-only resume with `python FRAMEWORK_ROOT/.gpt-codex/scripts/continuity_resume.py --root PROJECT_ROOT --repository-id SELECTED_REPOSITORY_ID`. For bound projects, use the selected numeric GitHub identity; optional expected context ID/revision must agree with durable CONTROL/STATE. Framework management, Consumer and Unbound modes are derived from the actual Git root and native authority, never folder names or chat memory. A nested or ambiguous root, identity conflict, stale STATE/remote, partial governance or unresolved recovery evidence fails closed.

Normal resume loads CORE and referenced TASK context. HISTORY_CONTEXT and PROGRAM_CONTEXT are excluded by default; load an exact task-needed reference only through `--history-context-ref`, `--program-context-ref` or `--task-context-ref`. Consumer never loads Framework-management context. The compact `context_plan` and `human_handoff` describe the same selected route and next existing gate. No route authorizes mutation: NORMAL_BOUND still enters Core lifecycle/Instruction/PRE gates.

`RECOVERY_INDEX` is an immutable derived mapping to existing gates, not a project registry, memory store or new authority. STALE_STATE_OR_REMOTE requires existing live continuity verification, IDENTITY_MISMATCH hard-stops, REVIEW_FINDING reads only the exact STATE-owned committed Result and returns to GPT/User decision before the existing FIX chain, and RECONCILIATION_REQUIRED uses the existing reconciliation gate. UNBOUND returns the read-only bootstrap challenge gate; existing phase-two identity verification and business hard-stop remain mandatory. No project file is created by routing.

Retain Stage 1 native builders and Stage 2 process-local authority reuse. Context/checkpoint/routing or named evidence markers participate in existing candidate fingerprints; changed markers reject stale supplied proof and require fresh native verification. Use exact owned scope, focused safety tests, real Consumer/Unbound acceptance and independent PRE/POST. Stage 6 remains unauthorized.
