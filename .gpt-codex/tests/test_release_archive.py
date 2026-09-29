import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from release_archive import (
    _version_key,
    archive_release_artifact,
    ensure_release_record,
    load_release_index,
)


class ReleaseArchiveTests(unittest.TestCase):
    def test_archive_accepts_legacy_current_suffix_and_build_names(self):
        versions = (
            "1.7", "1.7.0", "2.7.4-local.1", "2.7.4+build.1",
            "2.7.4-local.1+build.1", "2.7.4-01", "2.7.4-a..b", "2.7.4+..",
        )
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            for version in versions:
                with self.subTest(version=version):
                    artifact = Path(td) / f"gpt-codex-framework-v{version}-bootstrap.zip"
                    with zipfile.ZipFile(artifact, "w") as zf:
                        zf.writestr("AGENTS.md", "x")
                    record = archive_release_artifact(artifact, releases)
                    self.assertEqual(record["version"], version)
                    self.assertEqual(record["artifact"], artifact.name)

    def test_archive_rejects_currently_invalid_version_names(self):
        invalid = (
            "02.7.4", "2.07.4", "2.7.04", "2..4", "2.7.", "2.7.4.1",
            "2.7.4-", "2.7.4+", "2.7.4-foo_1", "non-semver", "2", "",
        )
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            for version in invalid:
                with self.subTest(version=version):
                    artifact = Path(td) / f"gpt-codex-framework-v{version}-bootstrap.zip"
                    with self.assertRaises(ValueError):
                        archive_release_artifact(artifact, releases)

    def test_version_key_preserves_legacy_patch_prerelease_and_build_order(self):
        ordered = (
            "1.7", "1.7.0", "2.2.1", "2.2.2-local.1", "2.2.2", "2.3.0",
        )
        keys = [_version_key(version) for version in ordered]
        self.assertEqual(keys[0], keys[1])
        self.assertEqual(keys, sorted(keys))
        self.assertLess(_version_key("2.7.4-local.2"), _version_key("2.7.4-local.10"))
        self.assertLess(_version_key("2.7.4-alpha"), _version_key("2.7.4-beta"))
        self.assertLess(_version_key("2.7.4-01"), _version_key("2.7.4"))
        self.assertEqual(_version_key("2.7.4+build.1"), _version_key("2.7.4+build.2"))
        self.assertEqual(_version_key("2.7.4-a..b"), _version_key("2.7.4-a..b+.."))

    def test_version_key_rejects_currently_invalid_forms(self):
        for version in (
            "02.7.4", "2.07.4", "2.7.04", "2..4", "2.7.", "2.7.4.1",
            "2.7.4-", "2.7.4+", "2.7.4-foo_1", "non-semver", "2", "",
        ):
            with self.subTest(version=version), self.assertRaises(ValueError):
                _version_key(version)

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

    def test_release_archive_writes_canonical_lf_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            ensure_release_record(
                releases_dir=releases,
                version="2.0.2",
                kernel_version="2.0.0",
                schema_version=1,
                previous_version="2.0.1",
            )

            for path in (releases / "INDEX.json", releases / "records" / "v2.0.2.json"):
                with self.subTest(path=path):
                    content = path.read_bytes()
                    content.decode("utf-8")
                    self.assertTrue(content.endswith(b"\n"))
                    self.assertNotIn(b"\r\n", content)

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

    def test_release_index_sorts_local_corrective_semver(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            record = ensure_release_record(
                releases_dir=releases,
                version="2.2.2-local.1",
                kernel_version="2.0.0",
                schema_version=1,
                previous_version="2.2.1",
            )
            self.assertEqual(record["version"], "2.2.2-local.1")
            index = load_release_index(releases)
            self.assertEqual(index["latest_recorded_version"], "2.2.2-local.1")


if __name__ == "__main__":
    unittest.main()
