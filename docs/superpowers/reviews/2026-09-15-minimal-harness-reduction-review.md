# Minimal Harness Reduction Review

## Baseline

* Design: docs/superpowers/specs/2026-09-15-minimal-closed-loop-harness-upgrade-design.md
* P0 baseline: 224d8c0ebdfdc0aa7024f2c69f06fc6fcfe4c699
* Principle: Preserve capability, compress structure; preserve the closed loop, remove duplication.
* Review baseline: `be46fc8e94c0d7b34a1e71d2499a060822b5d686`; full suite: 490 tests, 0 failures, 0 errors.

## Required Preserved Capabilities

* Git SHA/ancestry authority
* Framework/Project separation
* Project isolation
* Role boundaries
* Review/remediation causality
* Cold recovery
* Production/consumer projection boundaries
* Fail-closed ambiguity handling

## Candidates

| Candidate | Current Responsibility | Replacement Evidence | Status | Separate Removal Work Required |
| --- | --- | --- | --- | --- |
| Work Unit | Durable project-scoped authorization, revision basis, execution state, and Result correlation. | NONE — no capability-preserving replacement proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/schemas/work-unit.schema.json`; `test_framework_project_separation.py`. | KEEP | YES |
| Execution slots | Enforce one-active-work lifecycle, assignment binding, revision preconditions, and fail-closed slot transitions. | NONE — no capability-preserving replacement proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/continuity_resume.py` (`validate_execution_slots`, `validate_slot_transition`); `test_continuity_resume.py`. | KEEP | YES |
| Resume persistence | Preserve verified checkpoints, prior state/Git continuity, and bounded cold-recovery routing. | NONE — no capability-preserving replacement proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/continuity_resume.py`; `test_continuity_resume.py`. | KEEP | YES |
| Project Map | Provide derived but validated navigation/module routing for bounded reads and stale-context recovery. | NONE — no capability-preserving replacement proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/project_navigation.py`; `test_continuity_resume.py`. | KEEP | YES |
| Telemetry runtime | Provide optional, bounded, non-authoritative execution observations without making telemetry correctness-critical. | NONE — no capability-preserving replacement proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/execution_telemetry.py`; `test_execution_telemetry.py`. | KEEP | YES |
| Instruction Envelope | Retain canonical issuer/executor/return authority, actions, completion gate, correlations, and project binding. | Minimal Codex tasks are derived presentation only and do not replace authority: `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/instruction_envelope.py` (`render_minimal_codex_task`); `test_instruction_role_contract.py`. | KEEP | YES |
| Result Envelope / return | Retain canonical Result contract, responder/return roles, correlation, evidence, and durable Result authority. | Compact GPT return is derived presentation only and does not replace authority: `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/result_return.py` (`render_compact_gpt_return`); `test_review_lifecycle.py`. | KEEP | YES |
| Repeated schemas/validators | Layer canonical contract validation, authority validation, and local context/correlation validation to fail closed at distinct boundaries. | NONE — no duplicate responsibility proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/scripts/validate_project.py`; `test_framework_project_separation.py`, `test_instruction_role_contract.py`. | KEEP | YES |
| Module boundaries | Maintain seven responsibility-owned modules, explicit routing, dependency checks, and ownership-conflict rejection. | NONE — no mergeable boundary proven. `be46fc8e94c0d7b34a1e71d2499a060822b5d686:.gpt-codex/framework-modules/REGISTRY.json`; `test_framework_module_routing.py`. | KEEP | YES |

## Decision Rule

No item is deleted in this review. Deletion or merge requires a separately authorized Work Unit after a candidate is accepted and all capability-preservation tests are named.

## Note

Task 1–7 added bounded derived views and review gates. They are evidence for future reduction decisions, not replacement authority or execution authorization.
