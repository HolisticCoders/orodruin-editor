from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

if TYPE_CHECKING:
    from .graphics_node import GraphicsNode


@dataclass
class GraphicsNodeName(QGraphicsItem):
    """Graphical representation of an Orodruin Component."""

    _name: str
    _parent: GraphicsNode

    _name_color: QColor = field(init=False)
    _name_font_family: str = field(init=False, default="Roboto")
    _name_font_size: int = field(init=False, default=10)
    _name_font: QFont = field(init=False)

    _bounding_rect: QRectF = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self._name_color = Qt.white
        self._name_font = QFont(self._name_font_family, self._name_font_size)

        self._bounding_rect = QRectF(0, 0, 0, 0)

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

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
            self._name,
        )
        self._bounding_rect = path_name.boundingRect()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._name_color))
        painter.drawPath(path_name)
