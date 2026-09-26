# P2 Revision 002 Work Unit Authority Plan Amendment

Status: AUTHORITY_PLAN_CANDIDATE_ONLY. Purpose: WORK_UNIT_AND_BOOTSTRAP_AUTHORITY_MATERIALIZATION_ONLY. This append-only plan supplements the accepted P2 Design 91b485c6c93584ef2f89c459c10e488750f5801f, Base Plan 7ac219d15269bdc68d66f07cfe85b044fef35279, governing Plan 40b704e343762c1c1acbef8c243adb8b0d25b1f6, and Work Unit Authority Design cbf69259698a4eb0518ce9442d729e9804ad9f74. It neither changes those artifacts nor authorizes implementation.

## Authority and runtime facts

Repository identity is ID 1366213495, xqc2098948451-byte/gpt-codex-framework, default branch main. Authoring base is cbf69259698a4eb0518ce9442d729e9804ad9f74. Observed STATE revision 17, AUTHORIZED, active_work_unit framework-staged-closure-group-a-001, and next_action GROUP_C_PRE_EXECUTION_REOBSERVATION_REQUIRED are observations only. Revision 17 is not frozen for future execution. The old task-3-global-plugin-core-001 remains historical non-authority.

The candidate cannot claim its own accepted SHA. After independent Plan review, GPT adjudication, exact USER acceptance, USER_LOCAL exact Plan integration, and independent remote verification, set ACCEPTED_AUTHORITY_PLAN_SHA to the exact reviewed, accepted and integrated Authority Plan commit. This artifact identity remains immutable after integration. Determine whether any independently required existing-authority STATE reconciliation remains. If required, complete it under separate authority before freezing; this plan grants no STATE mutation. Then freshly observe final origin/main and STATE together. Set P2_AUTHORITY_BASE_SHA to that final origin/main SHA and FINAL_STABLE_STATE_REVISION to the revision R observed there only after Task 1 passes. Require ACCEPTED_AUTHORITY_PLAN_SHA to be an ancestor of or equal to P2_AUTHORITY_BASE_SHA; equality is not required. Freeze the Work Unit and bootstrap only after that final main/STATE pair is stable.

A separately accepted successor Authority Plan is required only if the accepted Authority Plan semantics are no longer valid, scope or authority changes, a new mechanism is required, or the accepted Design/Plan chain changes materially. Normal separately authorized pre-freeze reconciliation that advances main does not by itself invalidate this Authority Plan.

## Task 1 — Fresh authority-base observation

After Authority Plan integration and completion of any independently required existing-authority reconciliation, USER_LOCAL/GPT freshly read final remote main, repository identity, CONTROL and STATE identity/schema at that main, current revision R, P2 Work Unit path, and dedicated bootstrap ref. Verify the Authority Plan is integrated and reachable from final main, and prove exact ancestry with git merge-base --is-ancestor ACCEPTED_AUTHORITY_PLAN_SHA P2_AUTHORITY_BASE_SHA or equivalent. Verify final origin/main equals P2_AUTHORITY_BASE_SHA, STATE is valid and AUTHORIZED there, project_id is PRJ-FRAMEWORK-MANAGEMENT, repository identity matches CONTROL, Work Unit path is absent, bootstrap ref is absent, and old Task3 remains non-authority and is not selected. Set FINAL_STABLE_STATE_REVISION = runtime observed R only after all checks pass and the final main/STATE pair is stable. If the Authority Plan is not an ancestor of the final base, reconciliation is still required, or main or STATE drifts after freeze, stop with the applicable failure outcome. No inferred activation or reinterpretation of STATE.active_work_unit is allowed.

## Task 2 — Canonical Work Unit builder and freeze

Run the following complete Python 3 standard-library builder from the accepted Plan text, with the real final authority base SHA, accepted Authority Plan SHA, and final R supplied separately at runtime. The builder writes nothing. It emits canonical bytes and metrics only. Its ordered mapping is complete before serialization. No unresolved placeholder enters frozen bytes.

    import hashlib, json, re, sys
    from pathlib import Path

    DESIGN = {"path": "docs/superpowers/specs/2026-09-26-p2-minimum-capability-design-revision-002.md", "sha": "91b485c6c93584ef2f89c459c10e488750f5801f"}
    PLAN = {"path": "docs/superpowers/plans/2026-09-26-p2-minimum-capability-plan-revision-003.md", "sha": "40b704e343762c1c1acbef8c243adb8b0d25b1f6"}
    AUTH_DESIGN = {"path": "docs/superpowers/specs/2026-09-26-p2-rev002-work-unit-authority-design-amendment.md", "sha": "cbf69259698a4eb0518ce9442d729e9804ad9f74"}
    AUTH_PLAN_PATH = "docs/superpowers/plans/2026-09-26-p2-rev002-work-unit-authority-plan-amendment.md"
    WU_ID = "p2-minimum-capability-implementation-001"
    WU_PATH = ".gpt-codex/work-units/" + WU_ID + ".json"
    BOOT_ID = "p2-rev002-implementation-work-unit-bootstrap-001"
    BOOT_REF = "refs/tags/bootstrap/p2-rev002-implementation-work-unit-001"
    OWNED = [
        ".gpt-codex/scripts/continuity_resume.py",
        ".gpt-codex/scripts/framework_plugin_entry.py",
        ".gpt-codex/scripts/instruction_envelope.py",
        ".gpt-codex/scripts/result_return.py",
        ".gpt-codex/tests/test_continuity_resume.py",
        ".gpt-codex/tests/test_framework_plugin.py",
        ".gpt-codex/tests/test_instruction_envelope.py",
        ".gpt-codex/tests/test_instruction_role_contract.py",
        ".gpt-codex/tests/test_result_return.py",
        ".gpt-codex/tests/test_framework_plugin_package.py",
        ".gpt-codex/release/consumer-projection-manifest.json",
        "plugins/gpt-codex-framework/plugin.json",
        "plugins/gpt-codex-framework/.codex-plugin/plugin.json",
        "plugins/gpt-codex-framework/skills/framework-governance/SKILL.md",
        ".gpt-codex/evidence/instructions/",
        ".gpt-codex/evidence/P2-PLUGIN-E2E-ACCEPTANCE.json",
    ]
    EXCLUDED = [
        "VERSION", ".gpt-codex/CHANGELOG.md", "releases/", "dist/",
        ".agents/plugins/marketplace.json",
        DESIGN["path"],
        "docs/superpowers/plans/2026-09-26-p2-minimum-capability-plan-revision-002.md",
        PLAN["path"], ".gpt-codex/STATE.json", ".gpt-codex/CONTROL.json",
    ]
    READ_ONLY = [
        ".gpt-codex/scripts/validate_project.py",
        ".gpt-codex/scripts/role_communication.py",
        ".gpt-codex/scripts/framework_feedback.py",
        ".gpt-codex/tests/test_review_lifecycle.py",
        ".gpt-codex/tests/test_validator_context_binding.py",
        ".gpt-codex/tests/test_framework_feedback.py",
        ".gpt-codex/tests/test_consumer_projection.py",
        ".gpt-codex/schemas/instruction-envelope.schema.json",
        ".gpt-codex/schemas/result-envelope.schema.json",
        ".gpt-codex/schemas/work-unit.schema.json",
        ".gpt-codex/CONTROL.json", ".gpt-codex/STATE.json", "AGENTS.md",
    ]
    ACTIONS = ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"]
    FORBIDDEN = ["COMMIT", "PUSH", "PUBLISH", "AUTHORIZE", "SCOPE_EXPANSION",
                 "FRAMEWORK_RELEASE", "PLUGIN_RELEASE", "PLUGIN_ACTIVATION",
                 "DIRECT_MAIN_IMPLEMENTATION"]
    SHA = re.compile(r"[0-9a-f]{40}\Z")
    SELECTOR = re.compile(r"^(?!/)(?![A-Za-z]:)(?!.*\\)(?!.*[*?\[\]])(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*//)(?:[^/]+/)*[^/]+/?$")
    def canonical(value):
        raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        assert not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw
        assert all(line == line.rstrip(b" \t") for line in raw.split(b"\n"))
        return raw
    def check_sha(value):
        if not isinstance(value, str) or SHA.fullmatch(value) is None:
            raise ValueError("invalid exact SHA")
    def check_ref(ref):
        if list(ref) != ["path", "sha"] or not isinstance(ref["path"], str) or not ref["path"]:
            raise ValueError("invalid immutable ref")
        check_sha(ref["sha"])
    def validate_wu(value, schema):
        required = set(schema["required"])
        if not required.issubset(value):
            raise ValueError("Work Unit missing schema fields")
        if value["kernel_version"] != schema["properties"]["kernel_version"]["const"]:
            raise ValueError("kernel version mismatch")
        if value["schema_version"] != schema["properties"]["schema_version"]["const"]:
            raise ValueError("schema version mismatch")
        if type(value["basis_state_revision"]) is not int or value["basis_state_revision"] < 0:
            raise ValueError("invalid revision")
        if not isinstance(value["goal"], str) or not value["goal"]:
            raise ValueError("invalid goal")
        scope = value["scope"]
        if set(scope) - {"owned_paths", "excluded_paths"}:
            raise ValueError("unknown scope key")
        for key in ("owned_paths", "excluded_paths"):
            paths = scope[key]
            limit = schema["properties"]["scope"]["properties"][key]
            if not isinstance(paths, list) or len(paths) != len(set(paths)):
                raise ValueError("duplicate or malformed paths")
            if len(paths) < limit.get("minItems", 0) or len(paths) > limit.get("maxItems", 10**9):
                raise ValueError("scope cardinality")
            if any(not isinstance(p, str) or SELECTOR.fullmatch(p) is None for p in paths):
                raise ValueError("invalid selector")
        if set(scope["owned_paths"]) & set(scope["excluded_paths"]):
            raise ValueError("owned/excluded collision")
        if list(value["artifact_refs"]) != ["design", "plan"]:
            raise ValueError("artifact authority shape")
        for ref in value["artifact_refs"].values():
            check_ref(ref)
        if value["artifact_refs"] != {"design": DESIGN, "plan": PLAN}:
            raise ValueError("functional authority drift")
        if value["scope"]["owned_paths"] != OWNED or value["scope"]["excluded_paths"] != EXCLUDED:
            raise ValueError("scope drift")
        if value["permissions"] != {"authorized_actions": ACTIONS, "forbidden_actions": FORBIDDEN}:
            raise ValueError("role authority drift")
        if value["state"] != "AUTHORIZED" or value["project_id"] != "PRJ-FRAMEWORK-MANAGEMENT":
            raise ValueError("identity drift")
    def build_work_unit(revision, schema):
        if type(revision) is not int or revision < 0:
            raise ValueError("R must be an observed nonnegative integer")
        wu = {
            "kernel_version": "2.0.0", "schema_version": 1,
            "project_id": "PRJ-FRAMEWORK-MANAGEMENT", "work_unit_id": WU_ID,
            "goal": "Implement the accepted P2 minimum governance capability through repository-native authority and a thin optional Plugin, only after a separate native PRE-EXECUTION PASS and GPT adjudication.",
            "scope": {"owned_paths": OWNED, "excluded_paths": EXCLUDED},
            "acceptance": {"requirements": [
                "Accepted P2 Design and governing Plan Revision 003 govern implementation; this Authority Plan governs only materialization.",
                "Repository-level baseline resume works for every enrolled Project; valid execution-slot-aware enrichment is conditional.",
                "Slotless handoff uses exact governed Instruction, immutable target_work_unit_ref, instruction_locator, target_work_unit_id and expected_state_revision; no invented slot or STATE.active_work_unit reinterpretation.",
                "Missing, stale, ambiguous or conflicting handoff facts return RECONCILIATION_REQUIRED; valid slot authority and Instruction bindings must agree.",
                "Plugin remains thin; Core owns recovery, STATE interpretation and Result discovery.",
                "result_return.py changes only for a proven narrow adapter seam; .codex-plugin/plugin.json is an optional compatibility fallback; consumer projection manifest changes only when current validation proves classification is required.",
                "Instruction Evidence writes are confined to .gpt-codex/evidence/instructions/<instruction_id>.json; no general Evidence write authority.",
                "No STATE/CONTROL mutation, release, publication, activation, new schema, service, store, queue, or Plugin-owned recovery.",
                "CODEX_IMPLEMENTER has no COMMIT or PUSH; implementation requires a separate native Instruction and independent PRE-EXECUTION PASS."
            ], "read_only_dependencies": READ_ONLY},
            "artifact_refs": {"design": DESIGN, "plan": PLAN},
            "selected_extensions": {"skills": ["github-project-continuity"],
                                    "guardrails": ["universal-safety", "cross-project-context-binding", "github-repository-binding"],
                                    "fitness": []},
            "permissions": {"authorized_actions": ACTIONS, "forbidden_actions": FORBIDDEN},
            "state": "AUTHORIZED", "basis_state_revision": revision,
            "authorization": {"authority_type": "USER_APPROVAL", "status": "AUTHORIZED",
                              "implementation_authorized": False,
                              "implementation_start_allowed": False,
                              "next_gate": "NATIVE_P2_PRE_EXECUTION_REVIEW"},
        }
        validate_wu(wu, schema)
        raw = canonical(wu)
        if json.loads(raw) != wu:
            raise ValueError("roundtrip mismatch")
        return wu, raw
    def build_bootstrap(authority_base_sha, accepted_authority_plan_sha, revision, work_unit_sha256):
        check_sha(authority_base_sha)
        check_sha(accepted_authority_plan_sha)
        if type(revision) is not int or revision < 0 or not re.fullmatch(r"[0-9a-f]{64}", work_unit_sha256):
            raise ValueError("invalid frozen binding")
        return {
            "bootstrap_id": BOOT_ID, "bootstrap_ref": BOOT_REF,
            "repository_id": 1366213495,
            "repository_full_name": "xqc2098948451-byte/gpt-codex-framework",
            "default_branch": "main", "authority_base_sha": authority_base_sha,
            "expected_state_revision": revision,
            "functional_design_ref": DESIGN, "functional_plan_ref": PLAN,
            "materialization_design_ref": AUTH_DESIGN,
            "materialization_plan_ref": {"path": AUTH_PLAN_PATH, "sha": accepted_authority_plan_sha},
            "work_unit_id": WU_ID, "work_unit_path": WU_PATH,
            "work_unit_sha256": work_unit_sha256,
            "mutation_scope": [WU_PATH], "operation": "CREATE_ONLY",
            "executor_role": "USER_LOCAL", "one_time": True,
        }
    def freeze(authority_base_sha, accepted_authority_plan_sha, revision, schema_path):
        check_sha(authority_base_sha)
        check_sha(accepted_authority_plan_sha)
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        wu, wu_raw = build_work_unit(revision, schema)
        wu_sha = hashlib.sha256(wu_raw).hexdigest()
        boot = build_bootstrap(authority_base_sha, accepted_authority_plan_sha, revision, wu_sha)
        boot_raw = canonical(boot)
        if json.loads(boot_raw) != boot:
            raise ValueError("bootstrap roundtrip mismatch")
        return {
            "work_unit_bytes": wu_raw,
            "work_unit_byte_count": len(wu_raw),
            "work_unit_sha256": wu_sha,
            "work_unit_git_blob_sha1": hashlib.sha1(
                b"blob " + str(len(wu_raw)).encode("ascii") + b"\0" + wu_raw
            ).hexdigest(),
            "bootstrap_bytes": boot_raw,
            "bootstrap_byte_count": len(boot_raw),
            "bootstrap_sha256": hashlib.sha256(boot_raw).hexdigest(),
        }

Invoke freeze only after Task 1 as freeze(P2_AUTHORITY_BASE_SHA, ACCEPTED_AUTHORITY_PLAN_SHA, FINAL_STABLE_STATE_REVISION, schema_path), with schema_path .gpt-codex/schemas/work-unit.schema.json at exact final authority base. Preserve returned bytes verbatim in a reviewed transport artifact outside repository mutation scope. Freeze P2_WORK_UNIT_BYTE_COUNT, P2_WORK_UNIT_SHA256, P2_WORK_UNIT_GIT_BLOB_SHA1, P2_BOOTSTRAP_BYTE_COUNT and P2_BOOTSTRAP_SHA256. The builder's authority_base_sha, accepted_authority_plan_sha and revision are runtime inputs, never literal placeholders serialized into either frozen JSON. Confirm canonical UTF-8 without BOM, LF only, one terminal LF, and no trailing whitespace. The Work Unit artifact_refs.plan remains Plan 003, never this Authority Plan. READ_ONLY entries are acceptance assertions, not owned paths. Permission ownership does not require changing conditional paths.

## Task 3 — One-time bootstrap PRE review and approval

A fresh independent CODEX_REVIEWER compares exact repository/final base/STATE R, accepted Authority Plan provenance and ancestry, absent Work Unit path/ref, both frozen byte streams and metrics, one-path CREATE_ONLY scope, USER_LOCAL executor, one_time true, both functional refs, both materialization refs, and old Task3 non-reuse. Check no STATE mutation, Plugin implementation, release, publication, or CODEX COMMIT/PUSH. Return only BOOTSTRAP_PRE_REVIEW = PASS or REVIEW_FINDING. PASS is evidence, not mutation authority. GPT adjudicates. Exact USER approval must bind P2_BOOTSTRAP_SHA256, P2_WORK_UNIT_SHA256, P2_AUTHORITY_BASE_SHA, STATE_REVISION_R, WORK_UNIT_PATH, and BOOTSTRAP_REF. Only then grant bounded USER_LOCAL BOOTSTRAP_TAG_CREATE, WORK_UNIT_ONE_PATH_COMMIT, WORK_UNIT_CANDIDATE_PUSH and WORK_UNIT_MAIN_FAST_FORWARD_IF_VERIFIED. No P2 implementation authority arises.

## Task 4 — USER_LOCAL tag and Work Unit materialization

After exact approval, USER_LOCAL creates a single annotated tag at BOOT_REF targeting P2_AUTHORITY_BASE_SHA. Its annotation is exactly the frozen bootstrap byte stream. Before any push, read the local tag object as raw bytes, split header and annotation at the first blank line, and verify target, nonzero annotation length, byte count and SHA-256. Push tag without force; independently read the remote ref and tag object and repeat exact target/annotation checks. Empty or altered annotation must never be pushed.

From the exact authority base, USER_LOCAL writes exactly the frozen Work Unit bytes at WU_PATH, creates one candidate commit with parent exactly P2_AUTHORITY_BASE_SHA and changed path list exactly [WU_PATH], and pushes a dedicated candidate ref without force. Independently verify the remote candidate parent, one-path delta, Work Unit byte count/SHA-256/Git blob SHA-1, STATE revision R, unchanged bootstrap tag and accepted refs. Only after PASS may USER_LOCAL fast-forward main to that exact candidate commit, without force, merge, squash, cherry-pick substitution, or extra paths. Verify remote main equals P2_WORK_UNIT_INTEGRATION_SHA. Any drift stops; this plan does not authorize a repair by rewriting frozen bytes.

## Task 5 — Termination and fresh post-materialization check

After exact integration and independent remote verification, P2_BOOTSTRAP = TERMINATED and P2_BOOTSTRAP_REUSE = FORBIDDEN. No generic creation authority survives. Freshly read remote main, STATE revision and active_work_unit, Work Unit blob and artifact refs. Require STATE.revision == R, exact integrated Work Unit bytes, and unchanged active_work_unit unless a separately authorized prior reconciliation established a different value before freeze. If revision changed, return RECONCILIATION_REQUIRED / STALE_WORK_UNIT. Do not edit the frozen Work Unit or STATE to make it current.

## Task 6 — Native Instruction preparation and independent PRE review

Only after integration, freshly inspect current instruction-envelope.schema.json, instruction_envelope.py, role_communication.py and validate_project.py. Use their real builder and validator; do not invent an interface. Prepare a native EXECUTION_INSTRUCTION with issuer GPT_ORCHESTRATOR, executor CODEX_IMPLEMENTER and return GPT_ORCHESTRATOR. Bind CONTROL project_context_id, exact repository ID/name, target_work_unit WU_ID, immutable target_work_unit_ref {path: WU_PATH, sha: P2_WORK_UNIT_INTEGRATION_SHA}, expected_state_revision R and expected_base_sha P2_WORK_UNIT_INTEGRATION_SHA. The Instruction's authorized_actions are a subset of ACTIONS and forbidden_actions preserve CODEX Git/release boundaries.

Choose scope_paths as a concrete bounded projection of OWNED. If Instruction Evidence is in scope, replace the directory selector with .gpt-codex/evidence/instructions/<actual instruction_id>.json. Keep the three Plugin package paths exact. Do not include conditional paths unless their accepted conditions are demonstrated; Work Unit ownership alone does not require mutation. Do not include any general Evidence directory, STATE, CONTROL, read-only dependency, excluded path, release or publication path.

A fresh independent CODEX_REVIEWER compares accepted P2 Design, Base Plan 002, governing Plan 003, accepted Authority Design/Plan, integrated Work Unit, native Instruction, current STATE R/base, role/actions, exact projected scope, dual-path recovery and conditional boundaries. If bounded, report PRE_EXECUTION_REVIEW = PASS and NEXT = GPT_P2_IMPLEMENTATION_PREEXEC_ADJUDICATION. Wider scope, STATE transition, new schema/module/service/store/queue, Plugin-owned recovery, extra authority, release/publication, or unresolved slot/recovery conflict yields REVIEW_FINDING and STOP. This Plan stops here. It does not authorize or plan CODEX_IMPLEMENTER mutation, RED/GREEN implementation, task commits, Plugin package/E2E implementation, post-execution review or release. Those remain under the accepted P2 implementation Plan and require separate GPT adjudication after integrated Work Unit, native Instruction and PRE PASS.

## Failure table

| Condition | Required outcome |
| --- | --- |
| accepted Authority Plan is not an ancestor of final authority base | RECONCILIATION_REQUIRED |
| independently required existing-authority reconciliation remains incomplete before freeze | RECONCILIATION_REQUIRED |
| main changes after final authority-base freeze | RECONCILIATION_REQUIRED |
| STATE changes after freeze | RECONCILIATION_REQUIRED / STALE_WORK_UNIT |
| Work Unit path exists; bootstrap ref exists or is reused | RECONCILIATION_REQUIRED |
| Work Unit bytes/hash/blob mismatch; bootstrap bytes/hash mismatch | FAIL |
| candidate changes more than WU_PATH or has wrong parent | FAIL |
| old Task3 reused | FAIL / STALE_AUTHORITY_REUSE |
| STATE.active_work_unit silently changed or reinterpreted | FAIL / PROJECT_AUTHORITY_BOUNDARY_VIOLATION |
| Instruction exceeds Work Unit or grants general Evidence writes | FAIL / SCOPE_EXPANSION |
| CODEX receives COMMIT/PUSH | ROLE_AUTHORITY_CONFLICT |
| release, publication or activation enters scope | FAIL |
| new state, recovery or control subsystem required | AMENDMENT_REQUIRED |

## Self-review and stop condition

Before persistence request, verify builder replay against current Work Unit schema, exact ordered OWNED and EXCLUDED lists, Plan 003 artifact ref, runtime-only R/final authority base SHA/accepted Authority Plan SHA, exact Plan-to-base ancestry, one-path USER_LOCAL bootstrap, two distinct authority purposes, conditional/read-only boundaries, no STATE mutation, post-integration revision equality, immutable Instruction ref, concrete Evidence path, no CODEX Git transport and PRE-only stop. If any check fails, return REVIEW_FINDING, not candidate-ready. This candidate itself grants neither Work Unit creation nor P2 implementation.
