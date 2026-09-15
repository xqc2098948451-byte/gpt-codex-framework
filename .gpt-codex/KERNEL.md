# GPT–Codex Kernel v2.0

**Kernel Version:** 2.0.0  
**Schema Generation:** 1

The Kernel is deliberately small. If a project can safely exist without a capability, that capability probably does not belong in Kernel.

## 1. Project Adaptation Contract

A project must be governed from observed repository evidence and explicit user intent, not by mechanically copying defaults.

Adaptation sequence:

```text
DISCOVER → UNDERSTAND → REUSE → CONFIGURE → COMPILE → VALIDATE → AUTHORIZE
```

Project governance must be evidence-derived, not template-invented.

## 2. Minimal Work Unit Model

Kernel knows `WORK_UNIT`, not feature/task/bug/release-specific semantics. A Work Unit provides goal, scope, acceptance, selected extensions, permissions, and evidence bindings. Skills may introduce richer project-local work structures without changing Kernel.

## 3. Minimal State Machine + Revision

Core states:

- `PROPOSED`
- `AUTHORIZED`
- `ACTIVE`
- `VERIFYING`
- `COMPLETE`
- `BLOCKED`
- `AWAITING_APPROVAL`
- `RECONCILIATION_REQUIRED`

State writes use optimistic revision control. If a writer read revision `N`, it may update only when the authoritative state still has revision `N`; success writes `N+1`. A stale writer must return `RECONCILIATION_REQUIRED`, never overwrite newer state.

## 4. Authority / Least Privilege

Authority narrows down the execution chain:

```text
Kernel bounds
  ⊇ Project authorization
    ⊇ Extension authorization
      ⊇ Work Unit authorization
        ⊇ Execution authorization
```

A child scope may become more restrictive but cannot silently expand its parent. Dangerous or irreversible operations require an applicable authorization path and explicit user approval when the active Guardrail requires it.

## 5. Evidence Model

Every important state transition must be supported by evidence. Evidence must identify its source and bind to the relevant state revision and implementation/artifact identity where applicable.

Minimum source classes:

- `TOOL_OBSERVED`
- `USER_ASSERTED`
- `SYSTEM_DERIVED`
- `MODEL_INFERRED`

`MODEL_INFERRED` may guide investigation, but cannot alone authorize `COMPLETE`, privilege expansion, destructive action, production action, or an irreversible decision.

Evidence freshness is contextual: evidence bound to an older implementation or state revision must not be reused as if it validated a newer one.

## 6. Extension Contract

There are exactly three extension kinds:

- **Skill** — how to perform a bounded capability.
- **Guardrail** — what must be denied, restricted, or require approval.
- **Fitness** — how to measure whether a required property currently passes.

A project extension must declare identity, kind, maturity, semantic intent, trigger, inputs/outputs, permission requirements, evidence/provenance, and failure semantics sufficient for its kind.

Extension maturity:

```text
PROJECT_LOCAL
→ HARVEST_CANDIDATE
→ SHARED_CANDIDATE
→ BUILTIN
→ DEPRECATED / RETIRED
```

Only `BUILTIN` is framework-reusable. Harvest Candidates are evidence, not reusable Built-ins.

## 7. Governance Compilation & Validation

GPT acts as project governance compiler/coordinator. Before authorization, machine configuration must validate:

- supported Kernel/schema versions;
- unique extension IDs;
- referenced extensions exist;
- Built-in enablement is explicit;
- project-local extensions contain evidence/provenance;
- permissions do not expand parent authority;
- state and transition are legal;
- required capabilities are available or explicitly blocked;
- framework/project root boundaries are respected.

Kernel validation checks consistency; it does not invent project requirements.

## 8. Reconciliation

Kernel uses one generic `RECONCILIATION_REQUIRED` state. Domain-specific extensions provide `source` and `reason`, for example `git/BASE_MISMATCH` or `observability/IDENTITY_MISMATCH`. Kernel does not grow a new state for every capability.

## 9. Progressive Disclosure

Default context loading order:

```text
PROJECT → STATE → CONTROL → active WORK_UNIT → selected extensions → related evidence
```

Do not load unrelated Skills, Guardrails, Fitness, historical evidence, or framework development history merely because it exists.

## 10. Governance YAGNI / Complexity Control

The framework optimizes for **sufficient governance, not maximal governance**.

Fixed complexity-control principles:

- **Reuse before extension.**
- **Degrade before extend** when the requirement remains satisfied.
- **Generalize after repetition, not before.**
- **Preinstalled does not mean enabled.**

Before creating an extension:

```text
Reuse Built-in
→ Reuse project-native mechanism
→ Configure existing capability
→ Compose existing capabilities
→ Degrade safely if requirement remains satisfied
→ Extension Admission Gate
→ Smallest project-local extension
```

Default decision: `DO_NOT_ADD`.

Acceptable reasons derive from:

- observed evidence;
- explicit requirement;
- credible project-specific risk.

“Best practice”, hypothetical perfection, or generic quality improvement alone is insufficient.

Every project-local extension needs provenance and a retirement condition. Governance itself is eligible for periodic cleanup.

## Governed Change Entry

`capability-before-Design` is mandatory for a new or materially expanded Design: `EXISTING -> reuse`, `PARTIAL -> extend existing capability`, and `MISSING -> test existing responsibility first`. Record only observable authority, capability, root-cause, reuse-path, and minimum-delta facts.

Durable mutation follows one existing-authority path:

```text
CURRENT AUTHORITY / STATE
-> EXISTING CAPABILITY CHECK
-> minimum delta
-> authorized mutation
-> PRE-EXECUTION review
-> execution
-> POST-EXECUTION review
```

A failed entry is `ANALYSIS_ONLY / DENY_MUTATION`; read-only analysis remains governed by its current authority. The current accepted Framework governs Framework self-modification. A proposed rule is non-retroactive and becomes authority only after its governed acceptance, validation, and integration lifecycle. POST-EXECUTION `REVIEW_FINDING -> decision -> FIX_INSTRUCTION -> re-review` remains authoritative.

## 11. Kernel Versioning / Compatibility / Migration

Machine governance records:

- `kernel_version`
- `schema_version`
- framework `adopted_version`
- framework `last_evaluated_version`

A framework upgrade must not silently reinterpret existing governance. New framework versions are evaluated, not propagated.

Compatibility results:

- `NO_ACTION`
- `OPTIONAL_REUSE`
- `RECOMMENDED_UPGRADE`
- `REQUIRED_MIGRATION`
- `CONFLICT`

Incompatible schema/Kernel changes require explicit migration planning and validation. Evaluation does not mean adoption.

## Universal framework/project boundary

- Project root is authoritative.
- Framework root is auxiliary.
- Kernel/Built-ins are read-only during ordinary project execution.
- Current project may export only to its own Harvest Inbox namespace.
- Source-project extensions are modified in the source project, not in Harvest.
- Built-in promotion belongs only to framework maintenance.
- Promotion never silently changes source projects.

## Built-in adoption

Framework Built-ins are discovered read-only. Default adoption is `COPY_TO_PROJECT`: GPT selects a justified Built-in and Codex copies a versioned snapshot into the authoritative project extension area. The project records origin/version in CONTROL. A later framework release never rewrites that snapshot automatically; compatibility evaluation may propose replacement or migration.

## Built-in emergence

Built-ins should emerge from repeated project evidence, not speculative generalization. Compare semantic intent and contract, not filenames. Common behavior may be generalized while project-specific implementation remains local.

## Human routing contract

Every requested action identifies its executor as `[USER_LOCAL]`, `[CODEX]`, `[RETURN_TO_GPT]`, or `[INFO]`. Unlabeled prose is not executable.

Before every copyable Codex instruction GPT declares:

```text
【执行策略】<当前实际策略>
【完成后是否需要批准】不需要 | 需要 GPT 判断 | 需要用户批准
```

Machine completion gate: `NONE | GPT_DECISION | USER_APPROVAL`.

## Kernel exclusion test

Before adding any future Kernel concept, ask:

1. Do essentially all governed projects require it?
2. Without it, can Kernel no longer guarantee governance correctness?
3. Can it not be expressed as Skill, Guardrail, or Fitness?

If any answer is `NO`, default to keeping it outside Kernel.
