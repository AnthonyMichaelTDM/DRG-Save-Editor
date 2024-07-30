from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass
class Cost:
    """Crafting cost associated with a forgeable item"""
    credits: Optional[int] = 0
    bismor: Optional[int] = 0
    croppa: Optional[int] = 0
    enor: Optional[int] = 0
    jadiz: Optional[int] = 0
    magnite: Optional[int] = 0
    umanite: Optional[int] = 0

    def __add__(self, other):
        newcost = Cost()
        for key in self.__dict__.keys():
            try:
                newcost.__dict__[key] = self.__dict__[key] + other.__dict__[key]
            except KeyError:
                pass
        return newcost


@dataclass()
class Item:
    """An item read from the known list of GUIDs"""

    category: Literal["Weapon", "Cosmetic"]
    dwarf: str
    name: str
    cost: dict = field(default_factory=dict)
    weapon: str | None = None
    status: str = "Unacquired"
