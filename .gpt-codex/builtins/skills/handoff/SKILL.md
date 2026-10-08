# Handoff

Build a derived view from the authoritative project's `PROJECT.md`, `CONTROL.json`, `STATE.json`, active Work Unit, validated machine Result Envelope and relevant Evidence. Handoff and GPT Return Text never become authority. GPT verifies the Result's source project/context and Framework version before accepting it.

For every `return_to_gpt_required` (Return To GPT Required) Result, generate one independent, self-contained, directly copyable full GPT Return Text with the existing `result_return.render_gpt_return`. That renderer and `required_return_sections` own the complete field/section format for PASS, FAIL and BLOCKED, including applicable Git, role/correlation and extension fields and NONE for missing values. Do not hand-maintain a second field list. `render_compact_gpt_return` remains an additional durable-reference view; it does not replace the required full return. Keep logs, diffs, traces and reasoning in referenced Evidence.

Instruction/Result schemas and the role protocol own classification and correlation; presentation labels grant no execution authority. A REVIEW_FINDING is evidence only: GPT/User decision must produce a new FIX_INSTRUCTION before implementation and independent re-review.

When available, preserve the native derived navigation keys: `MAP_ROUTE`, `MAP_MODULES`, `MAP_STALE_MODULES`, `MAP_MISSING`, `RESUME_MODE`, `RESUME_CHECKPOINT_REVISION`, `RESUME_ANCHOR_SHA`, `HOT_MODULES`, `HOT_FILES`, `CONTEXT_INVALIDATED`, and `NEXT_REQUIRED_READS`. These hints are derived routing context only. They must not override CONTROL, STATE, Work Unit, Result, Evidence, source/tests or Git/GitHub facts.

GitHub continuity distinguishes LATEST_SYNCED_REMOTE_STATE from LOCAL_UNSYNCED_STATE. Re-observe the bound remote ref/head before accepting publication; new mutating Work Units require clean preflight. Degraded local continuation stays within the same already-authorized Work Unit and cannot produce formal PASS. Use the existing native continuity checks; formatting adds no permission or completion decision.
