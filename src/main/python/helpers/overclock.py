from dataclasses import dataclass

from helpers.datatypes import Cost, Dwarf, Category, Status


@dataclass
class Overclock:
    category: Category
    dwarf: Dwarf
    weapon: str
    name: str
    guid: str
    status: Status
    cost: Cost
