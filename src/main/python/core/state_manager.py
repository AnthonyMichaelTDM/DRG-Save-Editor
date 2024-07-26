from copy import deepcopy
import struct
from typing import Literal

from definitions import RESOURCE_GUIDS, SEASON_GUIDS
from helpers.enums import Dwarf, Resource
from helpers.overclock import Overclock
from helpers.datatypes import Item


class Stats:
    dwarf_xp: dict[Dwarf, int]
    dwarf_promo: dict[Dwarf, int]
    season_data: dict[int, dict[Literal["xp", "scrip"], int]] = dict()
    resources: dict[Resource, int] = dict()
    credits: int
    perk_points: int
    weapons: dict[int, list[int | bool]] = dict()
    guid_dict: dict[str, Item] = dict()
    overclocks: list[Overclock] = list()

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_season_data(
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
    def get_seasons(save_bytes: bytes) -> None:
        for season, guid in SEASON_GUIDS.items():
            try:
                Stats.season_data[season] = Stats.get_season_data(save_bytes, guid)
            except ValueError:
                print(f"Season {season} missing")

    @staticmethod
    def get_dwarf_xp(save_bytes: bytes) -> None:
        markers = {
            Dwarf.ENGINEER: b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50",
            Dwarf.SCOUT: b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50",
            Dwarf.DRILLER: b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50",
            Dwarf.GUNNER: b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50",
        }
        Stats.dwarf_xp = {}
        Stats.dwarf_promo = {}
        for dwarf, marker in markers.items():
            xp, num_promo = Stats.get_one_dwarf_xp(save_bytes, marker)
            Stats.dwarf_xp[dwarf] = xp
            Stats.dwarf_promo[dwarf] = num_promo

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
    def get_perk_points(save_bytes: bytes) -> int:
        marker = b"PerkPoints"
        offset = 36
        if save_bytes.find(marker) == -1:
            return 0
        else:
            pos = save_bytes.find(marker) + offset
            return struct.unpack("i", save_bytes[pos : pos + 4])[0]

    @staticmethod
    def get_misc(save_bytes: bytes) -> None:
        Stats.credits = Stats.get_credits(save_bytes)
        Stats.perk_points = Stats.get_perk_points(save_bytes)

    @staticmethod
    def get_resources(save_bytes: bytes) -> None:
        # extracts the resource counts from the save file
        # print('getting resources')
        # resource GUIDs
        resource_guids: dict[Resource, str] = deepcopy(RESOURCE_GUIDS)
        guid_length = 16  # length of GUIDs in bytes
        res_marker = b"OwnedResources"  # marks the beginning of where resource values can be found
        res_pos = save_bytes.find(res_marker)
        # print("getting resources")
        for k, v in resource_guids.items():  # iterate through resource list
            # print(f"key: {k}, value: {v}")
            marker = bytes.fromhex(v)
            pos = (
                save_bytes.find(marker, res_pos) + guid_length
            )  # search for the matching GUID
            end_pos = pos + 4  # offset for the actual value
            # extract and unpack the value
            unp = struct.unpack("f", save_bytes[pos:end_pos])
            Stats.resources[k] = int(unp[0])  # save resource count

    @staticmethod
    def get_weapons(save_data: bytes) -> None:
        weapon = save_data.find(b"WeaponMaintenanceEntry") + 0x2C

        WEAPON_SIZE = 0xD9
        OFFSET_WEAPON_XP = 0x6E
        OFFSET_WEAPON_LEVEL = 0x95
        OFFSET_WEAPON_LEVEL_UP = 0xCA

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

                Stats.weapons[weapon] = [xp, level, levelup]
                weapon += WEAPON_SIZE
        except UnicodeDecodeError:
            print("Missing weapon data")
            return

    @staticmethod
    def get_initial_stats(save_bytes: bytes) -> None:
        Stats.get_dwarf_xp(save_bytes)
        Stats.get_resources(save_bytes)
        Stats.get_misc(save_bytes)
        Stats.get_seasons(save_bytes)
        Stats.get_weapons(save_bytes)

    @staticmethod
    def get_overclocks(save_data: bytes) -> None:
        search_term = b"ForgedSchematics"
        search_end = b"SkinFixupCounter"
        start = save_data.find(search_term)
        end = save_data.find(search_end)
        if end == -1:
            search_end = b"bFirstSchematicMessageShown"
            end = save_data.find(search_end)

        for i in Stats.guid_dict.values():
            i["status"] = "UNACQUIRED"

            if start > 0:
                oc_data = save_data[start:end]
                oc_list_offset = 141

                # print(f'pos: {pos}, end_pos: {end_pos}')
                # print(f'owned_pos: {owned}, diff: {owned-pos}')
                # has_unforged = True if oc_data.find(b'Owned') else False
                has_unforged: bool = oc_data.find(b"Owned") > 0
                # print(has_unforged) # bool
                num_forged: int = struct.unpack(
                    "i", save_data[start + 63 : start + 67]
                )[0]
                # print(num_forged)

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
                        Stats.guid_dict[uuid]["status"] = "FORGED"
                        Stats.overclocks.append(
                            Overclock(
                                dwarf=Stats.guid_dict[uuid]["dwarf"],
                                weapon=Stats.guid_dict[uuid]["weapon"],
                                name=Stats.guid_dict[uuid]["name"],
                                guid=uuid,
                                status=Stats.guid_dict[uuid]["status"],
                                cost=Stats.guid_dict[uuid]["cost"],
                            )
                        )
                    except:
                        pass

                # print('after forged extraction')
                if has_unforged:
                    num_pos = save_data.find(b"Owned", start) + 62
                    num_unforged = struct.unpack("i", save_data[num_pos : num_pos + 4])[
                        0
                    ]
                    unforged_pos = num_pos + 77
                    for j in range(num_unforged):
                        uuid = (
                            save_data[
                                unforged_pos + (j * 16) : unforged_pos + (j * 16) + 16
                            ]
                            .hex()
                            .upper()
                        )
                        try:
                            Stats.guid_dict[uuid]["status"] = "UNFORGED"
                            Stats.overclocks.append(
                                Overclock(
                                    dwarf=Stats.guid_dict[uuid]["class"],
                                    weapon=Stats.guid_dict[uuid]["weapon"],
                                    name=Stats.guid_dict[uuid]["name"],
                                    guid=uuid,
                                    status=Stats.guid_dict[uuid]["status"],
                                    cost=Stats.guid_dict[uuid]["cost"],
                                )
                            )
                        except KeyError:
                            Stats.guid_dict[uuid]["class"] = "Cosmetic"

    @staticmethod
    def build_oc_dict():
        oc_dict = dict()
        try:
            for oc in Stats.overclocks:
                oc_dict.update({oc.dwarf: dict()})
        except:
            pass

        try:
            for oc in Stats.overclocks:
                oc_dict[oc.dwarf].update({oc.weapon: dict()})
        except:
            pass

        try:
            for oc in Stats.overclocks:
                oc_dict[oc.dwarf][oc.weapon].update({oc.name: oc.guid})
        except:
            pass

        return oc_dict

    #     for v in Stats.guid_dict.values():
    #         try:
    #             overclocks.update({v["class"]: dict()})
    #         except:
    #             pass

    #     for v in guid_dict.values():
    #         try:
    #             overclocks[v["class"]].update({v["weapon"]: dict()})
    #         except:
    #             pass

    #     for k, v in guid_dict.items():
    #         try:
    #             overclocks[v["class"]][v["weapon"]].update({v["name"]: k})
    #         except:
    #             pass