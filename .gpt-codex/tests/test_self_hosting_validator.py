import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".gpt-codex" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
VALIDATOR = ROOT / ".gpt-codex" / "scripts" / "validate_project.py"
FROZEN_ZIP = ROOT / "dist" / "gpt-codex-framework-v2.2.0-bootstrap.zip"
FROZEN_FIXTURE = ROOT / ".gpt-codex" / "tests" / "fixtures" / "frozen_v220_validate_project.py"


def run_validator(project_root: Path, validator: Path = VALIDATOR) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(validator), str(project_root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def management_control() -> dict:
    control = json.loads((ROOT / ".gpt-codex" / "CONTROL.json").read_text(encoding="utf-8"))
    control["extensions"] = {
        "skills": [],
        "guardrails": [
            {"id": "github-repository-binding", "source": "builtin", "enabled": True, "version": "1.0.0"},
        ],
        "fitness": [],
    }
    return control


def write_project(root: Path, control: dict) -> None:
    gov = root / ".gpt-codex"
    gov.mkdir(parents=True)
    (gov / "CONTROL.json").write_text(json.dumps(control), encoding="utf-8")
    (gov / "STATE.json").write_text(json.dumps({
        "kernel_version": "2.0.0",
        "schema_version": 1,
        "project_id": control["project_id"],
        "revision": 0,
        "state": "VERIFYING",
        "blockers": [],
        "evidence_refs": [],
        "continuity": {
            "current_remote_ref": None,
            "latest_verified_remote_sha": None,
            "latest_synced_state_revision": 0,
            "last_verified_result_ref": None,
            "sync_status": "SYNC_PENDING",
        },
    }), encoding="utf-8")


def governed_envelopes(control: dict) -> tuple[dict, dict, dict, dict, dict]:
    base_sha = "a" * 40
    state = {"project_id": control["project_id"], "revision": 3}
    work_unit = {"project_id": control["project_id"], "work_unit_id": "WU-GOVERNED", "state": "AUTHORIZED", "basis_state_revision": 3}
    mutation = {
        "instruction_id": "11111111-1111-4111-8111-111111111111", "instruction_type": "EXECUTION_INSTRUCTION",
        "issuer_role": "GPT_ORCHESTRATOR", "executor_role": "CODEX_IMPLEMENTER", "return_role": "GPT_ORCHESTRATOR",
        "target_project_context_id": control["project_context_id"], "target_github_repository_id": control["github"]["repository_id"],
        "target_github_repository_full_name": control["github"]["repository_full_name"], "target_work_unit": "WU-GOVERNED",
        "expected_state_revision": 3, "expected_base_sha": base_sha, "expected_remote_ref": "refs/heads/main",
        "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"], "forbidden_actions": [],
        "scope_paths": [],
    }
    request = {
        **mutation, "instruction_id": "22222222-2222-4222-8222-222222222222", "instruction_type": "REVIEW_REQUEST",
        "executor_role": "CODEX_REVIEWER", "authorized_actions": ["READ", "TEST", "VALIDATE", "REPORT"],
        "in_response_to_instruction_id": mutation["instruction_id"], "review_target_revision": base_sha,
    }
    result = {
        "result_message_type": "REVIEW_RESULT", "responder_role": "CODEX_REVIEWER", "status": "PASS",
        "response_to_instruction_id": request["instruction_id"], "review_target_revision": base_sha,
        "source_project_context_id": control["project_context_id"],
        "source_github_repository_id": control["github"]["repository_id"],
        "source_github_repository_full_name": control["github"]["repository_full_name"],
        "current_remote_ref": mutation["expected_remote_ref"],
    }
    return state, work_unit, mutation, request, result


def commit_repository(root: Path, message: str) -> str:
    for command in (("git", "init"), ("git", "config", "user.email", "test@example.com"),
                    ("git", "config", "user.name", "Test"), ("git", "add", "."), ("git", "commit", "-m", message)):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    return subprocess.run(("git", "rev-parse", "HEAD"), cwd=root, check=True, capture_output=True, text=True).stdout.strip()


class SelfHostingValidatorTests(unittest.TestCase):
    def test_task8_successor_seed_has_exact_current_four_path_authority(self):
        from validate_project import _derived_schema_errors

        seed_path = ROOT / ".gpt-codex/work-units/framework-group-b-control-plane-seed-001.json"
        expected_paths = {
            ".gpt-codex/STATE.json",
            ".gpt-codex/work-units/framework-baseline-stabilization-001.json",
            ".gpt-codex/evidence/results/RESULT-BASELINE-STABILIZATION-POSTEXEC-FINDING.json",
            ".gpt-codex/evidence/results/RESULT-FIX-REMEDIATION-LIFECYCLE-CONTRACT-RECONCILIATION.json",
        }
        self.assertTrue(seed_path.is_file(), "fresh Task-8 successor must be materialized")
        seed = json.loads(seed_path.read_text(encoding="utf-8"))
        self.assertEqual(seed["work_unit_id"], "framework-group-b-control-plane-seed-001")
        self.assertEqual(seed["state"], "AUTHORIZED")
        self.assertEqual(seed["basis_state_revision"], 16)
        self.assertEqual(seed["scope"]["excluded_paths"], [])
        self.assertEqual(set(seed["scope"]["owned_paths"]), expected_paths)
        self.assertEqual(len(seed["scope"]["owned_paths"]), 4)
        self.assertNotIn(".gpt-codex/work-units/framework-group-b-control-plane-seed-001.json", seed["scope"]["owned_paths"])
        self.assertEqual(_derived_schema_errors(seed, "work-unit"), [])
        def assert_exact_successor(candidate, revision=16):
            self.assertEqual(candidate["work_unit_id"], "framework-group-b-control-plane-seed-001")
            self.assertEqual(candidate["state"], "AUTHORIZED")
            self.assertEqual(candidate["basis_state_revision"], revision)
            self.assertEqual(set(candidate["scope"]["owned_paths"]), expected_paths)
            self.assertEqual(len(candidate["scope"]["owned_paths"]), 4)
            self.assertEqual(candidate["scope"]["excluded_paths"], [])
            self.assertNotIn(".gpt-codex/work-units/framework-group-b-control-plane-seed-001.json", candidate["scope"]["owned_paths"])
            self.assertEqual(candidate["artifact_refs"], seed["artifact_refs"])
            self.assertEqual(_derived_schema_errors(candidate, "work-unit"), [])
        for invalid in (
            {**seed, "scope": {"owned_paths": seed["scope"]["owned_paths"][:-1], "excluded_paths": []}},
            {**seed, "scope": {"owned_paths": [*seed["scope"]["owned_paths"][:-1], ".gpt-codex/evidence/results/OTHER.json"], "excluded_paths": []}},
            {**seed, "scope": {"owned_paths": [*seed["scope"]["owned_paths"], "arbitrary.txt"], "excluded_paths": []}},
            {**seed, "scope": {"owned_paths": [*seed["scope"]["owned_paths"], ".gpt-codex/work-units/framework-group-b-control-plane-seed-001.json"], "excluded_paths": []}},
            {**seed, "state": "PROPOSED"},
            {**seed, "basis_state_revision": 17},
            {**seed, "artifact_refs": {**seed["artifact_refs"], "design": {"path": "design.md", "sha": "0" * 40}}},
        ):
            with self.assertRaises(AssertionError):
                assert_exact_successor(invalid)
        with self.assertRaises(AssertionError):
            assert_exact_successor(seed, revision=17)
        historical = json.loads((ROOT / ".gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json").read_text(encoding="utf-8"))
        with self.assertRaises(AssertionError):
            assert_exact_successor(historical)

    def test_task7_admits_only_an_immutable_correlated_control_plane_chain(self):
        from validate_project import validate_governed_mutation_entry

        with tempfile.TemporaryDirectory(prefix="task7-chain-") as temporary:
            root = Path(temporary)
            control = management_control()
            scope = [".gpt-codex/STATE.json"]
            gov = root / ".gpt-codex"; (gov / "work-units").mkdir(parents=True)
            (gov / "STATE.json").write_text(json.dumps({"project_id": control["project_id"], "revision": 3}), encoding="utf-8")
            (root / "design.md").write_text("design", encoding="utf-8"); (root / "plan.md").write_text("plan", encoding="utf-8")
            work_unit = {
                "project_id": control["project_id"], "work_unit_id": "WU-CONTROL", "state": "AUTHORIZED", "basis_state_revision": 3,
                "scope": {"owned_paths": scope, "excluded_paths": []},
                "artifact_refs": {"design": {"path": "design.md", "sha": "a" * 40}, "plan": {"path": "plan.md", "sha": "a" * 40}},
            }
            work_unit_path = ".gpt-codex/work-units/authorization.json"
            (root / work_unit_path).write_text(json.dumps(work_unit), encoding="utf-8")
            base = commit_repository(root, "authority")
            work_unit["artifact_refs"] = {"design": {"path": "design.md", "sha": base}, "plan": {"path": "plan.md", "sha": base}}
            (root / work_unit_path).write_text(json.dumps(work_unit), encoding="utf-8")
            subprocess.run(["git", "add", work_unit_path], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "bind authority"], cwd=root, check=True, capture_output=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            state, _, mutation, request, result = governed_envelopes(control)
            reconciliation = {**mutation, "instruction_type": "RECONCILIATION_REQUEST", "target_work_unit": "WU-CONTROL", "target_project_name": "Framework", "framework_version": "2.7.2", "expected_base_sha": base, "scope_paths": scope, "target_work_unit_ref": {"path": work_unit_path, "sha": base}}
            request = {**request, "in_response_to_instruction_id": reconciliation["instruction_id"], "review_target_revision": base, "target_work_unit": "WU-CONTROL"}
            result["review_target_revision"] = base
            approval_request = {**reconciliation, "instruction_id": "33333333-3333-4333-8333-333333333333", "instruction_type": "APPROVAL_REQUEST", "authorized_actions": ["READ", "VALIDATE", "REPORT"], "in_response_to_instruction_id": reconciliation["instruction_id"]}
            approval = {"kernel_version": "2.0.0", "schema_version": 1, "project_id": control["project_id"], "work_unit_id": "WU-CONTROL", "extension": {}, "result_id": "approval-1", "result_message_type": "APPROVAL_RESULT", "responder_role": "USER_APPROVER", "status": "PASS", "decision": "APPROVE", "response_to_instruction_id": approval_request["instruction_id"], "approved_instruction": {key: reconciliation[key] for key in ("instruction_id", "expected_state_revision", "expected_base_sha", "scope_paths", "target_project_context_id", "target_project_name", "target_github_repository_id", "target_github_repository_full_name", "target_work_unit_ref", "issuer_role", "executor_role", "authorized_actions")}, "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "NOT_ATTEMPTED", "completion_evidence": None}
            approval_path = "approvals/approval.json"; (root / "approvals").mkdir(); (root / approval_path).write_text(json.dumps(approval), encoding="utf-8")
            subprocess.run(["git", "add", approval_path], cwd=root, check=True, capture_output=True); subprocess.run(["git", "commit", "-m", "approval"], cwd=root, check=True, capture_output=True)
            evidence_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            blob_sha = subprocess.run(["git", "rev-parse", f"HEAD:{approval_path}"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "remote", "add", "origin", str(root)], cwd=root, check=True, capture_output=True)
            branch = subprocess.run(["git", "branch", "--show-current"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            reconciliation["approval_evidence_ref"] = {"remote_ref": f"refs/heads/{branch}", "evidence_commit_sha": evidence_sha, "path": approval_path, "blob_sha": blob_sha}
            def validate(instruction=reconciliation, approval_req=approval_request):
                return validate_governed_mutation_entry(control, state, work_unit, instruction, request, result, current_state_revision=3, repository_root=root, approval_request=approval_req)
            self.assertEqual(validate(), [])
            self.assertIn("APPROVAL_CORRELATION_REQUIRED", validate({**reconciliation, "approval_evidence_ref": reconciliation["approval_evidence_ref"]}, {**approval_request, "in_response_to_instruction_id": "wrong"}))
            self.assertIn("CONTROL_PLANE_AUTHORITY_REQUIRED", validate({key: value for key, value in reconciliation.items() if key != "approval_evidence_ref"}))
            self.assertIn("CONTROL_PLANE_SCOPE_INVALID", validate({**reconciliation, "scope_paths": [".gpt-codex/scripts/validate_project.py"]}))
            (root / "outside.txt").write_text("outside", encoding="utf-8")
            self.assertIn("SCOPE_EXPANSION_DENIED", validate())
    def test_task7_reconciliation_mutation_requires_control_plane_approval_chain(self):
        from validate_project import validate_governed_mutation_entry

        with tempfile.TemporaryDirectory(prefix="task7-red-") as temporary:
            root = Path(temporary)
            state_path = root / ".gpt-codex" / "STATE.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(json.dumps({"revision": 3}), encoding="utf-8")
            base = commit_repository(root, "base")
            control = management_control()
            state, work_unit, mutation, request, result = governed_envelopes(control)
            work_unit["scope"] = {"owned_paths": [".gpt-codex/STATE.json"], "excluded_paths": []}
            reconciliation = {
                **mutation,
                "instruction_type": "RECONCILIATION_REQUEST",
                "expected_base_sha": base,
                "scope_paths": [".gpt-codex/STATE.json"],
            }
            request["review_target_revision"] = base
            result["review_target_revision"] = base
            errors = validate_governed_mutation_entry(
                control, state, work_unit, reconciliation, request, result,
                current_state_revision=3, repository_root=root,
            )
            self.assertIn("CONTROL_PLANE_AUTHORITY_REQUIRED", errors)

    def test_task6_governed_entry_binds_real_worktree_and_candidate_oracles(self):
        from validate_project import validate_governed_mutation_entry

        def entry(root: Path, base: str, mutation: dict, *, candidate: str | None = None) -> list[str]:
            control = management_control()
            state, work_unit, original, request, result = governed_envelopes(control)
            instruction = {**original, **mutation, "expected_base_sha": base, "scope_paths": ["src/"]}
            request["review_target_revision"] = base
            result["review_target_revision"] = base
            return validate_governed_mutation_entry(
                control, state, work_unit, instruction, request, result,
                current_state_revision=3, repository_root=root, candidate_revision=candidate,
            )

        with tempfile.TemporaryDirectory(prefix="task6-governed-") as temporary:
            root = Path(temporary)
            for relative in ("src/inside.py", "outside/tracked.py"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("base\n", encoding="utf-8")
            base = commit_repository(root, "base")
            mutate = {"authorized_actions": ["READ", "MUTATE_APPROVED_SCOPE"]}

            self.assertIn("ACTUAL_GIT_REPOSITORY_REQUIRED", validate_governed_mutation_entry(
                management_control(), *governed_envelopes(management_control()), current_state_revision=3,
            ))
            commit_control = management_control()
            commit_state, commit_work_unit, commit_mutation, commit_request, commit_result = governed_envelopes(commit_control)
            self.assertIn("ACTUAL_GIT_REPOSITORY_REQUIRED", validate_governed_mutation_entry(
                commit_control, commit_state, commit_work_unit,
                {**commit_mutation, "authorized_actions": ["READ", "COMMIT"]}, commit_request, commit_result,
                current_state_revision=3,
            ))
            for relative, staged in (("outside/tracked.py", False), ("outside/staged.py", True), ("outside/new.py", False)):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("outside\n", encoding="utf-8")
                if staged:
                    subprocess.run(["git", "add", relative], cwd=root, check=True, capture_output=True)
                self.assertIn("SCOPE_EXPANSION_DENIED", entry(root, base, mutate))
                subprocess.run(["git", "reset", "HEAD", "--", relative], cwd=root, check=True, capture_output=True)
                if relative.endswith("tracked.py"):
                    subprocess.run(["git", "restore", "--worktree", "--", relative], cwd=root, check=True, capture_output=True)
                elif target.exists():
                    target.unlink()
                self.assertNotIn("SCOPE_EXPANSION_DENIED", entry(root, base, mutate))
            for relative, staged in (("src/inside.py", False), ("src/staged.py", True), ("src/new.py", False)):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("inside\n", encoding="utf-8")
                if staged:
                    subprocess.run(["git", "add", relative], cwd=root, check=True, capture_output=True)
                self.assertNotIn("SCOPE_EXPANSION_DENIED", entry(root, base, mutate))
                subprocess.run(["git", "reset", "HEAD", "--", relative], cwd=root, check=True, capture_output=True)
                if relative == "src/inside.py":
                    subprocess.run(["git", "restore", "--worktree", "--", relative], cwd=root, check=True, capture_output=True)
                elif target.exists():
                    target.unlink()
            (root / "src/inside.py").write_text("staged\nunstaged\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/inside.py"], cwd=root, check=True, capture_output=True)
            (root / "src/inside.py").write_text("staged\nunstaged\nmore\n", encoding="utf-8")
            self.assertNotIn("SCOPE_EXPANSION_DENIED", entry(root, base, mutate))
            subprocess.run(["git", "restore", "--staged", "--worktree", "--", "src/inside.py"], cwd=root, check=True, capture_output=True)

        for changed_path, expected in (("outside/candidate.py", "SCOPE_EXPANSION_DENIED"), ("src/candidate.py", None)):
            with self.subTest(candidate_path=changed_path), tempfile.TemporaryDirectory(prefix="task6-candidate-") as temporary:
                root = Path(temporary)
                (root / "src").mkdir()
                (root / "src/base.py").write_text("base\n", encoding="utf-8")
                base = commit_repository(root, "base")
                target = root / changed_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("candidate\n", encoding="utf-8")
                subprocess.run(["git", "add", changed_path], cwd=root, check=True, capture_output=True)
                candidate = subprocess.run(["git", "commit", "-m", "candidate"], cwd=root, check=True, capture_output=True)
                candidate_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
                push = {"authorized_actions": ["READ", "MUTATE_APPROVED_SCOPE", "PUSH"]}
                errors = entry(root, base, push, candidate=candidate_sha)
                if expected is None:
                    self.assertNotIn("SCOPE_EXPANSION_DENIED", errors)
                else:
                    self.assertIn(expected, errors)
                self.assertIn("ACTUAL_GIT_CANDIDATE_REQUIRED", entry(root, base, push))
                self.assertIn("ACTUAL_GIT_CANDIDATE_INVALID", entry(root, base, push, candidate="invalid"))
                (root / "outside").mkdir(exist_ok=True)
                (root / "outside/worktree.py").write_text("outside\n", encoding="utf-8")
                self.assertIn("SCOPE_EXPANSION_DENIED", entry(root, base, push, candidate=candidate_sha))

    def test_task6_candidate_scope_check_rejects_outside_and_accepts_exact_paths(self):
        from validate_project import validate_committed_candidate_scope
        base, candidate = "a" * 40, "b" * 40
        outside = lambda command, **kwargs: subprocess.CompletedProcess(command, 0, b"src/outside.py\x00", b"")
        allowed = lambda command, **kwargs: subprocess.CompletedProcess(command, 0, b"src/inside.py\x00", b"")
        self.assertIn("SCOPE_EXPANSION_DENIED", validate_committed_candidate_scope(Path("."), base, candidate, {"src/inside.py"}, set(), runner=outside))
        self.assertEqual(validate_committed_candidate_scope(Path("."), base, candidate, {"src/inside.py"}, set(), runner=allowed), [])
    def test_work_unit_scope_schema_closes_owned_and_excluded_selectors(self):
        from validate_project import _derived_schema_errors

        valid = {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W",
            "goal": "scope test", "acceptance": [], "selected_extensions": {}, "state": "AUTHORIZED",
            "basis_state_revision": 1, "scope": {"owned_paths": ["src/main.py"], "excluded_paths": []},
        }
        self.assertEqual(_derived_schema_errors(valid, "work-unit"), [])
        invalid_scopes = (
            {}, {"owned_paths": []}, {"owned_paths": ["src/a.py", "src/a.py"]},
            {"owned_paths": ["src/a.py"], "unexpected": True},
            {"owned_paths": ["src/a.py"], "excluded_paths": ["src/x", "src/x"]},
        )
        for scope in invalid_scopes:
            with self.subTest(scope=scope):
                self.assertTrue(_derived_schema_errors({**valid, "scope": scope}, "work-unit"))
        from validate_project import _is_safe_scope_selector
        for selector in ("", "src//", "/absolute", "C:/drive", "src\\file", ".", "..", "src/../file"):
            with self.subTest(selector=selector):
                self.assertFalse(_is_safe_scope_selector(selector))
        self.assertTrue(_is_safe_scope_selector("src/main.py"))
        self.assertTrue(_is_safe_scope_selector("src/"))

    def test_work_unit_selector_schema_matches_runtime_wildcard_grammar(self):
        from validate_project import _derived_schema_errors, _is_safe_scope_selector

        base = {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "W",
            "goal": "selector parity", "acceptance": [], "selected_extensions": {}, "state": "AUTHORIZED",
            "basis_state_revision": 1,
        }
        selectors = (
            "src/a.py", "src/", ".gpt-codex/tests/", "VERSION",
            "src/*.py", "src/?", "src/[x]", "a*/b", "a?b", "a[b]/c", "a]b",
            "/src/a", "C:/src/a", "src\\a", ".", "..", "../src/a", "src/../a", "src//a", "",
        )
        for selector in selectors:
            for field in ("owned_paths", "excluded_paths"):
                scope = {"owned_paths": ["src/a.py"], "excluded_paths": []}
                scope[field] = [selector]
                with self.subTest(selector=selector, field=field):
                    schema_accepts = not _derived_schema_errors({**base, "scope": scope}, "work-unit")
                    self.assertEqual(schema_accepts, _is_safe_scope_selector(selector))

    def test_governed_mutation_uses_authoritative_work_unit_exclusions(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        work_unit["scope"] = {"owned_paths": ["src/"], "excluded_paths": ["src/private/"]}
        denied = {**mutation, "scope_paths": ["src/private/key"]}
        self.assertIn(
            "SCOPE_EXPANSION_DENIED",
            validate_governed_mutation_entry(control, state, work_unit, denied, request, result, current_state_revision=3),
        )
        allowed = {**mutation, "scope_paths": ["src/public/key"]}
        self.assertIn(
            "ACTUAL_GIT_REPOSITORY_REQUIRED",
            validate_governed_mutation_entry(control, state, work_unit, allowed, request, result, current_state_revision=3),
        )

    def test_group_b_prerequisite_contracts_compose_and_fail_at_their_owners(self):
        from instruction_envelope import build_instruction_envelope
        from publication_contract import validate_completion_evidence, validate_result_authority
        from role_communication import is_intrinsic_approval_result
        from validate_project import (
            _derived_schema_errors, validate_instruction_authority,
            validate_instruction_envelope_contract, validate_result_envelope_contract,
        )

        locator = {
            "remote_ref": "refs/heads/gpt-codex-approval-evidence",
            "evidence_commit_sha": "a" * 40,
            "path": "approvals/approval-result.json",
            "blob_sha": "b" * 40,
        }
        instruction = build_instruction_envelope(
            "RECONCILIATION_REQUEST", "33333333-3333-4333-8333-333333333333", "Example", 15,
            "2.7.2+fix.1", target_work_unit="WU-COMPOSED", expected_base_sha="c" * 40,
            target_github_repository_id="123", target_github_repository_full_name="example/project",
            target_work_unit_ref={"path": ".gpt-codex/work-units/composed.json", "sha": "d" * 40},
            scope_paths=["src/public/key"], approval_evidence_ref=locator,
            issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR",
            authorized_actions=["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
            forbidden_actions=[],
        )
        work_unit = {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "WU-COMPOSED",
            "goal": "compose prerequisite contracts", "acceptance": [], "selected_extensions": {},
            "state": "AUTHORIZED", "basis_state_revision": 15,
            "scope": {"owned_paths": ["src/"], "excluded_paths": ["src/private/"]},
        }
        approved_instruction = {
            key: instruction[key] for key in (
                "instruction_id", "expected_state_revision", "expected_base_sha", "scope_paths",
                "target_project_context_id", "target_project_name", "target_github_repository_id",
                "target_github_repository_full_name", "target_work_unit_ref", "issuer_role",
                "executor_role", "authorized_actions",
            )
        }
        approval = {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "WU-COMPOSED",
            "extension": {}, "result_id": "approval-1", "result_message_type": "APPROVAL_RESULT",
            "responder_role": "USER_APPROVER", "status": "PASS", "decision": "APPROVE",
            "response_to_instruction_id": "11111111-1111-4111-8111-111111111111",
            "approved_instruction": approved_instruction, "evidence_refs": [], "completion_gate": "NONE",
            "remote_verification": "NOT_ATTEMPTED", "completion_evidence": None,
        }
        scope = work_unit["scope"]
        owned_paths = scope["owned_paths"]
        excluded_paths = scope.get("excluded_paths", [])

        self.assertEqual(validate_instruction_envelope_contract(instruction), [])
        self.assertEqual(validate_instruction_authority(
            instruction, current_state_revision=15, approved_scope=set(owned_paths), excluded_scope=set(excluded_paths),
        ), [])
        self.assertEqual(_derived_schema_errors(work_unit, "work-unit"), [])
        self.assertEqual(validate_result_envelope_contract(approval), [])
        self.assertTrue(is_intrinsic_approval_result(approval))
        self.assertEqual(validate_result_authority(approval), [])
        self.assertEqual(validate_completion_evidence(approval), [])

        excluded_instruction = {**instruction, "scope_paths": ["src/private/key"]}
        self.assertIn("SCOPE_EXPANSION_DENIED", validate_instruction_authority(
            excluded_instruction, current_state_revision=15, approved_scope=set(owned_paths), excluded_scope=set(excluded_paths),
        ))
        malformed_locator = {**locator, "blob_sha": "not-a-sha"}
        with self.assertRaisesRegex(ValueError, "INVALID_APPROVAL_EVIDENCE_REF"):
            build_instruction_envelope(
                "RECONCILIATION_REQUEST", "33333333-3333-4333-8333-333333333333", "Example", 15,
                "2.7.2+fix.1", target_work_unit="WU-COMPOSED", expected_base_sha="c" * 40,
                target_github_repository_id="123", target_github_repository_full_name="example/project",
                target_work_unit_ref={"path": ".gpt-codex/work-units/composed.json", "sha": "d" * 40},
                scope_paths=["src/public/key"], approval_evidence_ref=malformed_locator,
                issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER", return_role="GPT_ORCHESTRATOR",
                authorized_actions=["READ", "TEST", "VALIDATE", "REPORT", "MUTATE_APPROVED_SCOPE"],
                forbidden_actions=[],
            )
        wrong_author = {**approval, "responder_role": "USER_LOCAL"}
        self.assertFalse(is_intrinsic_approval_result(wrong_author))
        self.assertTrue(validate_result_envelope_contract(wrong_author))
        self.assertTrue(validate_result_authority(wrong_author))
        ordinary_result = {
            "kernel_version": "2.0.0", "schema_version": 1, "project_id": "P", "work_unit_id": "WU-COMPOSED",
            "extension": {}, "result_message_type": "IMPLEMENTATION_RESULT", "status": "PASS",
            "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "VERIFIED",
            "completion_evidence": {
                "execution_state": "COMPLETED", "process_completed": True, "exit_code": 0,
                "intended_scope": ["src/public/key"], "executed_scope": ["src/public/key"],
                "test_files_expected": 1, "test_files_executed": 1, "test_count": 1,
                "failure_count": 0, "error_count": 0, "validators_expected": [],
                "validators_completed": [], "blocker_evidence_refs": [],
            },
        }
        self.assertEqual(validate_result_envelope_contract(ordinary_result), [])
        self.assertEqual(validate_result_authority(ordinary_result), [])
        self.assertEqual(validate_completion_evidence(ordinary_result), [])
        token_only = {**ordinary_result, "result_message_type": "APPROVAL_RESULT"}
        self.assertTrue(validate_result_envelope_contract(token_only))
        self.assertFalse(is_intrinsic_approval_result(token_only))
        self.assertTrue(validate_result_authority(token_only))
        self.assertTrue(validate_completion_evidence(token_only))
        with self.assertRaisesRegex(ValueError, "INVALID_FRAMEWORK_VERSION"):
            build_instruction_envelope(
                "RECONCILIATION_REQUEST", "33333333-3333-4333-8333-333333333333", "Example", 15,
                "2.7.2-01", issuer_role="GPT_ORCHESTRATOR", executor_role="CODEX_IMPLEMENTER",
                return_role="GPT_ORCHESTRATOR", authorized_actions=["MUTATE_APPROVED_SCOPE"], forbidden_actions=[],
                scope_paths=["src/public/key"], approval_evidence_ref=locator,
            )

    def test_intrinsic_approval_cannot_be_state_completion_or_synchronization_evidence(self):
        from publication_contract import (
            validate_completion_evidence, validate_result_authority, validate_state_authority,
        )

        approval = {
            "result_id": "approval-1", "result_message_type": "APPROVAL_RESULT",
            "responder_role": "USER_APPROVER", "status": "PASS", "decision": "APPROVE",
            "response_to_instruction_id": "11111111-1111-4111-8111-111111111111",
            "evidence_refs": [], "completion_gate": "NONE", "remote_verification": "NOT_ATTEMPTED",
            "completion_evidence": None,
            "approved_instruction": {
                "instruction_id": "22222222-2222-4222-8222-222222222222",
                "expected_state_revision": 15, "expected_base_sha": "a" * 40,
                "scope_paths": [".gpt-codex/scripts/example.py"],
                "target_project_context_id": "33333333-3333-4333-8333-333333333333",
                "target_project_name": "Example", "target_github_repository_id": "123",
                "target_github_repository_full_name": "example/project",
                "target_work_unit_ref": {"path": ".gpt-codex/work-units/example.json", "sha": "b" * 40},
                "issuer_role": "GPT_ORCHESTRATOR", "executor_role": "CODEX_IMPLEMENTER",
                "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
            },
        }
        self.assertEqual(validate_result_authority(approval), [])
        self.assertEqual(validate_completion_evidence(approval), [])
        bad_approval = deepcopy(approval)
        bad_approval["external_approval_locator"] = {
            "remote_ref": "refs/heads/example", "evidence_commit_sha": "a" * 40,
            "path": "approvals/result.json", "blob_sha": "b" * 40,
        }
        self.assertTrue(validate_result_authority(bad_approval))
        self.assertTrue(validate_completion_evidence(bad_approval))
        arbitrary_claim = deepcopy(approval)
        arbitrary_claim["extra_authority_claim"] = {"authorized": True}
        self.assertTrue(validate_result_authority(arbitrary_claim))
        self.assertTrue(validate_completion_evidence(arbitrary_claim))
        token_only = {
            "result_message_type": "APPROVAL_RESULT", "status": "PASS",
        }
        self.assertTrue(validate_result_authority(token_only))
        self.assertTrue(validate_completion_evidence(token_only))

        complete = {
            "state": "COMPLETE", "revision": 15, "evidence_refs": ["approval"],
            "continuity": {"last_verified_result_ref": "approval"},
        }
        synced = {
            "state": "AUTHORIZED", "revision": 15, "evidence_refs": ["approval"],
            "continuity": {
                "sync_status": "SYNCED", "latest_synced_state_revision": 15,
                "latest_verified_remote_sha": "a" * 40, "last_verified_result_ref": "approval",
            },
        }
        self.assertTrue(validate_state_authority(complete, {"approval": approval}))
        self.assertTrue(validate_state_authority(synced, {"approval": approval}))
    def test_governed_entry_requires_repository_backed_execution_authority_when_policy_is_adopted(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        control["execution_policy"] = {
            "strategy_profile_id": "PROJECT_PROFILE_001",
            "gpt_orchestrator_strategy": "MINIMAL_CLOSED_LOOP",
            "codex_implementer_strategy": "MINIMAL_DIFF_TDD",
            "codex_reviewer_strategy": "CONTRACT_FIRST",
            "task_splitting": "PROJECT_DETERMINED",
            "review_policy": "RISK_OR_MILESTONE",
            "instruction_policy": "REFERENCE_FIRST",
            "result_return_policy": "DURABLE_REF_FIRST",
        }
        state, work_unit, mutation, request, result = governed_envelopes(control)
        work_unit["strategy_profile_id"] = control["execution_policy"]["strategy_profile_id"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gov = root / ".gpt-codex"; gov.mkdir()
            (gov / "CONTROL.json").write_text(json.dumps(control), encoding="utf-8")
            (gov / "STATE.json").write_text(json.dumps({"project_id": control["project_id"], "revision": 3}), encoding="utf-8")
            (root / "design.md").write_text("design", encoding="utf-8")
            (root / "plan.md").write_text("plan", encoding="utf-8")
            base = commit_repository(root, "base")
            persisted = {**work_unit, "scope": {"owned_paths": [".gpt-codex/CONTROL.json"]},
                         "artifact_refs": {"design": {"path": "design.md", "sha": base}, "plan": {"path": "plan.md", "sha": base}}}
            (gov / "WU-GOVERNED.json").write_text(json.dumps(persisted), encoding="utf-8")
            locator_sha = commit_repository(root, "work unit")
            mutation.update({"expected_base_sha": base, "target_work_unit_ref": {"path": ".gpt-codex/WU-GOVERNED.json", "sha": locator_sha}})
            mutation["scope_paths"] = [".gpt-codex/CONTROL.json"]
            request["review_target_revision"] = base; result["review_target_revision"] = base
            authority = {
                "accepted_design_ref": "design.md@" + base,
                "accepted_plan_ref": "plan.md@" + base,
                "project_context_id": control["project_context_id"], "work_unit_id": work_unit["work_unit_id"], "state_revision": 3,
                "authorization": {"authority_type": "INSTRUCTION", "instruction_id": mutation["instruction_id"], "status": "EXECUTION_AUTHORIZED", "target_revision": base},
            }
            self.assertEqual(validate_governed_mutation_entry(control, state, work_unit, mutation, request, result, current_state_revision=3, repository_authority=authority, repository_root=root), [])
            canonical_authority = {
                key: value for key, value in authority.items() if key not in {"accepted_design_ref", "accepted_plan_ref"}
            }
            self.assertEqual(validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
                repository_authority=canonical_authority, repository_root=root,
            ), [])
            self.assertIn("IMPLEMENTATION_AUTHORIZATION = DENY", validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
                repository_authority={**authority, "accepted_design_ref": "fake"}, repository_root=root,
            ))
            for caller_assertion in (
                {**work_unit, "scope": {"owned_paths": []}},
                {**work_unit, "artifact_refs": {"design": {"path": "other.md", "sha": base}, "plan": {"path": "plan.md", "sha": base}}},
            ):
                with self.subTest(caller_assertion=caller_assertion):
                    self.assertIn("RECONCILIATION_REQUIRED", validate_governed_mutation_entry(
                        control, state, caller_assertion, mutation, request, result, current_state_revision=3,
                        repository_authority=authority, repository_root=root,
                    ))
            caller_only_change = deepcopy(control)
            caller_only_change["execution_policy"]["strategy_profile_id"] = "PROFILE_B"
            self.assertIn("RECONCILIATION_REQUIRED", validate_governed_mutation_entry(
                caller_only_change, state, {**work_unit, "strategy_profile_id": "PROFILE_B"}, mutation, request, result,
                current_state_revision=3, repository_authority=authority, repository_root=root,
            ))
            changed_control = deepcopy(control)
            changed_control["execution_policy"]["strategy_profile_id"] = "PROFILE_B"
            changed_work_unit = {**work_unit, "strategy_profile_id": "PROFILE_B"}
            changed_persisted = {
                **changed_work_unit,
                "scope": {"owned_paths": [".gpt-codex/CONTROL.json"]},
                "artifact_refs": persisted["artifact_refs"],
            }
            (gov / "CONTROL.json").write_text(json.dumps(changed_control), encoding="utf-8")
            (gov / "WU-GOVERNED.json").write_text(json.dumps(changed_persisted), encoding="utf-8")
            changed_sha = commit_repository(root, "governed strategy change")
            changed_mutation = {**mutation, "target_work_unit_ref": {"path": ".gpt-codex/WU-GOVERNED.json", "sha": changed_sha}}
            self.assertEqual(validate_governed_mutation_entry(
                changed_control, state, changed_work_unit, changed_mutation, request, result, current_state_revision=3,
                repository_authority=authority, repository_root=root,
            ), [])
            (gov / "WU-NO-CONTROL.json").write_text(json.dumps({
                **changed_persisted, "scope": {"owned_paths": []},
            }), encoding="utf-8")
            unowned_sha = commit_repository(root, "unowned strategy change")
            unowned_mutation = {
                **changed_mutation,
                "target_work_unit_ref": {"path": ".gpt-codex/WU-NO-CONTROL.json", "sha": unowned_sha},
            }
            self.assertIn("RECONCILIATION_REQUIRED", validate_governed_mutation_entry(
                changed_control, state, changed_work_unit, unowned_mutation, request, result, current_state_revision=3,
                repository_authority=authority, repository_root=root,
            ))
            self.assertIn("RECONCILIATION_REQUIRED", validate_governed_mutation_entry(
                changed_control, state, changed_work_unit, {**changed_mutation, "target_work_unit": "WRONG"}, request, result,
                current_state_revision=3, repository_authority=authority, repository_root=root,
            ))
            for role in ("design", "plan"):
                with self.subTest(role=role):
                    invalid_refs = deepcopy(changed_persisted)
                    invalid_refs["artifact_refs"][role]["path"] = f"missing-{role}.md"
                    invalid_path = f".gpt-codex/WU-BAD-{role}.json"
                    (root / invalid_path).write_text(json.dumps(invalid_refs), encoding="utf-8")
                    invalid_sha = commit_repository(root, f"invalid {role} ref")
                    invalid_mutation = {
                        **changed_mutation,
                        "target_work_unit_ref": {"path": invalid_path, "sha": invalid_sha},
                    }
                    self.assertIn("IMPLEMENTATION_AUTHORIZATION = DENY", validate_governed_mutation_entry(
                        changed_control, state, changed_work_unit, invalid_mutation, request, result,
                        current_state_revision=3, repository_authority=authority, repository_root=root,
                    ))
            self.assertIn("IMPLEMENTATION_AUTHORIZATION = DENY", validate_governed_mutation_entry(control, state, work_unit, {**mutation, "target_work_unit_ref": {"path": "missing.json", "sha": locator_sha}}, request, result, current_state_revision=3, repository_authority=authority, repository_root=root))
            return
        authority = {
            "accepted_design_ref": "design:foundation@" + "a" * 40,
            "accepted_plan_ref": "plan:foundation@" + "b" * 40,
            "project_context_id": control["project_context_id"],
            "work_unit_id": work_unit["work_unit_id"],
            "state_revision": 3,
            "authorization": {
                "authority_type": "INSTRUCTION",
                "instruction_id": mutation["instruction_id"],
                "status": "EXECUTION_AUTHORIZED",
                "target_revision": mutation["expected_base_sha"],
            },
        }
        self.assertIn(
            "IMPLEMENTATION_AUTHORIZATION = DENY",
            validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
            ),
        )
        self.assertEqual(
            validate_governed_mutation_entry(
                control, state, work_unit, mutation, request, result, current_state_revision=3,
                repository_authority=authority,
            ),
            [],
        )
        for invalid in (
            {**authority, "authorization": {**authority["authorization"], "status": "ARTIFACT_ACCEPTED"}},
            {**authority, "project_context_id": "chat-only"},
            {key: value for key, value in authority.items() if key != "accepted_plan_ref"},
            {**authority, "state_revision": 2},
        ):
            with self.subTest(invalid=invalid):
                self.assertIn(
                    "IMPLEMENTATION_AUTHORIZATION = DENY",
                    validate_governed_mutation_entry(
                        control, state, work_unit, mutation, request, result, current_state_revision=3,
                        repository_authority=invalid,
                    ),
                )

    def test_governed_entry_fails_closed_for_malformed_guardrail_control_mappings(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        for field in ("framework", "extensions"):
            for malformed_value in ("malformed", [], ""):
                with self.subTest(field=field, malformed_value=repr(malformed_value)):
                    malformed = deepcopy(control)
                    malformed[field] = malformed_value
                    errors = validate_governed_mutation_entry(
                        malformed, state, work_unit, mutation, request, result, current_state_revision=3,
                    )
                    self.assertTrue(errors)
                    self.assertIn("RECONCILIATION_REQUIRED", errors)

    def test_governed_entry_binds_review_result_identity_to_control_and_mutation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        self.assertIn("ACTUAL_GIT_REPOSITORY_REQUIRED", validate_governed_mutation_entry(
            control, state, work_unit, mutation, request, result, current_state_revision=3,
        ))
        for field in (
            "source_project_context_id", "source_github_repository_id",
            "source_github_repository_full_name", "current_remote_ref",
        ):
            with self.subTest(field=field):
                errors = validate_governed_mutation_entry(
                    control, state, work_unit, mutation, request, {**result, field: "foreign"}, current_state_revision=3,
                )
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn(f"IDENTITY_MISMATCH:{field}", errors)
                errors = validate_governed_mutation_entry(
                    control, state, work_unit, mutation, request, {key: value for key, value in result.items() if key != field},
                    current_state_revision=3,
                )
                self.assertIn("RECONCILIATION_REQUIRED", errors)
                self.assertIn(f"IDENTITY_MISMATCH:{field}", errors)

    def test_repository_guardrail_is_shared_by_governed_entry_and_main_validation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        missing = deepcopy(control)
        missing["extensions"]["guardrails"] = []
        disabled = deepcopy(control)
        disabled["extensions"]["guardrails"][0]["enabled"] = False
        for candidate in (missing, disabled):
            with self.subTest(candidate=candidate["extensions"]["guardrails"]):
                errors = validate_governed_mutation_entry(candidate, state, work_unit, mutation, request, result, current_state_revision=3)
                self.assertIn("GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled", errors)
                with tempfile.TemporaryDirectory() as td:
                    write_project(Path(td), candidate)
                    main_result = run_validator(Path(td))
                self.assertIn("GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled", main_result.stdout)

    def test_main_context_guardrail_keeps_2_1_rules_but_not_non_2_1_projects(self):
        control = management_control()
        control["framework_management_only"] = False
        control["governance_profile"] = "STANDARD"
        control["roots"]["framework_role"] = "ADVISORY"
        control["framework"]["adopted_version"] = "2.1.9"
        control["extensions"]["guardrails"].append(
            {"id": "cross-project-context-binding", "source": "builtin", "enabled": True, "version": "1.0.0"},
        )
        missing = deepcopy(control)
        missing["extensions"]["guardrails"] = [item for item in missing["extensions"]["guardrails"] if item["id"] != "cross-project-context-binding"]
        disabled = deepcopy(control)
        next(item for item in disabled["extensions"]["guardrails"] if item["id"] == "cross-project-context-binding")["enabled"] = False
        for candidate, expected in (
            (missing, "PROJECT_CONTEXT_BINDING: REQUIRED_CONTEXT_GUARDRAIL_ABSENT"),
            (disabled, "PROJECT_CONTEXT_BINDING: REQUIRED_CONTEXT_GUARDRAIL_DISABLED"),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as td:
                write_project(Path(td), candidate)
                self.assertIn(expected, run_validator(Path(td)).stdout)
        non_21 = deepcopy(missing)
        non_21["framework"]["adopted_version"] = "2.2.1"
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), non_21)
            self.assertNotIn("PROJECT_CONTEXT_BINDING:", run_validator(Path(td)).stdout)
    def test_governed_mutation_entry_applies_equally_to_consumer_and_self_hosting(self):
        from validate_project import validate_governed_mutation_entry

        management = management_control()
        consumer = deepcopy(management)
        consumer["framework_management_only"] = False
        consumer["governance_profile"] = "STANDARD"
        consumer["roots"]["framework_role"] = "ADVISORY"
        for control in (consumer, management):
            with self.subTest(profile=control["governance_profile"]):
                state, work_unit, mutation, request, result = governed_envelopes(control)
                self.assertIn("ACTUAL_GIT_REPOSITORY_REQUIRED", validate_governed_mutation_entry(
                    control, state, work_unit, mutation, request, result, current_state_revision=3,
                ))
                self.assertTrue(validate_governed_mutation_entry(control, state, {**work_unit, "state": "PROPOSED"}, mutation, request, result, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(control, {**state, "revision": 2}, work_unit, mutation, request, result, current_state_revision=3))
                self.assertIn("PRE_EXECUTION_REVIEW_REQUIRED", validate_governed_mutation_entry(control, state, work_unit, mutation, None, None, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(control, state, work_unit, {**mutation, "target_work_unit": "WRONG"}, request, result, current_state_revision=3))
                self.assertTrue(validate_governed_mutation_entry(
                    control, state, work_unit, {**mutation, "target_github_repository_id": "foreign-repository"}, request, result,
                    current_state_revision=3,
                ))

    def test_governed_mutation_entry_denies_disabled_guardrail_and_reviewer_mutation(self):
        from validate_project import validate_governed_mutation_entry

        control = management_control()
        state, work_unit, mutation, request, result = governed_envelopes(control)
        disabled = deepcopy(control)
        disabled["extensions"]["guardrails"][0]["enabled"] = False
        self.assertTrue(validate_governed_mutation_entry(disabled, state, work_unit, mutation, request, result, current_state_revision=3))
        errors = validate_governed_mutation_entry(
            control, state, work_unit, mutation, {**request, "authorized_actions": ["MUTATE_APPROVED_SCOPE"]}, result,
            current_state_revision=3,
        )
        self.assertIn("REVIEWER_MUTATION_DENIED", errors)
    @staticmethod
    def _valid_evolution_source() -> dict:
        return {
            "classification": "READ_ONLY_EVOLUTION_SOURCE",
            "framework_version": "2.6.0",
            "source_provenance": {"commit_sha": "a" * 40},
            "compatibility_rules": {"minimum_project_version": "2.0.0"},
            "migration_available": False,
        }

    def test_frozen_v220_validator_rejects_current_management_project(self):
        with tempfile.TemporaryDirectory() as td:
            frozen_root = Path(td)
            script_dir = frozen_root / ".gpt-codex" / "scripts"
            script_dir.mkdir(parents=True)
            if FROZEN_ZIP.exists():
                with zipfile.ZipFile(FROZEN_ZIP) as archive:
                    for name in archive.namelist():
                        if "/scripts/" in name and name.endswith(".py"):
                            relative = Path(name).relative_to("gpt-codex-framework-v2.2.0-bootstrap")
                            target = frozen_root / relative
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(archive.read(name))
            else:
                (script_dir / "validate_project.py").write_bytes(FROZEN_FIXTURE.read_bytes())
                for dependency in ("kernel_rules.py", "context_binding.py"):
                    (script_dir / dependency).write_bytes((ROOT / ".gpt-codex" / "scripts" / dependency).read_bytes())
            result = run_validator(ROOT, script_dir / "validate_project.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid governance_profile", result.stdout)

    def test_v221_validator_accepts_framework_management_project(self):
        result = run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_consumer_cannot_use_framework_management_profile(self):
        control = management_control()
        control["framework_management_only"] = False
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), control)
            result = run_validator(Path(td))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid governance_profile", result.stdout)

    def test_consumer_cannot_use_self_managed_framework_root(self):
        control = management_control()
        control["framework_management_only"] = False
        control["governance_profile"] = "STANDARD"
        with tempfile.TemporaryDirectory() as td:
            write_project(Path(td), control)
            result = run_validator(Path(td))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dual-root authority", result.stdout)

    def test_management_missing_catalog_builtin_is_rejected(self):
        control = management_control()
        control["extensions"]["skills"] = [{
            "id": "not-in-catalog",
            "source": "builtin",
            "enabled": True,
            "version": "1.0.0",
        }]
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            write_project(project, control)
            result = run_validator(project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("catalog", result.stdout.lower())

    def test_framework_evolution_source_is_read_only_and_provenance_bound(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        decision = validate_framework_evolution_source(source)

        self.assertEqual(decision.classification, "READ_ONLY_EVOLUTION_SOURCE")
        self.assertEqual(decision.source, source)
        self.assertEqual(set(decision.__dataclass_fields__), {"classification", "reason", "source"})
        self.assertEqual(source, self._valid_evolution_source())

    def test_evolution_source_snapshot_is_detached_from_caller_mutation(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        decision = validate_framework_evolution_source(source)
        source["source_provenance"]["commit_sha"] = "b" * 40
        source["compatibility_rules"]["minimum_project_version"] = "9.9.9"

        self.assertEqual(decision.source["source_provenance"]["commit_sha"], "a" * 40)
        self.assertEqual(
            decision.source["compatibility_rules"]["minimum_project_version"],
            "2.0.0",
        )

    def test_evolution_source_snapshot_top_level_is_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        decision = validate_framework_evolution_source(self._valid_evolution_source())

        with self.assertRaises(TypeError):
            decision.source["framework_version"] = "9.9.9"

    def test_evolution_source_snapshot_provenance_is_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        decision = validate_framework_evolution_source(self._valid_evolution_source())

        with self.assertRaises(TypeError):
            decision.source["source_provenance"]["commit_sha"] = "b" * 40

    def test_evolution_source_snapshot_compatibility_rules_are_recursively_immutable(self):
        from kernel_rules import validate_framework_evolution_source

        source = self._valid_evolution_source()
        source["compatibility_rules"]["supported_versions"] = ["2.0.0"]
        decision = validate_framework_evolution_source(source)

        with self.assertRaises(TypeError):
            decision.source["compatibility_rules"]["minimum_project_version"] = "9.9.9"
        with self.assertRaises(TypeError):
            decision.source["compatibility_rules"]["supported_versions"][0] = "9.9.9"

    def test_action_bearing_or_incomplete_evolution_source_is_invalid(self):
        from kernel_rules import validate_framework_evolution_source

        valid = self._valid_evolution_source()
        invalid_sources = [
            {key: value for key, value in valid.items() if key != "classification"},
            {**valid, "classification": "FRAMEWORK_EVOLUTION_SOURCE"},
            {key: value for key, value in valid.items() if key != "framework_version"},
            {**valid, "framework_version": ""},
            {key: value for key, value in valid.items() if key != "source_provenance"},
            {**valid, "source_provenance": {}},
            {**valid, "source_provenance": {"commit_sha": "not-a-sha"}},
            {key: value for key, value in valid.items() if key != "compatibility_rules"},
            {**valid, "compatibility_rules": []},
            {key: value for key, value in valid.items() if key != "migration_available"},
            {**valid, "migration_available": "false"},
        ]
        for action_field in (
            "authorized_actions", "target_work_unit", "state_revision", "command", "retry", "queue",
            "project_mutation", "role_authority", "schedule_execution", "force_adoption",
        ):
            invalid_sources.append({**valid, action_field: True})

        for source in invalid_sources:
            with self.subTest(source=source):
                decision = validate_framework_evolution_source(source)
                self.assertEqual(decision.classification, "FRAMEWORK_SOURCE_INVALID")
                self.assertIsNone(decision.source)

    def test_framework_validator_only_reports_optional_evolution_source(self):
        from validate_framework import validate_optional_framework_evolution_source

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(validate_optional_framework_evolution_source(root), [])
            source_path = root / ".gpt-codex" / "FRAMEWORK_EVOLUTION_SOURCE.json"
            source_path.parent.mkdir()
            source_path.write_text(json.dumps(self._valid_evolution_source()), encoding="utf-8")
            self.assertEqual(validate_optional_framework_evolution_source(root), [])
            source_path.write_text(json.dumps({"classification": "invalid"}), encoding="utf-8")
            self.assertEqual(
                validate_optional_framework_evolution_source(root),
                ["FRAMEWORK_SOURCE_INVALID"],
            )

    def test_read_only_source_does_not_replace_local_work_unit_authority(self):
        from validate_project import validate_framework_adoption

        control = management_control()
        instruction = {
            "target_project_context_id": control["project_context_id"],
            "target_github_repository_id": control["github"]["repository_id"],
            "target_github_repository_full_name": control["github"]["repository_full_name"],
            "target_work_unit": "WU-001",
            "expected_state_revision": 1,
            "executor_role": "CODEX_IMPLEMENTER",
            "authorized_actions": ["MUTATE_APPROVED_SCOPE"],
            "forbidden_actions": [],
        }
        work_unit = {
            "project_id": control["project_id"],
            "work_unit_id": "WU-001",
            "state": "PROPOSED",
            "basis_state_revision": 1,
        }
        self.assertEqual(
            validate_framework_adoption(
                control, instruction, work_unit, current_state_revision=1,
                source=self._valid_evolution_source(),
            ),
            ["FRAMEWORK_ADOPTION_NOT_AUTHORIZED"],
        )

    def test_management_evolution_index_remains_non_authoritative(self):
        from context_binding import classify_framework_evolution_index

        control = management_control()
        enrollment = {
            "explicit_enrollment": True,
            "enrollment_id": "management-1",
            "enrollment_status": "ACTIVE",
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "transport": "MANUAL",
        }
        observation = {
            "project_id": control["project_id"],
            "project_context_id": control["project_context_id"],
            "repository_id": control["github"]["repository_id"],
            "repository_full_name": control["github"]["repository_full_name"],
            "source_framework_version": "2.7.0",
            "source_provenance_digest": "a" * 64,
            "compatibility_outcome": "NO_ACTION",
            "observed_at": 1000,
            "local_revision_ref": "revision-7",
        }
        row = classify_framework_evolution_index(
            [enrollment], [observation], now=1001, stale_after_seconds=60,
        )[0]
        self.assertEqual(
            (row["classification"], row["evolution_status"]),
            ("FRAMEWORK_MANAGEMENT_METADATA", "PROJECT_EVOLUTION_OBSERVATION_CURRENT"),
        )
        self.assertFalse({
            "command", "retry", "queue", "target_work_unit", "authorized_actions", "project_mutation",
            "schedule_execution", "force_adoption", "work_unit",
        }.intersection(row))

    def test_structured_management_evolution_records_are_rejected_without_flagging_python_constants(self):
        from consumer_projection import scan_consumer_boundary

        records = {
            "framework-management.json": {"governance_profile": "FRAMEWORK_MANAGEMENT"},
            "self-managed.json": {"roots": {"framework_role": "SELF_MANAGED"}},
            "framework-management-classification.json": {"classification": "FRAMEWORK_MANAGEMENT"},
            "self-managed-classification.json": {"classification": "SELF_MANAGED"},
            "index.json": {"classification": "FRAMEWORK_MANAGEMENT_METADATA"},
            "observation.json": {
                "classification": "DERIVED_OBSERVATION_ONLY",
                "explicit_enrollment": True,
                "enrollment_status": "ACTIVE",
            },
        }
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td)
            for name, record in records.items():
                (staging / name).write_text(json.dumps(record), encoding="utf-8")
            (staging / "constants.py").write_text(
                'CLASSIFICATION = "FRAMEWORK_MANAGEMENT_METADATA"\n', encoding="utf-8",
            )
            result = scan_consumer_boundary(staging, {"contamination": {"forbidden_values": []}})

        self.assertEqual(set(result["management_identity_hits"]), set(records))
        self.assertNotIn("constants.py", result["management_identity_hits"])


if __name__ == "__main__":
    unittest.main()


class FrameworkContractRepairBridgeTests(unittest.TestCase):
    def test_bridge_output_work_units_are_materialized(self):
        repair = ROOT / ".gpt-codex/work-units/framework-contract-repair-001.json"
        seed = ROOT / ".gpt-codex/work-units/framework-baseline-checkpoint-control-plane-001.json"
        self.assertTrue(repair.is_file())
        self.assertTrue(seed.is_file())
