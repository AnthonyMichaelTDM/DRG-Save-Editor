from src.main.python.core.view import EditorUI
from src.main.python.core.controller import Controller
from src.main.python.core.state_manager import Stats

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QCoreApplication, Qt

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)


def test_load_save(qtbot, save_data):
    stats = Stats()
    stats.parse_data(save_data)

    widget = EditorUI()
    controller = Controller(widget, stats)  # type: ignore[arg-type]
    controller.setup(save_data)

    # can add overclocks
    assert controller.widget.overclock_tree.topLevelItemCount() == 8
    assert controller.widget.add_cores_button.isEnabled()
    assert controller.widget.unforged_list.count() == 18

    # all textboxes are filled
    for _, element in controller.widget.__dict__.items():
        if isinstance(element, QLineEdit):
            assert element.text()


def test_modify_overclocks(qtbot, save_data):
    stats = Stats()
    stats.parse_data(save_data)

    widget = EditorUI()
    controller = Controller(widget, stats)  # type: ignore[arg-type]
    controller.setup(save_data)

    assert controller.widget.unforged_list.count() == 18

    # modify overclocks
    controller.remove_all_ocs()
    assert controller.widget.unforged_list.count() == 0

    tree = controller.widget.overclock_tree
    # navigate down one branch of the tree until there is a selectable item
    parent = tree.topLevelItem(0)
    assert parent is not None, "Top level item should not be None"
    while parent and parent.childCount() > 0:
        parent = parent.child(0)
    # select the item
    tree.setCurrentItem(parent)

    controller.add_cores()
    assert controller.widget.unforged_list.count() == 1
