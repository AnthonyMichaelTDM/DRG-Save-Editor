from src.main.python.core.file_writer import make_save_file
from src.main.python.core.state_manager import Stats
from src.main.python.definitions import Resource


def test_saving_with_no_change(save_data: bytes):
    stats = Stats()
    stats.parse_data(save_data)
    output = make_save_file(save_data, stats)

    assert len(save_data) == len(output)
    assert output == save_data

    # make sure the new data is still parseable
    stats2 = Stats()
    stats2.parse_data(output)

    # no eq dunder for the class so do it manually
    assert stats2.dwarf_xp == stats.dwarf_xp
    assert stats2.dwarf_promo == stats.dwarf_promo
    assert stats2.season_data == stats.season_data
    assert stats2.resources == stats.resources
    assert stats2.credits == stats.credits
    assert stats2.perk_points == stats.perk_points
    assert stats2.weapons == stats.weapons
    assert stats2.guid_dict == stats.guid_dict
    assert stats2.overclocks == stats.overclocks


def test_saving_with_resource_change(save_data: bytes):
    stats = Stats()
    stats.parse_data(save_data)
    stats.resources[Resource.CORES] += 1
    output = make_save_file(save_data, stats)

    assert len(save_data) == len(output)
    assert output != save_data

    expected_diff_len = 2
    xored = bytes(a ^ b for a, b in zip(save_data, output))
    diff_len = len(save_data) - xored.count(0)

    assert diff_len == expected_diff_len

    stats2 = Stats()
    stats2.parse_data(output)

    assert stats2.resources[Resource.CORES] == stats.resources[Resource.CORES]


def test_saving_with_overclocks_change(save_data: bytes):
    stats = Stats()
    stats.parse_data(save_data)

    guid = "AF945B93A7B9D64CA6DD00683627BC80"
    stats.set_overclocks_to_unforged([guid])

    output = make_save_file(save_data, stats)

    assert len(save_data) + 16 == len(output)
    assert output != save_data

    stats2 = Stats()
    stats2.parse_data(output)

    assert stats2.get_unforged_overclocks() == stats.get_unforged_overclocks()
