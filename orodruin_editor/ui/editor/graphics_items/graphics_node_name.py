from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import orodruin.commands
from PySide2.QtCore import QRect, QRectF, Qt
from PySide2.QtGui import QFont, QPainter
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsTextItem,
    QLineEdit,
    QStyleOptionGraphicsItem,
    QWidget,
)

if TYPE_CHECKING:
    from ..graphics_state import GraphicsState
    from .graphics_node import GraphicsNode


class GraphicsNodeName(QGraphicsItem):
    """Graphical representation of an Orodruin Component."""

    def __init__(
        self,
        graphics_state: GraphicsState,
        name: str,
        graphics_node: GraphicsNode,
    ) -> None:
        super().__init__(parent=graphics_node)
        self._graphics_state = graphics_state
        self._name = name
        self._graphics_node = graphics_node

        self._name_color = Qt.white
        self._name_font_family = "Roboto"
        self._name_font_size = 10
        self._name_font = QFont(self._name_font_family, self._name_font_size)

        self._name_item = QGraphicsTextItem(self._name)
        self._name_item.setParentItem(self)
        self._name_item.setFont(self._name_font)
        self._name_item.setDefaultTextColor(self._name_color)
        self._name_item.setPos(0, -self._name_item.boundingRect().height())

        self._proxy_widget = QGraphicsProxyWidget(self)
        self._line_edit = QLineEdit(self._graphics_node.name())
        self._line_edit.editingFinished.connect(self.end_rename)
        self._line_edit.setGeometry(
            QRect(
                0,
                0,
                self._graphics_node.width(),
                20,  # arbitrary value that worked
            )
        )

        self._proxy_widget.setWidget(self._line_edit)
        self._proxy_widget.moveBy(0, -self._proxy_widget.boundingRect().height())
        self._proxy_widget.hide()

    def init_rename(self):
        """Init the rename process"""
        self._line_edit.setText(self.name())
        self._line_edit.selectAll()
        self._line_edit.setFocus()
        self._proxy_widget.show()

    def end_rename(self):
        """End the rename process"""
        self._proxy_widget.hide()
        if not self._line_edit.isModified():
            return

        # Qt sends the editingFinished signal twice.
        # Setting the line_edit as modified prevents anything to run the 2nd time.
        self._line_edit.setModified(False)

        new_name = self._line_edit.text()
        orodruin.commands.RenameNode(
            self._graphics_state.state(),
            self._graphics_node.uuid(),
            new_name,
        ).do()

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name
        self._name_item.setPlainText(name)

    def boundingRect(self) -> QRectF:
        name_bounding_rect = self._name_item.boundingRect()
        return QRectF(
            0,
            -name_bounding_rect.height(),
            name_bounding_rect.width(),
            name_bounding_rect.height(),
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        return
