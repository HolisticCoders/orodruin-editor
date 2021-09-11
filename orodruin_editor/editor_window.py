from typing import Optional

import orodruin.command
from orodruin.component import Component
from orodruin.port.port import PortDirection
from PySide2.QtWidgets import QHBoxLayout, QWidget

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

        self.root_component = Component("root")

        # scene
        self.graphics_scene = GraphicsScene(self.root_component.graph())

        # graphics view
        self.view = GraphicsView(self.graphics_scene, self)
        self.layout.addWidget(self.view)

        self.add_debug_content()

    def add_debug_content(self):
        for i in range(2):
            command = orodruin.command.CreateComponent(
                self.root_component.graph(), f"Component {i:0>3}"
            )
            command.do()

            component = list(self.root_component.graph().components().values())[-1]

            command = orodruin.command.CreatePort(
                self.root_component.graph(),
                component,
                "input 1",
                PortDirection.input,
                int,
            )
            command.do()

            command = orodruin.command.CreatePort(
                self.root_component.graph(),
                component,
                "input 2",
                PortDirection.input,
                int,
            )
            command.do()

            command = orodruin.command.CreatePort(
                self.root_component.graph(),
                component,
                "output",
                PortDirection.output,
                int,
            )
            command.do()

        port = list(self.root_component.graph().ports().values())[-1]
        command = orodruin.command.DeletePort(
            self.root_component.graph(),
            port.uuid(),
        )
        command.do()
        command.undo()
