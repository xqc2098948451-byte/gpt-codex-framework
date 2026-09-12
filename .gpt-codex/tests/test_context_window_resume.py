import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))


class GovernedProjectFixture:
    """Writes the smallest governed project that exercises map-first resume."""

    def __init__(self, root, project_map_path=None, module_map_paths=None):
        self.root = Path(root)
        self.project_map_path = project_map_path
        self.module_map_paths = module_map_paths or {}

    @staticmethod
    def write_json(root, relative_path, payload):
        path = Path(root) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    @classmethod
    def write(cls, root, *, with_map=True, with_checkpoint=True):
        from continuity_resume import fingerprint_file

        root = Path(root)
        cls.write_json(root, ".gpt-codex/CONTROL.json", {
            "project_id": "P",
            "project_context_id": "11111111-1111-4111-8111-111111111111",
            "github": {
                "repository_id": "repo-a",
                "repository_full_name": "owner/a",
                "default_branch": "main",
            },
        })
        cls.write_json(root, ".gpt-codex/STATE.json", {
            "project_id": "P",
            "revision": 4,
            "state": "VERIFYING",
            "continuity": {
                "current_remote_ref": "refs/heads/main",
                "latest_verified_remote_sha": "p",
                "latest_synced_state_revision": 4,
                "last_verified_result_ref": None,
                "sync_status": "SYNCED",
            },
        })

        project_map_path = None
        module_map_paths = {}
        context_sources = []
        if with_map:
            modules = []
            for module_id, purpose, path, entry_point in (
                ("auth", "Manage authentication sessions.", "src/auth/", "src/auth/session.ts"),
                ("billing", "Manage billing invoices.", "src/billing/", "src/billing/invoice.ts"),
            ):
                module_map_path = f".gpt-codex/navigation/modules/{module_id}.json"
                modules.append({
                    "id": module_id,
                    "purpose": purpose,
                    "paths": [path],
                    "entry_points": [entry_point],
                    "keywords": [module_id],
                    "module_map": module_map_path,
                    "verified_at_sha": None,
                    "freshness": "UNKNOWN",
                })
                module_map_paths[module_id] = cls.write_json(root, module_map_path, {
                    "schema_version": 1,
                    "authority": "DERIVED_NAVIGATION_INDEX",
                    "project_id": "P",
                    "project_context_id": "11111111-1111-4111-8111-111111111111",
                    "module_id": module_id,
                    "responsibility": purpose,
                    "tracked_paths": [path],
                    "key_files": [{"path": entry_point, "role": f"{module_id} implementation."}],
                    "interfaces": [],
                    "depends_on": [],
                    "tests": [],
                    "configuration": [],
                    "data_models": [],
                    "read_when": [f"Working on {module_id}."],
                    "verified_at_sha": None,
                    "freshness": "UNKNOWN",
                })
            project_map_path = cls.write_json(root, ".gpt-codex/navigation/PROJECT_MAP.json", {
                "schema_version": 1,
                "authority": "DERIVED_NAVIGATION_INDEX",
                "project_id": "P",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": "repo-a",
                "anchor_sha": None,
                "architecture_summary": "Authentication and billing handling.",
                "modules": modules,
            })
            context_sources = [
                {"path": ".gpt-codex/navigation/PROJECT_MAP.json", "fingerprint": fingerprint_file(project_map_path)},
                *[
                    {"path": str(path.relative_to(root)).replace("\\", "/"), "fingerprint": fingerprint_file(path)}
                    for path in module_map_paths.values()
                ],
            ]

        if with_checkpoint:
            cls.write_json(root, ".gpt-codex/continuity/RESUME.json", {
                "schema_version": 1,
                "authority": "DERIVED_CACHE",
                "project_id": "P",
                "project_context_id": "11111111-1111-4111-8111-111111111111",
                "repository_id": "repo-a",
                "context_sources": context_sources,
                "objective": "Resume work.",
                "decision": None,
                "blocker": None,
                "verification": [],
                "working_set": {
                    "hot_modules": ["auth"],
                    "hot_files": ["src/auth/session.ts"],
                    "next_required_reads": [],
                    "invalidated_context": [],
                },
            })
        return cls(root, project_map_path, module_map_paths)

    def change_project_map(self):
        payload = json.loads(self.project_map_path.read_text(encoding="utf-8"))
        payload["architecture_summary"] = "Authentication and billing handling, revised."
        self.project_map_path.write_text(json.dumps(payload), encoding="utf-8")


class ContextWindowResumeTests(unittest.TestCase):
    def test_fast_resume_avoids_unchanged_navigation_and_hot_context_reads(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))

            result = load_continuity_resume(fixture.root, "repo-a")

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["resume_mode"], "FAST_RESUME")
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [])

    def test_changed_project_map_fingerprint_invalidates_only_the_project_map_context(self):
        from continuity_resume import load_continuity_resume

        with tempfile.TemporaryDirectory() as directory:
            fixture = GovernedProjectFixture.write(Path(directory))
            fixture.change_project_map()

            result = load_continuity_resume(fixture.root, "repo-a")

            self.assertEqual(result["map_route"], "MAP_HIT")
            self.assertEqual(result["resume_mode"], "DELTA_RESUME")
            self.assertEqual(result["invalidated_context"], [".gpt-codex/navigation/PROJECT_MAP.json"])
            self.assertEqual(result["module_map_reads"], [])
            self.assertEqual(result["required_reads"], [".gpt-codex/navigation/PROJECT_MAP.json"])


if __name__ == "__main__":
    unittest.main()
