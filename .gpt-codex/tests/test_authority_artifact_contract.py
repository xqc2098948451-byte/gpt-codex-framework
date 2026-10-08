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

from unittest.mock import patch
from instruction_envelope import canonical_instruction_bytes,build_pre_execution_review_request
from git_continuity import build_state_sync_finalization,verify_work_publication
from validate_project import validate_review_lifecycle
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL).decode().strip()
def load(path):return json.loads((ROOT/path).read_bytes())
class BoundaryRegressions(unittest.TestCase):
 def fixture(self):
  closed=load('.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-CLOSURE.json');state=json.loads(subprocess.check_output(['git','-C',str(ROOT),'show','f018563a98e4f637652a1dd1182360d9a93ad9c1:.gpt-codex/STATE.json']));return closed,state,state['continuity']['latest_verified_remote_sha']
 def clone(self,folder,W):
  git(ROOT,'clone','--shared','--no-checkout',str(ROOT),str(folder));git(folder,'config','core.autocrlf','false');git(folder,'checkout','--detach',W);git(folder,'remote','set-url','origin',git(ROOT,'remote','get-url','origin'))
 def test_real_stage4_finalizer_rejects_unfinished_post_completion(self):
  closed,_,W=self.fixture();req=closed['post_request'];post=closed['independent_post']
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'review';self.clone(root,W)
   args=dict(work_sha=W,remote_ref='refs/heads/main',expected_state_revision=46,result_ref='.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-CLOSURE.json',post_request=req)
   observed={'remote_head_sha':W,'repository_id':'1366213495','repository':'xqc2098948451-byte/gpt-codex-framework','remote_ref':'refs/heads/main'}
   with patch('git_continuity.observe_bound_remote',return_value=observed):
    self.assertFalse(build_state_sync_finalization(root,post_result=post,**args)['work_unit_completed'])
    for change in ({'exit_code':None},{'process_completed':False},{'executed_scope':[]},{'validators_completed':[]}):
     bad=copy.deepcopy(post);bad['completion_evidence'].update(change)
     with self.subTest(change=change),self.assertRaises(ValueError):build_state_sync_finalization(root,post_result=bad,**args)
 def test_real_stage4_request_bound_fix_rejects_foreign_lineage(self):
  finding=load('.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-FINDING.json');decision=load('.gpt-codex/evidence/STAGE4-FRAMEWORK-REMEDIATION.json');basis=load('.gpt-codex/evidence/STAGE4-FRAMEWORK-REGRESSION.json')
  fixes=[load(p.relative_to(ROOT).as_posix()) for p in (ROOT/'.gpt-codex/evidence/instructions').glob('*.json')]
  fix=next(x for x in fixes if x.get('instruction_type')=='FIX_INSTRUCTION' and x.get('in_response_to_result_id')==finding['result_id'])
  # Pure bounded lineage fixture uses the original reviewed subject directly;
  # actual management-bridge and live W/P execution remain Consumer acceptance.
  fix={**fix,'expected_base_sha':finding['review_target_revision']}
  req=build_pre_execution_review_request(fix,current_state_revision=46,approved_scope=set(fix['scope_paths']),runtime_fresh_context_verified=True,runtime_input_source_kinds=['REPOSITORY_CONTENT'])
  post=load('.gpt-codex/evidence/results/RESULT-STAGE4-FRAMEWORK-FIX-RE-REVIEW.json');post={**post,'response_to_instruction_id':req['instruction_id'],'fix_round':fix['fix_round'],'finding_ids':[]};req['review_target_revision']=post['review_target_revision']
  def validate(r=req,p=post):return validate_review_lifecycle(fix,finding,current_state_revision=46,remediation_decision=decision,resolved_basis={basis['evidence_id']:basis},re_review_request=r,re_review_result=p,resulting_revision=post['review_target_revision'])
  self.assertEqual(validate(),[])
  for change in ({'in_response_to_result_id':'00000000-0000-4000-8000-000000000000'},{'fix_round':2},{'finding_ids':['FOREIGN']},{'remediation_decision_ref':'FOREIGN'}):
   with self.subTest(change=change):self.assertTrue(validate({**req,**change}))
  self.assertTrue(validate(p={**post,'finding_ids':['FOREIGN']}))
  for change in ({'target_project_context_id':'foreign-context'},{'target_github_repository_id':'foreign-repository'},{'expected_remote_ref':'refs/heads/foreign'}):
   with self.subTest(change=change):self.assertTrue(validate({**req,**change}))
  self.assertTrue(validate(p={**post,'current_remote_ref':'refs/heads/foreign'}))
 def test_real_stage4_publication_accepts_only_correlated_post_request(self):
  closed,state,W=self.fixture();scope=closed['publication_authorization']['scope_paths'] if 'publication_authorization' in closed else closed['post_request']['scope_paths'];closed=copy.deepcopy(closed);req=closed['post_request'];foreign=req['instruction_id'];req['instruction_id']='ef5c9407-1cf2-4cd6-93c0-8d7945a1e73c';closed['independent_post']['response_to_instruction_id']=req['instruction_id'];postpath=f".gpt-codex/evidence/instructions/{req['instruction_id']}.json"
  prior=json.loads(subprocess.check_output(['git','-C',str(ROOT),'show',W+':'+postpath]));self.assertEqual(prior['artifact_stage'],'IMPLEMENTATION');self.assertEqual(prior['in_response_to_instruction_id'],req['in_response_to_instruction_id'])
  original='f018563a98e4f637652a1dd1182360d9a93ad9c1';paths=git(ROOT,'diff','--name-only',W,original).splitlines()
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'review';self.clone(root,W)
   for p in paths:(root/p).write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show',original+':'+p]))
   closurepath=state['continuity']['last_verified_result_ref'];(root/closurepath).write_bytes(canonical_instruction_bytes(closed))
   (root/postpath).write_bytes(canonical_instruction_bytes(req));git(root,'add','--',*paths,postpath);git(root,'-c','user.name=ContractTests','-c','user.email=contract@example.invalid','commit','-m','exact request metadata fixture');P=git(root,'rev-parse','HEAD')
   observed={'remote_head_sha':P,'repository_id':'1366213495','repository':'xqc2098948451-byte/gpt-codex-framework','remote_ref':'refs/heads/main'}
   with patch('git_continuity.observe_bound_remote',return_value=observed):self.assertEqual(verify_work_publication(root,work_sha=W,publication_sha=P,remote_ref='refs/heads/main',scope_paths=scope)['status'],'PASS')
   for change in ({'target_work_unit':'foreign-work-unit'},{'return_role':'INFORMATION_ONLY'}):
    altered=copy.deepcopy(closed);altered['post_request'].update(change)
    index=Path(t)/('negative-'+next(iter(change))+'.index');env=dict(__import__('os').environ,GIT_INDEX_FILE=str(index));subprocess.check_call(['git','-C',str(root),'read-tree',P],env=env,stdout=subprocess.DEVNULL)
    for path,record in ((closurepath,altered),(postpath,altered['post_request'])):
     blob=subprocess.check_output(['git','-C',str(root),'hash-object','-w','--stdin'],input=canonical_instruction_bytes(record)).decode().strip();subprocess.check_call(['git','-C',str(root),'update-index','--add','--cacheinfo',f'100644,{blob},{path}'],env=env,stdout=subprocess.DEVNULL)
    tree=subprocess.check_output(['git','-C',str(root),'write-tree'],env=env).decode().strip();bad=git(root,'-c','user.name=ContractTests','-c','user.email=contract@example.invalid','commit-tree',tree,'-p',W,'-m','negative publication binding')
    with self.subTest(change=change),patch('git_continuity.observe_bound_remote',return_value={**observed,'remote_head_sha':bad}),self.assertRaises(ValueError):verify_work_publication(root,work_sha=W,publication_sha=bad,remote_ref='refs/heads/main',scope_paths=scope)

if __name__ == '__main__':
    unittest.main()
