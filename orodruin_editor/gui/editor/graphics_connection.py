from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide2.QtCore import QPointF
from PySide2.QtGui import QLinearGradient, QPainter, QPainterPath, QPen, Qt
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
        source_graphics_port: Optional[GraphicsPort] = None,
        target_graphics_port: Optional[GraphicsPort] = None,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.source_graphics_port = source_graphics_port
        self.target_graphics_port = target_graphics_port

        self.gradient = QLinearGradient(0, 0, 0, 0)
        self._unselected_pen = QPen(self.gradient, 2)
        self._selected_pen = QPen(Qt.white)
        self._unselected_pen.setWidth(2)
        self._selected_pen.setWidth(2)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

        self.mouse_position = QPointF(0, 0)

    def source_position(self) -> QPointF:
        """Returns the position of the source graphics port."""
        if not self.source_graphics_port:
            return self.mouse_position
        return self.source_graphics_port.scene_socket_position()

    def target_position(self) -> QPointF:
        """Returns the position of the target graphics port."""
        if not self.target_graphics_port:
            return self.mouse_position
        return self.target_graphics_port.scene_socket_position()

    def update_path(self):
        """Update the path."""
        a = self.source_position()
        b = self.source_position() + QPointF(20, 0)
        c = self.target_position() - QPointF(20, 0)
        d = self.target_position()

        path = QPainterPath(a)
        path.lineTo(b)
        path.lineTo(c)
        path.lineTo(d)
        self.setPath(path)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        self.update_path()
        self.gradient.setStart(self.source_position())
        self.gradient.setFinalStop(self.target_position())

        source_color = Qt.white
        target_color = Qt.white

        if self.source_graphics_port:
            source_color = self.source_graphics_port.graphics_socket.color()
        if self.target_graphics_port:
            target_color = self.target_graphics_port.graphics_socket.color()

        self.gradient.setColorAt(0, source_color)
        self.gradient.setColorAt(1, target_color)
        self._unselected_pen = QPen(self.gradient, 2)
        pen = self._unselected_pen if not self.isSelected() else self._selected_pen
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
