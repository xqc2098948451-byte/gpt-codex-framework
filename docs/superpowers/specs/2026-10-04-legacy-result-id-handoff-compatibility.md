# Legacy Result ID handoff compatibility

Authority: direct user GPT_ADJUDICATION, LEGACY_RESULT_ID_HANDOFF_COMPATIBILITY_REMEDIATION, 2026-10-04; FRAMEWORK_CONTRACT / BACKWARD_COMPATIBILITY.

The current target Result must have a nonempty string result_id, be the sole response to the exact Instruction, and pass every existing schema, authority and evidence check. An unrelated historical Result without an ID is tolerated only if its JSON is committed, clean and parseable. Every actual nonempty ID remains globally unique; missing IDs do not enter the uniqueness set. No synthetic ID or path is written to a Result.

Preserve existing continuity STATE.last_verified_result_ref repo-relative legacy paths, and preserve render_compact_gpt_return DURABLE_RESULT_REF_REQUIRED for all new native handoffs. Do not change any of the 13 historical Results or their blobs, kernel version, Result registry, or any R3 physical retirement. L7_STARTED=NO.

Regression A: 13/arbitrary unrelated legacy records plus one valid target yields HANDOFF_READY. B: target without ID reconciles. C: duplicate actual nonempty IDs reconcile. D: unrelated legacy records do not affect exact target selection. E: existing legacy STATE path continuity remains compatible. F: compact rendering without ID still raises DURABLE_RESULT_REF_REQUIRED.

Execute exact Work Unit/FIX, independent PRE, failing regression, smallest inventory fix, focused tests, full suite and framework/project validators, independent POST, fast-forward remote main integration and live verification. Rerun exact R3 handoff at revision28 without physical replay. Only after PASS perform separately bounded L6A durable closure and STATE transition to L7 readiness; do not start L7.
