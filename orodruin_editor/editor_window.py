from typing import Optional

from orodruin.component import Component
from orodruin.port.port import Port, PortDirection
from PySide2.QtGui import QBrush, QPen, Qt
from PySide2.QtWidgets import QGraphicsItem, QHBoxLayout, QListView, QWidget

from orodruin_editor.graphics_connection import GraphicsConnection
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

        self.root_component = Component.new("root")

        # scene
        self.graphics_scene = GraphicsScene(self.root_component)

        # graphics view
        self.view = GraphicsView(self.graphics_scene, self)
        self.layout.addWidget(self.view)

        self.add_debug_content()

    def add_debug_content(self):
        component = Component.new(f"Multiply")
        component.add_port("input1", PortDirection.input, float)
        component.add_port("input2", PortDirection.input, float)
        component.add_port("output", PortDirection.output, float)
        component.set_parent(self.root_component)

        connection = GraphicsConnection()
        self.graphics_scene.addItem(connection)
