import argparse
import struct
import sys

from ndspy.rom import NintendoDSRom

GET_SPEED_OPTION = 0x204B218
SPEED_OPTION_CALL_SITES = [0x2305778, 0x2305800, 0x2305A28]
GET_AND_STORE_BUTTON_INPUT = 0x22E13A4
PUSH_R3_LR = 0xE92D4008


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

    overlay = NintendoDSRom.fromFile(args.rom).loadArm9Overlays()[29]

    def word_at(addr: int) -> int:
        return struct.unpack_from("<I", overlay.data, addr - overlay.ramAddress)[0]

    checks = [(addr, bl_target(addr, word_at(addr)) == GET_SPEED_OPTION) for addr in SPEED_OPTION_CALL_SITES]
    checks.append((GET_AND_STORE_BUTTON_INPUT, word_at(GET_AND_STORE_BUTTON_INPUT) == PUSH_R3_LR))

    for addr, ok in checks:
        print(f"  {addr:#x}: {word_at(addr):08x} {'OK' if ok else 'UNEXPECTED'}")
    if not all(ok for _, ok in checks):
        sys.exit("The ROM does not match: the speed patch cannot be applied.")


if __name__ == "__main__":
    main()
