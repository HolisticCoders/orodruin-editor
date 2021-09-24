from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, Union
from uuid import UUID, uuid4

from orodruin.core import Port, PortDirection
from orodruin.core.port.port import PortLike
from PySide2.QtCore import QPoint, QPointF, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from .graphics_socket import GraphicsSocket

if TYPE_CHECKING:
    from .graphics_component import GraphicsComponent
    from .graphics_scene import GraphicsScene


class GraphicsPort(QGraphicsItem):
    """Graphical representation of an Orodruin Port."""

    def __init__(
        self,
        scene: GraphicsScene,
        name: str,
        direction: PortDirection,
        port_type: Type,
        component_id: UUID,
        uuid: Optional[UUID],
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent=parent)

        self._scene = scene

        self._name = name
        self._direction = direction
        self._port_type = port_type
        self._component_id = component_id

        if not uuid:
            uuid = uuid4()
        self._uuid = uuid

        self._width = 150
        self._height = 25
        self._padding = 15
        self._port_offset = 0

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self._graphics_socket = GraphicsSocket(self)
        self._graphics_socket.moveBy(
            self.socket_position().x(), self.socket_position().y()
        )

    def name(self) -> str:
        """Return the name of this GraphicsPort"""
        return self._name

    def set_name(self, value: str) -> None:
        """Set the name of this GraphicsPort"""
        self._name = value

    def direction(self) -> PortDirection:
        """Return the direction of this GraphicsPort"""
        return self._direction

    def port_type(self) -> Type:
        """Return tye type of this Graphics Port"""
        return self._port_type

    def graphics_component(self) -> GraphicsComponent:
        """Return this graphics port's graphics component."""
        return self._scene.get_graphics_component(self._component_id)

    def uuid(self) -> UUID:
        """Return this Graphics port's UUID."""
        return self._uuid

    def graphics_socket(self) -> GraphicsSocket:
        """Return this graphics port's graphics component."""
        return self._graphics_socket

    def width(self) -> int:
        """Return the width of this Graphics Port"""
        return self._width

    def height(self) -> int:
        """Return the height of this Graphics Port"""
        return self._height

    def socket_position(self) -> QPointF:
        """Local position of the Port's socket"""
        horizontal_offset = (
            self._port_offset
            if self.direction() is PortDirection.input
            else self.width() - self._port_offset
        )
        return QPointF(
            horizontal_offset,
            self.height() / 2,
        )

    def scene_socket_position(self) -> QPointF:
        """Global position of the Port's socket, used to attach Connections to."""
        return self.scenePos() + self.socket_position()

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

        path_name = QPainterPath()
        path_name.addText(
            0,
            0,
            self._name_font,
            self.name(),
        )

        horizontal_offset = (
            self._port_offset + self._padding
            if self.direction() is PortDirection.input
            else self.width()
            - path_name.boundingRect().width()
            - self._padding
            - self._port_offset
        )
        path_name.translate(
            horizontal_offset,
            -2 + self._name_font.pointSize() / 2.0 + self.height() / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)


GraphicsPortLike = Union[GraphicsPort, PortLike]

__all__ = [
    "GraphicsPort",
    "GraphicsPortLike",
]
