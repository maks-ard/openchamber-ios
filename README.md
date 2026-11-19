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

## Wi-Fi signature refresh on Windows

The user confirmed installation, connection to an OpenChamber server on a separate work laptop,
and successful **Refresh All with USB disconnected** on 2026-11-19.

AltServer runs on this Windows PC; it is separate from the OpenChamber server. The phone and this PC
must be on the same home network for local refresh. Enable Background Refresh in AltStore and allow
Background App Refresh for AltStore in iOS. iOS chooses when background attempts run; this is not a
fixed daily schedule or a guarantee. Check My Apps if an expiry date approaches.

`scripts/install-altserver-startup.ps1` registers the current user's interactive logon task
`OpenChamber AltServer` with highest privileges, unlimited runtime and no concurrent task instances.
The default executable is `.tools/altstore/AltServer/AltServer.exe`. Run the script as administrator;
`-StartNow` replaces matching manually started processes with one scheduled instance.
The scheduled task was launched and verified Running; a full reboot/login has not been tested.
To stop autostart, disable this task in Task Scheduler. Do not start extra manual AltServer instances.

During setup, Wi-Fi lockdown was already enabled and USB trust was valid. TCP port 62078 on the phone
was reachable over home Wi-Fi, but AltServer reported error 2003. Restarting Bonjour Service and
Apple Mobile Device Service, then AltServer, was followed by a successful wireless refresh reported
by the user. The diagnostic usbmux listing still showed no Network entry; that listing alone is not
a reliable success criterion for this setup. No firewall rules or network profiles were changed.

`scripts/iphone-wifi.py` is an optional diagnostic helper using pymobiledevice3 (tested 11.60.0):
`status` reads the flag via USB; `enable`/`disable` change it; `network` checks usbmux network discovery.
It uses existing trust only and deliberately excludes device identifiers and pairing records from output.
The local isolated environment is `.tools/ios-tools`; it includes the library modules needed by this
helper, not every dependency of the full pymobiledevice3 CLI.

For the earlier Windows TLS error, the user manually installed the official Apple Root CA from
[Apple PKI](https://www.apple.com/certificateauthority/). The Apple authentication endpoint then
passed Windows TLS verification. Never disable certificate verification as a workaround.

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

Verified on 2026-11-19:
- [First successful build and publication](https://github.com/maks-ard/openchamber-ios/actions/runs/44518904915):
  upstream v2.7.2, commit `1a151518c95cc5ff3578bab593d2f96862ff3bb8`, minimum iOS 15.5.
- Downloaded IPA: SHA-256 matched; ARM64 Mach-O executable and bundled mobile HTML were present;
  app extensions were absent. The IPA is approximately 28.5 MiB.
- [Repeat check](https://github.com/maks-ard/openchamber-ios/actions/runs/44520847439) succeeded and
  skipped both macOS compilation and publication.
- Workflow passed actionlint; all five release-selection tests passed locally and on GitHub.
- Installation, connection to the work-laptop server and wireless signature refresh were confirmed
  by the user. Unattended iOS background refresh and future daily release-check execution remain unverified.

To stop automatic updates, disable the workflow on the Actions page. Published files remain available.
