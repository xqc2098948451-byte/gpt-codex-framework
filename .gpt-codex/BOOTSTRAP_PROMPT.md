# GPT Bootstrap Prompt — Framework v2.4.0

You are bootstrapping or resuming a project using GPT–Codex Framework v2.4.0.

## Roots

Identify exactly two roots when available:

- `PROJECT_ROOT` — authoritative current project.
- `FRAMEWORK_ROOT` — auxiliary `gpt-codex-framework` directory.

Do not treat the framework root as the business project.

Before any business task, bind the active project by reading the authoritative `CONTROL.json` `project_context_id` and `project_name`. After v2.1.0 identity migration, `cross-project-context-binding` is a `REQUIRED_SAFETY_GUARDRAIL` selected from `CONTROL.extensions.guardrails[]`.

GitHub continuity is opt-in per project. Its stable identity is the three-field
`CONTROL.github` binding led by `repository_id`; `remote_name` remains a local
runtime hint. Run the read-only compatibility scan before migration, and never
select an ambiguous remote or create/replace a repository automatically.

## Consumer Workspace Setup

Add the Framework Source Folder once using a fixed, unversioned path such as `gpt-codex-framework` or `framework-source`. `Project is authoritative.` `Framework is advisory.` Do not bind the consumer workspace to names such as `gpt-codex-framework-v2.0.2-bootstrap` or `gpt-codex-framework-v2.0.3-bootstrap`; those are release artifact names, not long-lived source paths.

During ordinary project work, `Framework Kernel` and `Framework Built-ins` are `READ ONLY`. Adopted Built-ins are copied as versioned snapshots into the project-owned `.gpt-codex/extensions/` directory. Framework upgrades update the fixed source folder only and do not automatically modify the project.

Before any adoption or migration, run the read-only Framework Compatibility Scan and return exactly one of `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`.

For an existing versioned binding, migrate once: remove the old versioned auxiliary folder, add the fixed `framework-source` folder, save the Codex project configuration, and keep that fixed folder for future upgrades. Framework Management self-hosting is accepted only for the marked management project and cataloged Built-ins.

## Read first

Use progressive disclosure:

1. `FRAMEWORK_ROOT/.gpt-codex/KERNEL.md`
2. `FRAMEWORK_ROOT/.gpt-codex/builtins/INDEX.json`
3. project requirements/materials
4. existing `PROJECT_ROOT/.gpt-codex/PROJECT.md`, `CONTROL.json`, `STATE.json` if present
5. active Work Unit/extensions/evidence only when referenced

Do not load all Built-ins or historical docs by default.

## New project flow

For an unbound project, phase one of bootstrap is read-only: create no project file and return `BOOTSTRAP_CHALLENGE_ID` plus `BOOTSTRAP_CHALLENGE_REQUIRED`. Require the exact challenge in phase two; create and verify identity and required guardrail, then hard-stop. Never continue into a business task in the same bootstrap operation. For a legacy governed project, compare `BOOTSTRAP_TARGET_PROJECT_ID` to local `CONTROL.project_id`; mismatch is `CROSS_PROJECT_BOOTSTRAP_MISMATCH`.

1. Use the `repository-discovery` Built-in read-only to understand repository identity, technology, existing tools, tests, CI, constraints, and existing governance mechanisms.
2. Create a stable `project_id`. Folder name alone is not project identity.
3. Draft `PROJECT.md` from evidence and user intent.
4. Create the initial `PROJECT_MAP.json` and module maps from evidence and user intent.
5. Search Built-ins before designing project-local extensions.
6. Produce a `REUSE_REPORT` containing selected, not-applicable, and remaining capability gaps.
7. For each selected Built-in, direct Codex to copy a versioned snapshot from framework Built-ins into `PROJECT_ROOT/.gpt-codex/extensions/<kind>/<id>/` and record origin/version/path in `CONTROL.json`. Do not edit the framework Built-in.
8. Draft `CONTROL.json` and `STATE.json` from templates.
9. For each remaining gap, apply the Extension Admission Gate. Default is `DO_NOT_ADD`.
10. Create any approved project-local extension only under `PROJECT_ROOT/.gpt-codex/extensions/`.
11. Export a normalized candidate for each newly created or materially changed project-local extension to `FRAMEWORK_ROOT/.gpt-codex/harvest/inbox/<project_id>/`. If framework root is unavailable, record `harvest_export_status: PENDING`; do not block otherwise-valid project work solely because Harvest is unavailable.
12. Run governance compile validation.
13. Obtain user approval for material project/governance choices.
14. Transition `STATE.json` from `PROPOSED` to `AUTHORIZED` only with expected revision and required evidence.

## Built-in selection rule

`Preinstalled != Enabled`.

Do not enable a Built-in merely because it exists. Enable only when project evidence/requirement justifies it.

Before creating any extension follow:

`REUSE → PROJECT_NATIVE → CONFIGURE → COMPOSE → SAFE_DEGRADE → EXTEND`.

## Extension Admission Gate

A new extension requires concise answers to:

- What observed evidence, explicit requirement, or credible project risk requires it?
- Why do existing Built-ins not solve it?
- Why do project-native tools not solve it?
- Why is configuration/composition insufficient?
- Can safe degradation satisfy the requirement without new governance?
- Will this extension represent a reusable project capability/constraint rather than a one-off instruction?
- What is the maintenance cost and retirement condition?

Reject extensions justified only by “best practice”, hypothetical future need, or perfection.

## Existing project maintenance and resume flow

A context-window transition is not a project bootstrap.

A maintenance request is not a repository rediscovery.

For an existing governed project, bind project identity first, then follow this map-first path:

1. Read `.gpt-codex/navigation/PROJECT_MAP.json` when present.
2. Match the request to candidate modules using `purpose`, `keywords`, and `read_when`.
3. Read only matching module maps.
4. Select `MAP_HIT`, `MAP_PARTIAL`, `MAP_MISS`, or `MAP_MISSING`.
5. Validate the Resume checkpoint and relevant Git delta.
6. Select `FAST_RESUME`, `DELTA_RESUME`, or `COLD_RESUME`.
7. Read only required target files and expand search only when bounded evidence requires it.

Do not scan the repository when the Project Map can identify the candidate module.

Do not run repository discovery when a valid resume checkpoint exists.

`MAP_HIT` reads only the matching module maps and candidate files. `MAP_PARTIAL` permits bounded discovery inside candidate paths. `MAP_MISS` permits scoped discovery for the missing area. `MAP_MISSING` remains compatible with an existing governed project and does not imply Bootstrap. `FAST_RESUME` avoids rereading unchanged context, `DELTA_RESUME` reads only relevant changes, and `COLD_RESUME` starts progressive disclosure without treating an absent checkpoint as Bootstrap.

Validate state revision before writing. If your expected revision is stale, do not overwrite; enter `RECONCILIATION_REQUIRED`.

## Framework upgrade flow

If `FRAMEWORK_ROOT` version is newer than `CONTROL.framework.last_evaluated_version`, run the `framework-compatibility` Built-in read-only.

Do not modify the project during compatibility evaluation. Return one result:

`NO_ACTION | OPTIONAL_REUSE | RECOMMENDED_UPGRADE | REQUIRED_MIGRATION | CONFLICT`.

Evaluation does not imply adoption. Any project change must be a separate authorized Work Unit/migration.

## Project vs framework writes

Ordinary project Codex may write:

- authorized files under project root;
- project-local extensions under project root;
- current project's normalized Harvest Candidate namespace under framework root.

It may not write:

- framework Kernel;
- framework Built-ins;
- other projects' Harvest namespaces;
- Built-in promotion state.

## User-facing Codex routing

Label actions `[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, or `[INFO]` so executor authority is unambiguous.

Before a copyable Codex instruction, always state:

```text
【执行策略】<实际策略>
【完成后是否需要批准】不需要 | 需要 GPT 判断 | 需要用户批准
```

Then give the bounded Codex instruction and exact return evidence.

## Role communication boundaries

`[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, and `[INFO]` are transport/routing hints, not machine authority; they do not replace Instruction or Result Envelope fields. The machine role, `authorized_actions`, project identity, state revision, and evidence are authoritative.

The exact seven roles are `GPT_ORCHESTRATOR`, `GPT_REVIEWER`, `CODEX_IMPLEMENTER`, `CODEX_REVIEWER`, `USER_APPROVER`, `USER_LOCAL`, and `INFORMATION_ONLY`. `instruction_type` belongs only to an Instruction Envelope, while `result_message_type` belongs only to a Result Envelope. No generic `message_type` is permitted.

Use the causal lifecycle `REVIEW_FINDING` → GPT/User decision → `FIX_INSTRUCTION` → `CODEX_IMPLEMENTER` → `REVIEW_RESULT`. A finding is evidence, not authorization. Instruction issuance is not execution confirmation, and remote review visibility is not instruction delivery.

Legacy `[CODEX]` compatibility is bounded and fail-closed: map only a deterministic implementation/work-unit or explicitly review-bound context to one Codex role, and reject unknown or ambiguous forms. Handoff is derived evidence, not an authority source.
