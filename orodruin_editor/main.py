import sys

from editor_window import OrodruinEditorWindow
from PySide2.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OrodruinEditorWindow()
    window.show()

    sys.exit(app.exec_())
