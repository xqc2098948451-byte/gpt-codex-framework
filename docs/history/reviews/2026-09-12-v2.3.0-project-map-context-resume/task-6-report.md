# Task 6 Report: Optional Navigation and Resume Validation

## Status

Implemented and verified. The validator now checks optional derived
navigation and Resume assets when they are present, while projects with neither
asset remain valid.

## Files

- Modified `.gpt-codex/scripts/validate_project.py`
- Created `.gpt-codex/tests/test_navigation_project_validation.py`
- Created this report

## RED evidence

Created the Task 6 test suite before modifying production code.

`python -m unittest .gpt-codex/tests/test_navigation_project_validation.py -v`
was attempted first and was blocked by Windows dotted hidden-path handling with
`ValueError: Empty module name`.

The required direct-file fallback was then run:

`python .gpt-codex/tests/test_navigation_project_validation.py -v`

Initial result: 7 tests run; the no-asset compatibility test passed and six
invalid-derived-asset tests failed because `validate_project.py` did not yet
inspect navigation or Resume files. The failed cases were foreign Project Map,
foreign module map, duplicate module ID, mismatched module-map ID, non-JSON
module-map path, and authoritative Resume.

After the first GREEN cycle, a further shape regression test for a malformed
Project Map module ID was added before its implementation. It failed as
expected: the validator exited without reporting a validation error because the
navigation loader raised `TypeError`.

## GREEN evidence

The implementation imports and uses `load_project_map`, `load_module_map`,
`validate_navigation_identity`, and `load_resume_checkpoint`.

- Project Map validation is conditional on the map existing.
- The established Project Map loader rejects duplicate module IDs.
- Each module-map reference is required to be a project-relative `.json` path.
- Existing referenced module maps are loaded, identity-bound to CONTROL, and
  required to declare the Project Map entry's module ID.
- Resume validation is conditional on the checkpoint existing; the checkpoint
  loader enforces `DERIVED_CACHE`, and identity is bound to CONTROL.
- Validation only reads derived assets. It neither discovers unreferenced assets
  nor copies checkpoint revision/state into canonical STATE.

Focused Task 6 test result after the final GREEN cycle:

`python .gpt-codex/tests/test_navigation_project_validation.py -v`

Result: 8 tests run, all passed.

Required regression command was also attempted:

`python -m unittest .gpt-codex/tests/test_navigation_project_validation.py .gpt-codex/tests/test_context_binding.py .gpt-codex/tests/test_validator_context_binding.py .gpt-codex/tests/test_project_context_migration.py -v`

It produced the same Windows `ValueError: Empty module name`, so each required
file was run directly instead:

- `test_navigation_project_validation.py`: 8 passed
- `test_context_binding.py`: 8 passed
- `test_validator_context_binding.py`: 3 passed
- `test_project_context_migration.py`: 5 passed

Total direct-file regression result: 24 passed.

Additional verification:

`python .gpt-codex/scripts/validate_project.py .` passed for the framework
project (`PRJ-FRAMEWORK-MANAGEMENT`, `COMPLETE@revision-3`).

`git diff --check` exited 0.

## Self-review

- Optional-asset compatibility is preserved: absent Project Map and absent
  Resume return no validation errors.
- CONTROL remains the identity authority and STATE remains the canonical state
  authority; the authoritative-Resume test confirms STATE bytes do not change.
- The validator reads only the canonical Project Map, its explicitly referenced
  existing module maps, and the single existing Resume path. It does not scan
  navigation directories or introduce a second Resume mechanism.
- Existing `continuity_resume` behavior, including `MAP_MISSING` and
  `COLD_RESUME`, is not changed.
- No Kernel or schema constants were changed: Kernel remains `2.0.0` and schema
  generation remains `1`.

## Fix round 1

Hooke identified that the first implementation checked only derived authority,
version, and identity. Three new tests were added before the fix, each using an
identity-valid, schema-version-1, derived-authority asset with required fields
removed:

- incomplete Project Map (missing `architecture_summary`)
- incomplete referenced module map (missing `responsibility`)
- incomplete Resume checkpoint (missing the required resume payload)

RED evidence: the focused suite ran 11 tests and failed exactly these three
new tests because the validator returned success for each incomplete asset.
The failures were the intended behavior gap, not test collection or fixture
errors.

The smallest implementation adds a local validator for the JSON Schema features
used by the existing Project Map, module-map, and Resume schemas: required
fields, closed object shapes, constants/enums, string minimums, types, and
array item shapes. It loads those existing schema files and is invoked only
after the existing loaders accept a present asset. No loader, schema file,
Kernel constant, STATE authority, discovery behavior, or Resume flow was
changed.

GREEN evidence:

- Task 6 focused suite: 11 passed
- Project navigation loader suite: 17 passed
- Continuity/resume suite: 21 passed
- Navigation schema suite: 3 passed
- Context binding suite: 8 passed
- Validator context-binding suite: 3 passed
- Project context migration suite: 5 passed
- Total relevant direct-file regression tests: 68 passed
- `python .gpt-codex/scripts/validate_project.py .`: passed with
  `COMPLETE@revision-3`
- `git diff --check`: exited 0

The report and the two Task 6 code files are the only files in the fix-round
commit. The controller will update the ledger separately.

## Commit

Fix-round commit message:

`fix: validate derived navigation and resume asset shapes`

## Concerns

The documented `python -m unittest` commands cannot import a hidden dotted
`.gpt-codex` path on this Windows/Python 3.13 environment (`ValueError: Empty
module name`). Direct-file fallback commands passed and are recorded above.
