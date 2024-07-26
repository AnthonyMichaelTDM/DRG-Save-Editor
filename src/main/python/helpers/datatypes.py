from typing import TypedDict, Dict


class Cost(TypedDict):
    credits: int
    bismor: int
    croppa: int
    enor: int
    jadiz: int
    magnite: int
    umanite: int


class Item(TypedDict):
    dwarf: str
    weapon: str
    name: str
    cost: Cost
    status: str
