#!/usr/bin/env bash
# Both desktop editions are called "Plainwrite", so Tauri gives their installers the same file names.
# This adds the edition to each name, e.g. Plainwrite_1.0.8_x64-setup.exe -> Plainwrite-English_1.0.8_x64-setup.exe,
# so both sets can sit side by side in a run's Artifacts and on a release page.
# Usage: name-installers.sh <folder> <Edition>
set -euo pipefail
shopt -s nullglob
dir="$1"; edition="$2"
for f in "$dir"/*/*.deb "$dir"/*/*.rpm "$dir"/*/*.AppImage "$dir"/*/*.msi "$dir"/*/*.exe "$dir"/*/*.dmg; do
  base="$(basename "$f")"
  case "$base" in
    Plainwrite*) new="Plainwrite-${edition}${base#Plainwrite}" ;;
    *)           new="${edition}-${base}" ;;
  esac
  mv "$f" "$(dirname "$f")/$new"
  echo "$base -> $new"
done
