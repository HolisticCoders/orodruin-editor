import math
from typing import Optional

from PySide2.QtCore import QLine, QObject, QRectF
from PySide2.QtGui import QBrush, QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsScene


class QDMGraphicsScene(QGraphicsScene):
    def __init__(
        self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)

        # settings
        self.scene_width = 64000
        self.scene_height = 64000

        self.square_size = 50  # in pixels
        self.cell_size = 4  # in squares

        self._color_background = QColor("#2f2f2f")
        self._square_color = QColor("#1a1a1a")
        self._cell_color = QColor("#1a1a1a")

        self._pen_square = QPen(self._square_color)
        self._pen_square.setWidth(1)
        self._pen_cell = QPen(self._cell_color)
        self._pen_cell.setWidth(2)

        self.setSceneRect(
            -self.scene_width // 2,
            -self.scene_height // 2,
            self.scene_width,
            self.scene_height,
        )

        self.setBackgroundBrush(self._color_background)

    def drawBackground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.square_size)
        first_top = top - (top % self.square_size)

        square_lines = []
        cell_lines = []
        for x in range(first_left, right, self.square_size):
            if x % (self.square_size * self.cell_size) == 0:
                cell_lines.append(QLine(x, top, x, bottom))
            else:
                square_lines.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.square_size):
            if y % (self.square_size * self.cell_size) == 0:
                cell_lines.append(QLine(left, y, right, y))
            else:
                square_lines.append(QLine(left, y, right, y))

        painter.setPen(self._pen_square)
        painter.drawLines(square_lines)
        painter.setPen(self._pen_cell)
        painter.drawLines(cell_lines)
