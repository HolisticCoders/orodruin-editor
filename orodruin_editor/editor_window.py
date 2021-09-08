from orodruin_editor.graphics_view import QDMGraphicsView
from PySide2.QtGui import QBrush, QPen, Qt
from orodruin_editor.graphics_scene import QDMGraphicsScene
from PySide2.QtWidgets import QGraphicsItem, QGraphicsView, QVBoxLayout, QWidget
from typing import Optional


class OrodruinEditorWindow(QWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Orodruin Editor")
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # graphics scene
        self.graphics_scene = QDMGraphicsScene()

        # graphics view
        self.view = QDMGraphicsView(self.graphics_scene, self)
        self.view.setScene(self.graphics_scene)
        self.layout.addWidget(self.view)

        # self.add_debug_content()

    def add_debug_content(self):
        green_brush = QBrush(Qt.green)
        outline_pen = QPen(Qt.black)
        outline_pen.setWidth(2)

        rect = self.graphics_scene.addRect(
            -100,
            -100,
            100,
            100,
            outline_pen,
            green_brush,
        )
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.graphics_scene.addText("This is my awesome text!")
        text.setFlags(QGraphicsItem.ItemIsMovable)
