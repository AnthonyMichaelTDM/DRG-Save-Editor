from definitions import XP_TABLE


def xp_total_to_level(xp: int) -> tuple[int, int]:
    for i in XP_TABLE:
        if xp < i:
            level: int = XP_TABLE.index(i)
            remainder: int = xp - XP_TABLE[level - 1]
            return (level, remainder)
    return (25, 0)
