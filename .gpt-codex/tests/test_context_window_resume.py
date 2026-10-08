import json
import subprocess
from unittest.mock import patch
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
            "roots": {"project_role": "AUTHORITATIVE", "framework_role": "ADVISORY"},
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


class MachineContextRoutingTests(unittest.TestCase):
    def test_machine_route_handles_real_unicode_git_root(self):
        from continuity_resume import route_project_context
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'中文路由';root.mkdir()
            self.git(root,'init','-b','main')
            result=route_project_context(root,None)
            self.assertEqual(result['route'],'UNBOUND')

    def git(self,root,*args):
        return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL,text=True,encoding='utf-8').strip()

    def fixture(self,directory,management=False):
        root=Path(directory);GovernedProjectFixture.write(root)
        control=json.loads((root/'.gpt-codex/CONTROL.json').read_text());control.pop('github')
        if management:
            control.update(framework_management_only=True,governance_profile='FRAMEWORK_MANAGEMENT')
            control['roots']['framework_role']='SELF_MANAGED'
        GovernedProjectFixture.write_json(root,'.gpt-codex/CONTROL.json',control)
        for relative in ('.gpt-codex/navigation/PROJECT_MAP.json','.gpt-codex/continuity/RESUME.json'):
            payload=json.loads((root/relative).read_text());payload['repository_id']=None
            GovernedProjectFixture.write_json(root,relative,payload)
        self.git(root,'init','-b','main');self.git(root,'config','user.name','Routing test');self.git(root,'config','user.email','routing@example.invalid')
        self.git(root,'add','.');self.git(root,'commit','-m','governed fixture')
        return root

    def test_default_resume_skips_history_bytes_and_explicit_history_is_bounded(self):
        from continuity_resume import load_continuity_resume
        with tempfile.TemporaryDirectory() as d:
            fixture=GovernedProjectFixture.write(Path(d));root=fixture.root
            checkpoint=json.loads((root/'.gpt-codex/continuity/RESUME.json').read_text())
            history='.gpt-codex/history/HISTORY_CONTEXT.json'
            GovernedProjectFixture.write_json(root,history,{'old':'history'})
            checkpoint['context_sources'] += [{'path':history,'context_class':'HISTORY_CONTEXT','fingerprint':'old'}]*100
            checkpoint['working_set']['next_required_reads']=[history]
            GovernedProjectFixture.write_json(root,'.gpt-codex/continuity/RESUME.json',checkpoint)
            reads=[];original=Path.read_bytes
            def observed(path):
                reads.append(path);return original(path)
            with patch.object(Path,'read_bytes',observed):
                result=load_continuity_resume(root,'repo-a')
            self.assertEqual(sum(p==root/history for p in reads),0)
            self.assertNotIn(history,result['required_reads'])
            result=load_continuity_resume(root,'repo-a',history_context_refs=[history])
            self.assertEqual(result['required_reads'],[history])

    def test_local_modes_and_stale_identity_routes_are_deterministic(self):
        from continuity_resume import route_project_context
        for management,want in ((False,'CONSUMER'),(True,'FRAMEWORK_MANAGEMENT')):
            with self.subTest(mode=want),tempfile.TemporaryDirectory() as d:
                root=self.fixture(d,management)
                result=route_project_context(root,None)
                self.assertEqual(result['route'],'NORMAL_BOUND');self.assertEqual(result['context_mode'],want)
                self.assertFalse(result['mutation_authorized']);self.assertEqual(result,route_project_context(root,None))
                self.assertEqual(route_project_context(root,None,expected_state_revision=99)['route'],'STALE_STATE_OR_REMOTE')
                self.assertEqual(route_project_context(root,None,expected_project_context_id='foreign')['route'],'IDENTITY_MISMATCH')
                self.assertIn(result['route'],result['human_handoff'])
                control=json.loads((root/'.gpt-codex/CONTROL.json').read_text());control['governance_profile']='FRAMEWORK_MANAGEMENT' if not management else 'STANDARD'
                GovernedProjectFixture.write_json(root,'.gpt-codex/CONTROL.json',control)
                self.assertEqual(route_project_context(root,None)['route'],'IDENTITY_MISMATCH')
                control.update(framework_management_only=True,governance_profile='FRAMEWORK_MANAGEMENT')
                control['roots']['framework_role']='ADVISORY'
                GovernedProjectFixture.write_json(root,'.gpt-codex/CONTROL.json',control)
                self.assertEqual(route_project_context(root,None)['route'],'IDENTITY_MISMATCH')

    def test_fresh_git_unbound_partial_governance_and_ambiguous_root_fail_closed(self):
        from continuity_resume import route_project_context
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.git(root,'init','-b','main')
            result=route_project_context(root,None)
            self.assertEqual(result['route'],'UNBOUND');self.assertEqual(result['next_gate'],'BOOTSTRAP_CHALLENGE_REQUIRED')
            self.assertFalse(result['mutation_authorized']);self.assertFalse(result['continuation_allowed'])
            nested=root/'nested';nested.mkdir()
            self.assertEqual(route_project_context(nested,None)['route'],'IDENTITY_MISMATCH')
            GovernedProjectFixture.write_json(root,'.gpt-codex/STATE.json',{'project_id':'existing'})
            self.assertEqual(route_project_context(root,None)['route'],'RECONCILIATION_REQUIRED')

    def test_current_named_finding_uses_existing_remediation_gate(self):
        from continuity_resume import route_project_context
        from result_return import build_finding_result
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d);control=json.loads((root/'.gpt-codex/CONTROL.json').read_text());state=json.loads((root/'.gpt-codex/STATE.json').read_text())
            control['project_name']='Fixture'
            finding=build_finding_result(control,state,framework_version='2.10.0',review_target_revision=self.git(root,'rev-parse','HEAD'),finding_ids=['F-ROUTE'],evidence_refs=['.gpt-codex/STATE.json'])
            ref='.gpt-codex/evidence/results/RESULT-FINDING.json'
            GovernedProjectFixture.write_json(root,ref,finding)
            state['blockers']=['F-ROUTE'];state['next_action']='AWAIT_REMEDIATION_AUTHORIZATION';state['continuity']['last_verified_result_ref']=ref
            GovernedProjectFixture.write_json(root,'.gpt-codex/STATE.json',state)
            self.git(root,'add','.');self.git(root,'commit','-m','record current finding and blocker')
            result=route_project_context(root,None)
            self.assertEqual(result['route'],'REVIEW_FINDING');self.assertEqual(result['next_gate'],'GPT_USER_DECISION_THEN_FIX_INSTRUCTION')
            self.assertEqual(result['recovery_evidence_refs'],[ref]);self.assertFalse(result['continuation_allowed'])
            finding['source_project_context_id']='foreign';GovernedProjectFixture.write_json(root,ref,finding)
            self.assertEqual(route_project_context(root,None)['route'],'IDENTITY_MISMATCH')

    def test_program_context_is_explicit_and_foreign_dependency_is_denied(self):
        from continuity_resume import route_project_context
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d)
            ref='docs/roadmap/program.json';GovernedProjectFixture.write_json(root,ref,{'project_id':'P','project_context_id':'11111111-1111-4111-8111-111111111111','task':'only current child'})
            result=route_project_context(root,None)
            self.assertNotIn(ref,result['context_plan']['required_reads'])
            result=route_project_context(root,None,program_context_refs=[ref])
            self.assertEqual(result['context_plan']['program_context_refs'],[ref]);self.assertIn(ref,result['context_plan']['required_reads'])
            GovernedProjectFixture.write_json(root,ref,{'project_id':'FOREIGN','project_context_id':'foreign'})
            self.assertEqual(route_project_context(root,None,program_context_refs=[ref])['route'],'IDENTITY_MISMATCH')

    def test_context_marker_change_invalidates_stage2_process_local_reuse(self):
        from continuity_resume import capture_authority_snapshot,reuse_authority_snapshot
        with tempfile.TemporaryDirectory() as d:
            root=self.fixture(d);scope=['.gpt-codex/STATE.json']
            snapshot=capture_authority_snapshot(root,None,scope_paths=scope)
            self.assertEqual(reuse_authority_snapshot(root,None,snapshot,scope_paths=scope)['state']['revision'],4)
            checkpoint=json.loads((root/'.gpt-codex/continuity/RESUME.json').read_text());checkpoint['working_set']['next_required_reads']=['current-task.md']
            GovernedProjectFixture.write_json(root,'.gpt-codex/continuity/RESUME.json',checkpoint)
            with self.assertRaisesRegex(ValueError,'STALE_AUTHORITY'):
                reuse_authority_snapshot(root,None,snapshot,scope_paths=scope)


if __name__ == "__main__":
    unittest.main()
