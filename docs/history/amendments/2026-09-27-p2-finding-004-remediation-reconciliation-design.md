# P2-FINDING-004 Remediation Reconciliation Design

**Status:** corrective Design candidate for independent review and user acceptance.
**Execution authority:** none. No Work Unit, Instruction, Evidence, or STATE mutation is authorized by this document alone.

## Purpose and existing authority

This design establishes the smallest route through the current Framework remediation lifecycle for `P2-FINDING-004`. It adds no Framework capability or change to Core behavior. The current remote main is `d54f99078e4569fa65cb5af96b16a287d677fe65`; the durable STATE is revision `17`, `AUTHORIZED`, with `reconciliation = null`. The exact reviewed P2 candidate is `7f50439df6988111ae1544798d153e6c802a9a10`. The `REVIEW_FINDING` Result ID is `5e8f1c13-ccbe-4d7e-9e86-878d2c2d58d4`, with finding IDs `["P2-FINDING-004"]` and `review_target_revision = 7f50439df6988111ae1544798d153e6c802a9a10`.

Reuse the accepted P2 Design at `91b485c6c93584ef2f89c459c10e488750f5801f` and accepted governing P2 Plan at `40b704e343762c1c1acbef8c243adb8b0d25b1f6`. The accepted P2 Work Unit authority Design and Plan remain historical authority for the original implementation and are not rewritten. This corrective pair exists because the current remediation validator requires `FIX_INSTRUCTION.remediation_decision_ref` to resolve through current-HEAD `STATE.evidence_refs` to a `REMEDIATION_ADJUDICATION` and accepted or failing basis Evidence. The current P2 Work Unit owns neither STATE nor general remediation Evidence. Therefore a valid finding fix cannot execute at revision 17 without separately governed STATE reconciliation.

The frozen Fix Instruction commit `a48d87cebf3c0d054a7a888a61d271463f7ae7d3` remains historical and superseded after reconciliation. It is never executed as Stage B authority.

## Stage A — Remediation Authority Reconciliation

Future Work Unit ID: `p2-finding-004-remediation-authority-001`. Basis STATE revision: `17`. Its owned mutation scope is exactly:

```text
.gpt-codex/STATE.json
.gpt-codex/evidence/results/RESULT-P2-FINDING-004.json
.gpt-codex/evidence/P2-FINDING-004-REMEDIATION-ADJUDICATION.json
.gpt-codex/evidence/P2-FINDING-004-AUTHORITY-BASIS.json
```

After independent review, acceptance, exact integration, and remote verification of this Design and Plan, use the existing dedicated one-time bootstrap/materialization authority pattern to create the Stage A Work Unit. Freeze canonical Work Unit and bootstrap bytes against fresh repository/STATE revision 17 facts; require independent bootstrap PRE-EXECUTION PASS, GPT adjudication and exact USER bootstrap approval before bounded USER_LOCAL bootstrap and Work Unit materialization. Verify exact Work Unit integration and remote authority, terminate the bootstrap, then issue a Stage A Instruction and require a separate independent native PRE-EXECUTION PASS before execution. No additional Design or Plan is introduced.

Stage A durably records the native `REVIEW_FINDING` Result at `.gpt-codex/evidence/results/RESULT-P2-FINDING-004.json`, bound to Result ID `5e8f1c13-ccbe-4d7e-9e86-878d2c2d58d4`, finding ID `P2-FINDING-004`, and reviewed candidate SHA `7f50439df6988111ae1544798d153e6c802a9a10`. It also materializes GPT's accepted adjudication and accepted authority basis in the two named Evidence files. The adjudication identifies that durable Result ref and finding ID, has `subject = REMEDIATION_ADJUDICATION`, `decision = ACCEPT`, `basis_type = ACCEPTED_AUTHORITY_BASIS`, `source = SYSTEM_DERIVED`, and names the basis Evidence ID in `basis_refs`. The basis identifies the same finding, has `basis_type = ACCEPTED_AUTHORITY_BASIS`, `accepted = true`, and `source = SYSTEM_DERIVED`; it must cite exact accepted P2 Design SHA `91b485c6c93584ef2f89c459c10e488750f5801f`, accepted governing P2 Plan SHA `40b704e343762c1c1acbef8c243adb8b0d25b1f6`, reviewed candidate SHA `7f50439df6988111ae1544798d153e6c802a9a10`, and the durable Review Finding Result ref. Their IDs and references must resolve from the current repository HEAD after integration. Their `state_revision`, and the adjudication's `adjudicated_at_revision`, must match resulting STATE revision `18` so current lifecycle validation does not treat the basis as stale.

Stage A adds exactly the Result, adjudication, and basis paths to `STATE.evidence_refs` and increments STATE revision `17 → 18`. `state` remains `AUTHORIZED`; `active_work_unit`, `blockers`, and `reconciliation` remain unchanged. `continuity` remains unchanged unless the existing validator mechanically requires revision correlation; any such change must be confined to that correlation and independently reviewed. `next_action` remains a non-authoritative hint. No P2 implementation file changes in Stage A. After Stage A POST PASS, exact integrate the reviewed four-path delta, push, and independently verify remote main and remote STATE revision 18 before any Stage B Work Unit materialization.

## Stage B — Provenance Fix

Future Work Unit ID: `p2-finding-004-provenance-fix-001`. Basis STATE revision: `18`. Its owned mutation scope is exactly:

```text
.gpt-codex/evidence/P2-PLUGIN-E2E-ACCEPTANCE.json
.gpt-codex/evidence/instructions/
```

Only after Stage A exact integration, push, and independent remote verification of STATE revision 18, use the same existing dedicated one-time bootstrap/materialization authority pattern for the separate Stage B Work Unit. Freeze canonical Work Unit and bootstrap bytes against fresh remote/STATE revision 18 facts; require independent bootstrap PRE-EXECUTION PASS, GPT adjudication and exact USER bootstrap approval before bounded USER_LOCAL bootstrap and Work Unit materialization. Verify exact Work Unit integration and remote authority, then terminate the bootstrap. Generate a **new canonical** `FIX_INSTRUCTION` for revision 18. It binds `in_response_to_result_id = 5e8f1c13-ccbe-4d7e-9e86-878d2c2d58d4`, finding ID `P2-FINDING-004`, the exact reviewed candidate revision, and `remediation_decision_ref` to the durable Stage A adjudication Evidence ID. Resolve the durable Result, decision, and accepted basis through revision 18 STATE evidence refs at current HEAD; require a separate independent native PRE-EXECUTION PASS before executing the fix. No additional Design or Plan is introduced.

The fix changes only E2E acceptance provenance. The resulting top-level `source` is `SYSTEM_DERIVED`: plugin installation is `TOOL_OBSERVED`; fresh GPT result is `USER_ASSERTED`; fresh Codex/local validation is `TOOL_OBSERVED`; and the acceptance conclusion is `SYSTEM_DERIVED`. Preserve the underlying observed claims and P2 behavior. Run existing validators and a narrow POST re-review against the finding before final exact P2 integration.

## Boundaries

These are exactly two stages, with no intervening Design or Plan. Neither stage designs or authorizes remediation immutable-locator support, Framework validator or schema changes, Plugin changes, Hooks, P3/P4 work, release/version changes, public Plugin publication, replacement of `active_work_unit`, a second STATE, a new lifecycle, or a new evidence store. This candidate does not itself create either Work Unit, change STATE, or execute the fix.
