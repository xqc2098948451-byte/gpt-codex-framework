import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from consumer_projection import (  # noqa: E402
    ProjectionValidationError,
    audit_projection_paths,
    build_consumer_inventory,
    compare_projection_to_zip,
    load_projection_manifest,
    scan_consumer_boundary,
    stage_consumer_projection,
)


def write_minimal_projection_fixture(root: Path) -> None:
    (root / ".gpt-codex").mkdir(parents=True)
    (root / "VERSION").write_text("2.2.1\n", encoding="utf-8")
    (root / ".gpt-codex" / "README.md").write_text("generic\n", encoding="utf-8")
    (root / ".gpt-codex" / "CONTROL.json").write_text("management\n", encoding="utf-8")
    (root / ".gpt-codex" / "release").mkdir()
    (root / ".gpt-codex" / "release" / "consumer-projection-manifest.json").write_text(
        json.dumps(minimal_manifest()), encoding="utf-8"
    )


def minimal_manifest() -> dict[str, object]:
    return {
        "manifest_version": 1,
        "framework_version": "2.2.1",
        "projection": "CONSUMER_BOOTSTRAP",
        "paths": {
            "VERSION": "CONSUMER_REQUIRED",
            ".gpt-codex/README.md": "CONSUMER_REQUIRED",
            ".gpt-codex/CONTROL.json": "MANAGEMENT_ONLY",
            ".gpt-codex/release/consumer-projection-manifest.json": "MANAGEMENT_ONLY",
        },
    }


HISTORICAL_CONTINUITY_DOCS = (
    "docs/superpowers/specs/2026-09-11-v2.2.0-github-project-continuity-design.md",
    "docs/superpowers/plans/2026-09-11-v2.2.0-github-project-continuity.md",
)


def make_synthetic_consumer_fixture(root: Path) -> Path:
    (root / ".gpt-codex" / "release").mkdir(parents=True)
    (root / "VERSION").write_text("2.2.1\n", encoding="utf-8")
    (root / ".gpt-codex" / "README.md").write_text(
        "Synthetic Consumer Project uses synthetic-repository-1 and "
        "00000000-0000-4000-8000-000000000001.\n",
        encoding="utf-8",
    )
    (root / ".gpt-codex" / "release" / "consumer-projection-manifest.json").write_text(
        json.dumps(synthetic_manifest_for(root)), encoding="utf-8"
    )
    return root


def synthetic_manifest_for(root: Path) -> dict[str, object]:
    del root
    return {
        "manifest_version": 1,
        "framework_version": "2.2.1",
        "projection": "CONSUMER_BOOTSTRAP",
        "paths": {
            "VERSION": "CONSUMER_REQUIRED",
            ".gpt-codex/README.md": "CONSUMER_REQUIRED",
            ".gpt-codex/release/consumer-projection-manifest.json": "MANAGEMENT_ONLY",
        },
    }


def git_show_bytes(revision: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


class ConsumerProjectionTests(unittest.TestCase):
    def test_validate_consumer_projection_zip_derives_canonical_prefix(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate_consumer_projection.py"),
                "--root",
                str(ROOT),
                "--zip",
                str(ROOT / "dist" / "gpt-codex-framework-v2.2.1-bootstrap.zip"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONSUMER_PROJECTION_RELEASE_MATCH: PASS", result.stdout)

    def test_validate_consumer_projection_rejects_ambiguous_archive_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "ambiguous.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("first/VERSION", "2.2.1\n")
                archive.writestr("second/VERSION", "2.2.1\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_consumer_projection.py"),
                    "--root",
                    str(ROOT),
                    "--zip",
                    str(archive_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("archive must contain exactly one non-empty top-level directory", result.stdout)

    def test_cli_and_direct_api_use_equivalent_prefix_semantics(self):
        manifest = load_projection_manifest(ROOT)
        zip_path = ROOT / "dist" / "gpt-codex-framework-v2.2.1-bootstrap.zip"
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "staging"
            stage_consumer_projection(ROOT, staging, manifest)
            with zipfile.ZipFile(zip_path) as archive:
                prefix = sorted({name.split("/", 1)[0] for name in archive.namelist() if name})[0]
            direct = compare_projection_to_zip(staging, zip_path, prefix)
            cli = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_consumer_projection.py"),
                    "--root",
                    str(ROOT),
                    "--zip",
                    str(zip_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertTrue(direct["match"], direct)
            self.assertEqual(cli.returncode, 0, cli.stdout + cli.stderr)

    def test_manifest_classifies_exact_paths_without_globs(self):
        manifest = load_projection_manifest(ROOT)
        self.assertEqual(manifest["manifest_version"], 1)
        self.assertEqual(manifest["projection"], "CONSUMER_BOOTSTRAP")
        self.assertEqual(manifest["paths"][".gpt-codex/CONTROL.json"], "MANAGEMENT_ONLY")
        self.assertEqual(
            manifest["paths"][
                "docs/superpowers/specs/2026-09-11-v2.2.0-github-project-continuity-design.md"
            ],
            "DEVELOPMENT_HISTORY",
        )
        self.assertNotIn("**", manifest["paths"])

    def test_unknown_non_local_path_is_excluded_and_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            (root / "new-management-only.md").write_text("internal", encoding="utf-8")
            audit = audit_projection_paths(root, minimal_manifest())
            self.assertEqual(audit["unknown_paths"], ["new-management-only.md"])
            with self.assertRaises(ProjectionValidationError):
                build_consumer_inventory(root, minimal_manifest())

    def test_current_source_has_no_unclassified_non_local_paths(self):
        manifest = load_projection_manifest(ROOT)
        audit = audit_projection_paths(ROOT, manifest)
        self.assertEqual(audit["unknown_paths"], [])
        self.assertEqual(audit["missing_required_paths"], [])
        self.assertEqual(audit["invalid_classifications"], [])

    def test_projection_validator_cli_accepts_clean_synthetic_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_consumer_projection.py"),
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("CONSUMER_PROJECTION_RELEASE_MATCH: PASS", result.stdout)

    def test_staging_contains_required_files_but_not_management_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "stage"
            included = stage_consumer_projection(ROOT, staging, load_projection_manifest(ROOT))
            self.assertIn("VERSION", included)
            self.assertNotIn(".gpt-codex/CONTROL.json", included)
            self.assertNotIn(".gpt-codex/STATE.json", included)
            self.assertFalse((staging / ".gpt-codex/evidence").exists())

    def test_real_management_identity_is_rejected_in_projection_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "stage"
            stage_consumer_projection(ROOT, staging, load_projection_manifest(ROOT))
            (staging / "leak.txt").write_text(
                "cb1e0450-df32-4ff6-8a33-35187b69a866", encoding="utf-8"
            )
            result = scan_consumer_boundary(staging, load_projection_manifest(ROOT))
            self.assertIn("leak.txt", result["management_identity_hits"])

    def test_missing_required_path_is_reported_and_blocks_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            manifest = minimal_manifest()
            manifest["paths"]["missing-required.md"] = "CONSUMER_REQUIRED"
            audit = audit_projection_paths(root, manifest)
            self.assertEqual(audit["missing_required_paths"], ["missing-required.md"])
            with self.assertRaises(ProjectionValidationError):
                build_consumer_inventory(root, manifest)

    def test_projection_and_zip_have_identical_relative_files_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "stage"
            zip_path = Path(tmp) / "projection.zip"
            inventory = stage_consumer_projection(ROOT, staging, load_projection_manifest(ROOT))
            prefix = "gpt-codex-framework-v2.2.1-bootstrap"
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for relative in inventory:
                    archive.writestr(f"{prefix}/{relative}", (staging / relative).read_bytes())
            comparison = compare_projection_to_zip(staging, zip_path, prefix)
            self.assertTrue(comparison["match"], comparison)

    def test_synthetic_generic_fixture_is_allowed_without_real_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_synthetic_consumer_fixture(Path(tmp) / "source")
            manifest = synthetic_manifest_for(root)
            stage = Path(tmp) / "stage"
            stage_consumer_projection(root, stage, manifest)
            self.assertEqual(scan_consumer_boundary(stage, manifest)["management_identity_hits"], [])

    def test_historical_design_plan_bytes_are_unchanged(self):
        for relative in HISTORICAL_CONTINUITY_DOCS:
            working_tree = (ROOT / relative).read_text(encoding="utf-8").replace("\r\n", "\n").encode()
            self.assertEqual(working_tree, git_show_bytes("HEAD", relative))


if __name__ == "__main__":
    unittest.main()
