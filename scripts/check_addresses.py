import argparse
import struct
import sys

from ndspy.rom import NintendoDSRom

GET_SPEED_OPTION = 0x204B218
SPEED_OPTION_CALL_SITES = [0x2305778, 0x2305800, 0x2305A28]
GET_AND_STORE_BUTTON_INPUT = 0x22E13A4
PUSH_R3_LR = 0xE92D4008
ALERT_BOX_PAUSE_CMP = 0x234C67C
CMP_R0_180 = 0xE35000B4
TEXT_SPEED_LOADS = [0x2021028, 0x2021B04]
LDREQ_R0_R4_100 = 0x05940064
UPDATE_ALERT_BOX = 0x2030568
PUSH_R3_R9_LR = 0xE92D43F8
ADVANCE_FRAME = 0x22EA990
SWITCH_ANIMATION_CONTROL = 0x201C4F4
PUSH_R4_LR = 0xE92D4010
FLOOR_CARD_DECREMENT = 0x2349020
SUB_R5_R5_1 = 0xE2455001
FADE_DELTA_LOADS = {0x234D544: 0xE5940094, 0x234D56C: 0xE5941094, 0x234D598: 0xE5940094, 0x234D5C0: 0xE5940094}
CAMERA_PAUSE_COUNTER_LOAD = 0x22FA328
LDRSH_R0_R0_28 = 0xE1D001FC
PROJECTILE_ADVANCE_FRAMES = [0x232413C, 0x2348A28]


def bl_target(addr: int, word: int) -> int | None:
    if (word & 0x0F000000) != 0x0B000000 or (word >> 28) != 0xE:
        return None
    offset = word & 0x00FFFFFF
    if offset & 0x800000:
        offset -= 0x1000000
    return addr + 8 + offset * 4


def main() -> None:
    parser = argparse.ArgumentParser(description="Check that the ROM contains the instructions replaced by patches/speed.asm.")
    parser.add_argument("rom")
    args = parser.parse_args()

    rom = NintendoDSRom.fromFile(args.rom)
    overlays = rom.loadArm9Overlays()
    arm9 = rom.loadArm9()
    binaries = {
        "arm9": (arm9.ramAddress, arm9.save(compress=False)),
        "ov29": (overlays[29].ramAddress, overlays[29].data),
    }

    def word_at(addr: int, binary: str = "ov29") -> int:
        base, data = binaries[binary]
        return struct.unpack_from("<I", data, addr - base)[0]

    checks = [(addr, "ov29", bl_target(addr, word_at(addr)) == GET_SPEED_OPTION) for addr in SPEED_OPTION_CALL_SITES]
    checks.append((GET_AND_STORE_BUTTON_INPUT, "ov29", word_at(GET_AND_STORE_BUTTON_INPUT) == PUSH_R3_LR))
    checks.append((ALERT_BOX_PAUSE_CMP, "ov29", word_at(ALERT_BOX_PAUSE_CMP) == CMP_R0_180))
    checks += [(addr, "arm9", word_at(addr, "arm9") == LDREQ_R0_R4_100) for addr in TEXT_SPEED_LOADS]
    checks.append((UPDATE_ALERT_BOX, "arm9", word_at(UPDATE_ALERT_BOX, "arm9") == PUSH_R3_R9_LR))
    checks.append((ADVANCE_FRAME, "ov29", word_at(ADVANCE_FRAME) == PUSH_R3_LR))
    checks.append((SWITCH_ANIMATION_CONTROL, "arm9", word_at(SWITCH_ANIMATION_CONTROL, "arm9") == PUSH_R4_LR))
    checks.append((FLOOR_CARD_DECREMENT, "ov29", word_at(FLOOR_CARD_DECREMENT) == SUB_R5_R5_1))
    checks += [(addr, "ov29", word_at(addr) == word) for addr, word in FADE_DELTA_LOADS.items()]
    checks += [(addr, "ov29", bl_target(addr, word_at(addr)) == ADVANCE_FRAME) for addr in PROJECTILE_ADVANCE_FRAMES]
    checks.append((CAMERA_PAUSE_COUNTER_LOAD, "ov29", word_at(CAMERA_PAUSE_COUNTER_LOAD) == LDRSH_R0_R0_28))

    for addr, binary, ok in checks:
        print(f"  {binary} {addr:#x}: {word_at(addr, binary):08x} {'OK' if ok else 'UNEXPECTED'}")
    if not all(ok for _, _, ok in checks):
        sys.exit("The ROM does not match: the speed patch cannot be applied.")


if __name__ == "__main__":
    main()
