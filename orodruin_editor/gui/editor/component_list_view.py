from typing import Optional

import orodruin.commands
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QListView, QWidget


class ComponentListView(QListView):
    """Component List View."""

    def __init__(self, window, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.window = window

        self.doubleClicked.connect(self.on_double_click_item)

    def on_double_click_item(self, index: Optional[QModelIndex] = None) -> None:
        """Import the component double clicked component."""
        if not index:
            return

        component = self.model().components()[index.row()]

        command = orodruin.commands.ImportComponent(
            self.window.active_scene.graph,
            component.path.stem,
            component.library_name,
        )
        command.do()
