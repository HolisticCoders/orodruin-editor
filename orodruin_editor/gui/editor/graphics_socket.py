from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from orodruin import Port
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from .graphics_port import GraphicsPort


class GraphicsSocket(QGraphicsItem):
    """Graphical representation of a Socket

    Orodruin has no socket concept, this only exists to register events more precisely.
    """

    def __init__(self, graphics_port: GraphicsPort) -> None:
        super().__init__(parent=graphics_port)

        self.graphics_port = graphics_port

        self.radius = 5
        self._color_outline = QColor("#101010")
        self._color_background = QColor(Qt.white)

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(2)
        self._brush = QBrush(self._color_background)

    def port(self) -> Port:
        """Return the Orodruin Port this Socket maps to."""
        return self.graphics_port.port()

    def boundingRect(self) -> QRectF:
        return QRectF(
            -self.radius,
            -self.radius,
            2 * self.radius,
            2 * self.radius,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(
            -self.radius,
            -self.radius,
            2 * self.radius,
            2 * self.radius,
        )
