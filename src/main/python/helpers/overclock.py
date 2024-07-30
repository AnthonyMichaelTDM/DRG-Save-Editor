from dataclasses import dataclass
from typing import Literal

from helpers.datatypes import Cost


@dataclass
class Overclock:
    type_: Literal["weapon", "cosmetic", "invalid"]
    dwarf: str
    weapon: str
    name: str
    guid: str
    status: str
    cost: Cost
