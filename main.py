import logging
import sys
from pathlib import Path

from orodruin.core import State
from orodruin.core.library import LibraryManager
from PySide2.QtWidgets import QApplication

from orodruin_editor.ui.window import OrodruinWindow

if __name__ == "__main__":
    # logging.getLogger("orodruin").setLevel(logging.DEBUG)
    logging.getLogger("orodruin_editor").setLevel(logging.DEBUG)

    app = QApplication(sys.argv)

    test_library_path = (
        Path(__file__).parent.parent / "orodruin" / "tests" / "TestLibrary"
    )
    LibraryManager.register_library(test_library_path)

    state = State()
    window = OrodruinWindow(state)

    window.show()

    sys.exit(app.exec_())
