import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class MaintenanceNavigationContractTests(unittest.TestCase):
    def test_bootstrap_prompt_is_map_first_for_maintenance(self):
        text = (ROOT / ".gpt-codex/BOOTSTRAP_PROMPT.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "A context-window transition is not a project bootstrap.",
            "A maintenance request is not a repository rediscovery.",
            "Do not scan the repository when the Project Map can identify the candidate module.",
            "Do not run repository discovery when a valid resume checkpoint exists.",
            "MAP_HIT",
            "MAP_PARTIAL",
            "MAP_MISS",
            "MAP_MISSING",
            "FAST_RESUME",
            "DELTA_RESUME",
            "COLD_RESUME",
        ):
            self.assertIn(phrase, text)

    def test_repository_discovery_stays_read_only(self):
        manifest = json.loads(
            (
                ROOT
                / ".gpt-codex/builtins/skills/repository-discovery/manifest.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], "1.1.0")
        self.assertEqual(manifest["permissions"]["project_read"], "ALLOW")
        self.assertEqual(manifest["permissions"]["project_write"], "DENY")


if __name__ == "__main__":
    unittest.main()
