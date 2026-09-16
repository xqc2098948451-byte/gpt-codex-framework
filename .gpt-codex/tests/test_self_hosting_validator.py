import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
VALIDATOR = ROOT / ".gpt-codex" / "scripts" / "validate_project.py"
FROZEN_ZIP = ROOT / "dist" / "gpt-codex-framework-v2.2.0-bootstrap.zip"
FROZEN_FIXTURE = ROOT / ".gpt-codex" / "tests" / "fixtures" / "frozen_v220_validate_project.py"


def run_validator(project_root: Path, validator: Path = VALIDATOR) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(validator), str(project_root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def management_control() -> dict:
    control = json.loads((ROOT / ".gpt-codex" / "CONTROL.json").read_text(encoding="utf-8"))
    control["extensions"] = {
        "skills": [],
        "guardrails": [
            {"id": "github-repository-binding", "source": "builtin", "enabled": True, "version": "1.0.0"},
        ],
        "fitness": [],
    }
    return control


def write_project(root: Path, control: dict) -> None:
    gov = root / ".gpt-codex"
    gov.mkdir(parents=True)
    (gov / "CONTROL.json").write_text(json.dumps(control), encoding="utf-8")
    (gov / "STATE.json").write_text(json.dumps({
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": control["project_id"],
        "revision": 0,
        "state": "VERIFYING",
        "blockers": [],
        "evidence_refs": [],
        "continuity": {
            "current_remote_ref": None,
            "latest_verified_remote_sha": None,
            "latest_synced_state_revision": 0,
            "last_verified_result_ref": None,
            "sync_status": "SYNC_PENDING",
        },
    }), encoding="utf-8")


def governed_envelopes(control: dict) -> tuple[dict, dict, dict, dict, dict]:
    base_sha = "a" * 40
    state = {"project_id": control["project_id"], "revision": 3}
    work_unit = {"project_id": control["project_id"], "work_unit_id": "WU-GOVERNED", "state": "AUTHORIZED", "basis_state_revision": 3}
    mutation = {
        "instruction_id": "11111111-1111-4111-8111-111111111111", "instruction_type": "EXECUTION_INSTRUCTION",
        "issuer_role": "GPT_ORCHESTRATOR", "executor_role": "CODEX_IMPLEMENTER", "return_role": "GPT_ORCHESTRATOR",
        "target_project_context_id": control["project_context_id"], "target_github_repository_id": control["github"]["repository_id"],
        "target_github_repository_full_name": control["github"]["repository_full_name"], "target_work_unit": "WU-GOVERNED",
        "expected_state_revision": 3, "expected_base_sha": base_sha, "expected_remote_ref": "refs/heads/main",
        "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"], "forbidden_actions": [],
    }
    request = {
        **mutation, "instruction_id": "22222222-2222-4222-8222-222222222222", "instruction_type": "REVIEW_REQUEST",
        "executor_role": "CODEX_REVIEWER", "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT"],
        "in_response_to_instruction_id": mutation["instruction_id"], "review_target_revision": base_sha,
    }
    result = {
        "result_message_type": "REVIEW_RESULT", "responder_role": "CODEX_REVIEWER", "status": "PASS",
        "response_to_instruction_id": request["instruction_id"], "review_target_revision": base_sha,
        "source_project_context_id": control["project_context_id"],
        "source_github_repository_id": control["github"]["repository_id"],
        "source_github_repository_full_name": control["github"]["repository_full_name"],
        "current_remote_ref": mutation["expected_remote_ref"],
    }
    return state, work_unit, mutation, request, result


class SelfHostingValidatorTests(unittest.TestCase):
    def test_governed_entry_requires_repository_backed_execution_authority_when_policy_is_adopted(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        control["execution_policy"] = {
            "strategy_profile_id": "PROJECT_PROFILE_001",
            "gpt_orchestrator_strategy": "MINIMAL_CLOSED_LOOP",
            "codex_implementer_strategy": "MINIMAL_DIFF_TDD",
            "codex_reviewer_strategy": "CONTRACT_FIRST",
            "task_splitting": "PROJECT_DETERMINED",
            "review_policy": "RISK_OR_MILESTONE",
            "instruction_policy": "REFERENCE_FIRST",
            "result_return_policy": "DURABLE_REF_FIRST",
        }
        state, work_unit, mutation, request, result = governed_envelopes(control)
        work_unit["strategy_profile_id"] = control["execution_policy"]["strategy_profile_id"]
        authority = {
            "accepted_design_ref": "design:foundation@" + "a" * 40,
            "accepted_plan_ref": "plan:foundation@" + "b" * 40,
            "project_context_id": control["project_context_id"],
            "work_unit_id": work_unit["work_unit_id"],
            "state_revision": 3,
            "authorization": {
                "authority_type": "INSTRUCTION",
                "instruction_id": mutation["instruction_id"],
                "status": "EXECUTION_AUTHORIZED",
                "target_revision": mutation["expected_base_sha"],
            },
        }
        self.assertIn(
            "IMPLEMENTATION_AUTHORIZATION = DENY",
            validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
            ),
        )
        self.assertEqual(
            validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
                repository_authority=authority,
            ),
            [],
        )
        for invalid in (
            {**authority, "authorization": {**authority["authorization"], "status": "ARTIFACT_ACCEPTED"}},
            {**authority, "project_context_id": "chat-only"},
            {key: value for key, value in authority.items() if key != "accepted_plan_ref"},
            {**authority, "state_revision": 2},
        ):
            with self.subTest(invalid=invalid):
                self.assertIn(
                    "IMPLEMENTATION_AUTHORIZATION = DENY",
                    validate_governed_mutation_entry(
                        control, state, work_unit, mutation, request, result, current_state_revision=3,
                        repository_authority=invalid,
                    ),
                )

    def test_governed_entry_fails_closed_for_malformed_guardrail_control_mappings(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        for field in ("framework", "extensions"):
            for malformed_value in ("malformed", [], ""):
                with self.subTest(field=field, malformed_value=repr(malformed_value)):
                    malformed = deepcopy(control)
                    malformed[field] = malformed_value
                    errors = validate_governed_mutation_entry(
                        malformed, state, work_unit, mutation, request, result, current_state_revision=3,
                    )
                    self.assertTrue(errors)
                    self.assertIn("RECONCILIATION_REQUIRED", errors)

    def test_governed_entry_binds_review_result_identity_to_control_and_mutation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        self.assertEqual(validate_governed_mutation_entry(control, state, work_unit, mutation, request, result, current_state_revision=3), [])
        for field in (
            "source_project_context_id", "source_github_repository_id",
            "source_github_repository_full_name", "current_remote_ref",
        ):
            with self.subTest(field=field):
                errors = validate_governed_mutation_entry(
                    control, state, work_unit, mutation, request, {**result, field: "foreign"}, current_state_revision=3,
                )
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn(f"IDENTITY_MISMATCH:{field}", errors)
                errors = validate_governed_mutation_entry(
                    control, state, work_unit, mutation, request, {key: value for key, value in result.items() if key != field},
                    current_state_revision=3,
                )
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn(f"IDENTITY_MISMATCH:{field}", errors)

    def test_repository_guardrail_is_shared_by_governed_entry_and_main_validation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        missing = deepcopy(control)
        missing["extensions"]["guardrails"] = []
        disabled = deepcopy(control)
        disabled["extensions"]["guardrails"][0]["enabled"] = False
        for candidate in (missing, disabled):
            with self.subTest(candidate=candidate["extensions"]["guardrails"]):
                errors = validate_governed_mutation_entry(candidate, state, work_unit, mutation, request, result, current_state_revision=3)
                self.assertIn("GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled", errors)
                with tempfile.TemporaryDirectory() as td:
                    write_project(Path(td), candidate)
                    main_result = run_validator(Path(td))
                self.assertIn("GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled", main_result.stdout)

    def test_main_context_guardrail_keeps_2_1_rules_but_not_non_2_1_projects(self):
        control = management_control()
        control["framework_management_only"] = False
        control["governance_profile"] = "STANDARD"
        control["roots"]["framework_role"] = "ADVISORY"
        control["framework"]["adopted_version"] = "2.1.9"
        control["extensions"]["guardrails"].append(
            {"id": "cross-project-context-binding", "source": "builtin", "enabled": True, "version": "1.0.0"},
        )
        missing = deepcopy(control)
        missing["extensions"]["guardrails"] = [item for item in missing["extensions"]["guardrails"] if item["id"] != "cross-project-context-binding"]
        disabled = deepcopy(control)
        next(item for item in disabled["extensions"]["guardrails"] if item["id"] == "cross-project-context-binding")["enabled"] = False
        for candidate, expected in (
            (missing, "PROJECT_CONTEXT_BINDING: REQUIRED_CONTEXT_GUARDRAIL_ABSENT"),
            (disabled, "PROJECT_CONTEXT_BINDING: REQUIRED_CONTEXT_GUARDRAIL_DISABLED"),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as td:
                write_project(Path(td), candidate)
                self.assertIn(expected, run_validator(Path(td)).stdout)
        non_21 = deepcopy(missing)
        non_21["framework"]["adopted_version"] = "2.2.1"
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), non_21)
            self.assertNotIn("PROJECT_CONTEXT_BINDING:", run_validator(Path(td)).stdout)
    def test_governed_mutation_entry_applies_equally_to_consumer_and_self_hosting(self):
        from validate_project import validate_governed_mutation_entry

        management = management_control()
        consumer = deepcopy(management)
        consumer["framework_management_only"] = False
        consumer["governance_profile"] = "STANDARD"
        consumer["roots"]["framework_role"] = "ADVISORY"
        for control in (consumer, management):
            with self.subTest(profile=control["governance_profile"]):
                state, work_unit, mutation, request, result = governed_envelopes(control)
                self.assertEqual(validate_governed_mutation_entry(control, state, work_unit, mutation, request, result, current_state_revision=3), [])
                self.assertTrue(validate_governed_mutation_entry(control, state, {**work_unit, "state": "PROPOSED"}, mutation, request, result, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(control, {**state, "revision": 2}, work_unit, mutation, request, result, current_state_revision=3))
                self.assertIn("PRE_EXECUTION_REVIEW_REQUIRED", validate_governed_mutation_entry(control, state, work_unit, mutation, None, None, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(control, state, work_unit, {**mutation, "target_work_unit": "WRONG"}, request, result, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(
                    control, state, work_unit, {**mutation, "target_github_repository_id": "foreign-repository"}, request, result,
                    current_state_revision=3,
                ))

    def test_governed_mutation_entry_denies_disabled_guardrail_and_reviewer_mutation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        disabled = deepcopy(control)
        disabled["extensions"]["guardrails"][0]["enabled"] = False
        self.assertTrue(validate_governed_mutation_entry(disabled, state, work_unit, mutation, request, result, current_state_revision=3))
        errors = validate_governed_mutation_entry(
            control, state, work_unit, mutation, {**request, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]}, result,
            current_state_revision=3,
        )
        self.assertIn("REVIEWER_MUTATION_DENIED", errors)
    @staticmethod
    def _valid_evolution_source() -> dict:
        return {
            "classification": "READ_ONLY_EVOLUTION_SOURCE",
            "framework_version": "2.6.0",
            "source_provenance": {"commit_sha": "a" * 40},
            "compatibility_rules": {"minimum_project_version": "2.0.0"},
            "migration_available": False,
        }

    def test_frozen_v220_validator_rejects_current_management_project(self):
        with tempfile.TemporaryDirectory() as td:
            frozen_root = Path(td)
            script_dir = frozen_root / ".gpt-codex" / "scripts"
            script_dir.mkdir(parents=True)
            if FROZEN_ZIP.exists():
                with zipfile.ZipFile(FROZEN_ZIP) as archive:
                    for name in archive.namelist():
                        if "/scripts/" in name and name.endswith(".py"):
                            relative = Path(name).relative_to("gpt-codex-framework-v2.2.0-bootstrap")
                            target = frozen_root / relative
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(archive.read(name))
            else:
                (script_dir / "validate_project.py").write_bytes(FROZEN_FIXTURE.read_bytes())
                for dependency in ("kernel_rules.py", "context_binding.py"):
                    (script_dir / dependency).write_bytes((ROOT / ".gpt-codex" / "scripts" / dependency).read_bytes())
            result = run_validator(ROOT, script_dir / "validate_project.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid governance_profile", result.stdout)

    def test_v221_validator_accepts_framework_management_project(self):
        result = run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_consumer_cannot_use_framework_management_profile(self):
        control = management_control()
        control["framework_management_only"] = False
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), control)
            result = run_validator(Path(td))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid governance_profile", result.stdout)

    def test_consumer_cannot_use_self_managed_framework_root(self):
        control = management_control()
        control["framework_management_only"] = False
        control["governance_profile"] = "STANDARD"
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), control)
            result = run_validator(Path(td))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dual-root authority", result.stdout)

    def test_management_missing_catalog_builtin_is_rejected(self):
        control = management_control()
        control["extensions"]["skills"] = [{
            "id": "not-in-catalog",
            "source": "builtin",
            "enabled": True,
            "version": "1.0.0",
        }]
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            write_project(project, control)
            result = run_validator(project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("catalog", result.stdout.lower())

    def test_framework_evolution_source_is_read_only_and_provenance_bound(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        decision = validate_framework_evolution_source(source)

        self.assertEqual(decision.classification, "READ_ONLY_EVOLUTION_SOURCE")
        self.assertEqual(decision.source, source)
        self.assertEqual(set(decision.__dataclass_fields__), {"classification", "reason", "source"})
        self.assertEqual(source, self._valid_evolution_source())

    def test_evolution_source_snapshot_is_detached_from_caller_mutation(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        decision = validate_framework_evolution_source(source)
        source["source_provenance"]["commit_sha"] = "b" * 40
        source["compatibility_rules"]["minimum_project_version"] = "9.9.9"

        self.assertEqual(decision.source["source_provenance"]["commit_sha"], "a" * 40)
        self.assertEqual(
            decision.source["compatibility_rules"]["minimum_project_version"],
            "2.0.0",
        )

    def test_evolution_source_snapshot_top_level_is_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        decision = validate_framework_evolution_source(self._valid_evolution_source())

        with self.assertRaises(TypeError):
            decision.source["framework_version"] = "9.9.9"

    def test_evolution_source_snapshot_provenance_is_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        decision = validate_framework_evolution_source(self._valid_evolution_source())

        with self.assertRaises(TypeError):
            decision.source["source_provenance"]["commit_sha"] = "b" * 40

    def test_evolution_source_snapshot_compatibility_rules_are_recursively_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        source["compatibility_rules"]["supported_versions"] = ["2.0.0"]
        decision = validate_framework_evolution_source(source)

        with self.assertRaises(TypeError):
            decision.source["compatibility_rules"]["minimum_project_version"] = "9.9.9"
        with self.assertRaises(TypeError):
            decision.source["compatibility_rules"]["supported_versions"][0] = "9.9.9"

    def test_action_bearing_or_incomplete_evolution_source_is_invalid(self):
        from kernel_rules import validate_framework_evolution_source

        valid = self._valid_evolution_source()
        invalid_sources = [
            {key: value for key, value in valid.items() if key != "classification"},
            {**valid, "classification": "FRAMEWORK_EVOLUTION_SOURCE"},
            {key: value for key, value in valid.items() if key != "framework_version"},
            {**valid, "framework_version": ""},
            {key: value for key, value in valid.items() if key != "source_provenance"},
            {**valid, "source_provenance": {}},
            {**valid, "source_provenance": {"commit_sha": "not-a-sha"}},
            {key: value for key, value in valid.items() if key != "compatibility_rules"},
            {**valid, "compatibility_rules": []},
            {key: value for key, value in valid.items() if key != "migration_available"},
            {**valid, "migration_available": "false"},
        ]
        for action_field in (
            "authorized_actions", "target_work_unit", "state_revision", "command", "retry", "queue",
            "project_mutation", "role_authority", "schedule_execution", "force_adoption",
        ):
            invalid_sources.append({**valid, action_field: True})

        for source in invalid_sources:
            with self.subTest(source=source):
                decision = validate_framework_evolution_source(source)
                self.assertEqual(decision.classification, "FRAMEWORK_SOURCE_INVALID")
                self.assertIsNone(decision.source)

    def test_framework_validator_only_reports_optional_evolution_source(self):
        from validate_framework import validate_optional_framework_evolution_source

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(validate_optional_framework_evolution_source(root), [])
            source_path = root / ".gpt-codex" / "FRAMEWORK_EVOLUTION_SOURCE.json"
            source_path.parent.mkdir()
            source_path.write_text(json.dumps(self._valid_evolution_source()), encoding="utf-8")
            self.assertEqual(validate_optional_framework_evolution_source(root), [])
            source_path.write_text(json.dumps({"classification": "invalid"}), encoding="utf-8")
            self.assertEqual(
                validate_optional_framework_evolution_source(root),
                ["FRAMEWORK_SOURCE_INVALID"],
            )

    def test_read_only_source_does_not_replace_local_work_unit_authority(self):
        from validate_project import validate_framework_adoption

        control = management_control()
        instruction = {
            "target_project_context_id": control["project_context_id"],
            "target_github_repository_id": control["github"]["repository_id"],
            "target_github_repository_full_name": control["github"]["repository_full_name"],
            "target_work_unit": "WU-001",
            "expected_state_revision": 1,
            "executor_role": "CODEX_IMPLEMENTER",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": [],
        }
        work_unit = {
            "project_id": control["project_id"],
            "work_unit_id": "WU-001",
            "state": "PROPOSED",
            "basis_state_revision": 1,
        }
        self.assertEqual(
            validate_framework_adoption(
                control, instruction, work_unit, current_state_revision=1,
                source=self._valid_evolution_source(),
            ),
            ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
        )

    def test_management_evolution_index_remains_non_authoritative(self):
        from context_binding import classify_framework_evolution_index

        control = management_control()
        enrollment = {
            "explicit_enrollment": True,
            "enrollment_id": "management-1",
            "enrollment_status": "ACTIVE",
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "transport": "MANUAL",
        }
        observation = {
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "source_framework_version": "2.7.0",
            "source_provenance_digest": "a" * 64,
            "compatibility_outcome": "NO_ACTION",
            "observed_at": 1000,
            "local_revision_ref": "revision-7",
        }
        row = classify_framework_evolution_index(
            [enrollment], [observation], now=1001, stale_after_seconds=60,
        )[0]
        self.assertEqual(
            (row["classification"], row["evolution_status"]),
            ("FRAMEWORK_MANAGEMENT_METADATA", "PROJECT_EVOLUTION_OBSERVATION_CURRENT"),
        )
        self.assertFalse({
            "command", "retry", "queue", "target_work_unit", "authorized_actions", "project_mutation",
            "schedule_execution", "force_adoption", "work_unit",
        }.intersection(row))

    def test_structured_management_evolution_records_are_rejected_without_flagging_python_constants(self):
        from consumer_projection import scan_consumer_boundary

        records = {
            "framework-management.json": {"governance_profile": "FRAMEWORK_MANAGEMENT"},
            "self-managed.json": {"roots": {"framework_role": "SELF_MANAGED"}},
            "framework-management-classification.json": {"classification": "FRAMEWORK_MANAGEMENT"},
            "self-managed-classification.json": {"classification": "SELF_MANAGED"},
            "index.json": {"classification": "FRAMEWORK_MANAGEMENT_METADATA"},
            "observation.json": {
                "classification": "DERIVED_OBSERVATION_ONLY",
                "explicit_enrollment": True,
                "enrollment_status": "ACTIVE",
            },
        }
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td)
            for name, record in records.items():
                (staging / name).write_text(json.dumps(record), encoding="utf-8")
            (staging / "constants.py").write_text(
                'CLASSIFICATION = "FRAMEWORK_MANAGEMENT_METADATA"\n', encoding="utf-8",
            )
            result = scan_consumer_boundary(staging, {"contamination": {"forbidden_values": []}})

        self.assertEqual(set(result["management_identity_hits"]), set(records))
        self.assertNotIn("constants.py", result["management_identity_hits"])


if __name__ == "__main__":
    unittest.main()
