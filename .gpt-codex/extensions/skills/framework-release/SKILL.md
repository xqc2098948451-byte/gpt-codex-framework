# Skill — framework-release

This is a **project-local Skill for the GPT–Codex Framework management project**. It is not a general Built-in for ordinary projects and does not modify the v2.0 Kernel Contract.

## Purpose

Create a clean, validated framework release without manual file copying, while retaining only lightweight historical release metadata inside the management project.

## Single version source

`VERSION` at repository root is the single framework release-version source. Kernel compatibility remains independently identified by `.gpt-codex/scripts/kernel_rules.py::KERNEL_VERSION`.

## Release archive policy

- `releases/` stores metadata only: `INDEX.json` plus `records/v<version>.json`.
- Historical ZIP binaries remain external and must not be recursively embedded in later framework packages.
- A historical ZIP can be recorded with:

```bash
python .gpt-codex/scripts/release_archive.py /path/to/gpt-codex-framework-vX.Y-bootstrap.zip --releases-dir releases
```

The import verifies ZIP integrity, records SHA-256 and size, and copies no ZIP into `releases/`.
- The current release record is embedded before packaging. Its final ZIP hash is kept in the external `.zip.sha256` and `release.json` sidecars because a ZIP cannot reliably contain its own final hash.

## Release contract

Run:

```bash
python .gpt-codex/scripts/release_framework.py
```

The Skill must, in this order:

1. read and validate `VERSION` as SemVer;
2. maintain the current lightweight release record and index;
3. verify `VERSION` matches the framework catalog release version;
4. verify the current release exists in `CHANGELOG.md`;
5. validate the framework, Built-ins, Kernel contracts, and release-metadata policy;
6. run Kernel/release tests;
7. remove older generated release artifacts from `dist/`;
8. package a deterministic ZIP under `dist/`;
9. exclude VCS state, caches, editor files, prior release archives, and `dist/` itself;
10. reopen and integrity-check the ZIP;
11. compute SHA-256;
12. write the external release manifest.

A validation failure blocks publication. The script must not report a successful release by bypassing failing checks.

## Publication preflight and immutable artifact handoff

Before every publication write, evaluate observed preflight facts and prove all three capabilities: `TAG_WRITE`, `RELEASE_WRITE`, and `ASSET_UPLOAD`. The preflight is a blocker check; it does not create a tag, Release, or upload.

The accepted canonical asset is immutable `<W_SHA>:dist/gpt-codex-framework-vX.Y.Z-bootstrap.zip`. If it is absent locally, materialize that exact Git object, verify its SHA-256 and byte size, then use the verified temporary copy. Never regenerate an accepted artifact for publication, and never treat a same-named local ZIP as authority unless its hash and size match the canonical W authority.

Derive release-specific facts from current Git and remote observations. Existing Result/structure may be reused, but prior release-specific factual values must not be copied forward. Temporary materialization is disposable and does not create a second release system.

## Outputs

For `VERSION=2.0.2`:

```text
dist/
├── gpt-codex-framework-v2.0.2-bootstrap.zip
├── gpt-codex-framework-v2.0.2-bootstrap.zip.sha256
└── gpt-codex-framework-v2.0.2-release.json
```

The ZIP contains a single versioned top-level directory and is self-contained. It includes the lightweight `releases/` metadata directory, but no historical release ZIPs.

## Release guardrails

- Kernel version is not changed merely because framework release version changes.
- `VERSION` is not inferred from filenames or prose.
- Failed validator/tests block release.
- Cached/generated local debris must not enter the archive.
- Existing release ZIPs must not be recursively embedded into new archives.
- The release Skill may write only release metadata under `releases/` and generated outputs under `dist/`; other source changes happen before release execution.
- Historical source history remains in Git/docs even if local old ZIP files are deleted.
