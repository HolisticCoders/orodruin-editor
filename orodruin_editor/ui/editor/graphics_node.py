from dataclasses import dataclass, field
from typing import Optional, Union
from uuid import UUID

from orodruin.core.node import NodeLike
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QPainter, QPainterPath
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


@dataclass
class GraphicsNode(QGraphicsItem):

    _uuid: UUID
    _parent: Optional[QGraphicsItem] = None

    _header_height: int = field(init=False, default=5)

    _background_color: QColor = field(init=False)
    _background_brush: QBrush = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self._background_color = QColor("#333333")
        self._brush_background = QBrush(self._background_color)

    def width(self) -> int:
        return 150

    def height(self) -> int:
        return 150

    def boundingRect(self) -> QRectF:
        return QRectF(
            0,
            0,
            self.width(),
            self.height(),
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # pylint: disable=unused-argument
        widget: Optional[QWidget],  # pylint: disable=unused-argument
    ) -> None:

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


GraphicsNodeLike = Union[GraphicsNode, NodeLike]

__all__ = [
    "GraphicsNode",
    "GraphicsNodeLike",
]
