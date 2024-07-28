from helpers.datatypes import Cost


class Overclock:
    dwarf: str
    weapon: str
    name: str
    guid: str
    status: str
    cost: Cost

    def __init__(
        self,
        dwarf: str,
        weapon: str,
        name: str,
        guid: str,
        status: str,
        cost: Cost,
    ) -> None:
        self.dwarf = dwarf
        self.weapon = weapon
        self.name = name
        self.guid = guid
        self.status = status
        self.cost = cost
