from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from orodruin import Component, Graph
from orodruin.port.port import Port
from PySide2.QtCore import QLine, QObject, QRectF
from PySide2.QtGui import QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsScene

from orodruin_editor import graphics_component
from orodruin_editor.graphics_component import GraphicsComponent
from orodruin_editor.graphics_port import GraphicsPort


class GraphicsScene(QGraphicsScene):
    def __init__(
        self,
        graph: Graph,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.graph = graph
        self.graph.component_registered.subscribe(self.on_component_registered)
        self.graph.component_unregistered.subscribe(self.on_component_unregistered)
        self.graph.port_registered.subscribe(self.on_port_registered)
        self.graph.port_unregistered.subscribe(self.on_port_unregistered)

        self._components: Dict[UUID, GraphicsComponent] = {}
        self._ports: Dict[UUID, GraphicsPort] = {}
        # self._components: Dict[UUID, GraphicsComponent] = {}

        # settings
        self.square_size = 25  # in pixels
        self.cell_size = 10  # in squares

        self.scene_width = 64000
        self.scene_height = 64000

        self._color_background = QColor("#191919")
        self._square_color = QColor("#2f2f2f")
        self._cell_color = QColor("#2f2f2f")

        self._pen_square = QPen(self._square_color)
        self._pen_square.setWidthF(0.5)
        self._pen_cell = QPen(self._cell_color)
        self._pen_cell.setWidth(2)

        self.setSceneRect(
            -self.scene_width // 2,
            -self.scene_height // 2,
            self.scene_width,
            self.scene_height,
        )

        self.setBackgroundBrush(self._color_background)

    def init_content(self):
        for component in self.component.components():
            self.on_component_registered(component)

    def on_component_registered(self, component: Component):
        self.register_component(component)

    def on_component_unregistered(self, component: Component):
        self.unregister_component(component.uuid())

    def on_port_registered(self, port: Port):
        self.register_port(port)

    def on_port_unregistered(self, port: Port):
        self.unregister_port(port.uuid())

    def register_component(self, component: Component) -> None:
        graphics_component = GraphicsComponent(component)
        self.addItem(graphics_component)
        self._components[component.uuid()] = graphics_component

    def unregister_component(self, uuid: UUID) -> None:
        graphics_component = self._components.pop(uuid)
        self.removeItem(graphics_component)

    def register_port(self, port: Port) -> None:
        graphics_component = self._components[port.component().uuid()]
        graphics_port = GraphicsPort(port, graphics_component)
        # self.addItem(graphics_port)
        graphics_component.register_port(graphics_port)
        self._ports[port.uuid()] = graphics_port

    def unregister_port(self, uuid: UUID) -> None:
        graphics_port = self._ports.pop(uuid)
        graphics_component = graphics_port.graphics_component()
        graphics_component.unregister_port(uuid)
        self.removeItem(graphics_port)

    def drawBackground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.square_size)
        first_top = top - (top % self.square_size)

        square_lines = []
        cell_lines = []
        for x in range(first_left, right, self.square_size):
            if x % (self.square_size * self.cell_size) == 0:
                cell_lines.append(QLine(x, top, x, bottom))
            else:
                square_lines.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.square_size):
            if y % (self.square_size * self.cell_size) == 0:
                cell_lines.append(QLine(left, y, right, y))
            else:
                square_lines.append(QLine(left, y, right, y))

        painter.setPen(self._pen_square)
        painter.drawLines(square_lines)
        painter.setPen(self._pen_cell)
        painter.drawLines(cell_lines)
