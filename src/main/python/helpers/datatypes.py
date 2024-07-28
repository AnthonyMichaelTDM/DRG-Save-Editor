from typing import TypedDict, NotRequired


class Cost(TypedDict):
    credits: NotRequired[int]
    bismor: NotRequired[int]
    croppa: NotRequired[int]
    enor: NotRequired[int]
    jadiz: NotRequired[int]
    magnite: NotRequired[int]
    umanite: NotRequired[int]


class Item(TypedDict):
    dwarf: str
    weapon: str
    name: str
    cost: Cost
    status: str
