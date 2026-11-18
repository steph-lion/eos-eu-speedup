#!/usr/bin/env bash
# Usage: bash scripts/build_rom.sh [base_rom.nds] [output.nds]
# The base ROM is a clean EU ROM by default; an EU ROM hack also works if the patched
# locations are untouched (verified by scripts/check_addresses.py).
# Optional env: SKYTEMPLE_ARMIPS_EXEC (armips path), MSYS2_ROOT (default /c/msys64)
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"
BASE_ROM="${1:-rom/Pokemon Mystery Dungeon - Explorers of Sky (Europe) (En,Fr,De,Es,It).nds}"
OUT_ROM="${2:-out/eos-eu-speedup.nds}"
PREPARED_ROM="out/prepared.nds"
EU_SHA1="c838a5adf1ed32d2da8454976e5b1a1aa189c139"
MSYS2_ROOT="${MSYS2_ROOT:-/c/msys64}"
export PYTHONIOENCODING=utf-8

if [ -x .venv/Scripts/python ]; then PY=".venv/Scripts/python -I"; else PY=".venv/bin/python -I"; fi

if [ -z "${SKYTEMPLE_ARMIPS_EXEC:-}" ] && [ -f SkyTemple/_internal/skytemple_files/_resources/armips.exe ]; then
  export SKYTEMPLE_ARMIPS_EXEC="$ROOT/SkyTemple/_internal/skytemple_files/_resources/armips.exe"
fi

run_in_cot() {
  if [ -x "$MSYS2_ROOT/usr/bin/bash.exe" ]; then
    MSYSTEM=UCRT64 "$MSYS2_ROOT/usr/bin/bash.exe" -lc "cd '$(cygpath -u "$ROOT")/c-of-time' && $1"
  else
    (cd c-of-time && bash -c "$1")
  fi
}

echo "== Checking base ROM"
[ -f "$BASE_ROM" ] || { echo "ROM not found: $BASE_ROM"; exit 1; }
if [ "$(sha1sum "$BASE_ROM" | cut -d' ' -f1)" != "$EU_SHA1" ]; then
  echo "Not a clean EU ROM: building on top of an existing ROM hack"
fi
mkdir -p "$(dirname "$OUT_ROM")" out

echo "== Applying ExtraSpace and writing strings"
rm -f "$PREPARED_ROM"
$PY scripts/prepare_rom.py "$BASE_ROM" "$PREPARED_ROM"

echo "== Checking patch addresses"
$PY scripts/check_addresses.py "$PREPARED_ROM"

echo "== Building and injecting c-of-time code"
# "make headers" rewrites pmdsky-debug in place and is not idempotent.
if git -C c-of-time/pmdsky-debug diff --quiet; then
  run_in_cot "make headers"
fi
cp "$PREPARED_ROM" c-of-time/rom.nds
run_in_cot "make patch"

cp c-of-time/out.nds "$OUT_ROM"
rm -f c-of-time/rom.nds "$PREPARED_ROM"
echo "Done: $OUT_ROM"
