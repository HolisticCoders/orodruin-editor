from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from orodruin.port.port import Port, PortDirection
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)


class GraphicsPort(QGraphicsItem):
    def __init__(self, port: Port, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent=parent)

        self.port = port

        self.width = 175
        self.height = 25
        self.radius = 5
        self.padding = 10

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self._color_outline = Qt.black
        self._color_background = QColor("#7A996B")

        self._pen = QPen(self._color_outline)
        self._pen.setWidth(1)
        self._brush = QBrush(self._color_background)

        self.init_ui()

    def init_ui(self):
        pass

    def init_name(self):
        self.name_item = QGraphicsTextItem(self.port.name(), self)
        self.name_item.setDefaultTextColor(self._name_color)
        self.name_item.setFont(self._name_font)
        self.name_item.setPos(self.padding, 0)
        self.name_item.setTextWidth(self.width - 2 * self.padding)

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
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        path_name = QPainterPath()
        path_name.addText(
            0,
            0,
            self._name_font,
            self.port.name(),
        )

        horizontal_offset = (
            self.padding
            if self.port.direction() is PortDirection.input
            else self.width - path_name.boundingRect().width() - self.padding
        )
        path_name.translate(
            horizontal_offset,
            -2 + self._name_font.pointSize() / 2.0 + self.height / 2,
        )
        path_name.boundingRect
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)

        horizontal_offset = (
            0 if self.port.direction() is PortDirection.input else self.width
        )
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(
            -self.radius + horizontal_offset,
            -self.radius + self.height / 2,
            2 * self.radius,
            2 * self.radius,
        )