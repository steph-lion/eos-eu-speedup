import argparse
import sys

from ndspy.rom import NintendoDSRom
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.patch.patches import Patcher

# Must match SPEED_STRING_FIRST_ID in c-of-time/src/speed.c.
SPEED_STRING_FIRST_ID = 17298
SPEED_LABELS = {
    "e": "Speed:",
    "f": "Vitesse :",
    "g": "Tempo:",
    "i": "Velocità:",
    "s": "Velocidad:",
}


UNUSED_STRING_PLACEHOLDERS = ("[M:D0]", "[M:D1]")


def write_strings(rom, config, lang: str, strings_by_id: dict[int, str]) -> None:
    path = f"MESSAGE/text_{lang}.str"
    strings = FileType.STR.deserialize(rom.getFileByName(path), string_encoding=config.string_encoding)
    for string_id, text in strings_by_id.items():
        current = strings.strings[string_id - 1]
        if current not in UNUSED_STRING_PLACEHOLDERS and current != text:
            sys.exit(f"String {string_id} in {path} is already in use: {current!r}")
        strings.strings[string_id - 1] = text
    rom.setFileByName(path, FileType.STR.serialize(strings, string_encoding=config.string_encoding))


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply ExtraSpace (required by c-of-time) and write the speed patch strings.")
    parser.add_argument("rom_in")
    parser.add_argument("rom_out")
    args = parser.parse_args()

    rom = NintendoDSRom.fromFile(args.rom_in)
    config = get_ppmdu_config_for_rom(rom)
    if config.game_edition != "EoS_EU":
        sys.exit(f"Unexpected ROM: {config.game_edition} (EoS_EU required)")

    patcher = Patcher(rom, config)
    if not patcher.is_applied("ExtraSpace"):
        print("  applying ExtraSpace")
        patcher.apply("ExtraSpace")

    for lang, label in SPEED_LABELS.items():
        write_strings(rom, config, lang, {SPEED_STRING_FIRST_ID + i: f"{label} {i + 1}x" for i in range(4)})

    rom.saveToFile(args.rom_out)
    print(f"Done: {args.rom_out}")


if __name__ == "__main__":
    main()
