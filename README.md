# OpenChamber iOS builds

Unofficial unsigned iPhone builds of [OpenChamber](https://github.com/openchamber/openchamber).
No Mac, Apple credentials or paid Apple Developer membership is needed for cloud compilation.
Installation still requires local signing, for example with AltStore Classic on Windows.

## Updates

- Every day at 09:23 Moscow time (06:23 UTC), Linux checks the latest stable upstream release.
- A standard `macos-26` runner builds only when that version has no complete release here.
- The release contains the unsigned IPA, SHA-256 checksum, exact upstream commit and MIT license.
- Failed builds publish no new version and retry at the next check. Diagnostics expire after 3 days.
- Actions artifacts expire after 1 day; downloadable IPAs live in Releases.
- The Actions page also allows a manual run, an explicit stable tag, and a forced rebuild.
- GitHub can disable schedules after 60 days without repository activity. Re-enable the workflow
  from Actions if that happens. The workflow does not create artificial keepalive commits.
- Standard GitHub-hosted runners are currently free in public repositories. Keep this repository
  public and use standard runners; private repositories and larger runners have different billing.

## Install on Windows

1. Download the IPA from this repository's Releases.
2. Follow [AltStore Classic for Windows](https://faq.altstore.io/altstore-classic/how-to-install-altstore-windows).
3. In AltStore, My Apps → + → select the IPA, and sign with your own Apple Account.
4. Enable Developer Mode and trust the developer on the phone if prompted.
5. Pair the app with your running OpenChamber server.

A free account requires refreshing the signature every 7 days. That is separate from installing
a newer application version. Keep the same signing account and application identifier when updating;
install over the existing app rather than deleting it to preserve local connections.
Do not put Apple credentials, pairing QR codes, server tokens or provisioning profiles in this repository.

## Differences from TestFlight

The app uses the upstream `com.openchamber.app` identifier before local re-signing.
Widget and notification service extensions are excluded to avoid additional App IDs and App Groups.
APNs push notifications do not work with free-account re-signing. The main app, QR scanner and
server connection remain in the build; actual on-device behavior must be verified after installation.
An upstream update can require build maintenance; automation cannot guarantee every future release compiles.

## Security and verification

The Linux check resolves a stable release tag to an exact source commit. The macOS build job has
read-only repository permission and does not persist checkout credentials. A separate Linux job
verifies the checksum and publishes with write permission. No Apple signing secrets are required.
Third-party Actions are pinned to commit hashes. The package lockfile is enforced.

Local check: `node --test scripts/check-release.test.mjs`.
Build proof: a successful Actions run producing a device-arm64 IPA; device proof: installation and pairing.

To stop automatic updates, disable the workflow on the Actions page. Published files remain available.
