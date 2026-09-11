# Release Archive Metadata

This directory is the lightweight release-history index for the framework management project.

## Policy

- Source history lives in Git/docs.
- Release ZIP binaries are **not** embedded in the framework repository or in later framework ZIPs.
- `INDEX.json` and `records/` keep lightweight release metadata.
- Historical ZIPs may be imported with `.gpt-codex/scripts/release_archive.py`; import records filename, size and SHA-256, then discards no source file and copies no ZIP into this directory.
- The current release record is embedded before packaging. Its ZIP SHA-256 lives in the external `.zip.sha256` and `release.json` sidecars because embedding a ZIP's own final hash inside itself would be self-referential.
- Deleting a historical release ZIP from local working storage does not delete its Git/source history or its metadata record here.

## Current release workflow

`python .gpt-codex/scripts/release_framework.py`

The release Skill validates the source, maintains the current metadata record, clears old generated artifacts from `dist/`, and emits only the current ZIP, SHA-256 sidecar, and release manifest.
