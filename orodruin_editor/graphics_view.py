from typing import Optional

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QMouseEvent, QPainter, QWheelEvent
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QWidget


class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    def __init__(
        self,
        scene: QGraphicsScene,
        parent: Optional[QWidget],
    ) -> None:
        super().__init__(scene, parent=parent)

        self.setScene(scene)

        self.zoom_in_factor = 1.25
        self.zoom_step = 1

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
