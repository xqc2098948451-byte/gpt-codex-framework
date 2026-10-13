"""Project-local navigation only; never authorization or review evidence."""
import hashlib
import json
import re
import stat
import sys
from pathlib import Path
import codex_only as core

MAP = '.codex-only/project-map.json'
FIELDS = ('entry_points', 'key_files', 'tests', 'configuration')


def safe(root, name):
    core.safe_path(name)
    p = root
    for part in name.split('/'):
        p = p / part
        if p.exists() or p.is_symlink():
            st = p.lstat()
            core.require(not stat.S_ISLNK(st.st_mode) and not
                         (getattr(st, 'st_file_attributes', 0) & 1024), 'UNSAFE_PATH', name)
    core.require(p.resolve().is_relative_to(root), 'UNSAFE_PATH', name)
    return p


def modes(root, names):
    # Literal pathspecs prevent wildcard paths from widening these checks.
    for name in names:
        safe(root, name)
        ancestors = ['/'.join(name.split('/')[:i]) for i in range(1, len(name.split('/')) + 1)]
        for entry in core.git(root, 'ls-files', '--stage', '-z', '--',
                              *[':(literal)' + x for x in ancestors]).stdout.split('\0'):
            if entry:
                meta, path = entry.split('\t', 1)
                core.require(meta.split()[0] in ('100644', '100755') and meta.split()[2] == '0',
                             'UNSAFE_PATH', path)


def identity(root):
    modes(root, [core.IDENTITY, MAP])
    value = core.read_json(safe(root, core.IDENTITY), 'WRONG_PROJECT')
    core.require(set(value) == {'project_id', 'genesis'}, 'WRONG_PROJECT')
    core.require(value['genesis'] == core.genesis(root, 'HEAD'), 'WRONG_PROJECT')
    core.require(json.loads(core.gout(root, 'show', 'HEAD:' + core.IDENTITY)) == value, 'WRONG_PROJECT')
    return value


def description(root, value):
    core.require(isinstance(value.get('architecture'), str) and value['architecture'] and
                 isinstance(value.get('modules'), list) and value['modules'], 'INVALID_MAP')
    modules = {}
    prefixes = []
    for m in value['modules']:
        core.require(isinstance(m, dict) and set(m) == {'name', 'responsibility', 'paths',
                     'interfaces', 'depends_on', 'read_when', *FIELDS}, 'INVALID_MAP')
        name = m['name']
        core.require(isinstance(name, str) and re.fullmatch(r'[a-zA-Z0-9_-]+', name) and
                     name not in modules, 'INVALID_MAP')
        core.require(isinstance(m['responsibility'], str) and m['responsibility'], 'INVALID_MAP')
        for field in ('paths', 'interfaces', 'depends_on', 'read_when', *FIELDS):
            core.require(isinstance(m[field], list) and all(isinstance(x, str) and x for x in m[field]),
                         'INVALID_MAP')
        core.require(m['paths'] and m['read_when'], 'INVALID_MAP')
        for p in m['paths']:
            safe(root, p)
            core.require(not p.startswith('.codex-only') and not any(
                p == q or p.startswith(q + '/') or q.startswith(p + '/') for q in prefixes), 'INVALID_MAP')
            prefixes.append(p)
        for field in FIELDS:
            for p in m[field]:
                safe(root, p)
        modules[name] = m
    core.require(all(d in modules and d != n for n, m in modules.items() for d in m['depends_on']), 'INVALID_MAP')
    return modules


def owners(modules, path):
    return {n for n, m in modules.items() if any(path == p or path.startswith(p + '/') for p in m['paths'])}


def delta(root, anchor):
    paths = set(filter(None, core.git(root, 'diff', '--name-only', '--no-renames', '-z', anchor, '--').stdout.split('\0')))
    paths.update(filter(None, core.git(root, 'diff', '--cached', '--name-only', '--no-renames', '-z', anchor, '--').stdout.split('\0')))
    # Git discovers untracked names internally; no source text enters model context.
    paths.update(filter(None, core.git(root, 'ls-files', '--others', '--exclude-standard', '-z').stdout.split('\0')))
    return paths - {MAP, core.IDENTITY}


def fingerprint(root, name, metrics):
    modes(root, [name])
    p = safe(root, name)
    if not p.exists():
        return None
    core.require(p.is_file(), 'UNSAFE_PATH', name)
    data = p.read_bytes()
    metrics['source_reads'].append(dict(path=name, bytes=len(data)))
    return hashlib.sha256(data).hexdigest()


def load(root, ident):
    value = core.read_json(safe(root, MAP))
    core.require(value.get('schema_version') == 1 and value.get('authority') == 'NAVIGATION_ONLY', 'INVALID_MAP')
    core.require(all(value.get(k) == v for k, v in ident.items()), 'WRONG_PROJECT')
    modules = description(root, value)
    core.require(isinstance(value.get('anchor'), str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', value['anchor']), 'INVALID_MAP')
    core.require(core.git(root, 'merge-base', '--is-ancestor', value['anchor'], 'HEAD', check=False).returncode == 0,
                 'MAP_REBUILD_REQUIRED', 'Anchor is not an ancestor; explicitly bound a rebuild')
    core.require(isinstance(value.get('snapshot'), dict) and isinstance(value.get('dirty_paths'), list), 'INVALID_MAP')
    for p, h in value['snapshot'].items():
        safe(root, p)
        core.require(p not in (MAP, core.IDENTITY) and isinstance(h, str) and re.fullmatch('[0-9a-f]{64}', h), 'INVALID_MAP')
    for p in value['dirty_paths']:
        safe(root, p)
        core.require(p not in (MAP, core.IDENTITY), 'INVALID_MAP')
    core.require(all(owners(modules, p) for p in value['snapshot']), 'INVALID_MAP')
    core.require(all(p in value['snapshot'] for m in modules.values() for field in FIELDS for p in m[field]),
                 'INVALID_MAP', 'Navigation target absent from snapshot')
    return value


def run(args, metrics):
    root = core.root_path(args.root)
    ident = identity(root)
    if args.command != 'locate':
        task, _ = core.load_task(args.task, root)
        core.project(root, task)
        core.require(MAP in task['scope'], 'OUTSIDE_SCOPE', MAP)
        core.require(core.target(root, task) == task['baseline'], 'STALE_BASELINE')
        core.require(core.git(root, 'merge-base', '--is-ancestor', task['baseline'], 'HEAD', check=False).returncode == 0,
                     'NON_FAST_FORWARD')
    exists = safe(root, MAP).exists()
    if args.command == 'build':
        core.require(not exists, 'OUTPUT_EXISTS', 'Use bounded update for an existing map')
        old = None
    elif not exists:
        core.require(args.command == 'locate', 'MAP_MISSING')
        return dict(state='MAP_MISSING', next='Authorized initial build required')
    else:
        old = load(root, ident)
    before = description(root, old) if old else {}
    selected = set(args.module or []) & before.keys()
    related = set(selected)
    for n in selected:
        related.update(before[n]['depends_on'])
    changed = {}
    if old:
        for p in sorted(delta(root, old['anchor']) | set(old['dirty_paths'])):
            if args.command == 'locate' and not owners(before, p) & related:
                modes(root, [p])
                changed[p] = 'UNVERIFIED_UNSELECTED'
                continue
            h = fingerprint(root, p, metrics)
            if h != old['snapshot'].get(p):
                changed[p] = h
    affected = set().union(*(owners(before, p) for p in changed)) if changed else set()
    unknown = [p for p in changed if not owners(before, p)]
    if args.command == 'locate':
        # Changed providers invalidate their consumers, including transitive consumers.
        stale = set(affected)
        while True:
            extra = {n for n, m in before.items() if set(m['depends_on']) & stale}
            if extra <= stale:
                break
            stale.update(extra)
        state = 'MAP_MISS' if len(selected) != len(args.module or []) or not selected else (
            'MAP_PARTIAL' if related & stale or unknown else 'MAP_HIT')
        result = dict(state=state, architecture=old['architecture'], anchor=old['anchor'],
                      modules=[dict(before[n], validity='STALE' if n in stale or unknown else 'CURRENT') for n in sorted(related)],
                      affected_modules=sorted(stale), unknown_paths=unknown,
                      changed_paths=sorted(changed), next='Read selected key/entry/test/config files' if state == 'MAP_HIT' else 'Bound discovery and update reviewed module descriptions')
        return result
    supplied = core.read_json(core.external(args.description, root))
    after = description(root, supplied)
    if old:
        bound = set(args.module or [])
        metadata_changed = {n for n in before.keys() | after.keys() if before.get(n) != after.get(n)}
        new_affected = set().union(*(owners(after, p) for p in changed)) if changed else set()
        core.require(affected | new_affected | metadata_changed <= bound, 'MAP_REBUILD_REQUIRED', 'Include all affected old/new modules')
        core.require(bound and bound <= before.keys() | after.keys(), 'MAP_REBUILD_REQUIRED')
        core.require(all(owners(after, p) for p, h in changed.items() if h is not None), 'MAP_REBUILD_REQUIRED', 'Unmapped paths need an explicit bounded module description')
        snapshot = dict(old['snapshot'])
        for p, h in changed.items():
            if h is None:
                snapshot.pop(p, None)
            else:
                snapshot[p] = h
    else:
        metrics['full_discovery'] = True
        metrics['discovery_reason'] = 'Authorized first build'
        names = set(filter(None, core.git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').stdout.split('\0'))) - {MAP, core.IDENTITY}
        core.require(all(owners(after, p) for p in names), 'MAP_REBUILD_REQUIRED', 'Description must cover discovered files')
        snapshot = {}
        for p in sorted(names):
            h = fingerprint(root, p, metrics)
            if h is not None:
                snapshot[p] = h
    core.require(all(owners(after, p) for p in snapshot), 'MAP_REBUILD_REQUIRED', 'Split/merge must retain coverage')
    for m in after.values():
        for field in FIELDS:
            for p in m[field]:
                core.require(p in snapshot, 'MAP_REBUILD_REQUIRED', 'Missing navigation target: ' + p)
                modes(root, [p])
    value = dict(schema_version=1, authority='NAVIGATION_ONLY', **ident,
                 architecture=supplied['architecture'], modules=list(after.values()),
                 anchor=core.head(root), dirty_paths=sorted(delta(root, core.head(root))), snapshot=snapshot)
    modes(root, [MAP])
    core.write_json(safe(root, MAP), value, replace=old is not None)
    return dict(state='MAP_HIT', map=MAP, updated_modules=sorted(after if old is None else bound))


def main(argv=None):
    metrics = dict(source_reads=[], full_discovery=False)
    try:
        parser = core.Parser(description=__doc__)
        sub = parser.add_subparsers(dest='command', required=True)
        for name in ('build', 'locate', 'update'):
            p = sub.add_parser(name)
            p.add_argument('--root', required=True)
            p.add_argument('--module', action='append')
            if name != 'locate':
                p.add_argument('--task', required=True)
                p.add_argument('--description', required=True)
        result = dict(ok=True, **run(parser.parse_args(argv), metrics))
        code = 0
    except core.Denied as exc:
        result = dict(ok=False, state='MAP_PARTIAL', error=exc.code, detail=exc.detail)
        code = 1
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = dict(ok=False, state='MAP_PARTIAL', error='INVALID_MAP', detail=str(exc))
        code = 1
    metrics['source_files'] = len(metrics['source_reads'])
    metrics['source_bytes'] = sum(x['bytes'] for x in metrics['source_reads'])
    result['metrics'] = metrics
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
