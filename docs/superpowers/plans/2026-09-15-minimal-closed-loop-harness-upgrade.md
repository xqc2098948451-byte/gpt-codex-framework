# Minimal Closed-Loop Harness Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the current P0 framework into a smaller, reusable development Harness that preserves proven authority/recovery capabilities while adding production isolation, reliable handoff, fixed project strategy, bounded process records, Framework feedback, compact GPT↔Codex exchange, and evidence-driven reduction.

**Architecture:** Implement the upgrade as an additive transition over the frozen P0 baseline, never as a flag-day rewrite. New lightweight Harness concepts are introduced first and proved by tests; current P0 Work Unit, slot, Resume, Project Map, telemetry, envelopes, and validators remain in place until the final reduction review proves that a capability-preserving replacement exists. No eighth Framework module is introduced.

**Tech Stack:** Python 3 standard library, JSON Schema already used by the repository, Markdown project templates, existing Framework Module Registry, existing consumer-projection tooling, `unittest`, Git.

**Spec:** `docs/superpowers/specs/2026-09-15-minimal-closed-loop-harness-upgrade-design.md`

## Frozen Inputs

- P0 frozen baseline: `224d8c0ebdfdc0aa7024f2c69f06fc6fcfe4c699`
- Accepted Design commit: `061a119157be1602d61ced0276cb54a451bb6e8e`
- Accepted Design SHA256: `f18830447f9c3ce694ae7af3cd6d72fe57fe63f191f635564971accb1443b947`
- Implementation branches MUST descend from the commit that stores this Plan on top of the accepted Design.
- Existing P0 full-suite baseline before this upgrade: `443 tests / 0 failures / 0 errors`.

## Global Constraints

- Highest rule: **Preserve capability, compress structure; preserve the closed loop, remove duplication.**
- This rule applies to ordinary projects, project directory design, GPT/Codex collaboration, the Harness, and `gpt-codex-framework`.
- Preserve P0 capabilities until an explicit reduction gate proves a replacement: Git SHA/ancestry authority, Framework/Project separation, project isolation, role boundaries, review/remediation causality, cold-recovery semantics, production/consumer projection boundaries, and fail-closed ambiguity handling.
- No global fixed Codex count, Work Unit count, reviewer count, or parallelism target.
- Ordinary projects may emit process data, `PROCESS_REVIEW`, `FRAMEWORK_FEEDBACK`, and improvement candidates; they may not mutate global Framework policy.
- Only `gpt-codex-framework` may create or change global Harness rules, strategy profiles, templates, or Framework versions.
- No private model chain-of-thought is stored. `REASONING.md` contains only observable strategy, decisions, bounded process summaries, and structure-change rationale.
- Handoff is a derived view, never a second state authority.
- Production packaging must exclude Harness-only content by default.
- No Resource Governor, automatic token scheduler, agent scoring, Planner, Dispatcher, autonomous learning loop, automatic Framework optimizer, or new analytics service.
- P0-6 telemetry stays optional and observational. The upgrade must not make telemetry required for correctness.
- Existing P0 contracts are reused canonically during transition: canonical contract validation → authority validation → local context/correlation validation.
- Every task is TDD: RED → minimal implementation → focused GREEN → affected regression → commit.
- Every task must keep `python .gpt-codex/scripts/validate_framework.py`, `python .gpt-codex/scripts/validate_project.py .`, and `python .gpt-codex/scripts/validate_consumer_projection.py --root .` passing before acceptance.
- Consumer projection must end every task with `unknown_paths = 0`, `missing_required_paths = 0`, `invalid_classifications = 0`.
- Do not change `VERSION` or publish a release until a separately authorized release Work Unit after all tasks and the reduction review complete.

### A. DEVELOPMENT BASELINE RULE

Implementation may begin only from a commit where the Design and complete Plan are persisted; projection, Framework, and Project validation pass; the full baseline test suite passes; and the remote commit is verified. That commit is the `DEVELOPMENT_BASELINE_SHA`. Every implementation task descends from the current accepted `DEVELOPMENT_BASELINE_SHA` or an accepted implementation descendant.

### B. NEW-PATH CLOSURE RULE

Every repository path newly created by a task MUST be classified in `.gpt-codex/release/consumer-projection-manifest.json` in the SAME task before commit. Consumer Harness runtime assets are `CONSUMER_REQUIRED`; Framework-management implementation and test assets are `MANAGEMENT_ONLY`; Design, Plan, review, and process historical documents are `DEVELOPMENT_HISTORY`; release metadata is used only for genuine release metadata. A task with an unknown new path is incomplete.

### C. DIRECT TEST EXECUTION RULE

Any Python unittest file invoked as `python path/to/test_file.py` ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

Otherwise the Plan invokes it through unittest discovery. An exit code of zero without executing the intended tests is not PASS.

### D. TRANSFER PREFACE RULE

Task 4 formalizes this user-facing preface before the four task semantics:

```text
是否需要你上传内容：
需要上传的内容：
读取来源：
```

The preface grants no authority and does not replace GOAL, SCOPE, CONSTRAINTS, or DONE.

---

## File / Responsibility Map

### Existing files that remain authoritative during transition

- `.gpt-codex/schemas/control.schema.json` — project/framework boundary and project-level machine configuration.
- `.gpt-codex/project-template/CONTROL.template.json` — transitional machine template for adopted projects.
- `.gpt-codex/scripts/validate_project.py` — canonical project validation entry point.
- `.gpt-codex/scripts/continuity_resume.py` — existing durable recovery logic; gains the derived handoff view.
- `.gpt-codex/scripts/instruction_envelope.py` — existing authoritative instruction contract; gains a compact task renderer only.
- `.gpt-codex/scripts/result_return.py` — existing Result view renderer; gains durable-ref-first compact return.
- `.gpt-codex/release/consumer-projection-manifest.json` — projection classification authority.
- `.gpt-codex/project-template/` — source templates for ordinary projects.

### New lightweight assets

- `.gpt-codex/project-template/.harness/RULES.template.md`
- `.gpt-codex/project-template/.harness/STATE.template.md`
- `.gpt-codex/project-template/.harness/REASONING.template.md`
- `.gpt-codex/project-template/.harness/FEEDBACK.template.md`
- `.gpt-codex/scripts/framework_feedback.py` — one small, pure module for bounded process-review/feedback records and efficiency counters. This single module intentionally replaces separate Learning/Incident/Proposal subsystems.
- `.gpt-codex/tests/test_harness_project_layering.py`
- `.gpt-codex/tests/test_harness_handoff.py`
- `.gpt-codex/tests/test_framework_feedback.py`
- `.gpt-codex/tests/test_minimal_task_protocol.py`
- `.gpt-codex/tests/test_harness_reduction_gate.py`

No new Framework module is created. The new feedback helper is routed to `framework-core`; Handoff remains `navigation-continuity`; projection changes remain `release-projection`.

---

### Task 1: Establish semantic project layering and production isolation

**Files:**
- Modify: `.gpt-codex/schemas/control.schema.json`
- Modify: `.gpt-codex/project-template/CONTROL.template.json`
- Modify: `.gpt-codex/project-template/README.md`
- Create: `.gpt-codex/project-template/.harness/RULES.template.md`
- Create: `.gpt-codex/project-template/.harness/STATE.template.md`
- Create: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Create: `.gpt-codex/project-template/.harness/FEEDBACK.template.md`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/scripts/consumer_projection.py`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Create: `.gpt-codex/tests/test_harness_project_layering.py`
- Modify: `.gpt-codex/tests/test_consumer_projection.py`
- Modify: `.gpt-codex/tests/test_release_packaging.py`

**Interfaces:**
- Produces optional transitional CONTROL root fields:
  - `roots.harness_root: str`
  - `roots.product_roots: list[str]`
  - `roots.deploy_roots: list[str]`
  - `roots.production_excludes: list[str]`
- Produces `validate_harness_root_separation(control: Mapping[str, Any]) -> list[str]`.
- Extends the existing `stage_consumer_projection(...)` helper with a bounded optional `production_excludes=()` input; no second staging or packaging implementation is created.
- Produces four consumer-required `.harness` templates.
- Does not delete or rename current `.gpt-codex` P0 assets.

- [ ] **Step 1: Write failing semantic-root and production-isolation tests**

Create `.gpt-codex/tests/test_harness_project_layering.py` with:

```python
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_project import validate_harness_root_separation  # noqa: E402


class HarnessProjectLayeringTests(unittest.TestCase):
    def test_default_semantic_roots_are_disjoint(self):
        control = json.loads(
            (ROOT / ".gpt-codex/project-template/CONTROL.template.json").read_text(encoding="utf-8")
        )
        self.assertEqual(control["roots"]["harness_root"], ".harness")
        self.assertEqual(control["roots"]["product_roots"], ["app"])
        self.assertEqual(control["roots"]["deploy_roots"], ["ops"])
        self.assertIn(".harness", control["roots"]["production_excludes"])
        self.assertEqual(validate_harness_root_separation(control), [])

    def test_exact_and_nested_semantic_root_overlap_is_rejected(self):
        for roots in (
            {"harness_root": ".harness", "product_roots": [".harness"], "deploy_roots": ["ops"]},
            {"harness_root": ".harness", "product_roots": [".harness/app"], "deploy_roots": ["ops"]},
            {"harness_root": ".harness/project", "product_roots": [".harness"], "deploy_roots": ["ops"]},
            {"harness_root": ".harness", "product_roots": ["app"], "deploy_roots": ["app/deploy"]},
        ):
            with self.subTest(roots=roots):
                roots["production_excludes"] = [".harness"]
                self.assertEqual(
                    validate_harness_root_separation({"roots": roots}),
                    ["HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP"],
                )

    def test_unsafe_root_paths_are_rejected(self):
        for unsafe in ("/absolute", "../traversal", "app/../other", "./app", "app//nested", "app\\windows"):
            control = {
                "roots": {
                    "harness_root": unsafe,
                    "product_roots": ["app"],
                    "deploy_roots": ["ops"],
                    "production_excludes": [unsafe],
                }
            }
            with self.subTest(unsafe=unsafe):
                self.assertEqual(validate_harness_root_separation(control), ["HARNESS_ROOTS_INVALID"])

    def test_harness_cannot_be_product_or_deploy_root(self):
        control = {
            "roots": {
                "harness_root": ".harness",
                "product_roots": [".harness"],
                "deploy_roots": ["ops"],
                "production_excludes": [".harness"],
            }
        }
        self.assertEqual(
            validate_harness_root_separation(control),
            ["HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP"],
        )

    def test_harness_must_be_excluded_from_production(self):
        control = {
            "roots": {
                "harness_root": ".harness",
                "product_roots": ["app"],
                "deploy_roots": ["ops"],
                "production_excludes": [],
            }
        }
        self.assertEqual(
            validate_harness_root_separation(control),
            ["HARNESS_PRODUCTION_EXCLUSION_REQUIRED"],
        )

    def test_legacy_control_without_semantic_roots_remains_valid(self):
        self.assertEqual(validate_harness_root_separation({"roots": {"project_role": "AUTHORITATIVE"}}), [])

    def test_minimal_harness_templates_exist(self):
        harness = ROOT / ".gpt-codex/project-template/.harness"
        self.assertEqual(
            {path.name for path in harness.glob("*.template.md")},
            {
                "RULES.template.md",
                "STATE.template.md",
                "REASONING.template.md",
                "FEEDBACK.template.md",
            },
        )
```

The file ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python .gpt-codex/tests/test_harness_project_layering.py
```

Expected: import failure for `validate_harness_root_separation` and/or missing `.harness` templates.

- [ ] **Step 3: Add root fields to schema and template**

In `.gpt-codex/schemas/control.schema.json`, add these properties under `roots.properties` without removing existing P0 properties:

```json
"harness_root": {"type": "string", "minLength": 1},
"product_roots": {
  "type": "array",
  "minItems": 1,
  "items": {"type": "string", "minLength": 1},
  "uniqueItems": true
},
"deploy_roots": {
  "type": "array",
  "items": {"type": "string", "minLength": 1},
  "uniqueItems": true
},
"production_excludes": {
  "type": "array",
  "items": {"type": "string", "minLength": 1},
  "uniqueItems": true
}
```

Do not add them to the top-level schema `required` set yet; existing P0 projects remain backward compatible during transition.

In `.gpt-codex/project-template/CONTROL.template.json`, add:

```json
"harness_root": ".harness",
"product_roots": ["app"],
"deploy_roots": ["ops"],
"production_excludes": [".harness"]
```

inside `roots`.

- [ ] **Step 4: Implement the fail-closed separation validator**

Every declared `harness_root`, `product_roots[]`, `deploy_roots[]`, and `production_excludes[]` value is a safe repository-relative POSIX path. Reject absolute paths, `..` traversal, `.` components, empty path components, and backslash-form repository paths with `HARNESS_ROOTS_INVALID`. Keep this path checking private to the existing Task-1 project-root validator; do not create a path-validation subsystem.

Two semantic roots overlap when they are equal or either is a descendant of the other. Harness, Product, and Deploy roots are pairwise subtree-disjoint. Exact and nested overlap returns `HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP`.

Add to `.gpt-codex/scripts/validate_project.py`:

```python
def validate_harness_root_separation(control: Mapping[str, Any]) -> list[str]:
    roots = control.get("roots")
    if not isinstance(roots, Mapping):
        return []
    declared = (
        "harness_root" in roots
        or "product_roots" in roots
        or "deploy_roots" in roots
        or "production_excludes" in roots
    )
    if not declared:
        return []
    harness = roots.get("harness_root")
    products = roots.get("product_roots")
    deploy = roots.get("deploy_roots")
    excludes = roots.get("production_excludes")
    if (
        not isinstance(harness, str) or not harness.strip()
        or not isinstance(products, list) or not products
        or not all(isinstance(item, str) and item.strip() for item in products)
        or not isinstance(deploy, list)
        or not all(isinstance(item, str) and item.strip() for item in deploy)
        or not isinstance(excludes, list)
        or not all(isinstance(item, str) and item.strip() for item in excludes)
    ):
        return ["HARNESS_ROOTS_INVALID"]
    if not all(_is_safe_repository_relative_path(item) for item in [harness, *products, *deploy, *excludes]):
        return ["HARNESS_ROOTS_INVALID"]
    if any(_paths_overlap(left, right) for left, right in _root_pairs(harness, products, deploy)):
        return ["HARNESS_PRODUCT_DEPLOY_ROOT_OVERLAP"]
    if harness not in excludes:
        return ["HARNESS_PRODUCTION_EXCLUSION_REQUIRED"]
    return []
```

Wire this validator into the existing project validation aggregation so a declared invalid layering fails project validation, while projects with none of the four new fields remain valid.

`_is_safe_repository_relative_path`, `_paths_overlap`, and `_root_pairs` are small private helpers in `validate_project.py`. They do not grant authority and do not duplicate staging validation.

- [ ] **Step 5: Create the four minimal Harness templates**

Create `.gpt-codex/project-template/.harness/RULES.template.md`:

```markdown
# Project Harness Rules

## Highest Principle
Preserve capability, compress structure; preserve the closed loop, remove duplication.

## Semantic Roots
HARNESS_ROOT = .harness
PRODUCT_ROOTS = app
DEPLOY_ROOTS = ops

## Production Boundary
Harness content is development/governance-only and must not be required by product runtime.

## Stable Project Rules
- Project authority remains local to this repository.
- Reference durable artifacts instead of copying them when possible.
- Framework-wide changes are feedback only; global evolution occurs in gpt-codex-framework.
```

Create `.gpt-codex/project-template/.harness/STATE.template.md`:

```markdown
# Current Project State

PROJECT_STATUS = PROPOSED
CURRENT_GOAL = NONE
CURRENT_TASK = NONE
CURRENT_BRANCH = NONE
BASE_SHA = NONE
CURRENT_SHA = NONE
BLOCKER = NONE
PENDING_RESULT_REF = NONE
NEXT_ACTION = INITIALIZE_PROJECT
```

Create `.gpt-codex/project-template/.harness/REASONING.template.md`:

```markdown
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

## Process Reviews
No milestone process review recorded yet.
```

Create `.gpt-codex/project-template/.harness/FEEDBACK.template.md`:

```markdown
# Framework Feedback

No framework feedback recorded yet.

## Feedback Item Format
PROBLEM:
REASON:
LOCAL_SOLUTION:
RESULT:
FRAMEWORK_CHANGE_RECOMMENDED:
EVIDENCE_REFS:
```

- [ ] **Step 6: Update project-template bootstrap documentation**

Replace the opening bootstrap description in `.gpt-codex/project-template/README.md` with a transitional two-surface rule:

```markdown
The current transition supports the existing `.gpt-codex/` governance assets and the new minimal `.harness/` project surface in parallel.

- Copy/adapt `.gpt-codex/project-template/.harness/` to `PROJECT_ROOT/.harness/`.
- Existing `.gpt-codex/` P0 assets remain supported until the reduction phase proves they can be merged or removed.
- Product/runtime code belongs in project product roots, not in `.harness/`.
- Production packaging excludes `.harness/` by default.
```

Keep the existing Framework advisory/read-only and compatibility text.

- [ ] **Step 7: Classify every new Task-1 path**

Add the four new paths to `.gpt-codex/release/consumer-projection-manifest.json` as `CONSUMER_REQUIRED`, matching the existing project-template classification.

Also classify `.gpt-codex/tests/test_harness_project_layering.py` as `MANAGEMENT_ONLY`. `test_consumer_projection.py` directly asserts exactly these five classifications: the four Harness template paths are `CONSUMER_REQUIRED`, and `.gpt-codex/tests/test_harness_project_layering.py` is `MANAGEMENT_ONLY`. General unknown-path auditing does not replace this exact assertion.

- [ ] **Step 8: Add production-packaging regression**

Extend the existing `stage_consumer_projection(root, staging_root, manifest, *, production_excludes=())` helper minimally. Existing callers without `production_excludes` behave exactly as before. The helper consumes exclusions already validated by `validate_harness_root_separation`: the excluded root and all descendants are not staged, while product paths outside excluded roots remain staged. Do not duplicate semantic-root validation inside `consumer_projection.py`.

In `.gpt-codex/tests/test_release_packaging.py`, create a temporary consumer workspace containing `.harness/RULES.md`, a product path, and the Task-1 CONTROL semantic-root declaration. Obtain the validated `production_excludes` from that declaration and pass them through `stage_consumer_projection`. Prove `.harness/` and descendants are absent while product content remains staged. Do not make `.harness/RULES.md` `MANAGEMENT_ONLY` the mechanism under test; the exclusion outcome must be causally attributable to `production_excludes`.

- [ ] **Step 9: Run focused and affected tests**

Run:

```bash
python .gpt-codex/tests/test_harness_project_layering.py
python .gpt-codex/tests/test_consumer_projection.py
python .gpt-codex/tests/test_release_packaging.py
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
```

Task 1 is incomplete unless every Task-1-created repository path is classified and `unknown_paths = 0`.

Expected: all PASS; projection unknown/missing/invalid = 0; Harness/Product/Deploy roots are safe repository-relative POSIX paths and pairwise subtree-disjoint; `production_excludes` causally excludes its root and descendants from the existing staging helper.

- [ ] **Step 10: Commit**

```bash
git add \
  .gpt-codex/schemas/control.schema.json \
  .gpt-codex/project-template/CONTROL.template.json \
  .gpt-codex/project-template/README.md \
  .gpt-codex/project-template/.harness \
  .gpt-codex/scripts/validate_project.py \
  .gpt-codex/scripts/consumer_projection.py \
  .gpt-codex/release/consumer-projection-manifest.json \
  .gpt-codex/tests/test_harness_project_layering.py \
  .gpt-codex/tests/test_consumer_projection.py \
  .gpt-codex/tests/test_release_packaging.py
git commit -m "feat: add minimal harness project layering"
```

---

### Task 2: Add one derived project-handoff entry point and immutable artifact references

**Files:**
- Modify: `.gpt-codex/schemas/work-unit.schema.json`
- Modify: `.gpt-codex/project-template/WORK_UNIT.template.json`
- Modify: `.gpt-codex/scripts/continuity_resume.py`
- Create: `.gpt-codex/tests/test_harness_handoff.py`
- Modify: `.gpt-codex/tests/test_continuity_resume.py`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`

**Interfaces:**
- Produces optional Work Unit field:
  - `artifact_refs.design = {"path": str, "sha": 40hex} | null`
  - `artifact_refs.plan = {"path": str, "sha": 40hex} | null`
- Produces `build_project_handoff(root: Path, execution_slot_id: str | None = None) -> dict[str, Any]`.
- Handoff statuses: `HANDOFF_READY`, `EXECUTION_CONTEXT_MISMATCH`, `RECONCILIATION_REQUIRED`.
- Handoff is derived-only and never writes STATE/Work Unit/Result/Evidence/Git.

- [ ] **Step 1: Write failing handoff tests**

Create `.gpt-codex/tests/test_harness_handoff.py` with fixtures built from the existing continuity test helpers and these assertions:

```python
class HarnessHandoffTests(unittest.TestCase):
    def test_handoff_contains_one_safe_next_action_and_strategy(self):
        result = build_project_handoff(self.root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "HANDOFF_READY")
        self.assertFalse(result["reconciliation_required"])
        self.assertEqual(result["current_work"]["work_unit_id"], "WU-1")
        self.assertEqual(result["git"]["current_head_sha"], self.head)
        self.assertEqual(result["next_action"], "CONTINUE_IMPLEMENTATION")

    def test_multiple_pending_results_fail_closed(self):
        self.write_matching_result("result-a")
        self.write_matching_result("result-b")
        result = build_project_handoff(self.root, execution_slot_id="slot-1")
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertTrue(result["reconciliation_required"])

    def test_artifact_ref_uses_sha_path_not_branch_search(self):
        result = build_project_handoff(self.root, execution_slot_id="slot-1")
        self.assertEqual(
            result["accepted_artifacts"]["plan"],
            {"path": "docs/plan.md", "sha": self.base_sha},
        )
```

Also test a provided slot binding contradiction maps to `EXECUTION_CONTEXT_MISMATCH`, while missing authority maps to `RECONCILIATION_REQUIRED`.

The file ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run focused handoff test and verify RED**

Run:

```bash
python .gpt-codex/tests/test_harness_handoff.py
```

Expected: `ImportError` or missing `build_project_handoff`.

`test_harness_handoff.py` ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Add optional immutable artifact refs to Work Unit schema/template**

Add to `.gpt-codex/schemas/work-unit.schema.json`:

```json
"artifact_refs": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "design": {"$ref": "#/$defs/ImmutableArtifactRef"},
    "plan": {"$ref": "#/$defs/ImmutableArtifactRef"}
  }
}
```

and:

```json
"$defs": {
  "ImmutableArtifactRef": {
    "type": ["object", "null"],
    "required": ["path", "sha"],
    "additionalProperties": false,
    "properties": {
      "path": {"type": "string", "minLength": 1},
      "sha": {"type": "string", "pattern": "^[0-9a-fA-F]{40}$"}
    }
  }
}
```

If `$defs` already exists, merge rather than replace it.

Add to `WORK_UNIT.template.json`:

```json
"artifact_refs": {
  "design": null,
  "plan": null
}
```

The field stays optional for old Work Units.

- [ ] **Step 4: Implement bounded artifact-ref verification**

Add a private helper in `continuity_resume.py`:

```python
def _git_object_path_exists(root: Path, sha: str, path: str) -> bool:
    if not _COMMIT_SHA.fullmatch(sha) or not isinstance(path, str) or not path.strip():
        return False
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{sha}:{path}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0
```

Add:

```python
def _validated_artifact_refs(root: Path, work_unit: Mapping) -> dict[str, Any] | None:
    refs = work_unit.get("artifact_refs")
    if refs is None:
        return {"design": None, "plan": None}
    if not isinstance(refs, Mapping) or set(refs) - {"design", "plan"}:
        return None
    result = {"design": None, "plan": None}
    for name in ("design", "plan"):
        ref = refs.get(name)
        if ref is None:
            continue
        if (
            not isinstance(ref, Mapping)
            or set(ref) != {"path", "sha"}
            or not _git_object_path_exists(root, ref.get("sha"), ref.get("path"))
        ):
            return None
        result[name] = {"path": ref["path"], "sha": ref["sha"]}
    return result
```

- [ ] **Step 5: Implement unique pending-result discovery**

Reuse `_valid_recovery_result`; do not implement a second Result contract.

Add a helper that scans `.gpt-codex/evidence/results/*.json`, accepts only canonical valid Results matching current `project_id`, `work_unit_id`, current instruction/review correlation, and current/review-target SHA, and returns:

```python
(None, [])                       # zero match
(record, [])                     # exactly one match
(None, ["RECONCILIATION_REQUIRED"])  # more than one
```

Do not select by timestamp or filename when multiple authoritative candidates match.

- [ ] **Step 6: Implement `build_project_handoff` as a derived composition**

Add:

```python
def build_project_handoff(root: Path, execution_slot_id: str | None = None) -> dict[str, Any]:
    control = load_project_identity(root)
    state_path = root / ".gpt-codex" / "STATE.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _recovery_result()

    slots = state.get("active_execution_slots")
    if not isinstance(slots, list):
        return _recovery_result()

    candidates = [
        slot for slot in slots
        if isinstance(slot, Mapping)
        and slot.get("status") != "IDLE"
        and (execution_slot_id is None or slot.get("slot_id") == execution_slot_id)
    ]
    if len(candidates) != 1:
        return _recovery_result()

    slot = candidates[0]
    recovery = _execution_slot_recovery(
        root,
        control,
        state,
        slot["slot_id"],
        None,
        None,
    )
    if recovery.get("reconciliation_required"):
        status = recovery.get("status")
        if status == "EXECUTION_SLOT_MISMATCH":
            status = "EXECUTION_CONTEXT_MISMATCH"
        return {"status": status, "reconciliation_required": True}

    work_unit = _load_recovery_work_unit(root, control, slot, state)
    refs = _validated_artifact_refs(root, work_unit)
    if refs is None:
        return _recovery_result()

    pending, errors = _discover_pending_result(root, control, slot, state)
    if errors:
        return _recovery_result()

    strategy = _load_harness_strategy(root)
    return {
        "status": "HANDOFF_READY",
        "reconciliation_required": False,
        "project": {
            "project_id": control.get("project_id"),
            "project_context_id": control.get("project_context_id"),
            "repository": (control.get("github") or {}).get("repository_full_name"),
        },
        "state": {"revision": state.get("revision"), "state": state.get("state")},
        "current_work": {
            "execution_slot_id": slot.get("slot_id"),
            "status": slot.get("status"),
            "work_unit_id": slot.get("work_unit_id"),
        },
        "git": {
            "branch": slot.get("branch"),
            "base_sha": slot.get("base_sha"),
            "current_head_sha": slot.get("current_head_sha"),
            "last_accepted_sha": slot.get("last_accepted_sha"),
        },
        "accepted_artifacts": refs,
        "strategy": strategy,
        "latest_result_ref": (state.get("continuity") or {}).get("last_verified_result_ref"),
        "pending_result_ref": pending.get("result_id") if pending else None,
        "blocker": slot.get("block_reason"),
        "next_action": slot.get("next_action"),
    }
```

Implement `_load_harness_strategy(root)` as a bounded reader of `.harness/REASONING.md` strategy key/value lines; if `.harness/REASONING.md` is absent, return `None` without blocking recovery.

- [ ] **Step 7: Keep existing cold recovery behavior green**

Run:

```bash
python .gpt-codex/tests/test_harness_handoff.py
python .gpt-codex/tests/test_continuity_resume.py
python .gpt-codex/tests/test_context_window_resume.py
python .gpt-codex/tests/test_navigation_project_validation.py
```

Expected: all PASS; existing slot mismatch/reconciliation semantics remain intact.

- [ ] **Step 8: Run validators and commit**

Classify `.gpt-codex/tests/test_harness_handoff.py` as `MANAGEMENT_ONLY`, run projection validation, and require `unknown_paths = 0`, `missing_required_paths = 0`, and `invalid_classifications = 0` before commit.

Run validators, then:

```bash
git add \
  .gpt-codex/schemas/work-unit.schema.json \
  .gpt-codex/project-template/WORK_UNIT.template.json \
  .gpt-codex/scripts/continuity_resume.py \
  .gpt-codex/tests/test_harness_handoff.py \
  .gpt-codex/tests/test_continuity_resume.py \
  .gpt-codex/release/consumer-projection-manifest.json
git commit -m "feat: add derived project handoff"
```

---

### Task 3: Fix project strategy and bounded process records without storing private reasoning

**Files:**
- Modify: `.gpt-codex/schemas/control.schema.json`
- Modify: `.gpt-codex/project-template/CONTROL.template.json`
- Modify: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Create: `.gpt-codex/scripts/framework_feedback.py`
- Create: `.gpt-codex/tests/test_framework_feedback.py`
- Modify: `.gpt-codex/framework-modules/modules/framework-core.json`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Modify: `.gpt-codex/tests/test_framework_module_routing.py`
- Modify: `.gpt-codex/tests/test_consumer_projection.py`

**Interfaces:**
- Produces optional CONTROL `execution_policy`.
- Produces immutable `ProcessReview` and `FrameworkFeedback` dataclasses.
- Produces:
  - `validate_execution_policy(policy: Mapping[str, Any] | None) -> list[str]`
  - `build_process_review(records: Sequence[Mapping[str, Any]], strategy_profile: str, usage: Mapping[str, Any] | None = None) -> ProcessReview`
  - `validate_framework_feedback(record: Mapping[str, Any]) -> list[str]`
- `framework_feedback.py` is data-only; it has no mutation/release/adoption functions.

- [ ] **Step 1: Write failing strategy/feedback tests**

Create `.gpt-codex/tests/test_framework_feedback.py` with:

```python
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from framework_feedback import (  # noqa: E402
    build_process_review,
    validate_execution_policy,
    validate_framework_feedback,
)


class FrameworkFeedbackTests(unittest.TestCase):
    def test_execution_policy_is_bounded_and_project_fixed(self):
        policy = {
            "strategy_profile_id": "PROJECT_PROFILE_001",
            "gpt_orchestrator_strategy": "MINIMAL_CLOSED_LOOP",
            "codex_implementer_strategy": "MINIMAL_DIFF_TDD",
            "codex_reviewer_strategy": "CONTRACT_FIRST",
            "task_splitting": "PROJECT_DETERMINED",
            "review_policy": "RISK_OR_MILESTONE",
            "instruction_policy": "REFERENCE_FIRST",
            "result_return_policy": "DURABLE_REF_FIRST",
        }
        self.assertEqual(validate_execution_policy(policy), [])

    def test_process_review_uses_unknown_when_usage_is_unavailable(self):
        review = build_process_review(
            [
                {"codex_tasks": 1, "codex_retries": 2, "gpt_interventions": 1,
                 "review_rounds": 1, "remediation_rounds": 0,
                 "handoffs": 1, "handoff_failures": 0, "project_result": "PASS"}
            ],
            "PROJECT_PROFILE_001",
            usage=None,
        )
        self.assertEqual(review.usage, "UNKNOWN")
        self.assertEqual(review.codex_retries, 2)

    def test_feedback_is_evidence_not_framework_authority(self):
        record = {
            "problem": "handoff reconstruction",
            "reason": "missing durable project summary",
            "local_solution": "derived repository handoff",
            "result": "PASS",
            "framework_change_recommended": True,
            "evidence_refs": ["result:1"],
        }
        self.assertEqual(validate_framework_feedback(record), [])
        self.assertNotIn("authorized_actions", record)
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```bash
python .gpt-codex/tests/test_framework_feedback.py
```

Expected: missing module.

`test_framework_feedback.py` ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Add optional `execution_policy` to CONTROL**

Add schema property:

```json
"execution_policy": {
  "type": "object",
  "additionalProperties": false,
  "required": [
    "strategy_profile_id",
    "gpt_orchestrator_strategy",
    "codex_implementer_strategy",
    "codex_reviewer_strategy",
    "task_splitting",
    "review_policy",
    "instruction_policy",
    "result_return_policy"
  ],
  "properties": {
    "strategy_profile_id": {"type": "string", "minLength": 1, "maxLength": 128},
    "gpt_orchestrator_strategy": {"type": "string", "minLength": 1, "maxLength": 128},
    "codex_implementer_strategy": {"type": "string", "minLength": 1, "maxLength": 128},
    "codex_reviewer_strategy": {"type": "string", "minLength": 1, "maxLength": 128},
    "task_splitting": {"const": "PROJECT_DETERMINED"},
    "review_policy": {"enum": ["RISK_OR_MILESTONE", "EXPLICIT"]},
    "instruction_policy": {"const": "REFERENCE_FIRST"},
    "result_return_policy": {"const": "DURABLE_REF_FIRST"}
  }
}
```

Add the concrete default policy from the test to `CONTROL.template.json`.

Keep it optional in the schema during transition.

- [ ] **Step 4: Implement one bounded feedback/process module**

Create `.gpt-codex/scripts/framework_feedback.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

_REQUIRED_POLICY_KEYS = frozenset({
    "strategy_profile_id",
    "gpt_orchestrator_strategy",
    "codex_implementer_strategy",
    "codex_reviewer_strategy",
    "task_splitting",
    "review_policy",
    "instruction_policy",
    "result_return_policy",
})
_FORBIDDEN_FEEDBACK_AUTHORITY = frozenset({
    "authorized_actions",
    "framework_mutation",
    "policy_update",
    "release_authority",
    "adoption_authority",
})


@dataclass(frozen=True, slots=True)
class ProcessReview:
    strategy_profile: str
    codex_tasks: int
    codex_retries: int
    gpt_interventions: int
    review_rounds: int
    remediation_rounds: int
    handoffs: int
    handoff_failures: int
    project_result: str
    usage: Mapping[str, Any] | str


@dataclass(frozen=True, slots=True)
class FrameworkFeedback:
    problem: str
    reason: str
    local_solution: str
    result: str
    framework_change_recommended: bool
    evidence_refs: tuple[str, ...]


def _non_negative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_execution_policy(policy: Mapping[str, Any] | None) -> list[str]:
    if policy is None:
        return []
    if not isinstance(policy, Mapping) or set(policy) != _REQUIRED_POLICY_KEYS:
        return ["EXECUTION_POLICY_INVALID"]
    if policy["task_splitting"] != "PROJECT_DETERMINED":
        return ["EXECUTION_POLICY_INVALID"]
    if policy["instruction_policy"] != "REFERENCE_FIRST":
        return ["EXECUTION_POLICY_INVALID"]
    if policy["result_return_policy"] != "DURABLE_REF_FIRST":
        return ["EXECUTION_POLICY_INVALID"]
    if policy["review_policy"] not in {"RISK_OR_MILESTONE", "EXPLICIT"}:
        return ["EXECUTION_POLICY_INVALID"]
    for key in (
        "strategy_profile_id",
        "gpt_orchestrator_strategy",
        "codex_implementer_strategy",
        "codex_reviewer_strategy",
    ):
        value = policy[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            return ["EXECUTION_POLICY_INVALID"]
    return []


def build_process_review(
    records: Sequence[Mapping[str, Any]],
    strategy_profile: str,
    usage: Mapping[str, Any] | None = None,
) -> ProcessReview:
    counters = {
        "codex_tasks": 0,
        "codex_retries": 0,
        "gpt_interventions": 0,
        "review_rounds": 0,
        "remediation_rounds": 0,
        "handoffs": 0,
        "handoff_failures": 0,
    }
    project_result = "UNKNOWN"
    for record in records:
        for key in counters:
            value = record.get(key, 0)
            if not _non_negative_int(value):
                raise ValueError("PROCESS_REVIEW_INVALID")
            counters[key] += value
        value = record.get("project_result")
        if isinstance(value, str) and value:
            project_result = value
    return ProcessReview(
        strategy_profile=strategy_profile,
        project_result=project_result,
        usage=dict(usage) if usage is not None else "UNKNOWN",
        **counters,
    )


def validate_framework_feedback(record: Mapping[str, Any]) -> list[str]:
    if not isinstance(record, Mapping) or set(record) & _FORBIDDEN_FEEDBACK_AUTHORITY:
        return ["FRAMEWORK_FEEDBACK_INVALID"]
    required = {
        "problem", "reason", "local_solution", "result",
        "framework_change_recommended", "evidence_refs",
    }
    if set(record) != required:
        return ["FRAMEWORK_FEEDBACK_INVALID"]
    if any(
        not isinstance(record[key], str) or not record[key].strip()
        for key in ("problem", "reason", "local_solution", "result")
    ):
        return ["FRAMEWORK_FEEDBACK_INVALID"]
    if not isinstance(record["framework_change_recommended"], bool):
        return ["FRAMEWORK_FEEDBACK_INVALID"]
    refs = record["evidence_refs"]
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref.strip() for ref in refs):
        return ["FRAMEWORK_FEEDBACK_INVALID"]
    return []
```

Do not add file I/O, network I/O, Framework mutation, scoring, scheduling, or automatic strategy update functions.

- [ ] **Step 5: Reuse policy validation from `validate_project.py`**

Import `validate_execution_policy` and add its errors to project validation when `execution_policy` is present. Do not duplicate the policy rules in `validate_project.py`.

- [ ] **Step 6: Register ownership and projection**

Add exact ownership for `framework_feedback.py` and `test_framework_feedback.py` to `framework-core.json`, with the test in `REQUIRED_TESTS`.

Classify:
- `.gpt-codex/scripts/framework_feedback.py` = `CONSUMER_REQUIRED`
- `.gpt-codex/tests/test_framework_feedback.py` = `MANAGEMENT_ONLY`

Add routing assertions to `test_framework_module_routing.py` and projection assertions to `test_consumer_projection.py`.

- [ ] **Step 7: Run focused/affected tests and validators**

Run:

```bash
python .gpt-codex/tests/test_framework_feedback.py
python .gpt-codex/tests/test_framework_module_routing.py
python .gpt-codex/tests/test_consumer_projection.py
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
```

- [ ] **Step 8: Commit**

```bash
git add \
  .gpt-codex/schemas/control.schema.json \
  .gpt-codex/project-template/CONTROL.template.json \
  .gpt-codex/project-template/.harness/REASONING.template.md \
  .gpt-codex/scripts/validate_project.py \
  .gpt-codex/scripts/framework_feedback.py \
  .gpt-codex/tests/test_framework_feedback.py \
  .gpt-codex/framework-modules/modules/framework-core.json \
  .gpt-codex/release/consumer-projection-manifest.json \
  .gpt-codex/tests/test_framework_module_routing.py \
  .gpt-codex/tests/test_consumer_projection.py
git commit -m "feat: add fixed strategy and framework feedback"
```

---

### Task 4: Add the minimal Codex task view over the existing authoritative instruction contract

**Files:**
- Modify: `.gpt-codex/scripts/instruction_envelope.py`
- Create: `.gpt-codex/tests/test_minimal_task_protocol.py`
- Modify: `.gpt-codex/tests/test_instruction_envelope.py`
- Modify: `.gpt-codex/project-template/.harness/RULES.template.md`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`

**Interfaces:**
- Existing `build_instruction_envelope(...)` remains authoritative and unchanged in meaning.
- Produces:
  - `render_minimal_codex_task(envelope, *, goal: str, scope: list[str], constraints: list[str], done: list[str], refs: Mapping[str, str] | None = None, transfer: Mapping[str, Any] | None = None) -> str`
- The compact view always contains exactly the four required semantic sections: `GOAL`, `SCOPE`, `CONSTRAINTS`, `DONE`.
- Optional refs are `BASE_SHA`, `PLAN_REF`, `STATE_REF`, `OPEN_FINDINGS`, `STRATEGY_PROFILE`.
- The renderer grants no new authority.
- The renderer begins with the human-facing transfer preface before machine/task sections. No-upload instructions begin with `是否需要你上传内容：不需要`, `需要上传的内容：无`, and `读取来源：Git SHA:path`. Upload-required instructions begin with `是否需要你上传内容：需要`, explicit upload item(s), and `读取来源：当前附件或其他 explicit source`.
- The renderer fails closed when `upload_required = True` but upload item(s) or a source are absent. The preface never replaces canonical Instruction Envelope authority.
- `transfer` is absent or `{"upload_required": False, "source": "Git SHA:path"}` for the no-upload form. An upload-required transfer has exactly `upload_required`, `items`, and `source`; `items` is a non-empty bounded list of non-empty strings and `source` is a non-empty string. Invalid transfer values raise `MINIMAL_TASK_INVALID`.

- [ ] **Step 1: Write failing compact-task tests**

Create `.gpt-codex/tests/test_minimal_task_protocol.py`:

```python
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from instruction_envelope import render_minimal_codex_task  # noqa: E402


class MinimalTaskProtocolTests(unittest.TestCase):
    def test_minimal_task_has_four_required_sections(self):
        text = render_minimal_codex_task(
            {
                "instruction_id": "11111111-1111-4111-8111-111111111111",
                "instruction_type": "EXECUTION_INSTRUCTION",
                "target_work_unit": "WU-1",
                "expected_base_sha": "a" * 40,
            },
            goal="Implement parser",
            scope=["src/parser.py", "tests/test_parser.py"],
            constraints=["Do not change public API"],
            done=["Focused tests pass", "git diff --check passes"],
            refs={"STRATEGY_PROFILE": "PROJECT_PROFILE_001"},
        )
        for heading in ("GOAL", "SCOPE", "CONSTRAINTS", "DONE"):
            self.assertIn(f"{heading}:", text)
        self.assertIn("BASE_SHA: " + "a" * 40, text)
        self.assertIn("STRATEGY_PROFILE: PROJECT_PROFILE_001", text)

    def test_empty_required_section_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MINIMAL_TASK_INVALID"):
            render_minimal_codex_task(
                {},
                goal="",
                scope=["src/a.py"],
                constraints=["No API change"],
                done=["tests pass"],
            )
```

- [ ] **Step 2: Run RED**

```bash
python .gpt-codex/tests/test_minimal_task_protocol.py
```

Expected: missing function.

`test_minimal_task_protocol.py` ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Implement the compact renderer**

Add to `instruction_envelope.py`:

```python
_MINIMAL_TASK_REFS = (
    "BASE_SHA", "PLAN_REF", "STATE_REF", "OPEN_FINDINGS", "STRATEGY_PROFILE",
)


def _bounded_text_list(value: object) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or len(value) > 100
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        raise ValueError("MINIMAL_TASK_INVALID")
    return value


def render_minimal_codex_task(
    envelope: Mapping[str, Any],
    *,
    goal: str,
    scope: list[str],
    constraints: list[str],
    done: list[str],
    refs: Mapping[str, str] | None = None,
    transfer: Mapping[str, Any] | None = None,
) -> str:
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("MINIMAL_TASK_INVALID")
    scope = _bounded_text_list(scope)
    constraints = _bounded_text_list(constraints)
    done = _bounded_text_list(done)

    merged_refs: dict[str, str] = {}
    if envelope.get("expected_base_sha"):
        merged_refs["BASE_SHA"] = str(envelope["expected_base_sha"])
    if refs is not None:
        if not isinstance(refs, Mapping) or set(refs) - set(_MINIMAL_TASK_REFS):
            raise ValueError("MINIMAL_TASK_INVALID")
        for key, value in refs.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError("MINIMAL_TASK_INVALID")
            merged_refs[key] = value

    lines = [
        f"INSTRUCTION_ID: {_value(envelope.get('instruction_id'))}",
        f"INSTRUCTION_TYPE: {_value(envelope.get('instruction_type'))}",
        f"TARGET_WORK_UNIT: {_value(envelope.get('target_work_unit'))}",
    ]
    for key in _MINIMAL_TASK_REFS:
        if key in merged_refs:
            lines.append(f"{key}: {merged_refs[key]}")
    for heading, values in (
        ("GOAL", [goal]),
        ("SCOPE", scope),
        ("CONSTRAINTS", constraints),
        ("DONE", done),
    ):
        lines.append("")
        lines.append(f"{heading}:")
        lines.extend(f"- {item}" for item in values)
    return "\n".join(lines)
```

The renderer does not validate/authorize the envelope. Callers must still build and validate the canonical Instruction Envelope before rendering.

- [ ] **Step 4: Document the project-level rule**

Add to `RULES.template.md`:

```markdown
## Codex Task Protocol
Default Codex task view uses GOAL / SCOPE / CONSTRAINTS / DONE plus durable references.
The compact view never replaces canonical authority while legacy P0 authority contracts remain active.
GPT determines task count and parallelism per project.
```

- [ ] **Step 5: Run focused and role regressions**

Classify `.gpt-codex/tests/test_minimal_task_protocol.py` as `MANAGEMENT_ONLY` and run projection validation before commit.

Run:

```bash
python .gpt-codex/tests/test_minimal_task_protocol.py
python .gpt-codex/tests/test_instruction_envelope.py
python .gpt-codex/tests/test_instruction_role_contract.py
python .gpt-codex/tests/test_review_lifecycle.py
```

- [ ] **Step 6: Commit**

```bash
git add \
  .gpt-codex/scripts/instruction_envelope.py \
  .gpt-codex/tests/test_minimal_task_protocol.py \
  .gpt-codex/tests/test_instruction_envelope.py \
  .gpt-codex/project-template/.harness/RULES.template.md \
  .gpt-codex/release/consumer-projection-manifest.json
git commit -m "feat: add minimal codex task view"
```

---

### Task 5: Add durable-ref-first compact Result return and process counters

**Files:**
- Modify: `.gpt-codex/scripts/result_return.py`
- Modify: `.gpt-codex/tests/test_result_return.py`
- Modify: `.gpt-codex/project-template/.harness/STATE.template.md`
- Modify: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Modify: `.gpt-codex/tests/test_framework_feedback.py`

**Interfaces:**
- Existing `render_gpt_return(envelope)` remains available for compatibility.
- Produces:
  - `render_compact_gpt_return(envelope: Mapping[str, Any]) -> str`
  - compact fields: `RESULT`, `WORK_UNIT`, `HEAD_SHA`, `RESULT_REF`, `STATE_REVISION`, `BLOCKERS`, `NEXT_ACTION`.
- Compact return requires a durable Result reference when `return_to_gpt_required=True`.

- [ ] **Step 1: Write failing compact-return tests**

Add to `test_result_return.py`:

```python
def test_compact_return_is_durable_ref_first(self):
    envelope = self.valid_result()
    envelope.update({
        "result_id": "result-1",
        "state_revision": 7,
        "work_unit_id": "WU-1",
        "next_gpt_action": "REVIEW",
        "blockers": [],
        "git": {"implementation_sha": "b" * 40},
        "return_to_gpt_required": True,
    })
    text = self.module.render_compact_gpt_return(envelope)
    self.assertEqual(
        text.splitlines(),
        [
            "RESULT: PASS",
            "WORK_UNIT: WU-1",
            "HEAD_SHA: " + "b" * 40,
            "RESULT_REF: result-1",
            "STATE_REVISION: 7",
            "BLOCKERS: NONE",
            "NEXT_ACTION: REVIEW",
        ],
    )


def test_compact_return_requires_durable_result_ref(self):
    envelope = self.valid_result()
    envelope["return_to_gpt_required"] = True
    envelope.pop("result_id", None)
    with self.assertRaisesRegex(ValueError, "DURABLE_RESULT_REF_REQUIRED"):
        self.module.render_compact_gpt_return(envelope)
```

- [ ] **Step 2: Run RED**

```bash
python .gpt-codex/tests/test_result_return.py
```

- [ ] **Step 3: Implement compact Result rendering**

Add to `result_return.py`:

```python
def render_compact_gpt_return(envelope: Mapping[str, Any]) -> str:
    if not envelope.get("return_to_gpt_required", False):
        return ""
    result_ref = envelope.get("result_id")
    if not isinstance(result_ref, str) or not result_ref.strip():
        raise ValueError("DURABLE_RESULT_REF_REQUIRED")
    git = envelope.get("git")
    if not isinstance(git, Mapping):
        git = {}
    blockers = envelope.get("blockers")
    blocker_text = "NONE"
    if isinstance(blockers, Sequence) and not isinstance(blockers, (str, bytes, bytearray)) and blockers:
        blocker_text = ", ".join(str(item) for item in blockers)
    return "\n".join([
        f"RESULT: {_text(envelope.get('status'))}",
        f"WORK_UNIT: {_text(envelope.get('work_unit_id'))}",
        f"HEAD_SHA: {_text(git.get('implementation_sha', envelope.get('implementation_sha')))}",
        f"RESULT_REF: {result_ref}",
        f"STATE_REVISION: {_text(envelope.get('state_revision'))}",
        f"BLOCKERS: {blocker_text}",
        f"NEXT_ACTION: {_text(envelope.get('next_gpt_action'))}",
    ])
```

Reuse existing `_text`; do not duplicate Result schema validation.

- [ ] **Step 4: Update Harness templates**

In `STATE.template.md`, keep `PENDING_RESULT_REF`.

In `REASONING.template.md`, add a bounded `## Execution Record Format` section:

```markdown
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
```

No raw prompt or private reasoning field is permitted.

- [ ] **Step 5: Add process-counter regression**

Add a test showing the above observable counters can be fed to `build_process_review`, and that `usage=None` remains `UNKNOWN`.

- [ ] **Step 6: Run focused and Result contract regressions**

Run:

```bash
python .gpt-codex/tests/test_result_return.py
python .gpt-codex/tests/test_result_contract_schema.py
python .gpt-codex/tests/test_framework_feedback.py
python .gpt-codex/tests/test_return_context_binding.py
```

- [ ] **Step 7: Commit**

```bash
git add \
  .gpt-codex/scripts/result_return.py \
  .gpt-codex/tests/test_result_return.py \
  .gpt-codex/project-template/.harness/STATE.template.md \
  .gpt-codex/project-template/.harness/REASONING.template.md \
  .gpt-codex/tests/test_framework_feedback.py
git commit -m "feat: add durable ref result return"
```

---

### Task 6: Enforce centralized Framework evolution and bounded project feedback

**Files:**
- Modify: `.gpt-codex/project-template/.harness/FEEDBACK.template.md`
- Modify: `.gpt-codex/scripts/framework_feedback.py`
- Modify: `.gpt-codex/scripts/validate_project.py`
- Modify: `.gpt-codex/tests/test_framework_feedback.py`
- Modify: `.gpt-codex/tests/test_framework_project_separation.py`
- Modify: `.gpt-codex/tests/test_multi_project_github_isolation.py`

**Interfaces:**
- Produces `validate_framework_evolution_boundary(project_control, feedback) -> list[str]`.
- Ordinary project feedback is accepted only as evidence/candidate data.
- Global strategy/framework mutation remains management-project-only.

- [ ] **Step 1: Write failing centralized-evolution tests**

Add:

```python
def test_ordinary_project_feedback_cannot_claim_framework_mutation(self):
    feedback = {
        "problem": "review overhead",
        "reason": "review-everything",
        "local_solution": "risk milestones",
        "result": "PASS",
        "framework_change_recommended": True,
        "evidence_refs": ["result:1"],
        "framework_mutation": "APPLY_NOW",
    }
    self.assertEqual(
        validate_framework_feedback(feedback),
        ["FRAMEWORK_FEEDBACK_INVALID"],
    )


def test_only_framework_management_context_can_apply_global_evolution(self):
    ordinary = {
        "project_id": "PRJ-1",
        "governance_profile": "STANDARD",
        "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
    }
    self.assertEqual(
        validate_framework_evolution_boundary(ordinary, self.valid_feedback()),
        [],
    )
    self.assertFalse(
        framework_feedback_authorizes_mutation(ordinary, self.valid_feedback())
    )
```

The second assertion proves valid feedback is allowed but has no mutation authority.

- [ ] **Step 2: Implement explicit non-authority helpers**

Add:

```python
def validate_framework_evolution_boundary(
    project_control: Mapping[str, Any],
    feedback: Mapping[str, Any],
) -> list[str]:
    errors = validate_framework_feedback(feedback)
    if errors:
        return errors
    if project_control.get("framework_management_only") is True:
        return []
    roots = project_control.get("roots")
    if not isinstance(roots, Mapping):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    if roots.get("project_role") != "AUTHORITATIVE" or roots.get("framework_role") != "ADVISORY":
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    return []


def framework_feedback_authorizes_mutation(
    project_control: Mapping[str, Any],
    feedback: Mapping[str, Any],
) -> bool:
    return False
```

Do not add an automatic “apply feedback” path.

- [ ] **Step 3: Strengthen FEEDBACK template boundary**

Append:

```markdown
## Authority Boundary
This file is project evidence only.
It cannot modify Framework policy, strategy profiles, templates, releases, or another project.
Global evolution occurs only in the gpt-codex-framework management project after User approval.
```

- [ ] **Step 4: Add project separation / cross-project regressions**

Extend existing tests to prove:
- Project A feedback cannot mutate Project B.
- Project A feedback cannot change Framework version/profile.
- Framework management project may read/import feedback as evidence without making it authoritative.

- [ ] **Step 5: Run affected regressions**

Run:

```bash
python .gpt-codex/tests/test_framework_feedback.py
python .gpt-codex/tests/test_framework_project_separation.py
python .gpt-codex/tests/test_multi_project_github_isolation.py
python .gpt-codex/tests/test_context_binding.py
python .gpt-codex/scripts/validate_project.py .
```

- [ ] **Step 6: Commit**

```bash
git add \
  .gpt-codex/project-template/.harness/FEEDBACK.template.md \
  .gpt-codex/scripts/framework_feedback.py \
  .gpt-codex/scripts/validate_project.py \
  .gpt-codex/tests/test_framework_feedback.py \
  .gpt-codex/tests/test_framework_project_separation.py \
  .gpt-codex/tests/test_multi_project_github_isolation.py
git commit -m "feat: enforce centralized harness evolution"
```

---

### Task 7: Add directory-evolution and project-closure convergence rules without a manager subsystem

**Files:**
- Modify: `.gpt-codex/project-template/.harness/RULES.template.md`
- Modify: `.gpt-codex/project-template/.harness/REASONING.template.md`
- Modify: `.gpt-codex/project-template/.harness/STATE.template.md`
- Modify: `.gpt-codex/scripts/framework_feedback.py`
- Modify: `.gpt-codex/tests/test_framework_feedback.py`
- Create: `.gpt-codex/tests/test_harness_reduction_gate.py`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`

**Interfaces:**
- Produces pure `evaluate_structure_change(before_capabilities, after_capabilities, evidence) -> str`.
- Returns `ALLOW`, `NO_BENEFIT`, or `CAPABILITY_REGRESSION`.
- No filesystem auto-reorganizer is created.

- [ ] **Step 1: Write failing structure-review tests**

Create `.gpt-codex/tests/test_harness_reduction_gate.py`:

```python
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from framework_feedback import evaluate_structure_change  # noqa: E402


class HarnessReductionGateTests(unittest.TestCase):
    def test_structure_change_requires_capability_preservation_and_real_benefit(self):
        self.assertEqual(
            evaluate_structure_change(
                {"build", "test", "deploy"},
                {"build", "test", "deploy"},
                {"complexity_decreased": True},
            ),
            "ALLOW",
        )
        self.assertEqual(
            evaluate_structure_change(
                {"build", "test", "deploy"},
                {"build", "test"},
                {"complexity_decreased": True},
            ),
            "CAPABILITY_REGRESSION",
        )
        self.assertEqual(
            evaluate_structure_change(
                {"build", "test"},
                {"build", "test"},
                {},
            ),
            "NO_BENEFIT",
        )
```

The file ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Implement the pure structure gate**

Add:

```python
def evaluate_structure_change(
    before_capabilities: set[str],
    after_capabilities: set[str],
    evidence: Mapping[str, Any],
) -> str:
    if not before_capabilities.issubset(after_capabilities):
        return "CAPABILITY_REGRESSION"
    benefits = (
        evidence.get("complexity_decreased") is True,
        evidence.get("responsibility_clearer") is True,
        evidence.get("deployment_maintenance_testing_improved") is True,
    )
    return "ALLOW" if any(benefits) else "NO_BENEFIT"
```

- [ ] **Step 3: Add directory-evolution rules to RULES**

Append:

```markdown
## Structure Evolution
- Responsibility before structure.
- Do not split by file count, line count, agent count, or parallelism convenience.
- Split only for durable responsibility/runtime/security/testing boundaries.
- Merge/delete when layers always change together, are trivial wrappers, or duplicate ownership.
- AFTER_CAPABILITIES must contain every required BEFORE_CAPABILITY.
- Do not reorganize a stable structure for cosmetic reasons.
```

- [ ] **Step 4: Add bounded structure-review record to REASONING**

Append:

```markdown
## Structure Review Format
MOMENT:
CHANGE:
RESPONSIBILITY_REASON:
BEFORE_CAPABILITIES:
AFTER_CAPABILITIES:
MEASURABLE_BENEFIT:
RESULT:
```

- [ ] **Step 5: Add closure convergence to STATE**

Append:

```markdown
## Closure Rule
When PROJECT_STATUS becomes COMPLETE:
- CURRENT_TASK = NONE
- BLOCKER = NONE
- PENDING_RESULT_REF = NONE
- NEXT_ACTION = MAINTENANCE
Transient debugging/scratch state is removed or archived outside the active state view.
```

- [ ] **Step 6: Run focused tests**

Classify `.gpt-codex/tests/test_harness_reduction_gate.py` as `MANAGEMENT_ONLY` and run projection validation before commit.

```bash
python .gpt-codex/tests/test_harness_reduction_gate.py
python .gpt-codex/tests/test_framework_feedback.py
```

- [ ] **Step 7: Commit**

```bash
git add \
  .gpt-codex/project-template/.harness/RULES.template.md \
  .gpt-codex/project-template/.harness/REASONING.template.md \
  .gpt-codex/project-template/.harness/STATE.template.md \
  .gpt-codex/scripts/framework_feedback.py \
  .gpt-codex/tests/test_framework_feedback.py \
  .gpt-codex/tests/test_harness_reduction_gate.py \
  .gpt-codex/release/consumer-projection-manifest.json
git commit -m "feat: add harness structure evolution gate"
```

---

### Task 8: Run capability-preserving Framework reduction review — no deletion yet

**Files:**
- Create: `docs/superpowers/reviews/2026-09-15-minimal-harness-reduction-review.md`
- Modify: `.gpt-codex/release/consumer-projection-manifest.json`
- Test/verify existing P0 suites only.
- No source deletion in this task.

**Interfaces:**
- Produces one review table for these candidates:
  - complex Work Unit structure
  - execution slots
  - persistent Resume
  - Project Map
  - P0-6 telemetry runtime
  - large Instruction Envelope
  - large Result Envelope/return
  - repeated schemas/validators
  - Framework module boundaries
- Each candidate gets exactly one status: `KEEP`, `MERGE_CANDIDATE`, `DERIVE_ONLY_CANDIDATE`, `REMOVE_CANDIDATE`.
- A candidate may be `REMOVE_CANDIDATE` only when replacement tests prove all required P0 capabilities remain.

- [ ] **Step 1: Run the full suite before any reduction judgment**

Run established unittest discovery.

Required:
- Test count must be >= 443 because this upgrade adds tests.
- Failures = 0
- Errors = 0

If count is lower than 443, stop and reconcile test discovery.

- [ ] **Step 2: Run focused preservation suites**

Run:

```bash
python .gpt-codex/tests/test_framework_project_separation.py
python .gpt-codex/tests/test_multi_project_github_isolation.py
python .gpt-codex/tests/test_instruction_role_contract.py
python .gpt-codex/tests/test_review_lifecycle.py
python .gpt-codex/tests/test_continuity_resume.py
python .gpt-codex/tests/test_harness_handoff.py
python .gpt-codex/tests/test_consumer_projection.py
python .gpt-codex/tests/test_release_packaging.py
python .gpt-codex/tests/test_execution_telemetry.py
python .gpt-codex/tests/test_harness_reduction_gate.py
```

- [ ] **Step 3: Create the reduction review document**

Create `docs/superpowers/reviews/2026-09-15-minimal-harness-reduction-review.md` with this exact structure:

```markdown
# Minimal Harness Reduction Review

## Baseline
- Design: docs/superpowers/specs/2026-09-15-minimal-closed-loop-harness-upgrade-design.md
- P0 baseline: 224d8c0ebdfdc0aa7024f2c69f06fc6fcfe4c699
- Principle: Preserve capability, compress structure; preserve the closed loop, remove duplication.

## Required Preserved Capabilities
- Git SHA/ancestry authority
- Framework/Project separation
- Project isolation
- Role boundaries
- Review/remediation causality
- Cold recovery
- Production/consumer projection boundaries
- Fail-closed ambiguity handling

## Candidates
| Candidate | Current Responsibility | Replacement Evidence | Status | Separate Removal Work Required |
| --- | --- | --- | --- | --- |
| Work Unit | | | | YES |
| Execution slots | | | | YES |
| Resume persistence | | | | YES |
| Project Map | | | | YES |
| Telemetry runtime | | | | YES |
| Instruction Envelope | | | | YES |
| Result Envelope / return | | | | YES |
| Repeated schemas/validators | | | | YES |
| Module boundaries | | | | YES |

## Decision Rule
No item is deleted in this review.
Deletion or merge requires a separately authorized Work Unit after a candidate is accepted and all capability-preservation tests are named.
```

Fill every table cell from repository evidence; no unresolved placeholders or empty cells are allowed.

- [ ] **Step 4: Validate review-only scope**

Classify `docs/superpowers/reviews/2026-09-15-minimal-harness-reduction-review.md` as `DEVELOPMENT_HISTORY`, then run projection validation and require zero unknown paths before commit.

Run:

```bash
git diff --check
git status --short
```

The only new path in this task must be the reduction-review document.

- [ ] **Step 5: Commit review**

```bash
git add \
  docs/superpowers/reviews/2026-09-15-minimal-harness-reduction-review.md \
  .gpt-codex/release/consumer-projection-manifest.json
git commit -m "docs: review minimal harness reduction candidates"
```

Do not remove any P0 structure in this task.

---

### Task 9: Final integrated verification for the additive Harness upgrade

**Files:** Verify only. No mutation.

- [ ] **Step 1: Verify production isolation**

Prove:
- `.harness` templates are consumer bootstrap assets.
- `.harness` is excluded from product/runtime packaging.
- product runtime does not import `.harness`.

- [ ] **Step 2: Verify cold handoff**

Prove:
- fresh repository context can produce `HANDOFF_READY` from durable facts;
- one safe `next_action`;
- unique pending result discovery;
- immutable design/plan ref verification;
- missing/ambiguous facts fail closed;
- `.harness/REASONING.md` absence does not make authority unrecoverable.

- [ ] **Step 3: Verify strategy and feedback boundaries**

Prove:
- project strategy is stable data;
- no private chain-of-thought field;
- usage is `UNKNOWN` when unavailable;
- ordinary project feedback cannot mutate Framework;
- no cross-project feedback authority.

- [ ] **Step 4: Verify compact task and result views**

Prove:
- compact Codex task has `GOAL/SCOPE/CONSTRAINTS/DONE`;
- canonical Instruction authority remains required;
- compact Result return requires durable `RESULT_REF`;
- existing full envelope/return remains valid during transition.

- [ ] **Step 5: Verify no forbidden subsystem appeared**

Search changed code for and inspect any matches to:
- scheduler
- governor
- agent scoring
- auto strategy update
- framework mutation from feedback
- background service
- message bus
- telemetry persistence

A textual mention in docs/tests is allowed; executable behavior is not.

- [ ] **Step 6: Run all validators**

```bash
python .gpt-codex/scripts/validate_consumer_projection.py --root .
python .gpt-codex/scripts/validate_framework.py
python .gpt-codex/scripts/validate_project.py .
```

Required:
- all PASS
- projection unknown = 0
- missing required = 0
- invalid classification = 0

- [ ] **Step 7: Run full suite**

Run established unittest discovery.

Required:
- count >= 443
- failures = 0
- errors = 0

- [ ] **Step 8: No-mutation closure check**

```bash
git diff --check
git status --porcelain
```

Required clean after the final implementation commit(s).

No VERSION bump, release, publication, or main merge in this task.

---

## Whole-Plan New-Path Audit

Every planned new repository path has an explicit same-task projection classification:

| Task | New path | Classification |
| --- | --- | --- |
| 1 | `.gpt-codex/project-template/.harness/RULES.template.md` | `CONSUMER_REQUIRED` |
| 1 | `.gpt-codex/project-template/.harness/STATE.template.md` | `CONSUMER_REQUIRED` |
| 1 | `.gpt-codex/project-template/.harness/REASONING.template.md` | `CONSUMER_REQUIRED` |
| 1 | `.gpt-codex/project-template/.harness/FEEDBACK.template.md` | `CONSUMER_REQUIRED` |
| 1 | `.gpt-codex/tests/test_harness_project_layering.py` | `MANAGEMENT_ONLY` |
| 2 | `.gpt-codex/tests/test_harness_handoff.py` | `MANAGEMENT_ONLY` |
| 3 | `.gpt-codex/scripts/framework_feedback.py` | `CONSUMER_REQUIRED` |
| 3 | `.gpt-codex/tests/test_framework_feedback.py` | `MANAGEMENT_ONLY` |
| 4 | `.gpt-codex/tests/test_minimal_task_protocol.py` | `MANAGEMENT_ONLY` |
| 7 | `.gpt-codex/tests/test_harness_reduction_gate.py` | `MANAGEMENT_ONLY` |
| 8 | `docs/superpowers/reviews/2026-09-15-minimal-harness-reduction-review.md` | `DEVELOPMENT_HISTORY` |

`PLANNED_NEW_PATHS_WITHOUT_CLASSIFICATION = 0`. If a task creates a new path, it adds the listed manifest classification in the same task before commit and validates projection closure.

## Implementation Branch / Review Discipline

1. Persist this Plan on the Design branch first.
2. Create the implementation branch from the exact Plan commit:
   `feature/minimal-closed-loop-harness-upgrade-implementation`.
3. Execute Tasks 1–7 sequentially unless GPT explicitly authorizes independent parallel execution after checking file overlap.
4. After each task:
   - focused tests;
   - affected P0 regressions;
   - framework/project/projection validators;
   - one focused commit;
   - independent review when the task changes authority, recovery, production boundary, or cross-project behavior.
5. Task 8 is review-only and MUST NOT delete old P0 structures.
6. Any actual P0 structure removal after Task 8 requires a new, separately approved reduction Work Unit.
7. Task 9 is final verify-only.
8. Only after Task 9 passes may GPT propose release/version/publication work.

## Expected Completion State

At the end of this Plan:

- ordinary projects have a minimal `.harness` surface with RULES/STATE/REASONING/FEEDBACK templates;
- semantic Harness/Product/Deploy roots are explicit and production isolation is testable;
- Handoff can reconstruct current work, Git, strategy, immutable artifacts, pending Result, blocker, and one next action from durable repository facts;
- project strategy is fixed and observable, not hidden reasoning;
- process-review/feedback data is bounded and non-authoritative;
- ordinary projects cannot evolve the global Framework;
- Codex tasks can be rendered as `GOAL/SCOPE/CONSTRAINTS/DONE` without discarding canonical authority during transition;
- GPT returns can be durable-ref-first and compact;
- directory evolution has a capability-preservation gate;
- P0 structures are classified for reduction, but none are removed without a separately approved proof-backed change;
- existing P0 functionality remains passing.
