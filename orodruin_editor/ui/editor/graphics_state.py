from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List
from uuid import UUID

import attr
from orodruin.core import Connection, Graph, Node, Port, State
from orodruin.core.signal import Signal

from orodruin_editor.core import EditorDeserializer, EditorSerializer

from .graphics_graph import GraphicsGraph, GraphicsGraphLike
from .graphics_items.graphics_connection import (
    GraphicsConnection,
    GraphicsConnectionLike,
)
from .graphics_items.graphics_node import GraphicsNode, GraphicsNodeLike
from .graphics_items.graphics_port import GraphicsPort, GraphicsPortLike

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .graphics_view import GraphicsView


@attr.s
class GraphicsState:
    _state: State = attr.ib()
    _view: GraphicsView = attr.ib()

    selection_changed: Signal[List[UUID]] = attr.ib(init=False, factory=Signal)
    _active_graph: GraphicsGraph = attr.ib(init=False)
    _root_graph: GraphicsGraph = attr.ib(init=False)

    _graphics_graphs: Dict[UUID, GraphicsGraph] = attr.ib(init=False, factory=dict)
    _graphics_nodes: Dict[UUID, GraphicsNode] = attr.ib(init=False, factory=dict)
    _graphics_ports: Dict[UUID, GraphicsPort] = attr.ib(init=False, factory=dict)
    _graphics_connections: Dict[UUID, GraphicsConnection] = attr.ib(
        init=False, factory=dict
    )

    def __attrs_post_init__(self) -> None:
        self._state.graph_created.subscribe(self.create_graphics_graph)
        self._state.graph_deleted.subscribe(self.delete_graphics_graph)
        self._state.node_created.subscribe(self.create_graphics_node)
        self._state.node_deleted.subscribe(self.delete_graphics_node)
        self._state.port_created.subscribe(self.create_graphics_port)
        self._state.port_deleted.subscribe(self.delete_graphics_port)
        self._state.connection_created.subscribe(self.create_graphics_connection)
        self._state.connection_deleted.subscribe(self.delete_graphics_connection)

        self._root_graph = self.create_graphics_graph(self._state.root_graph())
        self.set_active_graph(self._root_graph)

        deserializer = EditorDeserializer(self)
        serializer = EditorSerializer(self)
        self._state.register_deserializer(deserializer)
        self._state.register_serializer(serializer)

    def state(self) -> State:
        return self._state

    def set_active_graph(self, graph: GraphicsGraphLike) -> None:
        graph = self.get_graphics_graph(graph)
        self._active_graph = graph
        self._view.setScene(self._active_graph)

    def active_graph(self) -> GraphicsGraph:
        return self._active_graph

    def get_graphics_graph(self, graph: GraphicsGraphLike) -> GraphicsGraph:
        """Return a registered graphics graph from a GraphicsGraphLike object."""
        if isinstance(graph, UUID):
            graphics_graph = self._graphics_graphs[graph]
        elif isinstance(graph, Graph):
            graphics_graph = self._graphics_graphs[graph.uuid()]
        elif isinstance(graph, GraphicsGraph):
            graphics_graph = graph

        return graphics_graph

    def get_graphics_node(self, node: GraphicsNodeLike) -> GraphicsNode:
        """Return a registered graphics node from a GraphicsNodeLike object."""
        if isinstance(node, UUID):
            graphics_node = self._graphics_nodes[node]
        elif isinstance(node, Node):
            graphics_node = self._graphics_nodes[node.uuid()]
        elif isinstance(node, GraphicsNode):
            graphics_node = node
        else:
            raise TypeError

        return graphics_node

    def get_graphics_port(self, port: GraphicsPortLike) -> GraphicsPort:
        """Return a registered graphics port from a GraphicsPortLike object."""
        if isinstance(port, UUID):
            graphics_port = self._graphics_ports[port]
        elif isinstance(port, Port):
            graphics_port = self._graphics_ports[port.uuid()]
        elif isinstance(port, GraphicsPort):
            graphics_port = port
        else:
            raise TypeError

        return graphics_port

    def get_graphics_connection(
        self, connection: GraphicsConnectionLike
    ) -> GraphicsPort:
        """Return a registered graphics connection from a GraphicsConnectionLike object."""
        if isinstance(connection, UUID):
            graphics_connection = self._graphics_connections[connection]
        elif isinstance(connection, Connection):
            graphics_connection = self._graphics_connections[connection.uuid()]
        elif isinstance(connection, GraphicsConnection):
            graphics_connection = connection
        else:
            raise TypeError

        return graphics_connection

    def get_graph(self, graph: GraphicsGraphLike) -> Graph:
        """Return a registered graph from a GraphicsGraphLike object."""
        if isinstance(graph, UUID):
            graph = self._state.get_graph(graph)
        elif isinstance(graph, GraphicsGraph):
            graph = self._state.get_graph(graph.uuid())
        elif isinstance(graph, Graph):
            pass
        else:
            raise TypeError

        return graph

    def get_node(self, node: GraphicsNodeLike) -> Node:
        """Return a registered node from a GraphicsNodeLike object."""
        if isinstance(node, UUID):
            node = self._state.get_node(node)
        elif isinstance(node, GraphicsNode):
            node = self._state.get_node(node.uuid())
        elif isinstance(node, Node):
            pass
        else:
            raise TypeError

        return node

    def create_graphics_graph(self, graph: Graph) -> GraphicsGraph:
        """Create a graphics graph and register it to the graphics state."""
        graphics_graph = GraphicsGraph.from_graph(self, graph)
        self._graphics_graphs[graph.uuid()] = graphics_graph
        logger.debug("Created graphics graph %s.", graph.uuid())
        return graphics_graph

    def delete_graphics_graph(self, uuid: UUID) -> None:
        """Delete a graphics graph and unregister it from the graphics state."""
        del self._graphics_graphs[uuid]
        logger.debug("Deleted graphics graph %s.", uuid)

    def create_graphics_node(self, node: Node) -> GraphicsNode:
        """Create a graphics node and register it to the graphics state."""
        graphics_node = GraphicsNode.from_node(self, node)
        self._graphics_nodes[node.uuid()] = graphics_node

        node_pos = self._view.mapToScene(self._view.viewport().rect().center())
        graphics_node.setPos(node_pos)

        logger.debug("Created graphics node %s.", node.uuid())
        return graphics_node

    def delete_graphics_node(self, uuid: UUID) -> None:
        """Delete a graphics node and unregister it from the graphics state."""
        del self._graphics_nodes[uuid]
        logger.debug("Deleted graphics node %s.", uuid)

    def create_graphics_port(self, port: Port) -> GraphicsPort:
        """Create a graphics port and register it to the graphics state."""
        graphics_port = GraphicsPort.from_port(self, port)
        self._graphics_ports[port.uuid()] = graphics_port
        logger.debug("Created graphics port %s.", port.path())
        return graphics_port

    def delete_graphics_port(self, uuid: UUID) -> None:
        """Delete a graphics port and unregister it from the graphics state."""
        graphics_port = self._graphics_ports.pop(uuid)
        logger.debug("Deleted graphics port %s.", uuid)

    def create_graphics_connection(self, connection: Connection) -> GraphicsConnection:
        """Create a graphics connection and register it to the graphics state."""
        graphics_connection = GraphicsConnection.from_connection(self, connection)
        self._graphics_connections[connection.uuid()] = graphics_connection
        logger.debug("Created graphics connection %s.", connection.uuid())
        return graphics_connection

    def delete_graphics_connection(self, uuid: UUID) -> None:
        """Delete a graphics connection and unregister it from the graphics state."""
        del self._graphics_connections[uuid]
        logger.debug("Deleted graphics connection %s.", uuid)
