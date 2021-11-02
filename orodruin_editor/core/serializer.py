from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import attr
from orodruin.core import SerializationType, Serializer

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, Node, Port

    from orodruin_editor.ui.editor.graphics_state import GraphicsState


@attr.s
class EditorSerializer(Serializer):
    """Serialize nodes editor state."""

    graphics_state: GraphicsState = attr.ib()

    def serialize_graph(
        self,
        graph: Graph,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        return {}

    def serialize_node(
        self,
        node: Node,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        if serialization_type is SerializationType.instance:
            graphics_node = self.graphics_state.get_graphics_node(node)
            data = {
                "editor": {
                    "position": [graphics_node.pos().x(), graphics_node.pos().y()],
                },
            }
        else:
            data = {}
        return data

    def serialize_port(
        self,
        port: Port,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        return {}

    def serialize_connection(
        self,
        connection: Connection,
        parent_node: Node,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        return {}
