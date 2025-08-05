from src.main.python.core.state_manager import Stats, Dwarf, Resource, Category, Status


def test_parse_without_errors(save_data: bytes):
    stats = Stats()
    stats.parse_data(save_data)

    expected_dwarf_xp = {
        Dwarf.DRILLER: 132020,
        Dwarf.GUNNER: 237569,
        Dwarf.SCOUT: 1561,
        Dwarf.ENGINEER: 6342,
    }
    assert stats.dwarf_xp == expected_dwarf_xp

    expected_dwarf_promo = {
        Dwarf.DRILLER: 1,
        Dwarf.GUNNER: 1,
        Dwarf.SCOUT: 0,
        Dwarf.ENGINEER: 0,
    }
    assert stats.dwarf_promo == expected_dwarf_promo

    expected_season_data = {
        2: {'xp': 3250, 'scrip': 0},
        3: {'xp': 0, 'scrip': 0},
        5: {'xp': 238581, 'scrip': 0},
    }
    assert stats.season_data == expected_season_data

    expected_resources = {
        Resource.YEAST: 49,
        Resource.STARCH: 129,
        Resource.BARLEY: 70,
        Resource.BISMOR: 785,
        Resource.ENOR: 343,
        Resource.MALT: 67,
        Resource.UMANITE: 823,
        Resource.JADIZ: 1698,
        Resource.CROPPA: 1977,
        Resource.MAGNITE: 261,
        Resource.ERROR: 3,
        Resource.CORES: 1,
        Resource.DATA: 1,
        Resource.PHAZ: 343,
    }
    assert stats.resources == expected_resources

    expected_credits = 60044
    assert stats.credits == expected_credits

    expected_perk_points = 2
    assert stats.perk_points == expected_perk_points

    expected_weapons = {
        67356: [1561, 0, False],
        67573: [1561, 0, False],
        67790: [66781, 6, False],
        68007: [48023, 6, False],
        68224: [6342, 0, False],
        68441: [6342, 0, False],
        68658: [0, 7, False],
        68875: [29345, 6, False],
        69092: [1970, 4, False],
        69309: [36255, 2, False],
        69526: [11606, 0, False],
        69743: [58231, 6, False],
        69960: [38621, 3, False],
        70177: [31469, 3, False]
    }
    assert stats.weapons == expected_weapons

    expected_unacquired_weapon_overclocks = 143
    expected_unacquired_overclocks = 485
    expected_unforged_overclocks = 18
    assert (
        len([
            x.guid for x in stats.overclocks
            if x.status == Status.UNACQUIRED and x.category == Category.WEAPONS
        ])
        == expected_unacquired_weapon_overclocks
    )
    assert len(stats.get_unacquired_overclocks()) == expected_unacquired_overclocks
    assert len(stats.get_unforged_overclocks()) == expected_unforged_overclocks
