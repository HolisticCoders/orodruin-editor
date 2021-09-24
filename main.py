import logging
import sys
from pathlib import Path

from orodruin.core import Scene
from orodruin.core.library import LibraryManager
from PySide2.QtWidgets import QApplication

from orodruin_editor.gui.editor_window import OrodruinEditorWindow

if __name__ == "__main__":
    logger = logging.getLogger("orodruin_editor")
    logger.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)

    test_library_path = (
        Path(__file__).parent.parent / "orodruin" / "tests" / "TestLibrary"
    )
    LibraryManager.register_library(test_library_path)

    scene = Scene()
    window = OrodruinEditorWindow(scene)

    window.show()

    sys.exit(app.exec_())
