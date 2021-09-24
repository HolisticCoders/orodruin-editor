from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import orodruin.commands
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QListView, QWidget

if TYPE_CHECKING:
    from .graphics_scene import GraphicsScene


class ComponentListView(QListView):
    """Component List View."""

    def __init__(self, scene: GraphicsScene, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._scene = scene

        self.doubleClicked.connect(self.on_double_click_item)

    def on_double_click_item(self, index: Optional[QModelIndex] = None) -> None:
        """Import the component double clicked component."""
        if not index:
            return

        component = self.model().components()[index.row()]

        command = orodruin.commands.ImportComponent(
            self._scene.scene(),
            self._scene.active_graph().uuid(),
            component.path.stem,
            component.library_name,
        )
        command.do()
