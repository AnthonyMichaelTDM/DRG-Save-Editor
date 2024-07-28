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
        parser = Parser()
        parser.load_into_state_manager(save_data, self)

    def build_oc_dict(self):
        oc_dict = dict()

        for _, oc in self.guid_dict.items():
            oc_dict.update({oc["dwarf"]: dict()})

        for _, oc in self.guid_dict.items():
            oc_dict[oc["dwarf"]].update({oc["weapon"]: dict()})

        for guid, oc in self.guid_dict.items():
            oc_dict[oc["dwarf"]][oc["weapon"]].update({oc["name"]: guid})

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
