import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class VersionConsistencyTests(unittest.TestCase):
    def test_current_framework_release_metadata_is_v221(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        catalog = json.loads((ROOT / ".gpt-codex" / "builtins" / "INDEX.json").read_text(encoding="utf-8"))
        record = json.loads((ROOT / "releases" / "records" / "v2.2.1.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "releases" / "INDEX.json").read_text(encoding="utf-8"))

        self.assertEqual(version, "2.2.1")
        self.assertEqual(catalog["framework_version"], "2.2.1")
        self.assertEqual(record["version"], "2.2.1")
        self.assertEqual(record["kernel_version"], "2.0.0")
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(index["latest_recorded_version"], "2.2.1")
        self.assertIn("2.2.1", {entry["version"] for entry in index["releases"]})
        self.assertIn("2.2.0", {entry["version"] for entry in index["releases"]})
        self.assertIn("2.0.3", {entry["version"] for entry in index["releases"]})

    def test_current_docs_and_changelog_name_v221(self):
        changelog = (ROOT / ".gpt-codex" / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("## v2.2.1", changelog)
        self.assertIn("Framework v2.2.1", readme)
        self.assertIn("Framework v2.2.1", bootstrap)
        self.assertIn("Framework v2.2.1", agents)
        self.assertIn("PUBLICATION_CANDIDATE_ONLY", changelog)
        self.assertIn("SELF_MANAGED", readme)


if __name__ == "__main__":
    unittest.main()
