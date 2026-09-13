import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ConsumerWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.operational_docs = "\n".join(
            (
                (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8"),
                (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8"),
            )
        )
        cls.corpus = "\n".join(
            (
                (ROOT / "AGENTS.md").read_text(encoding="utf-8"),
                (ROOT / ".gpt-codex" / "README.md").read_text(encoding="utf-8"),
                (ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md").read_text(encoding="utf-8"),
                (ROOT / ".gpt-codex" / "builtins" / "skills" / "framework-compatibility" / "SKILL.md").read_text(
                    encoding="utf-8"
                ),
                (ROOT / ".gpt-codex" / "project-template" / "README.md").read_text(encoding="utf-8"),
            )
        )

    def test_fixed_framework_folder_is_the_consumer_setup_rule(self):
        self.assertIn("Consumer Workspace Setup", self.corpus)
        self.assertIn("Project is authoritative", self.corpus)
        self.assertIn("Framework is advisory", self.corpus)
        self.assertIn("gpt-codex-framework", self.corpus)
        self.assertIn("framework-source", self.corpus)
        self.assertNotIn("通用开发框架管理", self.corpus)

    def test_framework_core_is_read_only_and_adoption_is_a_snapshot_copy(self):
        self.assertIn("Framework Kernel", self.corpus)
        self.assertIn("READ ONLY", self.corpus)
        self.assertIn("Framework Built-ins", self.corpus)
        self.assertIn("versioned snapshot", self.corpus)
        self.assertIn("Framework upgrades", self.corpus)
        self.assertIn("does not automatically modify the project", self.corpus)

    def test_compatibility_scan_results_and_one_time_migration_are_explicit(self):
        for result in (
            "NO_ACTION",
            "OPTIONAL_REUSE",
            "RECOMMENDED_UPGRADE",
            "REQUIRED_MIGRATION",
            "CONFLICT",
        ):
            self.assertIn(result, self.corpus)
        self.assertIn("remove the old versioned", self.corpus)
        self.assertIn("add the fixed", self.corpus)
        self.assertIn("save", self.corpus)

    def test_versioned_framework_folder_is_not_a_long_lived_binding(self):
        self.assertIn("must not", self.corpus.lower())
        self.assertIn("v2.0.2-bootstrap", self.corpus)
        self.assertIn("not recommended", self.corpus.lower())

    def test_operational_docs_state_framework_publishes_project_decides(self):
        self.assertIn("Framework publishes; Project decides.", self.operational_docs)
        self.assertIn("read-only compatibility evaluation", self.operational_docs)
        self.assertIn("explicit Project decision", self.operational_docs)
        self.assertIn("separately authorized local mutation or migration", self.operational_docs)

    def test_operational_docs_state_upgrade_evaluation_is_not_adoption(self):
        self.assertIn("Compatibility evaluation never adopts or mutates.", self.operational_docs)
        self.assertIn("never automatically adopts, propagates, or mutates a Project", self.operational_docs)

    def test_operational_docs_list_exact_separation_failure_vocabulary(self):
        for outcome in (
            "CROSS_PROJECT_CONTEXT_MISMATCH",
            "GITHUB_REPOSITORY_MISMATCH",
            "PROJECT_IDENTITY_INVALID",
            "PROJECT_AUTHORITY_BOUNDARY_VIOLATION",
            "FRAMEWORK_ADOPTION_NOT_AUTHORIZED",
            "MODULE_ROUTE_UNRESOLVED",
            "NAVIGATION_REPOSITORY_MISMATCH",
        ):
            self.assertIn(outcome, self.operational_docs)

    def test_existing_v25_project_is_no_migration(self):
        self.assertIn("Valid v2.5.0 projects using the current fixed Framework source remain `NO_MIGRATION`", self.operational_docs)

    def test_versioned_auxiliary_framework_folder_requires_explicit_migration_to_fixed_source(self):
        self.assertIn("versioned auxiliary Framework folder requires `EXPLICIT_MIGRATION`", self.operational_docs)
        self.assertIn("fixed unversioned Framework source", self.operational_docs)

    def test_operational_docs_keep_p0_4_as_an_unimplemented_boundary(self):
        self.assertIn("No automatic propagation, adoption, or P0-4 mechanism exists.", self.operational_docs)
        self.assertIn("P0-4 remains interface-only.", self.operational_docs)


if __name__ == "__main__":
    unittest.main()
