import sys
from pathlib import Path

from orodruin.core.component import Component
from orodruin.core.library import LibraryManager
from PySide2.QtWidgets import QApplication

from orodruin_editor.gui.editor_window import OrodruinEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OrodruinEditorWindow()
    window.show()

    LibraryManager.register_library(
        Path(__file__).parent.parent.parent / "orodruin" / "tests" / "TestLibrary"
    )

    root_component = Component("root")
    window.set_active_scene(root_component)

    sys.exit(app.exec_())
