from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

import attr
from orodruin.core.connection import Connection, ConnectionLike
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState
    from .graphics_port import GraphicsPort


@attr.s
class GraphicsConnection(QGraphicsPathItem):
    _graphics_state: GraphicsState = attr.ib()
    _uuid: UUID = attr.ib()

    _source_graphics_port: Optional[GraphicsPort] = attr.ib(default=None)
    _target_graphics_port: Optional[GraphicsPort] = attr.ib(default=None)
    _parent: Optional[QGraphicsItem] = attr.ib(default=None)

    _mouse_position: QPointF = attr.ib(init=False)

    _gradient: QLinearGradient = attr.ib(init=False)
    _unselected_pen: QPen = attr.ib(init=False)
    _selected_pen: QPen = attr.ib(init=False)

    @classmethod
    def from_connection(
        cls,
        graphics_state: GraphicsState,
        connection: Connection,
        parent: Optional[QGraphicsItem] = None,
    ) -> GraphicsConnection:

        source_graphics_port = graphics_state.get_graphics_port(connection.source())
        target_graphics_port = graphics_state.get_graphics_port(connection.target())

        return cls(
            graphics_state,
            connection.uuid(),
            source_graphics_port,
            target_graphics_port,
            parent=parent,
        )

    def __attrs_post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self._mouse_position = QPointF(0, 0)

        self._gradient = QLinearGradient(0, 0, 0, 0)
        self._unselected_pen = QPen(self._gradient, 2)
        self._selected_pen = QPen(Qt.white)
        self._unselected_pen.setWidth(2)
        self._selected_pen.setWidth(2)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def uuid(self) -> UUID:
        return self._uuid

    def source_graphics_port(self) -> GraphicsPort:
        return self._source_graphics_port

    def target_graphics_port(self) -> GraphicsPort:
        return self._target_graphics_port

    def set_source_graphics_port(self, graphics_port: GraphicsPort) -> None:
        self._source_graphics_port = graphics_port

    def set_target_graphics_port(self, graphics_port: GraphicsPort) -> None:
        self._target_graphics_port = graphics_port

    def mouse_position(self) -> QPointF:
        return self._mouse_position

    def set_mouse_position(self, position: QPointF):
        self._mouse_position = position

    def source_position(self) -> QPointF:
        """Returns the position of the source graphics port."""
        if not self._source_graphics_port:
            return self.mouse_position
        return self._source_graphics_port.scene_socket_position()

    def target_position(self) -> QPointF:
        """Returns the position of the target graphics port."""
        if not self._target_graphics_port:
            return self.mouse_position
        return self._target_graphics_port.scene_socket_position()

    def source_color(self) -> QColor:
        """Return the color of this connection's source socket"""
        if self._source_graphics_port:
            return self._source_graphics_port.graphics_socket().color()
        else:
            # This is likely a temporary connection that doesn't have a source yet.
            # We just return the target's color to have a consistent gradient
            return self._target_graphics_port.graphics_socket().color()

    def target_color(self) -> QColor:
        if self._target_graphics_port:
            return self._target_graphics_port.graphics_socket().color()
        else:
            # This is likely a temporary connection that doesn't have a target yet.
            # We just return the target's color to have a consistent gradient
            return self._source_graphics_port.graphics_socket().color()

    def update_path(self):
        """Update the connection's path."""
        a = self.source_position()
        b = self.source_position() + QPointF(25, 0)
        c = self.target_position() - QPointF(25, 0)
        d = self.target_position()

        path = QPainterPath(a)
        path.lineTo(b)
        path.lineTo(c)
        path.lineTo(d)
        self.setPath(path)

    def boundingRect(self) -> QRectF:

        source_pos = self.source_position()
        target_pos = self.target_position()
        source_target_vector = target_pos - source_pos

        x = source_pos.x()
        y = source_pos.y()
        width = source_target_vector.x()
        height = source_target_vector.y()

        return QRectF(x, y, width, height)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        self.update_path()
        self._gradient.setStart(self.source_position())
        self._gradient.setFinalStop(self.target_position())

        self._gradient.setColorAt(0, self.source_color())
        self._gradient.setColorAt(1, self.target_color())
        self._unselected_pen = QPen(self._gradient, 2)
        pen = self._unselected_pen if not self.isSelected() else self._selected_pen
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())


GraphicsConnectionLike = Union[GraphicsConnection, ConnectionLike]

__all__ = [
    "GraphicsConnection",
    "GraphicsConnectionLike",
]
