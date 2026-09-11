import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class GithubRepositoryBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.available = importlib.util.find_spec("github_repository_binding") is not None

    def test_binding_module_exists(self):
        self.assertTrue(self.available, "repository binding decision core is required")

    @unittest.skipUnless(importlib.util.find_spec("github_repository_binding"), "RED: module not implemented")
    def test_repository_id_is_authority_and_remote_name_is_local(self):
        from github_repository_binding import ObservedRepository, compare_repository_binding

        control = {"github": {"repository_id": "repo-1", "repository_full_name": "owner/project", "default_branch": "main"}}
        for remote_name in ("origin", "github", "upstream"):
            observed = ObservedRepository("repo-1", "owner/project", remote_name, "github:owner/project")
            decision = compare_repository_binding(control, observed)
            self.assertEqual(decision.decision, "ALLOW")
            self.assertTrue(decision.mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("github_repository_binding"), "RED: module not implemented")
    def test_foreign_repository_denies(self):
        from github_repository_binding import ObservedRepository, compare_repository_binding

        control = {"github": {"repository_id": "repo-1", "repository_full_name": "owner/project", "default_branch": "main"}}
        decision = compare_repository_binding(control, ObservedRepository("repo-2", "owner/project", "origin", "github:owner/project"))
        self.assertEqual(decision.reason, "GITHUB_REPOSITORY_MISMATCH")
        self.assertFalse(decision.mutation_allowed)

    @unittest.skipUnless(importlib.util.find_spec("github_repository_binding"), "RED: module not implemented")
    def test_missing_remote_name_in_control_is_valid(self):
        from github_repository_binding import ObservedRepository, compare_repository_binding

        control = {"github": {"repository_id": "repo-1", "repository_full_name": "old/project", "default_branch": "main"}}
        decision = compare_repository_binding(control, ObservedRepository("repo-1", "new/project", "upstream", "github:new/project"))
        self.assertEqual(decision.decision, "ALLOW")

    @unittest.skipUnless(importlib.util.find_spec("github_repository_binding"), "RED: module not implemented")
    def test_canonicalize_https_and_ssh(self):
        from github_repository_binding import canonicalize_remote_url

        values = [
            "https://github.com/owner/project.git",
            "git@github.com:owner/project.git",
            "ssh://git@github.com/owner/project.git",
        ]
        self.assertEqual({canonicalize_remote_url(value) for value in values}, {"github:owner/project"})

    @unittest.skipUnless(importlib.util.find_spec("github_repository_binding"), "RED: module not implemented")
    def test_compatibility_scan_is_read_only_and_classified(self):
        from github_repository_binding import scan_repository_compatibility

        result = scan_repository_compatibility(Path.cwd(), {"repository_id": "repo-1", "repository_full_name": "owner/project"})
        self.assertIn(result["classification"], {
            "ALREADY_BOUND", "GITHUB_BINDING_REQUIRED", "LOCAL_GIT_ONLY",
            "REMOTE_UNBOUND", "MULTIPLE_REMOTE_REVIEW_REQUIRED", "NON_GITHUB_REMOTE",
            "REPOSITORY_CONFLICT",
        })
        self.assertFalse(result.get("mutated", False))


if __name__ == "__main__":
    unittest.main()
