import json
import os
from typing import Literal

from core.file_parser import Parser
from helpers.enums import Dwarf, Resource, Category, Status
from helpers.overclock import Overclock
from helpers.datatypes import Item, OcData


class Stats:
    def __init__(self) -> None:
        self.dwarf_xp: dict[Dwarf, int] = {}
        self.dwarf_promo: dict[Dwarf, int] = {}
        self.season_data: dict[int, dict[Literal["xp", "scrip"], int]] = {}
        self.resources: dict[Resource, int] = {}
        self.credits: int = -1
        self.perk_points: int = -1
        self.weapons: dict[int, list[int | bool]] = {}
        self.guid_dict: dict[str, Item] = {}
        self.overclocks: list[Overclock] = []

    def parse_data(self, save_data: bytes):
        self.season_data = Parser.get_season_data(save_data)
        self.dwarf_xp, self.dwarf_promo = Parser.get_dwarf_xp(save_data)
        self.credits = Parser.get_credits(save_data)
        self.perk_points = Parser.get_perk_points(save_data)
        self.resources = Parser.get_resources(save_data)
        self.weapons = Parser.get_weapons(save_data)

        self.load_guid_dict()
        self.overclocks = Parser.get_overclocks(save_data, self.guid_dict)

    def get_max_promo(self):
        return max(self.dwarf_promo.values())

    def load_guid_dict(self):
        guids_file = "guids.json"

        # check if the guid file exists in the current working directory, if not, use the one in the same directory as the script (for pyinstaller)
        if not os.path.exists(guids_file):
            guids_file = os.path.join(os.path.dirname(__file__), guids_file)

        # load reference data
        with open(guids_file, "r", encoding="utf-8") as g:
            data = json.loads(g.read())
            data_reshaped = self._reshape_guid_data(data)
            self.guid_dict = {
                key: Item(**value) for key, value in data_reshaped.items()
            }

    @staticmethod
    def _reshape_guid_data(data: dict):
        new_data = {}
        for k, v in data[Category.WEAPONS.value].items():
            new_data[k] = {
                "category": Category.WEAPONS,
                "dwarf": Dwarf[v["dwarf"].upper()],
                "name": v["name"],
                "cost": v.get("cost"),
                "weapon": v.get("weapon"),
            }
        for k, v in data[Category.MINERAL_CONTAINERS.value].items():
            new_data[k] = {
                "category": Category.MINERAL_CONTAINERS,
                "dwarf": "",
                "name": v["name"]
            }
        for category_name in data.keys():
            if category_name != Category.WEAPONS and category_name != Category.MINERAL_CONTAINERS:
                for k, v in data[category_name].items():
                    new_data[k] = {
                        "category": Category(category_name),
                        "dwarf": Dwarf[v["dwarf"].upper()],
                        "name": v["name"],
                        "cost": v.get("cost"),
                        "weapon": v.get("weapon"),
                    }
        return new_data

    def build_oc_data(self) -> OcData:
        oc_data = OcData()
        for guid, item in self.guid_dict.items():
            oc_data.add_oc(item, guid)

        return oc_data

    def get_unforged_overclocks(self):
        return [x for x in self.overclocks if x.status is Status.UNFORGED]

    def get_unacquired_overclocks(self):
        return [x.guid for x in self.overclocks if x.status == Status.UNACQUIRED]

    def set_overclocks_to_unacquired(self, guids: list[str]):
        for i, oc in enumerate(self.overclocks):
            if oc.guid in guids:
                self.overclocks[i].status = Status.UNACQUIRED

    def set_overclocks_to_unforged(self, guids: list[str]):
        for i, oc in enumerate(self.overclocks):
            if oc.guid in guids:
                self.overclocks[i].status = Status.UNFORGED
