# Project

## Identity

- Project ID: `PRJ-EXAMPLE-001`
- Name: Example Project
- Purpose: Describe the actual product/system goal.

## Evidence-derived project profile

Document only project facts that materially shape governance:

- Languages / runtimes:
- Frameworks:
- Repository shape:
- Existing test/build/lint/typecheck mechanisms:
- CI/CD:
- Runtime environments:
- Data stores / external systems:
- Existing architecture rules:
- Material risks / compliance constraints:

## Architecture and constraints

Describe project architecture, boundaries, invariants, and explicit user requirements. Do not duplicate enabled extension lists from `CONTROL.json`.

## Governance rationale

Summarize why the selected governance profile is sufficient for this project and note material rejected/omitted capabilities when useful.

## Source-of-truth rule

- This file explains **what the project is**.
- `CONTROL.json` defines **which governance extensions are enabled**.
- `STATE.json` defines **where governed execution is now**.
