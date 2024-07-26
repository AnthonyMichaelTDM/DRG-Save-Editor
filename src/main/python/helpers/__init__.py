from typing import Literal


class Overclock:
    state: Literal["UNFORGED", "FORGED", "AQUIRED"]
    guid: str
