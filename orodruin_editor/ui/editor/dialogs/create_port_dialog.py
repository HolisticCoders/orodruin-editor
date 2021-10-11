from typing import Optional

from orodruin.core import PortDirection, PortTypes
from orodruin.core.port.types import PortType
from PySide2.QtCore import Qt
from PySide2.QtGui import Qt
from PySide2.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CreatePortDialog(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        f: Qt.WindowFlags = None,
    ) -> None:
        super().__init__()

        self.setWindowTitle("Create Port")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._port_name_layout = QHBoxLayout()
        layout.addLayout(self._port_name_layout)
        self._port_name_label = QLabel("Name")
        self._port_name_lineedit = QLineEdit()
        self._port_name_layout.addWidget(self._port_name_label)
        self._port_name_layout.addWidget(self._port_name_lineedit)

        self._port_direction_layout = QHBoxLayout()
        layout.addLayout(self._port_direction_layout)
        self._port_direction_label = QLabel("Direction")
        self._port_direction_combobox = QComboBox()
        self._port_direction_combobox.addItems(
            [direction.value for direction in PortDirection]
        )
        self._port_direction_layout.addWidget(self._port_direction_label)
        self._port_direction_layout.addWidget(self._port_direction_combobox)

        self._port_type_layout = QHBoxLayout()
        layout.addLayout(self._port_type_layout)
        self._port_type_label = QLabel("Direction")
        self._port_type_combobox = QComboBox()
        self._port_type_combobox.addItems(
            [port_type.value.__name__ for port_type in PortTypes]
        )
        self._port_type_layout.addWidget(self._port_type_label)
        self._port_type_layout.addWidget(self._port_type_combobox)

        self._buttons_layout = QHBoxLayout()
        layout.addLayout(self._buttons_layout)
        self._ok_button = QPushButton("OK")
        self._cancel_button = QPushButton("Cancel")
        self._buttons_layout.addWidget(self._ok_button)
        self._buttons_layout.addWidget(self._cancel_button)
        self._ok_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)

    def port_name(self) -> str:
        return self._port_name_lineedit.text()

    def port_direction(self) -> PortDirection:
        return PortDirection(self._port_direction_combobox.currentText())

    def port_type(self) -> PortType:
        return PortTypes[self._port_type_combobox.currentText()].value
