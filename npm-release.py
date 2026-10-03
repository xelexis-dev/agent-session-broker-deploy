"""Validate the public release bundle without extracting or executing its files."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

REPOSITORY = 'https://github.com/xelexis-dev/agent-session-broker-deploy'
PACKAGE = '@xelexis/x-broker'
SLOTS = {'darwin-arm64': 'darwin-arm64', 'darwin-x64': 'darwin-amd64',
         'linux-x64': 'linux-amd64', 'win32-x64': 'windows-amd64.exe'}
MAX_FILE = 256 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_tuple(version):
    require(isinstance(version, str) and re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version),
            'Expected a stable x.y.z version')
    return tuple(map(int, version.split('.')))


def asset_names(version):
    version_tuple(version)
    return {f'asb-{component}-{version}-{asset}' for component in ('client', 'server') for asset in SLOTS.values()} | {
        f'xelexis-x-broker-{version}.tgz'}


def validate_release(release, version):
    names = asset_names(version)
    require(release.get('tag_name') == version and release.get('name') == 'ASB ' + version
            and release.get('draft') is False and release.get('prerelease') is False,
            'Expected the published stable release for this version')
    body = release.get('body', '')
    require(isinstance(body, str), 'Missing release checksums')
    records = re.findall(r'^([0-9a-f]{64})  ([^\r\n]+)$', body, re.M)
    hashes = {name: digest for digest, name in records}
    require(len(records) == 9 and set(hashes) == names, 'Expected nine unique release checksums')
    assets = release.get('assets', [])
    require(isinstance(assets, list) and len(assets) == 9, 'Expected nine release assets')
    seen = set()
    for asset in assets:
        name = asset.get('name')
        require(name in names and name not in seen and asset.get('state') == 'uploaded'
                and type(asset.get('size')) is int and 0 < asset['size'] <= MAX_FILE
                and asset.get('digest') == 'sha256:' + hashes[name], 'Release asset differs from its checksum')
        seen.add(name)
    return hashes


def strict_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'Duplicate JSON key')
        value[key] = item
    return value


def verify_bundle(tarball, version, hashes):
    expected_assets = asset_names(version)
    require(set(hashes) == expected_assets and all(re.fullmatch(r'[0-9a-f]{64}', h) for h in hashes.values()),
            'Invalid release checksums')
    tarball = Path(tarball)
    require(tarball.name == f'xelexis-x-broker-{version}.tgz' and not tarball.is_symlink()
            and tarball.is_file() and 0 < tarball.stat().st_size <= MAX_FILE, 'Unsafe bundle')
    data = tarball.read_bytes()
    require(hashlib.sha256(data).hexdigest() == hashes[tarball.name], 'Bundle checksum mismatch')
    binaries = {f'package/bin/{slot}/' + ('asb-client.exe' if slot == 'win32-x64' else 'asb-client'):
                f'asb-client-{version}-{asset}' for slot, asset in SLOTS.items()}
    names = set(binaries) | {'package/package.json', 'package/README.md', 'package/bin/x-broker.js'}
    files = {}
    with tarfile.open(tarball, 'r:gz') as archive:
        for entry in archive:
            require(entry.name in names and entry.name not in files and entry.isreg()
                    and not entry.linkname and 0 < entry.size <= MAX_FILE, 'Unexpected bundle entry')
            mode = 0o755 if entry.name.startswith('package/bin/') else 0o644
            require(entry.mode == mode, 'Unexpected bundle file mode')
            content = archive.extractfile(entry).read(MAX_FILE + 1)
            require(len(content) == entry.size, 'Incomplete bundle file')
            files[entry.name] = content
    require(set(files) == names, 'Bundle must contain exactly seven regular files')
    for name, asset in binaries.items():
        require(hashlib.sha256(files[name]).hexdigest() == hashes[asset], 'Bundled client checksum mismatch')
    manifest = json.loads(files['package/package.json'], object_pairs_hook=strict_object)
    keys = {'name', 'version', 'description', 'bin', 'files', 'engines', 'repository', 'homepage', 'bugs'}
    paths = {n.removeprefix('package/') for n in names if n.startswith('package/bin/')}
    require(isinstance(manifest, dict) and set(manifest) == keys, 'Unexpected package manifest fields')
    require(manifest['name'] == PACKAGE and manifest['version'] == version
            and manifest['description'] == 'npx launcher and bundled clients for the Agent Session Broker MCP client (asb-client)'
            and manifest['bin'] == {'x-broker': 'bin/x-broker.js'}
            and manifest['engines'] == {'node': '>=18'}
            and isinstance(manifest['files'], list) and len(manifest['files']) == len(paths)
            and set(manifest['files']) == paths
            and manifest['repository'] == {'type': 'git', 'url': 'git+' + REPOSITORY + '.git'}
            and manifest['homepage'] == REPOSITORY + '#readme'
            and manifest['bugs'] == {'url': REPOSITORY + '#readme'}, 'Package identity or public metadata mismatch')
    return manifest


def npm_view(spec, field, runner):
    result = runner(['npm', 'view', spec, field, '--json', '--registry=https://registry.npmjs.org'],
                    text=True, capture_output=True, timeout=60, check=False)
    try:
        answer = json.loads(result.stdout, object_pairs_hook=strict_object)
    except (ValueError, TypeError):
        raise ValueError('Invalid registry response') from None
    if result.returncode != 0:
        require(isinstance(answer, dict) and isinstance(answer.get('error'), dict)
                and answer['error'].get('code') == 'E404', 'Registry lookup failed')
        return None
    require(answer is not None, 'Empty registry response')
    return answer


def publication_state(tarball, version, runner=subprocess.run):
    current = version_tuple(version)
    integrity = 'sha512-' + base64.b64encode(hashlib.sha512(Path(tarball).read_bytes()).digest()).decode('ascii')
    existing = npm_view(PACKAGE + '@' + version, 'dist.integrity', runner)
    if existing is not None:
        require(existing == integrity, 'This version already has different content')
        return {'action': 'skip'}
    tags = npm_view(PACKAGE, 'dist-tags', runner)
    require(tags is None or isinstance(tags, dict), 'Invalid registry dist-tags')
    tag = 'latest'
    if tags and 'latest' in tags and version_tuple(tags['latest']) > current:
        tag = 'release-' + version
    return {'action': 'publish', 'tag': tag}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'state'))
    parser.add_argument('--version', required=True)
    parser.add_argument('--tarball', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata = json.loads(args.release.read_text(), object_pairs_hook=strict_object)
        hashes = validate_release(metadata, args.version)
        verify_bundle(args.tarball, args.version, hashes)
        result = publication_state(args.tarball, args.version) if args.command == 'state' else {'verified': True}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, OSError, tarfile.TarError, subprocess.SubprocessError):
        # Registry bodies, environment values and package contents are never logged.
        print('Release validation or registry check failed; publication stopped.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
