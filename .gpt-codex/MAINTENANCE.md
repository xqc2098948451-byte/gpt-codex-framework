# Framework Maintenance — Recommended Semiannual Review

The expected cadence is roughly twice per year unless a critical Kernel defect requires an earlier release. Do not publish a new framework version merely because a new idea appears.

## 1. Harvest review

- inventory Harvest Candidates from independent projects;
- cluster by semantic identity rather than filename;
- compare intent, trigger, invariant/outcome, permissions, failure semantics, and technology context;
- promote only stable repeated contracts;
- keep project-specific cases local;
- delete rejected Harvest copies without touching source projects.

## 2. Built-in review

- identify Built-ins rarely enabled;
- identify Built-ins frequently overridden/forked;
- merge redundant Built-ins;
- deprecate/retire obsolete Built-ins;
- prefer improving parameters/contracts over multiplying capabilities.

## 3. Kernel review

A new Kernel concept is admitted only if all are effectively YES:

1. essentially every governed project needs it;
2. governance correctness depends on it;
3. it cannot reasonably be expressed as Skill, Guardrail, or Fitness.

Otherwise keep it outside Kernel.

## 4. Conformance and migration

Run the full Kernel conformance suite and distribution validator. For incompatible changes, write an explicit migration contract. Never silently reinterpret existing project governance.

## 5. Release and project adoption

Publish framework changes. Projects do not receive automatic updates. Each maintained project runs a read-only compatibility scan when convenient, then explicitly decides whether to adopt relevant changes.

**Framework publishes; Project decides.**

## 6. Release archive hygiene

`releases/` is metadata-only. Keep source/history in Git/docs and keep distributable ZIP binaries outside the source tree. Import retained historical ZIP metadata with `release_archive.py` when useful, then allow local archive binaries to be removed according to your storage policy. `dist/` is a transient current-release output directory and is cleaned by the release Skill before generating a new release.

## 7. Evidence-gated worktree cleanup

Treat the `KEEP`/`CLEAN` decision as separate from any worktree operation. `CLEAN` is evidence-gated authorization, never automatic deletion; existing `KEEP` decisions are not automatically reinterpreted. Perform any actual operation with native Git only, first checking the current repository and worktree state. Do not force removal. The permitted commands are `git worktree list`, `git status`, `git worktree remove`, and `git worktree prune`.
