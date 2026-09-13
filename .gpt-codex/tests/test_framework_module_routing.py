import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from framework_module_routing import (  # noqa: E402
    ModuleRoutingError,
    classify_changed_assets,
    load_registry,
    required_tests_for_change,
    route_responsibility,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".gpt-codex" / "framework-modules" / "REGISTRY.json"


MODULE_FIELDS = frozenset(
    {
        "MODULE_ID",
        "VERSION",
        "PURPOSE",
        "RESPONSIBILITIES",
        "NON_RESPONSIBILITIES",
        "OWNED_ASSETS",
        "ENTRY_POINTS",
        "INPUTS",
        "OUTPUTS",
        "DEPENDS_ON",
        "USED_BY",
        "INVARIANTS",
        "PERMISSIONS",
        "CHANGE_RISK",
        "REQUIRED_TESTS",
        "RELATED_MODULES",
    }
)


INITIAL_MODULE_IDS = [
    "framework-core",
    "identity-context",
    "role-communication",
    "navigation-continuity",
    "git-continuity",
    "release-projection",
    "framework-validation",
]


def minimal_descriptor(
    module_id: str,
    *,
    owned_assets: tuple[dict[str, str], ...] = (),
    depends_on: tuple[str, ...] = (),
    used_by: tuple[str, ...] = (),
    inputs: tuple[str, ...] = ("fixture input",),
    outputs: tuple[str, ...] = ("fixture output",),
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
        "INPUTS": list(inputs),
        "OUTPUTS": list(outputs),
        "DEPENDS_ON": list(depends_on),
        "USED_BY": list(used_by),
        "INVARIANTS": ["fixture invariant"],
        "PERMISSIONS": ["READ_ONLY_REFERENCE"],
        "CHANGE_RISK": "LOW",
        "REQUIRED_TESTS": list(required_tests),
        "RELATED_MODULES": [],
    }


def write_registry_fixture(
    root: Path, descriptors: list[dict[str, object]]
) -> dict[str, object]:
    test_path = root / ".gpt-codex/tests/test_framework_module_routing.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("# fixture\n", encoding="utf-8")
    modules = []
    for descriptor in descriptors:
        module_id = str(descriptor["MODULE_ID"])
        relative = f".gpt-codex/framework-modules/modules/{module_id}.json"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(descriptor), encoding="utf-8")
        modules.append({"module_id": module_id, "descriptor": relative, "status": "ACTIVE"})
    return {
        "schema_version": 1,
        "authority": "FRAMEWORK_MODULE_REGISTRY",
        "framework_version": "2.4.0",
        "modules": modules,
    }


def write_registry_file(root: Path, registry: dict[str, object]) -> None:
    path = root / ".gpt-codex/framework-modules/REGISTRY.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry), encoding="utf-8")


class FrameworkModuleRoutingTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT
        self.registry = load_registry(ROOT)

    def test_registry_has_exact_initial_module_ids(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["authority"], "FRAMEWORK_MODULE_REGISTRY")
        self.assertEqual(
            [entry["module_id"] for entry in registry["modules"]],
            INITIAL_MODULE_IDS,
        )
        self.assertTrue(all(entry["status"] == "ACTIVE" for entry in registry["modules"]))

    def test_each_registered_descriptor_has_exact_identity_and_fields(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for entry in registry["modules"]:
            descriptor = json.loads((ROOT / entry["descriptor"]).read_text(encoding="utf-8"))
            self.assertEqual(descriptor["MODULE_ID"], entry["module_id"])
            self.assertEqual(set(descriptor), MODULE_FIELDS)

    def test_missing_registry_raises_module_registry_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ModuleRoutingError) as caught:
                load_registry(Path(directory))
        self.assertEqual(caught.exception.code, "MODULE_REGISTRY_INVALID")

    def test_missing_descriptor_is_reported_as_module_descriptor_invalid(self):
        registry = {
            "schema_version": 1,
            "authority": "FRAMEWORK_MODULE_REGISTRY",
            "framework_version": "2.4.0",
            "modules": [{
                "module_id": "missing",
                "descriptor": ".gpt-codex/framework-modules/modules/missing.json",
                "status": "ACTIVE",
            }],
        }
        self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(self.root, registry))

    def test_dependency_and_used_by_edges_must_be_reciprocal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor("a", depends_on=("b",)), minimal_descriptor("b")],
            )
            self.assertIn("MODULE_DEPENDENCY_INVALID", validate_registry(root, registry))

    def test_contract_consumer_requires_reciprocal_dependency_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor(
                        "producer",
                        owned_assets=({"type": "EXACT_PATH", "value": "producer/file.py"},),
                        outputs=("CONTRACT_X",),
                    ),
                    minimal_descriptor("consumer", inputs=("CONTRACT_X",)),
                ],
            )
            self.assertIn("MODULE_DEPENDENCY_INVALID", validate_registry(root, registry))

    def test_invalid_contract_consumer_dependency_fails_before_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor(
                        "producer",
                        owned_assets=({"type": "EXACT_PATH", "value": "producer/file.py"},),
                        outputs=("CONTRACT_X",),
                    ),
                    minimal_descriptor("consumer", inputs=("CONTRACT_X",)),
                ],
            )
            registry_path = root / ".gpt-codex/framework-modules/REGISTRY.json"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaises(ModuleRoutingError) as caught:
                route_responsibility(
                    root,
                    "producer",
                    "fixture responsibility",
                    planned_assets=["producer/file.py"],
                    contracts_affected=["CONTRACT_X"],
                )
            self.assertEqual(caught.exception.code, "MODULE_DEPENDENCY_INVALID")

    def test_reciprocal_contract_consumer_dependency_remains_cross_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor(
                        "producer",
                        owned_assets=({"type": "EXACT_PATH", "value": "producer/file.py"},),
                        outputs=("CONTRACT_X",),
                        used_by=("consumer",),
                    ),
                    minimal_descriptor(
                        "consumer",
                        inputs=("CONTRACT_X",),
                        depends_on=("producer",),
                    ),
                ],
            )
            registry_path = root / ".gpt-codex/framework-modules/REGISTRY.json"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            decision = route_responsibility(
                root,
                "producer",
                "fixture responsibility",
                planned_assets=["producer/file.py"],
                contracts_affected=["CONTRACT_X"],
            )
            self.assertEqual(decision.outcome, "CROSS_MODULE_CHANGE_REQUIRED")

    def test_zero_owner_is_unresolved(self):
        self.assertEqual(
            classify_changed_assets(self.root, self.registry, ["unregistered/file.json"])[
                "unregistered/file.json"
            ],
            (),
        )
        with self.assertRaises(ModuleRoutingError) as caught:
            route_responsibility(
                self.root,
                "framework-core",
                "framework governance",
                planned_assets=["unregistered/file.json"],
            )
        self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")

    def test_selector_paths_reject_absolute_and_parent_traversal(self):
        for value in ("/absolute/file", "C:/absolute/file", "safe/../file"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                registry = write_registry_fixture(
                    Path(directory),
                    [minimal_descriptor("a", owned_assets=({"type": "EXACT_PATH", "value": value},))],
                )
                self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(Path(directory), registry))

    def test_malformed_selector_is_descriptor_invalid_without_raising(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor("a", owned_assets=({"type": [], "value": "file"},))],
            )
            self.assertIn("MODULE_DESCRIPTOR_INVALID", validate_registry(root, registry))

    def test_ownership_conflict_is_returned_by_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "EXACT_PATH", "value": "shared/file.json"},)),
                    minimal_descriptor("b", owned_assets=({"type": "EXACT_PATH", "value": "shared/file.json"},)),
                ],
            )
            self.assertIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))

    def test_prefix_matching_respects_component_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "PATH_PREFIX", "value": "foo/bar"},)),
                    minimal_descriptor("b", owned_assets=({"type": "EXACT_PATH", "value": "foo/bar2"},)),
                ],
            )
            owners = classify_changed_assets(root, registry, ["foo/bar2", "foo/bar/child"])
            self.assertEqual(owners["foo/bar2"], ("b",))
            self.assertEqual(owners["foo/bar/child"], ("a",))

    def test_exact_inside_prefix_is_an_ownership_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "PATH_PREFIX", "value": "foo"},)),
                    minimal_descriptor("b", owned_assets=({"type": "EXACT_PATH", "value": "foo/bar"},)),
                ],
            )
            self.assertIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))

    def test_overlapping_prefixes_are_an_ownership_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "PATH_PREFIX", "value": "foo"},)),
                    minimal_descriptor("b", owned_assets=({"type": "PATH_PREFIX", "value": "foo/bar"},)),
                ],
            )
            self.assertIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))

    def test_logical_identifiers_do_not_overlap_physical_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "LOGICAL_ASSET", "value": "contract/id"},)),
                    minimal_descriptor("b", owned_assets=({"type": "EXACT_PATH", "value": "contract/foo"},)),
                ],
            )
            self.assertNotIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))
            self.assertEqual(classify_changed_assets(root, registry, ["contract/foo"])["contract/foo"], ("b",))

    def test_logical_identifier_duplicates_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("a", owned_assets=({"type": "LOGICAL_ASSET", "value": "contract/foo"},)),
                    minimal_descriptor("b", owned_assets=({"type": "LOGICAL_ASSET", "value": "contract/foo"},)),
                ],
            )
            self.assertIn("MODULE_OWNERSHIP_CONFLICT", validate_registry(root, registry))

    def test_logical_asset_is_a_resolvable_exact_mutation_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor(
                    "a",
                    owned_assets=({"type": "LOGICAL_ASSET", "value": "LOGICAL_TEST_ASSET"},),
                )],
            )
            registry_path = root / ".gpt-codex/framework-modules/REGISTRY.json"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            self.assertEqual(
                classify_changed_assets(root, registry, ["LOGICAL_TEST_ASSET"])["LOGICAL_TEST_ASSET"],
                ("a",),
            )
            decision = route_responsibility(
                root,
                "a",
                "fixture responsibility",
                planned_assets=["LOGICAL_TEST_ASSET"],
            )
            self.assertEqual(decision.outcome, "MODULE_ROUTE")

    def test_logical_asset_does_not_use_path_prefix_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor(
                    "a",
                    owned_assets=({"type": "LOGICAL_ASSET", "value": "LOGICAL_TEST_ASSET"},),
                )],
            )
            owners = classify_changed_assets(root, registry, ["LOGICAL_TEST_ASSET/child"])
            self.assertEqual(owners["LOGICAL_TEST_ASSET/child"], ())

    def test_mixed_namespace_different_owners_is_ambiguous_not_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor(
                        "module-a",
                        owned_assets=({"type": "EXACT_PATH", "value": "contract/foo"},),
                    ),
                    minimal_descriptor(
                        "module-b",
                        owned_assets=({"type": "LOGICAL_ASSET", "value": "contract/foo"},),
                    ),
                ],
            )
            write_registry_file(root, registry)
            self.assertEqual(
                classify_changed_assets(root, registry, ["contract/foo"])["contract/foo"],
                (),
            )
            with self.assertRaises(ModuleRoutingError) as caught:
                route_responsibility(
                    root,
                    "module-a",
                    "fixture responsibility",
                    planned_assets=["contract/foo"],
                )
            self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")

    def test_same_owner_in_physical_and_logical_namespaces_is_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor(
                    "module-a",
                    owned_assets=(
                        {"type": "EXACT_PATH", "value": "contract/foo"},
                        {"type": "LOGICAL_ASSET", "value": "contract/foo"},
                    ),
                )],
            )
            self.assertEqual(
                classify_changed_assets(root, registry, ["contract/foo"])["contract/foo"],
                ("module-a",),
            )

    def test_slash_containing_logical_identifier_routes_without_physical_selector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor(
                    "module-a",
                    owned_assets=({"type": "LOGICAL_ASSET", "value": "contract/foo"},),
                )],
            )
            self.assertEqual(
                classify_changed_assets(root, registry, ["contract/foo"])["contract/foo"],
                ("module-a",),
            )

    def test_physical_only_value_routes_without_logical_selector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [minimal_descriptor(
                    "module-a",
                    owned_assets=({"type": "EXACT_PATH", "value": "contract/foo"},),
                )],
            )
            self.assertEqual(
                classify_changed_assets(root, registry, ["contract/foo"])["contract/foo"],
                ("module-a",),
            )

    def test_unsafe_physical_forms_cannot_use_logical_fallback(self):
        for value in ("/absolute/path", "C:/absolute/path", "safe/../path", "./relative"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                registry = write_registry_fixture(
                    root,
                    [minimal_descriptor(
                        "module-a",
                        owned_assets=({"type": "LOGICAL_ASSET", "value": value},),
                    )],
                )
                write_registry_file(root, registry)
                self.assertEqual(
                    classify_changed_assets(root, registry, [value])[value],
                    (),
                )
                with self.assertRaises(ModuleRoutingError) as caught:
                    route_responsibility(
                        root,
                        "module-a",
                        "fixture responsibility",
                        planned_assets=[value],
                    )
                self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")

    def test_required_tests_are_sorted_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = write_registry_fixture(
                root,
                [
                    minimal_descriptor("b", required_tests=("z-test", ".gpt-codex/tests/test_framework_module_routing.py")),
                    minimal_descriptor("a", required_tests=("a-test", ".gpt-codex/tests/test_framework_module_routing.py")),
                ],
            )
            self.assertEqual(
                required_tests_for_change(root, registry, ["b", "a"]),
                (".gpt-codex/tests/test_framework_module_routing.py", "a-test", "z-test"),
            )

    def test_registry_core_assets_have_exactly_framework_core_owner(self):
        assets = [
            ".gpt-codex/framework-modules/REGISTRY.json",
            ".gpt-codex/framework-modules/modules/framework-core.json",
            ".gpt-codex/schemas/framework-module-registry.schema.json",
            ".gpt-codex/schemas/framework-module.schema.json",
            ".gpt-codex/scripts/framework_module_routing.py",
        ]
        owners = classify_changed_assets(self.root, self.registry, assets)
        for asset in assets:
            self.assertEqual(owners[asset], ("framework-core",))

    def test_single_module_route_is_returned_for_one_verified_owner(self):
        decision = route_responsibility(
            self.root,
            "framework-core",
            "framework governance",
            planned_assets=[".gpt-codex/KERNEL.md"],
        )
        self.assertEqual(decision.outcome, "MODULE_ROUTE")
        self.assertEqual(decision.primary_module, "framework-core")
        self.assertEqual(decision.affected_modules, ("framework-core",))

    def test_missing_or_mismatched_responsibility_is_unresolved(self):
        for responsibility in ("", "not a declared responsibility"):
            with self.subTest(responsibility=responsibility):
                with self.assertRaises(ModuleRoutingError) as caught:
                    route_responsibility(
                        self.root,
                        "framework-core",
                        responsibility,
                        planned_assets=[".gpt-codex/KERNEL.md"],
                    )
                self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")

    def test_reading_a_dependency_does_not_make_a_change_cross_module(self):
        decision = route_responsibility(
            self.root,
            "role-communication",
            "role communication and instruction authority",
            planned_assets=[".gpt-codex/scripts/role_communication.py"],
        )
        self.assertEqual(decision.outcome, "MODULE_ROUTE")

    def test_consumed_output_contract_requires_cross_module_change(self):
        decision = route_responsibility(
            self.root,
            "role-communication",
            "role communication and instruction authority",
            planned_assets=[".gpt-codex/schemas/instruction-envelope.schema.json"],
            contracts_affected=["ROLE_COMMUNICATION_CONTRACT"],
        )
        self.assertEqual(decision.outcome, "CROSS_MODULE_CHANGE_REQUIRED")
        self.assertEqual(decision.primary_module, "role-communication")
        self.assertIn("role-communication", decision.affected_modules)
        self.assertIn("framework-validation", decision.affected_modules)
        self.assertEqual(decision.contracts_affected, ("ROLE_COMMUNICATION_CONTRACT",))
        self.assertTrue(decision.required_tests)

    def test_undeclared_contract_does_not_guess_a_consumer(self):
        with self.assertRaises(ModuleRoutingError) as caught:
            route_responsibility(
                self.root,
                "role-communication",
                "role communication and instruction authority",
                planned_assets=[".gpt-codex/scripts/role_communication.py"],
                contracts_affected=["UNDECLARED_CONTRACT"],
            )
        self.assertEqual(caught.exception.code, "MODULE_ROUTE_UNRESOLVED")

    def test_declared_output_without_consumers_remains_single_module(self):
        decision = route_responsibility(
            self.root,
            "navigation-continuity",
            "project navigation and continuity",
            planned_assets=[".gpt-codex/scripts/continuity_resume.py"],
            contracts_affected=["CONTINUITY_RESUME_CONTRACT"],
        )
        self.assertEqual(decision.outcome, "MODULE_ROUTE")
        self.assertEqual(decision.affected_modules, ("navigation-continuity",))

    def test_foreign_owned_asset_is_classified_as_cross_module(self):
        decision = route_responsibility(
            self.root,
            "framework-core",
            "framework governance",
            planned_assets=[".gpt-codex/release/consumer-projection-manifest.json"],
        )
        self.assertEqual(decision.outcome, "CROSS_MODULE_CHANGE_REQUIRED")
        self.assertIn("framework-core", decision.affected_modules)
        self.assertIn("release-projection", decision.affected_modules)

    def test_inactive_or_unregistered_candidate_fails_closed(self):
        for candidate in ("inactive-module", "not-registered"):
            with self.assertRaises(ModuleRoutingError) as caught:
                route_responsibility(self.root, candidate, "unregistered responsibility")
            self.assertIn(caught.exception.code, {"MODULE_ROUTE_UNRESOLVED", "MODULE_NOT_REGISTERED"})


if __name__ == "__main__":
    unittest.main()
