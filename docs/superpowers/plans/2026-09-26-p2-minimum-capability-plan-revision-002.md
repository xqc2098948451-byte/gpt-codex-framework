# P2 Minimum Capability Revision 002 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver an installable, optional GPT/Codex governance plugin that uses repository-backed durable resume and handoff to reduce manual GPT↔Codex state transfer while preserving all existing Framework authority boundaries.

**Architecture:** Reuse the existing repository-native authorities and helpers instead of creating a synchronization subsystem. Add one thin adapter module that composes `continuity_resume`, `instruction_envelope`, `result_return`, `validate_project`, `role_communication`, and `framework_feedback`; package the user-facing workflow as a skills-only portable plugin. No MCP server, daemon, message queue, session registry, central state store, workflow engine, or committed marketplace is introduced in P2 v1.

**Tech Stack:** Python 3 standard library, existing JSON/Markdown contracts, Git/GitHub durable facts, `unittest`, portable Agent Plugins `plugin.json`, Plugin skills.

**Spec:** `docs/superpowers/specs/2026-09-26-p2-minimum-capability-design-revision-002.md` at accepted Design SHA `91b485c6c93584ef2f89c459c10e488750f5801f`.

## Global Constraints

- P2 v1 exposes exactly four governance capabilities: Context Access, Validation Access, Evidence Feedback Routing, and Authorized Governance Capability Request.
- `Change Notification` is transport-only and is not a fifth governance capability.
- Repository-backed authority remains the source of durable facts; the Plugin never becomes an authority source.
- `NEXT_ACTION_HINT` / `NEXT_GPT_ACTION` are presentation/routing hints only and must never be upgraded to execution authority.
- Any executable next action must be independently revalidated against current STATE revision, active Work Unit, Instruction, role/permission authority, Guardrails, and Git/repository facts.
- GPT/Codex private conversations, raw prompts, private reasoning, scratchpads, transcripts, and private Reviewer context are never synchronized.
- P2 creates no second STATE, Work Unit system, review lifecycle, capability registry, marketplace product, synchronization server, daemon, queue, session manager, workflow engine, or automatic optimizer.
- P2 Plugin remains optional; the repository-native Framework must continue to work without it.
- PRs remain review/integration/Evidence-Bridge surfaces; they are not the routine GPT↔Codex handoff protocol.
- No Framework release/version change is part of this Plan.
- No Plugin release/public-directory submission is part of this Plan.
- P2 implementation begins only after this Plan is independently reviewed, explicitly accepted, repository-integrated, and a separately authorized implementation Work Unit plus passing PRE-EXECUTION review exist.
- Current packaging preflight: new portable Plugin packages use root `plugin.json`; `.codex-plugin/plugin.json` may be provided only as a compatibility fallback. P2 does not commit a repo marketplace; any local marketplace used for installation testing is external acceptance tooling, not a Framework capability.

## Review Focus

1. **Stale or foreign repository state:** a resume or handoff from the wrong repository, project context, or STATE revision must fail closed rather than return usable mutation context.
2. **Hint-to-authority leakage:** a `next_action` or `NEXT_GPT_ACTION` value must remain a hint unless current authority independently proves the action is executable.
3. **Durable artifact ambiguity:** mutable branch names, missing blob SHAs, duplicate Result IDs, or unresolved Instruction locators must not be treated as durable handoff authority.
4. **Plugin absence or unsupported surface:** Framework correctness and project recovery must remain available through repository-native mechanisms without the Plugin.
5. **Installation/package drift:** Plugin manifests and skill paths must remain valid and self-contained; no hidden marketplace, MCP, daemon, or external state dependency may enter the package.

---

### Task 1: Add the thin repository-backed Plugin entry/resume adapter

**Files:**
- Create: `.gpt-codex/scripts/framework_plugin_entry.py`
- Create: `.gpt-codex/tests/test_framework_plugin.py`
- Test: `.gpt-codex/tests/test_continuity_resume.py`
- Test: `.gpt-codex/tests/test_result_return.py`

**Interfaces:**
- Consumes:
  - `continuity_resume.build_project_handoff(root, execution_slot_id=None) -> dict[str, Any]`
  - `continuity_resume.load_continuity_resume(...)`
  - existing project/repository identity and recovery semantics.
- Produces:
  - `build_plugin_resume(root: Path, selected_repository_id: str, execution_slot_id: str | None = None) -> dict[str, Any]`
  - a compact Plugin-facing view containing only project/repository identity, STATE revision/state, active Work Unit/slot, accepted artifact locators, latest/pending Result refs, Git facts, blockers/reconciliation, and `next_action_hint`.
  - `next_action_hint` is derived presentation only; no field named `next_authorized_action` is produced.

- [ ] **Step 1: Write failing Plugin resume tests**

  In `test_framework_plugin.py`, add tests for:
  - one valid repository-backed active Work Unit returns `PLUGIN_RESUME_READY`;
  - wrong repository ID returns fail-closed mismatch/reconciliation;
  - stale/unsynced STATE does not return executable context;
  - ambiguous active slots fail closed;
  - the adapter exposes `next_action_hint` but never `next_authorized_action`;
  - accepted Design/Plan locators remain exact commit/path/blob locators;
  - missing/invalid durable Result references fail closed instead of fabricating a result.

- [ ] **Step 2: Run RED**

  Run:
  `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin.py" -v`

  Expected: failure because `framework_plugin_entry.py` does not yet exist.

- [ ] **Step 3: Implement the minimum adapter**

  Implement `build_plugin_resume(...)` only by composing existing repository-native recovery helpers. Do not duplicate STATE parsing, slot lifecycle rules, result discovery, artifact-locator validation, or Git authority logic.

- [ ] **Step 4: Run GREEN and adjacent regression**

  Run:
  - `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin.py" -v`
  - `python -m unittest discover -s .gpt-codex/tests -p "test_continuity_resume.py" -v`
  - `python -m unittest discover -s .gpt-codex/tests -p "test_result_return.py" -v`

- [ ] **Step 5: Commit Task 1**

  Commit only the adapter and focused tests. Do not package the Plugin yet.

### Task 2: Add durable Instruction publication/resolution without a second authority store

**Files:**
- Modify: `.gpt-codex/scripts/framework_plugin_entry.py`
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Modify: `.gpt-codex/tests/test_framework_plugin.py`
- Modify: `.gpt-codex/tests/test_instruction_envelope.py`
- Modify: `.gpt-codex/tests/test_instruction_role_contract.py`

**Interfaces:**
- Consumes:
  - existing Instruction Envelope schema/validator/builder;
  - `continuity_resume.resolve_immutable_artifact(...)`;
  - `validate_project.validate_instruction_authority(...)`;
  - current Work Unit / STATE / role / permission / Guardrail authority.
- Produces:
  - `instruction_artifact_relative_path(instruction_id: str) -> str`, deterministically under the existing project-owned Evidence surface: `.gpt-codex/evidence/instructions/<instruction_id>.json`;
  - `canonical_instruction_bytes(envelope: Mapping[str, Any]) -> bytes`;
  - `resolve_plugin_instruction(root: Path, locator: Mapping[str, Any], expected_repository: str, *, current_state_revision: int, approved_scope: set[str] | None = None, excluded_scope: set[str] | None = None) -> dict[str, Any]`.
- The helper prepares and validates exact bytes/locators only. It does not commit, push, create authorization, or silently persist anything.

- [ ] **Step 1: Write RED tests for durable Instruction handoff**

  Cover:
  - deterministic path and canonical bytes;
  - valid exact commit/path/blob locator resolution;
  - mutable ref or missing blob rejected as non-authority;
  - project-context, Work Unit, STATE-revision, executor-role, and scope mismatch rejected;
  - valid transport visibility without authorization remains non-executable;
  - no Instruction artifact may grant actions beyond the existing Work Unit/role authority.

- [ ] **Step 2: Run RED**

  Run:
  - `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_envelope.py" -v`
  - `python -m unittest discover -s .gpt-codex/tests -p "test_instruction_role_contract.py" -v`
  - `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin.py" -v`

- [ ] **Step 3: Implement only deterministic preparation and validation**

  Reuse the existing Instruction Envelope builder/validator and immutable artifact resolver. The Plugin may route a host-authorized write of the canonical bytes, but repository mutation remains subject to the existing mutation/integration authority; the helper itself performs no GitHub write.

- [ ] **Step 4: Run GREEN and project validator regression**

  Run the three focused suites above plus:
  `python .gpt-codex/scripts/validate_project.py .`

- [ ] **Step 5: Commit Task 2**

  Commit only Instruction handoff preparation/resolution behavior and tests.

### Task 3: Complete Codex→GPT durable Result/Evidence handoff

**Files:**
- Modify: `.gpt-codex/scripts/framework_plugin_entry.py`
- Modify: `.gpt-codex/scripts/result_return.py` only if a narrowly proven adapter seam is missing
- Modify: `.gpt-codex/tests/test_framework_plugin.py`
- Modify: `.gpt-codex/tests/test_result_return.py`

**Interfaces:**
- Consumes:
  - existing Result/Evidence storage and `build_project_handoff` discovery;
  - `result_return.render_compact_gpt_return(...)`;
  - existing exact Result ID, evidence refs, state revision, Git SHA, artifact locator, blocker, and review status semantics.
- Produces:
  - `build_plugin_result_handoff(root: Path, selected_repository_id: str, execution_slot_id: str | None = None) -> dict[str, Any]`;
  - a durable-reference-first Result view with Result ref, STATE revision, exact HEAD/implementation SHA, evidence refs, review status, blockers, and `next_action_hint`.

- [ ] **Step 1: Write RED tests**

  Cover:
  - valid Result/Evidence handoff from an exact repository state;
  - duplicate/missing Result identity fails closed;
  - Result PASS does not become Work Unit COMPLETE;
  - `NEXT_GPT_ACTION` is exposed only as `next_action_hint`;
  - stale Result/state/Git bindings return reconciliation;
  - no raw logs/private context enters the handoff.

- [ ] **Step 2: Run RED**

  Run the focused Plugin and Result suites.

- [ ] **Step 3: Implement the minimal adapter**

  Compose existing handoff/result-rendering functions; do not create a second Result store or a Plugin completion state.

- [ ] **Step 4: Run GREEN**

  Run:
  - `test_framework_plugin.py`
  - `test_result_return.py`
  - `test_continuity_resume.py`

- [ ] **Step 5: Commit Task 3**

### Task 4: Add Validation Access and Authorized Governance Capability Request

**Files:**
- Modify: `.gpt-codex/scripts/framework_plugin_entry.py`
- Modify: `.gpt-codex/tests/test_framework_plugin.py`
- Test: `.gpt-codex/tests/test_review_lifecycle.py`
- Test: `.gpt-codex/tests/test_validator_context_binding.py`

**Interfaces:**
- Produces:
  - fixed constant `P2_CAPABILITIES = ("CONTEXT_ACCESS", "VALIDATION_ACCESS", "EVIDENCE_FEEDBACK_ROUTING", "AUTHORIZED_GOVERNANCE_CAPABILITY_REQUEST")`;
  - `validate_plugin_capability_request(...)-> list[str]` validating exact capability name, project/repository identity, current STATE revision, active Work Unit, Instruction, role/action authority, scope, and Guardrails through existing validators;
  - `request_validation_access(...)` returning the Core-owned validation result/finding without interpreting it as completion.
- No registry/discovery engine is added; the four names are fixed code constants for P2 v1.

- [ ] **Step 1: Write RED boundary tests**

  Cover:
  - exactly four allowed P2 capability names;
  - unknown capability denied;
  - valid request inside Work Unit allowed to reach the existing Core operation;
  - unsupported, stale, foreign, out-of-scope, or unauthorized request denied;
  - validation PASS does not set completion;
  - Plugin cannot request `AUTHORIZE`, `SCOPE_EXPANSION`, `PUBLISH`, or other forbidden role actions.

- [ ] **Step 2: Run RED**

- [ ] **Step 3: Implement by composing existing validators only**

  No Plugin-owned permission calculation or state transition is permitted.

- [ ] **Step 4: Run GREEN plus review/identity regressions**

- [ ] **Step 5: Commit Task 4**

### Task 5: Add Evidence Feedback Routing and transport-neutral change detection

**Files:**
- Modify: `.gpt-codex/scripts/framework_plugin_entry.py`
- Modify: `.gpt-codex/tests/test_framework_plugin.py`
- Test: `.gpt-codex/tests/test_framework_feedback.py`

**Interfaces:**
- Consumes:
  - existing `framework_feedback.validate_framework_feedback(...)`;
  - existing `framework_feedback.framework_feedback_authorizes_mutation(...)` invariant;
  - project-owned Evidence/Harvest/P1 review path.
- Produces:
  - `route_plugin_feedback(...)` that validates provenance/project/Work Unit/revision bindings and returns the existing feedback destination/status; it never mutates global Framework authority;
  - `durable_authority_marker(resume: Mapping[str, Any]) -> tuple[str, int | None, str | None, str | None]` containing repository identity, STATE revision, authoritative Git SHA, and latest/pending durable Result ref;
  - `detect_durable_authority_change(previous_marker, current_marker) -> bool`.
- The marker comparator is transport-neutral. It may be called after explicit resume, host polling, repository event, connector event, or future supported event; P2 adds no webhook/daemon/background loop.

- [ ] **Step 1: Write RED tests**

  Cover:
  - valid P1 feedback route;
  - feedback remains non-authoritative;
  - wrong project/Work Unit/revision/provenance fails;
  - equal markers produce no notification;
  - STATE/SHA/Result changes produce `True`;
  - a change result means only `DURABLE_AUTHORITY_MAY_HAVE_CHANGED`, never execution authorization.

- [ ] **Step 2: Run RED**

- [ ] **Step 3: Implement minimal feedback routing and marker comparison**

- [ ] **Step 4: Run GREEN plus `test_framework_feedback.py`**

- [ ] **Step 5: Commit Task 5**

### Task 6: Package the installable P2 v1 Plugin without adding a marketplace product

**Files:**
- Create: `plugins/gpt-codex-framework/plugin.json`
- Create: `plugins/gpt-codex-framework/.codex-plugin/plugin.json` only as a compatibility fallback mirroring the portable identity
- Create: `plugins/gpt-codex-framework/skills/framework-governance/SKILL.md`
- Create: `.gpt-codex/tests/test_framework_plugin_package.py`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json` only if current projection validation requires exact classification for the Plugin package
- Test: `.gpt-codex/tests/test_consumer_projection.py`

**Interfaces:**
- Portable package root: `plugins/gpt-codex-framework/`.
- Root `plugin.json` declares stable name/version/description and skills-only package identity.
- The skill instructs ChatGPT/Codex to:
  1. bind project/repository identity;
  2. perform repository-backed resume before governed work;
  3. use durable Instruction/Result locators instead of chat transcript copying;
  4. treat all next-action text as hints;
  5. route validation/capability/feedback through existing Framework authority;
  6. stop fail-closed on stale/conflicting facts.
- No `mcp.json` is added in P2 v1.
- No `.agents/plugins/marketplace.json` is committed.

- [ ] **Step 1: Write RED package tests**

  Assert:
  - portable root `plugin.json` exists and parses;
  - package name is stable and kebab-case;
  - root skills path contains exactly the intended governance skill;
  - optional compatibility manifest cannot declare extra capability/MCP state;
  - no committed marketplace, MCP server, daemon, queue, or external-state configuration appears;
  - Plugin files do not duplicate or redefine Kernel/STATE/Work Unit schemas.

- [ ] **Step 2: Run RED**

- [ ] **Step 3: Create the minimal package and skill**

  Follow current OpenAI portable Plugin packaging shape; keep OpenAI-specific compatibility details bounded to the fallback manifest if needed.

- [ ] **Step 4: Run package/projection GREEN**

  Run:
  - `python -m unittest discover -s .gpt-codex/tests -p "test_framework_plugin_package.py" -v`
  - `python -m unittest discover -s .gpt-codex/tests -p "test_consumer_projection.py" -v`
  - `python .gpt-codex/scripts/validate_consumer_projection.py --root .`

- [ ] **Step 5: Commit Task 6**

### Task 7: End-to-end fresh-session installation and self-hosting acceptance

**Files:**
- Modify: `.gpt-codex/tests/test_framework_plugin.py` only for any missing deterministic E2E fixture assertions
- Create: `.gpt-codex/evidence/P2-PLUGIN-E2E-ACCEPTANCE.json` only during the separately authorized implementation Work Unit after the actual manual/runtime acceptance is performed
- No release/version files are modified.

**Interfaces:**
- Installation test uses the built Plugin folder and a temporary/personal local marketplace or supported local install mechanism outside committed Framework authority.
- Acceptance requires one fresh GPT/ChatGPT context and one fresh Codex context with no reliance on previous conversation history.

- [ ] **Step 1: Run full source validation before installation**

  Run:
  - `python -m unittest discover -s .gpt-codex/tests -p "test_*.py" -q`
  - `python .gpt-codex/scripts/validate_framework.py`
  - `python .gpt-codex/scripts/validate_project.py .`
  - `python .gpt-codex/scripts/validate_consumer_projection.py --root .`
  - `git diff --check`

- [ ] **Step 2: Install the Plugin in a fresh local test surface**

  Use a temporary/personal local marketplace or supported local Plugin install mechanism. Do not commit the marketplace into the Framework repository and do not publish to the public Plugin directory in this Work Unit.

- [ ] **Step 3: Run the fresh-session durable handoff scenario**

  Required scenario:
  1. fresh GPT/ChatGPT context uses the Plugin to identify repository/project and resume from durable authority;
  2. GPT prepares an authorized Instruction whose canonical bytes are persisted through an already-authorized repository write path;
  3. fresh Codex context resolves the exact Instruction locator, independently revalidates authority, and executes only if allowed;
  4. Codex publishes Result/Evidence/Git facts through existing governed mechanisms;
  5. fresh GPT/ChatGPT context resumes and discovers the durable Result without manual transcript copying;
  6. independent Reviewer flow remains isolated;
  7. any `next_action_hint` is independently revalidated before execution.

- [ ] **Step 4: Exercise failure cases**

  Repeat with:
  - stale STATE revision;
  - wrong repository/project;
  - missing/invalid Instruction locator;
  - duplicate/invalid Result;
  - unsupported capability request;
  - Plugin unavailable.

  Expected: fail-closed/reconciliation and repository-native fallback remains viable.

- [ ] **Step 5: Record bounded P1 effectiveness evidence**

  Record observable handoff friction, manual copy count, resume success/failure, retries, and recovery findings through the existing P1 evidence path. Do not score automatically and do not let feedback authorize Framework changes.

- [ ] **Step 6: Independent post-execution review**

  Review the exact implementation SHA and E2E evidence. Any finding follows `REVIEW_FINDING -> GPT/User adjudication -> FIX_INSTRUCTION -> fresh implementation -> re-review`.

- [ ] **Step 7: Stop at P2 implementation acceptance**

  P2 is eligible for completion only when installation and the fresh-session scenario pass. Public Plugin publication, universal-directory submission, Framework version bump, and later P3/P4 work remain separate future authority.

## Definition of Done

P2 Revision 002 is complete only when all of the following are proven on an exact reviewed implementation SHA:

1. The Plugin is installable in a supported local test surface.
2. Fresh GPT/ChatGPT and Codex contexts can recover the same project/Work Unit durable facts without prior conversation history.
3. GPT→Codex Instruction delivery is repository-backed, exact-locator based, and separately authority-validated.
4. Codex→GPT Result/Evidence delivery is repository-backed and discoverable without manual transcript copying.
5. The four P2 governance capabilities remain exactly bounded and fail closed.
6. `Change Notification` remains an optional transport hint based on durable authority changes; no background synchronization subsystem is required.
7. Framework operation remains viable when the Plugin is absent.
8. Independent post-execution review passes with no unresolved Critical/Important finding.
9. P1 receives bounded real effectiveness evidence from the P2 acceptance cycle.
10. No Framework release/version or public Plugin publication occurs in this Work Unit.

## Plan Self-Review

- Every Design Revision 002 requirement maps to a task above.
- The Plan reuses current repository-native resume, Instruction, Result, validation, role, feedback, and Git authority.
- The only new persistent convention is the project-owned durable Instruction artifact path under the existing Evidence surface; it is not a second authority/state store.
- No task introduces an MCP server, committed marketplace, queue, daemon, registry, workflow engine, central state service, or conversation synchronization.
- Package installation is tested only after source validation and does not itself authorize execution.
- P2 implementation remains blocked until this Plan is independently reviewed, accepted, integrated, and a separate implementation Work Unit plus PRE-EXECUTION PASS exist.
