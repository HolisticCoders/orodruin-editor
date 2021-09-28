from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

from orodruin.core import PortDirection, PortType
from orodruin.core.port.port import Port, PortLike
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from orodruin_editor.ui.editor.graphics_items.graphics_socket import GraphicsSocket

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState


@dataclass
class GraphicsPort(QGraphicsItem):

    _graphics_state: GraphicsState
    _name: str
    _direction: PortDirection
    _port_type: PortType
    _parent: Optional[QGraphicsItem] = None

    _height: int = field(init=False, default=25)
    _width: int = field(init=False, default=150)
    _horizontal_text_padding: int = field(init=False, default=15)
    _port_offset: int = field(init=False, default=0)

    _name_color: QColor = field(init=False)
    _name_brush: QBrush = field(init=False)
    _name_font_family: str = field(init=False, default="Roboto")
    _name_font_size: int = field(init=False, default=10)
    _name_font: QFont = field(init=False)

    _graphics_socket: GraphicsSocket = field(init=False)

    @classmethod
    def from_port(
        cls,
        graphics_state: GraphicsState,
        port: Port,
        parent: Optional[QGraphicsItem] = None,
    ):
        graphics_port = cls(
            graphics_state,
            port.name(),
            port.direction(),
            port.type(),
            parent,
        )
        return graphics_port

    def __post_init__(
        self,
    ) -> None:
        super().__init__(parent=self._parent)

        self._name_color = Qt.white
        self._name_brush = QBrush(self._name_color)
        self._name_font = QFont(self._name_font_family, self._name_font_size)

        self._graphics_socket = GraphicsSocket(self)
        self._graphics_socket.moveBy(
            self.socket_position().x(), self.socket_position().y()
        )

    def name(self) -> str:
        """Return the name of the graphics port."""
        return self._name

    def direction(self) -> PortDirection:
        """Return the direction of the graphics port."""
        return self._direction

    def type(self) -> PortType:
        """Return the type of the graphics port."""
        return self._port_type

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def graphics_socket(self) -> GraphicsSocket:
        return self._graphics_socket

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
            self._port_offset + self._horizontal_text_padding
            if self.direction() is PortDirection.input
            else self.width()
            - path_name.boundingRect().width()
            - self._horizontal_text_padding
            - self._port_offset
        )
        path_name.translate(
            horizontal_offset,
            -2 + self._name_font.pointSize() / 2.0 + self.height() / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._name_brush)
        painter.drawPath(path_name)


GraphicsPortLike = Union[GraphicsPort, PortLike]

__all__ = [
    "GraphicsPort",
    "GraphicsPortLike",
]
