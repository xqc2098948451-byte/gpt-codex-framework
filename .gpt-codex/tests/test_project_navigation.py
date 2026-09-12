import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))


class ProjectNavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.navigation = importlib.import_module("project_navigation")

    def write_json(self, root: Path, relative_path: str, payload: object) -> Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_missing_project_map_returns_none(self) -> None:
        try:
            navigation = importlib.import_module("project_navigation")
        except ModuleNotFoundError as exc:
            self.fail(f"project navigation implementation is unavailable: {exc}")

        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(navigation.load_project_map(Path(directory)))

    def test_rejects_duplicate_project_map_module_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
                "modules": [{"id": "api"}, {"id": "api"}],
            })

            with self.assertRaisesRegex(ValueError, "NAVIGATION_DUPLICATE_MODULE_ID"):
                self.navigation.load_project_map(root)

    def test_loads_project_map_with_distinct_module_ids(self) -> None:
        project_map = {
            "schema_version": 1,
            "authority": "DERIVED_NAVIGATION_INDEX",
            "project_id": "PRJ-EXAMPLE-001",
            "project_context_id": "context-a",
            "repository_id": None,
            "anchor_sha": None,
            "architecture_summary": "A project with two modules.",
            "modules": [
                {
                    "id": "api",
                    "purpose": "Serve requests.",
                    "paths": ["src/api/"],
                    "entry_points": ["src/api/main.py"],
                    "keywords": ["api"],
                    "module_map": ".gpt-codex/navigation/modules/api.json",
                    "verified_at_sha": None,
                    "freshness": "UNKNOWN",
                },
                {
                    "id": "web",
                    "purpose": "Render pages.",
                    "paths": ["src/web/"],
                    "entry_points": ["src/web/main.py"],
                    "keywords": ["web"],
                    "module_map": ".gpt-codex/navigation/modules/web.json",
                    "verified_at_sha": None,
                    "freshness": "UNKNOWN",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", project_map)

            self.assertEqual(project_map, self.navigation.load_project_map(root))

    def test_rejects_foreign_project_context_id(self) -> None:
        navigation = {
            "project_id": "project-a",
            "project_context_id": "context-a",
            "repository_id": "repo-a",
        }
        control = {
            "project_id": "project-a",
            "project_context_id": "context-b",
            "github": {"repository_id": "repo-a"},
        }

        with self.assertRaisesRegex(ValueError, "NAVIGATION_PROJECT_CONTEXT_MISMATCH"):
            self.navigation.validate_navigation_identity(navigation, control)

    def test_rejects_module_map_with_unsupported_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_json(root, "modules/api.json", {
                "schema_version": 2,
                "authority": "DERIVED_NAVIGATION_INDEX",
            })

            with self.assertRaisesRegex(ValueError, "MODULE_MAP_SCHEMA_UNSUPPORTED"):
                self.navigation.load_module_map(root, "modules/api.json")

    def test_rejects_module_map_with_invalid_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_json(root, "modules/api.json", {
                "schema_version": 1,
                "authority": "CANONICAL_STATE",
            })

            with self.assertRaisesRegex(ValueError, "MODULE_MAP_AUTHORITY_INVALID"):
                self.navigation.load_module_map(root, "modules/api.json")

    def test_rejects_absolute_module_map_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "project"
            root.mkdir()
            outside = self.write_json(base, "outside-module-map.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
            })

            with self.assertRaises(ValueError):
                self.navigation.load_module_map(root, str(outside))

    def test_rejects_traversing_module_map_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "project"
            root.mkdir()
            self.write_json(base, "outside-module-map.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
            })

            with self.assertRaises(ValueError):
                self.navigation.load_module_map(root, "../outside-module-map.json")

    def test_returns_the_single_matching_module(self) -> None:
        project_map = {
            "modules": [
                {"id": "api", "path": "src/api"},
                {"id": "web", "path": "src/web"},
            ]
        }

        self.assertEqual(
            {"id": "web", "path": "src/web"},
            self.navigation.module_by_id(project_map, "web"),
        )
        self.assertIsNone(self.navigation.module_by_id(project_map, "missing"))


if __name__ == "__main__":
    unittest.main()
