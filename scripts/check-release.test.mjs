import test from 'node:test';
import assert from 'node:assert/strict';
import { checkRelease } from './check-release.mjs';

const tag = 'v2.7.2';
const sha = 'a'.repeat(40);
const complete = { assets: ['OpenChamber-v2.7.2-unsigned.ipa', 'SHA256SUMS', 'build-info.json'].map(name => ({name, state: 'uploaded'})) };
const api = (existing = null) => async path => path.includes('/commits/') ? {sha} : path.includes('/repos/me/') ? existing : { tag_name: tag };
test('new stable version builds the resolved commit', async () => {
  assert.deepEqual(await checkRelease(api(), 'me/ios'), {build:'true', tag, sha, version:'2.7.2', filename:'OpenChamber-v2.7.2-unsigned.ipa'});
});
test('complete published release skips macOS', async () => {
  assert.equal((await checkRelease(api(complete), 'me/ios')).build, 'false');
});
test('draft and partial releases are retried; force rebuilds', async () => {
  for (const existing of [{...complete, draft:true}, {assets:[]}, complete]) {
    assert.equal((await checkRelease(api(existing), 'me/ios', '', existing === complete)).build, 'true');
  }
});
test('network and permission failures propagate', async () => {
  await assert.rejects(checkRelease(async () => {throw new Error('HTTP 403');}, 'me/ios'), /403/);
});
test('refuses arbitrary refs and prereleases', async () => {
  await assert.rejects(checkRelease(api(), 'me/ios', 'main'));
  await assert.rejects(checkRelease(async () => ({tag_name:tag, prerelease:true}), 'me/ios'));
});
