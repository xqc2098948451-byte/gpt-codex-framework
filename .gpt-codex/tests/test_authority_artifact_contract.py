"""Regressions for observed Stage4 authority false acceptances, not schema permutations."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / '.gpt-codex/scripts').exists():
    ROOT = Path(__file__).resolve().parent.parent / 'gpt-codex-framework'
sys.path.insert(0, str(ROOT / '.gpt-codex/scripts'))

def load(path):
    return json.loads((ROOT / path).read_bytes())

def stage4():
    pre = load('.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-PRE.json')
    request = load(f".gpt-codex/evidence/instructions/{pre['response_to_instruction_id']}.json")
    instruction = load(f".gpt-codex/evidence/instructions/{request['in_response_to_instruction_id']}.json")
    return instruction, request, pre

class AuthorityArtifactContractTests(unittest.TestCase):
    def test_real_noncanonical_instruction_is_readable_without_rewriting_immutable_bytes(self):
        import continuity_resume
        reader = getattr(continuity_resume, 'read_immutable_governed_artifact', None)
        self.assertTrue(callable(reader), 'Existing immutable resolver needs explicit legacy/current byte classification')
        path = '.gpt-codex/evidence/instructions/1350c9fc-f3b3-480b-84f2-c5c72749915c.json'
        commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        blob = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', f'{commit}:{path}'], text=True).strip()
        locator = {'repository': 'xqc2098948451-byte/gpt-codex-framework', 'commit_sha': commit, 'path': path, 'blob_sha': blob}
        before = (ROOT / path).read_bytes()
        observed = reader(ROOT, locator, locator['repository'])
        self.assertEqual(observed['contract_status'], 'LEGACY_VALID')
        self.assertEqual(observed['record']['instruction_id'], '1350c9fc-f3b3-480b-84f2-c5c72749915c')
        self.assertEqual((ROOT / path).read_bytes(), before)
        self.assertEqual(reader(ROOT, {**locator, 'blob_sha': '0' * 40}, locator['repository'])['contract_status'], 'STALE_OR_AMBIGUOUS')

    def test_actual_pre_rejects_changed_reference_scope_result_identity_and_revision(self):
        from validate_project import validate_pre_execution_review
        instruction, request, result = stage4()
        self.assertEqual(validate_pre_execution_review(instruction, request, result, current_state_revision=46), [])
        request_changes = [
            {'target_work_unit_ref': {**request['target_work_unit_ref'], 'sha': '0' * 40}},
            {'scope_paths': ['unowned.py']}, {'expected_remote_head_sha': '0' * 40},
        ]
        for changes in request_changes:
            with self.subTest(changes=changes):
                self.assertTrue(validate_pre_execution_review(instruction, {**request, **changes}, result, current_state_revision=46))
        partial = {k: v for k, v in result.items() if k not in {'kernel_version', 'framework_version'}}
        self.assertTrue(validate_pre_execution_review(instruction, {**request, 'scope_paths': ['unowned.py']}, partial, current_state_revision=46))
        for changes in [{'work_unit_id': 'foreign'}, {'state_revision': 45}, {'completion_evidence': None}]:
            with self.subTest(changes=changes):
                self.assertTrue(validate_pre_execution_review(instruction, request, {**result, **changes}, current_state_revision=46))

    def test_actual_closure_rejects_unrelated_baseline_and_accepts_explicit_wp_tuple(self):
        from publication_contract import validate_state_authority, classify_release_phase
        state = load('.gpt-codex/STATE.json')
        # Pin the immutable accepted Stage4 state rather than the changing Stage5 state.
        state = json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show', 'f018563a98e4f637652a1dd1182360d9a93ad9c1:.gpt-codex/STATE.json']))
        ref = state['continuity']['last_verified_result_ref']; result = load(ref)
        self.assertEqual(validate_state_authority(state, {ref: result}), [])
        wrong = copy.deepcopy(state); wrong['continuity']['latest_verified_remote_sha'] = '0' * 40
        self.assertTrue(validate_state_authority(wrong, {ref: result}))
        work = state['continuity']['latest_verified_remote_sha']; publication = 'b' * 40
        explicit = {**result, 'verified_baseline_sha': work, 'remote_head_sha': publication, 'publication_sha': publication}
        self.assertEqual(validate_state_authority(state, {ref: explicit}), [])
        wild = {**result, 'verified_baseline_sha': publication, 'remote_head_sha': publication}
        facts = {'candidate_consistent': True, 'candidate_sha': work, 'reviewed_sha': work, 'local_validation_passed': True, 'publication_result': wild}
        self.assertEqual(classify_release_phase(facts), 'RECONCILIATION_REQUIRED')

    def test_generic_result_never_satisfies_fix_lineage(self):
        from validate_project import validate_review_lifecycle
        instruction, _, _ = stage4()
        result = load('.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-CLOSURE.json')
        self.assertIn('FINDING_RESULT_REQUIRED', validate_review_lifecycle(instruction, result, current_state_revision=47))

    def test_completion_counts_and_review_pass_do_not_complete_execution(self):
        from publication_contract import validate_completion_evidence
        from continuity_resume import classify_execution_progress
        instruction, _, result = stage4()
        self.assertEqual(validate_completion_evidence(result), [])
        for number in (-1, True):
            changed = copy.deepcopy(result)
            for key in ('test_files_expected', 'test_files_executed', 'test_count'):
                changed['completion_evidence'][key] = number
            self.assertTrue(validate_completion_evidence(changed))
        state = {'project_id': result['project_id'], 'active_work_unit': result['work_unit_id'], 'revision': 46}
        unit = {'project_id': result['project_id'], 'work_unit_id': result['work_unit_id'], 'basis_state_revision': 46, 'state': 'AUTHORIZED'}
        review = {**result, 'git_base_sha': instruction['expected_base_sha']}
        self.assertEqual(classify_execution_progress(state, unit, [review], instruction_id=review['response_to_instruction_id'], base_sha=instruction['expected_base_sha'], safe_postcondition=True), 'RECONCILIATION_REQUIRED')

    def test_executable_revision_is_integer_authority(self):
        from validate_project import validate_instruction_authority
        instruction, _, _ = stage4()
        self.assertTrue(validate_instruction_authority({**instruction, 'expected_state_revision': None}, 46))
        self.assertTrue(validate_instruction_authority({**instruction, 'expected_state_revision': True}, 1))

    def test_structured_directory_and_unique_legacy_table_use_same_declared_semantics(self):
        from validate_project import _design_authorized_directory_paths
        from instruction_envelope import canonical_instruction_bytes
        declaration = {'path': 'semantic', 'purpose': 'approved evidence', 'content_type': 'JSON', 'authority_type': 'DERIVED', 'owner': 'project', 'lifetime': 'DURABLE', 'consumer_visible': False, 'release_visible': False, 'cleanup_policy': 'retain'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            def commit(data):
                (root / 'design.json').write_bytes(data)
                subprocess.run(['git', '-C', str(root), '-c', 'core.autocrlf=false', 'add', 'design.json'], check=True)
                subprocess.run(['git', '-C', str(root), '-c', 'user.name=ContractTests', '-c', 'user.email=contract@example.invalid', 'commit', '--quiet', '-m', 'contract fixture'], check=True)
                return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            structured = {'accepted': True, 'project_id': 'project', 'state_revision': 3, 'directory_creations': [declaration]}
            sha = commit(canonical_instruction_bytes(structured))
            unit = {'project_id': 'project', 'basis_state_revision': 3, 'artifact_refs': {key: {'path': 'design.json', 'sha': sha} for key in ('design', 'plan')}}
            self.assertEqual(_design_authorized_directory_paths(root, unit, {'semantic': declaration}), {'semantic'})
            legacy = ('The following new directories are the only ones this candidate proposes.\nEach line is a directory declaration.\n\n| path | purpose | content_type | authority_type |\n|---|---|---|---|\n| semantic | approved evidence | JSON | DERIVED |\n')
            # Legacy text is selected by its durable ref path; use an actual Markdown path.
            (root / 'design.md').write_text(legacy, encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'design.md'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=ContractTests', '-c', 'user.email=contract@example.invalid', 'commit', '--quiet', '-m', 'legacy fixture'], check=True)
            oldsha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            unit['artifact_refs'] = {key: {'path': 'design.md', 'sha': oldsha} for key in ('design', 'plan')}
            self.assertEqual(_design_authorized_directory_paths(root, unit, {'semantic': declaration}), {'semantic'})
            (root / 'design.md').write_text(legacy.replace('JSON | DERIVED', 'WRONG | WRONG'), encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'design.md'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=ContractTests', '-c', 'user.email=contract@example.invalid', 'commit', '--quiet', '-m', 'conflicting fixture'], check=True)
            badsha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            unit['artifact_refs'] = {key: {'path': 'design.md', 'sha': badsha} for key in ('design', 'plan')}
            self.assertEqual(_design_authorized_directory_paths(root, unit, {'semantic': declaration}), set())
            conflict = legacy + '| semantic | approved evidence | JSON | PROHIBITED |\n'
            (root / 'design.md').write_text(conflict, encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', 'design.md'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=ContractTests', '-c', 'user.email=contract@example.invalid', 'commit', '--quiet', '-m', 'duplicate conflicting declaration'], check=True)
            conflictsha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            unit['artifact_refs'] = {key: {'path': 'design.md', 'sha': conflictsha} for key in ('design', 'plan')}
            self.assertEqual(_design_authorized_directory_paths(root, unit, {'semantic': declaration}), set())

if __name__ == '__main__':
    unittest.main()
