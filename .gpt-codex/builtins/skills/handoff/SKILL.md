# Handoff

Generate a compact view from `PROJECT.md`, `CONTROL.json`, `STATE.json`, the active Work Unit, the machine Result Envelope, and relevant Evidence. The Result Envelope is the authoritative structured fact source; Handoff and GPT Return Text are derived views and must never become competing sources of truth. A return-required envelope must carry `SOURCE_PROJECT_CONTEXT_ID`, `SOURCE_PROJECT_NAME`, and `FRAMEWORK_VERSION`, and GPT must verify the source identity before accepting it.

When `Return To GPT Required = YES`, Codex's final output must include one independent, self-contained plain-text GPT Return Text generated from that Result Envelope. It must be directly copyable and must contain the complete stable sections:

`RESULT`, `WORK_UNIT`, `STATE_REVISION`, `EXECUTION`, `CHANGED`, `VERIFY`, `EVIDENCE`, `DEVIATIONS`, `BLOCKERS`, and `NEXT_GPT_ACTION`.

When applicable, also include Git Base / Implementation SHA, Parallel Batch / Execution Unit, Observability / Fitness, and Extension Evidence references. Missing or empty fields are written as `NONE`. Raw logs, full diffs, telemetry, debug traces, and intermediate reasoning are not part of the Return Contract; provide them only through Evidence references.

The same complete field set is required for `PASS`, `FAIL`, and `BLOCKED`, so GPT can determine the next authorized action from the copied text alone.

For GitHub continuity, Handoff must label `LATEST_SYNCED_REMOTE_STATE` and
`LOCAL_UNSYNCED_STATE` separately. GPT validates the selected repository ID
and independently re-observes the target remote ref/head before accepting a
publication. A new mutating Work Unit requires clean preflight; local
degraded continuation is limited to the same already-authorized active Work
Unit and cannot produce formal `PASS`.
