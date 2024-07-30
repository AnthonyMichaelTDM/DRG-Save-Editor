from enum import Enum, StrEnum, auto


class Dwarf(StrEnum):
    DRILLER = "Driller"
    GUNNER = "Gunner"
    SCOUT = "Scout"
    ENGINEER = "Engineer"


class Resource(Enum):
    BISMOR = auto()
    ENOR = auto()
    JADIZ = auto()
    CROPPA = auto()
    MAGNITE = auto()
    UMANITE = auto()
    YEAST = auto()
    MALT = auto()
    STARCH = auto()
    BARLEY = auto()
    ERROR = auto()
    CORES = auto()
    DATA = auto()
    PHAZ = auto()


class Category(StrEnum):
    """Type of overclock"""
    COSMETIC_BEARD = "Cosmetic - Beard"
    COSMETIC_HEADWEAR = "Cosmetic - Headwear"
    COSMETIC_MUSTACHE = "Cosmetic - Moustache"
    COSMETIC_SIDEBURNS = "Cosmetic - Sideburns"
    VICTORY_MOVES = "Victory Moves"
    WEAPONS = "Weapons"
    WEAPON_SKINS = "Weapon Skins"
    UNKNOWN = "Unknown"


class Status(StrEnum):
    """Status of an overclock"""
    UNACQUIRED = "Unacquired"
    UNFORGED = "Unforged"
    FORGED = "Forged"
