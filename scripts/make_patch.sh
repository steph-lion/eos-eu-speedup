#!/usr/bin/env bash
# Usage: bash scripts/make_patch.sh <version> [clean_eu_rom.nds]
# Run scripts/build_rom.sh first.
set -euo pipefail

cd "$(dirname "$0")/.."
VERSION="${1:?Usage: bash scripts/make_patch.sh <version> [clean_eu_rom.nds]}"
BASE_ROM="${2:-rom/Pokemon Mystery Dungeon - Explorers of Sky (Europe) (En,Fr,De,Es,It).nds}"
MOD_ROM="out/eos-eu-speedup.nds"
PATCH="dist/eos-eu-speedup-$VERSION.xdelta"
MSYS2_ROOT="${MSYS2_ROOT:-/c/msys64}"

if command -v xdelta3 >/dev/null; then
  XDELTA=xdelta3
elif [ -x "$MSYS2_ROOT/usr/bin/xdelta3.exe" ]; then
  XDELTA="$MSYS2_ROOT/usr/bin/xdelta3.exe"
else
  echo "xdelta3 not found"; exit 1
fi

mkdir -p dist
"$XDELTA" -e -9 -f -s "$BASE_ROM" "$MOD_ROM" "$PATCH"
echo "Patch: $PATCH ($(du -h "$PATCH" | cut -f1))"
echo "Patched ROM SHA1: $(sha1sum "$MOD_ROM" | cut -d' ' -f1)"
