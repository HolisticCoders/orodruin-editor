import logging
from dataclasses import dataclass, field
from typing import Dict, Union
from uuid import UUID

from orodruin.core import Scene
from orodruin.core.component import Component, ComponentLike
from orodruin.core.connection import Connection, ConnectionLike
from orodruin.core.graph import Graph, GraphLike
from orodruin.core.port.port import Port, PortLike

from orodruin_editor.gui.editor.graphics_view import GraphicsView

from .graphics_component import GraphicsComponent
from .graphics_connection import GraphicsConnection
from .graphics_graph import GraphicsGraph
from .graphics_port import GraphicsPort

logger = logging.getLogger(__name__)
print(logger)

GraphicsGraphLike = Union[GraphicsGraph, GraphLike]
GraphicsComponentLike = Union[GraphicsComponent, ComponentLike]
GraphicsPortLike = Union[GraphicsPort, PortLike]
GraphicsConnectionLike = Union[GraphicsConnection, ConnectionLike]


@dataclass
class GraphicsScene:
    """Scene object that tracks all the graphics items created

    This is not a QGraphicsScene subclass. Just something to manage graphics items.
    for all the GraphicsGraph (which are QGraphicsScene).
    """

    _scene: Scene
    _view: GraphicsView

    _active_graph_id: UUID = field(init=False)
    _graphics_graphs: Dict[UUID, GraphicsGraph] = field(
        init=False, default_factory=dict
    )
    _graphics_components: Dict[UUID, GraphicsComponent] = field(
        init=False, default_factory=dict
    )
    _graphics_ports: Dict[UUID, GraphicsPort] = field(init=False, default_factory=dict)
    _graphics_connections: Dict[UUID, GraphicsConnection] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        self._scene.graph_created.subscribe(self.create_graphics_graph)
        self._scene.graph_deleted.subscribe(self.delete_graphics_graph)
        self._scene.component_created.subscribe(self.create_component)
        self._scene.component_deleted.subscribe(self.delete_component)
        self._scene.port_created.subscribe(self.create_port)
        self._scene.port_deleted.subscribe(self.delete_port)
        self._scene.connection_created.subscribe(self.create_connection)
        self._scene.connection_deleted.subscribe(self.delete_connection)

        for graph in self._scene.graphs():
            self.create_graphics_graph(graph)

        self.set_active_graph(self.root_graph())

    def scene(self) -> Scene:
        """Return the orodruin scene of the graphics scene."""
        return self._scene

    def root_graph(self):
        """Return the root graphics graph of the scene."""
        return self.get_graphics_graph(self._scene.root_graph())

    def active_graph(self) -> GraphicsGraph:
        """Return the active graphics graph."""
        return self.get_graphics_graph(self._active_graph_id)

    def set_active_graph(self, graph: GraphLike):
        """Set the view's scene to the given graph"""
        graph = self.get_graphics_graph(graph)
        self._active_graph_id = graph.uuid()
        self._view.setScene(self.active_graph())

    def get_graphics_graph(self, graph: GraphicsGraphLike) -> GraphicsGraph:
        """Return a graphics graph from a GraphicsGraphLike object.

        Raises:
            TypeError: When the graph is not a valid GraphicsGraphLike object.
        """
        if isinstance(graph, GraphicsGraph):
            pass
        elif isinstance(graph, Graph):
            graph = self._graphics_graphs[graph.uuid()]
        elif isinstance(graph, UUID):
            graph = self._graphics_graphs[graph]
        else:
            raise TypeError(
                f"{type(graph)} is not a valid GraphicsGraphLike type. "
                "Expected Union[GraphicsGraph, Graph, UUID]"
            )

        return graph

    def get_graphics_component(
        self, component: GraphicsComponentLike
    ) -> GraphicsComponent:
        """Return a graphics component from a GraphicsComponentLike object.

        Raises:
            TypeError: When the graph is not a valid GraphicsComponentLike object.
        """
        if isinstance(component, GraphicsComponent):
            pass
        elif isinstance(component, Component):
            component = self._graphics_components[component.uuid()]
        elif isinstance(component, UUID):
            component = self._graphics_components[component]
        else:
            raise TypeError(
                f"{type(component)} is not a valid GraphicsComponentLike type. "
                "Expected Union[GraphicsComponent, Component, UUID]"
            )

        return component

    def get_graphics_port(self, port: GraphicsPortLike) -> GraphicsPort:
        """Return a graphics port from a GraphicsPortLike object.

        Raises:
            TypeError: When the graph is not a valid GraphicsPortLike object.
        """
        if isinstance(port, GraphicsGraph):
            pass
        elif isinstance(port, Graph):
            port = self._graphics_ports[port.uuid()]
        elif isinstance(port, UUID):
            port = self._graphics_ports[port]
        else:
            raise TypeError(
                f"{type(port)} is not a valid GraphicsPortLike type. "
                "Expected Union[GraphicsPort, Port, UUID]"
            )

        return port

    def get_graphics_connection(
        self, connection: GraphicsConnectionLike
    ) -> GraphicsConnection:
        """Return a graphics connection from a GraphicsConnectionLike object.

        Raises:
            TypeError: When the graph is not a valid GraphLike object.
        """
        if isinstance(connection, GraphicsGraph):
            pass
        elif isinstance(connection, Graph):
            connection = self._graphics_connections[connection.uuid()]
        elif isinstance(connection, UUID):
            connection = self._graphics_connections[connection]
        else:
            raise TypeError(
                f"{type(connection)} is not a valid GraphicsConnectionLike type. "
                "Expected Union[GraphicsConnection, Connection, UUID]"
            )

        return connection

    def create_graphics_graph(self, graph: Graph) -> GraphicsGraph:
        """Create graphics graph and register it to the scene."""
        graphics_graph = GraphicsGraph(self, graph)
        self._graphics_graphs[graph.uuid()] = graphics_graph
        logger.debug("Created graphics graph %s", graph.uuid())

    def delete_graphics_graph(self, uuid: UUID) -> None:
        """Delete a graphics graph and unregister it from the scene."""

    def create_component(self, component: Component) -> GraphicsComponent:
        """Create graphics component and register it to the scene."""
        graphics_component = GraphicsComponent.from_component(component)
        self._graphics_components[component.uuid()] = graphics_component
        logger.debug("Created graphics component %s", component.path())

    def delete_component(self, uuid: UUID) -> None:
        """Delete a graphics component and unregister it from the scene."""

    def create_port(self, port: Port) -> GraphicsPort:
        """Delete a graphics port and unregister it from the scene."""
        graphics_port = port = GraphicsPort.from_port(port)

        logger.debug("Created graphics port %s", port.path())

    def delete_port(self, uuid: UUID) -> None:
        """Delete a graphics port and unregister it from the scene."""

    def create_connection(self, connection: Connection) -> GraphicsConnection:
        """Delete a graphics connection and unregister it from the scene."""
        logger.debug("Created graphics connection %s", connection.uuid())

    def delete_connection(self, uuid: UUID) -> None:
        """Delete a graphics connection and unregister it from the scene."""
