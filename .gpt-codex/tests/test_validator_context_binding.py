import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from validate_project import validate_project_identity_boundary


class ValidatorContextBindingTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
