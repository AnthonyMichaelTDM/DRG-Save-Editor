import struct
from .Enums import Dwarf, Minerals, Brewing


class Stats:
    dwarf_xp: dict[Dwarf, int] = dict()
    dwarf_promo: dict[Dwarf, int] = dict()
    resources_minerals: dict[Minerals, int] = dict()
    resources_brewing: dict[Brewing, int] = dict()

    def get_dwarf_xp(save_bytes) -> None:

        en_marker = b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50"
        sc_marker = b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50"
        dr_marker = b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50"
        gu_marker = b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50"

        # start_offset = 0
        xp_offset = 48
        eng_xp_pos: int = save_bytes.find(en_marker) + xp_offset
        scout_xp_pos: int = save_bytes.find(sc_marker) + xp_offset
        drill_xp_pos: int = save_bytes.find(dr_marker) + xp_offset
        gun_xp_pos: int = save_bytes.find(gu_marker) + xp_offset

        eng_xp = struct.unpack("i", save_bytes[eng_xp_pos : eng_xp_pos + 4])[0]
        scout_xp = struct.unpack("i", save_bytes[scout_xp_pos : scout_xp_pos + 4])[0]
        drill_xp = struct.unpack("i", save_bytes[drill_xp_pos : drill_xp_pos + 4])[0]
        gun_xp = struct.unpack("i", save_bytes[gun_xp_pos : gun_xp_pos + 4])[0]

        num_promo_offset = 108
        eng_num_promo = struct.unpack(
            "i",
            save_bytes[
                eng_xp_pos + num_promo_offset : eng_xp_pos + num_promo_offset + 4
            ],
        )[0]
        scout_num_promo = struct.unpack(
            "i",
            save_bytes[
                scout_xp_pos + num_promo_offset : scout_xp_pos + num_promo_offset + 4
            ],
        )[0]
        drill_num_promo = struct.unpack(
            "i",
            save_bytes[
                drill_xp_pos + num_promo_offset : drill_xp_pos + num_promo_offset + 4
            ],
        )[0]
        gun_num_promo = struct.unpack(
            "i",
            save_bytes[
                gun_xp_pos + num_promo_offset : gun_xp_pos + num_promo_offset + 4
            ],
        )[0]

        Stats.dwarf_xp = {
            Dwarf.DRILLER: drill_xp,
            Dwarf.GUNNER: gun_xp,
            Dwarf.SCOUT: scout_xp,
            Dwarf.ENGINEER: eng_xp,
        }
        Stats.dwarf_promo = {
            Dwarf.DRILLER: drill_num_promo,
            Dwarf.GUNNER: gun_num_promo,
            Dwarf.SCOUT: scout_num_promo,
            Dwarf.ENGINEER: eng_num_promo,
        }
