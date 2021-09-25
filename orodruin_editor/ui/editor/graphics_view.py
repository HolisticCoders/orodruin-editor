from dataclasses import dataclass, field
from typing import Optional

from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QFont, QMouseEvent, QPainter, QWheelEvent
from PySide2.QtWidgets import QGraphicsView, QWidget

from orodruin_editor.ui.editor.graphics_state import GraphicsState


@dataclass
class GraphicsView(QGraphicsView):
    """GraphicsView for the orodruin editor."""

    _parent: Optional[QWidget] = None

    _zoom_in_factor: float = field(init=False, default=1.25)
    _font_family: str = field(init=False, default="Roboto")
    _font_size: int = field(init=False, default=20)
    _path_font: QFont = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(parent=self._parent)

        self._path_font = QFont(self._font_family, self._font_size)

        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.HighQualityAntialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.on_left_mouse_pressed(event)
        elif event.button() == Qt.RightButton:
            self.on_right_mouse_pressed(event)
        elif event.button() == Qt.MiddleButton:
            self.on_middle_mouse_pressed(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.on_left_mouse_released(event)
        elif event.button() == Qt.RightButton:
            self.on_right_mouse_released(event)
        elif event.button() == Qt.MiddleButton:
            self.on_middle_mouse_released(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            zoom_factor = self._zoom_in_factor
        else:
            zoom_factor = 1 / self._zoom_in_factor
        self.scale(zoom_factor, zoom_factor)

    def on_left_mouse_pressed(self, event: QMouseEvent):
        """Handle left mouse button pressed event."""
        super().mousePressEvent(event)

    def on_right_mouse_pressed(self, event: QMouseEvent):
        """Handle right mouse button pressed event."""
        super().mousePressEvent(event)

    def on_middle_mouse_pressed(self, event: QMouseEvent):
        """Handle middle mouse button pressed event."""
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

    def on_left_mouse_released(self, event: QMouseEvent):
        """Handle left mouse button released event."""
        super().mouseReleaseEvent(event)

    def on_right_mouse_released(self, event: QMouseEvent):
        """Handle right mouse button released event."""
        super().mouseReleaseEvent(event)

    def on_middle_mouse_released(self, event: QMouseEvent):
        """Handle middle mouse button released event."""
        fake_event = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() & ~Qt.LeftButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)
