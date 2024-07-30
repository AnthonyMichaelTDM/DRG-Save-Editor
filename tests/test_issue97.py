# This module contains tests for issue #97: Can't change current season value
# which was caused by the offsets used when reading save data in the edge case that the user has only one season in their save data.

import PySide6
import PySide6.QtCore
from src.main.python.core.view import EditorUI
from src.main.python.core.controller import Controller
from src.main.python.core.state_manager import Stats
import pytest


from PySide6.QtCore import QCoreApplication, Qt
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)


@pytest.fixture
def save_data_missing_seasons():
    filepath = "tests/sample_missing_all_but_one_season.sav"
    with open(filepath, "rb") as f:
        return f.read()


@pytest.fixture
def save_data_issue97():
    filepath = "tests/sample_issue97.sav"
    with open(filepath, "rb") as f:
        return f.read()


def test_parse_old_save_without_errors(save_data_missing_seasons):
    stats = Stats()
    stats.parse_data(save_data_missing_seasons)

    expected_season_data = {
        1: {"xp": 8228, "scrip": 2},
    }
    assert stats.season_data == expected_season_data


def test_parse_user_save_without_errors(save_data_issue97):
    stats = Stats()
    stats.parse_data(save_data_issue97)

    expected_season_data = {
        4: {"xp": 95893, "scrip": 0},
    }
    assert stats.season_data == expected_season_data


def test_weapon_oc_panel_disables_when_no_ocs(save_data_issue97, qtbot, save_data):
    stats = Stats()
    stats.parse_data(save_data_issue97)

    # First, make sure all OCs are marked as unacquired
    for oc in stats.overclocks:
        assert oc.status == "Unacquired"

    # Now, create the UI and controller, and run the `init_overclock_tree` method
    widget = EditorUI()
    controller = Controller(widget, stats)  # type: ignore[arg-type]
    controller.init_overclock_tree()

    # Ensure that the "No dwarf promoted yet" message is present
    assert (
        len(
            controller.widget.overclock_tree.findItems(
                "No dwarf promoted yet", PySide6.QtCore.Qt.MatchFlag.MatchExactly
            )
        )
        == 1
    )
    # Ensure that there are no other items in the tree
    assert controller.widget.overclock_tree.topLevelItemCount() == 1

    # Ensure that the "Add Cores" button is disabled
    assert not controller.widget.add_cores_button.isEnabled()


def test_ensure_oc_panel_gets_reenabled_on_new_save(
    save_data_issue97, qtbot, save_data
):
    _ = qtbot
    stats = Stats()
    stats.parse_data(save_data_issue97)

    # First, make sure all OCs are marked as unacquired
    for oc in stats.overclocks:
        assert oc.status == "Unacquired"

    # Now, create the UI and controller, and run the `init_overclock_tree` method
    widget = EditorUI()
    controller = Controller(widget, stats)  # type: ignore[arg-type]
    controller.init_overclock_tree()

    assert controller.widget.overclock_tree.topLevelItemCount() == 1
    assert not controller.widget.add_cores_button.isEnabled()

    # Ensure that if we open a new save file with OCs, the "No dwarf promoted yet" message is removed, and the "Add Cores" button is enabled
    controller.init_values(save_data)
    controller.reset_values()
    controller.update_rank()
    controller.init_overclock_tree()

    assert (
        len(
            controller.widget.overclock_tree.findItems(
                "No dwarf promoted yet", PySide6.QtCore.Qt.MatchFlag.MatchExactly
            )
        )
        == 0
    )
    assert controller.widget.add_cores_button.isEnabled()
    assert controller.widget.overclock_tree.topLevelItemCount() == 7


def test_parse_new_save_without_errors(save_data):
    stats = Stats()
    stats.parse_data(save_data)

    expected_season_data = {
        2: {"xp": 3250, "scrip": 0},
        3: {"xp": 0, "scrip": 0},
        5: {"xp": 238581, "scrip": 0},
    }
    assert stats.season_data == expected_season_data
