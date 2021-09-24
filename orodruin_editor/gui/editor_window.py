from typing import Optional

from orodruin.core import Scene
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
        scene: Scene,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle("Orodruin Editor")
        self.setGeometry(200, 200, 1280, 720)

        # graphics view
        self.view = GraphicsView(self)
        self.setCentralWidget(self.view)

        self._graphics_scene = GraphicsScene(scene, self.view)
        self.view.set_graphics_scene(self._graphics_scene)

        dock = QDockWidget("Component List", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        component_list = ComponentListView(self._graphics_scene, dock)
        component_list.setModel(ComponentListModel())
        dock.setWidget(component_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
