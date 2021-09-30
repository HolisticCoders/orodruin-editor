from typing import Optional

import orodruin.commands
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QListView, QWidget

from .editor.graphics_state import GraphicsState


class NodeListView(QListView):
    """Node List View."""

    def __init__(
        self, graphics_state: GraphicsState, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent=parent)
        self._graphics_state = graphics_state
        self.doubleClicked.connect(self.on_double_click_item)

    def on_double_click_item(self, index: Optional[QModelIndex] = None) -> None:
        """Import the node double clicked node."""
        if not index:
            return

        node = self.model().nodes()[index.row()]

        command = orodruin.commands.ImportNode(
            self._graphics_state.state(),
            self._graphics_state.active_graph().uuid(),
            node.path.stem,
            node.library_name,
        )
        command.do()
