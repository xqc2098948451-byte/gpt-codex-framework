import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from validate_project import (
    validate_project_identity_and_derived,
    validate_project_identity_boundary,
)
from context_binding import (
    evaluate_cross_project_resource_boundary,
    load_project_identity,
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


if __name__ == "__main__":
    unittest.main()
