import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CURRENT_PREFIX = f"gpt-codex-framework-v{CURRENT_VERSION}-bootstrap"
sys.path.insert(0, str(SCRIPTS))

import consumer_projection  # noqa: E402
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


def prefix_manifest() -> dict[str, object]:
    manifest = minimal_manifest()
    manifest["prefix_defaults"] = {
        ".gpt-codex/evidence/": "MANAGEMENT_ONLY",
        "docs/superpowers/": "DEVELOPMENT_HISTORY",
        ".superpowers/sdd/": "DEVELOPMENT_HISTORY",
        "releases/records/": "RELEASE_METADATA",
    }
    return manifest


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
    def test_harness_templates_are_consumer_required(self):
        manifest = load_projection_manifest(ROOT)
        expected = {
            ".gpt-codex/project-template/.harness/RULES.template.md": "CONSUMER_REQUIRED",
            ".gpt-codex/project-template/.harness/STATE.template.md": "CONSUMER_REQUIRED",
            ".gpt-codex/project-template/.harness/REASONING.template.md": "CONSUMER_REQUIRED",
            ".gpt-codex/project-template/.harness/FEEDBACK.template.md": "CONSUMER_REQUIRED",
            ".gpt-codex/tests/test_harness_project_layering.py": "MANAGEMENT_ONLY",
        }
        self.assertEqual(
            {relative: manifest["paths"].get(relative) for relative in expected},
            expected,
        )

    def test_execution_telemetry_is_management_only_and_stage_docs_are_history(self):
        manifest = load_projection_manifest(ROOT)
        paths = manifest["paths"]
        self.assertEqual(paths.get(".gpt-codex/scripts/execution_telemetry.py"), "MANAGEMENT_ONLY")
        self.assertEqual(paths.get(".gpt-codex/tests/test_execution_telemetry.py"), "MANAGEMENT_ONLY")
        self.assertEqual(paths.get(".gpt-codex/scripts/framework_feedback.py"), "CONSUMER_REQUIRED")
        self.assertEqual(paths.get(".gpt-codex/tests/test_framework_feedback.py"), "MANAGEMENT_ONLY")
        for relative in (
            "docs/superpowers/specs/2026-09-13-execution-telemetry-design.md",
            "docs/superpowers/plans/2026-09-14-execution-telemetry.md",
        ):
            self.assertEqual(
                consumer_projection._resolve_projection_classification(
                    relative, paths, manifest["prefix_defaults"]
                ),
                "DEVELOPMENT_HISTORY",
            )
        self.assertEqual(audit_projection_paths(ROOT, manifest)["unknown_paths"], [])

    def test_manifest_classifies_framework_module_management_boundary(self):
        manifest = load_projection_manifest(ROOT)
        expected_management_paths = {
            "docs/superpowers/specs/2026-09-13-framework-modular-architecture-routing-design.md": "DEVELOPMENT_HISTORY",
            "docs/superpowers/plans/2026-09-13-framework-modular-architecture-routing.md": "DEVELOPMENT_HISTORY",
            ".gpt-codex/framework-modules/REGISTRY.json": "MANAGEMENT_ONLY",
            ".gpt-codex/schemas/framework-module-registry.schema.json": "MANAGEMENT_ONLY",
            ".gpt-codex/schemas/framework-module.schema.json": "MANAGEMENT_ONLY",
            ".gpt-codex/scripts/framework_module_routing.py": "MANAGEMENT_ONLY",
            ".gpt-codex/tests/test_framework_module_schemas.py": "MANAGEMENT_ONLY",
            ".gpt-codex/tests/test_framework_module_routing.py": "MANAGEMENT_ONLY",
            ".gpt-codex/tests/test_framework_module_validation.py": "MANAGEMENT_ONLY",
        }
        for module_id in (
            "framework-core",
            "identity-context",
            "role-communication",
            "navigation-continuity",
            "git-continuity",
            "release-projection",
            "framework-validation",
        ):
            expected_management_paths[
                f".gpt-codex/framework-modules/modules/{module_id}.json"
            ] = "MANAGEMENT_ONLY"
        for path, classification in expected_management_paths.items():
            self.assertEqual(
                consumer_projection._resolve_projection_classification(
                    path, manifest["paths"], manifest["prefix_defaults"]
                ),
                classification,
            )
        audit = audit_projection_paths(ROOT, manifest)
        self.assertEqual(audit["unknown_paths"], [])
        self.assertEqual(audit["missing_required_paths"], [])

    def test_validate_consumer_projection_rejects_stale_canonical_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "stale.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(f"{CURRENT_PREFIX}/VERSION", f"{CURRENT_VERSION}\n")
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
        self.assertIn('"match": false', result.stdout)
        self.assertIn(".gpt-codex/schemas/project-map.schema.json", result.stdout)

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
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "staging"
            stage_consumer_projection(ROOT, staging, manifest)
            zip_path = Path(tmp) / "projection.zip"
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for relative in build_consumer_inventory(ROOT, manifest):
                    archive.writestr(f"{CURRENT_PREFIX}/{relative}", (staging / relative).read_bytes())
            prefix = CURRENT_PREFIX
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
            consumer_projection._resolve_projection_classification(
                "docs/superpowers/specs/2026-09-11-v2.2.0-github-project-continuity-design.md",
                manifest["paths"],
                manifest["prefix_defaults"],
            ),
            "DEVELOPMENT_HISTORY",
        )
        self.assertNotIn("**", manifest["paths"])

    def test_prefix_defaults_classify_new_evidence_and_superpowers_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            evidence = root / ".gpt-codex/evidence/new-result.json"
            history = root / "docs/superpowers/new-design.md"
            evidence.parent.mkdir(parents=True)
            history.parent.mkdir(parents=True)
            evidence.write_text("{}", encoding="utf-8")
            history.write_text("history", encoding="utf-8")

            audit = audit_projection_paths(root, prefix_manifest())

            self.assertEqual(audit["unknown_paths"], [])
            self.assertEqual(audit["invalid_classifications"], [])
            inventory = build_consumer_inventory(root, prefix_manifest())
            self.assertNotIn(".gpt-codex/evidence/new-result.json", inventory)
            self.assertNotIn("docs/superpowers/new-design.md", inventory)

    def test_exact_consumer_path_overrides_exclusion_prefix_and_stays_in_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            consumer_file = root / "docs/superpowers/required.md"
            consumer_file.parent.mkdir(parents=True)
            consumer_file.write_text("required", encoding="utf-8")
            manifest = prefix_manifest()
            manifest["paths"]["docs/superpowers/required.md"] = "CONSUMER_REQUIRED"

            self.assertEqual(audit_projection_paths(root, manifest)["unknown_paths"], [])
            self.assertIn("docs/superpowers/required.md", build_consumer_inventory(root, manifest))

    def test_longest_matching_prefix_wins(self):
        self.assertTrue(hasattr(consumer_projection, "_resolve_projection_classification"))
        self.assertEqual(
            consumer_projection._resolve_projection_classification(
                "docs/superpowers/private/note.md",
                {},
                {
                    "docs/superpowers/": "DEVELOPMENT_HISTORY",
                    "docs/superpowers/private/": "MANAGEMENT_ONLY",
                },
            ),
            "MANAGEMENT_ONLY",
        )

    def test_invalid_prefix_defaults_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            manifest = minimal_manifest()
            manifest["prefix_defaults"] = {
                "docs/superpowers/": "CONSUMER_REQUIRED",
                "docs/*.md/": "DEVELOPMENT_HISTORY",
            }

            invalid = audit_projection_paths(root, manifest)["invalid_classifications"]

            self.assertIn("docs/superpowers/", invalid)
            self.assertIn("docs/*.md/", invalid)

    def test_unmatched_path_stays_unknown_and_prefix_only_never_enters_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            default_file = root / "docs/superpowers/history.md"
            unmatched_file = root / "unmatched.md"
            default_file.parent.mkdir(parents=True)
            default_file.write_text("history", encoding="utf-8")
            unmatched_file.write_text("unknown", encoding="utf-8")
            manifest = prefix_manifest()

            audit = audit_projection_paths(root, manifest)

            self.assertEqual(audit["unknown_paths"], ["unmatched.md"])
            with self.assertRaises(ProjectionValidationError):
                build_consumer_inventory(root, manifest)

    def test_manifest_classifies_v230_navigation_consumer_boundary(self):
        manifest = load_projection_manifest(ROOT)
        expected_consumer_paths = (
            ".gpt-codex/schemas/project-map.schema.json",
            ".gpt-codex/schemas/module-map.schema.json",
            ".gpt-codex/schemas/resume.schema.json",
            ".gpt-codex/project-template/navigation/PROJECT_MAP.template.json",
            ".gpt-codex/project-template/navigation/modules/MODULE_MAP.template.json",
            ".gpt-codex/project-template/continuity/RESUME.template.json",
            ".gpt-codex/scripts/project_navigation.py",
        )
        for relative in expected_consumer_paths:
            self.assertEqual(manifest["paths"][relative], "CONSUMER_REQUIRED")
        self.assertEqual(
            consumer_projection._resolve_projection_classification(
                ".superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-1-brief.md",
                manifest["paths"],
                manifest["prefix_defaults"],
            ),
            "DEVELOPMENT_HISTORY",
        )

    def test_manifest_classifies_role_protocol_runtime_and_management_tests(self):
        manifest = load_projection_manifest(ROOT)
        self.assertEqual(manifest["paths"][".gpt-codex/scripts/role_communication.py"], "CONSUMER_REQUIRED")
        for relative in (
            ".gpt-codex/tests/test_instruction_role_contract.py",
            ".gpt-codex/tests/test_review_history.py",
            ".gpt-codex/tests/test_review_lifecycle.py",
            ".gpt-codex/tests/test_role_authority.py",
            ".gpt-codex/tests/test_role_communication_taxonomy.py",
            ".gpt-codex/tests/test_role_routing_docs.py",
            ".gpt-codex/tests/test_stage_review_routing.py",
        ):
            self.assertEqual(manifest["paths"][relative], "MANAGEMENT_ONLY")

    def test_manifest_classifies_current_task9_review_artifacts_as_history(self):
        manifest = load_projection_manifest(ROOT)
        for relative in (
            ".superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/review-0eccd66..cca699b.diff",
            ".superpowers/sdd/2026-09-12-v2.3.0-project-map-context-resume/task-9-report.md",
        ):
            self.assertEqual(
                consumer_projection._resolve_projection_classification(
                    relative, manifest["paths"], manifest["prefix_defaults"]
                ),
                "DEVELOPMENT_HISTORY",
            )

    def test_framework_validator_reads_bootstrap_phrase_corpus_specifically(self):
        validator = (SCRIPTS / "validate_framework.py").read_text(encoding="utf-8")
        self.assertIn(
            "bootstrap_prompt = (ROOT/'.gpt-codex/BOOTSTRAP_PROMPT.md').read_text(encoding='utf-8')",
            validator,
        )
        self.assertIn("for phrase in bootstrap_phrases:", validator)

    def test_unknown_non_local_path_is_excluded_and_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            (root / "new-management-only.md").write_text("internal", encoding="utf-8")
            audit = audit_projection_paths(root, minimal_manifest())
            self.assertEqual(audit["unknown_paths"], ["new-management-only.md"])
            with self.assertRaises(ProjectionValidationError):
                build_consumer_inventory(root, minimal_manifest())

    def test_git_worktrees_are_local_only_and_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_projection_fixture(root)
            worktree_file = root / ".worktrees" / "branch" / "state.txt"
            worktree_file.parent.mkdir(parents=True)
            worktree_file.write_text("local checkout", encoding="utf-8")
            audit = audit_projection_paths(root, minimal_manifest())
            self.assertEqual(audit["unknown_paths"], [])

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
            prefix = CURRENT_PREFIX
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
