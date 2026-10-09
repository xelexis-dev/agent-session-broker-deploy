"""Validate the public release bundle without extracting or executing its files."""
import argparse
import base64
import hashlib
import json
import io
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import time
import urllib.request
import urllib.error

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
    keys = {'name', 'version', 'description', 'bin', 'files', 'engines', 'repository', 'homepage', 'bugs', 'xBrokerClientInputs'}
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
            and manifest['bugs'] == {'url': REPOSITORY + '#readme'}
            and valid_fingerprint(manifest['xBrokerClientInputs']), 'Package identity or public metadata mismatch')
    return manifest


def npm_view(spec, field, runner, timeout=60):
    result = runner(['npm', 'view', spec] + ([field] if field else []) + ['--json', '--registry=https://registry.npmjs.org'],
                    text=True, capture_output=True, timeout=timeout, check=False)
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


def valid_fingerprint(value):
    return isinstance(value, str) and re.fullmatch(r'sha256:[0-9a-f]{64}', value) is not None


def package_manifest(data):
    require(isinstance(data, bytes) and 0 < len(data) <= MAX_FILE, 'Invalid registry bundle')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        manifests = []
        count = 0
        for entry in archive:
            count += 1
            require(count <= 32, 'Too many registry bundle entries')
            if entry.name == 'package/package.json':
                require(entry.isreg() and not entry.linkname and 0 < entry.size <= 64000,
                        'Unsafe registry manifest')
                manifests.append(json.loads(archive.extractfile(entry).read(64001), object_pairs_hook=strict_object))
        require(len(manifests) == 1 and isinstance(manifests[0], dict), 'Missing or duplicate registry manifest')
        return manifests[0]


def fetch_registry_bundle(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        require(response.geturl() == url, 'Unexpected registry redirect')
        return response.read(MAX_FILE + 1)


def publication_state(tarball, version, runner=subprocess.run, fetcher=fetch_registry_bundle):
    current = version_tuple(version)
    data = Path(tarball).read_bytes()
    candidate = package_manifest(data)
    fingerprint = candidate.get('xBrokerClientInputs')
    require(candidate.get('name') == PACKAGE and candidate.get('version') == version
            and valid_fingerprint(fingerprint), 'Missing client input fingerprint')
    integrity = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode('ascii')
    existing = npm_view(PACKAGE + '@' + version, 'dist.integrity', runner)
    if existing is not None:
        require(existing == integrity, 'This version already has different content')
        return {'action': 'skip'}
    metadata = npm_view(PACKAGE, None, runner)
    if metadata is None:
        return {'action': 'publish', 'tag': 'latest'}
    require(isinstance(metadata, dict) and metadata.get('name') == PACKAGE, 'Invalid registry package')
    tags, versions = metadata.get('dist-tags'), metadata.get('versions')
    require(isinstance(tags, dict) and isinstance(versions, list), 'Invalid registry versions')
    latest = tags.get('latest')
    previous = version_tuple(latest)
    require(previous != current, 'Inconsistent registry version lookup')
    stable = [v for v in versions if isinstance(v, str) and re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', v)]
    require(stable and max(stable, key=version_tuple) == latest and metadata.get('version') == latest,
            'Registry latest is not the highest stable version')
    dist = metadata.get('dist')
    require(isinstance(dist, dict), 'Missing registry integrity')
    url = 'https://registry.npmjs.org/@xelexis/x-broker/-/x-broker-' + latest + '.tgz'
    require(dist.get('tarball') == url, 'Unexpected registry tarball URL')
    baseline = fetcher(url)
    require(isinstance(baseline, bytes) and 0 < len(baseline) <= MAX_FILE, 'Invalid registry bundle')
    expected = 'sha512-' + base64.b64encode(hashlib.sha512(baseline).digest()).decode('ascii')
    require(dist.get('integrity') == expected, 'Registry bundle integrity mismatch')
    published = package_manifest(baseline)
    require(published.get('name') == PACKAGE and published.get('version') == latest,
            'Registry bundle identity mismatch')
    old = published.get('xBrokerClientInputs')
    require(('xBrokerClientInputs' in published) == ('xBrokerClientInputs' in metadata)
            and old == metadata.get('xBrokerClientInputs'), 'Registry fingerprint mismatch')
    if 'xBrokerClientInputs' in published:
        require(valid_fingerprint(old), 'Invalid published client fingerprint')
        if old == fingerprint:
            return {'action': 'skip', 'reason': 'client-unchanged', 'clientVersion': latest}
    # Legacy packages without a fingerprint migrate once through a real publish.
    tag = 'latest' if previous < current else 'release-' + version
    return {'action': 'publish', 'tag': tag}


def wait_for_publication(tarball, version, runner=subprocess.run,
                         sleeper=time.sleep, clock=time.monotonic, timeout=600):
    """Read only the exact published version; E404 may lag a successful publish."""
    version_tuple(version)
    require(0 < timeout <= 600, 'Invalid propagation timeout')
    data = Path(tarball).read_bytes()
    candidate = package_manifest(data)
    require(candidate.get('name') == PACKAGE and candidate.get('version') == version
            and valid_fingerprint(candidate.get('xBrokerClientInputs')), 'Invalid package identity')
    integrity = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode('ascii')
    deadline = clock() + timeout
    interval = 2
    while True:
        remaining = deadline - clock()
        require(remaining > 0, 'Registry propagation timed out')
        existing = npm_view(PACKAGE + '@' + version, 'dist.integrity', runner,
                            timeout=min(60, remaining))
        if existing is not None:
            require(existing == integrity, 'This version already has different content')
            return {'action': 'skip'}
        remaining = deadline - clock()
        require(remaining > 0, 'Registry propagation timed out')
        sleeper(min(interval, remaining))
        interval = min(interval * 2, 30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'state', 'wait'))
    parser.add_argument('--version', required=True)
    parser.add_argument('--tarball', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata = json.loads(args.release.read_text(), object_pairs_hook=strict_object)
        hashes = validate_release(metadata, args.version)
        verify_bundle(args.tarball, args.version, hashes)
        if args.command == 'state':
            result = publication_state(args.tarball, args.version)
        elif args.command == 'wait':
            result = wait_for_publication(args.tarball, args.version)
        else:
            result = {'verified': True}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, OSError, tarfile.TarError, subprocess.SubprocessError):
        # Registry bodies, environment values and package contents are never logged.
        print('Release validation or registry check failed; publication stopped.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
