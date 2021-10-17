from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

import attr
from orodruin.core import PortDirection, PortType
from orodruin.core.port.port import Port, PortLike
from PySide2.QtCore import QPointF, QRect, QRectF, Qt
from PySide2.QtGui import QColor, QFont, QPainter
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from orodruin_editor.ui.editor.graphics_items.graphics_socket import GraphicsSocket
from orodruin_editor.ui.editor.graphics_layouts import (
    LayoutItem,
    VerticalGraphicsLayout,
)

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState


@attr.s
class GraphicsPort(LayoutItem):

    _graphics_state: GraphicsState = attr.ib()
    _uuid: UUID = attr.ib()
    _name: str = attr.ib()
    _direction: PortDirection = attr.ib()
    _port_type: PortType = attr.ib()
    _parent_port_id: Optional[UUID] = attr.ib(default=None)
    _is_virtual: bool = attr.ib(default=False)
    _parent: Optional[QGraphicsItem] = attr.ib(default=None)

    _height: int = attr.ib(init=False, default=25)
    _width: int = attr.ib(init=False, default=150)
    _horizontal_text_padding: int = attr.ib(init=False, default=15)
    _port_offset: int = attr.ib(init=False, default=0)

    _name_color: QColor = attr.ib(init=False)
    _name_font_family: str = attr.ib(init=False, default="Roboto")
    _name_font_size: int = attr.ib(init=False, default=10)
    _name_font: QFont = attr.ib(init=False)

    _graphics_socket: GraphicsSocket = attr.ib(init=False)
    _name_item: QGraphicsTextItem = attr.ib(init=False)

    _child_ports_layout: VerticalGraphicsLayout = attr.ib(init=False)

    @classmethod
    def from_port(
        cls,
        graphics_state: GraphicsState,
        port: Port,
        parent: Optional[QGraphicsItem] = None,
    ) -> GraphicsPort:
        if port.parent_port():
            parent_port_id = port.parent_port().uuid()
        else:
            parent_port_id = None
        graphics_port = cls(
            graphics_state,
            port.uuid(),
            port.name(),
            port.direction(),
            port.type(),
            parent_port_id,
            parent,
        )
        port.name_changed.subscribe(graphics_port.set_name)
        return graphics_port

    def __attrs_post_init__(
        self,
    ) -> None:
        super().__init__(parent=self._parent)

        self._graphics_socket = GraphicsSocket(self)
        self._graphics_socket.moveBy(
            self.socket_position().x(), self.socket_position().y()
        )

        self._create_name_item()

        self._child_ports_layout = VerticalGraphicsLayout(self)
        self._child_ports_layout.setPos(0, self._height)
        self._child_ports_layout.hide()

    def _create_name_item(self) -> None:
        self._name_color = Qt.white
        self._name_font = QFont(self._name_font_family, self._name_font_size)

        self._name_item = QGraphicsTextItem(self._name)
        self._name_item.setParentItem(self)

        self._name_item.setFont(self._name_font)
        self._name_item.setDefaultTextColor(self._name_color)

        padding = (
            self._horizontal_text_padding
            if not self._parent_port_id
            else self._horizontal_text_padding * 2
        )
        horizontal_offset = (
            self._port_offset + padding
            if self.direction() is PortDirection.input
            else self.width()
            - self._name_item.boundingRect().width()
            - padding
            - self._port_offset
        )
        self._name_item.setPos(
            horizontal_offset,
            0
            # -2 + self._name_font.pointSize() / 2.0 + self.height() / 2,
        )

    def uuid(self) -> UUID:
        return self._uuid

    def name(self) -> str:
        """Return the name of the graphics port."""
        return self._name

    def set_name(self, name: str) -> None:
        """Set the name of the graphics port."""
        self._name = name
        self._name_item.setPlainText(name)

    def direction(self) -> PortDirection:
        """Return the direction of the graphics port."""
        return self._direction

    def type(self) -> PortType:
        """Return the type of the graphics port."""
        return self._port_type

    def is_virtual(self) -> bool:
        return self._is_virtual

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def parent_port(self) -> Optional[GraphicsPort]:
        if self._parent_port_id:
            return self._graphics_state.get_graphics_port(self._parent_port_id)
        return None

    def graphics_socket(self) -> GraphicsSocket:
        return self._graphics_socket

    def child_ports_layout(self) -> VerticalGraphicsLayout:
        return self._child_ports_layout

    def socket_position(self) -> QPointF:
        """Local position of the Port's socket"""
        horizontal_offset = (
            self._port_offset
            if self.direction() is PortDirection.input
            else self.width() - self._port_offset
        )
        return QPointF(
            horizontal_offset,
            self._height / 2,
        )

    def scene_socket_position(self) -> QPointF:
        """Global position of the Port's socket, used to attach Connections to."""
        return self.scenePos() + self.socket_position()

    def effective_bounding_rect(self) -> QRectF:
        width = self.width()
        height = (
            self._height + self._child_ports_layout.effective_bounding_rect().height()
        )
        return QRect(0, 0, width, height)

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
        return


GraphicsPortLike = Union[GraphicsPort, PortLike]

__all__ = [
    "GraphicsPort",
    "GraphicsPortLike",
]
