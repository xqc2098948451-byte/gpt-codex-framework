import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from framework_module_routing import validate_registry  # noqa: E402
from validate_framework import validate_module_registry  # noqa: E402


def descriptor(
    module_id: str,
    *,
    owned_assets: tuple[dict[str, str], ...] = (),
    depends_on: tuple[str, ...] = (),
    used_by: tuple[str, ...] = (),
    required_tests: tuple[str, ...] = (".gpt-codex/tests/test_framework_module_routing.py",),
) -> dict[str, object]:
    return {
        "MODULE_ID": module_id,
        "VERSION": "1.0.0",
        "PURPOSE": "fixture",
        "RESPONSIBILITIES": ["fixture responsibility"],
        "NON_RESPONSIBILITIES": ["fixture exclusion"],
        "OWNED_ASSETS": list(owned_assets),
        "ENTRY_POINTS": ["fixture entry"],
        "INPUTS": ["fixture input"],
        "OUTPUTS": ["fixture output"],
        "DEPENDS_ON": list(depends_on),
        "USED_BY": list(used_by),
        "INVARIANTS": ["fixture invariant"],
        "PERMISSIONS": ["READ_ONLY_REFERENCE"],
        "CHANGE_RISK": "LOW",
        "REQUIRED_TESTS": list(required_tests),
        "RELATED_MODULES": [],
    }


def fixture_registry(root: Path, descriptors: list[dict[str, object]]) -> dict[str, object]:
    test_path = root / ".gpt-codex/tests/test_framework_module_routing.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("# fixture\n", encoding="utf-8")
    modules = []
    for item in descriptors:
        module_id = str(item["MODULE_ID"])
        relative = f".gpt-codex/framework-modules/modules/{module_id}.json"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(item), encoding="utf-8")
        modules.append({"module_id": module_id, "descriptor": relative, "status": "ACTIVE"})
    return {
        "schema_version": 1,
        "authority": "FRAMEWORK_MODULE_REGISTRY",
        "framework_version": "2.4.0",
        "modules": modules,
    }


def write_registry(root: Path, registry: dict[str, object]) -> None:
    path = root / ".gpt-codex/framework-modules/REGISTRY.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry), encoding="utf-8")


def run_framework_with_registry_descriptor(descriptor_path: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "framework"
        shutil.copytree(
            ROOT,
            root,
            ignore=shutil.ignore_patterns(".git", ".worktrees", "dist"),
        )
        registry_path = root / ".gpt-codex/framework-modules/REGISTRY.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["modules"] = [
            {
                "module_id": "malformed",
                "descriptor": descriptor_path,
                "status": "ACTIVE",
            }
        ]
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(root / ".gpt-codex/scripts/validate_framework.py")],
            capture_output=True,
            text=True,
        )


class FrameworkModuleValidationTests(unittest.TestCase):
    def test_framework_validator_fails_closed_for_unsafe_descriptor_paths(self):
        for descriptor_path in (
            "C:/definitely-missing.json",
            "/definitely-missing.json",
            "../outside.json",
            "safe/../outside.json",
        ):
            with self.subTest(descriptor_path=descriptor_path):
                result = run_framework_with_registry_descriptor(descriptor_path)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertNotIn("Traceback", output)
                self.assertIn("MODULE_REGISTRY: MODULE_REGISTRY_INVALID", output)

    def test_framework_docs_describe_responsibility_first_registry_routing(self):
        corpus = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        corpus += (ROOT / ".gpt-codex/README.md").read_text(encoding="utf-8")
        for phrase in (
            "responsibility first, files second",
            "FRAMEWORK_MODULE_REGISTRY",
            "MODULE_ROUTE",
            "CROSS_MODULE_CHANGE_REQUIRED",
            "MODULE_ROUTE_UNRESOLVED",
            "Project Map remains DERIVED_NAVIGATION_INDEX",
        ):
            self.assertIn(phrase, corpus)

    def test_validate_framework_accepts_the_initial_registry(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / ".gpt-codex/scripts/validate_framework.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: PASS", result.stdout)

    def test_framework_validator_reports_registry_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(root, [descriptor("a")])
            registry["authority"] = "NOT_THE_REGISTRY"
            write_registry(root, registry)
            self.assertEqual(
                validate_module_registry(root),
                ["MODULE_REGISTRY: MODULE_REGISTRY_INVALID"],
            )

    def test_validate_project_does_not_require_management_registry(self):
        source = (ROOT / ".gpt-codex/scripts/validate_project.py").read_text(encoding="utf-8")
        self.assertNotIn("framework_module_routing", source)
        self.assertNotIn("framework-modules/REGISTRY.json", source)

    def test_unique_ids_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = descriptor("a")
            registry = fixture_registry(root, [first])
            registry["modules"].append(registry["modules"][0])
            self.assertIn("MODULE_REGISTRY_INVALID", validate_registry(root, registry))

    def test_authority_and_status_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(root, [descriptor("a")])
            registry["authority"] = "OTHER"
            self.assertIn("MODULE_REGISTRY_INVALID", validate_registry(root, registry))
            registry["authority"] = "FRAMEWORK_MODULE_REGISTRY"
            registry["modules"][0]["status"] = "PAUSED"
            self.assertIn("MODULE_REGISTRY_INVALID", validate_registry(root, registry))

    def test_descriptor_identity_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(root, [descriptor("a")])
            registry["modules"][0]["module_id"] = "wrong-id"
            self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(root, registry))

    def test_dependency_integrity_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(root, [descriptor("a", depends_on=("missing",))])
            self.assertIn("MODULE_DEPENDENCY_INVALID", validate_registry(root, registry))

    def test_reciprocal_depends_on_used_by_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(root, [descriptor("a", depends_on=("b",)), descriptor("b")])
            self.assertIn("MODULE_DEPENDENCY_INVALID", validate_registry(root, registry))

    def test_ownership_conflicts_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selector = {"type": "EXACT_PATH", "value": "shared/file.py"}
            registry = fixture_registry(
                root,
                [descriptor("a", owned_assets=(selector,)), descriptor("b", owned_assets=(selector,))],
            )
            self.assertIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))

    def test_unsafe_selectors_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selector = {"type": "EXACT_PATH", "value": "/absolute/file.py"}
            registry = fixture_registry(root, [descriptor("a", owned_assets=(selector,))])
            self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(root, registry))

    def test_required_test_references_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(
                root,
                [descriptor("a", required_tests=(".gpt-codex/tests/missing.py",))],
            )
            self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(root, registry))

    def test_valid_dependency_cycle_remains_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = fixture_registry(
                root,
                [
                    descriptor("a", depends_on=("b",), used_by=("b",)),
                    descriptor("b", depends_on=("a",), used_by=("a",)),
                ],
            )
            self.assertEqual(validate_registry(root, registry), [])


if __name__ == "__main__":
    unittest.main()
