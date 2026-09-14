# Project Harness Rules

## Highest Principle
Preserve capability, compress structure; preserve the closed loop, remove duplication.

## Semantic Roots
HARNESS_ROOT = .harness
PRODUCT_ROOTS = app
DEPLOY_ROOTS = ops

## Production Boundary
Harness content is development/governance-only and must not be required by product runtime.

## Stable Project Rules
- Project authority remains local to this repository.
- Reference durable artifacts instead of copying them when possible.
- Framework-wide changes are feedback only; global evolution occurs in gpt-codex-framework.
