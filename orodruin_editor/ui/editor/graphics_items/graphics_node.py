from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from orodruin.core.node import Node, NodeLike
from orodruin.core.port.port import PortDirection
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from orodruin_editor.ui.editor.graphics_layouts import VerticalGraphicsLayout

from .graphics_node_name import GraphicsNodeName
from .graphics_port import GraphicsPort, GraphicsPortLike

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState

logger = logging.getLogger(__name__)


@dataclass
class GraphicsNode(QGraphicsItem):

    _graphics_state: GraphicsState
    _uuid: UUID
    _name: str
    _parent: Optional[QGraphicsItem] = None

    _graphics_ports: List[UUID] = field(init=False, default_factory=list)

    _header_height: int = field(init=False, default=30)
    _corner_radius: float = field(init=False)

    _header_color: QBrush = field(init=False)
    _header_brush: QBrush = field(init=False)

    _background_color: QColor = field(init=False)
    _background_brush: QBrush = field(init=False)

    _outline_pen_default: QPen = field(init=False)
    _outline_pen_selected: QPen = field(init=False)

    _name_item: GraphicsNodeName = field(init=False)
    _input_port_layout: VerticalGraphicsLayout = field(init=False)
    _output_port_layout: VerticalGraphicsLayout = field(init=False)

    @classmethod
    def from_node(
        cls,
        graphics_state: GraphicsState,
        node: Node,
        parent: Optional[QGraphicsItem] = None,
    ) -> GraphicsNode:
        graphics_node = cls(graphics_state, node.uuid(), node.name(), parent)
        node.port_registered.subscribe(graphics_node.register_graphics_port)
        # node.port_unregistered.subscribe(graphics_node.register_graphics_port)
        node.name_changed.subscribe(graphics_node.set_name)
        return graphics_node

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

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
        if parent_port:
            port_layout = parent_port.child_ports_layout()
        elif graphics_port.direction() is PortDirection.input:
            port_layout = self._input_port_layout
        else:
            port_layout = self._output_port_layout

        port_layout.add_item(graphics_port)

        self._graphics_ports.append(graphics_port.uuid())

        logger.debug("Registered graphics port %s.", graphics_port.uuid())

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


GraphicsNodeLike = Union[GraphicsNode, NodeLike]

__all__ = [
    "GraphicsNode",
    "GraphicsNodeLike",
]
