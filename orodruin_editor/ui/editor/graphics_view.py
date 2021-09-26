from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import orodruin.commands
from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QFont, QKeyEvent, QMouseEvent, QPainter, QWheelEvent
from PySide2.QtWidgets import QGraphicsView, QWidget

from .graphics_items.graphics_node import GraphicsNode

if TYPE_CHECKING:
    from .graphics_state import GraphicsState


@dataclass
class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    _parent: Optional[QWidget] = None

    _graphics_state: GraphicsState = field(init=False)

    _zoom_in_factor: float = field(init=False, default=1.25)
    _font_family: str = field(init=False, default="Roboto")
    _font_size: int = field(init=False, default=20)
    _path_font: QFont = field(init=False)

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

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.on_del_released(event)
        elif event.key() == Qt.Key_G and event.modifiers() == Qt.ControlModifier:
            self.on_control_g_released(event)
        else:
            super().keyReleaseEvent(event)

    def on_left_mouse_pressed(self, event: QMouseEvent):
        """Handle left mouse button pressed event."""
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
        super().mouseReleaseEvent(event)

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
        # elif isinstance(item, GraphicsPort):
        #     # We picked up on the graphics port but actually want its component
        #     component = self.window.components[item.graphics_component().uuid()]
        #     self.window.set_active_scene(component.graph().uuid())
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
            if isinstance(item, GraphicsNode):
                orodruin.commands.DeleteNode(
                    self._graphics_state.state(),
                    item.uuid(),
                ).do()
            # if isinstance(item, GraphicsConnection):
            #     source = self.window.ports.get(item.source_graphics_port.uuid())
            #     target = self.window.ports.get(item.target_graphics_port.uuid())

            #     # The connection might have already been deleted
            #     # when its source or target was deleted
            #     if not source or not target:
            #         continue

            #     orodruin.commands.DisconnectPorts(
            #         self.window.active_scene.graph(),
            #         source,
            #         target,
            #     ).do()

    def on_control_g_released(self, event: QKeyEvent):
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
