"""Stage2 regressions replay real accepted authority, with only the network doubled."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.gpt-codex/scripts'))


class IncrementalAuthorityTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory) / 'project'
        subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--shared', '--quiet', str(ROOT), str(root)], check=True)
        subprocess.run(['git', '-C', str(root), 'config', 'core.autocrlf', 'false'], check=True)
        subprocess.run(['git', '-C', str(root), 'checkout', '--quiet', 'f656fc88aff864626df5cb1ada68e1b16bf1daa4'], check=True)
        unit_path = '.gpt-codex/work-units/issue17-stage2-authority-reuse-001.json'
        # Use the accepted immutable WU, even after this source WU is explicitly closed.
        scope = json.loads((ROOT / '.gpt-codex/evidence/STAGE2-FRAMEWORK-SCOPE.json').read_text(encoding='utf-8'))
        current_unit = json.loads((ROOT / unit_path).read_text(encoding='utf-8'))
        pre = json.loads((ROOT / '.gpt-codex/evidence/results/RESULT-STAGE2-FRAMEWORK-PRE.json').read_bytes())
        request_path = f".gpt-codex/evidence/instructions/{pre['response_to_instruction_id']}.json"
        request = json.loads((ROOT / request_path).read_bytes())
        instruction_path = f".gpt-codex/evidence/instructions/{request['in_response_to_instruction_id']}.json"
        execution = json.loads((ROOT / instruction_path).read_bytes())
        self.assertEqual(execution['target_work_unit'], current_unit['work_unit_id'])
        ref = execution['target_work_unit_ref']
        unit_bytes = subprocess.check_output(['git', '-C', str(ROOT), 'show', f"{ref['sha']}:{ref['path']}"])
        paths = [scope_path for scope_path in scope['scope'] if scope_path.startswith('.gpt-codex/evidence/instructions/')]
        paths += ['.gpt-codex/evidence/STAGE2-FRAMEWORK-SCOPE.json', '.gpt-codex/evidence/results/RESULT-STAGE2-FRAMEWORK-PRE.json']
        for relative in paths:
            target = root / relative; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
        (root / unit_path).write_bytes(unit_bytes)
        subprocess.run(['git', '-C', str(root), 'remote', 'set-url', 'origin', 'https://github.com/xqc2098948451-byte/gpt-codex-framework.git'], check=True)
        blob = subprocess.check_output(['git', '-C', str(root), 'hash-object', '--stdin'], input=(root / instruction_path).read_bytes(), text=False).decode().strip()
        # The real immutable execution Instruction is retained in source history.
        commit = subprocess.check_output(['git', '-C', str(ROOT), 'log', '--format=%H', '--', instruction_path], text=True).splitlines()[-1]
        locator = {'repository': 'xqc2098948451-byte/gpt-codex-framework', 'commit_sha': commit, 'path': instruction_path, 'blob_sha': blob}
        return root, execution, locator, request_path, paths[-1]

    def test_snapshot_reuses_native_context_then_rejects_changed_durable_bytes(self):
        from continuity_resume import capture_authority_snapshot, reuse_authority_snapshot
        with tempfile.TemporaryDirectory() as directory:
            root, instruction, _, _, _ = self.fixture(directory)
            snapshot = capture_authority_snapshot(root, '1366213495', scope_paths=instruction['scope_paths'])
            resumed = reuse_authority_snapshot(root, '1366213495', snapshot, scope_paths=instruction['scope_paths'])
            self.assertEqual(resumed['state']['revision'], 44)
            self.assertTrue(resumed['remote_reverification_required'])
            state_path = root / '.gpt-codex/STATE.json'
            state = json.loads(state_path.read_text(encoding='utf-8')); state['revision'] = 45
            state_path.write_text(json.dumps(state), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'STALE_AUTHORITY'):
                reuse_authority_snapshot(root, '1366213495', snapshot, scope_paths=instruction['scope_paths'])
            with self.assertRaisesRegex(ValueError, 'STALE_AUTHORITY'):
                reuse_authority_snapshot(root, '1366213495', {'authority': 'DERIVED'}, scope_paths=instruction['scope_paths'])

    def test_real_pre_attestation_reuse_keeps_remote_check_and_rejects_scope_drift(self):
        from validate_project import validate_incremental_governed_entry
        with tempfile.TemporaryDirectory() as directory:
            root, instruction, locator, request, pre = self.fixture(directory)
            args = dict(instruction_locator=locator, review_request_path=request, review_result_path=pre)
            observed = {'repository_id': '1366213495', 'repository': locator['repository'], 'remote_ref': 'refs/heads/main',
                        'remote_head_sha': instruction['expected_remote_head_sha'], 'evidence_type': 'TOOL_OBSERVED'}
            with patch('git_continuity.observe_bound_remote', return_value=observed) as network:
                verified = validate_incremental_governed_entry(root, '1366213495', **args)
                self.assertEqual(verified['errors'], [])
                reused = validate_incremental_governed_entry(root, '1366213495', attestation=verified['attestation'], **args)
                self.assertTrue(reused['reused'])
                self.assertEqual(network.call_count, 2)
                drift = dict(args, review_result_path='.gpt-codex/evidence/results/RESULT-STAGE1-PRE.json')
                with self.assertRaisesRegex(ValueError, 'STALE_AUTHORITY'):
                    validate_incremental_governed_entry(root, '1366213495', attestation=verified['attestation'], **drift)
                changed = dict(observed, remote_head_sha='0' * 40)
                with patch('git_continuity.observe_bound_remote', return_value=changed):
                    with self.assertRaisesRegex(ValueError, 'REMOTE_HEAD_MISMATCH'):
                        validate_incremental_governed_entry(root, '1366213495', attestation=verified['attestation'], **args)


if __name__ == '__main__':
    unittest.main()
