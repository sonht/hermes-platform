#!/usr/bin/env python3
"""Read-only, no inference, no restart. Compare existing M1/M0 configuration.

Print only approved model/provider labels and credential presence/equality. Never
print credentials, hashes of credentials, raw config, stderr or full doctor output.
"""
import argparse
import json
import subprocess

PROBE = r'''
import json, os, pathlib, re, subprocess
import yaml

def label(value):
    return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9._:/@-]{1,100}', value) else None

def envfile(path):
    result = {}
    if not path.is_file():
        return result
    for line in path.read_text().splitlines():
        m = re.match(r'^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=\s*(.*)\s*$', line)
        if m:
            result[m[1]] = m[2].strip().strip('"\'')
    return result

def credentials(values):
    return {k: v for k, v in values.items() if re.fullmatch(r'[A-Z][A-Z0-9_]{1,80}', k)
            and re.search(r'(API_KEY|AUTH_TOKEN|ACCESS_TOKEN|SECRET_KEY)$', k)}

root = pathlib.Path('/opt/data')
sources = {'container_env': credentials(dict(os.environ)), 'global_env_file': credentials(envfile(root / '.env'))}
profiles = {}
for name, base in [('global_config', root)] + [(name, root / 'profiles' / name) for name in ('nmprp-mapping', 'nmprp-stages')]:
    cfg = {}
    if (base / 'config.yaml').is_file():
        try:
            cfg = yaml.safe_load((base / 'config.yaml').read_text()) or {}
        except Exception:
            cfg = {}
    model = cfg.get('model', {})
    model_dict = model if isinstance(model, dict) else {}
    provider = model_dict.get('provider', cfg.get('provider'))
    profiles[name] = {'exists': base.is_dir(), 'config_exists': (base / 'config.yaml').is_file(),
                      'env_exists': (base / '.env').is_file(),
                      'model': label(model_dict.get('default', model if isinstance(model, str) else '')),
                      'provider': label(provider),
                      'config_api_key_present': bool(model_dict.get('api_key') or cfg.get('api_key')),
                      'auth_files_present': [f for f in ('auth.json', '.auth.json') if (base / f).is_file()],
                      'workspace_writable': os.access(base / 'workspace', os.W_OK)}
    sources[name + '_env_file'] = credentials(envfile(base / '.env'))
    if model_dict.get('api_key') or cfg.get('api_key'):
        sources[name + '_config'] = {'CONFIG_API_KEY': model_dict.get('api_key') or cfg.get('api_key')}

help_result = subprocess.run(['hermes', '--help'], capture_output=True, text=True, timeout=20)
help_text = help_result.stdout + help_result.stderr
flags = {flag: flag in help_text for flag in ('--usage-file', '--reasoning', '--profile', '--skill', '--toolsets')}
version = subprocess.run(['hermes', '--version'], capture_output=True, text=True, timeout=20)
version_match = re.search(r'\b\d+\.\d+\.\d+\b', version.stdout + version.stderr)
present = {source: {key: bool(value) for key, value in values.items()} for source, values in sources.items()}
equal = []
names = list(sources)
for i, a in enumerate(names):
    for b in names[i+1:]:
        for key in sources[a].keys() & sources[b].keys():
            equal.append({'a': a, 'b': b, 'name': key, 'same_nonempty_value': bool(sources[a][key]) and sources[a][key] == sources[b][key]})
print(json.dumps({'profiles': profiles, 'credential_sources': present, 'credential_equality': equal,
                  'global_auth_files_present': [f for f in ('auth.json', '.auth.json') if (root / f).is_file()],
                  'runtime_version': version_match[0] if version_match else None, 'cli_flags': flags,
                  'container_timeout_available': subprocess.run(['sh', '-c', 'command -v timeout >/dev/null']).returncode == 0,
                  'note': 'Presence is not effective resolution or provider authorization. No model call was made.'}, ensure_ascii=False))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='hermes-platform-agent')
    args = parser.parse_args()
    try:
        p = subprocess.run(['docker', 'exec', '-i', '-u', 'hermes', args.container, 'python', '-'],
                           input=PROBE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if p.returncode:
            # This script can also be piped from git show before deploying code.
            print(json.dumps({'ok': False, 'exit_code': p.returncode, 'reason': 'PROFILE_PROBE_FAILED_NO_RAW_OUTPUT'}))
            return 1
        print(json.dumps(json.loads(p.stdout), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'ok': False, 'reason': type(exc).__name__}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
