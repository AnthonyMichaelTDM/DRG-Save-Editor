import struct
from copy import deepcopy
from typing import Literal

from definitions import RESOURCE_GUIDS, SEASON_GUIDS
from helpers.enums import Dwarf, Resource
from helpers.overclock import Overclock, Cost


class Parser:
    @staticmethod
    def get_one_season_data(
        save_bytes: bytes, season_guid: str
    ) -> dict[Literal["xp", "scrip"], int]:
        # scrip_marker = bytes.fromhex("546F6B656E73")
        season_marker: bytes = bytes.fromhex(season_guid)
        season_marker_pos: int = save_bytes.find(season_marker)
        # season data does not exist
        if season_marker_pos == -1:
            raise ValueError("Season missing")

        season_xp_offset = 169
        scrip_offset = 209

        season_xp_pos = save_bytes.find(season_marker) + season_xp_offset
        scrip_pos = save_bytes.find(season_marker) + scrip_offset

        season_xp = struct.unpack("i", save_bytes[season_xp_pos : season_xp_pos + 4])[0]
        scrip = struct.unpack("i", save_bytes[scrip_pos : scrip_pos + 4])[0]

        return {"xp": season_xp, "scrip": scrip}

    @staticmethod
    def get_season_data(save_bytes: bytes):
        season_data = {}
        for season, guid in SEASON_GUIDS.items():
            try:
                season_data[season] = Parser.get_one_season_data(save_bytes, guid)
            except ValueError:
                print(f"Season {season} missing")
        return season_data

    @staticmethod
    def get_dwarf_xp(save_bytes: bytes):
        markers = {
            Dwarf.ENGINEER: b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50",
            Dwarf.SCOUT: b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50",
            Dwarf.DRILLER: b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50",
            Dwarf.GUNNER: b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50",
        }
        dwarf_xp = {}
        dwarf_promo = {}
        for dwarf, marker in markers.items():
            xp, num_promo = Parser.get_one_dwarf_xp(save_bytes, marker)
            dwarf_xp[dwarf] = xp
            dwarf_promo[dwarf] = num_promo
        return dwarf_xp, dwarf_promo

    @staticmethod
    def get_one_dwarf_xp(save_bytes: bytes, marker: bytes):
        xp_offset = 48
        xp_pos: int = save_bytes.find(marker) + xp_offset
        xp: int = struct.unpack("i", save_bytes[xp_pos : xp_pos + 4])[0]

        num_promo_offset = 108
        num_promo: int = struct.unpack(
            "i",
            save_bytes[xp_pos + num_promo_offset : xp_pos + num_promo_offset + 4],
        )[0]

        return xp, num_promo

    @staticmethod
    def get_credits(save_bytes: bytes) -> int:
        marker = b"Credits"
        offset = 33
        pos = save_bytes.find(marker) + offset
        return struct.unpack("i", save_bytes[pos : pos + 4])[0]

    @staticmethod
    def get_perk_points(save_bytes: bytes):
        marker = b"PerkPoints"
        if save_bytes.find(marker) == -1:
            return 0

        offset = 36
        pos = save_bytes.find(marker) + offset
        value: int = struct.unpack("i", save_bytes[pos : pos + 4])[0]
        return value

    @staticmethod
    def get_resources(save_bytes: bytes):
        resource_guids: dict[Resource, str] = deepcopy(RESOURCE_GUIDS)
        guid_length = 16
        res_marker = b"OwnedResources"
        res_pos = save_bytes.find(res_marker)

        resources = {}
        for k, v in resource_guids.items():
            marker = bytes.fromhex(v)
            pos = save_bytes.find(marker, res_pos) + guid_length
            end_pos = pos + 4
            unp = struct.unpack("f", save_bytes[pos:end_pos])
            resources[k] = int(unp[0])
        return resources

    @staticmethod
    def get_weapons(save_data: bytes):
        weapon = save_data.find(b"WeaponMaintenanceEntry") + 0x2C

        WEAPON_SIZE = 0xD9
        OFFSET_WEAPON_XP = 0x6E
        OFFSET_WEAPON_LEVEL = 0x95
        OFFSET_WEAPON_LEVEL_UP = 0xCA

        weapons = {}
        try:
            while save_data[weapon : weapon + 8].decode() == "WeaponID":
                xp = int.from_bytes(
                    save_data[
                        weapon + OFFSET_WEAPON_XP : weapon + OFFSET_WEAPON_XP + 4
                    ],
                    "little",
                )
                level = int.from_bytes(
                    save_data[
                        weapon + OFFSET_WEAPON_LEVEL : weapon + OFFSET_WEAPON_LEVEL + 4
                    ],
                    "little",
                )
                levelup = bool.from_bytes(
                    save_data[
                        weapon
                        + OFFSET_WEAPON_LEVEL_UP : weapon
                        + OFFSET_WEAPON_LEVEL_UP
                        + 1
                    ],
                    "little",
                )

                weapons[weapon] = [xp, level, levelup]
                weapon += WEAPON_SIZE
        except UnicodeDecodeError:
            print("Missing weapon data")
        return weapons

    @staticmethod
    def get_overclocks(save_data: bytes, guid_dict: dict):
        search_term = b"ForgedSchematics"
        start = save_data.find(search_term)
        if start == -1:
            raise Exception("Could not locate overclocks in the save file")

        search_end = b"SkinFixupCounter"
        end = save_data.find(search_end)
        if end == -1:
            search_end = b"bFirstSchematicMessageShown"
            end = save_data.find(search_end)

        for i in guid_dict.values():
            i["status"] = "Unacquired"

        oc_data = save_data[start:end]
        oc_list_offset = 141

        num_forged: int = struct.unpack("i", save_data[start + 63 : start + 67])[0]

        overclocks: list[Overclock] = []
        for j in range(num_forged):
            uuid = (
                save_data[
                    start
                    + oc_list_offset
                    + (j * 16) : start
                    + oc_list_offset
                    + (j * 16)
                    + 16
                ]
                .hex()
                .upper()
            )
            try:
                guid_dict[uuid]["status"] = "Forged"
                Parser._add_overclock(uuid, overclocks, guid_dict[uuid])
            except KeyError:
                pass

        has_unforged: bool = oc_data.find(b"Owned") > 0
        if not has_unforged:
            return

        num_pos = save_data.find(b"Owned", start) + 62
        num_unforged = struct.unpack("i", save_data[num_pos : num_pos + 4])[0]
        unforged_pos = num_pos + 77
        for j in range(num_unforged):
            uuid = (
                save_data[unforged_pos + (j * 16) : unforged_pos + (j * 16) + 16]
                .hex()
                .upper()
            )
            try:
                guid_dict[uuid]["status"] = "Unforged"
                Parser._add_overclock(uuid, overclocks, guid_dict[uuid])
            except KeyError:
                # does not exist in known guids
                overclocks.append(
                    Overclock(
                        dwarf="",
                        weapon="Cosmetic",
                        name="",
                        guid=uuid,
                        status="Unforged",
                        cost=Cost(),
                    )
                )

        # fill out overclocks that are known, but do not appear in the save
        loaded_ocs = [x.guid for x in overclocks]
        for uuid in guid_dict:
            if uuid not in loaded_ocs:
                Parser._add_overclock(uuid, overclocks, guid_dict[uuid])

        return overclocks

    @staticmethod
    def _add_overclock(uuid, overclocks, overclock_data):
        overclocks.append(
            Overclock(
                dwarf=overclock_data["dwarf"],
                weapon=overclock_data["weapon"],
                name=overclock_data["name"],
                guid=uuid,
                status=overclock_data["status"],
                cost=Cost(**overclock_data["cost"]),
            )
        )
