import sys
import tempfile
import unittest
from pathlib import Path

from test_context_window_resume import GovernedProjectFixture


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))


class MaintenanceNavigationFlowTests(unittest.TestCase):
    def test_map_hit_keeps_normal_maintenance_out_of_repository_rediscovery(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))

            result = load_continuity_resume(
                fixture.root, "repo-a", candidate_module_ids=["auth"]
            )

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [])

    def test_map_partial_reads_only_the_affected_module_map(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))

            result = load_continuity_resume(
                fixture.root,
                "repo-a",
                changed_paths=["src/auth/session.ts"],
                candidate_module_ids=["auth", "billing"],
            )

            self.assertEqual(result["map_route"], "MAP_PARTIAL")
            self.assertEqual(result["resume_mode"], "DELTA_RESUME")
            self.assertEqual(result["stale_modules"], ["auth"])
            required_reads = result["required_reads"]
            self.assertEqual(
                required_reads,
                [
                    "src/auth/session.ts",
                    ".gpt-codex/navigation/modules/auth.json",
                ],
            )
            self.assertEqual(result["module_map_reads"], [".gpt-codex/navigation/modules/auth.json"])
            for forbidden_read in (
                ".gpt-codex/PROJECT.md",
                ".gpt-codex/navigation/PROJECT_MAP.json",
                ".gpt-codex/navigation/modules/billing.json",
                "docs/unrelated.md",
                ".gpt-codex/builtins/skills/repository-discovery/SKILL.md",
                ".gpt-codex/builtins/skills/repository-discovery/manifest.json",
            ):
                with self.subTest(forbidden_read=forbidden_read):
                    self.assertNotIn(forbidden_read, required_reads)
            self.assertNotIn("billing", result["stale_modules"])

    def test_unrelated_git_delta_keeps_candidates_fresh_without_extra_reads(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))

            result = load_continuity_resume(
                fixture.root,
                "repo-a",
                changed_paths=["docs/architecture.md"],
                candidate_module_ids=["auth", "billing"],
            )

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["resume_mode"], "FAST_RESUME")
            self.assertEqual(result["stale_modules"], [])
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [])

    def test_map_miss_limits_follow_up_to_scoped_discovery_route(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))

            result = load_continuity_resume(
                fixture.root, "repo-a", candidate_module_ids=["search"]
            )

            self.assertEqual(result["map_route"], "MAP_MISS")
            self.assertEqual(result["candidate_modules"], [])
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [])

    def test_map_missing_remains_a_governed_cold_resume_not_bootstrap(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory), with_map=False)

            result = load_continuity_resume(fixture.root, "repo-a")

            self.assertEqual(result["status"], "LATEST_SYNCED_REMOTE_STATE")
            self.assertEqual(result["map_route"], "MAP_MISSING")
            self.assertEqual(result["resume_mode"], "COLD_RESUME")
            self.assertNotEqual(result["resume_mode"], "BOOTSTRAP")


if __name__ == "__main__":
    unittest.main()
