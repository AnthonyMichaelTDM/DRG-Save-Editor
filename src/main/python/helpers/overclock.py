from dataclasses import dataclass
from typing import Literal

from helpers.datatypes import Cost


@dataclass
class Overclock:
    category: str
    dwarf: Literal["Driller", "Engineer", "Gunner", "Scout", ""]
    weapon: str
    name: str
    guid: str
    status: Literal["Unacquired", "Unforged", "Forged"]
    cost: Cost
