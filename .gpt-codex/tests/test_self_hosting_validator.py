import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / ".gpt-codex" / "scripts" / "validate_project.py"
FROZEN_ZIP = ROOT / "dist" / "gpt-codex-framework-v2.2.0-bootstrap.zip"


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
    def test_frozen_v220_validator_rejects_current_management_project(self):
        with tempfile.TemporaryDirectory() as td:
            frozen_root = Path(td)
            with zipfile.ZipFile(FROZEN_ZIP) as archive:
                for name in archive.namelist():
                    if "/scripts/" in name and name.endswith(".py"):
                        relative = Path(name).relative_to("gpt-codex-framework-v2.2.0-bootstrap")
                        target = frozen_root / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.read(name))
            result = run_validator(ROOT, frozen_root / ".gpt-codex" / "scripts" / "validate_project.py")
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


if __name__ == "__main__":
    unittest.main()
