import sys

from core.controller import Controller
from core.state_manager import Stats
from core.view import EditorUI

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    app = QApplication()

    state_manager = Stats()

    # load the UI
    widget: EditorUI = EditorUI()
    controller = Controller(widget, state_manager)

    # actually display the thing
    widget.show()
    exit_code = app.exec()
    sys.exit(exit_code)
