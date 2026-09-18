import json
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


class VersionConsistencyTests(unittest.TestCase):
    def test_current_release_artifact_metadata_is_consistent_with_retention_policy(self):
        artifact = ROOT / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-bootstrap.zip"
        record = json.loads((ROOT / "releases" / "records" / f"v{CURRENT_VERSION}.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "releases" / "INDEX.json").read_text(encoding="utf-8"))
        index_entry = next(entry for entry in index["releases"] if entry["version"] == CURRENT_VERSION)

        self.assertRegex(record["artifact_sha256"], r"^[0-9a-f]{64}$")
        self.assertIsInstance(record["artifact_size_bytes"], int)
        self.assertGreater(record["artifact_size_bytes"], 0)
        self.assertEqual(record["artifact_sha256"], index_entry["artifact_sha256"])
        if artifact.is_file():
            expected_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertEqual(expected_sha, record["artifact_sha256"])
            self.assertEqual(artifact.stat().st_size, record["artifact_size_bytes"])
            sidecar = artifact.with_name(artifact.name + ".sha256")
            manifest = artifact.with_name(f"gpt-codex-framework-v{CURRENT_VERSION}-release.json")
            if sidecar.is_file():
                self.assertEqual(expected_sha, sidecar.read_text(encoding="utf-8").split()[0])
            if manifest.is_file():
                self.assertEqual(expected_sha, json.loads(manifest.read_text(encoding="utf-8"))["sha256"])
        else:
            self.assertEqual(record["archive_policy"], "METADATA_ONLY")
            self.assertEqual(record["artifact_hash_location"], "EXTERNAL_RELEASE_SIDECAR")

    def test_current_framework_source_version_is_consistent(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        catalog = json.loads((ROOT / ".gpt-codex" / "builtins" / "INDEX.json").read_text(encoding="utf-8"))
        registry = json.loads((ROOT / ".gpt-codex" / "framework-modules" / "REGISTRY.json").read_text(encoding="utf-8"))

        self.assertEqual(version, CURRENT_VERSION)
        self.assertEqual(catalog["framework_version"], CURRENT_VERSION)
        self.assertEqual(registry["framework_version"], CURRENT_VERSION)

    def test_current_release_metadata_is_consistent(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        record = json.loads((ROOT / "releases" / "records" / f"v{CURRENT_VERSION}.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "releases" / "INDEX.json").read_text(encoding="utf-8"))
        versions = [entry["version"] for entry in index["releases"]]
        current_position = versions.index(CURRENT_VERSION)

        self.assertEqual(version, CURRENT_VERSION)
        self.assertEqual(record["version"], CURRENT_VERSION)
        self.assertGreater(current_position, 0)
        self.assertEqual(record["previous_version"], versions[current_position - 1])
        self.assertEqual(record["kernel_version"], "2.0.0")
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(index["latest_recorded_version"], CURRENT_VERSION)
        self.assertEqual(versions[-1], CURRENT_VERSION)

    def test_current_docs_and_changelog_name_current_release(self):
        changelog = (ROOT / ".gpt-codex" / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        release_entry = changelog.split("## v2.7.1", 1)[0]
        self.assertIn(f"## v{CURRENT_VERSION}", release_entry)
        self.assertIn(f"Framework v{CURRENT_VERSION}", readme)
        self.assertIn(f"Framework v{CURRENT_VERSION}", bootstrap)
        self.assertIn(f"Framework v{CURRENT_VERSION}", agents)
        self.assertIn("publication/remote verification completed", release_entry)
        self.assertIn("SELF_MANAGED", readme)


if __name__ == "__main__":
    unittest.main()
