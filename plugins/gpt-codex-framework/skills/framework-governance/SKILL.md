---
name: framework-governance
description: Resume a governed GPT/Codex project from repository authority and route exact Instruction, Result, validation, and feedback handoffs.
---

# Framework governance handoff

Use the Project's own `.gpt-codex/` records and native scripts. The Project is authoritative. This optional skill adds no permission, completion decision, or state store.

1. Identify the selected Project, `CONTROL.json` project/context IDs, and Git repository ID/full name. Run the repository-native `load_continuity_resume(root, selected_repository_id)` for every enrolled Project. Reverify current remote and STATE revision before governed work. A baseline resume with no handoff bindings returns context only.
2. Resolve a durable Instruction by exact `instruction_id` and immutable `{repository, commit_sha, path, blob_sha}` locator through `resolve_plugin_instruction`. The only Instruction evidence path is `.gpt-codex/evidence/instructions/<instruction_id>.json`. Check its exact Work Unit ID/ref, project/context, repository, STATE revision, role, actions, scope, and Guardrails against current Core authority. Visibility never authorizes execution.
3. For a Result handoff, provide all four explicit bindings: `target_work_unit_id`, `target_work_unit_ref`, `instruction_locator`, and `expected_state_revision`. A legitimate Project without execution slots uses native `build_repository_handoff`; never infer a target from `STATE.active_work_unit` or `continuity.last_verified_result_ref`. If complete, unique, valid execution-slot authority exists, use native `build_project_handoff` as an additional check and require agreement with all Instruction bindings. Malformed or conflicting slot data yields `RECONCILIATION_REQUIRED`.
4. Use `build_plugin_result_handoff` to present only the validated native Result ID/ref, Evidence refs, STATE revision, and Git SHA. A Result `PASS` does not declare the Work Unit `COMPLETE`. Treat `next_action_hint` as presentation; revalidate authority before acting. Never copy private prompts, transcripts, hidden reasoning, or Reviewer-private context into handoff artifacts.
5. The fixed capabilities are `CONTEXT_ACCESS`, `VALIDATION_ACCESS`, `EVIDENCE_FEEDBACK_ROUTING`, and `AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST`. Use the Core validation entry for executable requests. Route feedback through the existing P1 evidence authority; feedback is non-authoritative.
6. A changed durable marker means only `DURABLE_AUTHORITY_MAY_HAVE_CHANGED`. Perform a fresh governed resume. Notification does not grant permission or Result-discovery authority.

If the Plugin is unavailable, use the same repository-native resume and validation scripts directly. Missing, stale, ambiguous, or foreign facts return `RECONCILIATION_REQUIRED` and require the existing reconciliation/review path.
