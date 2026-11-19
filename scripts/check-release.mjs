import { appendFileSync } from 'node:fs';

export async function checkRelease(api, repo, requested = '', force = false) {
  const upstream = 'openchamber/openchamber';
  if (requested && !/^v\d+\.\d+\.\d+$/.test(requested)) throw new Error('Use a stable tag such as v2.7.2');
  const release = await api(`/repos/${upstream}/releases/${requested ? `tags/${requested}` : 'latest'}`);
  if (release.draft || release.prerelease || !/^v\d+\.\d+\.\d+$/.test(release.tag_name)) throw new Error('Not a stable release');
  const tag = release.tag_name;
  const filename = `OpenChamber-${tag}-unsigned.ipa`;
  const existing = await api(`/repos/${repo}/releases/tags/${tag}`, true);
  const complete = existing && !existing.draft && [filename, 'SHA256SUMS', 'build-info.json'].every(name => existing.assets.some(a => a.name === name && a.state === 'uploaded'));
  if (complete && !force) return { build: 'false', tag };
  const commit = await api(`/repos/${upstream}/commits/${tag}`);
  if (!/^[0-9a-f]{40}$/.test(commit.sha)) throw new Error('Invalid upstream commit');
  return { build: 'true', tag, sha: commit.sha, version: tag.slice(1), filename };
}

if (process.env.GITHUB_OUTPUT) {
  const api = async (path, allow404 = false) => {
    const response = await fetch(`https://api.github.com${path}`, { headers: {
      Authorization: `Bearer ${process.env.GH_TOKEN}`, 'X-GitHub-Api-Version': '2022-11-28',
      Accept: 'application/vnd.github+json',
    }});
    if (allow404 && response.status === 404) return null;
    if (!response.ok) throw new Error(`GitHub ${path}: HTTP ${response.status}`);
    return response.json();
  };
  const result = await checkRelease(api, process.env.GITHUB_REPOSITORY, process.env.REQUESTED_TAG, process.env.FORCE_BUILD === 'true');
  for (const [key, value] of Object.entries(result)) appendFileSync(process.env.GITHUB_OUTPUT, `${key}=${value}\n`);
  console.log(result);
}
