from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import orodruin.commands
from orodruin.core import PortDirection
from PySide2.QtCore import QEvent, QRectF, Qt
from PySide2.QtGui import (
    QBrush,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QWheelEvent,
)
from PySide2.QtWidgets import QGraphicsView

from orodruin_editor.gui.editor.graphics_component_name import GraphicsComponentName
from orodruin_editor.gui.editor.graphics_socket import GraphicsSocket

from .graphics_component import GraphicsComponent
from .graphics_connection import GraphicsConnection
from .graphics_port import GraphicsPort

if TYPE_CHECKING:
    from orodruin_editor.gui.editor_window import OrodruinEditorWindow

logger = logging.getLogger(__name__)


class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    def __init__(
        self,
        window: OrodruinEditorWindow,
    ) -> None:
        super().__init__(parent=window)

        self.window = window
        self.zoom_in_factor = 1.25
        self.zoom_step = 1

        self._path_font = QFont("Roboto", 20)

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

        self._temporary_connection: Optional[GraphicsConnection] = None

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
            zoom_factor = self.zoom_in_factor
        else:
            zoom_factor = 1 / self.zoom_in_factor
        self.scale(zoom_factor, zoom_factor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.pos())
        if self._temporary_connection:
            if isinstance(item, GraphicsSocket):
                self._temporary_connection.mouse_position = (
                    item.graphics_port.scene_socket_position()
                )
            elif isinstance(item, GraphicsPort):
                self._temporary_connection.mouse_position = item.scene_socket_position()
            else:
                self._temporary_connection.mouse_position = self.mapToScene(event.pos())
            self._temporary_connection.update_path()
        return super().mouseMoveEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.on_del_released(event)
        super().keyReleaseEvent(event)

    def on_left_mouse_pressed(self, event: QMouseEvent):
        """Handle left mouse button pressed event."""
        item = self.itemAt(event.pos())
        if isinstance(item, GraphicsSocket):
            if item.port().direction() == PortDirection.output:
                self._temporary_connection = GraphicsConnection(
                    source_graphics_port=item.graphics_port,
                    target_graphics_port=None,
                )
            else:
                self._temporary_connection = GraphicsConnection(
                    source_graphics_port=None,
                    target_graphics_port=item.graphics_port,
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

        if isinstance(item, (GraphicsSocket, GraphicsPort)):
            if self._temporary_connection:
                if self._temporary_connection.source_graphics_port:
                    source = self._temporary_connection.source_graphics_port.port()
                    target = item.port()
                else:
                    source = item.port()
                    target = self._temporary_connection.target_graphics_port.port()

                connect_port_command = orodruin.commands.ConnectPorts(
                    self.window.active_scene.graph,
                    source,
                    target,
                    force=True,
                )
                try:
                    connect_port_command.do()
                except Exception as e:
                    logger.warning(e)
        elif isinstance(item, GraphicsComponentName):
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

        if item is None:
            parent_component = (
                self.window.active_scene.graph.parent_component().parent_component()
            )
            if parent_component:
                self.window.set_active_scene(parent_component)
        elif isinstance(item, GraphicsComponent):
            self.window.set_active_scene(item.component)
        elif isinstance(item, GraphicsPort):
            # We picked up on the graphics port but actually want its component
            self.window.set_active_scene(item.graphics_component().component)
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
        for item in selected_items:
            if isinstance(item, GraphicsComponent):
                orodruin.commands.DeleteComponent(
                    self.window.active_scene.graph,
                    item.uuid(),
                ).do()
            if isinstance(item, GraphicsConnection):
                orodruin.commands.DisconnectPorts(
                    self.window.active_scene.graph,
                    item.source_graphics_port.port(),
                    item.target_graphics_port.port(),
                ).do()

    def drawForeground(
        self,
        painter: QPainter,
        rect: QRectF,  # pylint: disable=unused-argument
    ) -> None:
        """Draw Path of the currently active component"""
        area = self.mapToScene(self.viewport().geometry()).boundingRect()

        path_name = QPainterPath()
        path_name.addText(
            area.x() + 25,
            area.y() + 40,
            self._path_font,
            str(self.scene().graph.parent_component().path()),
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.darkGray))
        painter.drawPath(path_name)
