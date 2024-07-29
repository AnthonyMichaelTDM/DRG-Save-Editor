# This module contains tests for issue #97: Can't change current season value
# which was caused by the offsets used when reading save data in the edge case that the user has only one season in their save data.

from src.main.python.core.state_manager import Stats
import pytest


@pytest.fixture
def save_data_issue97():
    filepath = "tests/sample_missing_all_but_one_season.sav"
    with open(filepath, "rb") as f:
        return f.read()


def test_parse_old_save_without_errors(save_data_issue97):
    stats = Stats()
    stats.parse_data(save_data_issue97)

    expected_season_data = {
        1: {"xp": 8228, "scrip": 2},
    }
    assert stats.season_data == expected_season_data


def test_parse_new_save_without_errors(save_data):
    stats = Stats()
    stats.parse_data(save_data)

    expected_season_data = {
        2: {"xp": 3250, "scrip": 0},
        3: {"xp": 0, "scrip": 0},
        5: {"xp": 238581, "scrip": 0},
    }
    assert stats.season_data == expected_season_data
