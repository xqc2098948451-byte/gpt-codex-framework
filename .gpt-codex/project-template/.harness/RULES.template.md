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
- A capability check precedes new/materially-expanded Design; duplicate mechanisms are denied when the capability already exists.
- Durable mutation requires governed entry plus PRE-EXECUTION review; failed entry denies mutation.
## Codex Task Protocol

Default compact view uses GOAL / SCOPE / CONSTRAINTS / DONE plus durable references.
It never replaces canonical Instruction authority; its transfer preface is
human-facing handoff metadata only. GPT determines task count and parallelism.

## Structure Evolution
- Responsibility before structure.
- Do not split by file count, line count, agent count, or parallelism convenience.
- Split only for durable responsibility/runtime/security/testing boundaries.
- Merge/delete when layers always change together, are trivial wrappers, or duplicate ownership.
- AFTER_CAPABILITIES must contain every required BEFORE_CAPABILITY.
- Do not reorganize a stable structure for cosmetic reasons.
