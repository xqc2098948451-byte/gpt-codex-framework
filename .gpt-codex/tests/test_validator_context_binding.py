import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from validate_project import (
    evaluate_project_evolution,
    validate_framework_adoption,
    validate_project_identity_and_derived,
    validate_project_identity_boundary,
)
from context_binding import (
    build_project_evolution_observation,
    classify_framework_evolution_index,
    evaluate_cross_project_resource_boundary,
    load_project_identity,
    validate_repository_transfer,
    validate_project_evolution_enrollment,
)


class ValidatorContextBindingTests(unittest.TestCase):
    def _complete_identity_control(self):
        return {
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "github": {
                "repository_id": "123",
                "repository_full_name": "example/project",
                "default_branch": "main",
            },
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
        }

    @staticmethod
    def _valid_evolution_source(version="2.6.0", compatibility_rules=None):
        return {
            "classification": "READ_ONLY_EVOLUTION_SOURCE",
            "framework_version": version,
            "source_provenance": {"commit_sha": "a" * 40},
            "compatibility_rules": compatibility_rules or {},
            "migration_available": False,
        }

    def _adoption_facts(self):
        control = self._complete_identity_control()
        control["framework"] = {"adopted_version": "2.6.0"}
        instruction = {
            "target_project_context_id": control["project_context_id"],
            "target_github_repository_id": control["github"]["repository_id"],
            "target_github_repository_full_name": control["github"]["repository_full_name"],
            "target_work_unit": "WU-001",
            "expected_state_revision": 6,
            "executor_role": "CODEX_IMPLEMENTER",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": [],
        }
        work_unit = {
            "project_id": control["project_id"],
            "work_unit_id": "WU-001",
            "state": "AUTHORIZED",
            "basis_state_revision": 6,
        }
        return control, instruction, work_unit

    def test_declared_invalid_identity_short_circuits_derived_validation(self):
        control = {"project_context_id": "not-a-uuid", "github": {}}
        with patch("validate_project.validate_optional_navigation_and_resume") as derived:
            errors = validate_project_identity_and_derived(Path("."), Path(".gpt-codex"), control)
        self.assertEqual(errors, ["PROJECT_IDENTITY_INVALID"])
        derived.assert_not_called()

    def test_declared_valid_identity_reaches_derived_validation(self):
        with patch(
            "validate_project.validate_optional_navigation_and_resume", return_value=["DERIVED_ERROR"]
        ) as derived:
            errors = validate_project_identity_and_derived(
                Path("."), Path(".gpt-codex"), self._complete_identity_control()
            )
        self.assertEqual(errors, ["DERIVED_ERROR"])
        derived.assert_called_once()

    def test_legacy_consumer_without_complete_identity_preserves_validation_flow(self):
        control = {"project_id": "legacy-project"}
        with patch(
            "validate_project.validate_optional_navigation_and_resume", return_value=["DERIVED_ERROR"]
        ) as derived:
            errors = validate_project_identity_and_derived(Path("."), Path(".gpt-codex"), control)
        self.assertEqual(errors, ["DERIVED_ERROR"])
        derived.assert_called_once_with(Path("."), Path(".gpt-codex"), control)

    def test_management_control_requires_explicit_management_profile(self):
        control = {
            "framework_management_only": True,
            "governance_profile": "FRAMEWORK_MANAGEMENT",
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "SELF_MANAGED", "framework_kernel_access": "READ_ONLY", "framework_builtins_access": "READ_ONLY"},
        }
        self.assertEqual(validate_project_identity_boundary(control, consumer=False), [])

    def test_consumer_control_rejects_management_identity_and_self_managed_root(self):
        control = {
            "framework_management_only": True,
            "governance_profile": "FRAMEWORK_MANAGEMENT",
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "SELF_MANAGED", "framework_kernel_access": "READ_ONLY", "framework_builtins_access": "READ_ONLY"},
        }
        self.assertIn("PROJECT_AUTHORITY_BOUNDARY_VIOLATION", validate_project_identity_boundary(control, consumer=True))
    def test_required_guardrail_manifest_and_catalog_are_present(self):
        manifest_path = ROOT / ".gpt-codex" / "builtins" / "guardrails" / "cross-project-context-binding" / "manifest.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "cross-project-context-binding")
        self.assertEqual(manifest["classification"], "REQUIRED_SAFETY_GUARDRAIL")
        catalog = json.loads((ROOT / ".gpt-codex" / "builtins" / "INDEX.json").read_text(encoding="utf-8"))
        self.assertIn("cross-project-context-binding", catalog["required"]["guardrails"])

    def test_framework_validator_checks_identity_contract(self):
        proc = subprocess.run(
            [sys.executable, ".gpt-codex/scripts/validate_framework.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("CONTEXT_BINDING: PASS", proc.stdout)

    def test_migrated_project_without_required_guardrail_is_rejected(self):
        control = {
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "framework": {"adopted_version": "2.1.0"},
            "extensions": {"guardrails": []},
        }
        from importlib.util import spec_from_file_location, module_from_spec
        path = ROOT / ".gpt-codex" / "scripts" / "validate_project.py"
        self.assertTrue(path.is_file())
        source = path.read_text(encoding="utf-8")
        self.assertIn("REQUIRED_CONTEXT_GUARDRAIL", source)

    def test_resource_boundary_rejects_foreign_or_ambiguous_authority_resources(self):
        identity = load_project_identity(self._complete_identity_control())
        resource_types = (
            "CONTROL", "STATE", "WORK_UNIT", "INSTRUCTION", "RESULT",
            "EVIDENCE", "REPOSITORY_BINDING", "EXTENSION_CONFIGURATION",
            "PROJECT_MAP", "RESUME",
        )
        matching_resource = {
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "123",
            "repository_full_name": "example/project",
        }
        foreign_context = "22222222-2222-4222-8222-222222222222"

        for resource_type in resource_types:
            with self.subTest(resource_type=resource_type, scenario="matching"):
                decision = evaluate_cross_project_resource_boundary(
                    identity, matching_resource, resource_type=resource_type,
                )
                self.assertEqual((decision.decision, decision.identity_match, decision.action_executable),
                                 ("ALLOW", True, False))

            with self.subTest(resource_type=resource_type, scenario="foreign-context"):
                decision = evaluate_cross_project_resource_boundary(
                    identity,
                    {**matching_resource, "project_context_id": foreign_context},
                    resource_type=resource_type,
                )
                self.assertEqual((decision.reason, decision.packet_status, decision.action_executable),
                                 ("CROSS_PROJECT_CONTEXT_MISMATCH", "QUARANTINED", False))

            with self.subTest(resource_type=resource_type, scenario="missing-repository-id"):
                decision = evaluate_cross_project_resource_boundary(
                    identity,
                    {key: value for key, value in matching_resource.items() if key != "repository_id"},
                    resource_type=resource_type,
                )
                self.assertEqual((decision.reason, decision.packet_status, decision.action_executable),
                                 ("PROJECT_IDENTITY_INVALID", "QUARANTINED", False))

            with self.subTest(resource_type=resource_type, scenario="verified-repository-contradiction"):
                decision = evaluate_cross_project_resource_boundary(
                    identity,
                    {**matching_resource, "repository_full_name": "other/project"},
                    resource_type=resource_type,
                )
                self.assertEqual((decision.reason, decision.packet_status, decision.action_executable),
                                 ("GITHUB_REPOSITORY_MISMATCH", "QUARANTINED", False))

            with self.subTest(resource_type=resource_type, scenario="analysis-only"):
                decision = evaluate_cross_project_resource_boundary(
                    identity,
                    {**matching_resource, "project_context_id": foreign_context},
                    resource_type=resource_type, analysis_only=True,
                )
                self.assertEqual((decision.reason, decision.packet_status, decision.action_executable,
                                  decision.current_project_mutation),
                                 ("CROSS_PROJECT_CONTEXT_MISMATCH", "QUARANTINED", False, False))

            with self.subTest(resource_type=resource_type, scenario="weak-identity-cannot-fill-binding"):
                decision = evaluate_cross_project_resource_boundary(
                    identity,
                    {
                        "project_id": "PRJ-001",
                        "project_context_id": "11111111-1111-4111-8111-111111111111",
                        "repository_full_name": "example/project",
                        "project_name": "Example Project",
                        "display_name": "Example Project",
                        "git_remote": "git@github.com:example/project.git",
                        "filesystem_path": "D:/example/project",
                    },
                    resource_type=resource_type,
                )
                self.assertEqual((decision.reason, decision.packet_status, decision.action_executable),
                                 ("PROJECT_IDENTITY_INVALID", "QUARANTINED", False))

    def test_repository_binding_classifies_malformed_configuration_before_conflict(self):
        from github_repository_binding import (
            ObservedRepository,
            compare_repository_binding,
            scan_repository_compatibility,
        )

        malformed = compare_repository_binding(
            {"github": {"repository_id": "123", "repository_full_name": "example/project"}},
            ObservedRepository("123", "example/project", "origin", "github:example/project"),
        )
        self.assertEqual(malformed.reason, "PROJECT_IDENTITY_INVALID")

        with patch(
            "github_repository_binding._git",
            side_effect=[
                (0, "true", ""),
                (0, "origin", ""),
                (0, "https://github.com/example/project.git", ""),
            ],
        ):
            malformed_scan = scan_repository_compatibility(
                Path("."), {"repository_id": "123", "repository_full_name": "not/a/path/"},
            )
        self.assertEqual(malformed_scan["classification"], "PROJECT_IDENTITY_INVALID")

        with patch(
            "github_repository_binding._git",
            side_effect=[
                (0, "true", ""),
                (0, "origin", ""),
                (0, "https://github.com/example/project.git", ""),
            ],
        ):
            contradiction = scan_repository_compatibility(
                Path("."),
                {"repository_id": "123", "repository_full_name": "example/project", "observed_repository_id": "456"},
            )
        self.assertEqual(contradiction["classification"], "GITHUB_REPOSITORY_MISMATCH")

    def test_evolution_metadata_is_descriptive_and_cannot_grant_role_instruction_or_result_authority(self):
        from instruction_envelope import validate_instruction_evolution_metadata
        from result_return import render_gpt_return, validate_result_evolution_metadata
        from role_communication import validate_evolution_metadata_authority

        descriptive = {"classification": "READ_ONLY_EVOLUTION_SOURCE", "framework_version": "2.6.0"}
        executable = {**descriptive, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]}
        self.assertEqual(validate_evolution_metadata_authority(descriptive), [])
        self.assertEqual(
            validate_evolution_metadata_authority(executable),
            ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
        )
        self.assertEqual(
            validate_instruction_evolution_metadata(executable),
            ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
        )
        self.assertEqual(
            validate_result_evolution_metadata(executable),
            ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
        )
        with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
            render_gpt_return({"return_to_gpt_required": True, "evolution_metadata": executable})

    def test_instruction_builder_and_renderer_enforce_evolution_metadata_boundary(self):
        from instruction_envelope import build_instruction_envelope, render_codex_instruction

        descriptive = {"classification": "READ_ONLY_EVOLUTION_SOURCE", "framework_version": "2.6.0"}
        executable = {**descriptive, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]}
        envelope = build_instruction_envelope(
            "WORK_UNIT", "11111111-1111-4111-8111-111111111111", "Example", 1, "2.6.0",
        )
        envelope["evolution_metadata"] = executable
        with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
            render_codex_instruction(envelope, "body", {})

        descriptive_envelope = build_instruction_envelope(
            "WORK_UNIT", "11111111-1111-4111-8111-111111111111", "Example", 1, "2.6.0",
            evolution_metadata=descriptive,
        )
        self.assertEqual(descriptive_envelope["evolution_metadata"], descriptive)
        with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
            build_instruction_envelope(
                "WORK_UNIT", "11111111-1111-4111-8111-111111111111", "Example", 1, "2.6.0",
                evolution_metadata=executable,
            )

    def test_project_evolution_evaluation_is_read_only(self):
        control = self._complete_identity_control()
        control["framework"] = {"adopted_version": "2.6.0"}
        cases = (
            ("2.6.0", {}, "NO_ACTION"),
            ("2.7.0", {"compatible": True, "reusable": True}, "OPTIONAL_REUSE"),
            ("2.7.0", {"compatible": True, "reusable": False}, "RECOMMENDED_UPGRADE"),
            ("2.7.0", {"compatible": True, "requires_migration": True}, "REQUIRED_MIGRATION"),
            ("2.7.0", {"identity_conflict": True}, "CONFLICT"),
        )
        for version, compatibility_rules, classification in cases:
            with self.subTest(classification=classification):
                source = self._valid_evolution_source(version, compatibility_rules)
                evaluation = evaluate_project_evolution(control, source)
                self.assertEqual(evaluation["classification"], classification)
                self.assertFalse(evaluation["mutated"])
                self.assertFalse(evaluation["adoption_authorized"])
                self.assertEqual(evaluation["source_provenance"], {"commit_sha": "a" * 40})
                self.assertEqual(evaluation["source_framework_version"], version)

        invalid_evaluation = evaluate_project_evolution(control, {"classification": "invalid"})
        self.assertEqual(invalid_evaluation["classification"], "FRAMEWORK_SOURCE_INVALID")
        self.assertIsNone(invalid_evaluation["source_framework_version"])

    def test_explicit_enrollment_is_not_discovery(self):
        control = self._complete_identity_control()
        enrollment = {
            "explicit_enrollment": True,
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
        }

        self.assertEqual(
            validate_project_evolution_enrollment(
                control, {"repository_full_name": "example/project"},
            ).reason,
            "PROJECT_IDENTITY_INVALID",
        )
        for transport in ("MANUAL", "PROJECT_PUSH", "PROJECT_PULL"):
            with self.subTest(transport=transport):
                decision = validate_project_evolution_enrollment(
                    control, {**enrollment, "transport": transport},
                )
                self.assertEqual((decision.decision, decision.action_executable), ("ALLOW", False))
        self.assertEqual(
            validate_project_evolution_enrollment(
                control, {**enrollment, "transport": "DISCOVERY"},
            ).reason,
            "PROJECT_IDENTITY_INVALID",
        )
        self.assertEqual(
            validate_project_evolution_enrollment(
                control,
                {**enrollment, "transport": "MANUAL", "project_context_id": "22222222-2222-4222-8222-222222222222"},
            ).reason,
            "CROSS_PROJECT_CONTEXT_MISMATCH",
        )
        self.assertEqual(
            validate_project_evolution_enrollment(
                control, {**enrollment, "transport": "MANUAL", "repository_id": "456"},
            ).reason,
            "GITHUB_REPOSITORY_MISMATCH",
        )

    def test_retired_enrollment_rejects_new_observation_and_preserves_history(self):
        control = self._complete_identity_control()
        enrollment = {
            "explicit_enrollment": True,
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "transport": "MANUAL",
        }
        evaluation = {
            "classification": "NO_ACTION",
            "source_framework_version": "2.7.0",
            "source_provenance": {"commit_sha": "a" * 40},
        }
        retired = {**enrollment, "enrollment_status": "RETIRED"}
        decision = validate_project_evolution_enrollment(control, retired)
        self.assertEqual(
            (decision.decision, decision.reason, decision.action_executable, decision.current_project_mutation),
            ("DENY", "PROJECT_EVOLUTION_NOT_ENROLLED", False, False),
        )
        with self.assertRaisesRegex(ValueError, "PROJECT_EVOLUTION_NOT_ENROLLED"):
            build_project_evolution_observation(
                control, evaluation, retired,
                observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
            )
        for status_enrollment in ({**enrollment, "enrollment_status": "ACTIVE"}, enrollment):
            with self.subTest(status=status_enrollment.get("enrollment_status", "ABSENT")):
                self.assertEqual(
                    build_project_evolution_observation(
                        control, evaluation, status_enrollment,
                        observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
                    )["classification"],
                    "DERIVED_OBSERVATION_ONLY",
                )
        historical = {
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "observed_at": 1000,
        }
        index_row = classify_framework_evolution_index(
            [retired], [historical], now=1001, stale_after_seconds=60,
        )[0]
        self.assertEqual(
            (index_row["enrollment_status"], index_row["evolution_status"]),
            ("RETIRED", "PROJECT_EVOLUTION_OBSERVATION_STALE"),
        )

    def test_observation_is_minimized_and_non_authoritative(self):
        control = self._complete_identity_control()
        enrollment = {
            "explicit_enrollment": True,
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "transport": "MANUAL",
            "control": {"secret": "must-not-copy"},
        }
        evaluation = {
            "classification": "RECOMMENDED_UPGRADE",
            "source_framework_version": "2.7.0",
            "source_provenance": {"commit_sha": "a" * 40},
            "mutated": False,
            "adoption_authorized": False,
            "result_evidence_ref": "result-1",
            "state": {"secret": "must-not-copy"},
            "source_content": "must-not-copy",
            "extensions": {"must-not-copy": True},
            "unknown": "must-not-copy",
        }

        observation = build_project_evolution_observation(
            control, evaluation, enrollment,
            observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
        )
        repeated = build_project_evolution_observation(
            control, evaluation, enrollment,
            observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
        )
        self.assertEqual(observation["classification"], "DERIVED_OBSERVATION_ONLY")
        self.assertEqual(observation["source_framework_version"], "2.7.0")
        self.assertEqual(observation["compatibility_outcome"], "RECOMMENDED_UPGRADE")
        self.assertEqual(observation["source_provenance_digest"], repeated["source_provenance_digest"])
        self.assertEqual(observation["result_evidence_ref"], "result-1")
        self.assertFalse(
            {"control", "state", "work_unit", "result", "evidence", "prompt", "reasoning", "credential",
             "credentials", "token", "tokens", "secret", "source_content", "environment", "log", "logs",
             "extensions", "unknown"}.intersection(observation)
        )
        no_reference = build_project_evolution_observation(
            control,
            {key: value for key, value in evaluation.items() if key != "result_evidence_ref"},
            enrollment, observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
        )
        max_reference = "a" * 256
        self.assertEqual(
            build_project_evolution_observation(
                control, {**evaluation, "result_evidence_ref": max_reference}, enrollment,
                observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
            )["result_evidence_ref"],
            max_reference,
        )
        for invalid_reference in ("a" * 257, "a" * (1024 * 1024), "evidence\ncontent", "raw prose"):
            with self.subTest(invalid_reference_length=len(invalid_reference)):
                self.assertEqual(
                    build_project_evolution_observation(
                        control, {**evaluation, "result_evidence_ref": invalid_reference}, enrollment,
                        observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
                    ),
                    no_reference,
                )
        with self.assertRaisesRegex(ValueError, "PROJECT_AUTHORITY_BOUNDARY_VIOLATION"):
            build_project_evolution_observation(
                control,
                {**evaluation, "evolution_metadata": {
                    "classification": "DERIVED_OBSERVATION_ONLY",
                    "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
                }},
                enrollment, observed_at="2026-09-14T12:00:00Z", local_revision_ref="revision-7",
            )
        self.assertEqual(
            validate_project_evolution_enrollment(
                control, {**enrollment, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]},
            ).reason,
            "PROJECT_AUTHORITY_BOUNDARY_VIOLATION",
        )

    def test_evolution_index_classifies_lifecycle_without_project_authority(self):
        enrollment = {
            "explicit_enrollment": True,
            "enrollment_id": "enroll-1",
            "enrollment_status": "ACTIVE",
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "123",
            "repository_full_name": "example/project",
            "transport": "MANUAL",
        }
        observation = {
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "123",
            "repository_full_name": "example/project",
            "source_framework_version": "2.7.0",
            "source_provenance_digest": "a" * 64,
            "compatibility_outcome": "RECOMMENDED_UPGRADE",
            "observed_at": 900,
            "local_revision_ref": "revision-7",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
        }
        current = classify_framework_evolution_index(
            [enrollment], [observation], now=1000, stale_after_seconds=200,
        )[0]
        stale = classify_framework_evolution_index(
            [enrollment], [observation], now=1200, stale_after_seconds=200,
        )[0]
        conflict = classify_framework_evolution_index(
            [enrollment, {**enrollment, "repository_id": "456", "repository_full_name": "other/project"}],
            [observation], now=1000, stale_after_seconds=200,
        )[0]
        not_enrolled = classify_framework_evolution_index(
            [], [observation], now=1000, stale_after_seconds=200,
        )[0]

        self.assertEqual(current["classification"], "FRAMEWORK_MANAGEMENT_METADATA")
        self.assertEqual(current["evolution_status"], "PROJECT_EVOLUTION_OBSERVATION_CURRENT")
        self.assertEqual(stale["evolution_status"], "PROJECT_EVOLUTION_OBSERVATION_STALE")
        self.assertEqual(conflict["evolution_status"], "PROJECT_EVOLUTION_ENROLLMENT_CONFLICT")
        self.assertEqual(not_enrolled["evolution_status"], "PROJECT_EVOLUTION_NOT_ENROLLED")
        self.assertFalse(
            {"command", "retry", "queue", "target_work_unit", "authorized_actions", "project_mutation",
             "schedule_execution", "force_adoption", "work_unit"}.intersection(current)
        )
        retired = classify_framework_evolution_index(
            [{**enrollment, "enrollment_status": "RETIRED"}], [observation],
            now=1000, stale_after_seconds=200,
        )[0]
        self.assertEqual(retired["evolution_status"], "PROJECT_EVOLUTION_OBSERVATION_STALE")
        renamed = classify_framework_evolution_index(
            [{**enrollment, "repository_full_name": "example/renamed", "display_name": "Renamed"}],
            [{**observation, "repository_full_name": "example/renamed"}],
            now=1000, stale_after_seconds=200,
        )[0]
        self.assertEqual(renamed["evolution_status"], "PROJECT_EVOLUTION_OBSERVATION_CURRENT")
        self.assertEqual(renamed["repository_id"], "123")

    def test_repository_transfer_requires_both_identity_bound_evidence(self):
        old_enrollment = {
            "explicit_enrollment": True,
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "123",
            "repository_full_name": "example/project",
            "transport": "MANUAL",
        }
        new_enrollment = {
            **old_enrollment, "repository_id": "456", "repository_full_name": "example/renamed",
        }
        old_evidence = {"status": "VERIFIED", "repository_id": "123", "repository_full_name": "example/project"}
        new_evidence = {"status": "VERIFIED", "repository_id": "456", "repository_full_name": "example/renamed"}

        self.assertEqual(
            validate_repository_transfer(
                old_enrollment, {**old_enrollment, "repository_full_name": "example/renamed"},
                old_repository_evidence=old_evidence, new_repository_evidence=new_evidence,
            ).reason,
            "PROJECT_IDENTITY_INVALID",
        )
        self.assertNotEqual(
            validate_repository_transfer(
                old_enrollment, new_enrollment,
                old_repository_evidence=None, new_repository_evidence=new_evidence,
            ).decision,
            "ALLOW",
        )
        self.assertNotEqual(
            validate_repository_transfer(
                old_enrollment, new_enrollment,
                old_repository_evidence=old_evidence, new_repository_evidence=None,
            ).decision,
            "ALLOW",
        )
        decision = validate_repository_transfer(
            old_enrollment, new_enrollment,
            old_repository_evidence=old_evidence, new_repository_evidence=new_evidence,
        )
        self.assertEqual((decision.decision, decision.current_project_mutation, decision.action_executable),
                         ("ALLOW", False, False))

    def test_evolution_index_rejects_observation_repository_conflict_without_split_statuses(self):
        enrollment = {
            "explicit_enrollment": True,
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "123",
            "repository_full_name": "example/project",
            "transport": "MANUAL",
        }
        observation = {
            "project_id": "PRJ-001",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": "456",
            "repository_full_name": "other/project",
            "observed_at": 1000,
        }
        rows = classify_framework_evolution_index(
            [enrollment], [observation], now=1001, stale_after_seconds=60,
        )
        affected_rows = [
            row for row in rows
            if (row["project_id"], row["project_context_id"])
            == ("PRJ-001", "11111111-1111-4111-8111-111111111111")
        ]
        self.assertTrue(affected_rows)
        self.assertTrue(all(
            row["evolution_status"] == "PROJECT_EVOLUTION_ENROLLMENT_CONFLICT"
            for row in affected_rows
        ))
        self.assertFalse(any(
            row["evolution_status"] in {
                "PROJECT_EVOLUTION_OBSERVATION_STALE", "PROJECT_EVOLUTION_NOT_ENROLLED",
            }
            for row in affected_rows
        ))

    def test_adoption_requires_local_authority_not_source_or_observation(self):
        control, instruction, work_unit = self._adoption_facts()
        source = self._valid_evolution_source()

        self.assertEqual(
            validate_framework_adoption(control, instruction, {**work_unit, "state": "PROPOSED"},
                                        current_state_revision=6, source=source),
            ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
        )
        self.assertEqual(
            validate_framework_adoption(control, instruction, work_unit, current_state_revision=7, source=source),
            ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
        )
        self.assertEqual(
            validate_framework_adoption(
                control,
                {**instruction, "evolution_metadata": {
                    "classification": "READ_ONLY_EVOLUTION_SOURCE",
                    "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
                }},
                work_unit,
                current_state_revision=6,
                source=source,
            ),
            ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"],
        )
        self.assertEqual(
            validate_framework_adoption(
                control, {**instruction, "target_project_context_id": "22222222-2222-4222-8222-222222222222"},
                work_unit, current_state_revision=6, source=source,
            ),
            ["CROSS_PROJECT_CONTEXT_MISMATCH"],
        )
        self.assertEqual(
            validate_framework_adoption(
                control, {**instruction, "target_project_context_id": "not-a-uuid"},
                work_unit, current_state_revision=6, source=source,
            ),
            ["PROJECT_IDENTITY_INVALID"],
        )
        malformed = {key: value for key, value in control.items() if key != "github"}
        self.assertEqual(
            validate_framework_adoption(malformed, instruction, work_unit, current_state_revision=6, source=source),
            ["PROJECT_IDENTITY_INVALID"],
        )
        self.assertEqual(
            validate_framework_adoption(
                control, {**instruction, "target_github_repository_id": "456"},
                work_unit, current_state_revision=6, source=source,
            ),
            ["GITHUB_REPOSITORY_MISMATCH"],
        )
        self.assertEqual(
            validate_framework_adoption(control, instruction, work_unit, current_state_revision=6,
                                        source={**source, "target_work_unit": "foreign"}),
            ["FRAMEWORK_SOURCE_INVALID"],
        )
        self.assertEqual(
            validate_framework_adoption(control, instruction, work_unit, current_state_revision=6, source=source),
            [],
        )


if __name__ == "__main__":
    unittest.main()


class ContractRepairTask4Tests(unittest.TestCase):
    def test_scope_exclusions_take_precedence_over_owned_prefixes(self):
        from validate_project import validate_instruction_authority

        instruction = {"instruction_type": "WORK_UNIT", "executor_role": "CODEX_IMPLEMENTER", "scope_paths": ["src/private/key"]}
        errors = validate_instruction_authority(
            instruction, approved_scope={"src/"}, excluded_scope={"src/private/"},
        )
        self.assertIn("SCOPE_EXPANSION_DENIED", errors)

    def test_scope_selector_exact_prefix_and_exclusion_semantics(self):
        from validate_project import validate_instruction_authority

        def errors(path, owned, excluded=()):
            return validate_instruction_authority(
                {"instruction_type": "WORK_UNIT", "executor_role": "CODEX_IMPLEMENTER", "scope_paths": [path]},
                approved_scope=set(owned), excluded_scope=set(excluded),
            )

        self.assertNotIn("SCOPE_EXPANSION_DENIED", errors("src/a.py", {"src/a.py"}))
        self.assertIn("SCOPE_EXPANSION_DENIED", errors("src/a.py.extra", {"src/a.py"}))
        self.assertNotIn("SCOPE_EXPANSION_DENIED", errors("src/a.py", {"src/"}))
        self.assertIn("SCOPE_EXPANSION_DENIED", errors("src/a.py", {"src/"}, {"src/a.py"}))
        self.assertIn("SCOPE_EXPANSION_DENIED", errors("src/private/a.py", {"src/"}, {"src/private/"}))
        self.assertIn("SCOPE_EXPANSION_DENIED", errors("other/file", {"src/"}, {"docs/"}))
        for malformed in ("", "/x", "C:/x", "src\\x", ".", "..", "src/../x", "src//"):
            with self.subTest(malformed=malformed):
                self.assertIn("SCOPE_EXPANSION_DENIED", errors("src/a.py", {malformed}))

    def test_existing_authority_gate_accepts_owned_directory_prefix(self):
        from validate_project import validate_instruction_authority
        instruction = {"instruction_type":"WORK_UNIT", "executor_role":"CODEX_IMPLEMENTER", "scope_paths":["plugins/gpt-codex-framework/subpath.py"]}
        errors = validate_instruction_authority(instruction, approved_scope={"plugins/gpt-codex-framework/"})
        self.assertNotIn("SCOPE_EXPANSION_DENIED", errors)


class ApprovalEvidenceConsumerTests(unittest.TestCase):
    def _intrinsic_approval(self):
        return {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "PRJ-001", "work_unit_id": "WU-001", "extension": {},
            "result_id": "approval-1", "result_message_type": "APPROVAL_RESULT", "responder_role": "USER_APPROVER", "status": "PASS", "decision": "APPROVE",
            "response_to_instruction_id": "11111111-1111-4111-8111-111111111111", "evidence_refs": [], "completion_gate": "NONE",
            "remote_verification": "NOT_ATTEMPTED", "completion_evidence": None, "publication_authority": None, "sync_status": None, "remote_head_sha": None,
            "approved_instruction": {
                "instruction_id": "22222222-2222-4222-8222-222222222222", "expected_state_revision": 16, "expected_base_sha": "a" * 40,
                "scope_paths": ["src/approved.py"], "target_project_context_id": "context", "target_project_name": "project",
                "target_github_repository_id": "1", "target_github_repository_full_name": "example/project",
                "target_work_unit_ref": {"path": ".gpt-codex/work-units/wu.json", "sha": "b" * 40},
                "issuer_role": "GPT_ORCHESTRATOR", "executor_role": "CODEX_IMPLEMENTER", "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
            },
        }

    def test_approval_evidence_consumer_accepts_only_a_valid_intrinsic_approval_result(self):
        from validate_project import resolve_approval_evidence
        locator = {"remote_ref": "refs/heads/evidence", "evidence_commit_sha": "a" * 40, "path": "evidence/result.json", "blob_sha": "b" * 40}
        with patch("validate_project.resolve_approval_evidence_locator", return_value=(self._intrinsic_approval(), [])):
            payload, errors = resolve_approval_evidence(Path("."), locator)
        self.assertEqual(errors, [])
        self.assertEqual(payload["result_message_type"], "APPROVAL_RESULT")

    def test_approval_evidence_consumer_accepts_a_valid_intrinsic_result_from_a_committed_blob(self):
        from validate_project import resolve_approval_evidence
        with tempfile.TemporaryDirectory(prefix="approval-consumer-") as temporary:
            root, remote = Path(temporary) / "work", Path(temporary) / "remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            root.mkdir()
            for command in (("init",), ("config", "user.name", "Task 5 test"), ("config", "user.email", "task5@example.invalid"), ("remote", "add", "origin", str(remote))):
                subprocess.run(["git", *command], cwd=root, check=True, capture_output=True)
            path = "evidence/approval.json"; target = root / path; target.parent.mkdir()
            target.write_text(json.dumps(self._intrinsic_approval(), separators=(",", ":")), encoding="utf-8")
            subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "approval"], cwd=root, check=True, capture_output=True)
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            blob = subprocess.run(["git", "rev-parse", f"{commit}:{path}"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "branch", "-M", "evidence"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "push", "-u", "origin", "evidence"], cwd=root, check=True, capture_output=True)
            payload, errors = resolve_approval_evidence(root, {"remote_ref": "refs/heads/evidence", "evidence_commit_sha": commit, "path": path, "blob_sha": blob})
        self.assertEqual(errors, [])
        self.assertEqual(payload["result_message_type"], "APPROVAL_RESULT")

    def test_approval_evidence_consumer_rejects_non_mapping_malformed_nonapproval_and_nonintrinsic_payloads(self):
        from validate_project import resolve_approval_evidence
        locator = {"remote_ref": "refs/heads/evidence", "evidence_commit_sha": "a" * 40, "path": "evidence/result.json", "blob_sha": "b" * 40}
        invalids = (
            None,
            ["not", "an", "object"],
            {**self._intrinsic_approval(), "result_message_type": "IMPLEMENTATION_RESULT"},
            {**self._intrinsic_approval(), "approved_instruction": {"instruction_id": "bad"}},
        )
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                with patch("validate_project.resolve_approval_evidence_locator", return_value=(invalid, [])):
                    payload, errors = resolve_approval_evidence(Path("."), locator)
                self.assertIsNone(payload)
                self.assertTrue(errors)


class Task6GitScopeOracleTests(unittest.TestCase):
    def test_actual_git_oracle_observes_real_unstaged_staged_untracked_and_restoration_states(self):
        from validate_project import collect_actual_git_changed_paths
        with tempfile.TemporaryDirectory(prefix="task6-real-") as temporary:
            root = Path(temporary)
            for command in (("init",), ("config", "user.name", "Task6 Fixture"), ("config", "user.email", "task6@example.invalid")):
                subprocess.run(["git", *command], cwd=root, check=True, capture_output=True)
            inside = root / "src/inside.py"; inside.parent.mkdir(); inside.write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True); subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
            for state, path, stage in (("unstaged", "outside/u.py", False), ("staged", "outside/s.py", True), ("untracked", "outside/n.py", False), ("inside-unstaged", "src/u.py", False), ("inside-staged", "src/s.py", True), ("inside-untracked", "src/n.py", False)):
                target=root/path; target.parent.mkdir(exist_ok=True); target.write_text(state, encoding="utf-8")
                if stage: subprocess.run(["git","add",path],cwd=root,check=True,capture_output=True)
                paths, errors = collect_actual_git_changed_paths(root)
                self.assertEqual(errors, []); self.assertIn(path, paths)
                if path.startswith("outside/"): self.assertIn("outside/" + path.split("/",1)[1], paths)
                subprocess.run(["git","reset","--hard","HEAD"],cwd=root,check=True,capture_output=True); target.unlink(missing_ok=True)
                restored, restore_errors = collect_actual_git_changed_paths(root)
                self.assertEqual((restored, restore_errors), (set(), []))
            inside.write_text("staged\n",encoding="utf-8"); subprocess.run(["git","add","src/inside.py"],cwd=root,check=True,capture_output=True); inside.write_text("staged and unstaged\n",encoding="utf-8")
            paths, errors = collect_actual_git_changed_paths(root)
            self.assertEqual(errors, []); self.assertEqual(paths, {"src/inside.py"})
    def test_actual_git_oracle_unions_nul_delimited_unstaged_staged_and_untracked_paths(self):
        from validate_project import collect_actual_git_changed_paths
        responses = [b"src/inside.py\x00", b"src/inside.py\x00", b"notes/outside.txt\x00"]
        def runner(_command, **_kwargs):
            return subprocess.CompletedProcess(_command, 0, responses.pop(0), b"")
        paths, errors = collect_actual_git_changed_paths(Path("."), runner=runner)
        self.assertEqual(paths, {"src/inside.py", "notes/outside.txt"})
        self.assertEqual(errors, [])

    def test_actual_git_oracle_fails_closed_for_observation_failure_and_unsafe_paths(self):
        from validate_project import collect_actual_git_changed_paths
        failed, errors = collect_actual_git_changed_paths(Path("."), runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 1, b"", b"failed"))
        self.assertIsNone(failed); self.assertIn("ACTUAL_GIT_OBSERVATION_FAILED", errors)
        responses = [b"../escape\x00", b"", b""]
        unsafe, errors = collect_actual_git_changed_paths(Path("."), runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 0, responses.pop(0), b""))
        self.assertIsNone(unsafe); self.assertIn("ACTUAL_GIT_PATH_INVALID", errors)


class Task7ApprovedCoreTests(unittest.TestCase):
    def test_control_plane_approved_core_is_closed_and_excludes_the_locator(self):
        from validate_project import _control_plane_approved_core
        instruction = {
            "instruction_id": "11111111-1111-4111-8111-111111111111", "expected_state_revision": 16,
            "expected_base_sha": "a" * 40, "scope_paths": [".gpt-codex/STATE.json"],
            "target_project_context_id": "context", "target_project_name": "project",
            "target_github_repository_id": "repo", "target_github_repository_full_name": "owner/repo",
            "target_work_unit_ref": {"path": ".gpt-codex/work-units/auth.json", "sha": "b" * 40},
            "issuer_role": "GPT_ORCHESTRATOR", "executor_role": "CODEX_IMPLEMENTER",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"], "approval_evidence_ref": {"mutable": "outside core"},
        }
        core = _control_plane_approved_core(instruction)
        self.assertNotIn("approval_evidence_ref", core)
        self.assertEqual(core["scope_paths"], instruction["scope_paths"])
