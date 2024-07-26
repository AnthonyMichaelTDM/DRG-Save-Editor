from typing import Dict
from dataclasses import dataclass


@dataclass
class Cost:
    credits: int
    bismor: int
    croppa: int
    enor: int
    jadiz: int
    magnite: int
    umanite: int


@dataclass
class Item:
    dwarf: str
    weapon: str
    name: str
    cost: Cost
    status: str
