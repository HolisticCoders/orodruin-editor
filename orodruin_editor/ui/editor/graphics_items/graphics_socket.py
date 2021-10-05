from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from orodruin.core.port.port import PortDirection
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
    Quaternion = QColor("#b294bb")
    bool = QColor("#de935f")
    float = QColor("#8abeb7")
    int = QColor("#81a2be")
    str = QColor("#f0c674")


@dataclass
class GraphicsSocket(QGraphicsItem):
    """Graphical representation of a Socket

    Orodruin has no socket concept, this only exists to register events more precisely.
    """

    _graphics_port: GraphicsPort

    _radius: int = field(init=False, default=6)
    _color_outline: QColor = field(init=False)
    _color_background: QColor = field(init=False)

    _pen: QPen = field(init=False)
    _brush: QBrush = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._graphics_port)

        self._color_outline = QColor("#101010")
        self._color_background = QColor(Qt.white)

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(2)
        self._brush = QBrush(self.color())

    def graphics_port(self) -> GraphicsPort:
        """Return this Graphics Socket's Graphics Port"""
        return self._graphics_port

    def direction(self) -> PortDirection:
        """Return this Graphics Socket's PortDirection"""
        return self._graphics_port.direction()

    def uuid(self) -> UUID:
        """Return this Graphics Socket's UUID"""
        return self._graphics_port.uuid()

    def color(self) -> QColor:
        """Color the Socket should have"""
        port_type = self._graphics_port.type()
        try:
            color = PortColor[port_type.__name__].value
        except:
            color = Qt.lightGray
        return color

    def boundingRect(self) -> QRectF:
        # return a bigger bounding rect than the visual socket
        # to make it easier to interact with
        return QRectF(
            -self._radius * 2,
            -self._radius * 2,
            2 * self._radius * 2,
            2 * self._radius * 2,
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
            -self._radius,
            -self._radius,
            2 * self._radius,
            2 * self._radius,
        )
