from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide2.QtCore import QPointF
from PySide2.QtGui import QPainter, QPainterPath, QPen, Qt
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

if TYPE_CHECKING:
    from .graphics_port import GraphicsPort


class GraphicsConnection(QGraphicsPathItem):
    """Graphical representation of an Orodruin Connection."""

    def __init__(
        self,
        source_graphics_port: GraphicsPort,
        target_graphics_port: GraphicsPort,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.source_graphics_port = source_graphics_port
        self.target_graphics_port = target_graphics_port

        self._unselected_pen = QPen(Qt.white)
        self._selected_pen = QPen(Qt.yellow)
        self._unselected_pen.setWidth(2)
        self._selected_pen.setWidth(2)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def source_position(self) -> QPointF:
        """Returns the position of the source graphics port."""
        return self.source_graphics_port.scene_port_position()

    def target_position(self) -> QPointF:
        """Returns the position of the target graphics port."""
        return self.target_graphics_port.scene_port_position()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        path = QPainterPath(self.source_position())
        path.lineTo(self.target_position())
        self.setPath(path)

        pen = self._unselected_pen if not self.isSelected() else self._selected_pen
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
