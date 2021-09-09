from typing import Optional

from orodruin.component import Component
from orodruin.port.port import Port
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from orodruin_editor.graphics_port import GraphicsPort


class GraphicsComponent(QGraphicsItem):
    def __init__(
        self, component: Component, parent: Optional[QGraphicsItem] = None
    ) -> None:
        super().__init__(parent=parent)

        self.component = component

        self.width = 175
        self.border_thickness = 10
        self.name_height = 25
        self.padding = 5

        self._pen_default = QPen(QColor("#000000"))
        self._pen_selected = QPen(QColor("#43FCA2"))
        self._pen_selected.setWidth(2)

        self._brush_name = QBrush(QColor("#3F4F81"))
        self._brush_background = QBrush(QColor("#2E4076"))

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self.init_ui()

    @property
    def height(self):
        return self.name_height + 25 * len(self.component.ports())

    def init_ui(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.init_content()

    def init_content(self):
        self.init_name()
        self.init_ports()

    def init_name(self):
        self.name_item = QGraphicsTextItem(self.component.name(), self)
        self.name_item.setDefaultTextColor(self._name_color)
        self.name_item.setFont(self._name_font)
        self.name_item.setPos(self.padding, 0)
        self.name_item.setTextWidth(self.width - 2 * self.padding)

    def init_ports(self):
        for i, port in enumerate(self.component.ports()):
            self.on_port_added(port, i)

    def on_port_added(self, port: Port, index: int):
        graphics_port = GraphicsPort(port, self)
        graphics_port.setPos(
            0,
            self.name_height + graphics_port.height * index,
        )

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            +self.width,
            +self.height,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:
        path_background = QPainterPath()
        path_background.addRoundedRect(
            0,
            0,
            self.width,
            self.height,
            self.border_thickness,
            self.border_thickness,
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
            self.border_thickness,
            self.border_thickness,
        )
        path_name.addRect(
            0,
            self.name_height - self.border_thickness,
            self.border_thickness,
            self.border_thickness,
        )
        path_name.addRect(
            self.width - self.border_thickness,
            self.name_height - self.border_thickness,
            self.border_thickness,
            self.border_thickness,
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
            self.border_thickness,
            self.border_thickness,
        )
        pen = self._pen_default if not self.isSelected() else self._pen_selected
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_background.simplified())
