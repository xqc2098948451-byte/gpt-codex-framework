# Extension Harvesting

Harvest converts real project experience into evidence for future Built-ins.

## Ordinary project permissions

- Kernel: read-only.
- Built-ins: read-only.
- `inbox/<current-project-id>/`: current project may create/update its normalized candidate exports.
- other project namespaces: read-only or unavailable.
- `shared-candidates/` and Built-in promotion: framework-maintenance only.

## Source-of-truth rule

Source projects remain authoritative. If a candidate reveals a bug in a project extension, fix the source project first, then re-export. Never repair the source by editing Harvest.

## Maintenance flow

```text
PROJECT_LOCAL
→ normalized HARVEST_CANDIDATE
→ cross-project semantic comparison
→ optional SHARED_CANDIDATE
→ promotion review
→ BUILTIN or reject/delete candidate
```

Deleting a candidate never deletes the source-project extension.

## Comparison dimensions

Compare semantics rather than filenames:

- kind;
- intent;
- trigger;
- invariant or produced outcome;
- inputs/outputs;
- permissions;
- failure semantics;
- technology context;
- parameterizable vs project-specific details.

Prefer repeated independent project evidence. A reference count such as three independent projects may be useful during maintenance, but it is not a Kernel hard rule.
