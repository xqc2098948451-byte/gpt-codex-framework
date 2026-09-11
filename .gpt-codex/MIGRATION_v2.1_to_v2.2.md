# v2.1 to v2.2 GitHub Continuity Migration

Migration is an explicit, authorized Work Unit. It binds one project context
to exactly one GitHub repository through the three durable fields in
`CONTROL.github`: `repository_id`, `repository_full_name`, and `default_branch`.
`remote_name` is local runtime observation or a non-authoritative instruction
hint and is never project-global configuration.

The read-only compatibility scan returns one of:

- `ALREADY_BOUND`
- `GITHUB_BINDING_REQUIRED`
- `LOCAL_GIT_ONLY`
- `REMOTE_UNBOUND`
- `MULTIPLE_REMOTE_REVIEW_REQUIRED`
- `NON_GITHUB_REMOTE`
- `REPOSITORY_CONFLICT`

The owner/GPT selects the exact repository ID. Rename and transfer preserve the
stable ID and update the diagnostic full name explicitly. Multiple remotes are
reviewed; no remote is selected implicitly. Migration never creates a GitHub
repository, replaces or deletes a remote, rewrites history, force-pushes, or
silently chooses an ambiguous repository.

The one-project/one-repository invariant and the existing
`PROJECT_CONTEXT_ID` guardrail both remain required. Framework Management is
not migrated as part of the v2.2 release; it is a later independent migration
Work Unit after the release is accepted as a clean baseline.
