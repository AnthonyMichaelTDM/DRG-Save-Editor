from typing import Literal


class Overclock:
    state: Literal["Unforged", "Forged", "Unacquired"]
    guid: str
