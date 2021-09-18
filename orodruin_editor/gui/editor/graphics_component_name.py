from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import orodruin.commands
from orodruin.core.component import Component
from PySide2.QtCore import QRect, QRectF, Qt
from PySide2.QtGui import QBrush, QFont, QPainter, QPainterPath
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsProxyWidget,
    QLineEdit,
    QStyleOptionGraphicsItem,
    QWidget,
)

if TYPE_CHECKING:
    from .graphics_component import GraphicsComponent


class GraphicsComponentName(QGraphicsItem):
    """Graphical representation of an Orodruin Component."""

    def __init__(self, graphics_component: GraphicsComponent) -> None:
        super().__init__(parent=graphics_component)

        self._name_color = Qt.white
        self._name_font = QFont("Roboto", 10)

        self.graphics_component = graphics_component
        self._bounding_rect = QRectF(0, 0, 0, 0)

        self.proxy_widget = QGraphicsProxyWidget(self)
        self.line_edit = QLineEdit(self.graphics_component.component.name())
        self.line_edit.editingFinished.connect(self.end_rename)
        self.line_edit.setGeometry(
            QRect(
                0,
                0,
                self.graphics_component.width,
                20,  # arbitrary value that worked
            )
        )

        self.proxy_widget.setWidget(self.line_edit)
        self.proxy_widget.moveBy(0, -self.proxy_widget.boundingRect().height())
        self.proxy_widget.hide()

    def component(self) -> Component:
        """Return the name of the orodruin component."""
        return self.graphics_component.component

    def name(self) -> str:
        """Return the name of the orodruin component."""
        return self.component().name()

    def init_rename(self):
        """Init the rename process"""
        self.line_edit.setText(self.name())
        self.line_edit.selectAll()
        self.line_edit.setFocus()
        self.proxy_widget.show()

    def end_rename(self):
        """End the rename process"""
        name = self.line_edit.text()
        orodruin.commands.RenameComponent(self.component(), name).do()
        self.proxy_widget.hide()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def set_bounding_rect(self, rect: QRectF) -> None:
        """Set the bounding rect"""
        self._bounding_rect = rect

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
            self.graphics_component.component.name(),
        )
        self.set_bounding_rect(path_name.boundingRect())
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.white))
        painter.drawPath(path_name)
