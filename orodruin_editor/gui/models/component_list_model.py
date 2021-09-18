from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from orodruin.core import LibraryManager
from PySide2.QtCore import QAbstractListModel, QModelIndex, QObject, Qt


@dataclass
class ComponentItem:
    path: Path
    library_name: str


class ComponentListModel(QAbstractListModel):
    """List model of all the registered orodruin components."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)

        self._components: List[ComponentItem] = []
        self.refresh_components_list()

    def components(self) -> List[ComponentItem]:
        """The components stored in this model."""
        return self._components

    def refresh_components_list(self):
        """Refresh the component list."""
        self._components = []
        for library in LibraryManager.libraries():
            self._components.extend(
                [
                    ComponentItem(component_path, library.name())
                    for component_path in library.components("orodruin")
                ]
            )

    def rowCount(
        self,
        parent: QModelIndex,  # pylint: disable=unused-argument
    ) -> int:
        return len(self._components)

    def data(self, index: QModelIndex, role: int) -> Any:
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._components[index.row()].path.stem

        return None
