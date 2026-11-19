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
ANIMATION_STEP_LOADS = [0x201C524, 0x201C53C, 0x201C568]
LDRSH_R0_R4_4 = 0xE1D400F4


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
    overlay = rom.loadArm9Overlays()[29]
    arm9 = rom.loadArm9()
    arm9_data = arm9.save(compress=False)

    def word_at(addr: int) -> int:
        if addr < overlay.ramAddress:
            return struct.unpack_from("<I", arm9_data, addr - arm9.ramAddress)[0]
        return struct.unpack_from("<I", overlay.data, addr - overlay.ramAddress)[0]

    checks = [(addr, bl_target(addr, word_at(addr)) == GET_SPEED_OPTION) for addr in SPEED_OPTION_CALL_SITES]
    checks.append((GET_AND_STORE_BUTTON_INPUT, word_at(GET_AND_STORE_BUTTON_INPUT) == PUSH_R3_LR))
    checks.append((ALERT_BOX_PAUSE_CMP, word_at(ALERT_BOX_PAUSE_CMP) == CMP_R0_180))
    checks += [(addr, word_at(addr) == LDREQ_R0_R4_100) for addr in TEXT_SPEED_LOADS]
    checks.append((UPDATE_ALERT_BOX, word_at(UPDATE_ALERT_BOX) == PUSH_R3_R9_LR))
    checks.append((ADVANCE_FRAME, word_at(ADVANCE_FRAME) == PUSH_R3_LR))
    checks += [(addr, word_at(addr) == LDRSH_R0_R4_4) for addr in ANIMATION_STEP_LOADS]

    for addr, ok in checks:
        print(f"  {addr:#x}: {word_at(addr):08x} {'OK' if ok else 'UNEXPECTED'}")
    if not all(ok for _, ok in checks):
        sys.exit("The ROM does not match: the speed patch cannot be applied.")


if __name__ == "__main__":
    main()
