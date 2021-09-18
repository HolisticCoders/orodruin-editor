from pathlib import Path
from typing import Any, List, Optional

from orodruin.core import LibraryManager
from PySide2.QtCore import QAbstractListModel, QModelIndex, QObject, Qt


class ComponentListModel(QAbstractListModel):
    """List model of all the registered orodruin components."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

        self._components: List[Path] = []
        self.refresh_components_list()

    def refresh_components_list(self):
        """Refresh the component list."""
        self._components = []
        for library in LibraryManager.libraries():
            self._components.extend(library.components("orodruin"))

    def rowCount(
        self,
        parent: QModelIndex,  # pylint: disable=unused-argument
    ) -> int:
        return len(self._components)

    def data(self, index: QModelIndex, role: int) -> Any:
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._components[index.row()].stem

        return None
