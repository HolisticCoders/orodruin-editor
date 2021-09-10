from typing import Optional

from PySide2.QtCore import QPointF
from PySide2.QtGui import QPainter, QPainterPath, QPen, Qt
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)


class GraphicsConnection(QGraphicsPathItem):
    def __init__(
        self,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.source_position = (0, 0)
        self.destination_position = (100, 100)

        self._unselected_pen = QPen(Qt.black)
        self._selected_pen = QPen(Qt.yellow)
        self._unselected_pen.setWidth(2)
        self._selected_pen.setWidth(2)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:
        self.update_path()
        pen = self._unselected_pen if not self.isSelected() else self._selected_pen
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def update_path(self):
        path = QPainterPath(QPointF(self.source_position[0], self.source_position[1]))
        path.lineTo(self.destination_position[0], self.destination_position[1])
        self.setPath(path)
