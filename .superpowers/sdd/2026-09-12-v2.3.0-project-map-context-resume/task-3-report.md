# Task 3 Report: Module Freshness and Bounded Impact Calculation

## Status

Implemented the Task 3 project-navigation helpers and their focused unit tests.

## Files

- `.gpt-codex/scripts/project_navigation.py`
- `.gpt-codex/tests/test_project_navigation.py`
- `.superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-3-report.md`

## TDD Evidence

### RED

Added tests for configured-path matching, affected-module calculation, requested
module-map paths, and all four map-route outcomes. The required command
`python -m unittest .gpt-codex/tests/test_project_navigation.py -v` failed on
Windows with `ValueError: Empty module name`, so the brief's fallback command
was used:

```text
python .gpt-codex/tests/test_project_navigation.py -v
```

Before implementation, that command ran 13 tests and produced four expected
`AttributeError` failures because `path_belongs_to_module`, `affected_modules`,
`module_map_read_paths`, and `classify_map_route` did not yet exist.

### GREEN

Implemented the four focused helpers using `PurePosixPath` normalization. The
fallback focused-test command then passed all 13 tests:

```text
Ran 13 tests in 0.030s
OK
```

## Self-Review

- `affected_modules` considers only dictionary modules, returns only string IDs,
  and sorts/deduplicates results.
- Path matching is bounded to configured module path prefixes and avoids partial
  prefix collisions such as `src/auth` matching `src/author`.
- Route classification gives missing maps priority, then misses, stale overlap,
  and hits.
- No filesystem discovery, NLP, embeddings, or canonical-state mutations were
  introduced. Existing Kernel 2.0.0 and Schema generation 1 validation remains
  unchanged.
- `git diff --check` reported no whitespace errors (only existing Windows line-ending warnings).

## Commit

Committed only the Task 3 files with:

```text
feat: calculate incremental navigation impact
```

## Concerns

The dotted hidden-directory `unittest` invocation is unsupported by this Windows
environment and continues to require the fallback script-path invocation.

---

# Review-Findings Fix Report

## Status

Fixed the reviewed path-normalization defect and added the requested route
precedence coverage without expanding navigation scope.

## Root Cause

`_normalise_relative()` used `lstrip("./")`. Unlike removal of a single leading
`./` path component, `lstrip` removes every leading `.` or `/` character. It
therefore converted `/src/auth/session.ts` and `../src/auth/session.ts` to a
relative `src/auth/session.ts`, allowing false module ownership. It also passed
Windows backslashes unchanged to `PurePosixPath`, so `src\\auth\\session.ts`
did not match a POSIX module prefix.

## TDD Evidence

### RED

Added real-behavior tests that exercise `path_belongs_to_module()` with `./`,
duplicate separators, Windows backslashes, absolute paths, and traversal paths.
Also added independent route-precedence tests for a missing map with candidate
and stale IDs, and for stale IDs with no candidates.

Command:

```text
python .gpt-codex/tests/test_project_navigation.py -v
```

Output before the fix:

```text
Ran 17 tests in 0.038s
FAILED (failures=3)
```

The expected failing cases were the backslash path incorrectly returning
`False`, and `/src/auth/session.ts` plus `../src/auth/session.ts` incorrectly
returning `True`. The new route-precedence cases passed, confirming their
existing implementation before being locked down by tests.

### GREEN

Replaced implicit character stripping with deliberate separator normalization,
then reject absolute and `..`-containing candidate or configured-prefix paths
before comparing bounded module prefixes.

Command:

```text
python .gpt-codex/tests/test_project_navigation.py -v
```

Output after the fix:

```text
Ran 17 tests in 0.031s
OK
```

## Files Changed

- `.gpt-codex/scripts/project_navigation.py`
- `.gpt-codex/tests/test_project_navigation.py`
- `.superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-3-report.md`

## Self-Review

- Safe relative paths normalize `\\` to `/`; `PurePosixPath` handles `./` and
  duplicate `/` separators without collapsing absolute or traversal input.
- Absolute and traversal candidates and module prefixes return no match, so they
  cannot be treated as project-relative ownership paths.
- Route values and priority remain `MAP_MISSING`, `MAP_MISS`, `MAP_PARTIAL`,
  then `MAP_HIT`.
- No repository discovery, canonical-state mutation, authority change, Kernel
  version change, or schema-generation change was introduced.

## Concerns

The Windows dotted hidden-directory unittest form remains unavailable; all
focused test evidence uses the documented script-path fallback command.
