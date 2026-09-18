import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class GithubContinuityValidatorTests(unittest.TestCase):
    def test_git_decodes_unicode_controlled_remote_output_without_host_encoding_dependency(self):
        from github_repository_binding import _git

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(
                ["git", "remote", "add", "中文远程", "https://github.com/example/repository.git"],
                cwd=repository,
                check=True,
            )
            code, stdout, stderr = _git(repository, "remote")

        self.assertEqual(code, 0)
        self.assertEqual(stdout, "中文远程")
        self.assertEqual(stderr, "")

    def test_bounded_subprocess_diagnostic_preserves_safe_facts_and_never_argv_secret(self):
        from github_repository_binding import _run_bounded_diagnostic

        result = _run_bounded_diagnostic(
            ["tool", "token=DO_NOT_RETAIN_123"], "GIT_VERSION_PROBE",
            runner=lambda *_args, **_kwargs: type("P", (), {"returncode": 7, "stdout": "中文", "stderr": "error"})(),
        )
        self.assertTrue(result.process_started)
        self.assertEqual(result.exit_code, 7)
        self.assertEqual(result.stdout, "中文")
        self.assertEqual(result.stderr, "error")
        self.assertNotIn("DO_NOT_RETAIN_123", repr(result))

    def test_bounded_subprocess_diagnostic_handles_launch_timeout_and_truncation(self):
        from github_repository_binding import _run_bounded_diagnostic

        launch = _run_bounded_diagnostic(["tool"], "SAFE", runner=lambda *_a, **_k: (_ for _ in ()).throw(OSError("missing")))
        self.assertFalse(launch.process_started)
        self.assertIsNone(launch.exit_code)
        huge = _run_bounded_diagnostic(["tool"], "SAFE", runner=lambda *_a, **_k: type("P", (), {"returncode": 0, "stdout": "x" * 5000, "stderr": "y" * 5000})())
        self.assertTrue(huge.stdout_truncated)
        self.assertTrue(huge.stderr_truncated)

    def test_bounded_subprocess_diagnostic_preserves_timeout_partial_streams_and_empty_success_streams(self):
        from github_repository_binding import _run_bounded_diagnostic

        timeout = _run_bounded_diagnostic(
            ["tool"], "SAFE", runner=lambda *_a, **_k: (_ for _ in ()).throw(
                subprocess.TimeoutExpired(["tool"], 1, output="partial-out", stderr="partial-err")
            )
        )
        self.assertTrue(timeout.process_started)
        self.assertIsNone(timeout.exit_code)
        self.assertEqual(timeout.completion, "INCOMPLETE")
        self.assertEqual(timeout.stdout, "partial-out")
        self.assertEqual(timeout.stderr, "partial-err")
        empty = _run_bounded_diagnostic(
            ["tool"], "SAFE", runner=lambda *_a, **_k: type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        )
        self.assertTrue(empty.process_started)
        self.assertEqual(empty.exit_code, 0)
        self.assertEqual(empty.stdout, "")
        self.assertEqual(empty.stderr, "")
        self.assertFalse(empty.stdout_truncated)
        self.assertFalse(empty.stderr_truncated)
    def test_execution_capability_observation_uses_injected_discovery_and_supports_pwsh_7(self):
        from github_repository_binding import observe_execution_capabilities

        locations = {"pwsh": "runtime/pwsh", "python": "runtime/python", "git": "runtime/git", "gh": None}
        probes = {
            "runtime/pwsh": (0, "PowerShell 7.4.1", "secret-token"),
            "runtime/python": (0, "Python 3.12.0", ""),
            "runtime/git": (0, "git version 2.45.0", ""),
        }
        observed = observe_execution_capabilities(
            executable_lookup=locations.get,
            version_probe=lambda executable: probes[executable],
            remote_probe=lambda: True,
            path_probe=lambda _path: True,
        )
        self.assertEqual(observed["powershell"]["status"], "SUPPORTED")
        self.assertEqual(observed["python"]["status"], "AVAILABLE")
        self.assertEqual(observed["git"]["status"], "AVAILABLE")
        self.assertEqual(observed["gh"]["status"], "ABSENT")
        self.assertTrue(observed["remote"]["available"])
        self.assertNotIn("secret-token", repr(observed))

    def test_execution_capability_observation_distinguishes_missing_and_legacy_powershell(self):
        from github_repository_binding import observe_execution_capabilities

        missing = observe_execution_capabilities(
            executable_lookup=lambda _name: None,
            version_probe=lambda _executable: (0, "", ""),
            remote_probe=lambda: False,
            path_probe=lambda _path: True,
        )
        self.assertEqual(missing["powershell"]["status"], "UNAVAILABLE")
        legacy = observe_execution_capabilities(
            executable_lookup=lambda name: {"pwsh": "shell", "python": "py", "git": "git"}.get(name),
            version_probe=lambda executable: (0, "Windows PowerShell 5.1" if executable == "shell" else "ok", ""),
            remote_probe=lambda: True,
            path_probe=lambda _path: True,
        )
        self.assertEqual(legacy["powershell"]["status"], "UNSUPPORTED")

    def test_execution_capability_observation_round_trips_real_chinese_path_without_environment_capture(self):
        from github_repository_binding import observe_execution_capabilities

        with tempfile.TemporaryDirectory() as temporary:
            chinese_path = Path(temporary) / "中文路径"
            chinese_path.mkdir()
            observed = observe_execution_capabilities(
                executable_lookup=lambda name: {"pwsh": "pwsh", "python": "python", "git": "git"}.get(name),
                version_probe=lambda executable: (0, {"pwsh": "PowerShell 7.4", "python": "Python 3.12", "git": "git version 2"}[executable], ""),
                remote_probe=lambda: True,
                path=chinese_path,
            )
        self.assertTrue(observed["unicode_path_round_trip"])
        self.assertNotIn("environment", observed)

    def test_execution_capability_observation_fails_closed_for_malformed_path_probe(self):
        from github_repository_binding import observe_execution_capabilities

        observed = observe_execution_capabilities(
            executable_lookup=lambda name: {"pwsh": "pwsh", "python": "python", "git": "git"}.get(name),
            version_probe=lambda executable: (0, {"pwsh": "PowerShell 7.4", "python": "Python 3.12", "git": "git version 2"}[executable], ""),
            remote_probe=lambda: True,
            path=object(),
        )
        self.assertFalse(observed["unicode_path_round_trip"])

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
