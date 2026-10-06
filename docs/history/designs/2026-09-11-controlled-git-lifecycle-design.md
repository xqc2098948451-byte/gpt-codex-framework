# Controlled Git Lifecycle Design

## Goal

Upgrade GPT–Codex Framework v1.3 so Codex has safe, explicit Git capabilities during project development without gaining uncontrolled authority over repository history.

## Scope

The upgrade is governance-only. It does not redesign any project's business architecture or task content.

## Core model

Git permissions are mode-bound:

- `REPOSITORY_DISCOVERY`: Git read-only.
- `GOVERNANCE_UPDATE`: Git read-only by default; governance commit only when explicitly authorized.
- `REPO_CLEANUP`: no destructive Git recovery shortcuts; only approved cleanup actions.
- `CODEX_IMPLEMENTATION`: Git read plus task-scoped branch/add/commit operations.
- `FRESH_REVIEW`: Git read-only.
- `GIT_INTEGRATION`: merge/push or other integration actions only under an explicit integration contract.

The default project Git strategy is `TASK_BRANCH`; projects may explicitly choose `EXISTING_BRANCH` or `NO_COMMIT`.

## Task Git lifecycle

An implementation task proceeds through:

1. Bootstrap and durable-state authorization checks.
2. Git preflight: repository root, branch, HEAD, expected base, worktree state.
3. Task branch creation when strategy requires it.
4. Implementation and verification.
5. Diff/scope review.
6. Task-scoped staging and commit when authorized.
7. Record `Implementation SHA` and synchronize derived state/handoff.
8. Fresh review bound to exact base..implementation SHA.
9. Separate `GIT_INTEGRATION` for merge/push when explicitly authorized.

## Dirty worktree safety

Pre-existing or unknown changes must never be hidden, destroyed, staged, overwritten, or committed by Codex. Changes are classified as `TASK_OWNED`, `PRE_EXISTING`, or `UNKNOWN`. Material overlap or uncertainty blocks implementation with `BLOCKED_DIRTY_WORKTREE` or `GIT_RECONCILIATION_REQUIRED`.

## Default Git permissions

Normally allowed in `CODEX_IMPLEMENTATION` when the task authorizes Git writes:

- status/diff/log/show/rev-parse/branch inspection;
- `git switch -c` or equivalent task-branch creation;
- `git add` only for task-owned files;
- `git restore --staged` for task-owned staging corrections;
- `git commit` for the approved task.

Not implicitly allowed:

- push/force-push;
- merge/rebase/cherry-pick;
- `reset --hard`, destructive restore, `clean -fd`;
- stash as a way to hide unknown/pre-existing changes;
- branch deletion;
- remote or Git config mutation;
- history rewriting.

## Review binding

Fresh review is bound to exact Git evidence: task base SHA and implementation SHA. A later code commit makes the previous review stale for the changed implementation.

## State and handoff

`STATE.md` records the current Git strategy, branch, task base, current HEAD, and worktree classification/status. `HANDOFF.md` and Compact Handoff expose only decision-relevant Git signals, not full logs.

## Reconciliation

Unexpected branch/HEAD, detached HEAD, missing commits, base mismatch, dirty pre-existing changes, review SHA mismatch, or repository changes outside the approved lifecycle trigger `GIT_RECONCILIATION_REQUIRED` rather than automatic repair.

## Compatibility

Bootstrap Validation, Compact Handoff, Context Continuity, Action Routing, and Handoff Manifest remain intact. Git becomes an additional controlled layer below task authorization and above implementation/review evidence.
