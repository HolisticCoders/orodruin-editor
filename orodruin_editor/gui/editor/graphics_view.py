from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtCore import QEvent, QRectF, Qt
from PySide2.QtGui import (
    QBrush,
    QFont,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QWheelEvent,
)
from PySide2.QtWidgets import QGraphicsView

if TYPE_CHECKING:
    from orodruin_editor.gui.editor_window import OrodruinEditorWindow


class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    def __init__(
        self,
        window: OrodruinEditorWindow,
    ) -> None:
        super().__init__(parent=window)

        self.window = window
        self.zoom_in_factor = 1.25
        self.zoom_step = 1

        self._path_font = QFont("Roboto", 20)

        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            press_event = QMouseEvent(
                QEvent.MouseButtonPress,
                event.localPos(),
                event.screenPos(),
                Qt.LeftButton,
                Qt.NoButton,
                event.modifiers(),
            )
            self.mousePressEvent(press_event)

        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
        else:
            zoom_factor = 1 / self.zoom_in_factor
        self.scale(zoom_factor, zoom_factor)

    def drawForeground(
        self,
        painter: QPainter,
        rect: QRectF,  # pylint: disable=unused-argument
    ) -> None:
        area = self.mapToScene(self.viewport().geometry()).boundingRect()

        path_name = QPainterPath()
        path_name.addText(
            area.x() + 25,
            area.y() + 40,
            self._path_font,
            str(self.scene().graph.parent_component().path()),
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.darkGray))
        painter.drawPath(path_name)
