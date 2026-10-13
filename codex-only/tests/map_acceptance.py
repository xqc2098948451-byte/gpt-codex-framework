"""Repeatable synthetic evidence, or read-only acceptance via the existing CLI test.

--prepare creates a new, retained four-module project (no review fixtures).
--verify-root reads a supplied candidate; suitable for both actual A and B sessions.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import codex_only as core
import project_map as nav


class Recorder:
    def __init__(self, output):
        self.output = output
        output.mkdir(parents=True, exist_ok=False)
        self.records = []

    def run(self, label, argv, expected=0):
        p = subprocess.run([str(x) for x in argv], capture_output=True,
                           env=dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1'))
        stdout, stderr = p.stdout.decode('utf-8'), p.stderr.decode('utf-8')
        record = dict(label=label, argv=[str(x) for x in argv], exit_code=p.returncode,
                      stdout=stdout, stderr=stderr,
                      cli_text_bytes=len(p.stdout) + len(p.stderr),
                      model_injected_source_bytes=0, model_injected_source_paths=[])
        try:
            record['result'] = json.loads(stdout)
        except ValueError:
            pass
        self.records.append(record)
        self.flush()
        if p.returncode != expected:
            raise AssertionError(record)
        return record.get('result', stdout.strip())

    def flush(self):
        (self.output / 'raw.json').write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding='utf-8')

    def inject(self, label, root, names):
        # Explicit source payload saved for an observer; never confuse Git lists with reads.
        chunks = []
        paths = []
        for name in sorted(set(names)):
            data = nav.safe(root, name).read_bytes()
            paths.append(dict(path=name, bytes=len(data)))
            chunks.append('--- ' + name + '\n' + data.decode('utf-8'))
        payload = '\n'.join(chunks)
        (self.output / (label + '-source.txt')).write_bytes(payload.encode('utf-8'))
        self.records.append(dict(label=label, actual_source_reads=paths,
                                 source_files=len(paths), source_bytes=sum(x['bytes'] for x in paths),
                                 model_visible_payload_bytes=len(payload.encode('utf-8')),
                                 note='Prepared explicit source payload; not proof another native session consumed it'))
        self.flush()


def prepare(base):
    base.mkdir(parents=True, exist_ok=False)
    rec = Recorder(base / 'evidence')
    delivery, scenario = base / 'delivery', base / 'scenarios'
    task, desc = base / 'task.json', base / 'description.json'
    req = base / 'requirements.md'
    req.write_text('1. Goal: persistent map for modular commerce.\n2. Behavior: scoped pricing lookup.\n'
                   '3. IO: map JSON and pricing API.\n4. Rules: exact scope, independent sessions.\n'
                   '5. Errors: reject invalid map and unsafe paths.\n6. GWT: build, delta, independent test, FF deliver/recover.\n', encoding='utf-8')

    def git(root, *args):
        return rec.run('git-' + args[0], [core.GIT, '-C', root, '-c', 'user.name=Codex Pilot',
                       '-c', 'user.email=codex-pilot@example.invalid', *args])

    def cli(action, root, *args, expected=0):
        return rec.run(action, [sys.executable, '-B', BASE / 'codex_only.py', action, '--root', root, *args], expected)

    def maprun(label, action, modules=(), expected=0):
        argv = [sys.executable, '-B', BASE / 'project_map.py', action, '--root', scenario]
        if action != 'locate':
            argv += ['--task', task, '--description', desc]
        for m in modules:
            argv += ['--module', m]
        return rec.run(label, argv, expected)

    delivery.mkdir()
    git(delivery, 'init', '-b', 'main')
    cli('init', delivery)
    modules = []
    for name, purpose in [('pricing', 'Calculate quotes and discounts'), ('catalog', 'Manage product descriptions'),
                          ('reporting', 'Aggregate sales reports'), ('shared', 'Money and identifiers')]:
        folder = delivery / name
        folder.mkdir()
        (folder / 'api.py').write_text('VALUE = 1\n', encoding='utf-8')
        (folder / 'test_api.py').write_text('from pathlib import Path\nassert Path(__file__).with_name("api.py").is_file()\n', encoding='utf-8')
        (folder / 'settings.json').write_text('{"enabled":true}\n', encoding='utf-8')
        for i in range(24):
            (folder / f'part_{i:02}.py').write_text(
                '\n'.join(f'def operation_{j}(value):\n    return value + {i + j}\n' for j in range(30)), encoding='utf-8')
        modules.append(dict(name=name, responsibility=purpose, paths=[name], entry_points=[name + '/api.py'],
                            key_files=[name + '/api.py'], interfaces=['VALUE'], depends_on=['shared'] if name != 'shared' else [],
                            tests=[name + '/test_api.py'], configuration=[name + '/settings.json'],
                            read_when=['Read when changing ' + purpose.lower()]))
    description = dict(architecture='Four commerce modules with a shared value layer', modules=modules)
    desc.write_text(json.dumps(description, indent=2), encoding='utf-8')
    git(delivery, 'add', '.')
    git(delivery, 'commit', '-m', 'Representative four module baseline')
    cli('authorize', delivery, '--task', task, '--requirements', req, '--scope', nav.MAP,
        '--scope', 'pricing/api.py', '--test-command-json',
        json.dumps([sys.executable, '-B', str(Path(__file__).resolve()), '--verify-root', '{root}']), '--task-id', 'issue28-synthetic')
    git(delivery, 'worktree', 'add', '-b', 'map-scenarios', str(scenario))
    maprun('initial-build', 'build')
    maprun('subsequent-pricing-locate', 'locate', ['pricing'])
    rec.inject('subsequent-pricing', scenario, ['pricing/api.py', 'pricing/test_api.py', 'pricing/settings.json', 'shared/api.py'])
    (scenario / 'catalog/part_00.py').write_text('VALUE = 2\n', encoding='utf-8')
    result = maprun('unrelated-change', 'locate', ['pricing'])
    assert result['state'] == 'MAP_HIT' and result['metrics']['source_files'] == 0
    git(scenario, 'restore', 'catalog/part_00.py')
    (scenario / 'pricing/api.py').write_text('VALUE = 2\n', encoding='utf-8')
    assert maprun('related-change', 'locate', ['pricing'])['state'] == 'MAP_PARTIAL'
    maprun('related-update', 'update', ['pricing'])
    maprun('dirty-snapshot-hit', 'locate', ['pricing'])
    # Commit only the business file: the map anchor is never self-referential.
    git(scenario, 'add', 'pricing/api.py')
    git(scenario, 'commit', '-m', 'Pricing change')
    assert maprun('dirty-to-commit', 'locate', ['pricing'])['state'] == 'MAP_HIT'
    (scenario / 'pricing/added.py').write_text('ADDED = True\n', encoding='utf-8')
    maprun('added', 'locate', ['pricing'])
    maprun('added-update', 'update', ['pricing'])
    git(scenario, 'mv', 'pricing/part_01.py', 'pricing/moved.py')
    maprun('renamed', 'locate', ['pricing'])
    maprun('renamed-update', 'update', ['pricing'])
    (scenario / 'pricing/part_02.py').unlink()
    maprun('deleted', 'locate', ['pricing'])
    maprun('deleted-update', 'update', ['pricing'])
    git(scenario, 'mv', 'pricing/api.py', 'pricing/entry.py')
    maprun('dangling-entry-rejected', 'update', ['pricing'], expected=1)
    modules[0]['entry_points'] = modules[0]['key_files'] = ['pricing/entry.py']
    modules[0]['depends_on'] = ['shared', 'catalog']
    desc.write_text(json.dumps(description), encoding='utf-8')
    maprun('entry-dependency-update', 'update', ['pricing'])
    # Split and merge are reviewed metadata updates, not inferred from filenames.
    split = dict(modules[0], name='discounts', paths=['pricing/added.py'],
                 entry_points=['pricing/added.py'], key_files=['pricing/added.py'], tests=[], configuration=[])
    modules[0]['paths'] = ['pricing/' + p.name for p in (scenario / 'pricing').iterdir() if p.name != 'added.py']
    modules.append(split)
    desc.write_text(json.dumps(description), encoding='utf-8')
    maprun('split-update', 'update', ['pricing', 'discounts'])
    modules.pop()
    modules[0]['paths'] = ['pricing']
    desc.write_text(json.dumps(description), encoding='utf-8')
    maprun('merge-update', 'update', ['pricing', 'discounts'])
    mapfile = scenario / nav.MAP
    saved = mapfile.read_bytes()
    for label, data in [('corrupt', b'{'), ('identity-mismatch', json.dumps(dict(json.loads(saved), project_id='wrong')).encode())]:
        mapfile.write_bytes(data)
        maprun(label, 'locate', ['pricing'], expected=1)
    bad = json.loads(saved)
    bad['modules'][0]['key_files'] = ['../outside']
    mapfile.write_text(json.dumps(bad), encoding='utf-8')
    maprun('unsafe-path', 'locate', ['pricing'], expected=1)
    mapfile.unlink()
    assert maprun('missing', 'locate', ['pricing'])['state'] == 'MAP_MISSING'
    mapfile.write_bytes(saved)
    # Preserve authorization; a separate protocol fixture demonstrates no-write denial.
    task_before = task.read_bytes()
    denied = json.loads(task_before)
    denied['scope'] = ['pricing/api.py']
    denial_task = base / 'denied-task-protocol-fixture.json'
    denial_task.write_text(json.dumps(denied), encoding='utf-8')
    rec.run('scope-no-write', [sys.executable, '-B', BASE / 'project_map.py', 'update', '--root', scenario,
                            '--task', denial_task, '--description', desc, '--module', 'pricing'], 1)
    assert mapfile.read_bytes() == saved and task.read_bytes() == task_before
    # Restore the experimental structure, leaving only the authorized pricing change + map.
    git(scenario, 'restore', '--source=HEAD', '--staged', '--worktree', 'pricing')
    (scenario / 'pricing/added.py').unlink()
    modules[0]['entry_points'] = modules[0]['key_files'] = ['pricing/api.py']
    modules[0]['depends_on'] = ['shared']
    desc.write_text(json.dumps(description, indent=2), encoding='utf-8')
    maprun('final-bounded-update', 'update', ['pricing'])
    # This portable final map must anchor to the authorized baseline, present in B's clone.
    # HEAD is a descendant of baseline; use the final scenario commit as implementer start.
    state = dict(delivery=str(delivery), scenario=str(scenario), task=str(task), description=str(desc),
                 scenario_sha=core.head(scenario), evidence=str(rec.output), map=nav.MAP,
                 next='After Framework commit, create implementer worktree at scenario_sha, copy map, commit, run CLI test with real session')
    (base / 'handoff.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(json.dumps(state))


def verify(root):
    root = core.root_path(root)
    results = []
    reads = []
    for name in ('pricing', 'catalog', 'reporting', 'shared'):
        p = subprocess.run([sys.executable, '-B', str(BASE / 'project_map.py'), 'locate', '--root', str(root),
                            '--module', name], capture_output=True, encoding='utf-8')
        assert p.returncode == 0, p.stdout + p.stderr
        result = json.loads(p.stdout)
        assert result['state'] == 'MAP_HIT', result
        assert not result['metrics']['full_discovery'], result
        results.append(result)
        data = nav.safe(root, name + '/api.py').read_bytes()
        assert data.decode('utf-8').splitlines() == ['VALUE = 2' if name == 'pricing' else 'VALUE = 1']
        reads.append(dict(path=name + '/api.py', bytes=len(data)))
    print(json.dumps(dict(acceptance='PASS', results=results,
                         explicit_source_reads=reads), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', type=Path)
    group.add_argument('--verify-root', type=Path)
    args = parser.parse_args()
    prepare(args.prepare.resolve()) if args.prepare else verify(args.verify_root)
