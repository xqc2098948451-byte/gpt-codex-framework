# Legacy Result ID compatibility Implementation Plan

> For agentic workers: use superpowers:executing-plans inline; independent CODEX_REVIEWER before source mutation and before remote integration.

**Goal:** Let unrelated legacy Result IDs coexist with strict current handoff contracts.
**Architecture:** Change only build_repository_handoff inventory ID admission. Existing committed JSON and target validation remain authoritative.
**Tech Stack:** Python unittest, native Git, repository validation.
**Spec:** docs/superpowers/specs/2026-10-04-legacy-result-id-handoff-compatibility.md

## Global Constraints
13 historical blobs immutable. Kernel unchanged. No synthetic IDs or registry. No R3 physical replay. No L7 start.

## Review Focus
Missing/empty/whitespace/nonstrings at the current target; duplicate IDs including unrelated history; multiple matching targets; uncommitted/dirty/unparseable legacy JSON; existing legacy STATE references and strict compact output.

### Task 1: Governed compatibility repair
- [ ] Exact authorized Work Unit and canonical FIX, durable user adjudication and independent PRE; passing native mutation gate.
- [ ] Add A-D regression cases in .gpt-codex/tests/test_continuity_resume.py, E in test_harness_handoff.py, F in test_result_return.py. Run with python -X utf8 -m unittest discover; A/D fail on the legacy ID rejection before the fix.
- [ ] Modify only .gpt-codex/scripts/continuity_resume.py inventory: check uniqueness only for actual nonempty strings; reject missing ID when matching the exact current Instruction; keep all file and target checks.
- [ ] Focused tests pass; python -X utf8 -m unittest discover -s .gpt-codex/tests -q; python -X utf8 .gpt-codex/scripts/validate_framework.py; python -X utf8 .gpt-codex/scripts/validate_project.py . all pass.
- [ ] Independent POST against exact commit; live remote fast-forward integration/verification; historical byte/blob equality; exact R3 handoff PASS.

### Task 2: Conditional L6A closure
- [ ] Inspect accepted L6A/R3 durable authority, make separate closure Work Unit/Instruction and independent PRE. Preserve all physical evidence; no filesystem retirement commands.
- [ ] Record verified R3 handoff and L6A closure, transition STATE once from28 to29 with L7 ready but not started; validate and independently review; integrate and verify remote.

Ruling: execute the user's explicit remediation plan without a further plan approval. Use external ephemeral review scratch; do not create or retire worktrees during this fix because the worktree registry is part of the pending L6A closure.
