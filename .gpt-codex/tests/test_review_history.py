import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from git_continuity import validate_review_history_operation, validate_review_revision


class ReviewHistoryTests(unittest.TestCase):
    def test_new_review_revision_is_append_only_descendant(self):
        reviewed = "a" * 40
        fixed = "b" * 40
        ancestry = {(reviewed, fixed)}
        self.assertEqual(
            validate_review_revision(reviewed, fixed, lambda old, new: (old, new) in ancestry),
            [],
        )

    def test_replaced_review_revision_is_reconciliation_required(self):
        errors = validate_review_revision("a" * 40, "b" * 40, lambda _old, _new: False)
        self.assertIn("RECONCILIATION_REQUIRED", errors)
        self.assertIn("REVIEWED_REVISION_NOT_ANCESTOR", errors)

    def test_history_rewrite_and_publication_are_forbidden_for_formal_review(self):
        for operation in ("AMEND", "REBASE", "RESET_REVIEWED", "FORCE_PUSH", "PUBLISH"):
            with self.subTest(operation=operation):
                errors = validate_review_history_operation("DESIGN", operation)
                self.assertIn("REVIEW_HISTORY_REWRITE_FORBIDDEN", errors)


if __name__ == "__main__":
    unittest.main()
