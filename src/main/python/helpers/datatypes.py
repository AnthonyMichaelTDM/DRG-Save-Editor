from dataclasses import dataclass, field

from helpers.enums import Category, Dwarf, Status


@dataclass
class Cost:
    """Crafting cost associated with a forgeable item"""

    credits: int = 0
    bismor: int = 0
    croppa: int = 0
    enor: int = 0
    jadiz: int = 0
    magnite: int = 0
    umanite: int = 0

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

    category: Category
    dwarf: Dwarf
    name: str
    cost: dict = field(default_factory=dict)
    weapon: str | None = None
    status: Status = Status.UNACQUIRED


@dataclass
class OcData:
    """Data structure used to store the data rendered in the overclock tree(s)"""

    # dict[Dwarf][weapon][overclock_name] = guid
    weapon: dict[Dwarf, dict[str, dict[str, str]]] = field(
        default_factory=lambda: {
            Dwarf.DRILLER: {},
            Dwarf.ENGINEER: {},
            Dwarf.GUNNER: {},
            Dwarf.SCOUT: {},
        }
    )
    # dict[name] = guid
    mineral_containers: dict[str, str] = field(default_factory=dict)
    # dict[Category][overclock_name][Dwarf] = guid
    other: dict[Category, dict[str, dict[Dwarf, str]]] = field(default_factory=dict)

    def add_oc(self, oc: Item, guid: str) -> None:
        match oc.category:
            case Category.WEAPONS:
                if not oc.weapon:
                    return
                if oc.weapon not in self.weapon[oc.dwarf]:
                    self.weapon[oc.dwarf][oc.weapon] = {}
                self.weapon[oc.dwarf][oc.weapon][oc.name] = guid
            case Category.MINERAL_CONTAINERS:
                self.mineral_containers[oc.name] = guid
            case _:
                if oc.category not in self.other:
                    self.other[oc.category] = {}
                if oc.name not in self.other[oc.category]:
                    self.other[oc.category][oc.name] = {}
                self.other[oc.category][oc.name][oc.dwarf] = guid
