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
    _previous_recorded_version,
    artifact_basename,
    clean_output_dir,
    evaluate_publication_preflight,
    finalize_release_manifest,
    materialize_verified_git_artifact,
    package_release,
    read_version,
    should_exclude,
    validate_release_fact_consistency,
)
from consumer_projection import stage_consumer_projection
from validate_project import validate_harness_root_separation


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
    def test_release_fact_consistency_requires_exact_candidate_metadata(self):
        facts = {
            "target_version": "2.7.2", "release_record_version": "2.7.2",
            "manifest_framework_version": "2.7.2", "artifact_sha256": "a" * 64,
            "release_record_artifact_sha256": "a" * 64, "artifact_size_bytes": 17,
            "release_record_artifact_size_bytes": 17, "candidate_sha": "b" * 40,
            "reviewed_sha": "b" * 40,
        }
        self.assertEqual(validate_release_fact_consistency(facts), [])
        for key, value, code in (
            ("release_record_version", "2.7.1", "VERSION_RELEASE_RECORD_MISMATCH"),
            ("manifest_framework_version", "2.7.1", "VERSION_MANIFEST_MISMATCH"),
            ("release_record_artifact_sha256", "c" * 64, "ARTIFACT_SHA_MISMATCH"),
            ("release_record_artifact_size_bytes", 18, "ARTIFACT_SIZE_MISMATCH"),
            ("reviewed_sha", "c" * 40, "CANDIDATE_REVIEW_SHA_MISMATCH"),
        ):
            with self.subTest(code=code):
                candidate = dict(facts, **{key: value})
                self.assertIn(code, validate_release_fact_consistency(candidate))
    def test_publication_preflight_returns_ordered_blockers_for_invalid_facts(self):
        facts = {
            "source_version": "2.7.0", "source_version_closed": True,
            "projection_closed": True,
            "release_record_ready": True,
            "canonical_lf_verified": True,
            "repository_identity_verified": True,
            "work_main_ancestry_verified": True,
            "tag_conflict": False,
            "release_conflict": False,
            "publication_mechanism_available": True,
            "canonical_artifact_ref": "a" * 40 + ":dist/gpt-codex-framework-v2.7.0-bootstrap.zip",
            "artifact_sha256": "b" * 64,
            "artifact_size_bytes": 1,
            "available_capabilities": {"TAG_WRITE", "RELEASE_WRITE", "ASSET_UPLOAD"},
        }
        self.assertEqual(evaluate_publication_preflight(facts), [])
        invalid = {**facts, "source_version_closed": False, "tag_conflict": True, "artifact_size_bytes": 0, "available_capabilities": {"RELEASE_WRITE"}}
        self.assertEqual(
            evaluate_publication_preflight(invalid),
            ["SOURCE_VERSION_NOT_CLOSED", "TAG_CONFLICT", "ARTIFACT_SIZE_INVALID", "MISSING_CAPABILITY_TAG_WRITE", "MISSING_CAPABILITY_ASSET_UPLOAD"],
        )

    def test_publication_preflight_fails_closed_for_missing_and_malformed_facts(self):
        codes = evaluate_publication_preflight({})
        self.assertEqual(codes[:9], [
            "SOURCE_VERSION_NOT_CLOSED", "PROJECTION_NOT_CLOSED", "RELEASE_RECORD_NOT_READY",
            "CANONICAL_LF_NOT_VERIFIED", "REPOSITORY_IDENTITY_NOT_VERIFIED", "WORK_MAIN_ANCESTRY_NOT_VERIFIED",
            "TAG_CONFLICT", "RELEASE_CONFLICT", "PUBLICATION_MECHANISM_UNAVAILABLE",
        ])
        self.assertIn("CANONICAL_ARTIFACT_REF_INVALID", codes)
        self.assertIn("ARTIFACT_SHA256_INVALID", codes)
        self.assertIn("ARTIFACT_SIZE_INVALID", codes)
        self.assertEqual(codes[-3:], ["MISSING_CAPABILITY_TAG_WRITE", "MISSING_CAPABILITY_RELEASE_WRITE", "MISSING_CAPABILITY_ASSET_UPLOAD"])

    def test_publication_preflight_validates_each_fact_boundary(self):
        facts = {
            "source_version": "2.7.0", "source_version_closed": True, "projection_closed": True, "release_record_ready": True,
            "canonical_lf_verified": True, "repository_identity_verified": True,
            "work_main_ancestry_verified": True, "tag_conflict": False, "release_conflict": False,
            "publication_mechanism_available": True,
            "canonical_artifact_ref": "a" * 40 + ":dist/gpt-codex-framework-v2.7.0-bootstrap.zip",
            "artifact_sha256": "b" * 64, "artifact_size_bytes": 1,
            "available_capabilities": {"TAG_WRITE", "RELEASE_WRITE", "ASSET_UPLOAD"},
        }
        for key, code, value in (
            ("projection_closed", "PROJECTION_NOT_CLOSED", False),
            ("release_record_ready", "RELEASE_RECORD_NOT_READY", False),
            ("canonical_lf_verified", "CANONICAL_LF_NOT_VERIFIED", False),
            ("repository_identity_verified", "REPOSITORY_IDENTITY_NOT_VERIFIED", False),
            ("work_main_ancestry_verified", "WORK_MAIN_ANCESTRY_NOT_VERIFIED", False),
            ("release_conflict", "RELEASE_CONFLICT", True),
            ("publication_mechanism_available", "PUBLICATION_MECHANISM_UNAVAILABLE", False),
            ("canonical_artifact_ref", "CANONICAL_ARTIFACT_REF_INVALID", "main:dist/a.zip"),
            ("artifact_sha256", "ARTIFACT_SHA256_INVALID", "bad"),
            ("artifact_size_bytes", "ARTIFACT_SIZE_INVALID", True),
            ("available_capabilities", "MISSING_CAPABILITY_TAG_WRITE", "TAG_WRITE"),
        ):
            with self.subTest(key=key):
                self.assertIn(code, evaluate_publication_preflight({**facts, key: value}))

    def test_publication_preflight_binds_closed_source_version_to_canonical_artifact(self):
        facts = {
            "source_version": "2.7.0", "source_version_closed": True,
            "projection_closed": True, "release_record_ready": True,
            "canonical_lf_verified": True, "repository_identity_verified": True,
            "work_main_ancestry_verified": True, "tag_conflict": False, "release_conflict": False,
            "publication_mechanism_available": True,
            "canonical_artifact_ref": "a" * 40 + ":dist/gpt-codex-framework-v2.7.0-bootstrap.zip",
            "artifact_sha256": "b" * 64, "artifact_size_bytes": 1,
            "available_capabilities": {"TAG_WRITE", "RELEASE_WRITE", "ASSET_UPLOAD"},
        }
        self.assertEqual(evaluate_publication_preflight(facts), [])
        for source_version in (None, "not-semver"):
            with self.subTest(source_version=source_version):
                self.assertIn(
                    "SOURCE_VERSION_NOT_CLOSED",
                    evaluate_publication_preflight({**facts, "source_version": source_version}),
                )
        self.assertIn(
            "SOURCE_VERSION_NOT_CLOSED",
            evaluate_publication_preflight({**facts, "source_version_closed": False}),
        )
        self.assertIn(
            "CANONICAL_ARTIFACT_REF_INVALID",
            evaluate_publication_preflight({
                **facts,
                "canonical_artifact_ref": "a" * 40 + ":dist/gpt-codex-framework-v2.7.1-bootstrap.zip",
            }),
        )

    def test_materializer_reads_verified_binary_bytes_from_immutable_git_object(self):
        payload = b"\x00zip-like\xffbytes\n"
        digest = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            artifact = root / "dist" / "gpt-codex-framework-v2.7.0-bootstrap.zip"
            artifact.parent.mkdir()
            artifact.write_bytes(payload)
            subprocess.run(["git", "add", "dist"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            artifact.write_bytes(b"wrong local bytes")
            target = Path(td) / "materialized"
            result = materialize_verified_git_artifact(root, revision, artifact.relative_to(root).as_posix(), digest, len(payload), target)
            self.assertEqual(result.read_bytes(), payload)
            with self.assertRaises(ValueError):
                materialize_verified_git_artifact(root, revision, artifact.relative_to(root).as_posix(), "0" * 64, len(payload), target)
            with self.assertRaises(ValueError):
                materialize_verified_git_artifact(root, revision, artifact.relative_to(root).as_posix(), digest, len(payload) + 1, target)
            with self.assertRaises(ValueError):
                materialize_verified_git_artifact(root, "b" * 40, artifact.relative_to(root).as_posix(), digest, len(payload), target)
            with self.assertRaises(ValueError):
                materialize_verified_git_artifact(root, revision, "../artifact.zip", digest, len(payload), target)

    def test_materializer_never_overwrites_or_follows_existing_final_target(self):
        payload = b"\x00immutable\xffartifact\n"
        digest = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            relative_path = "dist/gpt-codex-framework-v2.7.0-bootstrap.zip"
            artifact = root / relative_path
            artifact.parent.mkdir()
            artifact.write_bytes(payload)
            subprocess.run(["git", "add", "dist"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

            destination = Path(td) / "materialized"
            destination.mkdir()
            target = destination / artifact.name
            target.write_bytes(b"existing regular target")
            with self.assertRaises(FileExistsError):
                materialize_verified_git_artifact(root, revision, relative_path, digest, len(payload), destination)
            self.assertEqual(target.read_bytes(), b"existing regular target")

            target.unlink()
            outside = Path(td) / "outside-target.zip"
            outside.write_bytes(b"outside bytes must not change")
            try:
                target.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symbolic links unavailable in this environment: {exc}")
            with self.assertRaises(FileExistsError):
                materialize_verified_git_artifact(root, revision, relative_path, digest, len(payload), destination)
            self.assertEqual(outside.read_bytes(), b"outside bytes must not change")

            target.unlink()
            result = materialize_verified_git_artifact(root, revision, relative_path, digest, len(payload), destination)
            self.assertEqual(result.parent, destination.resolve())
            self.assertEqual(result.read_bytes(), payload)
    def test_harness_material_is_not_staged_as_product_runtime_input(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "consumer"
            staging = Path(td) / "staging"
            (root / ".harness").mkdir(parents=True)
            (root / ".harness" / "RULES.md").write_text("governance\n", encoding="utf-8")
            (root / ".harness" / "nested").mkdir()
            (root / ".harness" / "nested" / "state.md").write_text("state\n", encoding="utf-8")
            (root / "app").mkdir()
            (root / "app" / "main.py").write_text("print('product')\n", encoding="utf-8")
            manifest = {
                "paths": {
                    ".harness/RULES.md": "CONSUMER_REQUIRED",
                    ".harness/nested/state.md": "CONSUMER_REQUIRED",
                    "app/main.py": "CONSUMER_REQUIRED",
                }
            }
            control = {
                "roots": {
                    "harness_root": ".harness",
                    "product_roots": ["app"],
                    "deploy_roots": ["ops"],
                    "production_excludes": [".harness"],
                }
            }
            self.assertEqual(validate_harness_root_separation(control), [])
            inventory = stage_consumer_projection(
                root,
                staging,
                manifest,
                production_excludes=control["roots"]["production_excludes"],
            )
            self.assertEqual(inventory, ["app/main.py"])
            self.assertFalse((staging / ".harness" / "RULES.md").exists())
            self.assertFalse((staging / ".harness" / "nested" / "state.md").exists())
            self.assertTrue((staging / "app" / "main.py").is_file())

            default_staging = Path(td) / "default-staging"
            default_inventory = stage_consumer_projection(root, default_staging, manifest)
            self.assertIn(".harness/RULES.md", default_inventory)
            self.assertTrue((default_staging / ".harness" / "RULES.md").is_file())

    def test_previous_recorded_version_accepts_prerelease_records(self):
        with tempfile.TemporaryDirectory() as td:
            releases = Path(td) / "releases"
            releases.mkdir()
            (releases / "INDEX.json").write_text(
                json.dumps({
                    "releases": [
                        {"version": "2.2.1"},
                        {"version": "2.2.2-local.1"},
                    ],
                }),
                encoding="utf-8",
            )

            self.assertEqual(
                _previous_recorded_version(releases, "2.3.0"),
                "2.2.2-local.1",
            )

    def test_fresh_release_preserves_final_index_artifact_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fresh_release_fixture(tmp)
            result = _run_fresh_release(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            fields = _current_sha_fields(root)
            self.assertEqual(fields, (fields[0], fields[0], fields[0], fields[0], fields[0]))
            release_manifest = json.loads(
                (root / "dist" / f"gpt-codex-framework-v{CURRENT_VERSION}-release.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(release_manifest["validation"]["tests"], "PASS")

    def test_release_text_outputs_use_canonical_lf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fresh_release_fixture(tmp)
            result = package_release(
                root=root,
                output_dir=root / "dist",
                kernel_version="2.0.0",
                schema_version=1,
                validation_summary={"framework": "PASS", "tests": "PENDING"},
            )
            finalize_release_manifest(Path(result["manifest_path"]))

            for path in (Path(result["sha256_path"]), Path(result["manifest_path"])):
                with self.subTest(path=path):
                    content = path.read_bytes()
                    content.decode("utf-8")
                    self.assertTrue(content.endswith(b"\n"))
                    self.assertNotIn(b"\r\n", content)

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
