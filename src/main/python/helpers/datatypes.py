from dataclasses import dataclass
from typing import Optional


@dataclass
class Cost:
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
    dwarf: str
    weapon: str
    name: str
    cost: Cost
    status: str
