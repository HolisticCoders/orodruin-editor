from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from orodruin.port.port import Port, PortDirection
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from .graphics_component import GraphicsComponent


class GraphicsPort(QGraphicsItem):
    """Graphical representation of an Orodruin Port."""

    def __init__(
        self,
        port: Port,
        graphics_component: GraphicsComponent,
    ) -> None:
        super().__init__(parent=graphics_component)

        self._port = port
        self._graphics_component = graphics_component

        self.width = 175
        self.height = 25
        self.radius = 5
        self.padding = 10

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self._color_outline = QColor("#101010")

        self._color_background = QColor(Qt.white)

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(2)
        self._brush = QBrush(self._color_background)

    def uuid(self) -> UUID:
        """UUID of this graphics port."""
        return self._port.uuid()

    def port(self) -> Port:
        """Getter for this graphics port's orodruin port."""
        return self._port

    def graphics_component(self) -> GraphicsComponent:
        """Getter for this graphics port's graphics component."""
        return self._graphics_component

    def port_position(self) -> QPointF:
        """Local position of the Port"""
        horizontal_offset = (
            0 if self._port.direction() is PortDirection.input else self.width
        )
        return QPointF(
            horizontal_offset,
            self.height / 2,
        )

    def scene_port_position(self) -> QPointF:
        """Global position of the Port, used to attach Connections to."""
        return self.scenePos() + self.port_position()

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            self.width,
            self.height,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        path_name = QPainterPath()
        path_name.addText(
            0,
            0,
            self._name_font,
            self._port.name(),
        )

        horizontal_offset = (
            self.padding
            if self._port.direction() is PortDirection.input
            else self.width - path_name.boundingRect().width() - self.padding
        )
        path_name.translate(
            horizontal_offset,
            -2 + self._name_font.pointSize() / 2.0 + self.height / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)

        horizontal_offset = (
            0 if self._port.direction() is PortDirection.input else self.width
        )
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(
            -self.radius + horizontal_offset,
            -self.radius + self.height / 2,
            2 * self.radius,
            2 * self.radius,
        )
