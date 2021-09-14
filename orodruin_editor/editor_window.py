from typing import Optional

import orodruin.commands
from orodruin.component import Component
from orodruin.port.port import PortDirection
from PySide2.QtWidgets import QHBoxLayout, QWidget

from orodruin_editor.graphics_scene import GraphicsScene
from orodruin_editor.graphics_view import GraphicsView


class OrodruinEditorWindow(QWidget):
    """Window class for the orodruin editor."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
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
        """Add debug content to the scene."""
        components = []
        for i in range(2):
            command = orodruin.commands.CreateComponent(
                self.root_component.graph(), f"Component {i:0>3}"
            )
            component = command.do()
            components.append(component)

            command = orodruin.commands.CreatePort(
                self.root_component.graph(),
                component,
                "input1",
                PortDirection.input,
                int,
            )
            command.do()

            command = orodruin.commands.CreatePort(
                self.root_component.graph(),
                component,
                "input2",
                PortDirection.input,
                int,
            )
            command.do()

            command = orodruin.commands.CreatePort(
                self.root_component.graph(),
                component,
                "output",
                PortDirection.output,
                int,
            )
            command.do()

        orodruin.commands.ConnectPorts(
            self.root_component.graph(),
            components[0].output,
            components[1].input1,
        ).do()
