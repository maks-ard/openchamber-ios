"""Package a device build for local re-signing, without paid-account extensions."""
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

app = Path(sys.argv[1])
with (app / 'Info.plist').open('rb') as stream:
    info = plistlib.load(stream)
if info.get('CFBundleSupportedPlatforms') != ['iPhoneOS']:
    raise RuntimeError('Expected an iPhone device build, not a simulator app')
if info['CFBundleIdentifier'] != 'com.openchamber.app':
    raise RuntimeError('Upstream changed the bundle identifier; review before publishing')
if info['CFBundleShortVersionString'] != os.environ['APP_VERSION']:
    raise RuntimeError('Unexpected application version')
binary = app / info['CFBundleExecutable']
arches = subprocess.check_output(['lipo', '-archs', str(binary)], text=True).split()
if 'arm64' not in arches:
    raise RuntimeError('Missing arm64 device executable')

output = Path('dist')
payload = output / 'Payload'
payload.mkdir()
target = payload / app.name
shutil.copytree(app, target, symlinks=True)
# A free Apple account cannot provide upstream APNs/App Group capabilities.
# Exclude widget/notification extensions to avoid extra App IDs and entitlements.
shutil.rmtree(target / 'PlugIns', ignore_errors=True)
for signature in list(target.rglob('_CodeSignature')):
    shutil.rmtree(signature)
for profile in target.rglob('embedded.mobileprovision'):
    profile.unlink()
filename = os.environ['IPA_FILENAME']
subprocess.run(['ditto', '-c', '-k', '--keepParent', str(payload), str(output / filename)], check=True)
shutil.rmtree(payload)
digest = hashlib.sha256((output / filename).read_bytes()).hexdigest()
(output / 'SHA256SUMS').write_text(f'{digest}  {filename}\n')
metadata = {
    'upstream': 'openchamber/openchamber', 'tag': os.environ['UPSTREAM_TAG'],
    'commit': os.environ['UPSTREAM_SHA'], 'version': info['CFBundleShortVersionString'],
    'bundleIdentifier': info['CFBundleIdentifier'], 'minimumOSVersion': info['MinimumOSVersion'],
    'architectures': arches, 'sha256': digest, 'signed': False,
    'excluded': ['widgets', 'notification service extension', 'APNs/App Group entitlements'],
    'workflowRun': f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
}
(output / 'build-info.json').write_text(json.dumps(metadata, indent=2) + '\n')
shutil.copy('upstream/LICENSE', output / 'UPSTREAM-LICENSE.txt')
print(json.dumps(metadata, indent=2))
