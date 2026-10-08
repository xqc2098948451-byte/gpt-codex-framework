import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VALID_ID = "11111111-1111-4111-8111-111111111111"


def load_instruction_envelope():
    path = SCRIPTS / "instruction_envelope.py"
    if not path.is_file():
        raise AssertionError("instruction_envelope.py production behavior is not implemented")
    spec = importlib.util.spec_from_file_location("instruction_envelope_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionEnvelopeTests(unittest.TestCase):
    def test_fix_builder_requires_explicit_correlated_adjudication(self):
        ie = load_instruction_envelope()
        mutation = ie.build_instruction_envelope("EXECUTION_INSTRUCTION", VALID_ID, "Example", 7, "2.8.0",
            target_work_unit="WU-1", expected_base_sha="a" * 40, issuer_role="GPT_ORCHESTRATOR",
            executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR",
            authorized_actions=["READ", "MUTATE_APPROVED_SCOPE"], forbidden_actions=["AUTHORIZE"],
            scope_paths=["docs/approved.md"])
        finding = {"result_id": "22222222-2222-4222-8222-222222222222", "result_message_type": "REVIEW_FINDING",
                   "responder_role": "CODEX_REVIEWER", "review_target_revision": "a" * 40,
                   "finding_ids": ["F-1"], "evidence_refs": ["reproduction"], "fix_round": 0}
        decision = {"evidence_id": "decision", "subject": "REMEDIATION_ADJUDICATION", "decision": "ACCEPT",
                    "finding_ids": ["F-1"], "basis_type": "CONCRETE_REGRESSION_EVIDENCE",
                    "basis_refs": ["reproduction"], "adjudicated_at_revision": 7}
        basis = {"reproduction": {"basis_type": "CONCRETE_REGRESSION_EVIDENCE", "finding_ids": ["F-1"],
                                  "state_revision": 7, "failing": True}}
        fix = ie.build_fix_instruction(mutation, finding, decision, basis, current_state_revision=7,
                                       approved_scope={"docs/approved.md"})
        self.assertEqual(fix["instruction_type"], "FIX_INSTRUCTION")
        self.assertEqual(fix["in_response_to_result_id"], finding["result_id"])
        self.assertEqual(fix["remediation_decision_ref"], "decision")
        self.assertEqual(fix["fix_round"], 1)
        with self.assertRaisesRegex(ValueError, "REMEDIATION_DECISION"):
            ie.build_fix_instruction(mutation, finding, {}, basis, current_state_revision=7,
                                     approved_scope={"docs/approved.md"})

    def test_compact_handoff_keeps_complete_binding_in_one_block(self):
        ie = load_instruction_envelope()
        instruction = ie.build_instruction_envelope("EXECUTION_INSTRUCTION", VALID_ID, "Example", 7, "2.8.0",
            target_work_unit="WU-1", expected_base_sha="a" * 40, issuer_role="GPT_ORCHESTRATOR",
            executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR", authorized_actions=["READ"],
            forbidden_actions=["AUTHORIZE"], scope_paths=["docs/approved.md"],
            target_github_repository_id="12", target_github_repository_full_name="owner/project")
        locator = {"repository": "owner/project", "commit_sha": "b" * 40,
                   "path": ie.instruction_artifact_relative_path(instruction["instruction_id"]), "blob_sha": "c" * 40}
        text = ie.render_compact_codex_handoff(instruction, locator, goal="Read approved document",
                                             stop_conditions=["STOP on authority drift"])
        self.assertEqual(text.count("```text"), 1)
        self.assertIn("STATE_REVISION: 7", text)
        self.assertIn("CODEX_IMPLEMENTER", text)
        self.assertIn("docs/approved.md", text)
        self.assertIn("STOP on authority drift", text)
        self.assertIn("b" * 40, text)

    def test_machine_pre_request_derives_correlation_without_issuing_pass(self):
        ie = load_instruction_envelope()
        from validate_project import validate_pre_execution_review_request
        mutation = ie.build_instruction_envelope(
            "EXECUTION_INSTRUCTION", VALID_ID, "Example", 7, "2.8.0",
            target_work_unit="WU-1", expected_base_sha="a" * 40,
            issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER",
            return_role="GPT_ORCHESTRATOR", authorized_actions=["READ", "MUTATE_APPROVED_SCOPE"],
            forbidden_actions=["AUTHORIZE"], scope_paths=["docs/approved.md"],
        )
        request = ie.build_pre_execution_review_request(
            mutation, current_state_revision=7, approved_scope={"docs/approved.md"},
            runtime_fresh_context_verified=True, runtime_input_source_kinds=["GOVERNED_INSTRUCTION"],
        )
        self.assertEqual(request["review_target_revision"], "a" * 40)
        self.assertEqual(request["in_response_to_instruction_id"], mutation["instruction_id"])
        self.assertEqual(validate_pre_execution_review_request(mutation, request, current_state_revision=7), [])
        self.assertNotIn("status", request)
        with self.assertRaisesRegex(ValueError, "REQUEST_CONSTRUCTION_BLOCKED"):
            ie.build_pre_execution_review_request(mutation, current_state_revision=8,
                approved_scope={"docs/approved.md"}, runtime_fresh_context_verified=True,
                runtime_input_source_kinds=["GOVERNED_INSTRUCTION"])

    def test_work_unit_candidate_locks_local_bytes_without_authorizing_execution(self):
        ie = load_instruction_envelope()
        import subprocess
        project = ROOT.parent
        state = json.loads((ROOT / "STATE.json").read_text(encoding="utf-8"))
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=project, text=True).strip()
        candidate = ie.build_work_unit_candidate(project,
            {"work_unit_id": "builder-check", "goal": "Check candidate materialization",
             "scope": {"owned_paths": [".gpt-codex/scripts/result_return.py"]}, "acceptance": ["candidate only"]},
            predecessor_ref={"path": ".gpt-codex/work-units/framework-staged-closure-group-a-001.json", "sha": head},
            expected_state_revision=state["revision"], expected_head_sha=head,
            approved_scope={".gpt-codex/scripts/result_return.py"})
        import hashlib
        self.assertEqual(candidate["sha256"], hashlib.sha256(candidate["bytes"]).hexdigest())
        self.assertEqual(candidate["work_unit"]["state"], "DRAFT")
        self.assertFalse(candidate["work_unit"]["authorization"]["implementation_authorized"])
        self.assertEqual(candidate["work_unit"]["basis_state_revision"], state["revision"])
        self.assertEqual(candidate["byte_count"], len(candidate["bytes"]))
        with self.assertRaisesRegex(ValueError, "STALE_STATE_REVISION"):
            ie.build_work_unit_candidate(project, {"work_unit_id": "builder-check"},
                predecessor_ref={"path": ".gpt-codex/work-units/framework-staged-closure-group-a-001.json", "sha": head},
                expected_state_revision=state["revision"] + 1, expected_head_sha=head, approved_scope=set())

    def test_review_dispatch_requires_independent_freshness_and_allowed_sources(self):
        ie = load_instruction_envelope()
        args = dict(instruction_type="REVIEW_REQUEST", target_project_context_id="ctx", target_project_name="Project", expected_state_revision=1, framework_version="2.0.0", target_work_unit="WU-1", expected_base_sha="a" * 40, issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_REVIEWER", return_role="GPT_ORCHESTRATOR", target_github_repository_id="repo")
        for freshness, sources in ((None, ["REPOSITORY_CONTENT"]), (False, ["REPOSITORY_CONTENT"]), (True, ["IMPLEMENTER_RAW_TRANSCRIPT"])):
            with self.subTest(freshness=freshness, sources=sources):
                with self.assertRaisesRegex(ValueError, "ROLE_DISPATCH = BLOCKED"):
                    ie.build_instruction_envelope(**args, runtime_fresh_context_verified=freshness, runtime_input_source_kinds=sources)
        envelope = ie.build_instruction_envelope(**args, runtime_fresh_context_verified=True, runtime_input_source_kinds=["REPOSITORY_CONTENT", "ACCEPTED_FINDING"])
        self.assertNotIn("runtime_input_source_kinds", envelope)
        self.assertNotIn("runtime_fresh_context_verified", envelope)
    def test_instruction_schema_and_template_exist_with_context_contract(self):
        schema_path = ROOT / "schemas" / "instruction-envelope.schema.json"
        template_path = ROOT / "project-template" / "INSTRUCTION_ENVELOPE.template.json"
        self.assertTrue(schema_path.is_file())
        self.assertTrue(template_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        template = json.loads(template_path.read_text(encoding="utf-8"))
        for key in (
            "instruction_id",
            "instruction_type",
            "target_project_context_id",
            "target_project_name",
            "expected_state_revision",
            "framework_version",
        ):
            self.assertIn(key, schema["properties"])
            self.assertIn(key, template)

    def test_builder_generates_all_required_fields_without_manual_identity(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.1.0",
        )
        for key in (
            "instruction_id",
            "instruction_type",
            "target_project_context_id",
            "target_project_name",
            "expected_state_revision",
            "framework_version",
        ):
            self.assertIn(key, envelope)
        self.assertNotEqual(envelope["instruction_id"], "NONE")

    def test_optional_work_unit_locator_has_one_consistent_shape_and_preserves_legacy_building(self):
        ie = load_instruction_envelope()
        locator = {"path": ".gpt-codex/work-units/WU-1.json", "sha": "a" * 40}
        envelope = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT", target_project_context_id=VALID_ID,
            target_project_name="Example Project", expected_state_revision=7,
            framework_version="2.1.0", target_work_unit="WU-1", target_work_unit_ref=locator,
        )
        self.assertEqual(envelope["target_work_unit_ref"], locator)
        legacy = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT", target_project_context_id=VALID_ID,
            target_project_name="Example Project", expected_state_revision=7, framework_version="2.1.0",
        )
        self.assertNotIn("target_work_unit_ref", legacy)
        for invalid in ({"sha": "a" * 40}, {"path": ".gpt-codex/WU.json"},
                        {"path": "", "sha": "a" * 40}, {"path": ".gpt-codex/WU.json", "sha": "bad"},
                        {"path": ".gpt-codex/WU.json", "sha": "a" * 40, "extra": True}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    ie.build_instruction_envelope(
                        instruction_type="WORK_UNIT", target_project_context_id=VALID_ID,
                        target_project_name="Example Project", expected_state_revision=7,
                        framework_version="2.1.0", target_work_unit_ref=invalid,
                    )
        schema = json.loads((ROOT / "schemas" / "instruction-envelope.schema.json").read_text(encoding="utf-8"))
        template = json.loads((ROOT / "project-template" / "INSTRUCTION_ENVELOPE.template.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["properties"]["target_work_unit_ref"]["required"]), {"path", "sha"})
        self.assertEqual(template["target_work_unit_ref"], {"path": "REPOSITORY_RELATIVE_PATH", "sha": "40_HEX_GIT_SHA"})

    def test_instruction_is_one_copyable_block_with_envelope_first(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="WORK_UNIT",
            target_project_context_id=VALID_ID,
            target_project_name="Example Project",
            expected_state_revision=7,
            framework_version="2.1.0",
        )
        rendered = ie.render_codex_instruction(
            envelope,
            "Run the authorized task body.",
            {"execution_strategy": "串行", "approval": "需要 GPT 判断"},
        )
        self.assertTrue(rendered.startswith("INSTRUCTION_ID:"))
        self.assertLess(rendered.index("INSTRUCTION_ID:"), rendered.index("Run the authorized task body."))
        self.assertIn("TARGET_PROJECT_CONTEXT_ID: " + VALID_ID, rendered)
        self.assertEqual(rendered.count("Run the authorized task body."), 1)

    def test_legacy_bootstrap_carries_target_project_id(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="Example Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_target_project_id="LEGACY-001",
        )
        self.assertEqual(envelope["bootstrap_target_project_id"], "LEGACY-001")

    def test_challenge_bound_bootstrap_carries_exact_challenge(self):
        ie = load_instruction_envelope()
        envelope = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="New Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_challenge_id="challenge-opaque-001",
        )
        self.assertEqual(envelope["bootstrap_challenge_id"], "challenge-opaque-001")

    def test_normal_instruction_requires_target_and_challenge_bootstrap_is_identity_only(self):
        ie = load_instruction_envelope()
        with self.assertRaises(ValueError):
            ie.build_instruction_envelope(
                instruction_type="WORK_UNIT",
                target_project_context_id=None,
                target_project_name="Example Project",
                expected_state_revision=7,
                framework_version="2.1.0",
            )
        challenge = ie.build_instruction_envelope(
            instruction_type="PROJECT_CONTEXT_BOOTSTRAP",
            target_project_context_id=None,
            target_project_name="New Project",
            expected_state_revision=None,
            framework_version="2.1.0",
            bootstrap_challenge_id="challenge-opaque-001",
            bootstrap_phase="CHALLENGE_BOUND",
        )
        with self.assertRaises(ValueError):
            ie.render_codex_instruction(
                challenge,
                "run business task",
                {"execution_strategy": "串行", "approval": "需要 GPT 判断"},
            )


    def test_minimal_renderer_preserves_canonical_envelope(self):
        module = load_instruction_envelope()
        envelope = {"instruction_id": "i", "instruction_type": "EXECUTION_INSTRUCTION",
                    "target_work_unit": "WU", "expected_base_sha": "a" * 40}
        before = dict(envelope)
        text = module.render_minimal_codex_task(envelope, goal="g", scope=["s"], constraints=["c"], done=["d"])
        self.assertEqual(envelope, before)
        self.assertIn("INSTRUCTION_ID: i", text)
        self.assertIn("BASE_SHA: " + "a" * 40, text)


if __name__ == "__main__":
    unittest.main()


class ContractRepairTask2Tests(unittest.TestCase):
    def mutation_kwargs(self, instruction_type="EXECUTION_INSTRUCTION"):
        return dict(instruction_type=instruction_type, target_project_context_id="ctx", target_project_name="Project", expected_state_revision=1, framework_version="2.7.2+fix.1", issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR", authorized_actions=["MUTATE_APPROVED_SCOPE"])

    def test_scope_paths_are_required_nonempty_relative_unique_selectors(self):
        ie = load_instruction_envelope()
        kwargs = self.mutation_kwargs("FIX_INSTRUCTION")
        envelope = ie.build_instruction_envelope(**kwargs, scope_paths=[".gpt-codex/scripts/validate_project.py"])
        self.assertEqual(envelope["scope_paths"], [".gpt-codex/scripts/validate_project.py"])
        for invalid in ([], ["x", "x"], ["/absolute"], ["C:/drive"], ["a\\b"], ["."], [".."], ["a//b"], ["a/../b"]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    ie.build_instruction_envelope(**kwargs, scope_paths=invalid)

    def test_mutating_instruction_types_require_scope_paths(self):
        ie = load_instruction_envelope()
        for instruction_type in ("EXECUTION_INSTRUCTION", "FIX_INSTRUCTION", "RECONCILIATION_REQUEST"):
            with self.subTest(instruction_type=instruction_type), self.assertRaisesRegex(ValueError, "SCOPE_PATHS_REQUIRED"):
                ie.build_instruction_envelope(**self.mutation_kwargs(instruction_type))

    def test_remediation_ref_and_strict_semver_contract(self):
        ie = load_instruction_envelope()
        base = self.mutation_kwargs("FIX_INSTRUCTION")
        base["scope_paths"] = [".gpt-codex/STATE.json"]
        envelope = ie.build_instruction_envelope(**base, remediation_decision_ref="DECISION-001")
        self.assertEqual(envelope["remediation_decision_ref"], "DECISION-001")
        for value in ("", " ", 1):
            with self.subTest(ref=value), self.assertRaisesRegex(ValueError, "INVALID_REMEDIATION_DECISION_REF"):
                ie.build_instruction_envelope(**base, remediation_decision_ref=value)
        for version in ("2.7.2", "2.7.2+fix.1", "2.7.2-alpha", "2.7.2-alpha.1+build.01"):
            with self.subTest(version=version):
                self.assertEqual(ie.build_instruction_envelope(**{**base, "framework_version": version})["framework_version"], version)
        for version in ("02.7.2", "2.07.2", "2.7.02", "2.7.2-..", "2.7.2-01", "2.7.2+", "2.7"):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "INVALID_FRAMEWORK_VERSION"):
                ie.build_instruction_envelope(**{**base, "framework_version": version})
