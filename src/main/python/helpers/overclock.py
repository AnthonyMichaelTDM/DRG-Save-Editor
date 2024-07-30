from dataclasses import dataclass
from typing import Literal

from helpers.datatypes import Cost


@dataclass
class Overclock:
    category: Literal["Weapon", "Cosmetic", "Unknown"]
    dwarf: str
    weapon: str
    name: str
    guid: str
    status: str
    cost: Cost
