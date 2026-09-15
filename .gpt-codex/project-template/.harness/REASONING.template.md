# Development Strategy and Process Record

## Strategy
STRATEGY_PROFILE = PROJECT_DEFAULT
GPT_STRATEGY = MINIMAL_CLOSED_LOOP
CODEX_IMPLEMENTER_STRATEGY = MINIMAL_DIFF_TDD
CODEX_REVIEWER_STRATEGY = CONTRACT_FIRST
TASK_SPLITTING = PROJECT_DETERMINED
REVIEW_POLICY = RISK_OR_MILESTONE
INSTRUCTION_POLICY = REFERENCE_FIRST
RESULT_RETURN_POLICY = DURABLE_REF_FIRST

## Decision Records
No project decisions recorded yet.

## Governed Change Decision Format
Record observable decision facts only; do not record private reasoning.

CURRENT_AUTHORITY:
EXISTING_CAPABILITY:
EXISTING_AUTHORITY_REFS:
ROOT_CAUSE:
REUSE_PATH:
MINIMUM_DELTA:
NEW_MECHANISM_REQUIRED:

`EXISTING -> reuse`; `PARTIAL -> extend existing capability`; `MISSING -> test existing responsibility/module before adding mechanism`.

## Process Reviews
Record only observable milestone facts: task, key decision, error category,
retry/intervention/review/remediation/handoff counts, final result, durable
Git/evidence refs, and reliable usage (otherwise UNKNOWN).

## Execution Record Format
TASK:
METHOD:
KEY_DECISION:
ERROR_CATEGORY:
CODEX_RETRIES:
GPT_INTERVENTIONS:
REVIEW_ROUNDS:
REMEDIATION_ROUNDS:
HANDOFF_RESULT:
FINAL_RESULT:
GIT_SHA:

## Structure Review Format
MOMENT:
CHANGE:
RESPONSIBILITY_REASON:
BEFORE_CAPABILITIES:
AFTER_CAPABILITIES:
MEASURABLE_BENEFIT:
RESULT:
