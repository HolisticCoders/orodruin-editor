from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

import orodruin.commands
from orodruin.core.port.port import PortDirection
from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import (
    QContextMenuEvent,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PySide2.QtWidgets import (
    QGraphicsTextItem,
    QGraphicsView,
    QInputDialog,
    QMenu,
    QWidget,
)

from orodruin_editor.ui.editor.dialogs.create_port_dialog import CreatePortDialog
from orodruin_editor.ui.editor.graphics_items.graphics_node_name import GraphicsNodeName

from .graphics_items.graphics_connection import GraphicsConnection
from .graphics_items.graphics_node import GraphicsNode
from .graphics_items.graphics_port import GraphicsPort
from .graphics_items.graphics_socket import GraphicsSocket

if TYPE_CHECKING:
    from .graphics_state import GraphicsState


logger = logging.getLogger(__name__)


@dataclass
class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    _parent: Optional[QWidget] = None

    _graphics_state: GraphicsState = field(init=False)

    _zoom_in_factor: float = field(init=False, default=1.25)
    _font_family: str = field(init=False, default="Roboto")
    _font_size: int = field(init=False, default=20)
    _path_font: QFont = field(init=False)

    _temporary_connection: Optional[GraphicsConnection] = field(
        init=False, default=None
    )

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self._path_font = QFont(self._font_family, self._font_size)

        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def graphics_state(self) -> GraphicsState:
        return self._graphics_state

    def set_graphics_state(self, state: GraphicsState):
        self._graphics_state = state

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.on_left_mouse_pressed(event)
        elif event.button() == Qt.RightButton:
            self.on_right_mouse_pressed(event)
        elif event.button() == Qt.MiddleButton:
            self.on_middle_mouse_pressed(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.on_left_mouse_released(event)
        elif event.button() == Qt.RightButton:
            self.on_right_mouse_released(event)
        elif event.button() == Qt.MiddleButton:
            self.on_middle_mouse_released(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.on_left_mouse_double_clicked(event)
        elif event.button() == Qt.RightButton:
            self.on_right_mouse_double_clicked(event)
        elif event.button() == Qt.MiddleButton:
            self.on_middle_mouse_double_clicked(event)

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            zoom_factor = self._zoom_in_factor
        else:
            zoom_factor = 1 / self._zoom_in_factor
        self.scale(zoom_factor, zoom_factor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if self._temporary_connection:
            if isinstance(item, GraphicsSocket):
                self._temporary_connection.mouse_position = (
                    item._graphics_port.scene_socket_position()
                )
            elif isinstance(item, GraphicsPort):
                self._temporary_connection.mouse_position = item.scene_socket_position()
            else:
                self._temporary_connection.mouse_position = self.mapToScene(event.pos())
            self._temporary_connection.update_path()
        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_G and event.modifiers() == Qt.ControlModifier:
            self.on_control_g_pressed(event)
        else:
            return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.on_del_released(event)
        else:
            super().keyReleaseEvent(event)

    def on_left_mouse_pressed(self, event: QMouseEvent):
        """Handle left mouse button pressed event."""
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if isinstance(item, GraphicsSocket):
            if item.direction() == PortDirection.output:
                source = item._graphics_port
                target = None
            else:
                source = None
                target = item._graphics_port
            self._temporary_connection = GraphicsConnection(
                self._graphics_state,
                uuid4(),
                _source_graphics_port=source,
                _target_graphics_port=target,
            )
            self._temporary_connection.mouse_position = self.mapToScene(event.pos())
            self.scene().addItem(self._temporary_connection)
        else:
            super().mousePressEvent(event)

    def on_right_mouse_pressed(self, event: QMouseEvent):
        """Handle right mouse button pressed event."""
        super().mousePressEvent(event)

    def on_middle_mouse_pressed(self, event: QMouseEvent):
        """Handle middle mouse button pressed event."""
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        press_event = QMouseEvent(
            QEvent.MouseButtonPress,
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            Qt.NoButton,
            event.modifiers(),
        )
        self.mousePressEvent(press_event)

    def on_left_mouse_released(self, event: QMouseEvent):
        """Handle left mouse button released event."""
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if isinstance(item, (GraphicsSocket, GraphicsPort)):
            if self._temporary_connection:
                if self._temporary_connection.source_graphics_port():
                    source_id = self._temporary_connection.source_graphics_port().uuid()
                    target_id = item.uuid()
                else:
                    source_id = item.uuid()
                    target_id = self._temporary_connection.target_graphics_port().uuid()

                connect_port_command = orodruin.commands.ConnectPorts(
                    self._graphics_state.state(),
                    self._graphics_state.active_graph().uuid(),
                    source_id,
                    target_id,
                    force=True,
                )
                try:
                    connect_port_command.do()
                except Exception as e:
                    logger.error(e)
        elif isinstance(item, GraphicsNodeName):
            item.init_rename()
        super().mouseReleaseEvent(event)

        if self._temporary_connection:
            self.scene().removeItem(self._temporary_connection)
            self._temporary_connection = None

    def on_right_mouse_released(self, event: QMouseEvent):
        """Handle right mouse button released event."""
        super().mouseReleaseEvent(event)

    def on_middle_mouse_released(self, event: QMouseEvent):
        """Handle middle mouse button released event."""
        fake_event = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() & ~Qt.LeftButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def on_left_mouse_double_clicked(self, event: QMouseEvent):
        """Handle left mouse button double click event."""
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if item is None:
            graphics_graph = self._graphics_state.active_graph()
            graph = self._graphics_state.get_graph(graphics_graph)
            node = graph.parent_node()
            if node:
                parent_graph = node.parent_graph()
                if parent_graph:
                    self._graphics_state.set_active_graph(parent_graph)
        elif isinstance(item, GraphicsNode):
            node = self._graphics_state.get_node(item.uuid())
            graphics_graph = self._graphics_state.get_graphics_graph(node.graph())
            self._graphics_state.set_active_graph(graphics_graph)
        elif isinstance(item, GraphicsPort):
            if item.child_ports_layout().isVisible():
                item.child_ports_layout().hide()
            else:
                item.child_ports_layout().show()
        else:
            super().mouseDoubleClickEvent(event)

    def on_right_mouse_double_clicked(self, event: QMouseEvent):
        """Handle right mouse button double click event."""
        super().mouseDoubleClickEvent(event)

    def on_middle_mouse_double_clicked(self, event: QMouseEvent):
        """Handle middle mouse button double click event."""
        super().mouseDoubleClickEvent(event)

    def on_del_released(self, event: QKeyEvent):
        """Handle del key released event."""
        selected_items = self.scene().selectedItems()
        selected_nodes = [
            item for item in selected_items if isinstance(item, GraphicsNode)
        ]
        selected_connections = [
            item for item in selected_items if isinstance(item, GraphicsConnection)
        ]
        for graphics_connection in selected_connections:
            orodruin.commands.DisconnectPorts(
                self._graphics_state.state(),
                self._graphics_state.active_graph().uuid(),
                graphics_connection.source_graphics_port().uuid(),
                graphics_connection.target_graphics_port().uuid(),
            ).do()

        for graphics_node in selected_nodes:
            if isinstance(graphics_node, GraphicsNode):
                orodruin.commands.DeleteNode(
                    self._graphics_state.state(),
                    graphics_node.uuid(),
                ).do()

    def on_control_g_pressed(self, event: QKeyEvent):
        """Handle control-g released event."""
        selected_items = self.scene().selectedItems()
        selected_nodes_ids = [
            item.uuid() for item in selected_items if isinstance(item, GraphicsNode)
        ]

        orodruin.commands.GroupNodes(
            self._graphics_state.state(),
            self._graphics_state.active_graph().uuid(),
            selected_nodes_ids,
        ).do()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        item = self.itemAt(event.pos())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if isinstance(item, GraphicsNode):
            self.on_node_context_menu_event(item, event)
        elif isinstance(item, GraphicsPort):
            self.on_port_context_menu_event(item, event)
        return super().contextMenuEvent(event)

    def on_node_context_menu_event(
        self,
        graphics_node: GraphicsPort,
        event: QContextMenuEvent,
    ):
        """Create the port context menu."""
        context_menu = QMenu(self)
        create_port_action = context_menu.addAction("Create Port")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == create_port_action:
            self.on_create_port(graphics_node)

    def on_port_context_menu_event(
        self,
        graphics_port: GraphicsPort,
        event: QContextMenuEvent,
    ):
        """Create the port context menu."""
        context_menu = QMenu(self)
        rename_port_action = context_menu.addAction("Rename Port")
        delete_port_action = context_menu.addAction("Delete Port")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == rename_port_action:
            self.on_rename_port(graphics_port)
        elif action == delete_port_action:
            self.on_delete_port(graphics_port)

    def on_create_port(self, graphics_node: GraphicsNode):

        create_port_dialog = CreatePortDialog()
        return_code = create_port_dialog.exec_()

        if return_code:
            name = create_port_dialog.port_name()
            direction = create_port_dialog.port_direction()
            port_type = create_port_dialog.port_type()
            orodruin.commands.CreatePort(
                self._graphics_state.state(),
                graphics_node.uuid(),
                name,
                direction,
                port_type,
            ).do()

    def on_rename_port(self, graphics_port: GraphicsPort):
        """Rename the port."""
        port = self._graphics_state.state().port_from_portlike(graphics_port.uuid())

        rename_port_dialog = QInputDialog()
        rename_port_dialog.setWindowTitle("Rename Port")
        rename_port_dialog.setLabelText("Enter New Port Name")
        rename_port_dialog.setTextValue(port.name())

        return_code = rename_port_dialog.exec_()

        if return_code:
            new_name = rename_port_dialog.textValue()
            orodruin.commands.RenamePort(
                self._graphics_state.state(),
                port,
                new_name,
            ).do()

    def on_delete_port(self, graphics_port: GraphicsPort) -> None:
        orodruin.commands.DeletePort(
            self._graphics_state.state(), graphics_port.uuid()
        ).do()
