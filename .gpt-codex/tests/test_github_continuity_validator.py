import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GithubContinuityValidatorTests(unittest.TestCase):
    def test_framework_management_project_validates_after_migration(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_project.py"), str(ROOT.parent)],
            cwd=ROOT.parent,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_guardrail_and_skill_are_cataloged(self):
        guardrail = ROOT / "builtins" / "guardrails" / "github-repository-binding"
        skill = ROOT / "builtins" / "skills" / "github-project-continuity"
        self.assertTrue((guardrail / "GUARDRAIL.md").exists())
        self.assertTrue((guardrail / "manifest.json").exists())
        self.assertTrue((skill / "SKILL.md").exists())
        catalog = json.loads((ROOT / "builtins" / "INDEX.json").read_text(encoding="utf-8"))
        self.assertIn("github-repository-binding", catalog["optional"]["guardrails"])
        self.assertIn("github-project-continuity", catalog["optional"]["skills"])

    def test_control_github_has_no_remote_name(self):
        template = json.loads((ROOT / "project-template" / "CONTROL.template.json").read_text(encoding="utf-8"))
        self.assertNotIn("remote_name", template["github"])


if __name__ == "__main__":
    unittest.main()
