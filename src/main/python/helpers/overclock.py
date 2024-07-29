from dataclasses import dataclass

from helpers.datatypes import Cost


@dataclass
class Overclock:
    dwarf: str
    weapon: str
    name: str
    guid: str
    status: str
    cost: Cost
