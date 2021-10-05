from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QPainter
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from .layout_item import LayoutItem


@dataclass
class VerticalGraphicsLayout(LayoutItem):
    _parent: Optional[QGraphicsItem] = None

    _children: List[LayoutItem] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow]
        self._color = colors[random.randint(0, 3)]

    def add_item(self, item: LayoutItem):
        self._children.append(item)
        item.setParentItem(self)
        self.reorder_children()

    def reorder_children(self):
        y = 0
        for child in self._children:
            _y = y if child.isVisible() else 0
            child.setPos(0, _y)
            y += child.effective_bounding_rect().height()

    def effective_bounding_rect(self) -> QRectF:
        if self.isVisible():
            width = 150
            height = 0
            for child in self.childItems():
                height += child.effective_bounding_rect().height()
            return QRectF(0, 0, width, height)
        else:
            return QRectF(0, 0, 0, 0)

    def boundingRect(self) -> QRectF:
        return self.effective_bounding_rect()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:
        self.reorder_children()

        # painter.setPen(Qt.NoPen)
        # painter.setBrush(QBrush(self._color))
        # painter.drawRect(self.boundingRect())
