import cProfile
import os
import sys

from orodruin.core import State
from PySide2.QtWidgets import QApplication

from orodruin_editor.ui.window import OrodruinWindow


def to_profile() -> None:
    app = QApplication(sys.argv)

    state = State()
    window = OrodruinWindow(state)

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    cProfile.run("to_profile()", "tmp/editor.prof")
