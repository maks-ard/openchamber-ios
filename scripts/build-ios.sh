#!/usr/bin/env bash
set -euo pipefail
cd upstream
command -v pod >/dev/null || brew install cocoapods
bun install --frozen-lockfile
# Build the same mobile assets as upstream, syncing only iOS.
bun run mobile:build
(cd packages/mobile && bunx cap sync ios)

mkdir -p ../dist
set +e
xcodebuild -workspace packages/mobile/ios/App/App.xcworkspace \
  -scheme App -configuration Release -sdk iphoneos \
  -destination 'generic/platform=iOS' -derivedDataPath "$RUNNER_TEMP/oc-derived" \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= \
  CODE_SIGN_ENTITLEMENTS= DEVELOPMENT_TEAM= \
  MARKETING_VERSION="$APP_VERSION" CURRENT_PROJECT_VERSION="$GITHUB_RUN_NUMBER" \
  build > ../dist/xcodebuild.log 2>&1
status=$?
set -e
tail -n 60 ../dist/xcodebuild.log
if [ "$status" -ne 0 ]; then exit "$status"; fi
cd ..
python3 scripts/package-ipa.py "$RUNNER_TEMP/oc-derived/Build/Products/Release-iphoneos/App.app"
