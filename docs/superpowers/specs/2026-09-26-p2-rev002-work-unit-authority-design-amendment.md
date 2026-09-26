# P2 Revision 002 Work Unit Authority Design Amendment

## Status and trigger

**Status:** Design candidate for independent review.  
**Implementation authorized:** NO.  
**Plugin implementation authorized:** NO.  
**Work Unit creation authorized:** NO until this Design and its later Plan are accepted and the dedicated bootstrap PRE-EXECUTION gate passes.

This amendment closes one bounded authority gap after acceptance of:

- Design: `91b485c6c93584ef2f89c459c10e488750f5801f:docs/superpowers/specs/2026-09-26-p2-minimum-capability-design-revision-002.md`
- Plan: `7ac219d15269bdc68d66f07cfe85b044fef35279:docs/superpowers/plans/2026-09-26-p2-minimum-capability-plan-revision-002.md`

The gap is not P2 behavior. The gap is the missing current authority route needed to create a new implementation Work Unit for P2 Revision 002 without reusing stale Plugin authority or silently replacing the current active Work Unit.

## Observed current authority facts

At this Design baseline:

```text
PROJECT_ID = PRJ-FRAMEWORK-MANAGEMENT
STATE_REVISION = 17
STATE = AUTHORIZED
ACTIVE_WORK_UNIT = framework-staged-closure-group-a-001
STATE_NEXT_ACTION = GROUP_C_PRE_EXECUTION_REOBSERVATION_REQUIRED
MAIN_SHA = 7ac219d15269bdc68d66f07cfe85b044fef35279
```

An older Plugin Work Unit exists:

`task-3-global-plugin-core-001`

but it is not valid P2 Revision 002 implementation authority because:

- it binds the superseded 2026-09-16 Plugin Design and Plan;
- `basis_state_revision = 10`;
- `state = INCOMPLETE`;
- it contains `USER_DIRECTED_DEFERRAL`;
- `resume_requires_new_authorization = true`;
- its scope does not cover the complete accepted P2 Revision 002 Plan.

Therefore:

```text
OLD_TASK3_REUSE = DENY
SILENT_REAUTHORIZATION = DENY
SILENT_ACTIVE_WORK_UNIT_REPLACEMENT = DENY
```

The old Work Unit remains historical evidence and is not deleted or rewritten.

## Root cause

```text
ROOT_CAUSE = P2_REV002_NATIVE_IMPLEMENTATION_WORK_UNIT_CREATION_AUTHORITY_MISSING
```

The accepted P2 Design/Plan define implementation scope and acceptance, but they deliberately do not authorize their own execution and do not create a Work Unit.

The current STATE also names a different legacy/management `active_work_unit` value. That observation does not authorize changing it and does not, by itself, create or deny P2 execution authority. Existing native execution validation binds the exact Work Unit through `target_work_unit_ref`, `target_work_unit`, immutable artifact refs, and the current STATE revision. This Design therefore does not add a P2 activation STATE transition.

## Exact future P2 implementation Work Unit

The future canonical Work Unit is:

```text
WORK_UNIT_ID = p2-minimum-capability-implementation-001
PROJECT_ID = PRJ-FRAMEWORK-MANAGEMENT
STATE = AUTHORIZED
BASIS_STATE_REVISION = <final stable STATE revision observed immediately before freeze>
```

The Work Unit binds exactly the accepted P2 Design and Plan above.

### Default owned paths

The default implementation mutation scope is limited to the paths required by the accepted Plan:

```text
.gpt-codex/scripts/framework_plugin_entry.py
.gpt-codex/scripts/instruction_envelope.py
.gpt-codex/scripts/result_return.py
.gpt-codex/tests/test_framework_plugin.py
.gpt-codex/tests/test_instruction_envelope.py
.gpt-codex/tests/test_instruction_role_contract.py
.gpt-codex/tests/test_result_return.py
.gpt-codex/tests/test_framework_plugin_package.py
.gpt-codex/release/consumer-projection-manifest.json
plugins/gpt-codex-framework/plugin.json
plugins/gpt-codex-framework/.codex-plugin/plugin.json
plugins/gpt-codex-framework/skills/framework-governance/SKILL.md
.gpt-codex/evidence/instructions/
.gpt-codex/evidence/P2-PLUGIN-E2E-ACCEPTANCE.json
```

The following are read-only dependencies unless a later independent PRE review proves a minimum-delta amendment is necessary:

```text
.gpt-codex/scripts/continuity_resume.py
.gpt-codex/scripts/validate_project.py
.gpt-codex/scripts/role_communication.py
.gpt-codex/scripts/framework_feedback.py
.gpt-codex/tests/test_review_lifecycle.py
.gpt-codex/tests/test_validator_context_binding.py
.gpt-codex/tests/test_framework_feedback.py
.gpt-codex/tests/test_consumer_projection.py
.gpt-codex/schemas/instruction-envelope.schema.json
.gpt-codex/schemas/result-envelope.schema.json
.gpt-codex/schemas/work-unit.schema.json
.gpt-codex/CONTROL.json
.gpt-codex/STATE.json
AGENTS.md
```

No read-only dependency becomes mutable merely because the Plan references it.

### Explicit exclusions

The Work Unit excludes:

```text
VERSION
.gpt-codex/CHANGELOG.md
releases/
dist/
.agents/plugins/marketplace.json
docs/superpowers/specs/2026-09-26-p2-minimum-capability-design-revision-002.md
docs/superpowers/plans/2026-09-26-p2-minimum-capability-plan-revision-002.md
.gpt-codex/STATE.json
.gpt-codex/CONTROL.json
```

It also excludes any MCP server, queue, daemon, workflow engine, central project-state store, session manager, capability registry, autonomous dispatcher, public Plugin publication, or Framework release activity.

## Work Unit permissions

The future P2 Work Unit permissions are:

```text
authorized_actions =
  READ
  TEST
  VALIDATE
  REPORT
  MUTATE_APPROVED_SCOPE

forbidden_actions =
  COMMIT
  PUSH
  PUBLISH
  AUTHORIZE
  SCOPE_EXPANSION
  FRAMEWORK_RELEASE
  PLUGIN_RELEASE
  PLUGIN_ACTIVATION
  DIRECT_MAIN_IMPLEMENTATION
```

The accepted Plan's task-level "Commit Task N" checkpoints do not grant `CODEX_IMPLEMENTER` Git transport authority. Those checkpoints, when used, are separate governed Git integration actions outside the Implementer's durable permissions.

## Dedicated one-time CREATE_ONLY bootstrap

Because no current native authority exists to create this new Work Unit, the Work Unit is materialized only through one dedicated bootstrap:

```text
BOOTSTRAP_ID = p2-rev002-implementation-work-unit-bootstrap-001
BOOTSTRAP_REF = refs/tags/bootstrap/p2-rev002-implementation-work-unit-001
EXECUTOR_ROLE = USER_LOCAL
OPERATION = CREATE_ONLY
ONE_TIME = true

MUTATION_SCOPE =
  .gpt-codex/work-units/p2-minimum-capability-implementation-001.json
```

The frozen bootstrap payload must bind:

- repository ID `1366213495`;
- repository full name `xqc2098948451-byte/gpt-codex-framework`;
- default branch `main`;
- exact fresh main/base SHA;
- exact fresh STATE revision;
- accepted Design ref;
- accepted Plan ref;
- Work Unit ID/path;
- canonical Work Unit SHA-256;
- exact one-path mutation scope;
- `operation = CREATE_ONLY`;
- `executor_role = USER_LOCAL`;
- `one_time = true`.

The bootstrap does not authorize Plugin implementation, STATE mutation, activation, COMMIT/PUSH for `CODEX_IMPLEMENTER`, release, or publication.

After exact Work Unit integration and independent verification:

```text
P2_BOOTSTRAP = TERMINATED
P2_BOOTSTRAP_REUSE = FORBIDDEN
```

Historical bootstrap refs may not be reused.

## STATE revision stability gate

The P2 Work Unit is bound to the **final stable STATE revision** used for execution authority.

Any reconciliation or State transition that is independently required by existing authority must complete **before** canonical P2 Work Unit bytes are frozen. After that transition completes, GPT/User must freshly observe the resulting repository base and STATE revision and use that exact revision as both:

- the Work Unit `basis_state_revision`; and
- the bootstrap `expected_state_revision`.

This Design does not require or authorize changing `STATE.active_work_unit` as a P2 activation step. Current native execution validation binds P2 through the immutable Work Unit reference, Work Unit ID, current STATE revision, accepted artifact refs, native Instruction, and PRE-EXECUTION authority.

Therefore the legal ordering is:

```text
any separately required existing-authority STATE reconciliation
-> fresh final STATE revision R / main observation
-> freeze P2 Work Unit with basis_state_revision = R
-> freeze bootstrap with expected_state_revision = R
-> one-path Work Unit materialization
-> verify STATE revision is still R
-> native P2 Instruction with expected_state_revision = R
-> independent PRE-EXECUTION review
-> execution only while current STATE revision remains R
```

No STATE mutation is permitted between the Work Unit freeze and P2 implementation execution under this Work Unit. If STATE revision changes at any point after freeze, the frozen Work Unit is stale for execution and the result is `RECONCILIATION_REQUIRED`; it must not be rewritten in place or treated as current authority.

The current `STATE.active_work_unit` value is not silently overwritten, closed, or reinterpreted by this Design. If a future authoritative validator or PRE-EXECUTION review proves that a separate STATE transition is actually required for P2 execution, stop before implementation, complete that transition under separate existing authority, and then create a fresh successor Work Unit authority bound to the resulting revision.

## Instruction and PRE-EXECUTION boundary

After exact Work Unit creation, remote verification, and confirmation that the STATE revision still equals the Work Unit `basis_state_revision`, GPT may prepare one native implementation Instruction that:

- targets `p2-minimum-capability-implementation-001`;
- includes an immutable `target_work_unit_ref`;
- binds the current `expected_state_revision`;
- binds the current `expected_base_sha`;
- names `CODEX_IMPLEMENTER`;
- carries only actions permitted by the Work Unit and role contract;
- excludes COMMIT/PUSH/PUBLISH/AUTHORIZE/SCOPE_EXPANSION.

An independent `CODEX_REVIEWER` PRE-EXECUTION review must pass before any P2 mutation.

## Authority ordering

```text
accepted P2 Design
-> accepted P2 Plan
-> this Work Unit Authority Design candidate
-> independent Design review
-> GPT adjudication
-> exact USER Design acceptance
-> bounded USER_LOCAL Design integration
-> independent remote verification
-> Work Unit Authority Plan candidate
-> independent Plan review
-> GPT adjudication
-> exact USER Plan acceptance
-> bounded USER_LOCAL Plan integration
-> independent remote verification
-> complete any independently required existing-authority STATE reconciliation before freeze
-> fresh final main / STATE revision R observation
-> canonical P2 Work Unit bytes freeze with basis_state_revision = R
-> canonical one-time bootstrap freeze with expected_state_revision = R
-> independent bootstrap PRE-EXECUTION review
-> GPT adjudication
-> exact USER bootstrap approval
-> USER_LOCAL bootstrap ref creation / verification
-> USER_LOCAL exact one-path Work Unit materialization
-> independent candidate verification
-> conditional exact main fast-forward / verification
-> bootstrap TERMINATED
-> verify current STATE revision remains R
-> native P2 Instruction with expected_state_revision = R
-> independent PRE-EXECUTION review
-> GPT adjudication
-> CODEX_IMPLEMENTER execution
```

No implementation mutation may occur before this ordering completes.

## Failure rules

| Condition | Result |
| --- | --- |
| main/base or STATE revision changes after freeze | `RECONCILIATION_REQUIRED` |
| P2 Work Unit path unexpectedly preexists with non-identical bytes | `RECONCILIATION_REQUIRED` |
| bootstrap ref unexpectedly preexists or is reused | `RECONCILIATION_REQUIRED` |
| old `task-3-global-plugin-core-001` is treated as current P2 authority | `FAIL / STALE_AUTHORITY_REUSE` |
| current `STATE.active_work_unit` is silently replaced or reinterpreted | `FAIL / PROJECT_AUTHORITY_BOUNDARY_VIOLATION` |
| STATE revision changes after Work Unit freeze | `RECONCILIATION_REQUIRED / STALE_WORK_UNIT` |
| CODEX_IMPLEMENTER receives COMMIT/PUSH | `ROLE_AUTHORITY_CONFLICT` |
| scope expands beyond accepted Plan without amendment | `FAIL / SCOPE_EXPANSION` |
| Plugin release/publication/activation enters scope | `FAIL` |
| new schema/module/state system becomes required | `AMENDMENT_REQUIRED` |

## Independent Design review criteria

The Reviewer must verify:

1. the stale Task 3 analysis is correct;
2. a new P2 Work Unit is necessary rather than silent reuse;
3. the default mutation scope matches the accepted Plan and is minimal;
4. read-only dependencies do not become mutable accidentally;
5. Design/Plan and STATE/CONTROL remain immutable in the implementation Work Unit;
6. CODEX_IMPLEMENTER has no COMMIT/PUSH;
7. task-level Plan commit checkpoints are correctly separated from Implementer authority;
8. the one-time CREATE_ONLY bootstrap is exact, non-reusable, and creates one path only;
9. Work Unit creation does not imply activation;
10. any required STATE reconciliation occurs before Work Unit freeze, and no P2-specific `active_work_unit` mutation is invented;
11. the frozen Work Unit and bootstrap bind the same final stable STATE revision used by the native Instruction;
12. no second state/control plane or generic bootstrap factory is introduced;
13. no release/Plugin publication/activation authority is introduced.

## Non-goals

This amendment does not:

- implement P2;
- create the P2 Work Unit;
- create the bootstrap ref;
- mutate STATE or CONTROL;
- close the current active Work Unit;
- activate P2;
- create an Instruction;
- publish a Plugin;
- change Framework version;
- alter the accepted P2 Design or Plan.
