import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ConsumerWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        self.assertIn("通用开发框架管理", self.corpus)

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


if __name__ == "__main__":
    unittest.main()
