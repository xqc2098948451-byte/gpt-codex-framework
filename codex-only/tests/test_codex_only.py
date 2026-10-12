"""Real Git/process integration tests; review fixtures are protocol data only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


BASE = Path(__file__).resolve().parents[1]
CLI = BASE / 'codex_only.py'
os.environ['PYTHONUTF8'] = '1'
GIT = os.environ.get('CODEX_ONLY_GIT', r'C:/Program Files/Git/cmd/git.exe')
if not Path(GIT).exists():
    GIT = 'git'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        (BASE / '.test-tmp').mkdir(exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(dir=BASE / '.test-tmp'))
        self.repo = self.tmp / 'delivery'
        self.repo.mkdir()
        self.git(self.repo, 'init', '-b', 'main')
        self.task = self.tmp / 'task.json'
        self.req = self.tmp / 'requirements.md'
        self.req.write_text('1. Goal\n2. Behavior\n3. IO\n4. Rules\n5. Errors\n6. GWT\n')
        self.impl = self.tmp / 'implementer'
        self.reviewer = self.tmp / 'reviewer'
        self.ev = self.tmp / 'implementer-tests.json'
        self.rev_ev = self.tmp / 'reviewer-tests.json'
        self.review = self.tmp / 'review.json'

    def tearDown(self):
        # Git makes object files read-only on Windows.
        def writable(function, path, exc):
            os.chmod(path, 0o700)
            function(path)
        shutil.rmtree(self.tmp, onexc=writable)

    def git(self, root, *args, ok=True):
        p = subprocess.run([GIT, '-C', str(root), '-c', 'user.name=Fixture',
                            '-c', 'user.email=fixture@example.invalid', *args],
                           capture_output=True, text=True, encoding='utf-8')
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def cli(self, command, root=None, ok=True, error=None, **args):
        argv = [sys.executable, str(CLI), command, '--root', str(root or self.repo)]
        for key, value in args.items():
            for item in value if isinstance(value, list) else [value]:
                argv.extend(['--' + key.replace('_', '-'), str(item)])
        p = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode == 0, ok, (argv, p.stdout, p.stderr))
        try:
            data = json.loads(p.stdout)
        except ValueError:
            self.fail(f'CLI must return JSON: {p.stdout!r} {p.stderr!r}')
        if error:
            self.assertEqual(data['error'], error, data)
        return data

    def load(self, path):
        return json.loads(path.read_text(encoding='utf-8'))

    def save(self, path, value):
        path.write_text(json.dumps(value), encoding='utf-8')

    def setup_task(self, scope=None, command=None):
        self.cli('init')
        self.baseline = self.git(self.repo, 'rev-parse', 'HEAD')
        self.cli('authorize', task=self.task, requirements=self.req,
                 scope=scope or ['app.py', 'test_app.py'],
                 test_command_json=json.dumps(command or [sys.executable, '{root}/test_app.py']),
                 task_id='fixture-task')
        self.git(self.repo, 'worktree', 'add', '-b', 'implementer', str(self.impl))

    def candidate(self, bad=False):
        (self.impl / 'app.py').write_text('VALUE = 42\n', encoding='utf-8')
        (self.impl / 'test_app.py').write_text(
            'from app import VALUE\nassert VALUE == ' + ('0' if bad else '42') + '\n',
            encoding='utf-8')
        self.git(self.impl, 'add', 'app.py', 'test_app.py')
        self.git(self.impl, 'commit', '-m', 'Candidate')
        self.sha = self.git(self.impl, 'rev-parse', 'HEAD')

    def evidence(self):
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='implementer-fixture', output=self.ev)
        self.git(self.tmp, 'clone', '--no-local', str(self.repo), str(self.reviewer))
        self.git(self.reviewer, 'checkout', '--detach', self.sha)
        self.cli('test', root=self.reviewer, task=self.task, candidate=self.sha,
                 session='reviewer-fixture', output=self.rev_ev)
        task = self.load(self.task)
        self.save(self.review, dict(candidate=self.sha, project_id=task['project_id'],
                  task_digest=hashlib.sha256(self.task.read_bytes()).hexdigest(),
                  verdict='PASS', findings=[], reviewer_session='reviewer-fixture',
                  reviewer_worktree=str(self.reviewer.resolve()), test_evidence=str(self.rev_ev)))

    def gate(self, ok=True, error=None):
        return self.cli('gate', root=self.impl, task=self.task, candidate=self.sha,
                        test_evidence=self.ev, review=self.review, ok=ok, error=error)

    def deliver(self, ok=True, error=None):
        return self.cli('deliver', source_root=self.impl, task=self.task,
                        candidate=self.sha, test_evidence=self.ev, review=self.review,
                        ok=ok, error=error)

    def unchanged(self):
        self.assertEqual(self.git(self.repo, 'rev-parse', 'main'), self.baseline)

    def test_init_authorization_and_exact_root(self):
        self.cli('init')
        first = self.git(self.repo, 'rev-parse', 'HEAD')
        self.cli('init')
        self.assertEqual(self.git(self.repo, 'rev-parse', 'HEAD'), first)
        sub = self.repo / 'nested'
        sub.mkdir()
        self.cli('init', root=sub, ok=False, error='ROOT_NOT_TOPLEVEL')
        self.cli('authorize', task=self.repo / 'task.json', requirements=self.req,
                 scope='app.py', test_command_json='["python"]', task_id='x',
                 ok=False, error='PATH_NOT_EXTERNAL')
        self.cli('check', task=self.task, candidate=first, ok=False, error='AUTHORIZATION_MISSING')

    def test_init_preserves_unrelated_dirty_files(self):
        (self.repo / 'private.txt').write_text('keep')
        self.cli('init', ok=False, error='DIRTY_WORKTREE')
        self.assertEqual(self.git(self.repo, 'ls-files'), '')
        self.assertEqual((self.repo / 'private.txt').read_text(), 'keep')

    def test_existing_project_and_single_authorization(self):
        (self.repo / 'existing').write_text('old')
        self.git(self.repo, 'add', 'existing')
        self.git(self.repo, 'commit', '-m', 'Existing genesis')
        genesis = self.git(self.repo, 'rev-parse', 'HEAD')
        self.setup_task()
        self.assertEqual(self.load(self.repo / '.codex-only/project.json')['genesis'], genesis)
        before = self.task.read_bytes()
        self.cli('authorize', task=self.task, requirements=self.req, scope='app.py',
                 test_command_json='["python"]', task_id='again', ok=False, error='OUTPUT_EXISTS')
        self.assertEqual(self.task.read_bytes(), before)

    def test_delivery_retry_and_interrupted_completion_recovery(self):
        self.setup_task()
        self.candidate()
        self.evidence()
        self.gate()
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'ACTIVE')
        self.deliver()
        completion = Path(self.load(self.task)['completion_path'])
        self.assertEqual(self.load(completion)['candidate'], self.sha)
        before = completion.read_bytes()
        self.deliver()
        self.assertEqual(completion.read_bytes(), before)
        completion.unlink()  # Simulate crash after merge, before record write.
        recovered = self.cli('recover', task=self.task)
        self.assertEqual(recovered['state'], 'DELIVERED')
        self.assertTrue(recovered['completion_missing'])
        self.assertFalse(completion.exists())  # recover is read-only.
        self.deliver()
        self.assertEqual(self.git(self.repo, 'rev-parse', 'main'), self.sha)
        self.assertEqual(self.load(completion)['candidate'], self.sha)

    def test_branch_tag_collision_authorization(self):
        self.cli('init')
        self.git(self.repo, 'tag', 'main')
        self.setup_task()
        self.assertEqual(self.load(self.task)['target_branch'], 'main')
        self.cli('check', task=self.task, candidate=self.baseline)
        recovered = self.cli('recover', task=self.task)
        self.assertEqual(recovered['state'], 'ACTIVE')
        self.assertEqual(recovered['target_head'], self.baseline)

    def test_branch_tag_collision_added_after_authorization_delivery(self):
        self.setup_task()
        self.candidate()
        self.evidence()  # Protocol fixtures, not an independent review.
        self.git(self.repo, 'tag', 'main')
        self.git(self.repo, 'checkout', '-b', 'heads/main')
        self.deliver(ok=False, error='WRONG_TARGET_BRANCH')
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/heads/main'), self.baseline)
        self.assertFalse(Path(self.load(self.task)['completion_path']).exists())
        self.git(self.repo, 'checkout', 'main')
        self.deliver()
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/heads/main'), self.sha)
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/heads/heads/main'), self.baseline)
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/tags/main'), self.baseline)
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'DELIVERED')
        self.deliver()  # Retry must also identify the full target ref.

    def test_heads_main_branch_with_tag_collision(self):
        self.cli('init')
        self.git(self.repo, 'branch', '-m', 'heads/main')
        self.git(self.repo, 'tag', 'heads/main')
        self.setup_task()
        self.assertEqual(self.load(self.task)['target_branch'], 'heads/main')
        self.cli('check', task=self.task, candidate=self.baseline)
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'ACTIVE')
        self.candidate()
        self.evidence()  # Protocol fixtures, not an independent review.
        self.deliver()
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/heads/heads/main'), self.sha)
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/tags/heads/main'), self.baseline)
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'DELIVERED')

    def test_scope_is_exact_and_includes_rename_source(self):
        self.setup_task(scope=['app.py'])
        self.candidate()
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='OUTSIDE_SCOPE')
        self.unchanged()

    def test_rename_source_outside_scope_rejected(self):
        self.cli('init')
        (self.repo / 'old.py').write_text('content\n')
        self.git(self.repo, 'add', 'old.py')
        self.git(self.repo, 'commit', '-m', 'Old path')
        self.setup_task(scope=['new.py'])
        self.git(self.impl, 'mv', 'old.py', 'new.py')
        self.git(self.impl, 'commit', '-m', 'Rename')
        self.sha = self.git(self.impl, 'rev-parse', 'HEAD')
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='OUTSIDE_SCOPE')
        self.unchanged()

    def test_dirty_stale_head_and_stale_baseline(self):
        self.setup_task()
        self.candidate()
        self.cli('check', root=self.impl, task=self.task, candidate=self.baseline,
                 ok=False, error='CANDIDATE_MISMATCH')
        (self.impl / 'untracked').write_text('dirty')
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='DIRTY_WORKTREE')
        self.assertEqual(self.cli('recover', root=self.impl, task=self.task)['state'], 'DIRTY')
        (self.impl / 'untracked').unlink()
        self.git(self.repo, 'commit', '--allow-empty', '-m', 'Moved target')
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='STALE_BASELINE')
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'STALE')

    def test_failed_test_records_real_output(self):
        self.setup_task()
        self.candidate(bad=True)
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='impl', output=self.ev, ok=False, error='TEST_FAILED')
        ev = self.load(self.ev)
        self.assertNotEqual(ev['exit_code'], 0)
        self.assertIn('AssertionError', ev['stderr'])
        self.unchanged()

    def test_test_mutation_is_recorded_and_rejected(self):
        self.setup_task(command=[sys.executable, '-c', "from pathlib import Path; Path('app.py').write_text('changed')"])
        self.candidate()
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='impl', output=self.ev, ok=False, error='TEST_WORKTREE_CHANGED')
        self.assertEqual(self.load(self.ev)['exit_code'], 0)
        self.assertFalse(self.load(self.ev)['worktree_unchanged'])
        self.unchanged()

    def test_review_and_evidence_denials_and_rereview(self):
        self.setup_task()
        self.candidate()
        self.evidence()
        original = self.load(self.review)
        variants = [('verdict', 'FAIL', 'REVIEW_FAILED'), ('findings', ['fix needed'], 'REVIEW_FAILED'),
                    ('reviewer_session', 'implementer-fixture', 'SELF_REVIEW'),
                    ('candidate', self.baseline, 'REVIEW_BINDING_MISMATCH'),
                    ('task_digest', 'stale', 'REVIEW_BINDING_MISMATCH')]
        for key, value, error in variants:
            with self.subTest(key=key):
                self.save(self.review, dict(original, **{key: value}))
                self.deliver(ok=False, error=error)
                self.unchanged()
        self.review.unlink()
        self.deliver(ok=False, error='REVIEW_MISSING')
        self.save(self.review, original)
        independent = self.load(self.rev_ev)
        self.save(self.rev_ev, dict(independent, exit_code=1))
        self.deliver(ok=False, error='TEST_FAILED')
        self.save(self.rev_ev, independent)
        impl = self.load(self.ev)
        self.save(self.ev, dict(impl, task_digest='stale'))
        self.deliver(ok=False, error='EVIDENCE_BINDING_MISMATCH')
        self.save(self.ev, impl)
        # Fix changes the SHA: all previous evidence must be rerun/reviewed.
        (self.impl / 'app.py').write_text('VALUE = 42\n# fixed\n')
        self.git(self.impl, 'commit', '-am', 'Fix finding')
        self.sha = self.git(self.impl, 'rev-parse', 'HEAD')
        self.deliver(ok=False, error='EVIDENCE_BINDING_MISMATCH')
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='implementer-fixture', output=self.tmp / 'new-impl.json')
        self.ev = self.tmp / 'new-impl.json'
        self.git(self.reviewer, 'fetch', 'origin', 'implementer')
        self.git(self.reviewer, 'checkout', '--detach', self.sha)
        self.rev_ev = self.tmp / 'new-reviewer.json'
        self.cli('test', root=self.reviewer, task=self.task, candidate=self.sha,
                 session='reviewer-fixture-2', output=self.rev_ev)
        self.save(self.review, dict(original, candidate=self.sha, reviewer_session='reviewer-fixture-2',
                                   test_evidence=str(self.rev_ev)))
        self.deliver()

    def test_reviewer_changed_and_clone_mutation_denied(self):
        self.setup_task()
        self.candidate()
        self.evidence()
        self.cli('check', root=self.reviewer, task=self.task, candidate=self.sha,
                 ok=False, error='WRONG_COMMON_DIRECTORY')
        (self.reviewer / 'extra').write_text('dirty')
        self.deliver(ok=False, error='REVIEWER_CHANGED')
        (self.reviewer / 'extra').unlink()
        self.git(self.reviewer, 'checkout', '--detach', self.baseline)
        self.deliver(ok=False, error='REVIEWER_CHANGED')
        self.unchanged()

    def test_symlink_git_mode_without_os_symlink_privileges(self):
        self.setup_task(scope=['link'])
        blob = self.git(self.impl, 'hash-object', '-w', '--stdin')
        self.git(self.impl, 'update-index', '--add', '--cacheinfo', f'120000,{blob},link')
        self.git(self.impl, 'commit', '-m', 'Git symlink')
        self.git(self.impl, '-c', 'core.symlinks=false', 'checkout-index', '-f', '-a')
        self.sha = self.git(self.impl, 'rev-parse', 'HEAD')
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='UNSAFE_PATH')
        self.unchanged()

    def test_scope_traversal_and_prefix_rejected(self):
        self.cli('init')
        self.cli('authorize', task=self.task, requirements=self.req, scope='../escape',
                 test_command_json='["python"]', task_id='x', ok=False, error='UNSAFE_PATH')
        self.setup_task(scope=['app'])
        self.candidate()
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='OUTSIDE_SCOPE')

    def test_wrong_project_and_non_descendant(self):
        self.setup_task()
        self.candidate()
        task = self.load(self.task)
        self.save(self.task, dict(task, project_id='wrong'))
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='WRONG_PROJECT')
        self.save(self.task, task)
        tree = self.git(self.impl, 'rev-parse', 'HEAD^{tree}')
        orphan = self.git(self.impl, 'commit-tree', tree, '-m', 'Unrelated history')
        self.git(self.impl, 'reset', '--hard', orphan)
        self.cli('check', root=self.impl, task=self.task, candidate=orphan,
                 ok=False, error='NON_FAST_FORWARD')
        self.unchanged()

    def test_unrecorded_target_advance_is_not_delivery_retry(self):
        self.setup_task()
        self.candidate()
        self.evidence()
        self.git(self.repo, 'merge', '--ff-only', self.sha)
        self.assertEqual(self.cli('recover', task=self.task)['state'], 'STALE')
        self.deliver(ok=False, error='STALE_BASELINE')
        self.assertFalse(Path(self.load(self.task)['completion_path']).exists())

    def test_recover_orphan_worktree_reports_stale(self):
        self.setup_task()
        self.candidate()
        tree = self.git(self.impl, 'rev-parse', 'HEAD^{tree}')
        orphan = self.git(self.impl, 'commit-tree', tree, '-m', 'Orphan')
        self.git(self.impl, 'reset', '--hard', orphan)
        self.assertEqual(self.cli('recover', root=self.impl, task=self.task)['state'], 'STALE')
        self.unchanged()

    def test_gitlink_submodule_mode_is_rejected(self):
        self.setup_task(scope=['vendor'])
        self.git(self.impl, 'update-index', '--add', '--cacheinfo', f'160000,{self.baseline},vendor')
        self.git(self.impl, 'commit', '-m', 'Gitlink')
        (self.impl / 'vendor').mkdir()
        self.sha = self.git(self.impl, 'rev-parse', 'HEAD')
        self.cli('check', root=self.impl, task=self.task, candidate=self.sha,
                 ok=False, error='UNSAFE_PATH')
        self.unchanged()

    def test_evidence_and_delivery_root_denials(self):
        self.setup_task()
        self.candidate()
        self.evidence()
        original = self.ev.read_bytes()
        self.ev.unlink()
        self.deliver(ok=False, error='EVIDENCE_MISSING')
        self.ev.write_bytes(original)
        data = self.load(self.ev)
        self.save(self.ev, dict(data, exit_code=1))
        self.deliver(ok=False, error='TEST_FAILED')
        self.ev.write_bytes(original)
        (self.repo / 'dirty.txt').write_text('keep')
        self.deliver(ok=False, error='DIRTY_WORKTREE')
        (self.repo / 'dirty.txt').unlink()
        self.git(self.repo, 'checkout', '-b', 'other')
        self.deliver(ok=False, error='WRONG_TARGET_BRANCH')
        self.unchanged()

    def test_test_output_must_be_external_and_argv_is_authorized(self):
        self.setup_task(command=[sys.executable, '-c',
                                "import os; print(os.environ['PYTHONDONTWRITEBYTECODE']); print('trusted')"])
        self.candidate()
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha, session='impl',
                 output=self.impl / 'evidence.json', ok=False, error='PATH_NOT_EXTERNAL')
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='impl', output=self.ev)
        self.assertEqual(self.load(self.ev)['stdout'], '1\ntrusted\n')
        self.cli('test', root=self.impl, task=self.task, candidate=self.sha,
                 session='impl', output=self.ev, ok=False, error='OUTPUT_EXISTS')
        self.assertEqual(self.git(self.impl, 'status', '--porcelain'), '')


if __name__ == '__main__':
    unittest.main()
