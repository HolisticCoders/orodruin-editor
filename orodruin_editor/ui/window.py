import logging
from dataclasses import dataclass, field
from typing import Optional

import orodruin.commands
from orodruin.core import State
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QAction, QDockWidget, QMainWindow, QMenuBar, QWidget

from orodruin_editor.ui.editor.graphics_state import GraphicsState

from ..models.node_list_model import NodeListModel
from .editor.graphics_items.graphics_node import GraphicsNode
from .editor.graphics_view import GraphicsView
from .node_list_view import NodeListView

logger = logging.getLogger(__name__)


@dataclass
class OrodruinWindow(QMainWindow):
    _state: State
    _parent: Optional[QWidget] = None

    _graphics_state: GraphicsState = field(init=False)

    _view: GraphicsView = field(init=False)
    _menu_bar: QMenuBar = field(init=False)

    _export_node_action: QAction = field(init=False)
    _node_list_model: NodeListModel = field(init=False)
    _node_list_view: NodeListView = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self.setWindowTitle("Orodruin Editor")
        self.setGeometry(200, 200, 1280, 720)

        self._menu_bar = QMenuBar()
        self.setMenuBar(self._menu_bar)
        file_menu = self._menu_bar.addMenu("File")
        self._export_node_action = QAction("Export Node")
        file_menu.addAction(self._export_node_action)
        self._export_node_action.triggered.connect(self._export_node)

        self._view = GraphicsView(self)
        self.setCentralWidget(self._view)

        self._graphics_state = GraphicsState(self._state, self._view)
        self._view.set_graphics_state(self._graphics_state)

        dock = QDockWidget("Node List", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self._node_list_model = NodeListModel()
        self._node_list_view = NodeListView(self._graphics_state, dock)
        self._node_list_view.setModel(self._node_list_model)
        dock.setWidget(self._node_list_view)

    def _export_node(self):
        selection = self._view.scene().selectedItems()
        if not selection:
            logger.error("No node are selected.")
            return

        first_item = selection[0]
        if not isinstance(first_item, GraphicsNode):
            logger.error("Can't export a %s", type(first_item))
            return

        orodruin_node = self._state.node_from_nodelike(first_item.uuid())

        orodruin.commands.ExportNode(
            orodruin_node, "orodruin-library", "orodruin", orodruin_node.name()
        ).do()
        self._node_list_model.refresh_nodes_list()
