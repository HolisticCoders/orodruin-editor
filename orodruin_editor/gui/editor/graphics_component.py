from typing import Any, Dict, Optional
from uuid import UUID

from orodruin.component import Component
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

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
        self.header_height = 10
        self.padding = 5
        self.bottom_padding = 5

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self._outline_pen_default = Qt.NoPen
        self._outline_pen_selected = QPen(Qt.white)
        self._outline_pen_selected.setWidth(2)

        self._brush_header = QBrush(QColor("#2B6299"))
        self._brush_background = QBrush(QColor("#333333"))

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

    @property
    def height(self):
        """Height of the graphics component."""
        return (
            self.header_height + self.bottom_padding + 25 * len(self.component.ports())
        )

    def register_port(self, graphics_port: GraphicsPort) -> None:
        """Register a graphics port to this graphics component.

        Args:
            graphics_port: Graphics port to register.
        """
        index = len(self._ports)
        graphics_port.setParentItem(self)
        graphics_port.setPos(
            0,
            self.header_height + graphics_port.height * index,
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

        # Name
        path_name = QPainterPath()
        path_name.addText(
            0,
            -5,
            self._name_font,
            self.component.name(),
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)

        # Outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            0,
            0,
            self.width,
            self.height,
            self.corner_radius,
            self.corner_radius,
        )
        painter.setClipPath(path_outline)

        # Header
        path_header = QPainterPath()
        path_header.setFillRule(Qt.WindingFill)
        path_header.addRoundedRect(
            0,
            0,
            self.width,
            self.header_height,
            self.corner_radius,
            self.corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_header)
        painter.drawPath(path_header.simplified())

        # Footer
        path_header = QPainterPath()
        path_header.setFillRule(Qt.WindingFill)
        path_header.addRoundedRect(
            0,
            self.height - self.header_height,
            self.width,
            self.header_height,
            self.corner_radius,
            self.corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_header.simplified())

        # Body
        path_body = QPainterPath()
        path_body.addRect(
            0,
            self.header_height / 2,
            self.width,
            self.height - self.header_height / 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_body.simplified())

        # Outline
        outline_pen = (
            self._outline_pen_default
            if not self.isSelected()
            else self._outline_pen_selected
        )
        painter.setPen(outline_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())
