import json
import os
from typing import Literal

from core.file_parser import Parser
from helpers.enums import Dwarf, Resource
from helpers.overclock import Overclock
from helpers.datatypes import Item


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

    def load_guid_dict(self):
        guids_file = "guids.json"

        # check if the guid file exists in the current working directory, if not, use the one in the same directory as the script (for pyinstaller)
        if not os.path.exists(guids_file):
            guids_file = os.path.join(os.path.dirname(__file__), guids_file)

        # load reference data
        with open(guids_file, "r", encoding="utf-8") as g:
            self.guid_dict = {
                key: Item(**value) for key, value in json.loads(g.read()).items()
            }

    def build_oc_dict(self):
        oc_dict = dict()

        for _, oc in self.guid_dict.items():
            oc_dict.update({oc.dwarf: dict()})

        for _, oc in self.guid_dict.items():
            oc_dict[oc.dwarf].update({oc.weapon: dict()})

        for guid, oc in self.guid_dict.items():
            oc_dict[oc.dwarf][oc.weapon].update({oc.name: guid})

        return oc_dict

    def get_unforged_overclocks(self):
        return [x for x in self.overclocks if x.status == "Unforged"]

    def get_unacquired_overclocks(self):
        return [x.guid for x in self.overclocks if x.status == "Unacquired"]

    def set_overclocks_to_unacquired(self, guids: list[str]):
        for i, oc in enumerate(self.overclocks):
            if oc.guid in guids:
                self.overclocks[i].status = "Unacquired"

    def set_overclocks_to_unforged(self, guids: list[str]):
        for i, oc in enumerate(self.overclocks):
            if oc.guid in guids:
                self.overclocks[i].status = "Unforged"
