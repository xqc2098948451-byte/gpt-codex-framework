import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ValidatorContextBindingTests(unittest.TestCase):
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
