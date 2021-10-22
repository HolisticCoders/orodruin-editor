from __future__ import annotations

import logging
from math import floor
from typing import TYPE_CHECKING, Any, List, Optional, Union
from uuid import UUID

import attr
from orodruin.core.node import Node, NodeLike
from orodruin.core.port.port import Port, PortDirection
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from orodruin_editor.ui.editor.graphics_layouts import VerticalGraphicsLayout

from .graphics_node_name import GraphicsNodeName
from .graphics_port import GraphicsPort, GraphicsPortLike

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState

logger = logging.getLogger(__name__)


@attr.s
class GraphicsNode(QGraphicsItem):

    _graphics_state: GraphicsState = attr.ib()
    _uuid: UUID = attr.ib()
    _name: str = attr.ib()
    _parent: Optional[QGraphicsItem] = attr.ib(default=None)

    _graphics_ports: List[UUID] = attr.ib(init=False, factory=list)

    _header_height: int = attr.ib(init=False, default=30)
    _corner_radius: float = attr.ib(init=False)

    _header_color: QBrush = attr.ib(init=False)
    _header_brush: QBrush = attr.ib(init=False)

    _background_color: QColor = attr.ib(init=False)
    _background_brush: QBrush = attr.ib(init=False)

    _outline_pen_default: QPen = attr.ib(init=False)
    _outline_pen_selected: QPen = attr.ib(init=False)

    _name_item: GraphicsNodeName = attr.ib(init=False)
    _input_port_layout: VerticalGraphicsLayout = attr.ib(init=False)
    _output_port_layout: VerticalGraphicsLayout = attr.ib(init=False)

    _mouse_offset: QPointF = attr.ib(init=False, factory=QPointF)

    @classmethod
    def from_node(
        cls,
        graphics_state: GraphicsState,
        node: Node,
        parent: Optional[QGraphicsItem] = None,
    ) -> GraphicsNode:
        graphics_node = cls(graphics_state, node.uuid(), node.name(), parent)
        node.port_registered.subscribe(graphics_node.register_graphics_port)
        node.port_unregistered.subscribe(graphics_node.unregister_graphics_port)
        node.name_changed.subscribe(graphics_node.set_name)
        return graphics_node

    def __attrs_post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self._header_color = QColor("#2B6299")
        self._header_brush = QBrush(self._header_color)

        self._background_color = QColor("#333333")
        self._background_brush = QBrush(self._background_color)

        self._name_item = GraphicsNodeName(self._graphics_state, self._name, self)

        self._corner_radius = 5

        self._outline_pen_default = Qt.NoPen
        self._outline_pen_selected = QPen(Qt.white)
        self._outline_pen_selected.setWidth(5)

        self._port_layout = VerticalGraphicsLayout(self)
        self._port_layout.setPos(0, self._header_height)
        self._output_port_layout = VerticalGraphicsLayout()
        self._input_port_layout = VerticalGraphicsLayout()
        self._port_layout.add_item(self._output_port_layout)
        self._port_layout.add_item(self._input_port_layout)

    def uuid(self) -> Node:
        """Return the UUID of the graphics node."""
        return self._uuid

    def name(self) -> str:
        """Return the name of the graphics node."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the graphics node."""
        self._name = name
        self._name_item.set_name(name)

    def width(self) -> int:
        """Return the width of the graphics node."""
        return 150

    def height(self) -> int:
        """Return the height of the graphics node."""
        return (
            self._header_height
            + self._input_port_layout.boundingRect().height()
            + self._output_port_layout.boundingRect().height()
        )

    def register_graphics_port(self, graphics_port: GraphicsPortLike) -> None:
        """Register an existing graphics port to the graph."""

        if isinstance(graphics_port, GraphicsPort):
            # We may have a virtual graphics port on our hands
            # which is not registered in the state
            # In that case we need to bypass the call to `get_graphics_port`
            pass
        else:
            graphics_port = self._graphics_state.get_graphics_port(graphics_port)

        parent_port = graphics_port.parent_port()
        if parent_port and graphics_port.is_virtual():
            parent_port = self.scene().get_virtual_port(parent_port.uuid())

        if parent_port:
            port_layout = parent_port.child_ports_layout()
        elif graphics_port.direction() is PortDirection.input:
            port_layout = self._input_port_layout
        else:
            port_layout = self._output_port_layout

        port_layout.add_item(graphics_port)

        self._graphics_ports.append(graphics_port.uuid())

        logger.debug("Registered graphics port %s.", graphics_port.uuid())

    def unregister_graphics_port(self, graphics_port: GraphicsPortLike) -> None:
        graphics_port = self._graphics_state.get_graphics_port(graphics_port)
        self._graphics_ports.remove(graphics_port.uuid())
        graphics_port.parentItem().remove_item(graphics_port)
        logger.debug("Unregistered graphics port %s.", graphics_port.uuid())

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            self.width(),
            self.height(),
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:

        # Outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            self._corner_radius,
            self._corner_radius,
        )
        painter.setClipPath(path_outline)

        # Header
        path_header = QPainterPath()
        path_header.setFillRule(Qt.WindingFill)
        path_header.addRoundedRect(
            0,
            0,
            self.width(),
            self._header_height,
            self._corner_radius,
            self._corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._header_brush)
        painter.drawPath(path_header.simplified())

        # Body
        path_body = QPainterPath()
        path_body.addRect(
            0,
            self._header_height / 2,
            self.width(),
            self.height() - self._header_height / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_brush)
        painter.drawPath(path_body.simplified())

        # Outline
        outline_pen = (
            self._outline_pen_default
            if not self.isSelected()
            else self._outline_pen_selected
        )
        painter.setPen(outline_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def closest_grid_position(self, point: QPointF) -> QPointF:
        grid_size = self.scene()._square_size
        adjusted_x = floor(point.x() / grid_size) * grid_size
        adjusted_y = floor(point.y() / grid_size) * grid_size
        return QPointF(adjusted_x, adjusted_y)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            return self.closest_grid_position(value)
        return super().itemChange(change, value)


GraphicsNodeLike = Union[GraphicsNode, NodeLike]

__all__ = [
    "GraphicsNode",
    "GraphicsNodeLike",
]
