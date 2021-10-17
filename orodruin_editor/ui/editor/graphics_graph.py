from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID, uuid4

import attr
from orodruin.core import graph
from orodruin.core.connection import Connection
from orodruin.core.graph import Graph, GraphLike
from orodruin.core.node import Node
from orodruin.core.port.port import Port, PortDirection
from PySide2.QtCore import QLine, QObject, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import QGraphicsScene

from .graphics_items.graphics_node import GraphicsNode
from .graphics_items.graphics_port import GraphicsPort

if TYPE_CHECKING:
    from .graphics_state import GraphicsState

logger = logging.getLogger(__name__)


@attr.s
class GraphicsGraph(QGraphicsScene):
    """Graphical representation of an Orodruin Graph."""

    _graphics_state: GraphicsState = attr.ib()
    _uuid: UUID = attr.ib()
    parent: Optional[QObject] = attr.ib(default=None)

    _graphics_nodes: List[UUID] = attr.ib(init=False, factory=list)
    _graphics_ports: List[UUID] = attr.ib(init=False, factory=list)
    _graphics_connections: List[UUID] = attr.ib(init=False, factory=list)

    _input_graphics_node: Optional[GraphicsNode] = attr.ib(init=False, default=None)
    _output_graphics_node: Optional[GraphicsNode] = attr.ib(init=False, default=None)
    _virtual_graphics_ports: Dict[GraphicsPort] = attr.ib(init=False, factory=dict)

    _square_size: int = attr.ib(init=False, default=25)  # in pixels
    _cell_size: int = attr.ib(init=False, default=10)  # in squares

    _width: int = attr.ib(init=False, default=64000)
    _height: int = attr.ib(init=False, default=64000)

    _background_color: QColor = attr.ib(init=False)
    _square_color: QColor = attr.ib(init=False)
    _cell_color: QColor = attr.ib(init=False)

    _pen_square: QPen = attr.ib(init=False)
    _pen_cell: QPen = attr.ib(init=False)

    @classmethod
    def from_graph(cls, graphics_state: GraphicsState, graph: Graph):
        graphics_graph = cls(graphics_state, graph.uuid())
        graph.node_registered.subscribe(graphics_graph.register_graphics_node)
        graph.node_unregistered.subscribe(graphics_graph.unregister_graphics_node)
        graph.port_registered.subscribe(graphics_graph.register_graphics_port)
        graph.port_unregistered.subscribe(graphics_graph.unregister_graphics_port)
        graph.connection_registered.subscribe(
            graphics_graph.register_graphics_connection
        )
        graph.connection_unregistered.subscribe(
            graphics_graph.unregister_graphics_connection
        )

        if graph.parent_node():
            graphics_graph._create_input_output_nodes()
            graph.parent_node().port_registered.subscribe(
                graphics_graph._create_virtual_port
            )
            graph.parent_node().port_unregistered.subscribe(
                graphics_graph._delete_virtual_port
            )

        return graphics_graph

    def __attrs_post_init__(
        self,
    ) -> None:
        super().__init__(parent=self.parent)

        self._background_color = QColor("#191919")
        self._square_color = QColor("#2f2f2f")
        self._cell_color = QColor("#2f2f2f")

        self._pen_square = QPen(self._square_color)
        self._pen_square.setWidthF(0.5)
        self._pen_cell = QPen(self._cell_color)
        self._pen_cell.setWidth(2)

        self.setSceneRect(
            -self._width // 2,
            -self._height // 2,
            self._width,
            self._height,
        )

        self.selectionChanged.connect(self._on_selection_changed)
        self.setBackgroundBrush(self._background_color)

    def get_virtual_port(self, uuid: UUID) -> GraphicsPort:
        return self._virtual_graphics_ports[uuid]

    def _create_input_output_nodes(self) -> None:
        self._input_graphics_node = GraphicsNode(self._graphics_state, uuid4(), "Input")
        self.addItem(self._input_graphics_node)

        self._output_graphics_node = GraphicsNode(
            self._graphics_state, uuid4(), "Output"
        )
        self.addItem(self._output_graphics_node)

    def _create_virtual_port(self, port: Port) -> None:
        if port.direction() is PortDirection.input:
            graphics_node = self._input_graphics_node
            direction = PortDirection.output
        else:
            graphics_node = self._output_graphics_node
            direction = PortDirection.input

        parent_port = port.parent_port()
        if parent_port:
            parent_port_id = parent_port.uuid()
        else:
            parent_port_id = None

        graphics_port = GraphicsPort(
            self._graphics_state,
            port.uuid(),
            port.name(),
            direction,
            port.type(),
            parent_port_id,
            True,
        )
        graphics_node.register_graphics_port(graphics_port)

        self._virtual_graphics_ports[port.uuid()] = graphics_port

    def _delete_virtual_port(self, port: Port) -> None:
        if port.direction() is PortDirection.input:
            graphics_node = self._input_graphics_node
        else:
            graphics_node = self._output_graphics_node

        graphics_port = self._virtual_graphics_ports.pop(port.uuid())

        graphics_node.unregister_graphics_port(graphics_port)
        self.removeItem(graphics_port)

    def uuid(self) -> UUID:
        """Return the UUID of the graph."""
        return self._uuid

    def register_graphics_node(self, node: Node):
        """Register an existing graphics node to the graph."""
        graphics_node = self._graphics_state.get_graphics_node(node)
        self._graphics_nodes.append(node.uuid())
        self.addItem(graphics_node)
        logger.debug("Registered graphics node %s.", node.path())

    def unregister_graphics_node(self, node: Node):
        """Register an existing graphics node to the graph."""
        graphics_node = self._graphics_state.get_graphics_node(node)
        self._graphics_nodes.remove(node.uuid())
        self.removeItem(graphics_node)
        logger.debug("Unregistered graphics node %s.", node.path())

    def register_graphics_port(self, port: Port):
        """Register an existing graphics port to the graph."""
        graphics_port = self._graphics_state.get_graphics_port(port)
        self._graphics_ports.append(port.uuid())

        # the port might have already been added to the graph when its parent node
        # was moved to the graph.
        if graphics_port not in self.items():
            self.addItem(graphics_port)

        logger.debug("Registered graphics port %s.", port.path())

    def unregister_graphics_port(self, port: Port) -> None:
        """Register a graphics port from the graph."""
        graphics_port = self._graphics_state.get_graphics_port(port)
        self._graphics_ports.remove(port.uuid())

        # the port might have already been removed from the graph when its parent node
        # was moved to another graph.
        if graphics_port in self.items():
            self.removeItem(graphics_port)

        logger.debug("Unregistered graphics port %s.", port.path())

    def register_graphics_connection(self, connection: Connection):
        """Register an existing graphics connection to the graph."""
        graphics_connection = self._graphics_state.get_graphics_connection(connection)
        self._graphics_connections.append(connection.uuid())
        self.addItem(graphics_connection)

        connection = self._graphics_state.state().get_connection(
            graphics_connection.uuid()
        )

        virtual_source_graphics_port = self._virtual_graphics_ports.get(
            connection.source().uuid()
        )
        if virtual_source_graphics_port:
            graphics_connection.set_source_graphics_port(virtual_source_graphics_port)

        virtual_target_graphics_port = self._virtual_graphics_ports.get(
            connection.target().uuid()
        )
        if virtual_target_graphics_port:
            graphics_connection.set_target_graphics_port(virtual_target_graphics_port)

        logger.debug("Registered graphics connection %s.", connection.uuid())

    def unregister_graphics_connection(self, connection: Connection):
        """Unregister an existing graphics connection from the graph."""
        graphics_connection = self._graphics_state.get_graphics_connection(connection)
        self._graphics_connections.remove(connection.uuid())
        self.removeItem(graphics_connection)
        logger.debug("Unregistered graphics connection %s.", connection.uuid())

    def _on_selection_changed(self) -> None:
        selected_nodes = [
            item.uuid()
            for item in self.selectedItems()
            if isinstance(item, GraphicsNode)
        ]

        self._graphics_state.selection_changed.emit(selected_nodes)

    def drawBackground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self._square_size)
        first_top = top - (top % self._square_size)

        square_lines = []
        cell_lines = []
        for x in range(first_left, right, self._square_size):
            if x % (self._square_size * self._cell_size) == 0:
                cell_lines.append(QLine(x, top, x, bottom))
            else:
                square_lines.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self._square_size):
            if y % (self._square_size * self._cell_size) == 0:
                cell_lines.append(QLine(left, y, right, y))
            else:
                square_lines.append(QLine(left, y, right, y))

        painter.setPen(self._pen_square)
        painter.drawLines(square_lines)
        painter.setPen(self._pen_cell)
        painter.drawLines(cell_lines)

    def drawForeground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        graph = self._graphics_state.state().get_graph(self.uuid())
        parent_node = graph.parent_node()
        if parent_node:
            path_text = str(parent_node.path())
        else:
            path_text = "/"

        path_name = QPainterPath()
        path_name.addText(
            rect.x() + 25,
            rect.y() + 40,
            QFont("Roboto", 20),
            path_text,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.darkGray))
        painter.drawPath(path_name)


GraphicsGraphLike = Union[GraphicsGraph, GraphLike]

__all__ = [
    "GraphicsGraph",
    "GraphicsGraphLike",
]
