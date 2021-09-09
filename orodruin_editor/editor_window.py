from typing import Optional

from orodruin.component import Component
from orodruin.port.port import Port, PortDirection
from PySide2.QtGui import QBrush, QPen, Qt
from PySide2.QtWidgets import QGraphicsItem, QHBoxLayout, QListView, QWidget

from orodruin_editor.graphics_scene import GraphicsScene
from orodruin_editor.graphics_view import GraphicsView


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

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        root_component = Component.new("root")

        # scene
        self.graphics_scene = GraphicsScene(root_component)

        component = Component.new(f"Multiply")
        component.add_port("input1", PortDirection.input, float)
        component.add_port("input2", PortDirection.input, float)
        component.add_port("output", PortDirection.output, float)
        component.set_parent(root_component)

        # graphics view
        self.view = GraphicsView(self.graphics_scene, self)
        self.layout.addWidget(self.view)

    def add_debug_content(self):
        green_brush = QBrush(Qt.green)
        outline_pen = QPen(Qt.black)
        outline_pen.setWidth(2)

        rect = self.scene.graphics_scene.addRect(
            -100,
            -100,
            100,
            100,
            outline_pen,
            green_brush,
        )
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.scene.graphics_scene.addText("This is my awesome text!")
        text.setFlags(QGraphicsItem.ItemIsMovable)
