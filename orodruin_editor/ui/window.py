from dataclasses import dataclass, field
from typing import Optional

from orodruin.core import State
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDockWidget, QMainWindow, QWidget

from orodruin_editor.ui.editor.graphics_state import GraphicsState

from ..models.node_list_model import NodeListModel
from .editor.graphics_view import GraphicsView
from .node_list_view import NodeListView


@dataclass
class OrodruinWindow(QMainWindow):
    _state: State
    _parent: Optional[QWidget] = None

    _graphics_state: GraphicsState = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self.setWindowTitle("Orodruin Editor")
        self.setGeometry(200, 200, 1280, 720)

        self._view = GraphicsView(self)
        self.setCentralWidget(self._view)

        self._graphics_state = GraphicsState(self._state, self._view)

        dock = QDockWidget("Node List", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        node_list_model = NodeListModel()
        node_list_view = NodeListView(self._graphics_state, dock)
        node_list_view.setModel(node_list_model)
        dock.setWidget(node_list_view)
