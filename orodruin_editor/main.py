import sys
from logging import root
from pathlib import Path

from orodruin.core.component import Component
from orodruin.core.library import LibraryManager
from PySide2.QtWidgets import QApplication

from orodruin_editor.gui.editor_window import OrodruinEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    test_library_path = (
        Path(__file__).parent.parent.parent / "orodruin" / "tests" / "TestLibrary"
    )
    LibraryManager.register_library(test_library_path)

    window = OrodruinEditorWindow()

    root_component = Component("root")
    window.components[root_component.uuid()] = root_component
    window.graphs[root_component.uuid()] = root_component.graph()
    window.set_active_scene(root_component.uuid())

    window.show()

    sys.exit(app.exec_())
