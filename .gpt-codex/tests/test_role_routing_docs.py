import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = (
    ROOT / "AGENTS.md",
    ROOT / ".gpt-codex" / "README.md",
    ROOT / ".gpt-codex" / "BOOTSTRAP_PROMPT.md",
)
TEXT = "\n".join(path.read_text(encoding="utf-8") for path in DOCS)


class RoleRoutingDocumentationTests(unittest.TestCase):
    def test_human_routing_labels_are_preserved(self):
        for label in ("[USER_LOCAL]", "[CODEX]", "[RETURN_TO_GPT]", "[INFO]"):
            with self.subTest(label=label):
                self.assertIn(label, TEXT)

    def test_labels_are_transport_hints_and_machine_fields_are_authoritative(self):
        self.assertIn("transport/routing hints", TEXT)
        self.assertIn("do not replace envelope fields", TEXT)
        self.assertIn("machine role", TEXT)
        self.assertIn("authorized_actions", TEXT)

    def test_exact_roles_and_wire_type_ownership_are_documented(self):
        for role in (
            "GPT_ORCHESTRATOR", "GPT_REVIEWER", "CODEX_IMPLEMENTER", "CODEX_REVIEWER",
            "USER_APPROVER", "USER_LOCAL", "INFORMATION_ONLY",
        ):
            with self.subTest(role=role):
                self.assertIn(role, TEXT)
        self.assertIn("instruction_type", TEXT)
        self.assertIn("result_message_type", TEXT)
        self.assertIn("No generic `message_type`", TEXT)

    def test_finding_decision_fix_lifecycle_is_documented(self):
        for phrase in (
            "REVIEW_FINDING",
            "GPT/User",
            "FIX_INSTRUCTION",
            "CODEX_IMPLEMENTER",
            "REVIEW_RESULT",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, TEXT)

    def test_legacy_route_and_execution_confirmation_boundaries_are_documented(self):
        for phrase in (
            "bounded",
            "fail-closed",
            "legacy",
            "instruction issuance is not execution confirmation",
            "remote review visibility is not instruction delivery",
            "Handoff",
            "derived",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), TEXT.lower())


if __name__ == "__main__":
    unittest.main()
