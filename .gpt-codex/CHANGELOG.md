# GPT–Codex Framework Changelog

## v2.2.2-local.1 — Local Consumer Dependency Closure Corrective Release

- Repairs the consumer projection dependency closure for `validate_project.py`.
- Keeps `validate_framework.py` independent from management-only release tooling.
- Adds isolated extracted-artifact import coverage for consumer validators.
- Supports local corrective SemVer release metadata without claiming an official
  upstream release or performing GitHub publication.

## v2.2.1 — Self-Hosting and Publication Authority Corrective Patch

- Added management-only Framework self-hosting validation for the marked `FRAMEWORK_MANAGEMENT` / `SELF_MANAGED` project while preserving ordinary consumer isolation.
- Added catalog-and-manifest checks for the narrow management builtin installed-path exception.
- Mechanically reject `PASS` without `VERIFIED`, `SYNCED` without verified evidence, and candidate authority combined with final claims or `COMPLETE` state.
- Local pre-publication results remain `LOCAL_COMPLETE`/`SYNC_PENDING` with `PUBLICATION_CANDIDATE_ONLY` until a separately authorized remote publication is verified.
- Distinguished verified generic baseline W from management attestation head P and kept the bounded W → verify W → P model without self-reference.
- Recorded forward-only local reconciliation; this release does not perform GitHub publication and preserves `KERNEL_VERSION = 2.0.0` and `SCHEMA_VERSION = 1`.

## v2.2.0 — GitHub-backed Project Continuity & Coordination

- Added stable `CONTROL.github.repository_id` binding with durable full-name and default-branch metadata; local remote names remain runtime-only.
- Added cross-window resume from canonical CONTROL/STATE/Evidence/Result records and explicit `LATEST_SYNCED_REMOTE_STATE` versus `LOCAL_UNSYNCED_STATE` semantics.
- Added phase-specific clean preflight and authorized-active-work local degradation with `LOCAL_COMPLETE`/`SYNC_PENDING`.
- Added bounded WORK COMMIT W → PUBLICATION COMMIT P → live `TOOL_OBSERVED` remote verification; publication commits never self-assert their own SHA.
- Added repository binding Guardrail, continuity Skill, migration classifications, isolation checks, and additive Schema generation 1 contracts.
- Preserved `KERNEL_VERSION = 2.0.0` and `SCHEMA_VERSION = 1`.

## v2.1.0 — Bidirectional Project Context Binding

- Added one authoritative `PROJECT_CONTEXT_ID` binding for GPT instructions and Codex Result Envelopes.
- Added required `cross-project-context-binding` Guardrail, legacy target-project protection, and two-step read-only/challenge-bound bootstrap with replay protection.
- Added contamination recovery and migration guidance while excluding management identity from release packages.
- Kept `KERNEL_VERSION = 2.0.0` and `SCHEMA_VERSION = 1`; this release does not change the Kernel Contract or introduce a breaking Schema change.

## v2.0.3 — Paste-ready GPT Return and Fixed Framework Source Folder

- Added a Result Envelope-derived, plain-text GPT Return Text for required Codex-to-GPT handoffs, with complete PASS/FAIL/BLOCKED fields and explicit `NONE` values.
- Added handoff/template/schema coverage for state revision, execution, verification, evidence, deviations, blockers, Git SHAs, parallel/execution units, observability/fitness, extension evidence, and the next GPT action without creating a second source of truth.
- Added Consumer Workspace Setup guidance for one fixed, unversioned Framework Source Folder, read-only Framework Kernel/Built-ins, compatibility scans, and one-time migration from versioned folder bindings.
- Kept `KERNEL_VERSION = 2.0.0` and `SCHEMA_VERSION = 1`; this patch does not change the Kernel Contract.

## v2.0.2 — Lightweight Release Archive

- Added `releases/INDEX.json` and per-version lightweight release records; historical release ZIPs are not embedded in the source repository or later packages.
- Added `.gpt-codex/scripts/release_archive.py` to import historical ZIP metadata with integrity validation and SHA-256 recording.
- Extended the project-local `framework-release` Skill to maintain release metadata, clear previous generated artifacts from `dist/`, and emit only the current release artifacts.
- Added recorded metadata for the historical ZIPs supplied during the v2.0.2 maintenance upgrade.
- Fixed the v2.0.1 bootstrap prompt version typo.
- Kept `KERNEL_VERSION = 2.0.0`; this patch does not change the v2.0 Kernel Contract.

## v2.0.1 — Framework Release Packaging

- Added root `VERSION` as the single framework release-version source.
- Added project-local `framework-release` Skill for the framework management project.
- Added automated framework validation, test execution, deterministic ZIP packaging, ZIP hygiene checks, SHA-256 output, and release manifest generation.
- Kept `KERNEL_VERSION = 2.0.0`; this patch does not change the v2.0 Kernel Contract.
- Updated new-project templates to adopt framework release v2.0.1 while retaining Kernel/schema compatibility identifiers.

## v2.0.0 — Minimal Kernel & Evidence-Based Extensions

### Architectural reset

- Replaced the v1.x monolithic governance model with a small 11-part Kernel.
- Introduced dual-root operation: authoritative project root + auxiliary framework root.
- Moved technology/project behavior to curated Built-ins or project-local Skill / Guardrail / Fitness extensions.
- Established `Preinstalled != Enabled` and governance YAGNI as first-class rules.

### Machine-verifiable governance

- Added machine-authoritative JSON contracts for CONTROL, STATE, Work Unit, Extension, Evidence, and Result Envelope.
- Added state revision for optimistic concurrency and stale-write reconciliation.
- Added evidence provenance classes and restrictions on model-inferred evidence.
- Added standard-library Kernel conformance tests and validators.

### Extension lifecycle

- Added extension maturity: `PROJECT_LOCAL → HARVEST_CANDIDATE → SHARED_CANDIDATE → BUILTIN → DEPRECATED/RETIRED`.
- Added Extension Admission Gate, provenance, retirement, and complexity controls.
- Added evidence-based Harvest Inbox and semantic comparison model.
- Added `Generalize after repetition, not before`.

### Reuse and upgrades

- Added curated Required/Optional Built-in catalog.
- Added Built-in Reuse Report before new project extensions.
- Added framework compatibility evaluation separate from framework adoption.
- Added explicit Kernel/schema versioning and migration contract.
- Added `Framework upgrades are evaluated, not propagated`.

### Preserved usability

- Preserved Chinese human-facing `【执行策略】` and `【完成后是否需要批准】` declarations.
- Preserved complete v1.x framework design/plan history under `docs/superpowers/`.
- Archived the v1.7 v2.0 roadmap under `.gpt-codex/history/`.

## v1.7 and earlier

See preserved `docs/superpowers/specs/` and `docs/superpowers/plans/` for the complete framework evolution. v1.7 remains the final v1.x baseline; v2.0 is a structural reset rather than a direct expansion of the monolith.
