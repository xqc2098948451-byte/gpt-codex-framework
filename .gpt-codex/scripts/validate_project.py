#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from kernel_rules import *
from context_binding import is_valid_project_context_id, required_guardrail_allows
from continuity_resume import load_resume_checkpoint
from publication_contract import validate_result_authority, validate_state_authority
from project_navigation import (
    load_module_map,
    load_project_map,
    validate_navigation_identity,
)

REQUIRED_CONTEXT_GUARDRAIL = 'cross-project-context-binding'
REQUIRED_REPOSITORY_GUARDRAIL = 'github-repository-binding'
FRAMEWORK_ROOT = HERE.parent.parent


def _cataloged_builtin(kind: str, extension_id: str) -> tuple[bool, str]:
    catalog_path = FRAMEWORK_ROOT / '.gpt-codex' / 'builtins' / 'INDEX.json'
    try:
        catalog = load(catalog_path)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f'Framework Built-in catalog unavailable: {exc}'
    bucket = None
    for candidate in ('required', 'optional'):
        if extension_id in (catalog.get(candidate) or {}).get(kind, []):
            bucket = candidate
            break
    if bucket is None:
        return False, f'Builtin {kind}/{extension_id} is not present in Framework catalog'
    manifest_path = FRAMEWORK_ROOT / '.gpt-codex' / 'builtins' / kind / extension_id / 'manifest.json'
    try:
        manifest = load(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f'Builtin {kind}/{extension_id} manifest unavailable: {exc}'
    expected_kind = {'skills': 'SKILL', 'guardrails': 'GUARDRAIL', 'fitness': 'FITNESS'}[kind]
    manifest_errors = check_common_version(manifest)
    if manifest.get('id') != extension_id:
        manifest_errors.append('manifest id mismatch')
    if manifest.get('kind') != expected_kind:
        manifest_errors.append(f'manifest kind must be {expected_kind}')
    if manifest.get('maturity') != 'BUILTIN':
        manifest_errors.append('manifest maturity must be BUILTIN')
    if manifest_errors:
        return False, f'Builtin {kind}/{extension_id} invalid: {", ".join(manifest_errors)}'
    return True, ''


def load(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def _matches_json_type(value, expected_type: str) -> bool:
    if expected_type == 'object':
        return isinstance(value, dict)
    if expected_type == 'array':
        return isinstance(value, list)
    if expected_type == 'string':
        return isinstance(value, str)
    if expected_type == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == 'boolean':
        return isinstance(value, bool)
    if expected_type == 'null':
        return value is None
    return True


def _schema_shape_errors(value, schema: dict, path: str = '$') -> list[str]:
    errors = []
    expected = schema.get('type')
    expected_types = expected if isinstance(expected, list) else [expected]
    if expected and not any(_matches_json_type(value, item) for item in expected_types):
        return [f'{path} must be {" or ".join(expected_types)}']
    if 'const' in schema and value != schema['const']:
        errors.append(f'{path} must equal {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path} must be one of {schema["enum"]!r}')
    if isinstance(value, str) and 'minLength' in schema and len(value) < schema['minLength']:
        errors.append(f'{path} must not be empty')
    if isinstance(value, dict):
        properties = schema.get('properties') or {}
        for required in schema.get('required') or []:
            if required not in value:
                errors.append(f'{path}.{required} is required')
        if schema.get('additionalProperties') is False:
            for key in value:
                if key not in properties:
                    errors.append(f'{path}.{key} is not allowed')
        for key, child_schema in properties.items():
            if key in value:
                errors += _schema_shape_errors(value[key], child_schema, f'{path}.{key}')
    if isinstance(value, list) and schema.get('items'):
        for index, item in enumerate(value):
            errors += _schema_shape_errors(item, schema['items'], f'{path}[{index}]')
    return errors


def _derived_schema_errors(payload: dict, schema_name: str) -> list[str]:
    schema_path = FRAMEWORK_ROOT / '.gpt-codex' / 'schemas' / f'{schema_name}.schema.json'
    try:
        schema = load(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f'{schema_name.upper().replace("-", "_")}_SCHEMA_UNAVAILABLE:{exc}']
    return [
        f'{schema_name.upper().replace("-", "_")}_SCHEMA_INVALID:{error}'
        for error in _schema_shape_errors(payload, schema)
    ]


def validate_optional_navigation_and_resume(root: Path, gov: Path, control: dict) -> list[str]:
    errors = []
    try:
        project_map = load_project_map(root)
    except ValueError as exc:
        errors.append(str(exc))
        project_map = None
    except TypeError:
        errors.append('NAVIGATION_INVALID_SHAPE')
        project_map = None
    if project_map is not None:
        errors += _derived_schema_errors(project_map, 'project-map')
        try:
            validate_navigation_identity(project_map, control)
        except ValueError as exc:
            errors.append(str(exc))
        for module in project_map.get('modules', []):
            if not isinstance(module, dict):
                errors.append('NAVIGATION_MODULE_INVALID')
                continue
            module_id = module.get('id')
            module_map_path = module.get('module_map')
            if not isinstance(module_map_path, str):
                errors.append('MODULE_MAP_PATH_INVALID')
                continue
            supplied_path = Path(module_map_path)
            if (
                supplied_path.is_absolute()
                or '..' in supplied_path.parts
                or supplied_path.suffix.lower() != '.json'
            ):
                errors.append(f'MODULE_MAP_PATH_INVALID:{module_map_path}')
                continue
            module_map_file = root / supplied_path
            if not module_map_file.exists():
                continue
            try:
                module_map = load_module_map(root, module_map_path)
                errors += _derived_schema_errors(module_map, 'module-map')
                validate_navigation_identity(module_map, control)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if module_map.get('module_id') != module_id:
                errors.append('MODULE_MAP_ID_MISMATCH')
    try:
        checkpoint = load_resume_checkpoint(gov)
    except ValueError as exc:
        errors.append(str(exc))
        checkpoint = None
    if checkpoint is not None:
        errors += _derived_schema_errors(checkpoint, 'resume')
        try:
            validate_navigation_identity(checkpoint, control)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def main():
    ap = argparse.ArgumentParser(description='Validate GPT-Codex v2 project governance mechanically.')
    ap.add_argument('project_root', type=Path)
    args = ap.parse_args()
    root = args.project_root.resolve()
    gov = root / '.gpt-codex'
    control_p = gov / 'CONTROL.json'
    state_p = gov / 'STATE.json'
    errors = []
    for p in (control_p, state_p):
        if not p.exists():
            errors.append(f'missing {p}')
    if errors:
        print('\n'.join('FAIL: '+e for e in errors)); return 1
    try:
        control, state = load(control_p), load(state_p)
    except Exception as e:
        print(f'FAIL: invalid JSON: {e}'); return 1
    errors += [f'CONTROL: {e}' for e in check_common_version(control)]
    errors += [f'STATE: {e}' for e in check_common_version(state)]
    if control.get('project_id') != state.get('project_id'):
        errors.append('project_id mismatch between CONTROL and STATE')
    if state.get('state') not in STATES:
        errors.append('invalid STATE.state')
    if not isinstance(state.get('revision'), int) or state.get('revision') < 0:
        errors.append('STATE.revision must be a non-negative integer')
    fw = control.get('framework') or {}
    if fw.get('evaluation_result') not in COMPAT_RESULTS:
        errors.append('invalid framework evaluation_result')
    management_project = control.get('framework_management_only') is True
    if control.get('governance_profile') not in GOVERNANCE_PROFILES and not (management_project and control.get('governance_profile') == 'FRAMEWORK_MANAGEMENT'):
        errors.append('invalid governance_profile')
    github = control.get('github')
    if github is not None:
        if not isinstance(github, dict) or set(github) != {'repository_id', 'repository_full_name', 'default_branch'}:
            errors.append('GITHUB_REPOSITORY_BINDING: exactly repository_id, repository_full_name, default_branch are required')
        elif not all(isinstance(github.get(key), str) and github.get(key).strip() for key in ('repository_id', 'repository_full_name', 'default_branch')):
            errors.append('GITHUB_REPOSITORY_BINDING: fields must be non-empty strings')
        repository_guardrails = [item for item in (control.get('extensions') or {}).get('guardrails', []) if item.get('id') == REQUIRED_REPOSITORY_GUARDRAIL]
        if len(repository_guardrails) != 1 or not repository_guardrails[0].get('enabled'):
            errors.append('GITHUB_REPOSITORY_BINDING: required profile Guardrail missing or disabled')
    continuity = state.get('continuity')
    if continuity is not None:
        required_continuity = {'current_remote_ref', 'latest_verified_remote_sha', 'latest_synced_state_revision', 'last_verified_result_ref', 'sync_status'}
        if not isinstance(continuity, dict) or not required_continuity.issubset(continuity):
            errors.append('STATE.continuity: incomplete continuity facts')
        elif continuity.get('sync_status') not in {'SYNCED', 'SYNC_PENDING', 'RECONCILIATION_REQUIRED'}:
            errors.append('STATE.continuity: invalid sync_status')
    project_context_id = control.get('project_context_id')
    if str(fw.get('adopted_version', '')).startswith('2.1.'):
        if not is_valid_project_context_id(project_context_id):
            errors.append('PROJECT_CONTEXT_BINDING: MIGRATION_REQUIRED (PROJECT_CONTEXT_ID_MISSING)')
        else:
            binding = required_guardrail_allows(control, 'project_validation')
            if binding.decision != 'ALLOW':
                errors.append(f'PROJECT_CONTEXT_BINDING: {binding.reason}')
    roots = control.get('roots') or {}
    roots_valid = (
        roots.get('project_role') == 'AUTHORITATIVE' and roots.get('framework_role') == 'ADVISORY'
    ) or (
        management_project and roots.get('project_role') == 'AUTHORITATIVE' and roots.get('framework_role') == 'SELF_MANAGED'
    )
    if not roots_valid:
        errors.append('dual-root authority must be project=AUTHORITATIVE/framework=ADVISORY')
    if roots.get('framework_kernel_access') != 'READ_ONLY' or roots.get('framework_builtins_access') != 'READ_ONLY':
        errors.append('framework Kernel/Built-ins must be READ_ONLY during ordinary project operation')
    ids = set()
    for kind in ('skills','guardrails','fitness'):
        for item in (control.get('extensions') or {}).get(kind, []):
            iid = item.get('id')
            if not iid:
                errors.append(f'{kind} contains extension without id')
            elif iid in ids:
                errors.append(f'duplicate extension id: {iid}')
            ids.add(iid)
            if item.get('enabled'):
                installed = item.get('installed_path')
                if not installed:
                    if not (management_project and item.get('source') == 'builtin'):
                        errors.append(f'{kind}/{iid}: enabled extension missing installed_path')
                    else:
                        valid_builtin, reason = _cataloged_builtin(kind, iid)
                        if not valid_builtin:
                            errors.append(f'{kind}/{iid}: {reason}')
                elif installed:
                    ip = root / installed
                    if not ip.exists():
                        errors.append(f'{kind}/{iid}: installed_path does not exist: {installed}')
                if item.get('source') == 'builtin' and installed:
                    valid_builtin, reason = _cataloged_builtin(kind, iid)
                    if not valid_builtin:
                        errors.append(f'{kind}/{iid}: {reason}')
    if state.get('state') == 'COMPLETE' and not state.get('evidence_refs'):
        errors.append('COMPLETE state requires durable evidence_refs')
    durable_results = {}
    for ref in set((state.get('evidence_refs') or []) + [((state.get('continuity') or {}).get('last_verified_result_ref'))]):
        if not ref:
            continue
        result_path = root / ref
        if not result_path.is_file():
            continue
        try:
            candidate = load(result_path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(candidate, dict) and 'status' in candidate:
            durable_results[ref] = candidate
            errors += [f'RESULT {ref}: {error}' for error in validate_result_authority(candidate)]
    errors += [f'STATE: {error}' for error in validate_state_authority(state, durable_results)]
    errors += validate_optional_navigation_and_resume(root, gov, control)
    # Validate project-local contracts if present.
    ext_root = gov / 'extensions'
    if ext_root.exists():
        for p in ext_root.rglob('*.json'):
            try: ext = load(p)
            except Exception as e:
                errors.append(f'{p}: invalid JSON: {e}'); continue
            errors += [f'{p}: {e}' for e in check_common_version(ext)]
            if ext.get('kind') not in EXTENSION_KINDS: errors.append(f'{p}: invalid kind')
            if ext.get('maturity') not in MATURITY: errors.append(f'{p}: invalid maturity')
            if not project_extension_has_provenance(ext): errors.append(f'{p}: project-local extension lacks required provenance/evidence/retirement')
    if errors:
        for e in errors: print('FAIL:', e)
        print(f'RESULT: FAIL ({len(errors)} errors)')
        return 1
    print('RESULT: PASS')
    print(f'PROJECT: {control.get("project_id")}')
    print(f'STATE: {state.get("state")}@revision-{state.get("revision")}')
    print('PROJECT_CONTEXT_BINDING: PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
