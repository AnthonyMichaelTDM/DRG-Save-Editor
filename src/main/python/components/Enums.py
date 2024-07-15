from enum import Enum


class Dwarf(Enum):
    DRILLER = 0
    GUNNER = 1
    SCOUT = 2
    ENGINEER = 3


class Minerals(Enum):
    BISMOR = 0
    ENOR = 1
    JADIZ = 2
    CROPPA = 3
    MAGNITE = 4
    UMANITE = 5


class Brewing(Enum):
    YEAST = 0
    MALT = 1
    STARCH = 2
    BARLEY = 3
