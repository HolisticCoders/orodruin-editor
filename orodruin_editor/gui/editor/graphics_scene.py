from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from orodruin.core import Component, Connection, Graph, Port
from orodruin.core.port.port import PortDirection
from PySide2.QtCore import QLine, QObject, QRectF
from PySide2.QtGui import QColor, QPainter, QPen
from PySide2.QtWidgets import QGraphicsScene

from .graphics_component import GraphicsComponent
from .graphics_connection import GraphicsConnection
from .graphics_port import GraphicsPort

if TYPE_CHECKING:
    from ..editor_window import OrodruinEditorWindow


logger = logging.getLogger(__name__)


class GraphicsScene(QGraphicsScene):
    """Graphical representation of an Orodruin Graph."""

    def __init__(
        self,
        window: OrodruinEditorWindow,
        graph: Graph,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.window = window

        self._graph = graph
        self._graph.component_registered.subscribe(self.register_component)
        self._graph.component_unregistered.subscribe(self.unregister_component)
        self._graph.port_registered.subscribe(self.register_port)
        self._graph.port_unregistered.subscribe(self.unregister_port)
        self._graph.connection_registered.subscribe(self.register_connection)
        self._graph.connection_unregistered.subscribe(self.unregister_connection)

        self._graphics_components: Dict[UUID, GraphicsComponent] = {}
        self._graphics_ports: Dict[UUID, GraphicsPort] = {}
        self._graphics_connections: Dict[UUID, GraphicsConnection] = {}

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

        self._init_content()

    def _init_content(self):
        """Create all the graphics components, ports and connections in the graph."""
        self._create_input_output_components()

        for component in self._graph.components():
            self.register_component(component)

        for port in self._graph.ports():
            self.register_port(port)

        for connection in self._graph.connections():
            self.register_connection(connection)

    def _create_input_output_components(self):
        parent_component = self._graph.parent_component()
        if not parent_component:
            return

        input_component = GraphicsComponent("Input")
        self.addItem(input_component)

        output_component = GraphicsComponent("Output")
        self.addItem(output_component)

        for port in parent_component.ports():
            if port.direction() is PortDirection.input:
                component = input_component
                port_direction = PortDirection.output
            else:
                component = output_component
                port_direction = PortDirection.input

            graphics_port = GraphicsPort(
                port.name(),
                port_direction,
                port.type(),
                component,
                port.uuid(),
            )
            self._graphics_ports[port.uuid()] = graphics_port
            component.add_graphics_port(graphics_port)

    def graph(self) -> Graph:
        """Return the graph this Scene represents."""
        return self._graph

    def register_component(self, component: Component) -> None:
        """Register a graphics component to the scene.

        Args:
            component: Orodruin Component to register a graphics component for.
        """
        graphics_component = GraphicsComponent.from_component(component)
        self.addItem(graphics_component)
        self._graphics_components[component.uuid()] = graphics_component
        self.window.components[component.uuid()] = component
        self.window.graphs[component.graph().uuid()] = component.graph()

    def unregister_component(self, component: Component) -> None:
        """Unregister a component from the scene

        Args:
            uuid: UUID of the Orodruin Component.
        """
        graphics_component = self._graphics_components.pop(component.uuid())
        self.removeItem(graphics_component)
        del self.window.components[component.uuid()]
        del self.window.graphs[component.graph().uuid()]

    def register_port(self, port: Port) -> None:
        """Register a graphics port to the scene.

        Args:
            port: Orodruin Port to register a graphics port for.
        """
        graphics_component = self._graphics_components[port.component().uuid()]
        graphics_port = GraphicsPort.from_port(port, graphics_component)
        graphics_component.add_graphics_port(graphics_port)
        self._graphics_ports[port.uuid()] = graphics_port
        self.window.ports[port.uuid()] = port

    def unregister_port(self, port: Port) -> None:
        """Unregister a graphics port from the scene.

        Args:
            uuid: UUID of the Orodruin Port.
        """
        graphics_port = self._graphics_ports.pop(port.uuid())
        graphics_component = graphics_port.graphics_component()
        graphics_component.remove_graphics_port(port.uuid())
        self.removeItem(graphics_port)
        del self.window.ports[port.uuid()]

    def register_connection(self, connection: Connection) -> None:
        """Register a graphics connection to the scene.

        Args:
            connection: Orodruin Connection to register a graphics connection for.
        """
        # TODO: Fix connections not created to the parent component
        try:
            source_id = connection.source().uuid()
            target_id = connection.target().uuid()

            source_graphics_port = self._graphics_ports[source_id]
            target_graphics_port = self._graphics_ports[target_id]

            graphics_connection = GraphicsConnection(
                source_graphics_port, target_graphics_port
            )
            self.addItem(graphics_connection)
            self._graphics_connections[connection.uuid()] = graphics_connection
            self.window.connections[connection.uuid()] = connection
        except Exception:
            logger.error(
                "Could not create graphical connection between "
                f"{connection.source().path()} and {connection.source().path()}"
            )

    def unregister_connection(self, connection: Connection) -> None:
        """Unregister a graphics connection from the scene.

        Args:
            uuid: UUID of the Orodruin Connection.
        """
        try:
            graphics_connection = self._graphics_connections.pop(connection.uuid())
            self.removeItem(graphics_connection)
            del self.window.connections[connection.uuid()]
        except Exception:
            logger.error(
                "Could not delete graphical connection between "
                f"{connection.source().path()} and {connection.source().path()}"
            )

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
