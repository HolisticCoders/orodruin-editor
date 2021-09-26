from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from orodruin.core.graph import Graph, GraphLike
from orodruin.core.node import Node
from PySide2.QtCore import QLine, QObject, QRectF
from PySide2.QtGui import QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsScene

if TYPE_CHECKING:
    from orodruin_editor.ui.editor.graphics_state import GraphicsState

logger = logging.getLogger(__name__)


@dataclass
class GraphicsGraph(QGraphicsScene):
    """Graphical representation of an Orodruin Graph."""

    _graphics_state: GraphicsState
    _uuid: UUID
    parent: Optional[QObject] = None

    _graphics_nodes: List[UUID] = field(init=False, default_factory=list)

    _square_size: int = field(init=False, default=25)  # in pixels
    _cell_size: int = field(init=False, default=10)  # in squares

    _width: int = field(init=False, default=64000)
    _height: int = field(init=False, default=64000)

    _background_color: QColor = field(init=False)
    _square_color: QColor = field(init=False)
    _cell_color: QColor = field(init=False)

    _pen_square: QPen = field(init=False)
    _pen_cell: QPen = field(init=False)

    @classmethod
    def from_graph(cls, graphics_state: GraphicsState, graph: Graph):
        graphics_graph = GraphicsGraph(graphics_state, graph.uuid())
        graph.node_registered.subscribe(graphics_graph.register_graphics_node)
        graph.node_unregistered.subscribe(graphics_graph.unregister_graphics_node)
        return graphics_graph

    def __post_init__(
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

        self.setBackgroundBrush(self._background_color)

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


GraphicsGraphLike = Union[GraphicsGraph, GraphLike]

__all__ = [
    "GraphicsGraph",
    "GraphicsGraphLike",
]
