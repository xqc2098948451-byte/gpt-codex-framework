"""Small, local Git workflow. External review is data, never an implementer role."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

IDENTITY = '.codex-only/project.json'
GIT = os.environ.get('CODEX_ONLY_GIT') or shutil.which('git')
if not GIT and Path('C:/Program Files/Git/cmd/git.exe').exists():
    GIT = 'C:/Program Files/Git/cmd/git.exe'


class Denied(Exception):
    def __init__(self, code, detail=''):
        self.code, self.detail = code, detail
        super().__init__(detail)


def require(condition, code, detail=''):
    if not condition:
        raise Denied(code, detail)


def git(root, *args, check=True, env=None):
    require(GIT, 'GIT_UNAVAILABLE')
    clean_env = os.environ.copy()
    # Inherited Git routing must not override the explicit root or index.
    for key in list(clean_env):
        if key.startswith('GIT_'):
            clean_env.pop(key)
    clean_env.update(env or {})
    p = subprocess.run([GIT, '-C', str(root), *args], env=clean_env,
                       capture_output=True, encoding='utf-8', errors='replace')
    require(not check or p.returncode == 0, 'GIT_ERROR', p.stderr.strip())
    return p


def gout(root, *args):
    return git(root, *args).stdout.strip()


def root_path(value):
    root = Path(value).resolve()
    p = git(root, 'rev-parse', '--show-toplevel', check=False)
    require(p.returncode == 0, 'NOT_GIT_ROOT')
    require(Path(p.stdout.strip()).resolve() == root, 'ROOT_NOT_TOPLEVEL')
    return root


def common_dir(root):
    return str(Path(gout(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve())


def external(value, root):
    path = Path(value).resolve()
    require(not path.is_relative_to(root), 'PATH_NOT_EXTERNAL', str(path))
    # In linked worktrees the common metadata directory is outside the root.
    require(not path.is_relative_to(Path(common_dir(root))), 'PATH_NOT_EXTERNAL', str(path))
    return path


def read_json(path, missing='INVALID_JSON'):
    require(Path(path).is_file(), missing, str(path))
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as exc:
        raise Denied('INVALID_JSON', str(exc)) from exc
    require(isinstance(value, dict), 'INVALID_JSON', 'Expected JSON object')
    return value


def write_json(path, data, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if not replace:
        try:
            with path.open('x', encoding='utf-8') as stream:
                stream.write(content)
        except FileExistsError as exc:
            raise Denied('OUTPUT_EXISTS', str(path)) from exc
        return
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dirty(root):
    return bool(gout(root, 'status', '--porcelain=v1', '--untracked-files=all'))


def head(root):
    return gout(root, 'rev-parse', 'HEAD')


def genesis(root, ref):
    roots = gout(root, 'rev-list', '--max-parents=0', ref).splitlines()
    require(len(roots) == 1, 'WRONG_PROJECT', 'Expected exactly one genesis commit')
    return roots[0]


def safe_path(path):
    require(isinstance(path, str) and path and not path.startswith('/') and
            '\\' not in path and ':' not in path and '\x00' not in path,
            'UNSAFE_PATH', str(path))
    require(all(part not in ('', '.', '..') and part.lower() != '.git' and
                not part.endswith(('.', ' ')) for part in path.split('/')),
            'UNSAFE_PATH', path)
    return path


def load_task(path, root, allow_revoked=False):
    path = external(path, root)
    task = read_json(path, 'AUTHORIZATION_MISSING')
    required = {'project_id', 'genesis', 'baseline', 'target_branch', 'common_dir',
                'requirements', 'requirements_digest', 'scope', 'test_argv',
                'authority', 'task_id', 'completion_path'}
    require(required <= task.keys(), 'INVALID_TASK')
    require(task['authority'] == 'user:authorize-cli', 'AUTHORIZATION_MISSING')
    require(all(isinstance(task[k], str) and task[k] for k in required - {'scope', 'test_argv'}),
            'INVALID_TASK')
    require(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', task['baseline']), 'INVALID_TASK')
    require(git(root, 'check-ref-format', 'refs/heads/' + task['target_branch'], check=False).returncode == 0,
            'INVALID_TASK')
    require(hashlib.sha256(task['requirements'].encode('utf-8')).hexdigest() == task['requirements_digest'],
            'INVALID_TASK')
    require(isinstance(task['scope'], list) and task['scope'], 'INVALID_TASK')
    for path_item in task['scope']:
        safe_path(path_item)
    require(isinstance(task['test_argv'], list) and task['test_argv'] and
            all(isinstance(x, str) and x and '\x00' not in x for x in task['test_argv']), 'INVALID_TASK')
    completion = external(task['completion_path'], root)
    require(completion != path, 'INVALID_TASK')
    task_digest = digest(path)
    if not allow_revoked:
        assert_not_revoked(root, task, task_digest)
    return task, task_digest


def task_control(task):
    # Task identity survives a byte-for-byte copy to another external path.
    identity = [task['project_id'], task['genesis'], task['task_id']]
    key = hashlib.sha256(json.dumps(identity).encode('utf-8')).hexdigest()
    common = Path(task['common_dir'])
    require(common.is_absolute() and common.resolve() == common, 'INVALID_TASK')
    require(common.is_dir(), 'REVOCATION_UNAVAILABLE', str(common))
    control = common / 'codex-only-revocations'
    require(control.resolve() == control, 'UNSAFE_PATH', str(control))
    return control / key


def revocation(task, task_digest):
    path = task_control(task).with_suffix('.json')
    require(path.resolve() == path, 'UNSAFE_PATH', str(path))
    if not path.exists():
        return None
    record = read_json(path)
    expected = dict(state='REVOKED', project_id=task['project_id'], genesis=task['genesis'],
                    task_id=task['task_id'], task_digest=task_digest,
                    baseline=task['baseline'], target_branch=task['target_branch'],
                    common_dir=task['common_dir'], completion_path=task['completion_path'])
    require(all(record.get(k) == v for k, v in expected.items()), 'REVOCATION_MISMATCH')
    return dict(record=record, path=str(path))


def assert_not_revoked(root, task, task_digest):
    # Verify the calling project's identity before accessing the original project's marker.
    identity = read_json(root / IDENTITY, 'WRONG_PROJECT')
    require(identity == dict(project_id=task['project_id'], genesis=task['genesis']), 'WRONG_PROJECT')
    require(revocation(task, task_digest) is None, 'TASK_REVOKED')


@contextmanager
def task_lock(task):
    path = task_control(task).with_suffix('.lock')
    require(path.resolve() == path, 'UNSAFE_PATH', str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    # Kernel locks are released when a process exits, including a killed process.
    with path.open('a+b') as stream:
        if os.name == 'nt':
            import msvcrt
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b'\0')
                stream.flush()
            def lock():
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            def unlock():
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            def lock():
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            def unlock():
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        deadline = time.monotonic() + 30
        while True:
            try:
                lock()
                break
            except OSError:
                require(time.monotonic() < deadline, 'TASK_BUSY')
                time.sleep(0.05)
        try:
            yield
        finally:
            unlock()


def project(root, task, clone=False):
    if not clone:
        require(common_dir(root) == task['common_dir'], 'WRONG_COMMON_DIRECTORY')
    identity = read_json(root / IDENTITY, 'WRONG_PROJECT')
    expected = dict(project_id=task['project_id'], genesis=task['genesis'])
    require(identity == expected, 'WRONG_PROJECT')
    # Check history at the baseline separately: an orphan with copied identity
    # must still fail the candidate ancestry check, not become a new project.
    require(genesis(root, task['baseline']) == task['genesis'], 'WRONG_PROJECT')
    for ref in (task['baseline'], 'HEAD'):
        p = git(root, 'show', f'{ref}:{IDENTITY}', check=False)
        try:
            stored = json.loads(p.stdout)
        except ValueError:
            stored = None
        require(p.returncode == 0 and stored == expected, 'WRONG_PROJECT')


def target(root, task):
    return gout(root, 'rev-parse', 'refs/heads/' + task['target_branch'])


def validate(root, task, candidate, clone=False, delivered=False, task_digest=None):
    require(isinstance(candidate, str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', candidate),
            'CANDIDATE_MISMATCH', 'Use a full commit SHA')
    project(root, task, clone)
    if task_digest is not None:
        assert_not_revoked(root, task, task_digest)
    require(head(root) == candidate, 'CANDIDATE_MISMATCH')
    require(not dirty(root), 'DIRTY_WORKTREE')
    require(git(root, 'merge-base', '--is-ancestor', task['baseline'], candidate,
                check=False).returncode == 0, 'NON_FAST_FORWARD')
    require(genesis(root, candidate) == task['genesis'], 'WRONG_PROJECT')
    if common_dir(root) == task['common_dir']:
        allowed = {task['baseline'], candidate} if delivered else {task['baseline']}
        require(target(root, task) in allowed, 'STALE_BASELINE')
    # --no-renames represents a rename as deletion+addition, including both paths.
    paths = git(root, 'diff', '--name-only', '--no-renames', '-z', task['baseline'], candidate).stdout.split('\0')
    changed = set(filter(None, paths))
    for name in changed:
        safe_path(name)
        require(name in task['scope'], 'OUTSIDE_SCOPE', name)
        require((root / name).resolve().is_relative_to(root), 'UNSAFE_PATH', name)
    for ref in (task['baseline'], candidate):
        for entry in git(root, 'ls-tree', '-r', '-z', ref).stdout.split('\0'):
            if entry:
                metadata, name = entry.split('\t', 1)
                if name in changed:
                    require(metadata.split()[0] in ('100644', '100755'), 'UNSAFE_PATH', name)
    return sorted(changed)


def init(root):
    require(not dirty(root), 'DIRTY_WORKTREE')
    if (root / IDENTITY).exists():
        identity = read_json(root / IDENTITY)
        require(set(identity) == {'project_id', 'genesis'}, 'WRONG_PROJECT')
        try:
            uuid.UUID(identity['project_id'])
        except (ValueError, TypeError, AttributeError) as exc:
            raise Denied('WRONG_PROJECT') from exc
        require(identity['genesis'] == genesis(root, 'HEAD'), 'WRONG_PROJECT')
        require(gout(root, 'ls-files', '--', IDENTITY) == IDENTITY, 'WRONG_PROJECT')
        return dict(project_id=identity['project_id'], baseline=head(root))
    commit_args = ('-c', 'user.name=Codex Pilot', '-c', 'user.email=codex-pilot@example.invalid')
    if git(root, 'rev-parse', '--verify', 'HEAD', check=False).returncode:
        git(root, *commit_args, 'commit', '--allow-empty', '-m', 'Bootstrap project genesis')
    identity = dict(project_id=str(uuid.uuid4()), genesis=genesis(root, 'HEAD'))
    write_json(root / IDENTITY, identity)
    git(root, 'add', '--', IDENTITY)
    git(root, *commit_args, 'commit', '-m', 'Initialize Codex-only project identity', '--', IDENTITY)
    return dict(project_id=identity['project_id'], baseline=head(root))


def authorize(root, args):
    path = external(args.task, root)
    require(not path.exists(), 'OUTPUT_EXISTS', str(path))
    require(not dirty(root), 'DIRTY_WORKTREE')
    branch = git(root, 'symbolic-ref', '--quiet', 'HEAD', check=False)
    branch_ref = branch.stdout.strip()
    require(branch.returncode == 0 and branch_ref.startswith('refs/heads/'), 'TARGET_BRANCH_REQUIRED')
    identity = read_json(root / IDENTITY, 'WRONG_PROJECT')
    require(identity.get('genesis') == genesis(root, 'HEAD'), 'WRONG_PROJECT')
    require(gout(root, 'ls-files', '--', IDENTITY) == IDENTITY, 'WRONG_PROJECT')
    scope = sorted(set(safe_path(p) for p in args.scope))
    try:
        argv = json.loads(args.test_command_json)
    except ValueError as exc:
        raise Denied('INVALID_TEST_COMMAND') from exc
    require(isinstance(argv, list) and argv and all(isinstance(x, str) and x and '\x00' not in x for x in argv),
            'INVALID_TEST_COMMAND')
    requirements = Path(args.requirements).read_text(encoding='utf-8')
    require(requirements.strip() and args.task_id.strip(), 'INVALID_REQUIREMENTS')
    completion = external(str(path) + '.completion.json', root)
    require(not completion.exists(), 'OUTPUT_EXISTS', str(completion))
    # Strip only the namespace: heads/main is itself a valid branch name.
    task = dict(**identity, baseline=head(root), target_branch=branch_ref.removeprefix('refs/heads/'),
                common_dir=common_dir(root), requirements=requirements,
                requirements_digest=hashlib.sha256(requirements.encode('utf-8')).hexdigest(),
                scope=scope, test_argv=argv, authority='user:authorize-cli',
                task_id=args.task_id, completion_path=str(completion))
    write_json(path, task)
    return dict(task=str(path), task_digest=digest(path), baseline=task['baseline'])


def bindings(task, task_digest, candidate):
    return dict(project_id=task['project_id'], task_digest=task_digest, candidate=candidate)


def test_candidate(root, task, task_digest, args):
    validate(root, task, args.candidate, clone=True, task_digest=task_digest)
    output = external(args.output, root)
    require(not output.exists(), 'OUTPUT_EXISTS', str(output))
    require(args.session.strip(), 'INVALID_SESSION')
    argv = [item.replace('{root}', str(root)) for item in task['test_argv']]
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    started = datetime.now(timezone.utc).isoformat()
    try:
        run = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                             encoding='utf-8', errors='replace')
        exit_code, stdout, stderr = run.returncode, run.stdout, run.stderr
    except OSError as exc:
        exit_code, stdout, stderr = 127, '', str(exc)
    validation_error = None
    try:
        validate(root, task, args.candidate, clone=True, task_digest=task_digest)
    except Denied as exc:
        validation_error = exc.code
    evidence = dict(**bindings(task, task_digest, args.candidate), session=args.session,
                    argv=argv, cwd=str(root), started_at=started,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    exit_code=exit_code, stdout=stdout, stderr=stderr,
                    worktree_unchanged=validation_error is None, validation_error=validation_error)
    write_json(output, evidence)
    require(validation_error is None, 'TEST_WORKTREE_CHANGED', validation_error or '')
    require(exit_code == 0, 'TEST_FAILED', str(output))
    return dict(evidence=str(output), **bindings(task, task_digest, args.candidate))


def verify_evidence(path, root, task, task_digest, candidate):
    evidence = read_json(external(path, root), 'EVIDENCE_MISSING')
    require(all(evidence.get(k) == v for k, v in bindings(task, task_digest, candidate).items()),
            'EVIDENCE_BINDING_MISMATCH')
    require(evidence.get('cwd') == str(root) and
            evidence.get('argv') == [s.replace('{root}', str(root)) for s in task['test_argv']] and
            isinstance(evidence.get('session'), str) and evidence['session'].strip(),
            'EVIDENCE_BINDING_MISMATCH')
    require(type(evidence.get('exit_code')) is int and evidence['exit_code'] == 0 and
            evidence.get('worktree_unchanged') is True, 'TEST_FAILED')
    return evidence


def gate(root, task, task_digest, args, delivered=False):
    validate(root, task, args.candidate, delivered=delivered, task_digest=task_digest)
    implementer = verify_evidence(args.test_evidence, root, task, task_digest, args.candidate)
    review = read_json(external(args.review, root), 'REVIEW_MISSING')
    require(all(review.get(k) == v for k, v in bindings(task, task_digest, args.candidate).items()),
            'REVIEW_BINDING_MISMATCH')
    require(review.get('verdict') == 'PASS' and review.get('findings') == [], 'REVIEW_FAILED')
    session = review.get('reviewer_session')
    require(isinstance(session, str) and session.strip(), 'REVIEW_BINDING_MISMATCH')
    require(session != implementer['session'], 'SELF_REVIEW')
    require(isinstance(review.get('reviewer_worktree'), str) and isinstance(review.get('test_evidence'), str),
            'REVIEW_BINDING_MISMATCH')
    try:
        reviewer = root_path(review['reviewer_worktree'])
        require(reviewer != root, 'REVIEWER_CHANGED')
        validate(reviewer, task, args.candidate, clone=True, delivered=delivered)
    except Denied as exc:
        raise Denied('REVIEWER_CHANGED', exc.code) from exc
    independent = verify_evidence(review['test_evidence'], reviewer, task, task_digest, args.candidate)
    require(independent['session'] == session, 'REVIEW_BINDING_MISMATCH')
    return dict(review=str(Path(args.review).resolve()), review_digest=digest(args.review),
                tests=[dict(path=str(Path(args.test_evidence).resolve()), digest=digest(args.test_evidence)),
                       dict(path=str(Path(review['test_evidence']).resolve()), digest=digest(review['test_evidence']))])


def completion_matches(record, task, task_digest, candidate):
    return (all(record.get(k) == v for k, v in bindings(task, task_digest, candidate).items()) and
            record.get('state') == 'DELIVERED')


def delivery_marker(root, task, task_digest, candidate):
    log = git(root, 'reflog', 'show', '-1', '--format=%H%x00%gs',
              'refs/heads/' + task['target_branch'], check=False).stdout.strip()
    return log.startswith(f'{candidate}\0codex-only deliver {task_digest} {candidate}: ')


def deliver(root, task, task_digest, args):
    project(root, task)
    with task_lock(task):
        assert_not_revoked(root, task, task_digest)
        return deliver_locked(root, task, task_digest, args)


def deliver_locked(root, task, task_digest, args):
    source = root_path(args.source_root)
    completion = external(task['completion_path'], root)
    previous = read_json(completion) if completion.exists() else None
    retry = (completion_matches(previous, task, task_digest, args.candidate) if previous else
             delivery_marker(source, task, task_digest, args.candidate))
    receipt = gate(source, task, task_digest, args, delivered=retry)
    project(root, task)
    require(not dirty(root), 'DIRTY_WORKTREE')
    branch = gout(root, 'symbolic-ref', '--quiet', 'HEAD')
    require(branch == 'refs/heads/' + task['target_branch'], 'WRONG_TARGET_BRANCH')
    current = head(root)
    require(current in (task['baseline'], args.candidate), 'STALE_BASELINE')
    if previous is not None:
        require(completion_matches(previous, task, task_digest, args.candidate) and
                current == args.candidate and all(previous.get(k) == v for k, v in receipt.items()),
                'COMPLETION_MISMATCH')
        return previous
    if current != args.candidate:
        # Marker lives in Git's normal reflog, enabling read-only crash diagnosis.
        action = f'codex-only deliver {task_digest} {args.candidate}'
        git(root, '-c', 'core.logAllRefUpdates=true', 'merge', '--ff-only', '--no-edit', args.candidate,
            env={'GIT_REFLOG_ACTION': action})
    require(head(root) == args.candidate and not dirty(root), 'DELIVERY_CHANGED')
    # Recheck candidate/reviewer after the merge before reporting completion.
    require(gate(source, task, task_digest, args, delivered=True) == receipt, 'REVIEW_CHANGED')
    record = dict(state='DELIVERED', **bindings(task, task_digest, args.candidate), **receipt)
    write_json(completion, record, replace=True)
    return record


def revoke(root, task, task_digest):
    project(root, task)
    with task_lock(task):
        current = target(root, task)
        completion = external(task['completion_path'], root)
        if completion.exists():
            completed = read_json(completion)
            require(completion_matches(completed, task, task_digest, completed.get('candidate')),
                    'COMPLETION_MISMATCH')
            raise Denied('ALREADY_DELIVERED', 'Completion proof is preserved; revoke does not undo Git')
        require(not delivery_marker(root, task, task_digest, current), 'ALREADY_DELIVERED')
        previous = revocation(task, task_digest)
        if previous:
            return dict(state='REVOKED', revocation=previous['path'], task_digest=task_digest)
        require(current == task['baseline'], 'STALE_BASELINE')
        path = task_control(task).with_suffix('.json')
        record = dict(state='REVOKED', project_id=task['project_id'], genesis=task['genesis'],
                      task_id=task['task_id'], task_digest=task_digest,
                      baseline=task['baseline'], target_branch=task['target_branch'],
                      common_dir=task['common_dir'], completion_path=task['completion_path'],
                      revoked_at=datetime.now(timezone.utc).isoformat())
        # Atomic replace + fsync publishes the negative fact before lock release/success.
        write_json(path, record, replace=True)
        return dict(state='REVOKED', revocation=str(path), task_digest=task_digest)


def recover(root, task, task_digest):
    project(root, task)
    current = target(root, task)
    completion = external(task['completion_path'], root)
    result = dict(state='ACTIVE', target_head=current, worktree_head=head(root),
                  baseline=task['baseline'], completion_missing=not completion.exists())
    if dirty(root):
        result['state'] = 'DIRTY'
    elif git(root, 'merge-base', '--is-ancestor', task['baseline'], head(root), check=False).returncode:
        result['state'] = 'STALE'
    elif completion.exists():
        record = read_json(completion)
        result['state'] = 'DELIVERED' if completion_matches(record, task, task_digest, current) else 'STALE'
    elif current != task['baseline']:
        result['state'] = 'DELIVERED' if delivery_marker(root, task, task_digest, current) else 'STALE'
    revoked = revocation(task, task_digest)
    if revoked:
        require(result['state'] != 'DELIVERED', 'REVOCATION_CONFLICT')
        result.update(state='REVOKED', worktree_state=result['state'], revocation=revoked['path'])
    return result


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Denied('INVALID_ARGUMENTS', message)


def main(argv=None):
    parser = Parser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'authorize', 'check', 'test', 'gate', 'deliver', 'recover', 'revoke'):
        command = sub.add_parser(name)
        command.add_argument('--root', required=True)
        if name != 'init':
            command.add_argument('--task', required=True)
        if name in ('check', 'test', 'gate', 'deliver'):
            command.add_argument('--candidate', required=True)
        if name in ('gate', 'deliver'):
            command.add_argument('--test-evidence', required=True)
            command.add_argument('--review', required=True)
        if name == 'deliver':
            command.add_argument('--source-root', required=True)
        if name == 'test':
            command.add_argument('--session', required=True)
            command.add_argument('--output', required=True)
        if name == 'authorize':
            command.add_argument('--requirements', required=True)
            command.add_argument('--scope', action='append', required=True)
            command.add_argument('--test-command-json', required=True)
            command.add_argument('--task-id', required=True)
    try:
        args = parser.parse_args(argv)
        root = root_path(args.root)
        if args.command == 'init':
            result = init(root)
        elif args.command == 'authorize':
            result = authorize(root, args)
        else:
            task, task_digest = load_task(args.task, root, allow_revoked=args.command in ('recover', 'revoke'))
            if args.command == 'check':
                result = dict(changed_paths=validate(root, task, args.candidate, task_digest=task_digest))
            elif args.command == 'test':
                result = test_candidate(root, task, task_digest, args)
            elif args.command == 'gate':
                result = gate(root, task, task_digest, args)
            elif args.command == 'deliver':
                result = deliver(root, task, task_digest, args)
            elif args.command == 'revoke':
                result = revoke(root, task, task_digest)
            else:
                result = recover(root, task, task_digest)
        print(json.dumps(dict(ok=True, **result), ensure_ascii=False))
        return 0
    except Denied as exc:
        print(json.dumps(dict(ok=False, error=exc.code, detail=exc.detail), ensure_ascii=False))
        return 1
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps(dict(ok=False, error='INVALID_INPUT', detail=str(exc)), ensure_ascii=False))
        return 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
