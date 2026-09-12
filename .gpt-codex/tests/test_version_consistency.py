import json
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


class VersionConsistencyTests(unittest.TestCase):
    def test_current_v230_metadata_points_to_new_projection_sha(self):
        artifact = ROOT / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-bootstrap.zip"
        expected_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        sidecar_sha = (ROOT / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-bootstrap.zip.sha256").read_text(
            encoding="utf-8"
        ).split()[0]
        release_json = json.loads(
            (ROOT / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-release.json").read_text(encoding="utf-8")
        )
        record = json.loads((ROOT / "releases" / "records" / f"v{CURRENT_VERSION}.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "releases" / "INDEX.json").read_text(encoding="utf-8"))
        index_entry = next(entry for entry in index["releases"] if entry["version"] == CURRENT_VERSION)

        self.assertEqual(expected_sha, sidecar_sha)
        self.assertEqual(expected_sha, release_json["sha256"])
        self.assertEqual(expected_sha, record["artifact_sha256"])
        self.assertEqual(expected_sha, index_entry["artifact_sha256"])
        self.assertNotEqual(expected_sha, "02171f7984d7409ce945ebb26154f216ff63027bbc35fcf1d3d99ad8ff2806c6")

    def test_current_framework_release_metadata_is_v230(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        catalog = json.loads((ROOT / ".gpt-codex" / "builtins" / "INDEX.json").read_text(encoding="utf-8"))
        record = json.loads((ROOT / "releases" / "records" / f"v{CURRENT_VERSION}.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "releases" / "INDEX.json").read_text(encoding="utf-8"))

        self.assertEqual(version, "2.3.0")
        self.assertEqual(catalog["framework_version"], CURRENT_VERSION)
        self.assertEqual(record["version"], CURRENT_VERSION)
        self.assertEqual(record["kernel_version"], "2.0.0")
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(index["latest_recorded_version"], CURRENT_VERSION)
        self.assertIn(CURRENT_VERSION, {entry["version"] for entry in index["releases"]})
        self.assertIn("2.2.0", {entry["version"] for entry in index["releases"]})
        self.assertIn("2.0.3", {entry["version"] for entry in index["releases"]})

    def test_current_docs_and_changelog_name_v230(self):
        changelog = (ROOT / ".gpt-codex" / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("## v2.3.0", changelog)
        self.assertIn("Framework v2.3.0", readme)
        self.assertIn("Framework v2.3.0", bootstrap)
        self.assertIn("Framework v2.3.0", agents)
        self.assertIn("PUBLICATION_CANDIDATE_ONLY", changelog)
        self.assertIn("SELF_MANAGED", readme)


if __name__ == "__main__":
    unittest.main()
