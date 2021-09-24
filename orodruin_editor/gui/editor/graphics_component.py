from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from orodruin.core.component import Component, ComponentLike
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from .graphics_component_name import GraphicsComponentName
from .graphics_port import GraphicsPortLike

if TYPE_CHECKING:
    from .graphics_scene import GraphicsScene


class GraphicsComponent(QGraphicsItem):
    """Graphical representation of an Orodruin Component."""

    @classmethod
    def from_component(
        cls,
        scene: GraphicsScene,
        component: Component,
        parent: Optional[QGraphicsItem] = None,
    ) -> GraphicsComponent:
        """Create a GraphicsComponent from an orodruin Component."""
        graphics_component = cls(scene, component.name(), component.uuid(), parent)

        component.port_registered.subscribe(graphics_component.register_graphics_port)
        component.port_unregistered.subscribe(
            graphics_component.unregister_graphics_port
        )

        return graphics_component

    def __init__(
        self,
        scene: GraphicsScene,
        name: str,
        uuid: Optional[UUID] = None,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent=parent)

        self._scene = scene

        self._name = name
        if not uuid:
            uuid = uuid4()
        self._uuid = uuid

        self._graphics_ports: List[UUID] = []

        self._width = 150
        self._header_height = 5
        self._corner_radius = self._header_height / 2
        self.padding = 5
        self.bottom_padding = 5

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self._outline_pen_default = Qt.NoPen
        self._outline_pen_selected = QPen(Qt.white)
        self._outline_pen_selected.setWidth(self._header_height)

        self._brush_header = QBrush(QColor("#2B6299"))
        self._brush_background = QBrush(QColor("#333333"))

        self.name_item = GraphicsComponentName(self)

    def name(self) -> None:
        """Return the name of this Graphics Component."""
        return self._name

    def set_name(self, value: str) -> None:
        """Set the name of this Graphics Component."""
        self._name = value

    def uuid(self) -> UUID:
        """Return this Graphics component's UUID."""
        return self._uuid

    def height(self):
        """Height of the graphics component."""
        return (
            self._header_height + self.bottom_padding + 25 * len(self._graphics_ports)
        )

    def width(self):
        """Height of the graphics component."""
        return self._width

    def register_graphics_port(self, graphics_port: GraphicsPortLike) -> None:
        """Register a graphics port to this graphics component."""
        graphics_port = self._scene.get_graphics_port(graphics_port)
        index = len(self._graphics_ports)
        graphics_port.setParentItem(self)
        graphics_port.setPos(
            0,
            self._header_height + graphics_port.height() * index,
        )
        self._graphics_ports.append(graphics_port.uuid())

    def unregister_graphics_port(self, uuid: UUID) -> None:
        """Unregister a graphics port from this graphics component.

        Args:
            uuid: UUID of the port to unregister.
        """
        self._graphics_ports.pop(uuid)

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            +self.width(),
            +self.height(),
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

        # Outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            self._corner_radius,
            self._corner_radius,
        )
        painter.setClipPath(path_outline)

        # Header
        path_header = QPainterPath()
        path_header.setFillRule(Qt.WindingFill)
        path_header.addRoundedRect(
            0,
            0,
            self.width(),
            self._header_height,
            self._corner_radius,
            self._corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_header)
        painter.drawPath(path_header.simplified())

        # Footer
        path_header = QPainterPath()
        path_header.setFillRule(Qt.WindingFill)
        path_header.addRoundedRect(
            0,
            self.height() - self._header_height,
            self.width(),
            self._header_height,
            self._corner_radius,
            self._corner_radius,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_header.simplified())

        # Body
        path_body = QPainterPath()
        path_body.addRect(
            0,
            self._header_height / 2,
            self.width(),
            self.height() - self._header_height / 2,
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


GraphicsComponentLike = Union[GraphicsComponent, ComponentLike]

__all__ = [
    "GraphicsComponent",
    "GraphicsComponentLike",
]
