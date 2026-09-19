# Group B Prerequisite Contract Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status:** Plan amendment candidate only. It is not accepted Plan, not a Work Unit, not an Instruction, not implementation authority, and not migration authority.

**Goal:** implement only the accepted Group-B prerequisite reconciliation needed to make a repeated B0 semantic remap possible without changing historical Contract Repair Tasks 5–9.

**Architecture:** retain the existing Framework owners and one existing lifecycle. First repair the module-routing metadata prerequisite (R0), then close the historical Task-2, Task-3, and Task-4 contracts in their existing owners, add only the minimum current-version representation fix, prove the production Result consumers remain fail-closed, run cross-contract composition and full regressions, and finally repeat B0 read-only. No task in this Plan implements B1–B5 or creates bridge-005.

**Tech Stack:** Python 3 standard library, JSON Schema 2020-12, `unittest`, Git, existing Framework validators and module-routing code.

**Spec:** `docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`

**Accepted Design immutable ref:** `15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md`

**Accepted Design blob:** `fc59f21d3046151b227ef22fd4bfe3e358b05f8b`

**Design acceptance evidence:** PR #10 comment `5739372216`. The discovery branch `refs/heads/framework-group-b-prerequisite-contract-reconciliation-design-accepted-001` is not authority; the immutable commit/path/blob above is.

## Global Constraints

- `TASKS_5_9_TECHNICAL_SEMANTICS_CHANGED = NO`.
- `GROUP_B_RELEASE = 2.7.3`; Group C remains downstream of fresh `2.7.3 REMOTE_ACTIVE`.
- `PLUGIN_WORK_RESUMED = NO`.
- `BRIDGE_004_REUSE = FORBIDDEN`.
- `BRIDGE_005_CREATED_BY_THIS_PLAN = NO`; this Plan cannot prepare, approve, transport, or consume bridge-005.
- Historical revision-12 seed artifacts remain historical and non-reusable.
- Repeated `B0 PASS` is readiness evidence only; it is not B1 mutation authority.
- No new State value, authority subsystem, review lifecycle, module, routing algorithm, database, queue, daemon, or compatibility subsystem.
- `CODEX_IMPLEMENTER != CODEX_REVIEWER`. Required reviewer sessions are fresh local independent Codex sessions explicitly started by USER. GitHub Cloud Codex is supplemental only unless USER explicitly authorizes it.
- Every mutation task requires a separate bounded Work Unit/Instruction and passing local independent PRE_EXECUTION review before mutation, then a local independent POST_EXECUTION review before the next mutation task.
- The Plan candidate itself authorizes no mutation. After Plan acceptance, execution authority must bind the accepted Design and accepted Plan immutable refs, fresh current base, fresh State revision, exact scope, module route, and reviewer evidence.
- Implementation re-observes current `main`, State revision, module Registry, and exact file owners at execution time. If any authority/semantic/security/evidence contract has materially drifted, stop `AMENDMENT_REQUIRED` or `RECONCILIATION_REQUIRED` as applicable; do not silently rebind.
- `git diff --check`, focused RED→GREEN tests, sensitivity restoration, Framework validation, project validation, consumer validation, and final clean-room/full-suite evidence are mandatory before repeated B0.
- No implementation step may modify this accepted Design or the accepted Plan artifact.

## Review Focus

1. A valid intrinsic `APPROVAL_RESULT` must pass the schema/taxonomy/production Result-consumer chain while a type-token-only imitation still fails.
2. `excluded_paths` must override matching `owned_paths`; no prefix combination may re-expand an explicitly excluded Work Unit path.
3. R0 must register exactly the five previously unowned Task-2/3 test mutation paths without creating an ownership conflict or changing module authority.
4. Strict Instruction SemVer must accept `2.7.2+fix.1` while rejecting malformed core/prerelease/build forms, without altering release parsing or creating version-equality authority.
5. Existing execution/publication/State completion evidence must remain unchanged for non-approval Results; no approval exception may imply `SYNCED`, `CONFIRMED_PUBLICATION`, execution completion, or State completion.

---

## File / owner map

| Owner | Planned mutable assets | Verification assets |
| --- | --- | --- |
| `framework-core` | `.gpt-codex/framework-modules/modules/role-communication.json`; `.gpt-codex/schemas/work-unit.schema.json`; `.gpt-codex/project-template/WORK_UNIT.template.json` | `test_framework_module_schemas.py`, `test_framework_module_routing.py`, `test_kernel_conformance.py`, `test_execution_telemetry.py`, `test_framework_feedback.py` |
| `role-communication` | `.gpt-codex/schemas/instruction-envelope.schema.json`; `.gpt-codex/scripts/instruction_envelope.py`; `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`; `.gpt-codex/schemas/result-envelope.schema.json`; `.gpt-codex/scripts/role_communication.py`; `.gpt-codex/scripts/result_return.py`; `.gpt-codex/project-template/RESULT_ENVELOPE.template.json` | the five Task-2/3 test paths registered by R0 plus existing descriptor-required suites |
| `framework-validation` | `.gpt-codex/scripts/validate_project.py`; composed tests in existing owned validation test files | `test_self_hosting_validator.py`, `test_validator_context_binding.py`, `test_framework_module_routing.py` |
| `release-projection` | `.gpt-codex/scripts/publication_contract.py` | `test_consumer_projection.py`, `test_consumer_runtime_closure.py`, `test_release_packaging.py`, `test_publication_authority.py` |

The five Task-2/3 test paths that R0 must register are exactly:

```text
.gpt-codex/tests/test_instruction_envelope.py
.gpt-codex/tests/test_instruction_role_contract.py
.gpt-codex/tests/test_result_contract_schema.py
.gpt-codex/tests/test_role_communication_taxonomy.py
.gpt-codex/tests/test_result_return.py
```

---

### Task 0: Freeze execution inputs and prove the current module route

**Files:**
- Read only: `AGENTS.md`
- Read only: `.gpt-codex/CONTROL.json`
- Read only: `.gpt-codex/STATE.json`
- Read only: `.gpt-codex/framework-modules/REGISTRY.json`
- Read only: the four current module descriptors named in the file/owner map
- Read only: accepted Design at `15263527e985cb285dcc0354de09d507a5bd86dd`
- Read only: future accepted Plan at `$ACCEPTED_PLAN_SHA`

**Interfaces:**
- Consumes: `ACCEPTED_DESIGN_SHA=15263527e985cb285dcc0354de09d507a5bd86dd`, `$ACCEPTED_PLAN_SHA` supplied by the future governed execution instruction, fresh `origin/main`, current `STATE.revision`.
- Produces: `EXECUTION_BASE_SHA`, `EXECUTION_STATE_REVISION`, exact current module route, exact pre-R0 ownership classification, and the exact future mutation scope for R0.
- `$ACCEPTED_PLAN_SHA` is a runtime binding supplied only after Plan acceptance. It must be an immutable 40-hex commit containing this Plan path; a branch name, tag name, chat assertion, or current HEAD is not a substitute.

- [ ] **Step 1: Freshly verify immutable artifacts and current base**

Run:

```bash
git fetch origin --prune
git rev-parse origin/main
git cat-file -e 15263527e985cb285dcc0354de09d507a5bd86dd^{commit}
git cat-file -e "$ACCEPTED_PLAN_SHA^{commit}"
git show 15263527e985cb285dcc0354de09d507a5bd86dd:docs/superpowers/specs/2026-09-18-group-b-prerequisite-contract-reconciliation-design.md >/dev/null
git show "$ACCEPTED_PLAN_SHA":docs/superpowers/plans/2026-09-19-group-b-prerequisite-contract-reconciliation-plan.md >/dev/null
```

Expected: every command exits 0. Record the exact `origin/main` SHA as `EXECUTION_BASE_SHA`. If accepted Design or Plan cannot be resolved exactly, return `RECONCILIATION_REQUIRED`.

- [ ] **Step 2: Read current State and authority without mutating**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
state=json.loads(Path(".gpt-codex/STATE.json").read_text())
control=json.loads(Path(".gpt-codex/CONTROL.json").read_text())
print("STATE_REVISION", state["revision"])
print("STATE", state["state"])
print("NEXT_ACTION", state.get("next_action"))
print("PROJECT", control["project_id"])
print("REPOSITORY", (control.get("github") or {}).get("repository_full_name"))
PY
```

Expected: exact current facts are recorded. Do not require revision 15 if a later governed control-plane-only change has legitimately advanced State; instead reconcile it against the accepted Design/Plan and current authority. Any unexplained or implementation-bearing drift blocks execution.

- [ ] **Step 3: Prove current routing and pre-R0 ownership gap**

Run:

```bash
python - <<'PY'
import sys
from pathlib import Path
root=Path(".").resolve()
sys.path.insert(0, str(root/".gpt-codex/scripts"))
from framework_module_routing import load_registry, validate_registry, classify_changed_assets, required_tests_for_change
registry=load_registry(root)
print("REGISTRY_ERRORS", validate_registry(root, registry))
paths=[
 ".gpt-codex/tests/test_instruction_envelope.py",
 ".gpt-codex/tests/test_instruction_role_contract.py",
 ".gpt-codex/tests/test_result_contract_schema.py",
 ".gpt-codex/tests/test_role_communication_taxonomy.py",
 ".gpt-codex/tests/test_result_return.py",
]
print("PRE_R0_OWNERS", classify_changed_assets(root, registry, paths))
print("ROUTE_TESTS", required_tests_for_change(root, registry, ["role-communication","framework-core","framework-validation","release-projection"]))
PY
```

Expected:
- `REGISTRY_ERRORS []`.
- all five paths have no mutation owner before R0;
- the four-module route resolves through existing module descriptors;
- required tests include the currently declared suites for all four modules.

- [ ] **Step 4: Produce the R0 Work Unit/Instruction proposal only**

The future GPT_ORCHESTRATOR derives the exact R0 mutation scope as the single descriptor path:

```text
.gpt-codex/framework-modules/modules/role-communication.json
```

Then obtain a fresh USER-started local independent `CODEX_REVIEWER` PRE_EXECUTION review. No file is mutated before that review passes.

**Completion evidence:** accepted Design/Plan object availability, exact execution base, current State revision, Registry validation, pre-R0 five-path unresolved mapping, required-test route, and passing R0 PRE_EXECUTION review.

---

### Task 1: R0 — register the five role-communication test mutation assets

**Files:**
- Modify: `.gpt-codex/framework-modules/modules/role-communication.json`
- Test only: `.gpt-codex/tests/test_framework_module_routing.py`
- Test only: existing descriptor-required Framework-core tests

**Interfaces:**
- Consumes: Task-0 pre-R0 evidence and R0 bounded authority.
- Produces: exactly five new `OWNED_ASSETS` exact-path selectors and exactly two new `REQUIRED_TESTS` entries for `test_instruction_envelope.py` and `test_result_return.py`.
- No module id, dependency, responsibility, permission, routing algorithm, Registry schema, or authority field changes.

- [ ] **Step 1: Capture RED / unresolved ownership evidence**

Re-run the Task-0 `PRE_R0_OWNERS` command immediately before mutation. Expected: every one of the five exact test paths still maps to `()`.

- [ ] **Step 2: Apply the minimal descriptor change**

Add these exact entries to `OWNED_ASSETS`:

```json
{"type":"EXACT_PATH","value":".gpt-codex/tests/test_instruction_envelope.py"}
{"type":"EXACT_PATH","value":".gpt-codex/tests/test_instruction_role_contract.py"}
{"type":"EXACT_PATH","value":".gpt-codex/tests/test_result_contract_schema.py"}
{"type":"EXACT_PATH","value":".gpt-codex/tests/test_role_communication_taxonomy.py"}
{"type":"EXACT_PATH","value":".gpt-codex/tests/test_result_return.py"}
```

Add only these two missing entries to `REQUIRED_TESTS`:

```text
.gpt-codex/tests/test_instruction_envelope.py
.gpt-codex/tests/test_result_return.py
```

The existing three role-communication required tests remain unchanged.

- [ ] **Step 3: Verify Registry and exact single-owner routing**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_framework_module_routing.py" -v
python - <<'PY'
import sys
from pathlib import Path
root=Path(".").resolve()
sys.path.insert(0, str(root/".gpt-codex/scripts"))
from framework_module_routing import load_registry, validate_registry, classify_changed_assets
registry=load_registry(root)
paths=[
 ".gpt-codex/tests/test_instruction_envelope.py",
 ".gpt-codex/tests/test_instruction_role_contract.py",
 ".gpt-codex/tests/test_result_contract_schema.py",
 ".gpt-codex/tests/test_role_communication_taxonomy.py",
 ".gpt-codex/tests/test_result_return.py",
]
errors=validate_registry(root, registry)
owners=classify_changed_assets(root, registry, paths)
print("REGISTRY_ERRORS", errors)
print("POST_R0_OWNERS", owners)
assert errors == []
assert all(v == ("role-communication",) for v in owners.values())
PY
```

Expected: test command PASS, `REGISTRY_ERRORS []`, every path maps to exactly `("role-communication",)`.

- [ ] **Step 4: Run Framework-core descriptor-required regressions**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_framework_module_schemas.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_kernel_conformance.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_execution_telemetry.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_framework_feedback.py" -v
```

Expected: all PASS.

- [ ] **Step 5: Commit only the R0 descriptor mutation**

```bash
git add .gpt-codex/framework-modules/modules/role-communication.json
git diff --cached --check
git commit -m "chore: register role communication contract tests"
```

Record the resulting durable R0 SHA. All later Task-2/3 Work Units/Instructions must bind a base at or after this exact R0 SHA.

- [ ] **Step 6: Independent R0 POST_EXECUTION review**

USER starts a fresh local independent `CODEX_REVIEWER`. The reviewer verifies the exact single changed path, the exact five registrations, two required-test additions, no ownership conflict, and no authority/routing semantic change.

**Completion evidence:** pre-R0 unresolved mapping, post-R0 exact single-owner mapping, Registry PASS, required regressions PASS, exact R0 SHA, clean or task-bounded working tree, and local independent POST review PASS.

---

### Task 2: Close the Instruction Envelope residual contract and strict active-version representation

**Files:**
- Modify: `.gpt-codex/schemas/instruction-envelope.schema.json`
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Modify: `.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json`
- Test: `.gpt-codex/tests/test_instruction_envelope.py`
- Test: `.gpt-codex/tests/test_instruction_role_contract.py`

**Interfaces:**
- Produces:
  `build_instruction_envelope(..., scope_paths: list[str] | None = None, remediation_decision_ref: str | None = None, approval_evidence_ref: Mapping[str, str] | None = None, ...) -> dict[str, Any]`.
- `scope_paths`: 1–100 unique safe repository-relative exact paths when required by mutating instructions.
- `remediation_decision_ref`: optional non-empty string; FIX lifecycle semantics remain owned by existing lifecycle validation.
- `approval_evidence_ref`: closed object `{remote_ref,evidence_commit_sha,path,blob_sha}`; permitted only on a `RECONCILIATION_REQUEST` requesting `MUTATE_APPROVED_SCOPE`. It remains outside the approved authority core.
- `framework_version`: strict SemVer 2.0.0 syntax; must accept exact `2.7.2+fix.1`. This is representation only and does not introduce a version-equality authority gate or change release parsing.

- [ ] **Step 1: Add RED tests for scope and locator closure**

Add parameterized tests covering:
- mutating `EXECUTION_INSTRUCTION`, `FIX_INSTRUCTION`, and mutating `RECONCILIATION_REQUEST` missing `scope_paths`;
- empty, duplicate, absolute, drive-qualified, backslash, `.`, `..`, and empty-component scope paths;
- valid `scope_paths=[".gpt-codex/STATE.json"]`;
- valid and malformed `remediation_decision_ref`;
- valid locator with exact keys and 40-hex `evidence_commit_sha` / `blob_sha`;
- locator with missing/extra key, unsafe path, non-SHA, or use on an ineligible instruction.

Representative RED fixture:

```python
locator = {
    "remote_ref": "refs/heads/gpt-codex-approval-evidence",
    "evidence_commit_sha": "a" * 40,
    "path": "approvals/approval-result.json",
    "blob_sha": "b" * 40,
}
with self.assertRaises(ValueError):
    build_instruction_envelope(
        "EXECUTION_INSTRUCTION",
        context_id, project_name, state_revision, "2.7.2+fix.1",
        issuer_role="GPT_ORCHESTRATOR",
        executor_role="CODEX_IMPLEMENTER",
        return_role="GPT_ORCHESTRATOR",
        authorized_actions=["MUTATE_APPROVED_SCOPE"],
        approval_evidence_ref=locator,
    )
```

- [ ] **Step 2: Add RED tests for strict SemVer**

Pin the following matrix:

```python
valid = [
    "2.7.2",
    "2.7.2+fix.1",
    "2.7.2-alpha",
    "2.7.2-alpha.1+build.01",
]
invalid = [
    "02.7.2",
    "2.07.2",
    "2.7.02",
    "2.7.2-..",
    "2.7.2-01",
    "2.7.2+",
    "2.7",
]
```

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_instruction_role_contract.py" -v
```

Expected: new tests FAIL against the pre-Task-2 implementation.

- [ ] **Step 3: Implement the minimum schema additions**

Add `scope_paths`, `remediation_decision_ref`, and `approval_evidence_ref` to the closed Instruction schema.

The locator schema is exactly:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["remote_ref", "evidence_commit_sha", "path", "blob_sha"],
  "properties": {
    "remote_ref": {"type": "string", "minLength": 1},
    "evidence_commit_sha": {"type": "string", "pattern": "^[0-9a-fA-F]{40}$"},
    "path": {"type": "string", "minLength": 1, "pattern": "^(?!/)(?![A-Za-z]:)(?!.*(?:^|/)\.\.(?:/|$))(?!.*\\\\).+$"},
    "blob_sha": {"type": "string", "pattern": "^[0-9a-fA-F]{40}$"}
  }
}
```

The strict SemVer pattern must encode SemVer 2.0.0 core/prerelease/build identifier rules and must not reuse the current permissive release regex as though it were SemVer-complete.

- [ ] **Step 4: Implement minimum builder validation/rendering**

In `instruction_envelope.py`:
- add the two residual parameters after `scope_paths`;
- validate locator exact keys, SHA fields, and safe path;
- reject locator unless the instruction is `RECONCILIATION_REQUEST` and normalized `authorized_actions` contains `MUTATE_APPROVED_SCOPE`;
- validate strict Instruction SemVer using an Instruction-local strict regex/helper;
- serialize each non-null field;
- do not change release-framework SemVer parsing.

Update the template with real placeholders:

```json
"scope_paths": ["PATH_IN_APPROVED_SCOPE"],
"remediation_decision_ref": "OPTIONAL_DURABLE_DECISION_REF",
"approval_evidence_ref": {
  "remote_ref": "refs/heads/gpt-codex-approval-evidence",
  "evidence_commit_sha": "40_HEX_COMMIT_SHA",
  "path": "approvals/APPROVAL_RESULT_ID.json",
  "blob_sha": "40_HEX_BLOB_SHA"
}
```

- [ ] **Step 5: Verify GREEN and sensitivity restoration**

Run the two focused suites again; expect PASS.

Then independently inject and restore:
1. remove only `remediation_decision_ref` from a FIX fixture where the existing lifecycle requires it;
2. change one locator `blob_sha` to a non-SHA;
3. replace `2.7.2+fix.1` with `2.7.2-01`.

Each injected fault must FAIL; exact restoration must PASS.

- [ ] **Step 6: Commit and POST review**

```bash
git add   .gpt-codex/schemas/instruction-envelope.schema.json   .gpt-codex/scripts/instruction_envelope.py   .gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json   .gpt-codex/tests/test_instruction_envelope.py   .gpt-codex/tests/test_instruction_role_contract.py
git diff --cached --check
git commit -m "fix: close instruction authority envelope"
```

USER starts a fresh local `CODEX_REVIEWER` for the exact Task-2 commit.

**Completion evidence:** RED output, GREEN output, three sensitivity fail/restore pairs, serialized valid instruction examples, exact commit SHA, and local POST review PASS.

---

### Task 3: Close intrinsic APPROVAL_RESULT across schema, role, rendering, and production consumers

**Files:**
- Modify: `.gpt-codex/schemas/result-envelope.schema.json`
- Modify: `.gpt-codex/scripts/role_communication.py`
- Modify: `.gpt-codex/project-template/RESULT_ENVELOPE.template.json`
- Modify: `.gpt-codex/scripts/result_return.py`
- Modify: `.gpt-codex/scripts/publication_contract.py`
- Test: `.gpt-codex/tests/test_result_contract_schema.py`
- Test: `.gpt-codex/tests/test_role_communication_taxonomy.py`
- Test: `.gpt-codex/tests/test_result_return.py`
- Composition tests: existing owned `.gpt-codex/tests/test_self_hosting_validator.py` and/or `.gpt-codex/tests/test_validator_context_binding.py`
- Run unchanged release-projection suites: `test_consumer_projection.py`, `test_consumer_runtime_closure.py`, `test_release_packaging.py`, `test_publication_authority.py`

**Interfaces:**
- `APPROVAL_RESULT` intrinsic payload:
  `result_id`, `result_message_type="APPROVAL_RESULT"`, `responder_role="USER_APPROVER"`, `status="PASS"`, `decision="APPROVE"|"REJECT"`, `response_to_instruction_id`, closed `approved_instruction`, `evidence_refs=[]`, `completion_gate="NONE"`, `remote_verification="NOT_ATTEMPTED"`, `completion_evidence=null`.
- Closed approved authority core contains exactly:
  `instruction_id`, `expected_state_revision`, `expected_base_sha`, normalized `scope_paths`, project context/name, repository id/full name, immutable `target_work_unit_ref`, `issuer_role`, `executor_role`, and authorized actions containing `MUTATE_APPROVED_SCOPE`.
- Intrinsic approval contains no external evidence locator fields.
- A valid intrinsic approval is exempt from execution-style completion evidence and remote-verification-at-creation requirements. All non-approval execution/publication/State requirements remain unchanged.
- A bare `result_message_type="APPROVAL_RESULT"` token is never sufficient to select the exception.

- [ ] **Step 1: Write RED schema/taxonomy fixtures**

Add tests for:
- valid APPROVE and REJECT intrinsic payloads;
- missing/invalid `result_id`;
- wrong responder role;
- missing/invalid decision;
- missing authority-core field;
- extra authority-core field;
- empty/invalid `scope_paths`;
- external locator/commit/blob field embedded in intrinsic approval;
- non-empty `evidence_refs`;
- `completion_gate != NONE`;
- `remote_verification != NOT_ATTEMPTED`;
- non-null execution `completion_evidence`;
- changed-but-still-well-formed authority core remains intrinsically valid because request correlation belongs to later Task 7.

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_role_communication_taxonomy.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_result_return.py" -v
```

Expected: new complete-contract cases expose the current partial implementation.

- [ ] **Step 2: Add a minimum role-authority helper**

Keep the existing taxonomy registration and add a narrowly scoped helper in `role_communication.py`:

```python
def validate_result_role_authority(result_message_type: object, responder_role: object) -> list[str]:
    if result_message_type == "APPROVAL_RESULT" and responder_role != "USER_APPROVER":
        return ["ROLE_AUTHORITY_CONFLICT", "APPROVAL_RESULT_REQUIRES_USER_APPROVER"]
    return []
```

Do not move existing reviewer/implementer authority into a new subsystem.

- [ ] **Step 3: Close the Result schema and templates**

Add `result_id`, `decision`, and `approved_instruction` schema properties and an `APPROVAL_RESULT` conditional branch with `additionalProperties: false` on the approved authority core.

For the generic PASS branches, make the exception conditional on the **complete intrinsic approval shape**, not only the type token. The schema must still require remote verification/completion evidence for existing execution-style PASS Results.

Update the Result template to include the intrinsic fields as optional/example surface without changing the default implementation-result example.

Update `render_gpt_return()` to render `RESULT_ID`, `DECISION`, and `APPROVED_INSTRUCTION` when present; do not synthesize authority.

- [ ] **Step 4: Make publication_contract consumers understand only a validated intrinsic approval**

Add one private helper whose predicate checks the intrinsic transaction values before any exception, conceptually:

```python
def _is_intrinsic_approval_transaction(result):
    return (
        result.get("result_message_type") == "APPROVAL_RESULT"
        and result.get("responder_role") == "USER_APPROVER"
        and result.get("status") == "PASS"
        and result.get("decision") in {"APPROVE", "REJECT"}
        and isinstance(result.get("result_id"), str)
        and bool(result.get("result_id"))
        and isinstance(result.get("response_to_instruction_id"), str)
        and isinstance(result.get("approved_instruction"), Mapping)
        and result.get("evidence_refs") == []
        and result.get("completion_gate") == "NONE"
        and result.get("remote_verification") == "NOT_ATTEMPTED"
        and result.get("completion_evidence") is None
    )
```

Then:
- `validate_result_authority()` does not require `remote_verification=VERIFIED` only for this validated intrinsic transaction;
- `validate_completion_evidence()` permits null only for this validated intrinsic transaction;
- `SYNCED`, `CONFIRMED_PUBLICATION`, remote-head and State-completion rules remain unchanged;
- a malformed or token-only approval continues to receive the existing PASS errors.

- [ ] **Step 5: Add production composition RED→GREEN tests**

In an already-owned framework-validation test file, prove:

```python
self.assertEqual(validate_result_authority(valid_approval), [])
self.assertEqual(validate_completion_evidence(valid_approval), [])

token_only = dict(valid_execution_result)
token_only["result_message_type"] = "APPROVAL_RESULT"
self.assertTrue(validate_result_authority(token_only))
self.assertTrue(validate_completion_evidence(token_only))
```

Also prove a valid execution PASS still requires its current verified/completion evidence and that a valid intrinsic approval does not make a State `SYNCED` or `COMPLETE`.

- [ ] **Step 6: Verify focused and release-projection regressions**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_role_communication_taxonomy.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_result_return.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_consumer_projection.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_consumer_runtime_closure.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_release_packaging.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_publication_authority.py" -v
```

Expected: all PASS after implementation.

- [ ] **Step 7: Sensitivity restore**

Inject each fault independently:
- wrong `USER_LOCAL` responder;
- `decision="APPROVE"` removed;
- `remote_verification="VERIFIED"` at intrinsic creation;
- non-null execution completion evidence on approval;
- token-only approval substitution.

Every fault must FAIL; exact restoration must PASS.

- [ ] **Step 8: Commit and POST review**

```bash
git add   .gpt-codex/schemas/result-envelope.schema.json   .gpt-codex/scripts/role_communication.py   .gpt-codex/project-template/RESULT_ENVELOPE.template.json   .gpt-codex/scripts/result_return.py   .gpt-codex/scripts/publication_contract.py   .gpt-codex/tests/test_result_contract_schema.py   .gpt-codex/tests/test_role_communication_taxonomy.py   .gpt-codex/tests/test_result_return.py   .gpt-codex/tests/test_self_hosting_validator.py   .gpt-codex/tests/test_validator_context_binding.py
git diff --cached --check
git commit -m "fix: close intrinsic approval result contract"
```

USER starts a fresh local independent `CODEX_REVIEWER` for the exact Task-3 commit.

**Completion evidence:** complete intrinsic payload examples, RED/GREEN output, production-consumer composition, unchanged release-projection suite results, sensitivity matrix, exact commit SHA, and local POST review PASS.

---

### Task 4: Close Work Unit effective-scope semantics

**Files:**
- Modify: `.gpt-codex/schemas/work-unit.schema.json`
- Modify: `.gpt-codex/project-template/WORK_UNIT.template.json`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Test: `.gpt-codex/tests/test_self_hosting_validator.py`
- Test: `.gpt-codex/tests/test_validator_context_binding.py`

**Interfaces:**
- `scope.additionalProperties = false`.
- `owned_paths`: required, 1–100, unique safe selectors.
- `excluded_paths`: optional, unique safe selectors.
- Selector is exact repository-relative file path or safe directory prefix ending in exactly one `/`.
- Effective scope rule: a requested exact path must match an owned selector and match no excluded selector. Exclusion always wins and can only narrow.
- Preserve backward-compatible call sites while extending `validate_instruction_authority(...)` with an explicit excluded-selector input or an equivalent current-Work-Unit extraction inside `validate_governed_mutation_entry()`. Do not create a second authority source.

- [ ] **Step 1: Write RED schema fixtures**

Add fixtures for:
- missing/empty/duplicate owned paths;
- malformed exact/directory selectors;
- absolute, drive, backslash, `.`, `..`, empty component;
- unexpected `scope` property;
- duplicate excluded selectors;
- non-empty valid scope.

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v
```

Expected: at least one newly closed invalid shape currently passes and therefore produces RED.

- [ ] **Step 2: Add exclusion-precedence RED cases**

Pin:

```python
owned = {"src/"}
excluded = {"src/private/"}
assert denied("src/private/key", owned, excluded)
assert allowed_by_scope("src/public/key", owned, excluded)
```

Also test exact exclusion:

```python
owned = {"src/"}
excluded = {"src/secret.txt"}
assert denied("src/secret.txt", owned, excluded)
```

- [ ] **Step 3: Close the Work Unit schema and template**

Define `scope` as a closed object. Use the same selector grammar for owned/excluded paths.

Change the template example from empty ownership to:

```json
"scope": {
  "owned_paths": ["PATH_IN_APPROVED_SCOPE"],
  "excluded_paths": []
}
```

Before committing, validate every durable current Work Unit. If any legitimate durable Work Unit cannot satisfy the accepted grammar without altering its authority meaning, stop `DESIGN_RECONCILIATION_REQUIRED`; do not weaken the schema.

- [ ] **Step 4: Implement effective-scope validation**

Refactor the current path matcher into a small pure helper, for example:

```python
def _selector_covers(selector: object, path: object) -> bool:
    return (
        isinstance(selector, str)
        and isinstance(path, str)
        and (path == selector or (selector.endswith("/") and path.startswith(selector)))
    )

def _scope_covers(path: object, owned: set[str], excluded: set[str]) -> bool:
    return any(_selector_covers(s, path) for s in owned) and not any(
        _selector_covers(s, path) for s in excluded
    )
```

The production call must derive selectors from the immutable Work Unit used as authority. Caller assertions, chat, evidence requirements, or template values cannot enlarge scope.

- [ ] **Step 5: Verify GREEN and compatibility**

Run the two focused suites. Also load and validate every current durable Work Unit under `.gpt-codex/work-units/*.json`.

Expected:
- malformed/new RED cases now fail closed;
- existing valid Work Units remain valid;
- exclusion precedence cases behave exactly as specified;
- historical revision-12 seed stays historical/non-current; no test re-authorizes it.

- [ ] **Step 6: Sensitivity restore**

Temporarily invert exclusion precedence so `src/private/key` becomes covered; the dedicated test must FAIL. Restore exact implementation; PASS.

- [ ] **Step 7: Commit and POST review**

```bash
git add   .gpt-codex/schemas/work-unit.schema.json   .gpt-codex/project-template/WORK_UNIT.template.json   .gpt-codex/scripts/validate_project.py   .gpt-codex/tests/test_self_hosting_validator.py   .gpt-codex/tests/test_validator_context_binding.py
git diff --cached --check
git commit -m "fix: close work unit effective scope"
```

USER starts a fresh local independent `CODEX_REVIEWER` for the exact Task-4 commit.

**Completion evidence:** schema RED/GREEN results, durable Work Unit validation, exclusion sensitivity fail/restore, exact commit SHA, and local POST review PASS.

---

### Task 5: Add cross-contract prerequisite composition proof

**Files:**
- Modify only existing owned validation tests:
  - `.gpt-codex/tests/test_self_hosting_validator.py`
  - and/or `.gpt-codex/tests/test_validator_context_binding.py`
- Production files: none unless a failing composition test exposes a missing call already required by the accepted Design. Any broader production redesign returns `AMENDMENT_REQUIRED`.

**Interfaces:**
- Valid chain: production-shaped Instruction fields → immutable Work Unit effective scope → intrinsic Approval Result schema/role/production-consumer validation.
- This task does **not** implement external locator resolution, actual-Git scope oracle, approval correlation against execution request, native control-plane admission, seed consumption, or any historical Task 5–9 behavior.

- [ ] **Step 1: Write one valid composed prerequisite fixture**

Construct:
- a valid mutating Instruction with current-version SemVer and exact `scope_paths`;
- an immutable Work Unit scope that owns those paths and excludes none of them;
- a production-shaped intrinsic `APPROVAL_RESULT` over the closed authority core.

Assert all prerequisite validators pass individually and together.

- [ ] **Step 2: Add one-fault-at-a-time negatives**

At minimum:
- change requested scope to an excluded path;
- drop `approval_evidence_ref` shape validity;
- replace USER_APPROVER with USER_LOCAL;
- change approval to a type-token-only imitation;
- make `framework_version="2.7.2-01"`.

Each fault must fail at its responsibility owner.

- [ ] **Step 3: Run composed and owner-required suites**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -p "test_self_hosting_validator.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_validator_context_binding.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_role_authority.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_role_communication_taxonomy.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_instruction_role_contract.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_result_contract_schema.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py" -v
python -m unittest discover -s .gpt-codex/tests -p "test_result_return.py" -v
```

Expected: all PASS.

- [ ] **Step 4: Commit test-only composition proof and POST review**

```bash
git add .gpt-codex/tests/test_self_hosting_validator.py .gpt-codex/tests/test_validator_context_binding.py
git diff --cached --check
git commit -m "test: compose group B prerequisite contracts"
```

USER starts a fresh local independent `CODEX_REVIEWER` for this exact composition commit.

**Completion evidence:** composed valid-chain PASS, five named one-fault negatives, exact changed-test paths, exact commit SHA, and local POST review PASS.

---

### Task 6: Full regression and clean-room prerequisite verification

**Files:** no intended production mutation.

**Interfaces:**
- Consumes Task-1 through Task-5 reviewed commits.
- Produces a bounded verification matrix proving the prerequisite reconciliation only.
- Any failure is retained as evidence; do not “fix while verifying” without a new governed FIX cycle and appropriate review.

- [ ] **Step 1: Run Framework/project/consumer validators**

Run:

```bash
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py
python .gpt-codex/scripts/validate_consumer_projection.py
git diff --check
```

Expected: all exit 0.

- [ ] **Step 2: Run full test suite**

Run:

```bash
python -m unittest discover -s .gpt-codex/tests -v
```

Record the exact numeric `Ran N tests`, failures, and errors. Completion requires failures = 0 and errors = 0.

- [ ] **Step 3: Re-run all four module descriptor-required sets**

Require the complete current declared sets for:
- `role-communication`;
- `framework-core`;
- `framework-validation`;
- `release-projection`.

Do not infer success from the full suite alone; record the focused owner results as evidence.

- [ ] **Step 4: Clean-room fault matrix**

On a clean disposable worktree or equivalent isolated clone of the exact candidate SHA, run one-fault-at-a-time checks for:
- R0 ownership registration absent;
- malformed Instruction SemVer;
- out-of-scope/excluded path;
- malformed intrinsic approval;
- token-only approval consumer bypass attempt.

Restore each exact byte before the next case. None of these checks may mutate the authoritative reviewed branch.

- [ ] **Step 5: Independent final reconciliation POST review**

USER starts a fresh local independent `CODEX_REVIEWER` against the exact complete prerequisite implementation candidate and cumulative implementation diff. Reviewer verifies scope, four-module route, all reviewed task commits, test/validator evidence, and confirms no Task 5–9, bridge-005, Plugin, B1, release, or State mutation slipped into the implementation.

**Completion evidence:** validator outputs, full-suite numeric result, owner-focused suites, clean-room fault matrix, clean working tree, exact final implementation SHA, and local final review PASS.

---

### Task 7: Repeat Group B B0 read-only semantic remap

**Files:** read only. No bridge creation, Plan mutation, Work Unit mutation, State mutation, code mutation, release mutation, or B1 mutation.

**Interfaces:**
- Consumes the accepted historical Contract Repair Design/Plan, accepted staged-closure Design/Master Plan, accepted prerequisite reconciliation Design/Plan, exact reviewed prerequisite implementation candidate, current remote/main/release/State/module facts.
- Produces the B0 remap table:
  `old immutable requirement -> current owner -> unchanged semantic proof -> proposed exact future B1–B5 scope`.

- [ ] **Step 1: Freshly observe remote-active/current repository facts**

Verify exact current:
- main SHA/ref;
- active Framework version/release/tag/artifact;
- CONTROL identity;
- STATE revision/sync;
- prerequisite implementation commit reachability and review evidence.

Do not use stale author-time revision 15 if a governed implementation lifecycle has advanced it.

- [ ] **Step 2: Re-run B0 remap for immutable historical Tasks 5–9**

For each historical requirement, prove:
- current owner exists;
- behavior/authority/security/evidence/acceptance semantics are unchanged;
- only mechanical current path/interface binding is proposed.

Any semantic/authority/security/evidence difference returns `AMENDMENT_REQUIRED`.

- [ ] **Step 3: Explicitly classify migration-authority requirement**

Return one of:

```text
B0 = PASS
MIGRATION_AUTHORITY_REQUIRED = YES
```

or

```text
B0 = PASS
MIGRATION_AUTHORITY_REQUIRED = NO
```

or the appropriate blocked/amendment/reconciliation result.

A `B0 PASS` alone authorizes nothing.

- [ ] **Step 4: Stop before B1**

If migration authority remains required, the next lifecycle is separately:

```text
fresh current base + State revision + exact scope + exact payload
-> USER-started local independent PRE_EXECUTION review
-> exact USER_APPROVER approval
-> immutable remote verification
-> separate B1 Work Unit / Instruction
-> B1
```

This Plan neither creates nor authorizes that artifact.

**Completion evidence:** current remote facts, complete remap table, exact B0 result, migration-authority classification, and explicit `B1_AUTHORIZED = NO`.

---

## Plan self-review

### 1. Spec coverage

- Section 6.1 Instruction residual closure → Task 2.
- Section 6.2 intrinsic Approval Result + publication consumers → Task 3.
- Section 6.3 Work Unit effective scope/exclusion precedence → Task 4.
- Section 6.4 strict active-version representation → Task 2.
- Section 6.5 four-module route + five-path R0 → Tasks 0–1.
- Section 7 serial ordering → Tasks 0–7.
- Section 8 sensitivity matrix → Tasks 1–6.
- Section 9 Group-A regression boundary → Tasks 3 and 6.
- Section 10 authority/migration boundary → Task 7 and Global Constraints.
- Section 11 exact review binding → every review gate and final review.
- Section 12 acceptance criteria → Tasks 0–7 plus final B0 output.

No accepted Design requirement is intentionally deferred inside the prerequisite reconciliation.

### 2. Placeholder scan

There are no `TBD`, `TODO`, “similar to Task N”, or unnamed implementation steps. `$ACCEPTED_PLAN_SHA` is a defined runtime authority input that cannot exist until this candidate itself is accepted; it is not an unresolved design placeholder.

### 3. Type/interface consistency

- Task 2 produces the fields consumed by Task 3/5.
- Task 3 produces intrinsic approval semantics only; request correlation remains historical Task 7 and is not pulled forward.
- Task 4 provides effective scope; Task 5 composes only prerequisite behavior.
- R0 becomes durable before Task-2/3 test mutation authority is issued.
- Task 6 verifies the complete prerequisite candidate; Task 7 is read-only B0.
- No task implements locator resolution, actual-Git scope oracle, native admission, seed materialization, or production Task-5–9 composition.

### 4. Review Focus coverage

- Approval type-token bypass → Task 3 production composition and Task 6 clean-room fault.
- Exclusion precedence → Task 4 sensitivity and Task 6 clean-room fault.
- R0 exact ownership → Task 1 pre/post mapping and Task 6 route regressions.
- Strict SemVer → Task 2 RED/GREEN/sensitivity and Task 6 clean-room fault.
- Execution/publication/State evidence preservation → Task 3 unchanged regression suites and Task 6 full validation.

## Plan acceptance and execution boundary

Required lifecycle from here:

```text
Plan candidate
-> USER starts fresh local independent CODEX_REVIEWER
-> GPT adjudication
-> exact Plan USER_APPROVER acceptance
-> immutable accepted Plan ref
-> fresh current authority/base/State observation
-> bounded Work Unit + Instruction for Task 0/R0
-> local independent PRE_EXECUTION review
-> implementation tasks with local independent POST reviews
-> final local independent review
-> repeated B0
```

This Plan candidate does not authorize any implementation step. Do not trigger GitHub Cloud Codex for the Plan review unless USER explicitly authorizes that mode.
