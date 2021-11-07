from pathlib import Path
from typing import Any, List, Optional

import attr
from orodruin.core import LibraryManager
from PySide2.QtCore import QAbstractListModel, QModelIndex, QObject, Qt


@attr.s
class NodeItem:
    path: Path = attr.ib()
    library_name: str = attr.ib()


class NodeListModel(QAbstractListModel):
    """List model of all the registered orodruin nodes."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

        self._nodes: List[NodeItem] = []
        self.refresh_nodes_list()

    def nodes(self) -> List[NodeItem]:
        """The nodes stored in this model."""
        return self._nodes

    def refresh_nodes_list(self):
        """Refresh the node list."""
        self.beginResetModel()
        self._nodes = []
        for library in LibraryManager.libraries():
            self._nodes.extend(
                [
                    NodeItem(node_path, library.name())
                    for node_path in library.nodes("orodruin")
                ]
            )
        self.endResetModel()

    def rowCount(
        self,
        parent: QModelIndex,  # pylint: disable=unused-argument
    ) -> int:
        return len(self._nodes)

    def data(self, index: QModelIndex, role: int) -> Any:
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._nodes[index.row()].path.stem

        return None
