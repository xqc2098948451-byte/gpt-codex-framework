import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from consumer_projection import load_projection_manifest, stage_consumer_projection


def _local_script_imports(path: Path, script_names: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            name = node.module.split(".", 1)[0]
            if name in script_names:
                imports.add(name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".", 1)[0]
                if name in script_names:
                    imports.add(name)
    return imports


class ConsumerRuntimeClosureTests(unittest.TestCase):
    def test_role_protocol_runtime_helper_is_projected_and_importable(self):
        manifest = load_projection_manifest(ROOT)
        self.assertEqual(
            manifest["paths"].get(".gpt-codex/scripts/role_communication.py"),
            "CONSUMER_REQUIRED",
        )
        imports = _local_script_imports(
            ROOT / ".gpt-codex" / "scripts" / "validate_project.py",
            {
                Path(relative).stem
                for relative, classification in manifest["paths"].items()
                if relative.startswith(".gpt-codex/scripts/") and relative.endswith(".py")
            },
        )
        self.assertIn("role_communication", imports)

    def test_consumer_required_python_imports_are_projection_closed(self):
        manifest = load_projection_manifest(ROOT)
        paths = manifest["paths"]
        script_names = {
            Path(relative).stem
            for relative, classification in paths.items()
            if relative.startswith(".gpt-codex/scripts/")
            and relative.endswith(".py")
        }
        missing: list[str] = []
        for relative, classification in paths.items():
            if classification != "CONSUMER_REQUIRED" or not relative.endswith(".py"):
                continue
            imports = _local_script_imports(ROOT / Path(*relative.split("/")), script_names)
            for imported in sorted(imports):
                imported_relative = f".gpt-codex/scripts/{imported}.py"
                if paths.get(imported_relative) != "CONSUMER_REQUIRED":
                    missing.append(f"{relative} -> {imported_relative}")
        self.assertEqual(missing, [])

    def test_extracted_consumer_validators_import_without_management_fallback(self):
        manifest = load_projection_manifest(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "staging"
            inventory = stage_consumer_projection(ROOT, staging, manifest)
            self.assertIn(".gpt-codex/scripts/publication_contract.py", inventory)
            self.assertNotIn(".gpt-codex/scripts/release_framework.py", inventory)
            archive_path = Path(tmp) / "consumer.zip"
            prefix = "consumer"
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for relative in inventory:
                    archive.writestr(
                        f"{prefix}/{relative}",
                        (staging / Path(*relative.split("/"))).read_bytes(),
                    )
            extract = Path(tmp) / "extract"
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(extract)
            script_root = extract / prefix / ".gpt-codex" / "scripts"
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            for module in ("validate_project", "validate_framework"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        "-c",
                        "import sys; sys.path.insert(0, sys.argv[1]); __import__(sys.argv[2])",
                        str(script_root),
                        module,
                    ],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_extracted_consumer_does_not_contain_management_identity(self):
        manifest = load_projection_manifest(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "staging"
            stage_consumer_projection(ROOT, staging, manifest)
            payload = b"".join(
                path.read_bytes() for path in staging.rglob("*") if path.is_file()
            )
            for value in manifest["contamination"]["forbidden_values"]:
                self.assertNotIn(value.encode("utf-8"), payload)

    def test_extracted_consumer_validator_runs_against_synthetic_project(self):
        manifest = load_projection_manifest(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "staging"
            inventory = stage_consumer_projection(ROOT, staging, manifest)
            project = Path(tmp) / "project"
            gov = project / ".gpt-codex"
            gov.mkdir(parents=True)
            (gov / "CONTROL.json").write_text(
                json.dumps(
                    {
                        "kernel_version": "2.0.0",
                        "schema_version": 1,
                        "project_id": "PRJ-SYNTHETIC-CONSUMER",
                        "governance_profile": "STANDARD",
                        "framework": {
                            "adopted_version": "2.2.2-local.1",
                            "last_evaluated_version": "2.2.2-local.1",
                            "evaluation_result": "ADOPTED",
                        },
                        "roots": {
                            "project_role": "AUTHORITATIVE",
                            "framework_role": "ADVISORY",
                            "framework_kernel_access": "READ_ONLY",
                            "framework_builtins_access": "READ_ONLY",
                            "harvest_namespace": "PRJ-SYNTHETIC-CONSUMER",
                        },
                        "extensions": {"skills": [], "guardrails": [], "fitness": []},
                        "permissions": {},
                        "complexity": {},
                    }
                ),
                encoding="utf-8",
            )
            (gov / "STATE.json").write_text(
                json.dumps(
                    {
                        "kernel_version": "2.0.0",
                        "schema_version": 1,
                        "project_id": "PRJ-SYNTHETIC-CONSUMER",
                        "revision": 0,
                        "state": "PROPOSED",
                        "blockers": [],
                        "evidence_refs": [],
                    }
                ),
                encoding="utf-8",
            )
            script = staging / ".gpt-codex" / "scripts" / "validate_project.py"
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            result = subprocess.run(
                [sys.executable, "-I", str(script), str(project)],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("RESULT: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
