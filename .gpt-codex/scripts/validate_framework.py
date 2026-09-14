#!/usr/bin/env python3
from __future__ import annotations
import json, re, runpy, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from kernel_rules import *
from context_binding import is_valid_project_context_id, required_guardrail_allows

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def read_version(root: Path) -> str:
    value = (Path(root) / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(value):
        raise ValueError(f"VERSION must be SemVer, got: {value!r}")
    return value


def load(p):
    with Path(p).open('r', encoding='utf-8') as f: return json.load(f)


def _load_module_registry(root: Path, *, full_validation: bool) -> tuple[dict | None, list[str]]:
    registry_path = Path(root) / '.gpt-codex/framework-modules/REGISTRY.json'
    if not registry_path.exists():
        return None, []
    routing_path = Path(root) / '.gpt-codex/scripts/framework_module_routing.py'
    if not routing_path.exists():
        return None, ['MODULE_REGISTRY: MODULE_REGISTRY_INVALID']
    try:
        namespace = runpy.run_path(str(routing_path), run_name='framework_module_routing_management')
        loader = namespace.get('load_registry')
        if not callable(loader):
            return None, ['MODULE_REGISTRY: MODULE_REGISTRY_INVALID']
        registry = loader(Path(root))
        if full_validation:
            validator = namespace.get('validate_registry')
            if not callable(validator):
                return None, ['MODULE_REGISTRY: MODULE_REGISTRY_INVALID']
            codes = validator(Path(root))
            if codes:
                return registry, [f'MODULE_REGISTRY: {code}' for code in codes]
        return registry, []
    except Exception:
        return None, ['MODULE_REGISTRY: MODULE_REGISTRY_INVALID']


def validate_module_registry(root: Path, *, full_validation: bool = True) -> list[str]:
    _, errors = _load_module_registry(root, full_validation=full_validation)
    return errors


def validate_optional_framework_evolution_source(root: Path) -> list[str]:
    """Read and report the optional Framework-owned source; never create or repair it."""
    source_path = Path(root) / '.gpt-codex' / 'FRAMEWORK_EVOLUTION_SOURCE.json'
    if not source_path.exists():
        return []
    try:
        source = load(source_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return ['FRAMEWORK_SOURCE_INVALID']
    decision = validate_framework_evolution_source(source)
    return [] if decision.classification == 'READ_ONLY_EVOLUTION_SOURCE' else ['FRAMEWORK_SOURCE_INVALID']


def main():
    errors = []
    errors.extend(validate_optional_framework_evolution_source(ROOT))
    required_files = [
        ROOT/'AGENTS.md', ROOT/'.gpt-codex/KERNEL.md', ROOT/'.gpt-codex/README.md',
        ROOT/'.gpt-codex/builtins/INDEX.json', ROOT/'.gpt-codex/project-template/CONTROL.template.json',
        ROOT/'.gpt-codex/project-template/STATE.template.json', ROOT/'.gpt-codex/scripts/kernel_rules.py', ROOT/'VERSION',
        ROOT/'releases/INDEX.json', ROOT/'releases/README.md', ROOT/'.gpt-codex/scripts/release_archive.py'
        , ROOT/'.gpt-codex/schemas/instruction-envelope.schema.json'
        , ROOT/'.gpt-codex/project-template/INSTRUCTION_ENVELOPE.template.json'
        , ROOT/'.gpt-codex/MIGRATION_v2.0_to_v2.1.md'
        , ROOT/'.gpt-codex/MIGRATION_v2.1_to_v2.2.md'
        , ROOT/'.gpt-codex/schemas/control.schema.json'
        , ROOT/'.gpt-codex/schemas/state.schema.json'
        , ROOT/'.gpt-codex/schemas/result-envelope.schema.json'
        , ROOT/'.gpt-codex/scripts/github_repository_binding.py'
        , ROOT/'.gpt-codex/scripts/git_continuity.py'
        , ROOT/'.gpt-codex/scripts/continuity_resume.py'
        , ROOT/'.gpt-codex/builtins/guardrails/github-repository-binding/manifest.json'
        , ROOT/'.gpt-codex/builtins/guardrails/github-repository-binding/GUARDRAIL.md'
        , ROOT/'.gpt-codex/builtins/skills/github-project-continuity/manifest.json'
        , ROOT/'.gpt-codex/builtins/skills/github-project-continuity/SKILL.md'
        , ROOT/'.gpt-codex/builtins/guardrails/cross-project-context-binding/manifest.json'
        , ROOT/'.gpt-codex/builtins/guardrails/cross-project-context-binding/GUARDRAIL.md'
        , ROOT/'.gpt-codex/schemas/project-map.schema.json'
        , ROOT/'.gpt-codex/schemas/module-map.schema.json'
        , ROOT/'.gpt-codex/schemas/resume.schema.json'
        , ROOT/'.gpt-codex/project-template/navigation/PROJECT_MAP.template.json'
        , ROOT/'.gpt-codex/project-template/navigation/modules/MODULE_MAP.template.json'
        , ROOT/'.gpt-codex/project-template/continuity/RESUME.template.json'
    ]
    registry_path = ROOT/'.gpt-codex/framework-modules/REGISTRY.json'
    registry = None
    module_registry_errors = []
    if registry_path.exists():
        required_files.extend([
            registry_path,
            ROOT/'.gpt-codex/schemas/framework-module-registry.schema.json',
            ROOT/'.gpt-codex/schemas/framework-module.schema.json',
            ROOT/'.gpt-codex/scripts/framework_module_routing.py',
        ])
        module_test_suite = ROOT/'.gpt-codex/tests/test_framework_module_routing.py'
        registry, module_registry_errors = _load_module_registry(
            ROOT,
            full_validation=module_test_suite.exists(),
        )
        if not module_registry_errors:
            try:
                for entry in registry.get('modules', []):
                    if isinstance(entry, dict) and isinstance(entry.get('descriptor'), str):
                        required_files.append(ROOT / entry['descriptor'])
            except (AttributeError, TypeError):
                pass
    for p in required_files:
        if not p.exists(): errors.append(f'missing {p.relative_to(ROOT)}')
    errors.extend(module_registry_errors)
    if errors:
        for e in errors: print('FAIL:', e)
        return 1
    version = read_version(ROOT)
    index = load(ROOT/'.gpt-codex/builtins/INDEX.json')
    if index.get('framework_version') != version:
        errors.append(f"VERSION/catalog mismatch: VERSION={version}, catalog={index.get('framework_version')}")
    changelog = (ROOT/'.gpt-codex/CHANGELOG.md').read_text(encoding='utf-8')
    if f'## v{version}' not in changelog:
        errors.append(f'CHANGELOG missing current release heading: v{version}')
    release_index = load(ROOT/'releases/INDEX.json')
    if release_index.get('archive_policy') != 'METADATA_ONLY':
        errors.append('release archive policy must be METADATA_ONLY')
    current_record = ROOT/f'releases/records/v{version}.json'
    if not current_record.exists():
        errors.append(f'missing current release record: releases/records/v{version}.json')
    else:
        current_release = load(current_record)
        if current_release.get('archive_policy') != 'METADATA_ONLY':
            errors.append('current release record must use METADATA_ONLY archive policy')
        if current_release.get('kernel_version') != KERNEL_VERSION or current_release.get('schema_version') != SCHEMA_VERSION:
            errors.append('current release record Kernel/schema version mismatch')
    if any((ROOT/'releases').rglob('*.zip')):
        errors.append('release metadata archive must not embed ZIP binaries')
    seen = set()
    listed = []
    for bucket in ('required','optional'):
        for kind, ids in index[bucket].items():
            for iid in ids:
                listed.append((bucket,kind,iid))
    kind_paths = {'skills':'skills','guardrails':'guardrails','fitness':'fitness'}
    for bucket, kind, iid in listed:
        mp = ROOT/'.gpt-codex/builtins'/kind_paths[kind]/iid/'manifest.json'
        if not mp.exists(): errors.append(f'index references missing manifest: {kind}/{iid}'); continue
        m = load(mp)
        errors += [f'{kind}/{iid}: {e}' for e in check_common_version(m)]
        if m.get('id') != iid: errors.append(f'{kind}/{iid}: manifest id mismatch')
        expected_kind = {'skills':'SKILL','guardrails':'GUARDRAIL','fitness':'FITNESS'}[kind]
        if m.get('kind') != expected_kind: errors.append(f'{kind}/{iid}: kind mismatch')
        if m.get('maturity') != 'BUILTIN': errors.append(f'{kind}/{iid}: Built-in manifest maturity must be BUILTIN')
        if iid in seen: errors.append(f'duplicate Built-in id: {iid}')
        seen.add(iid)
        if bool(m.get('required_builtin')) != (bucket == 'required'):
            errors.append(f'{kind}/{iid}: required_builtin mismatch with catalog bucket')
    # Templates must parse and obey core rules.
    for name in ['CONTROL','STATE','WORK_UNIT','EXTENSION','EVIDENCE','RESULT_ENVELOPE','HARVEST_CANDIDATE']:
        p = ROOT/f'.gpt-codex/project-template/{name}.template.json'
        try: obj = load(p)
        except Exception as e: errors.append(f'{name} template invalid JSON: {e}'); continue
        errors += [f'{name}: {e}' for e in check_common_version(obj)]
    for filename, schema_id in [
        ('project-map.schema.json', 'gpt-codex/project-map-v1'),
        ('module-map.schema.json', 'gpt-codex/module-map-v1'),
        ('resume.schema.json', 'gpt-codex/resume-v1'),
    ]:
        try:
            schema = load(ROOT/'.gpt-codex/schemas'/filename)
        except Exception as e:
            errors.append(f'{filename} invalid JSON: {e}')
            continue
        if schema.get('$id') != schema_id:
            errors.append(f'{filename} schema id must be {schema_id}')
    # Framework-management-only project extension. It must not leak into Built-ins.
    release_manifest_path = ROOT/'.gpt-codex/extensions/skills/framework-release/manifest.json'
    if release_manifest_path.exists():
        release_manifest = load(release_manifest_path)
        errors += [f'framework-release: {e}' for e in check_common_version(release_manifest)]
        if release_manifest.get('kind') != 'SKILL' or release_manifest.get('maturity') != 'PROJECT_LOCAL':
            errors.append('framework-release must remain a PROJECT_LOCAL SKILL')
        if not project_extension_has_provenance(release_manifest):
            errors.append('framework-release requires admissible project-local provenance')
        if 'framework-release' in seen:
            errors.append('framework-release must not be listed as a Built-in')
    else:
        errors.append('missing project-local framework-release Skill manifest')

    hc = load(ROOT/'.gpt-codex/project-template/HARVEST_CANDIDATE.template.json')
    if not harvest_candidate_is_safe(hc): errors.append('Harvest candidate template violates source-authority/promotion invariant')
    c = load(ROOT/'.gpt-codex/project-template/CONTROL.template.json')
    if set(c.get('github', {})) != {'repository_id', 'repository_full_name', 'default_branch'}:
        errors.append('CONTROL template github binding must contain exactly three durable fields')
    if 'remote_name' in c.get('github', {}):
        errors.append('CONTROL template must not make remote_name project-global authority')
    if c.get('project_context_id') != 'GENERATE_DURING_BOOTSTRAP':
        errors.append('CONTROL template must require generated PROJECT_CONTEXT_ID')
    template_guardrails = (c.get('extensions') or {}).get('guardrails', [])
    matching_template_guardrails = [g for g in template_guardrails if g.get('id') == 'cross-project-context-binding']
    if len(matching_template_guardrails) != 1 or not matching_template_guardrails[0].get('enabled'):
        errors.append('CONTROL template must select cross-project-context-binding as enabled')
    roots = c.get('roots',{})
    if roots.get('project_role') != 'AUTHORITATIVE' or roots.get('framework_role') != 'ADVISORY': errors.append('CONTROL template violates dual-root authority')
    if roots.get('framework_kernel_access') != 'READ_ONLY' or roots.get('framework_builtins_access') != 'READ_ONLY': errors.append('CONTROL template framework core must be READ_ONLY')
    management_control_path = ROOT/'.gpt-codex/CONTROL.json'
    if not management_control_path.exists():
        errors.append('missing management .gpt-codex/CONTROL.json')
    else:
        management_control = load(management_control_path)
        management_id = management_control.get('project_context_id')
        if not management_control.get('framework_management_only'):
            errors.append('management CONTROL must be marked framework_management_only')
        if not is_valid_project_context_id(management_id):
            errors.append('management CONTROL must contain a valid PROJECT_CONTEXT_ID')
        binding = required_guardrail_allows(management_control, 'framework_validation')
        if binding.decision != 'ALLOW':
            errors.append(f'management CONTROL required guardrail invalid: {binding.reason}')
        leakage_roots = [
            ROOT/'AGENTS.md', ROOT/'.gpt-codex/README.md', ROOT/'.gpt-codex/BOOTSTRAP_PROMPT.md',
            ROOT/'.gpt-codex/MIGRATION_v2.0_to_v2.1.md', ROOT/'.gpt-codex/KERNEL.md',
            ROOT/'.gpt-codex/builtins', ROOT/'.gpt-codex/project-template', ROOT/'.gpt-codex/schemas',
            ROOT/'.gpt-codex/scripts'
        ]
        for scan_root in leakage_roots:
            paths = [scan_root] if scan_root.is_file() else scan_root.rglob('*')
            for path in paths:
                if path.is_file() and path.suffix.lower() in {'.md', '.json', '.py', '.txt'}:
                    if management_id and management_id in path.read_text(encoding='utf-8', errors='ignore'):
                        errors.append(f'management PROJECT_CONTEXT_ID leaked into {path.relative_to(ROOT)}')
        schema = load(ROOT/'.gpt-codex/schemas/result-envelope.schema.json')
        props = schema.get('properties') or {}
        for field in ('source_project_context_id', 'source_project_name', 'framework_version'):
            if field not in props:
                errors.append(f'Result Envelope schema missing {field}')
        if 'PROJECT_CONTEXT_ID_MISSING' not in (ROOT/'.gpt-codex/MIGRATION_v2.0_to_v2.1.md').read_text(encoding='utf-8'):
            errors.append('migration guide missing PROJECT_CONTEXT_ID_MISSING')
    # Required human phrases/principles.
    corpus = (ROOT/'AGENTS.md').read_text(encoding='utf-8') + (ROOT/'.gpt-codex/KERNEL.md').read_text(encoding='utf-8') + (ROOT/'.gpt-codex/README.md').read_text(encoding='utf-8')
    phrases = [
        '【执行策略】', '【完成后是否需要批准】', 'Preinstalled does not mean enabled',
        'Generalize after repetition, not before', 'Framework upgrades are evaluated, not propagated',
        'sufficient governance, not maximal governance', 'Consumer Workspace Setup',
        'Project is authoritative', 'Framework is advisory', 'Framework Kernel',
        'Framework Built-ins', 'READ ONLY', 'versioned snapshot', 'NO_ACTION',
        'OPTIONAL_REUSE', 'RECOMMENDED_UPGRADE', 'REQUIRED_MIGRATION', 'CONFLICT',
        'remove the old versioned', 'add the fixed', 'save the Codex project configuration'
    ]
    for x in phrases:
        if x.lower() not in corpus.lower(): errors.append(f'missing required principle/phrase: {x}')
    bootstrap_prompt = (ROOT/'.gpt-codex/BOOTSTRAP_PROMPT.md').read_text(encoding='utf-8')
    bootstrap_phrases = [
        'A context-window transition is not a project bootstrap.',
        'A maintenance request is not a repository rediscovery.',
        'Do not scan the repository when the Project Map can identify the candidate module.',
    ]
    for phrase in bootstrap_phrases:
        if phrase.lower() not in bootstrap_prompt.lower(): errors.append(f'missing required Bootstrap phrase: {phrase}')
    if errors:
        for e in errors: print('FAIL:', e)
        print(f'RESULT: FAIL ({len(errors)} errors)')
        return 1
    print('RESULT: PASS')
    print(f'BUILTINS: {len(seen)}')
    print('KERNEL_VERSION:', KERNEL_VERSION)
    print('CONTEXT_BINDING: PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
