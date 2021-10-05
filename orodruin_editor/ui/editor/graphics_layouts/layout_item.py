from PySide2.QtCore import QRectF
from PySide2.QtWidgets import QGraphicsItem


class LayoutItem(QGraphicsItem):
    def effective_bounding_rect(self) -> QRectF:
        """The bounding rect used by the parent layout to position its items."""
        return self.boundingRect()
