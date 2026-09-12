# Task 4 Report: Derived Resume Checkpoint Fingerprints

## Scope

Extended the existing `.gpt-codex/scripts/continuity_resume.py` resume system without changing canonical resume reconciliation behavior. The implementation adds derived checkpoint loading, deterministic file fingerprints, and declared-source-only context comparison.

## TDD evidence

### RED

Added focused tests for:

- absent `continuity/RESUME.json` returning `None`;
- a changed declared context source invalidating only that source; and
- an unchanged `.gpt-codex/navigation/PROJECT_MAP.json` remaining outside `invalidated_context`.

`python -m unittest .gpt-codex/tests/test_continuity_resume.py -v` failed on Windows before discovery with `ValueError: Empty module name`, as anticipated by the brief.

The required direct-file fallback, `python .gpt-codex/tests/test_continuity_resume.py -v`, then ran the suite and failed with three expected import errors for the absent `load_resume_checkpoint`, `fingerprint_file`, and `compare_context_sources` interfaces. The four pre-existing canonical-resume tests passed.

### GREEN

Implemented only the requested helpers and constant:

- `RESUME_RELATIVE_PATH = Path("continuity") / "RESUME.json"`;
- `load_resume_checkpoint(gov)` with the specified absent, invalid, schema, and derived-authority behavior;
- deterministic `fingerprint_file(path)` SHA-256 fingerprints; and
- `compare_context_sources(root, checkpoint)` that reads only explicitly declared sources, invalidates changed sources, and reports missing declared sources as required reads.

After the implementation, `python .gpt-codex/tests/test_continuity_resume.py -v` passed all 7 tests.

## Files

- `.gpt-codex/scripts/continuity_resume.py`
- `.gpt-codex/tests/test_continuity_resume.py`
- `.superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-4-report.md`

## Self-review

- Kept `load_continuity_resume` and its canonical reconciliation precedence unchanged.
- Did not add repository discovery, canonical-state mutation, a second resume system, or kernel/schema-generation changes.
- Context comparison examines only `checkpoint["context_sources"]` entries and retains their declared paths in results.
- Fingerprinting uses exactly file bytes with a `sha256:` prefix and returns `None` for non-files.

## Commit

Committed with `feat: add derived resume checkpoint fingerprints`.

## Concerns

The documented dotted hidden-directory unittest command is unsupported by this Windows/Python invocation and raises `ValueError: Empty module name`; the brief-provided direct-file fallback was used for RED and GREEN verification.

## Status

Complete. Focused verification passed and the Task 4 files were committed.

## Review-fix addendum

### Findings addressed

- Updated `compare_context_sources` from the erroneous mapping-only interpretation to the approved Resume v1 array contract. Each operational entry is a declared `{"path": ..., "fingerprint": ...}` source, so changed and missing entries are now processed rather than silently ignored.
- Changed checkpoint absence detection to use `exists()`. Only an absent path returns `None`; an existing directory or unreadable/non-JSON path is read and produces `RESUME_CHECKPOINT_INVALID`.
- Enforced project-relative, root-contained context-source paths. Absolute paths, `..` traversal, and resolved paths escaping the root raise `RESUME_CONTEXT_SOURCE_PATH_INVALID:<path>` before any fingerprint operation.
- Added real-behavior coverage for Resume checkpoint error codes, raw-byte SHA-256 formatting, missing-source required reads, array-shaped context sources, safe-path rejection, and retained `working_set.hot_modules`.

### Root cause and contract evidence

The Resume v1 schema declares `context_sources` as an array and requires `working_set.hot_modules`; the template initializes both as arrays. The earlier runtime expected a dictionary, therefore schema-valid array checkpoints returned `([], [])`. The navigation runtime’s existing safe-path pattern validates non-absolute/no-parent paths, resolves from the root, and confirms containment with `relative_to`.

### Review-fix RED

Command:

```text
python .gpt-codex/tests/test_continuity_resume.py -v
```

Output summary before the runtime fix:

```text
Ran 12 tests in 0.040s
FAILED (failures=5)
```

The failing behaviors were exactly the review findings: array-form changed sources did not invalidate, an array-form missing source was not queued, parent and absolute paths were accepted, and an existing `RESUME.json` directory returned `None`. The raw-byte fingerprint and retained hot-module tests passed because those behaviors were already present. The test harness’s initial absolute-path regex escaping error was corrected before the recorded RED run; it was not a runtime defect.

### Review-fix GREEN

Command:

```text
python .gpt-codex/tests/test_continuity_resume.py -v
```

Output:

```text
Ran 12 tests in 0.067s
OK
```

Covered passing tests include array-form changed-source invalidation, unchanged project map validity, missing-source reads, absolute and traversal rejection, exact raw-byte fingerprint output, non-file/invalid/schema/authority checkpoint error codes, and `working_set.hot_modules` retention. The four canonical resume/reconciliation tests also remain green.

### Review-fix self-review and status

- `load_continuity_resume` remains byte-for-byte behaviorally unchanged; canonical reconciliation precedence is preserved.
- The derived checkpoint remains authority-gated as `DERIVED_CACHE`; no canonical state is written or discovered.
- Kernel `2.0.0` and Schema generation `1` remain unchanged.
- The only outstanding environment note is the prior documented Windows hidden-directory unittest invocation limitation; direct-file focused execution is used.

Review-fix implementation passed final scoped verification and was committed with `fix: validate resume checkpoint context sources`.
