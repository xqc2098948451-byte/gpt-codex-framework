# Framework v2.0.x to v2.1.0 Migration

This migration adds bidirectional Project Context Binding while keeping the Framework Kernel contract unchanged.

## Required project identity

The authoritative project `.gpt-codex/CONTROL.json` must contain a canonical `project_context_id` UUID and a `project_name`. `PROJECT_CONTEXT_ID` is generated during bootstrap and is not inferred from a directory name, Git state, or a copied template. The authoritative selection source for the required safety control is exactly `CONTROL.extensions.guardrails[]`; do not create a second enablement field.

After v2.1.0 adoption, `cross-project-context-binding` is a `REQUIRED_SAFETY_GUARDRAIL`. It must be present once, enabled, sourced from the Built-ins, and at version `1.0.0`. `PROJECT_CONTEXT_ID_MISSING`, a missing guardrail, a disabled guardrail, or malformed adoption requires migration and denies business execution.

## Bootstrap order and protection

For a legacy governed project, bootstrap must compare `BOOTSTRAP_TARGET_PROJECT_ID` with the local authoritative `CONTROL.project_id`. A mismatch is `CROSS_PROJECT_BOOTSTRAP_MISMATCH` and must not mutate the local project.

For an unbound initial bootstrap, phase one is read-only. It creates no `CONTROL.json`, no identity, and no other project file; it returns `BOOTSTRAP_CHALLENGE_ID` and `BOOTSTRAP_CHALLENGE_REQUIRED`. Phase two must carry the exact challenge and is accepted once only. On exact match it creates and verifies the identity and required guardrail, then hard-stops before any business task. Wrong, stale, or replayed challenges are denied.

## Bidirectional runtime binding

GPT-generated instructions carry `TARGET_PROJECT_CONTEXT_ID`, `TARGET_PROJECT_NAME`, `EXPECTED_STATE_REVISION`, and `FRAMEWORK_VERSION`. Codex must verify identity, freshness, and the required guardrail before executable work. A foreign or stale instruction is quarantined or analysis-only.

Codex Result Envelopes carry `SOURCE_PROJECT_CONTEXT_ID`, `SOURCE_PROJECT_NAME`, and `FRAMEWORK_VERSION`. GPT must verify the same source identity and expected revision before accepting the return. Foreign or stale packets are quarantined or analysis-only; they cannot authorize business work.

## Release boundary

The management project's `.gpt-codex/CONTROL.json` is operational identity and is excluded from release ZIPs. Its concrete `PROJECT_CONTEXT_ID` must not occur in release ZIPs, Built-ins, generic docs, templates, schemas, manifests, or source scripts. The generic `.gpt-codex/project-template/CONTROL.template.json` remains part of the release and uses placeholders only.
