# Project Template

The current transition supports the existing `.gpt-codex/` governance assets and the new minimal `.harness/` project surface in parallel.

- Copy/adapt `.gpt-codex/project-template/.harness/` to `PROJECT_ROOT/.harness/`.
- Existing `.gpt-codex/` P0 assets remain supported until the reduction phase proves they can be merged or removed.
- Product/runtime code belongs in project product roots, not in `.harness/`.
- Production packaging excludes `.harness/` by default.

Do not mechanically copy values: GPT must derive project configuration from repository evidence and user intent.

## Consumer Workspace Setup

The consumer workspace has two roots: `PROJECT_ROOT` is authoritative and the fixed, unversioned `FRAMEWORK_ROOT` (for example `gpt-codex-framework` or `framework-source`) is advisory. `Framework Kernel` and `Framework Built-ins` are `READ ONLY` during ordinary project work. Adopted Built-ins are copied as versioned snapshots into the project-owned extensions directory; Framework upgrades do not automatically modify the project.

Run the Framework Compatibility Scan before adoption or migration and return `NO_ACTION`, `OPTIONAL_REUSE`, `RECOMMENDED_UPGRADE`, `REQUIRED_MIGRATION`, or `CONFLICT`. If the project was bound to a versioned folder, remove the old versioned auxiliary folder, add the fixed folder, save the Codex project configuration, and keep the fixed folder for future upgrades.

- `PROJECT.template.md` — human project identity/architecture/constraints.
- `CONTROL.template.json` — machine governance configuration.
- `STATE.template.json` — current machine state and revision.
- `WORK_UNIT.template.json` — generic governed unit of work.
- `EXTENSION.template.json` — project-local Skill/Guardrail/Fitness contract.
- `EVIDENCE.template.json` — evidence/provenance contract.
- `RESULT_ENVELOPE.template.json` — common execution result envelope.
- report templates support reuse, governance compilation, compatibility, migration, and Harvest.

## Map-first maintenance

For an existing governed project, Project Map = where to look, Resume = what is already known, and Git delta = what may be stale. Bind identity, route through the Project Map and candidate module maps, validate Resume and the relevant Git delta, then read only required files. Use Repository Discovery only for initial bootstrap, `MAP_MISS` scoped discovery, `MAP_PARTIAL` bounded discovery, or an explicit material re-baseline.
