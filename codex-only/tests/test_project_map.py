"""Real Git integration tests. No independent-review evidence is fabricated."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import test_codex_only as workflow
BASE = workflow.BASE


class MapTests(workflow.WorkflowTests):
    # Reuse only fixture helpers; inherited workflow tests are removed below.
    def setUp(self):
        super().setUp()
        self.cli('init')
        for name in ('pricing', 'catalog', 'shared'):
            (self.repo / name).mkdir()
            (self.repo / name / 'api.py').write_text('VALUE = 1\n')
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Modules')
        self.desc = self.tmp / 'description.json'
        self.description = dict(architecture='Three modules', modules=[dict(
            name=n, responsibility=n, paths=[n], entry_points=[n + '/api.py'],
            key_files=[n + '/api.py'], interfaces=['VALUE'],
            depends_on=['shared'] if n == 'pricing' else [], tests=[],
            configuration=[], read_when=['Changes to ' + n])
            for n in ('pricing', 'catalog', 'shared')])
        self.save(self.desc, self.description)
        self.cli('authorize', task=self.task, requirements=self.req,
                 scope=['.codex-only/project-map.json', 'pricing/api.py'],
                 test_command_json=json.dumps([sys.executable, '-c', 'pass']), task_id='map-fixture')
        self.git(self.repo, 'checkout', '-b', 'map-work')
        self.mapfile = self.repo / '.codex-only/project-map.json'

    def nav(self, action, ok=True, **kw):
        argv = [sys.executable, '-B', str(BASE / 'project_map.py'), action,
                '--root', str(self.repo)]
        if action != 'locate':
            kw.update(task=self.task, description=self.desc)
        for k, v in kw.items():
            for value in v if isinstance(v, list) else [v]:
                argv += ['--' + k.replace('_', '-'), str(value)]
        p = subprocess.run(argv, capture_output=True, encoding='utf-8')
        self.assertEqual(p.returncode == 0, ok, (argv, p.stdout, p.stderr))
        return json.loads(p.stdout)

    def test_build_route_and_unrelated_change(self):
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_MISSING')
        self.nav('build')
        hit = self.nav('locate', module='pricing')
        self.assertEqual(hit['state'], 'MAP_HIT')
        self.assertEqual(hit['metrics']['source_reads'], [])
        (self.repo / 'catalog/api.py').write_text('VALUE = 2\n')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        self.assertEqual(self.nav('locate', module='catalog')['state'], 'MAP_PARTIAL')
        self.assertEqual(self.nav('locate', module='absent')['state'], 'MAP_MISS')

    def test_f1_unrelated_batch_is_count_only(self):
        self.nav('build')
        for i in range(24):
            (self.repo / f'catalog/part_{i:02}.py').write_text('VALUE = 2\n')
        result = self.nav('locate', module='pricing')
        self.assertEqual(result['state'], 'MAP_HIT')
        self.assertEqual(result['changed_paths'], [])
        self.assertEqual(result['unrelated_changed_paths_count'], 24)
        self.assertEqual(result['metrics']['source_files'], 0)

    def test_f1_bounded_details_and_complete_audit(self):
        names = [f'pricing/part_{i:02}.py' for i in range(30)]
        for name in names:
            (self.repo / name).write_text('VALUE = 1\n')
        self.description['modules'][0]['key_files'] = names
        self.save(self.desc, self.description)
        audit = self.tmp / 'build-audit.json'
        result = self.nav('build', audit=audit)
        full = self.load(audit)
        self.assertEqual(full['metrics']['source_files'], 33)
        self.assertEqual(len(full['metrics']['source_reads']), 33)
        self.assertEqual(result['metrics']['source_bytes'], sum(x['bytes'] for x in full['metrics']['source_reads']))
        self.assertLessEqual(len(result['metrics']['source_reads']), 20)
        self.assertTrue(result['metrics']['source_reads_truncated'])
        for name in names:
            (self.repo / name).write_text('VALUE = 2\n')
        result = self.nav('locate', module='pricing', audit=self.tmp / 'locate-audit.json')
        self.assertEqual(result['changed_paths_count'], 30)
        self.assertLessEqual(len(result['changed_paths']), 20)
        self.assertTrue(result['changed_paths_truncated'])
        self.assertEqual(result['metrics']['source_files'], 30)
        module = next(m for m in result['modules'] if m['name'] == 'pricing')
        self.assertEqual(module['key_files_count'], 30)
        self.assertLessEqual(len(module['key_files']), 20)
        self.assertTrue(module['key_files_truncated'])
        self.assertEqual(len(self.load(self.tmp / 'locate-audit.json')['changed_paths']), 30)
        self.nav('locate', module='pricing', audit=self.repo / 'audit.json', ok=False)
        self.assertFalse((self.repo / 'audit.json').exists())

    def test_f2_cross_references_deleted_or_moved(self):
        self.nav('build')
        for field in ('entry_points', 'key_files', 'tests', 'configuration'):
            with self.subTest(field=field):
                self.description['modules'][0][field] = ['catalog/api.py']
                self.save(self.desc, self.description)
                self.nav('update', module='pricing')
                self.git(self.repo, 'mv', 'catalog/api.py', 'catalog/moved.py')
                result = self.nav('locate', module='pricing')
                self.assertEqual(result['state'], 'MAP_PARTIAL')
                self.assertEqual(next(m for m in result['modules'] if m['name'] == 'pricing')['validity'], 'STALE')
                self.nav('update', module=['pricing', 'catalog'], ok=False)
                self.git(self.repo, 'restore', '--source=HEAD', '--staged', '--worktree', 'catalog')
                (self.repo / 'catalog/api.py').unlink()
                self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')
                self.git(self.repo, 'restore', 'catalog/api.py')

    def test_f2_central_reference_without_directory_owner(self):
        (self.repo / 'config').mkdir()
        (self.repo / 'config/settings.json').write_text('{}')
        self.description['modules'][0]['configuration'] = ['config/settings.json']
        self.save(self.desc, self.description)
        self.nav('build')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        (self.repo / 'config/settings.json').unlink()
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')

    def test_f3_multihop_dirty_commit_revert_and_cycle(self):
        self.nav('build')
        modules = self.description['modules']
        modules[0]['depends_on'] = ['catalog']
        modules[1]['depends_on'] = ['shared']
        self.save(self.desc, self.description)
        p = self.repo / 'shared/api.py'
        p.write_text('VALUE = 2\n')
        self.nav('update', module=['pricing', 'catalog', 'shared'])
        for cycle in (False, True):
            if cycle:
                modules[2]['depends_on'] = ['pricing']
                self.save(self.desc, self.description)
                self.nav('update', module='shared')
            result = self.nav('locate', module='pricing')
            self.assertEqual(result['state'], 'MAP_HIT')
            self.assertEqual(len(result['modules']), 3)
            self.assertEqual(result['metrics']['source_reads'], [dict(path='shared/api.py', bytes=len(p.read_bytes()))])
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Commit multihop snapshot')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        p.write_text('VALUE = 1\n')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')
        self.nav('update', module='shared')
        self.git(self.repo, 'restore', 'shared/api.py')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')

    def test_dirty_commit_revert_and_update(self):
        self.nav('build')
        p = self.repo / 'pricing/api.py'
        p.write_text('VALUE = 2\n')
        self.nav('update', module='pricing')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Commit dirty snapshot')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        p.write_text('VALUE = 1\n')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')
        self.nav('update', module='pricing')
        self.git(self.repo, 'restore', 'pricing/api.py')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')

    def test_scope_corruption_identity_and_paths(self):
        task = self.load(self.task)
        self.save(self.task, dict(task, scope=['pricing/api.py']))
        self.assertEqual(self.nav('build', ok=False)['error'], 'OUTSIDE_SCOPE')
        self.assertFalse(self.mapfile.exists())
        self.save(self.task, task)
        self.nav('build')
        original = self.load(self.mapfile)
        for path in ('../escape', '/escape', 'C:/escape', 'pricing/../escape'):
            bad = json.loads(json.dumps(original))
            bad['modules'][0]['key_files'] = [path]
            self.save(self.mapfile, bad)
            self.assertEqual(self.nav('locate', module='pricing', ok=False)['error'], 'UNSAFE_PATH')
        self.save(self.mapfile, dict(original, project_id='wrong'))
        self.assertEqual(self.nav('locate', module='pricing', ok=False)['error'], 'WRONG_PROJECT')
        self.save(self.mapfile, dict(original, snapshot={}))
        self.assertEqual(self.nav('locate', module='pricing', ok=False)['error'], 'INVALID_MAP')
        self.mapfile.write_text('{')
        self.nav('locate', module='pricing', ok=False)

    def test_add_delete_rename_and_bounded_metadata(self):
        self.nav('build')
        self.git(self.repo, 'mv', 'pricing/api.py', 'pricing/new.py')
        self.nav('update', module='catalog', ok=False)
        self.nav('update', module='pricing', ok=False)  # dangling entry
        m = self.description['modules'][0]
        m['entry_points'] = m['key_files'] = ['pricing/new.py']
        self.save(self.desc, self.description)
        self.nav('update', module='pricing')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        (self.repo / 'unknown.py').write_text('x=1')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')
        self.nav('update', module='pricing', ok=False)

    def test_git_symlink_and_submodule_refused(self):
        self.nav('build')
        blob = self.git(self.repo, 'hash-object', '-w', '--stdin')
        for mode, oid in [('120000', blob), ('160000', self.git(self.repo, 'rev-parse', 'HEAD'))]:
            self.git(self.repo, 'update-index', '--add', '--cacheinfo', f'{mode},{oid},pricing/unsafe')
            self.assertEqual(self.nav('locate', module='pricing', ok=False)['error'], 'UNSAFE_PATH')
            self.git(self.repo, 'update-index', '--force-remove', 'pricing/unsafe')

    def test_dependency_split_merge_and_cold_process(self):
        self.nav('build')
        (self.repo / 'shared/api.py').write_text('VALUE = 9\n')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_PARTIAL')
        self.nav('update', module='shared')
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_HIT')
        m = self.description['modules'][0]
        m['depends_on'] = ['catalog']
        self.save(self.desc, self.description)
        self.nav('update', module='catalog', ok=False)
        self.nav('update', module='pricing')
        m['name'] = 'quotes'
        self.save(self.desc, self.description)
        self.nav('update', module=['pricing', 'quotes'])
        self.assertEqual(self.nav('locate', module='pricing')['state'], 'MAP_MISS')
        self.assertEqual(self.nav('locate', module='quotes')['state'], 'MAP_HIT')

    def test_reparse_point_rejected_before_source_read(self):
        self.nav('build')
        outside = self.tmp / 'outside'
        outside.mkdir()
        (outside / 'secret.py').write_text('DO NOT READ')
        link = self.repo / 'pricing/link'
        if os.name == 'nt':
            quoted = lambda p: "'" + str(p).replace("'", "''") + "'"
            p = subprocess.run(['powershell', '-NoProfile', '-Command',
                                'New-Item -ItemType Junction -Path ' + quoted(link) + ' -Target ' + quoted(outside)],
                               capture_output=True)
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            link.symlink_to(outside, target_is_directory=True)
        try:
            result = self.nav('locate', module='pricing', ok=False)
            self.assertEqual(result['error'], 'UNSAFE_PATH')
            self.assertEqual(result['metrics']['source_reads'], [])
        finally:
            os.rmdir(link) if os.name == 'nt' else link.unlink()


# Avoid running the inherited 22 workflow tests twice.
for _name in list(vars(workflow.WorkflowTests)):
    if _name.startswith('test_'):
        setattr(MapTests, _name, None)

if __name__ == '__main__':
    unittest.main()
