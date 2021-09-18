from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from orodruin.core import Port, PortDirection
from PySide2.QtCore import QPoint, QPointF, QRectF, Qt
from PySide2.QtGui import QBrush, QFont, QPainter, QPainterPath
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from .graphics_socket import GraphicsSocket

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

        self.width = 150
        self.height = 25
        self.padding = 15
        self.port_offset = 0

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self.graphics_socket = GraphicsSocket(self)
        self.graphics_socket.moveBy(
            self.socket_position().x(), self.socket_position().y()
        )

    def uuid(self) -> UUID:
        """UUID of this graphics port."""
        return self._port.uuid()

    def port(self) -> Port:
        """Getter for this graphics port's orodruin port."""
        return self._port

    def graphics_component(self) -> GraphicsComponent:
        """Getter for this graphics port's graphics component."""
        return self._graphics_component

    def socket_position(self) -> QPointF:
        """Local position of the Port's socket"""
        horizontal_offset = (
            self.port_offset
            if self._port.direction() is PortDirection.input
            else self.width - self.port_offset
        )
        return QPointF(
            horizontal_offset,
            self.height / 2,
        )

    def scene_socket_position(self) -> QPointF:
        """Global position of the Port's socket, used to attach Connections to."""
        return self.scenePos() + self.socket_position()

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

        path_name = QPainterPath()
        path_name.addText(
            0,
            0,
            self._name_font,
            self._port.name(),
        )

        horizontal_offset = (
            self.port_offset + self.padding
            if self._port.direction() is PortDirection.input
            else self.width
            - path_name.boundingRect().width()
            - self.padding
            - self.port_offset
        )
        path_name.translate(
            horizontal_offset,
            -2 + self._name_font.pointSize() / 2.0 + self.height / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)
