import json
import os
import struct
from copy import deepcopy
from typing import Literal

from definitions import RESOURCE_GUIDS, SEASON_GUIDS
from helpers.enums import Dwarf, Resource
from helpers.overclock import Overclock, Cost


class Parser:
    def load_into_state_manager(self, save_bytes: bytes, state_manager) -> None:
        self.get_season_data(save_bytes, state_manager)
        self.get_dwarf_xp(save_bytes, state_manager)
        self.get_misc(save_bytes, state_manager)
        self.get_resources(save_bytes, state_manager)
        self.get_weapons(save_bytes, state_manager)

        self.load_guid_dict(state_manager)
        self.get_overclocks(save_bytes, state_manager)

    def load_guid_dict(self, state_manager):
        guids_file = "guids.json"

        # check if the guid file exists in the current working directory, if not, use the one in the same directory as the script (for pyinstaller)
        if not os.path.exists(guids_file):
            guids_file = os.path.join(os.path.dirname(__file__), guids_file)

        # load reference data
        with open(guids_file, "r", encoding="utf-8") as g:
            state_manager.guid_dict = json.loads(g.read())

    def get_one_season_data(
        self, save_bytes: bytes, season_guid: str
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

    def get_season_data(self, save_bytes: bytes, state_manager):
        for season, guid in SEASON_GUIDS.items():
            try:
                state_manager.season_data[season] = self.get_one_season_data(save_bytes, guid)
            except ValueError:
                print(f"Season {season} missing")

    def get_dwarf_xp(self, save_bytes: bytes, state_manager) -> None:
        markers = {
            Dwarf.ENGINEER: b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50",
            Dwarf.SCOUT: b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50",
            Dwarf.DRILLER: b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50",
            Dwarf.GUNNER: b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50",
        }
        for dwarf, marker in markers.items():
            xp, num_promo = self.get_one_dwarf_xp(save_bytes, marker)
            state_manager.dwarf_xp[dwarf] = xp
            state_manager.dwarf_promo[dwarf] = num_promo

    def get_one_dwarf_xp(self, save_bytes: bytes, marker: bytes):
        xp_offset = 48
        xp_pos: int = save_bytes.find(marker) + xp_offset
        xp: int = struct.unpack("i", save_bytes[xp_pos : xp_pos + 4])[0]

        num_promo_offset = 108
        num_promo: int = struct.unpack(
            "i",
            save_bytes[xp_pos + num_promo_offset : xp_pos + num_promo_offset + 4],
        )[0]

        return xp, num_promo

    def get_credits(self, save_bytes: bytes) -> int:
        marker = b"Credits"
        offset = 33
        pos = save_bytes.find(marker) + offset
        return struct.unpack("i", save_bytes[pos : pos + 4])[0]

    def get_perk_points(self, save_bytes: bytes):
        marker = b"PerkPoints"
        if save_bytes.find(marker) == -1:
            return 0

        offset = 36
        pos = save_bytes.find(marker) + offset
        value: int = struct.unpack("i", save_bytes[pos : pos + 4])[0]
        return value

    def get_misc(self, save_bytes: bytes, state_manager) -> None:
        state_manager.credits = self.get_credits(save_bytes)
        state_manager.perk_points = self.get_perk_points(save_bytes)

    def get_resources(self, save_bytes: bytes, state_manager):
        resource_guids: dict[Resource, str] = deepcopy(RESOURCE_GUIDS)
        guid_length = 16
        res_marker = b"OwnedResources"
        res_pos = save_bytes.find(res_marker)

        for k, v in resource_guids.items():
            marker = bytes.fromhex(v)
            pos = save_bytes.find(marker, res_pos) + guid_length
            end_pos = pos + 4
            unp = struct.unpack("f", save_bytes[pos:end_pos])
            state_manager.resources[k] = int(unp[0])

    def get_weapons(self, save_data: bytes, state_manager):
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

                state_manager.weapons[weapon] = [xp, level, levelup]
                weapon += WEAPON_SIZE
        except UnicodeDecodeError:
            print("Missing weapon data")

    def get_overclocks(self, save_data: bytes, state_manager) -> None:
        search_term = b"ForgedSchematics"
        start = save_data.find(search_term)
        if start == -1:
            return

        search_end = b"SkinFixupCounter"
        end = save_data.find(search_end)
        if end == -1:
            search_end = b"bFirstSchematicMessageShown"
            end = save_data.find(search_end)

        for i in state_manager.guid_dict.values():
            i["status"] = "Unacquired"

        oc_data = save_data[start:end]
        oc_list_offset = 141

        num_forged: int = struct.unpack(
            "i", save_data[start + 63 : start + 67]
        )[0]

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
                state_manager.guid_dict[uuid]["status"] = "Forged"
                self._add_overclock(uuid, state_manager)
            except KeyError:
                pass

        has_unforged: bool = oc_data.find(b"Owned") > 0
        if not has_unforged:
            return

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
                state_manager.guid_dict[uuid]["status"] = "Unforged"
                self._add_overclock(uuid, state_manager)
            except KeyError:
                # does not exist in known guids
                state_manager.overclocks.append(
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
        loaded_ocs = [x.guid for x in state_manager.overclocks]
        for uuid in state_manager.guid_dict:
            if uuid not in loaded_ocs:
                self._add_overclock(uuid, state_manager)
        print()

    def _add_overclock(self, uuid, state_manager):
        state_manager.overclocks.append(
            Overclock(
                dwarf=state_manager.guid_dict[uuid]["dwarf"],
                weapon=state_manager.guid_dict[uuid]["weapon"],
                name=state_manager.guid_dict[uuid]["name"],
                guid=uuid,
                status=state_manager.guid_dict[uuid]["status"],
                cost=state_manager.guid_dict[uuid]["cost"],
            )
        )
