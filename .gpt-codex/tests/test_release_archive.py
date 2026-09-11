import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from release_archive import (
    archive_release_artifact,
    ensure_release_record,
    load_release_index,
)


class ReleaseArchiveTests(unittest.TestCase):
    def test_archive_records_zip_metadata_without_copying_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "framework"
            releases = root / "releases"
            releases.mkdir(parents=True)
            artifact = Path(td) / "gpt-codex-framework-v1.7-bootstrap.zip"
            with zipfile.ZipFile(artifact, "w") as zf:
                zf.writestr("gpt-codex-framework-v1.7-bootstrap/AGENTS.md", "x")

            record = archive_release_artifact(artifact, releases)

            self.assertEqual(record["version"], "1.7")
            self.assertEqual(record["artifact"], artifact.name)
            self.assertRegex(record["artifact_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(record["archive_policy"], "METADATA_ONLY")
            self.assertFalse((releases / artifact.name).exists())
            self.assertTrue((releases / "records" / "v1.7.json").is_file())
            index = load_release_index(releases)
            self.assertIn("1.7", [item["version"] for item in index["releases"]])

    def test_archive_rejects_corrupt_zip(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            artifact = Path(td) / "gpt-codex-framework-v1.2-bootstrap.zip"
            artifact.write_bytes(b"not-a-zip")
            with self.assertRaises(ValueError):
                archive_release_artifact(artifact, releases)
            self.assertFalse((releases / "records" / "v1.2.json").exists())

    def test_current_release_record_can_be_embedded_without_self_hash(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            record = ensure_release_record(
                releases_dir=releases,
                version="2.0.2",
                kernel_version="2.0.0",
                schema_version=1,
                previous_version="2.0.1",
            )
            self.assertEqual(record["version"], "2.0.2")
            self.assertEqual(record["previous_version"], "2.0.1")
            self.assertIsNone(record["artifact_sha256"])
            self.assertEqual(record["artifact_hash_location"], "EXTERNAL_RELEASE_SIDECAR")
            index = load_release_index(releases)
            self.assertEqual(index["latest_recorded_version"], "2.0.2")

    def test_current_release_record_preserves_corrective_publication_fields(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            record_dir = releases / "records"
            record_dir.mkdir(parents=True)
            (record_dir / "v2.2.1.json").write_text(json.dumps({
                "version": "2.2.1",
                "publication_policy": "CONFIRMED_BASELINE_ONLY",
                "github_write_performed": "NO",
            }), encoding="utf-8")
            record = ensure_release_record(
                releases_dir=releases,
                version="2.2.1",
                kernel_version="2.0.0",
                schema_version=1,
                previous_version="2.2.0",
            )
            self.assertEqual(record["publication_policy"], "CONFIRMED_BASELINE_ONLY")
            self.assertEqual(record["github_write_performed"], "NO")


if __name__ == "__main__":
    unittest.main()
