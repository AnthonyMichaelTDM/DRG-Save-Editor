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

    controller.init_values(save_data)
    controller.reset_values()
    controller.update_rank()
    controller.init_overclock_tree()

    # can add overclocks
    assert controller.widget.overclock_tree.topLevelItemCount() == 7
    assert controller.widget.add_cores_button.isEnabled()
    assert controller.widget.unforged_list.count() == 18

    # all textboxes are filled
    for _, element in controller.widget.__dict__.items():
        if isinstance(element, QLineEdit):
            assert element.text()
