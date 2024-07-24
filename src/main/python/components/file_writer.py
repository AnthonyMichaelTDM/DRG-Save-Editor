import struct


from definitions import (
    RESOURCE_GUIDS,
    SEASON_GUIDS,
)
from .Enums import Dwarf
from .StateManager import Stats


def make_save_file(file_path, new_values: Stats) -> bytes:
    with open(file_path, "rb") as f:
        save_data: bytes = f.read()

    save_data = write_resources(new_values, save_data)
    save_data = write_credits(new_values, save_data)
    save_data = write_perk_points(new_values, save_data)
    save_data = write_xp(new_values, save_data)
    save_data = write_overclocks(new_values, save_data)
    save_data = write_season_data(new_values, save_data)
    save_data = write_weapon_maintenance_data(new_values, save_data)

    return save_data


def write_weapon_maintenance_data(new_values, save_data):
    OFFSET_WEAPON_XP = 0x6E
    OFFSET_WEAPON_LEVEL_UP = 0xCA
    if new_values.weapons:
        for weapon_pos, _ in new_values.weapons.items():
            xp = struct.pack("i", new_values.weapons[weapon_pos][0])
            level_up = struct.pack("b", new_values.weapons[weapon_pos][2])
            save_data = (
                save_data[: weapon_pos + OFFSET_WEAPON_XP]
                + xp
                + save_data[weapon_pos + OFFSET_WEAPON_XP + 4 :]
            )
            save_data = (
                save_data[: weapon_pos + OFFSET_WEAPON_LEVEL_UP]
                + level_up
                + save_data[weapon_pos + OFFSET_WEAPON_LEVEL_UP + 1 :]
            )
            
    return save_data


def write_season_data(new_values, save_data):
    # todo: have this only declared once between here and initial file parsing
    SEASON_XP_OFFSET = 169
    SCRIP_OFFSET = 209

    for season_num, season_guid in SEASON_GUIDS.items():
        season_marker: bytes = bytes.fromhex(season_guid)
        season_marker_pos: int = save_data.find(season_marker)

        # season data does not exist
        if season_marker_pos == -1:
            print(f"Season {season_num} missing")
            continue

        season_xp_pos: int = season_marker_pos + SEASON_XP_OFFSET
        scrip_pos: int = season_marker_pos + SCRIP_OFFSET

        save_data = (
            save_data[:season_xp_pos]
            + struct.pack("i", new_values.season_data[season_num]["xp"])
            + save_data[season_xp_pos + 4 :]
        )
        save_data = (
            save_data[:scrip_pos]
            + struct.pack("i", new_values.season_data[season_num]["scrip"])
            + save_data[scrip_pos + 4 :]
        )

    return save_data


def write_overclocks(new_values, save_data):
    search_term = b"ForgedSchematics"  # \x00\x0F\x00\x00\x00Struct'
    search_end = b"SkinFixupCounter"
    pos = save_data.find(search_term)
    end_pos: int = (
        save_data.find(search_end) - 4
    )

    if pos > 0:
        num_forged = struct.unpack("i", save_data[pos + 63 : pos + 67])[0]
        # TODO - After implementing OCS into the State Manager
        # unforged_ocs = new_values["unforged"]

        schematic_save_marker = b"SchematicSave"
        schematic_save_offset = 33
        schematic_save_pos = (
            save_data.find(schematic_save_marker) + schematic_save_offset
        )
        schematic_save_end_pos = schematic_save_pos + 8
        schematic_save_size = b""

        # assuming something like this will be implemented in the future
        unforged_ocs = new_values.unforged_ocs

        if len(unforged_ocs) > 0:
            ocs: bytes = (
                b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0E\x00\x00\x00\x41\x72\x72\x61\x79\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                # number of bytes between position of first "OwnedSchematic" and end_pos, -62, as a 64bit unsigned integer
                + struct.pack("Q", 139 + len(unforged_ocs) * 16 - 62)
                + b"\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x00"
                # number of unforged ocs, stored as a 32bit unsigned integer
                + struct.pack("I", len(unforged_ocs))
                + b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                # number of bytes taken up by the GUID's of the unforged oc's, stored as a 64bit unsigned integer
                + struct.pack("Q", len(unforged_ocs) * 16)
                + b"\x05\x00\x00\x00\x47\x75\x69\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            )
            uuids: list[bytes] = [bytes.fromhex(i) for i in unforged_ocs.keys()]
            for i in uuids:
                ocs += i

            # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
            schematic_save_size = struct.pack(
                "Q",
                139 + (141 + num_forged * 16) + 4 + (139 + len(unforged_ocs) * 16) - 17,
            )

        else:
            ocs = b""
            # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
            schematic_save_size = struct.pack("Q", 139 + (141 + num_forged * 16) - 17)

        save_data = (
            save_data[: pos + (num_forged * 16) + 141] + ocs + save_data[end_pos:]
        )
        save_data = (
            save_data[:schematic_save_pos]
            + schematic_save_size
            + save_data[schematic_save_end_pos:]
        )
        
    return save_data


def write_xp(new_values, save_data):
    en_marker = b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50"
    sc_marker = b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50"
    dr_marker = b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50"
    gu_marker = b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50"
    offset = 48
    eng_xp_pos: int = save_data.find(en_marker) + offset
    scout_xp_pos: int = save_data.find(sc_marker) + offset
    drill_xp_pos: int = save_data.find(dr_marker) + offset
    gun_xp_pos: int = save_data.find(gu_marker) + offset

    eng_xp_bytes: bytes = struct.pack("i", new_values.dwarf_xp[Dwarf.ENGINEER])
    scout_xp_bytes: bytes = struct.pack("i", new_values.dwarf_xp[Dwarf.SCOUT])
    drill_xp_bytes: bytes = struct.pack("i", new_values.dwarf_xp[Dwarf.DRILLER])
    gun_xp_bytes: bytes = struct.pack("i", new_values.dwarf_xp[Dwarf.GUNNER])

    promo_offset = 108
    levels_per_promo = 25
    promo_levels_offset = 56
    eng_promo_pos: int = eng_xp_pos + promo_offset
    scout_promo_pos: int = scout_xp_pos + promo_offset
    drill_promo_pos: int = drill_xp_pos + promo_offset
    gun_promo_pos: int = gun_xp_pos + promo_offset

    eng_promo_bytes: bytes = struct.pack("i", new_values.dwarf_promo[Dwarf.ENGINEER])
    eng_promo_level_bytes: bytes = struct.pack(
        "i", new_values.dwarf_promo[Dwarf.ENGINEER] * levels_per_promo
    )
    scout_promo_bytes: bytes = struct.pack("i", new_values.dwarf_promo[Dwarf.SCOUT])
    scout_promo_level_bytes: bytes = struct.pack(
        "i", new_values.dwarf_promo[Dwarf.SCOUT] * levels_per_promo
    )
    drill_promo_bytes: bytes = struct.pack("i", new_values.dwarf_promo[Dwarf.DRILLER])
    drill_promo_level_bytes: bytes = struct.pack(
        "i", new_values.dwarf_promo[Dwarf.DRILLER] * levels_per_promo
    )
    gun_promo_bytes: bytes = struct.pack("i", new_values.dwarf_promo[Dwarf.GUNNER])
    gun_promo_level_bytes: bytes = struct.pack(
        "i", new_values.dwarf_promo[Dwarf.GUNNER] * levels_per_promo
    )

    save_data = save_data[:eng_xp_pos] + eng_xp_bytes + save_data[eng_xp_pos + 4 :]
    save_data = (
        save_data[:eng_promo_pos] + eng_promo_bytes + save_data[eng_promo_pos + 4 :]
    )
    save_data = (
        save_data[: eng_promo_pos + promo_levels_offset]
        + eng_promo_level_bytes
        + save_data[eng_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = (
        save_data[:scout_xp_pos] + scout_xp_bytes + save_data[scout_xp_pos + 4 :]
    )
    save_data = (
        save_data[:scout_promo_pos]
        + scout_promo_bytes
        + save_data[scout_promo_pos + 4 :]
    )
    save_data = (
        save_data[: scout_promo_pos + promo_levels_offset]
        + scout_promo_level_bytes
        + save_data[scout_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = (
        save_data[:drill_xp_pos] + drill_xp_bytes + save_data[drill_xp_pos + 4 :]
    )
    save_data = (
        save_data[:drill_promo_pos]
        + drill_promo_bytes
        + save_data[drill_promo_pos + 4 :]
    )
    save_data = (
        save_data[: drill_promo_pos + promo_levels_offset]
        + drill_promo_level_bytes
        + save_data[drill_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = save_data[:gun_xp_pos] + gun_xp_bytes + save_data[gun_xp_pos + 4 :]
    save_data = (
        save_data[:gun_promo_pos] + gun_promo_bytes + save_data[gun_promo_pos + 4 :]
    )
    save_data = (
        save_data[: gun_promo_pos + promo_levels_offset]
        + gun_promo_level_bytes
        + save_data[gun_promo_pos + promo_levels_offset + 4 :]
    )
    
    return save_data


def write_perk_points(new_values, save_data):
    if new_values.perk_points > 0:
        perks_marker = b"PerkPoints"
        perks_bytes: bytes = struct.pack("i", new_values.perk_points)
        if save_data.find(perks_marker) != -1:
            perks_pos: int = save_data.find(perks_marker) + 36
            save_data = save_data[:perks_pos] + perks_bytes + save_data[perks_pos + 4 :]
        else:
            perks_entry: bytes = (
                b"\x0B\x00\x00\x00\x50\x65\x72\x6B\x50\x6F\x69\x6E\x74\x73\x00\x0C\x00\x00\x00\x49\x6E\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"
                + perks_bytes
            )
            perks_pos = save_data.find(
                b"\x11\x00\x00\x00\x55\x6E\x4C\x6F\x63\x6B\x65\x64\x4D\x69\x73\x73\x69\x6F\x6E\x73\x00\x0E"
            )
            save_data = (
                save_data[:perks_pos] + perks_entry + save_data[perks_pos:]
            )
            
    return save_data


def write_credits(new_values, save_data):
    cred_marker = b"Credits"
    cred_pos: int = save_data.find(cred_marker) + 33
    cred_bytes: bytes = struct.pack("i", new_values.credits)
    save_data = save_data[:cred_pos] + cred_bytes + save_data[cred_pos + 4 :]
    return save_data


def write_resources(new_values, save_data):
    resources = new_values.resources

    res_marker = b"OwnedResources"
    res_pos: int = save_data.find(res_marker) + 85
    res_length = struct.unpack("i", save_data[res_pos - 4 : res_pos])[0] * 20
    res_bytes: bytes = save_data[res_pos : res_pos + res_length]

    for k, v in resources.items():
        if res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k])) > -1:
            pos: int = res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k]))
            res_bytes = (
                res_bytes[: pos + 16] + struct.pack("f", v) + res_bytes[pos + 20 :]
            )

    save_data = save_data[:res_pos] + res_bytes + save_data[res_pos + res_length :]
    return save_data