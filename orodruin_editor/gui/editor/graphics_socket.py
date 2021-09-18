from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

from orodruin.core import Port
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from .graphics_port import GraphicsPort


class PortColor(Enum):
    """A Mapping between the port type and port colors."""

    Matrix3 = QColor("#cc6666")
    Matrix4 = QColor("#cc6666")
    Vector2 = QColor("#b5bd68")
    Vector3 = QColor("#b5bd68")
    bool = QColor("#de935f")
    float = QColor("#8abeb7")
    int = QColor("#81a2be")
    str = QColor("#f0c674")


class GraphicsSocket(QGraphicsItem):
    """Graphical representation of a Socket

    Orodruin has no socket concept, this only exists to register events more precisely.
    """

    def __init__(self, graphics_port: GraphicsPort) -> None:
        super().__init__(parent=graphics_port)

        self.graphics_port = graphics_port

        self.radius = 6
        self._color_outline = QColor("#101010")
        self._color_background = QColor(Qt.white)

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(2)
        self._brush = QBrush(self.color())

    def color(self) -> QColor:
        """Color the Socket should have"""
        port_type = self.graphics_port.port().type()
        try:
            color = PortColor[port_type.__name__].value
        except:
            color = Qt.lightGray
        return color

    def port(self) -> Port:
        """Return the Orodruin Port this Socket maps to."""
        return self.graphics_port.port()

    def boundingRect(self) -> QRectF:
        # return a bigger bounding rect than the visual socket
        # to make it easier to interact with
        return QRectF(
            -self.radius * 2,
            -self.radius * 2,
            2 * self.radius * 2,
            2 * self.radius * 2,
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
