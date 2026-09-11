# Controlled Git Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the universal framework from v1.3 to v1.4 with task-scoped Git capability and a separate integration gate.

**Architecture:** Git authority is attached to agent modes and durable task/state metadata. Implementation may perform safe task-owned Git writes, while repository-history integration remains separately authorized and destructive recovery operations remain forbidden by default.

**Tech Stack:** Markdown governance artifacts, Git CLI contracts.

**Spec:** `docs/superpowers/specs/2026-09-11-controlled-git-lifecycle-design.md`

## Global Constraints

- Do not alter project business architecture through framework migration.
- Default Git strategy is `TASK_BRANCH` unless a project explicitly selects another strategy.
- Pre-existing/unknown user changes must never be destroyed, hidden, staged, or committed by Codex.
- Commit may belong to implementation; merge/push belongs to explicit `GIT_INTEGRATION`.
- Existing Bootstrap, Compact Handoff, Context Continuity, Action Routing, and Handoff Manifest behavior must remain valid.

---

### Task 1: Add framework-level Git governance

**Files:**
- Modify: `.gpt-codex/FRAMEWORK.md`
- Modify: `AGENTS.md`
- Modify: `.gpt-codex/CHANGELOG.md`

**Interfaces:**
- Consumes: existing v1.3 mode and source-of-truth hierarchy.
- Produces: v1.4 Git permission matrix, lifecycle, stop conditions, and reconciliation rules.

- [x] Define mode-bound Git read/write permissions.
- [x] Define `TASK_BRANCH`, `EXISTING_BRANCH`, and `NO_COMMIT` strategies.
- [x] Define dirty-worktree ownership classification and blockers.
- [x] Define `GIT_INTEGRATION` and dangerous-operation restrictions.
- [x] Add v1.4 changelog entry.

### Task 2: Bind project/task/state/review artifacts to Git

**Files:**
- Modify: `.gpt-codex/templates/PROJECT.template.md`
- Modify: `.gpt-codex/templates/STATE.template.md`
- Modify: `.gpt-codex/templates/TASK.template.md`
- Modify: `.gpt-codex/templates/CODEX_EXECUTION_PACKET.template.md`
- Modify: `.gpt-codex/templates/REVIEW.template.md`
- Modify: `.gpt-codex/templates/HANDOFF.template.md`

**Interfaces:**
- Consumes: framework Git lifecycle.
- Produces: exact Git strategy/base/branch/commit/review bindings.

- [x] Add project Git strategy and integration authority metadata.
- [x] Add current Git state to `STATE.md`.
- [x] Add task Git contract and implementation SHA fields.
- [x] Add execution Git preflight and commit policy.
- [x] Bind review to exact base..implementation SHA and stale-review rule.
- [x] Add compact Git signals to handoff manifest.

### Task 3: Add dedicated Git contracts and documentation

**Files:**
- Create: `.gpt-codex/templates/GIT_PRECHECK.template.md`
- Create: `.gpt-codex/templates/GIT_INTEGRATION.template.md`
- Modify: `.gpt-codex/BOOTSTRAP_PROMPT.md`
- Modify: `.gpt-codex/README.md`

**Interfaces:**
- Consumes: v1.4 Git governance.
- Produces: reusable preflight/integration contracts and user-facing workflow guidance.

- [x] Add Git precheck template with PASS/blocker outcomes.
- [x] Add least-privilege integration template.
- [x] Teach bootstrap/resume flow to establish/verify Git strategy.
- [x] Document user workflow and Git safety boundaries.

### Task 4: Verify and package v1.4

**Files:**
- Verify: all framework Markdown artifacts.
- Create: distribution ZIP.

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: self-consistent v1.4 package.

- [x] Verify framework version references are 1.4 where current-version metadata is expected.
- [x] Verify Git write permissions are forbidden outside explicit modes.
- [x] Verify merge/push is never implicitly authorized by task completion.
- [x] Verify dirty/pre-existing changes are protected.
- [x] Verify review SHA binding and Git reconciliation rules are represented.
- [x] Verify ZIP integrity and compute SHA-256.
