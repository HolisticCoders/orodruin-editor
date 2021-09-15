from typing import Any, Dict, Optional
from uuid import UUID

from orodruin.component import Component
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from .graphics_port import GraphicsPort


class GraphicsComponent(QGraphicsItem):
    """Graphical representation of an Orodruin Component."""

    def __init__(
        self, component: Component, parent: Optional[QGraphicsItem] = None
    ) -> None:
        super().__init__(parent=parent)

        self.component = component
        self._ports: Dict[UUID, GraphicsPort] = {}

        self.width = 175
        self.corner_radius = 5
        self.name_height = 30
        self.padding = 5
        self.bottom_padding = 5

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self._pen_default = QPen(QColor("#101010"))
        self._pen_default.setWidth(2)
        self._pen_selected = QPen(QColor("#f5b933"))
        self._pen_selected.setWidth(2)

        self._brush_name = QBrush(QColor("#2B6299"))
        self._brush_background = QBrush(QColor("#333333"))

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self._name_item = QGraphicsTextItem(self.component.name(), self)
        self._name_item.setDefaultTextColor(self._name_color)
        self._name_item.setFont(self._name_font)
        self._name_item.setTextWidth(self.width - 2 * self.padding)
        self._name_item.setPos(
            self.padding,
            self.name_height / 2 - self._name_item.boundingRect().height() / 2,
        )

    @property
    def height(self):
        """Height of the graphics component."""
        return self.name_height + self.bottom_padding + 25 * len(self.component.ports())

    def register_port(self, graphics_port: GraphicsPort) -> None:
        """Register a graphics port to this graphics component.

        Args:
            graphics_port: Graphics port to register.
        """
        index = len(self._ports)
        graphics_port.setParentItem(self)
        graphics_port.setPos(
            0,
            self.name_height + graphics_port.height * index,
        )
        self._ports[graphics_port.uuid()] = graphics_port

    def unregister_port(self, uuid: UUID) -> None:
        """Unregister a graphics port from this graphics component.

        Args:
            uuid: UUID of the port to unregister.
        """
        self._ports.pop(uuid)

    def uuid(self) -> UUID:
        """UUID of this graphics component."""
        return self.component.uuid()

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            +self.width,
            +self.height,
        )

    def itemChange(
        self,
        change: QGraphicsItem.GraphicsItemChange,
        value: Any,
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.setZValue(1)
            else:
                self.setZValue(0)
        return super().itemChange(change, value)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:

        # Background
        path_background = QPainterPath()
        path_background.addRoundedRect(
            0,
            0,
            self.width,
            self.height,
            self.corner_radius,
            self.corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_background.simplified())

        # name
        path_name = QPainterPath()
        path_name.setFillRule(Qt.WindingFill)
        path_name.addRoundedRect(
            0,
            0,
            self.width,
            self.name_height,
            self.corner_radius,
            self.corner_radius,
        )
        path_name.addRect(
            0,
            self.name_height - self.corner_radius,
            self.corner_radius,
            self.corner_radius,
        )
        path_name.addRect(
            self.width - self.corner_radius,
            self.name_height - self.corner_radius,
            self.corner_radius,
            self.corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_name)
        painter.drawPath(path_name.simplified())

        path_background = QPainterPath()
        path_background.addRoundedRect(
            0,
            0,
            self.width,
            self.height,
            self.corner_radius,
            self.corner_radius,
        )
        pen = self._pen_default if not self.isSelected() else self._pen_selected
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_background.simplified())
