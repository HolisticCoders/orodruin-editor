import sys

from PySide2.QtWidgets import QApplication

from orodruin_editor.gui.editor_window import OrodruinEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OrodruinEditorWindow()
    window.show()

    sys.exit(app.exec_())
