# GPT–Codex Framework v2.0 Roadmap

**Status:** IDEA BACKLOG — NOT ACTIVE GOVERNANCE

This file records ideas for v2.0 exploration. It does not change v1.7 behavior and is not implementation authority.

## Primary architectural direction

- Split monolithic framework guidance into **Core + Capabilities**.
- Define capability manifests, dependencies, version compatibility, and enable/disable rules.
- Add Preset / Extension / Bundle concepts for project-specific composition.
- Make context loading capability-aware and progressively disclosed by machine-readable references.
- Provide framework self-validation/schema checks and safer automated migration between framework versions.
- Explore standardized workflow composition for Bootstrap, Git, Parallel, Observability, Specification Quality, Review, Hygiene, and Integration.

## Deferred ideas

- Capability/plugin registry and project-local overrides.
- Explicit capability dependency graph and compatibility matrix.
- Automated framework migration plans/overlays.
- More formal machine-readable state schemas.
- Optional scheduler integration for recurring hygiene/quality scans.
- Multi-agent coordination improvements beyond the v1.x fixed parallel ceiling.

## Freeze rule

v1.7 is the final planned v1.x feature baseline. Append new non-critical structural ideas here until the user explicitly starts v2.0 design.
