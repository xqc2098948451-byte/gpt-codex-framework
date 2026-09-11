import hashlib
import json
import shutil
import sys
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from release_framework import (
    artifact_basename,
    clean_output_dir,
    package_release,
    read_version,
    should_exclude,
)


ROOT = Path(__file__).resolve().parents[2]
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _fresh_release_fixture(tmp: str) -> Path:
    root = Path(tmp) / "framework"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git"))
    tests = root / ".gpt-codex" / "tests"
    shutil.rmtree(tests)
    tests.mkdir(parents=True)
    (tests / "test_smoke.py").write_text(
        "import unittest\n\nclass SmokeTests(unittest.TestCase):\n    def test_smoke(self):\n        pass\n",
        encoding="utf-8",
    )
    manifest_path = root / ".gpt-codex" / "release" / "consumer-projection-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["paths"][".gpt-codex/tests/test_smoke.py"] = "MANAGEMENT_ONLY"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return root


def _run_fresh_release(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(root / ".gpt-codex" / "scripts" / "release_framework.py"),
            "--root",
            str(root),
            "--output-dir",
            str(root / "dist"),
        ],
        capture_output=True,
        text=True,
    )


def _current_sha_fields(root: Path) -> tuple[str, str, str, str, str]:
    artifact = root / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-bootstrap.zip"
    actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
    sidecar = (artifact.with_name(artifact.name + ".sha256")).read_text(encoding="utf-8").split()[0]
    release_json = json.loads(
        (root / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-release.json").read_text(encoding="utf-8")
    )
    record = json.loads((root / "releases" / "records" / f"v{CURRENT_VERSION}.json").read_text(encoding="utf-8"))
    index = json.loads((root / "releases" / "INDEX.json").read_text(encoding="utf-8"))
    entry = next(item for item in index["releases"] if item["version"] == CURRENT_VERSION)
    return actual, sidecar, release_json["sha256"], record["artifact_sha256"], entry["artifact_sha256"]


class ReleasePackagingTests(unittest.TestCase):
    def test_fresh_release_preserves_final_index_artifact_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fresh_release_fixture(tmp)
            result = _run_fresh_release(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            fields = _current_sha_fields(root)
            self.assertEqual(fields, (fields[0], fields[0], fields[0], fields[0], fields[0]))

    def test_release_generation_is_metadata_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fresh_release_fixture(tmp)
            first = _run_fresh_release(root)
            first_metadata = _current_sha_fields(root)
            second = _run_fresh_release(root)
            second_metadata = _current_sha_fields(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(first_metadata, second_metadata)
            self.assertEqual(len(set(second_metadata)), 1)

    def test_all_current_release_sha_fields_agree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fresh_release_fixture(tmp)
            result = _run_fresh_release(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            fields = _current_sha_fields(root)
            self.assertEqual(len(set(fields)), 1, fields)

    def test_package_release_uses_consumer_projection_boundary(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as output:
            result = package_release(
                root=root,
                output_dir=Path(output),
                kernel_version="2.0.0",
                schema_version=1,
                validation_summary={"framework": "PASS", "tests": "PASS"},
            )
            with zipfile.ZipFile(result["zip_path"]) as archive:
                names = set(archive.namelist())
                payload = b"".join(archive.read(name) for name in names)
            self.assertFalse(any("docs/superpowers/" in name for name in names))
            self.assertNotIn(b"cb1e0450-df32-4ff6-8a33-35187b69a866", payload)
            self.assertNotIn(b"1366213495", payload)
            self.assertFalse(any(name.endswith("/.gpt-codex/CONTROL.json") for name in names))
            self.assertFalse(any(name.endswith("/.gpt-codex/STATE.json") for name in names))

    def test_management_control_is_excluded_but_generic_control_template_is_included(self):
        self.assertTrue(should_exclude(Path(".gpt-codex/CONTROL.json")))
        self.assertFalse(should_exclude(Path(".gpt-codex/project-template/CONTROL.template.json")))

    def test_management_state_evidence_and_root_gitignore_are_excluded(self):
        self.assertTrue(should_exclude(Path(".gpt-codex/STATE.json")))
        self.assertTrue(should_exclude(Path(".gpt-codex/evidence/results/result.json")))
        self.assertTrue(should_exclude(Path(".gitignore")))
        self.assertFalse(should_exclude(Path(".gpt-codex/project-template/evidence/.gitkeep")))

    def test_version_is_read_from_single_version_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "VERSION").write_text("2.0.1\n", encoding="utf-8")
            self.assertEqual(read_version(root), "2.0.1")
            self.assertEqual(artifact_basename("2.0.1"), "gpt-codex-framework-v2.0.1-bootstrap")

    def test_release_hygiene_excludes_transient_and_old_release_files(self):
        excluded = [
            Path(".git/config"),
            Path("dist/old.zip"),
            Path("pkg/__pycache__/x.pyc"),
            Path(".pytest_cache/state"),
            Path(".DS_Store"),
            Path("old-release.zip"),
            Path("old-release.zip.sha256"),
        ]
        for path in excluded:
            with self.subTest(path=path):
                self.assertTrue(should_exclude(path))
        self.assertFalse(should_exclude(Path(".gpt-codex/KERNEL.md")))

    def test_release_hygiene_excludes_nested_versioned_framework_source_copy(self):
        self.assertTrue(
            should_exclude(Path("gpt-codex-framework-v2.0.2-bootstrap/.gpt-codex/KERNEL.md"))
        )

    def test_clean_output_dir_removes_previous_release_outputs_only(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            for name in [
                "gpt-codex-framework-v2.0.0-bootstrap.zip",
                "gpt-codex-framework-v2.0.0-bootstrap.zip.sha256",
                "gpt-codex-framework-v2.0.0-release.json",
            ]:
                (out / name).write_text("old", encoding="utf-8")
            (out / "keep.txt").write_text("keep", encoding="utf-8")
            clean_output_dir(out)
            self.assertFalse(any(out.glob("gpt-codex-framework-v*-bootstrap.zip")))
            self.assertFalse(any(out.glob("gpt-codex-framework-v*-bootstrap.zip.sha256")))
            self.assertFalse(any(out.glob("gpt-codex-framework-v*-release.json")))
            self.assertTrue((out / "keep.txt").exists())

    def test_package_release_creates_clean_versioned_zip_hash_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "framework"
            root.mkdir()
            (root / "VERSION").write_text("2.0.1\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("framework\n", encoding="utf-8")
            (root / ".gpt-codex").mkdir()
            (root / ".gpt-codex" / "KERNEL.md").write_text("kernel\n", encoding="utf-8")
            (root / ".gpt-codex" / "release").mkdir()
            (root / ".gpt-codex" / "release" / "consumer-projection-manifest.json").write_text(
                json.dumps({
                    "manifest_version": 1,
                    "framework_version": "2.0.1",
                    "projection": "CONSUMER_BOOTSTRAP",
                    "paths": {
                        "VERSION": "CONSUMER_REQUIRED",
                        "AGENTS.md": "CONSUMER_REQUIRED",
                        ".gpt-codex/KERNEL.md": "CONSUMER_REQUIRED",
                        ".gpt-codex/release/consumer-projection-manifest.json": "MANAGEMENT_ONLY",
                        "dist/old.zip": "GENERATED_ARTIFACT",
                    },
                }),
                encoding="utf-8",
            )
            (root / "dist").mkdir()
            (root / "dist" / "old.zip").write_bytes(b"old")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "x.pyc").write_bytes(b"cache")

            out = Path(td) / "out"
            result = package_release(
                root=root,
                output_dir=out,
                kernel_version="2.0.0",
                schema_version=1,
                validation_summary={"framework": "PASS", "tests": "PASS"},
            )

            zip_path = Path(result["zip_path"])
            sha_path = Path(result["sha256_path"])
            manifest_path = Path(result["manifest_path"])
            self.assertTrue(zip_path.is_file())
            self.assertTrue(sha_path.is_file())
            self.assertTrue(manifest_path.is_file())

            expected_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()
            self.assertEqual(result["sha256"], expected_hash)
            self.assertIn(expected_hash, sha_path.read_text(encoding="utf-8"))

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["framework_version"], "2.0.1")
            self.assertEqual(manifest["kernel_version"], "2.0.0")
            self.assertEqual(manifest["validation"]["framework"], "PASS")
            self.assertEqual(manifest["validation"]["tests"], "PASS")
            self.assertEqual(manifest["validation"]["zip_integrity"], "PASS")
            self.assertEqual(manifest["validation"]["release_hygiene"], "PASS")

            prefix = "gpt-codex-framework-v2.0.1-bootstrap/"
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                self.assertTrue(names)
                self.assertTrue(all(name.startswith(prefix) for name in names))
                self.assertIn(prefix + "VERSION", names)
                self.assertIn(prefix + ".gpt-codex/KERNEL.md", names)
                self.assertFalse(any("__pycache__" in name for name in names))
                self.assertFalse(any("/dist/" in name for name in names))
                self.assertFalse(any(name.endswith("old-release.zip") for name in names))
                self.assertIsNone(zf.testzip())


if __name__ == "__main__":
    unittest.main()
