import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class NavigationProjectValidationTests(unittest.TestCase):
    def _write_json(self, root, relative_path, payload):
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def _write_project(self, root):
        self._write_json(root, ".gpt-codex/CONTROL.json", {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "framework_management_only": True,
            "governance_profile": "FRAMEWORK_MANAGEMENT",
            "framework": {"evaluation_result": "ADOPTED"},
            "roots": {
                "project_role": "AUTHORITATIVE",
                "framework_role": "SELF_MANAGED",
                "framework_kernel_access": "READ_ONLY",
                "framework_builtins_access": "READ_ONLY",
            },
            "extensions": {"skills": [], "guardrails": [], "fitness": []},
        })
        self._write_json(root, ".gpt-codex/STATE.json", {
            "kernel_version": "2.0.0",
            "schema_version": 1,
            "project_id": "PROJECT-ONE",
            "revision": 7,
            "state": "ACTIVE",
        })

    def _project_map(self, modules):
        return {
            "schema_version": 1,
            "authority": "DERIVED_NAVIGATION_INDEX",
            "project_id": "PROJECT-ONE",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "repository_id": None,
            "anchor_sha": None,
            "architecture_summary": "A project summary.",
            "modules": modules,
        }

    def _module(self, module_id="core", module_map=".gpt-codex/navigation/modules/core.json"):
        return {
            "id": module_id,
            "purpose": "Core behavior.",
            "paths": ["src/core/"],
            "entry_points": ["src/core/index.py"],
            "keywords": ["core"],
            "module_map": module_map,
            "verified_at_sha": None,
            "freshness": "UNKNOWN",
        }

    def _module_map(self, module_id="core", project_id="PROJECT-ONE"):
        return {
            "schema_version": 1,
            "authority": "DERIVED_NAVIGATION_INDEX",
            "project_id": project_id,
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "module_id": module_id,
            "responsibility": "Core behavior.",
            "tracked_paths": ["src/core/"],
            "key_files": [{"path": "src/core/index.py", "role": "Entry point."}],
            "interfaces": [],
            "depends_on": [],
            "tests": [],
            "configuration": [],
            "data_models": [],
            "read_when": [],
            "verified_at_sha": None,
            "freshness": "UNKNOWN",
        }

    def _validate(self, root):
        return subprocess.run(
            [sys.executable, str(ROOT / ".gpt-codex/scripts/validate_project.py"), str(root)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_project_without_navigation_or_resume_is_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)

            result = self._validate(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_foreign_project_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            project_map = self._project_map([])
            project_map["project_id"] = "PROJECT-FOREIGN"
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", project_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_PROJECT_ID_MISMATCH", result.stdout)

    def test_incomplete_identity_valid_project_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            project_map = self._project_map([])
            del project_map["architecture_summary"]
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", project_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PROJECT_MAP_SCHEMA_INVALID", result.stdout)

    def test_foreign_module_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", self._module_map(project_id="PROJECT-FOREIGN"))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_PROJECT_ID_MISMATCH", result.stdout)

    def test_incomplete_identity_valid_module_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            module_map = self._module_map()
            del module_map["responsibility"]
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", module_map)

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_SCHEMA_INVALID", result.stdout)

    def test_duplicate_module_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(), self._module()]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_DUPLICATE_MODULE_ID", result.stdout)

    def test_malformed_project_map_module_shape_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(module_id={})]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NAVIGATION_INVALID_SHAPE", result.stdout)

    def test_module_map_id_must_match_project_map_entry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module()]))
            self._write_json(root, ".gpt-codex/navigation/modules/core.json", self._module_map(module_id="foreign"))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_ID_MISMATCH", result.stdout)

    def test_module_map_path_must_be_project_relative_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", self._project_map([self._module(module_map="navigation/modules/core.txt")]))

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODULE_MAP_PATH_INVALID", result.stdout)

    def test_resume_claiming_authoritative_state_is_rejected_without_state_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            state_path = root / ".gpt-codex/STATE.json"
            state_before = state_path.read_text(encoding="utf-8")
            self._write_json(root, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "CANONICAL_STATE",
                "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "revision": 999,
                "state": "COMPLETE",
            })

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_CHECKPOINT_AUTHORITY_INVALID", result.stdout)
            self.assertEqual(state_path.read_text(encoding="utf-8"), state_before)

    def test_incomplete_identity_valid_resume_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_project(root)
            self._write_json(root, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "DERIVED_CACHE",
                "project_id": "PROJECT-ONE",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": None,
            })

            result = self._validate(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_SCHEMA_INVALID", result.stdout)


if __name__ == "__main__":
    unittest.main()
