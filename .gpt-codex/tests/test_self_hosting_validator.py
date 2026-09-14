import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
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


class SelfHostingValidatorTests(unittest.TestCase):
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
