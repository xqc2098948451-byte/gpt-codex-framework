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
