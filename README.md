# EoS EU Speedup

A patch for the **European** release of **Pokémon Mystery Dungeon: Explorers of Sky** that adds an adjustable **1x–4x dungeon speed**.

The speed-up is native: the game logic is not run multiple times per frame. Durations are shortened directly in the game code, so it costs no extra CPU time and works on real hardware.

## Features

| Input | Effect |
|---|---|
| **Select** (in a dungeon) | Cycles the speed 1x → 2x → 3x → 4x → 1x and shows it in the message log |
| **Hold B** (anywhere) | Text appears instantly |

What the speed affects:
- **Walking** of every Pokémon on the floor, team members and enemies alike.
- **Message pause**: after each dungeon message ("X used Y!") the game blocks for 60 frames at 1x, 30 at 2x, 20 at 3x and 15 at 4x. The message stays on screen for its usual time.
- **Animations**: every sprite animation in a dungeon (attacks, move effects, hit reactions, idle) advances N times per frame. Outside dungeons animations run at normal speed.
- **Message box**: the dungeon message box prints and scrolls its lines up to N times per frame.
- **Floor transitions**: the floor title card and the dungeon fades last 1/N of their usual time.
- **Camera switches**: the pause before the camera moves to another Pokémon lasts 1/N of its usual time.
- **Projectiles**: thrown items and projectile moves fly N times faster.
- **Text speed**: text is revealed 1 to 4 characters per step, in dungeons and in every other dialogue, using the last speed set in a dungeon.

Notes:
- The setting persists until the game is turned off. It starts at 1x on boot.
- Inside dungeons, Select is used only for the speed setting. Its vanilla action is disabled there.
- Outside dungeons only the text speed changes: movement, the guild, towns and cutscenes run at normal speed. Dialogue still waits for a button press.
- The speed message is localized for all five EU languages.


## Installation

You need your own **European** Explorers of Sky ROM (game code `C2SP`):

| | |
|---|---|
| File | `Pokemon Mystery Dungeon - Explorers of Sky (Europe) (En,Fr,De,Es,It).nds` |
| SHA1 | `c838a5adf1ed32d2da8454976e5b1a1aa189c139` |

1. Download the `.xdelta` file from [Releases](../../releases).
2. Apply it to the clean ROM with [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) or Delta Patcher.
3. Play the patched ROM in an emulator such as [melonDS](https://melonds.kuribo64.net/), or on a 3DS with TWiLight Menu++.

**Notes:**
- Saves from the original ROM are compatible: copy the `.sav` file and give it the same name as the patched ROM.
- After updating the patch, load in-game saves rather than emulator savestates. Savestates keep the previous version of the patch code in memory.
- Tested on melonDS and on a 3DS with TWiLight Menu++ (nds-bootstrap).

This repository does not contain or distribute any ROM.

## Combining with other patches

The patch includes Frostbyte's **ExtraSpace** patch, which c-of-time needs to load custom code. Other [SkyTemple](https://skytemple.org) ASM patches are expected to work when applied on top of the patched ROM with SkyTemple, but that order is not tested yet. The tested order is the opposite: SkyTemple patches first, then this patch built on top (see below).

To add the speed patch to an existing EU ROM hack, build from source and pass your ROM to the build script. The build stops if the hack changed any of the game locations this patch modifies, or if it uses the message IDs 17298–17301.

## Building from source (Windows)

Requirements: Git, Python 3.12, [MSYS2](https://www.msys2.org/) and [SkyTemple](https://skytemple.org), which provides `armips`.

```bash
git clone --recursive https://github.com/steph-lion/eos-eu-speedup.git
cd eos-eu-speedup
```

In an **MSYS2 UCRT64** terminal:

```bash
pacman -S git make xdelta3 mingw-w64-ucrt-x86_64-arm-none-eabi-toolchain mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-python-pip mingw-w64-ucrt-x86_64-python-yaml
```

```bash
pip3 install --break-system-packages ndspy
```

In Git Bash, from the project folder:

```bash
py -3.12 -m venv .venv
```

```bash
.venv/Scripts/python -m pip install -r requirements.txt
```

Then:
1. Put the clean EU ROM in `rom/`, or pass its path to the build script.
2. If SkyTemple is not installed in `SkyTemple/` inside the project, set `SKYTEMPLE_ARMIPS_EXEC` to its `armips.exe`.
3. Build the ROM and the patch:

```bash
bash scripts/build_rom.sh
```

```bash
bash scripts/make_patch.sh v0.1.0
```

The outputs are `out/eos-eu-speedup.nds` and `dist/eos-eu-speedup-v0.1.0.xdelta`.

To build on top of another EU ROM hack:

```bash
bash scripts/build_rom.sh path/to/hack.nds out/hack-speedup.nds
```

## Layout

| Path | Contents |
|---|---|
| `scripts/prepare_rom.py` | Applies ExtraSpace and writes the localized speed messages |
| `scripts/check_addresses.py` | Verifies the instructions replaced by the speed patch |
| `scripts/build_rom.sh` | Builds the patched ROM |
| `scripts/make_patch.sh` | Creates the distributable `.xdelta` |
| `c-of-time/src/speed.c`, `c-of-time/src/speed_hook.s` | Speed patch code |
| `c-of-time/patches/speed.asm` | Patched game locations (EU addresses) |

### How the speed patch works
The game has an internal "Speed" option (`GetSpeedOption`). When it is set to fast, the game uses a walk multiplier of 2: each tile takes 24 / multiplier frames and the sprite moves multiplier pixels per frame. The multiplier is computed in three places in overlay 29. The patch replaces all three with a value from 1 to 4. Since 24 is divisible by 1, 2, 3 and 4, every step stays whole and even.

Speed cycling hooks `GetAndStoreButtonInput`. The hook reads Select, then clears it from the input the dungeon sees.

`LogMessage` starts the message box timer at 240 frames and `WaitUntilAlertBoxPauseIsOver` blocks until it drops below 180. The patch raises that threshold with the speed, so the blocking part shrinks while the box keeps its display time.

`UpdateAlertBox` prints one line or scrolls the message box by 2 pixels per call. While the box is printing or scrolling, the patch calls it up to N times per frame.

`SwitchAnimationControlToNextFrame` advances an animation by one tick. In dungeons the patch runs it N times per frame, which also covers frames shorter than N ticks, such as most move effects. A hook on `AdvanceFrame`, which only runs in dungeon mode, tells the patch whether a dungeon is active.

`HandleFloorCard` counts the title card frames down by N, and the dungeon fade update multiplies its per-frame brightness change by N where it is read. `TryPointCameraToMonster` waits for a frame counter to reach a threshold; the patch reads the counter multiplied by N, so it also works with patches that change the threshold. The projectile flight loops only call `AdvanceFrame` on every Nth iteration.

The text renderer copies a "characters per step" value from the text box state before revealing text. The patch multiplies that value by the speed at both places where it is read, or replaces it with the renderer's own "show everything" value while B is held.

## Credits
- [c-of-time](https://github.com/SkyTemple/c-of-time), vendored in `c-of-time/` at `1b6cabb`
- [pmdsky-debug](https://github.com/UsernameFodder/pmdsky-debug) by UsernameFodder and contributors
- ExtraSpace by Frostbyte, applied through [SkyTemple](https://skytemple.org)
- [armips](https://github.com/Kingcom/armips) by Kingcom

## License
Same split as c-of-time:
- scripts in `scripts/` and `c-of-time/scripts/` are licensed under **GPLv3** ([LICENSE_GPLv3](LICENSE_GPLv3));
- all other code (C, assembly, patches) is licensed under **MIT** ([LICENSE_MIT](LICENSE_MIT)).

This is a fan project, not affiliated with Nintendo, The Pokémon Company, Chunsoft or Spike Chunsoft. Pokémon is a trademark of its respective owners.
