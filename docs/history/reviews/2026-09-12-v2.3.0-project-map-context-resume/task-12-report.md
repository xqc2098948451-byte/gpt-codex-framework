# Task 12 Release Report — Framework v2.3.0

## Scope and outcome

Task 12 was completed on branch `feature/v2.3-project-map-context-resume`.
Framework version is `2.3.0`; Kernel version remains `2.0.0`; schema generation
remains `1`; Repository Discovery remains `1.1.0`; Handoff remains `1.2.0`.

The release artifact was generated through the repository-supported command:

```text
python .gpt-codex/scripts/release_framework.py
```

## TDD RED/GREEN evidence

### Version-consistency and version-bearing documentation

RED, after changing the version-consistency test expectations to v2.3.0 but
before synchronizing release metadata and version-bearing documentation:

```text
python .gpt-codex/tests/test_version_consistency.py -v
Ran 3 tests
FAILED (failures=2)
```

The failures were the v2.3.0 changelog/README/BOOTSTRAP/AGENTS assertions and
the current release metadata assertion; the artifact SHA test was still green.

GREEN, after synchronizing `VERSION`, the v2.3.0 changelog entry, catalog,
release metadata, README, bootstrap prompt, and AGENTS heading:

```text
python .gpt-codex/tests/test_version_consistency.py -v
Ran 3 tests in 0.005s
OK
```

The seven required changelog bullets are present under `## v2.3.0`.

### SemVer/prerelease ordering

RED, before the tooling correction:

```text
python -m unittest discover -s .gpt-codex/tests -p "test_release_packaging.py" -v
Ran 12 tests
FAILED (failures=2, errors=2)
```

The focused prerelease test raised `ValueError: invalid literal for int() with
base 10: '2-local'` while sorting `2.2.2-local.1`.

GREEN, after using the repository's robust SemVer/prerelease key:

```text
python -m unittest discover -s .gpt-codex/tests -p "test_release_packaging.py" -v
Ran 12 tests in 5.951s
OK

python -m unittest discover -s .gpt-codex/tests -p "test_release_archive.py" -v
Ran 5 tests in 0.065s
OK
```

### Artifact-before-dependent-test sequencing

RED, after v2.3.0 metadata was selected but before release generation:

```text
python .gpt-codex/tests/test_version_consistency.py -v
Ran 3 tests
FAILED (errors=2)
```

The two errors were `FileNotFoundError` for
`releases/records/v2.3.0.json` and
`dist/gpt-codex-framework-v2.3.0-bootstrap.zip`, which are produced by the
release command itself.

GREEN, after the command was corrected to create the provisional artifact and
hash-backed record before running artifact-dependent tests, while still
aborting on test failure and finalizing the release manifest only after the
test gate:

```text
python .gpt-codex/scripts/release_framework.py
RESULT: PASS
Ran 200 tests in 14.412s
OK
```

The generated release manifest records `framework`, `tests`, `release_hygiene`,
and `zip_integrity` as `PASS`.

### Release-path classification

RED: adding this report before classifying it in the consumer projection
manifest made the exact validator command fail:

```text
python .gpt-codex/scripts/validate_consumer_projection.py --root . --zip dist/gpt-codex-framework-v2.3.0-bootstrap.zip
RESULT: FAIL
REASON: {"invalid_classifications": [], "missing_required_paths": [], "unknown_paths": [".superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-12-report.md"]}
```

This demonstrated that the new development-history path required an explicit
manifest classification.

GREEN: after adding the exact report path as `DEVELOPMENT_HISTORY`, alongside
the exact v2.3.0 record and generated-artifact paths, the required validator
reports:

```text
python .gpt-codex/scripts/validate_consumer_projection.py --root . --zip dist/gpt-codex-framework-v2.3.0-bootstrap.zip
CONSUMER_PROJECTION_RELEASE_MATCH: PASS
CONSUMER_REQUIRED_COUNT: 80
UNKNOWN_PATH_COUNT: 0
MISSING_REQUIRED_PATH_COUNT: 0
MANAGEMENT_IDS_IN_CONSUMER_PROJECTION: NONE
```

## Explicit rulings

1. The Task 12 plan omitted the required version-bearing documentation and
   version-consistency test updates. They were necessary to make the explicit
   v2.3.0 release assertions consistent and were authorized as a ruling.
2. The Task 12 release tooling required two necessary corrections: robust
   SemVer/prerelease sorting for existing records, and artifact generation plus
   hash-backed record creation before artifact-dependent tests. Existing safety
   and validation gates remain active; failures still abort.
3. The Task 12 consumer projection manifest omitted four exact v2.3.0 release
   paths. The release record is `RELEASE_METADATA`; the ZIP, SHA256 sidecar, and
   release JSON are `GENERATED_ARTIFACT`; none is `CONSUMER_REQUIRED` and no
   globs are used.

## Validation record

Pre-release validation passed with 199 tests and framework, project, and
consumer validators. Post-release validation passed with 200 tests,
framework/project validators, and the exact ZIP validator. The v2.3.0 ZIP
SHA-256 is:

```text
6a0647ba401c89e9b46a4d74d24e9e4c168b24fbf6ebdda35d392f3bf1c21e43
```

The literal plan command
`python -m unittest .gpt-codex/tests/test_version_consistency.py -v` remains a
Windows/Python invocation minor: it raises `ValueError: Empty module name`.
The direct-file equivalent above passes all three tests.

No publish, push, merge, or `progress.md` edit was performed.
