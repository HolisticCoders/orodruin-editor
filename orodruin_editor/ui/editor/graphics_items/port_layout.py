from dataclasses import dataclass
from typing import Optional

from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QPainter
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class PortLayout(QGraphicsItem):
    def boundingRect(self) -> QRectF:
        return self.childrenBoundingRect()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        return
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.red))
        painter.drawRect(self.boundingRect())
