import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".gpt-codex" / "scripts"))

from framework_feedback import evaluate_structure_change  # noqa: E402


class HarnessReductionGateTests(unittest.TestCase):
    def test_capability_preservation_precedes_measurable_benefit(self):
        before = {"build", "test", "deploy"}

        self.assertEqual(
            evaluate_structure_change(before, before, {"complexity_decreased": True}),
            "ALLOW",
        )
        for evidence in (
            {"complexity_decreased": True},
            {"responsibility_clearer": True},
            {"deployment_maintenance_testing_improved": True},
            {
                "complexity_decreased": True,
                "responsibility_clearer": True,
                "deployment_maintenance_testing_improved": True,
            },
        ):
            with self.subTest(evidence=evidence):
                self.assertEqual(
                    evaluate_structure_change(before, {"build", "test"}, evidence),
                    "CAPABILITY_REGRESSION",
                )
        self.assertEqual(
            evaluate_structure_change({"build", "test"}, {"build", "test"}, {}),
            "NO_BENEFIT",
        )

    def test_each_recognized_benefit_is_strict_and_capability_supersets_are_allowed(self):
        before = {"build", "test"}
        after = {"build", "test", "deploy"}

        for benefit in (
            "complexity_decreased",
            "responsibility_clearer",
            "deployment_maintenance_testing_improved",
        ):
            with self.subTest(benefit=benefit):
                self.assertEqual(evaluate_structure_change(before, before, {benefit: True}), "ALLOW")
        self.assertEqual(
            evaluate_structure_change(before, before, {"complexity_decreased": "yes"}),
            "NO_BENEFIT",
        )
        self.assertEqual(
            evaluate_structure_change(before, after, {"responsibility_clearer": True}),
            "ALLOW",
        )
        self.assertEqual(evaluate_structure_change(before, after, {}), "NO_BENEFIT")
        evidence = {"responsibility_clearer": True, "extra_observation": ["unchanged"]}
        before_snapshot = set(before)
        after_snapshot = set(after)
        evidence_snapshot = deepcopy(evidence)

        self.assertEqual(evaluate_structure_change(before, after, evidence), "ALLOW")
        self.assertEqual(before, before_snapshot)
        self.assertEqual(after, after_snapshot)
        self.assertEqual(evidence, evidence_snapshot)

    def test_structure_and_closure_templates_are_bounded_and_complete(self):
        rules = (ROOT / ".gpt-codex/project-template/.harness/RULES.template.md").read_text(encoding="utf-8")
        reasoning = (ROOT / ".gpt-codex/project-template/.harness/REASONING.template.md").read_text(encoding="utf-8")
        state = (ROOT / ".gpt-codex/project-template/.harness/STATE.template.md").read_text(encoding="utf-8")

        for section in ("## Highest Principle", "## Semantic Roots", "## Production Boundary", "## Stable Project Rules", "## Codex Task Protocol"):
            self.assertIn(section, rules)
        self.assertIn("## Structure Evolution", rules)
        for rule in (
            "- Responsibility before structure.",
            "- Do not split by file count, line count, agent count, or parallelism convenience.",
            "- Split only for durable responsibility/runtime/security/testing boundaries.",
            "- Merge/delete when layers always change together, are trivial wrappers, or duplicate ownership.",
            "- AFTER_CAPABILITIES must contain every required BEFORE_CAPABILITY.",
            "- Do not reorganize a stable structure for cosmetic reasons.",
        ):
            self.assertIn(rule, rules)
        for section in ("## Strategy", "## Decision Records", "## Process Reviews", "## Execution Record Format", "## Structure Review Format"):
            self.assertIn(section, reasoning)
        for label in ("MOMENT:", "CHANGE:", "RESPONSIBILITY_REASON:", "BEFORE_CAPABILITIES:", "AFTER_CAPABILITIES:", "MEASURABLE_BENEFIT:", "RESULT:"):
            self.assertIn(label, reasoning)
        self.assertIn("## Governed Change Decision Format", reasoning)
        for label in ("CURRENT_AUTHORITY:", "EXISTING_CAPABILITY:", "EXISTING_AUTHORITY_REFS:", "ROOT_CAUSE:", "REUSE_PATH:", "MINIMUM_DELTA:", "NEW_MECHANISM_REQUIRED:"):
            self.assertIn(label, reasoning)
        for rule in ("EXISTING -> reuse", "PARTIAL -> extend existing capability", "MISSING -> test existing responsibility/module before adding mechanism"):
            self.assertIn(rule, reasoning)
        for forbidden in ("RAW_PROMPT", "PROMPT", "CHAIN_OF_THOUGHT", "PRIVATE_REASONING", "SCRATCHPAD", "REASONING_TRANSCRIPT", "TOKEN_TRACE"):
            self.assertNotIn(forbidden, reasoning)
        self.assertIn("## Closure Rule", state)
        for item in ("CURRENT_TASK = NONE", "BLOCKER = NONE", "PENDING_RESULT_REF = NONE", "NEXT_ACTION = MAINTENANCE", "Transient debugging/scratch state is removed or archived outside the active state view."):
            self.assertIn(item, state)

    def test_reduction_gate_test_is_management_only(self):
        manifest = json.loads((ROOT / ".gpt-codex/release/consumer-projection-manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["paths"][".gpt-codex/tests/test_harness_reduction_gate.py"],
            "MANAGEMENT_ONLY",
        )

    def test_verification_evidence_transport_contract_reuses_retained_facts(self):
        verification = (ROOT / ".gpt-codex/builtins/skills/verification/SKILL.md").read_text(encoding="utf-8")

        for fact in ("command", "tested SHA", "exit status", "test count", "failures", "errors", "concise relevant summary", "UNKNOWN"):
            self.assertIn(fact, verification)
        for rerun_cause in ("source/test change", "material environment change", "incomplete execution", "unauthentic evidence"):
            self.assertIn(rerun_cause, verification)
        for transport_only_case in ("console capture was lost", "report formatting", "must NOT be rerun"):
            self.assertIn(transport_only_case, verification)
        for boundary in ("Transport does not establish verification success", "No result platform", "no telemetry authority"):
            self.assertIn(boundary, verification)


if __name__ == "__main__":
    unittest.main()
