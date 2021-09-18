from pathlib import Path
from typing import Dict, Optional
from uuid import UUID

import orodruin.commands
from orodruin.core import Component, LibraryManager, PortDirection
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDockWidget, QMainWindow, QWidget

from .editor.component_list_view import ComponentListView
from .editor.graphics_scene import GraphicsScene
from .editor.graphics_view import GraphicsView
from .models.component_list_model import ComponentListModel


class OrodruinEditorWindow(QMainWindow):
    """Window class for the orodruin editor."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle("Orodruin Editor")
        self.setGeometry(200, 200, 800, 600)

        self._scenes: Dict[UUID, GraphicsScene] = {}
        self.active_scene: GraphicsScene = None

        LibraryManager.register_library(
            Path(__file__).parent.parent.parent.parent  # 🙃
            / "orodruin"
            / "tests"
            / "TestLibrary"
        )

        # graphics view
        self.view = GraphicsView(self)
        self.setCentralWidget(self.view)

        dock = QDockWidget("Component List", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        component_list = ComponentListView(self, dock)
        component_list.setModel(ComponentListModel())
        dock.setWidget(component_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        root_component = Component("root")
        self.set_active_scene(root_component)
        # self.add_debug_content()

    def add_debug_content(self):
        """Add debug content to the scene."""
        components = []
        for i in range(2):
            command = orodruin.commands.CreateComponent(
                self.active_scene.graph, f"Component {i:0>3}"
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

    def set_active_scene(self, component: Component):
        """Set the component's graph as the active scene."""
        scene = self._scenes.get(component.uuid(), None)
        if not scene:
            scene = GraphicsScene(self, component.graph())
            self._scenes[component.uuid()] = scene
        self.active_scene = scene
        self.view.setScene(self.active_scene)
