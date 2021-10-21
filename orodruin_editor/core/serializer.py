from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

import attr
from orodruin.core.serializer import ExternalSerializer

if TYPE_CHECKING:
    from orodruin_editor.ui.editor.graphics_state import GraphicsState
    from orodruin.core import Node, Connection, Graph, Port


@attr.s
class EditorSerializer(ExternalSerializer):
    """Serialize nodes editor state."""

    graphics_state: GraphicsState = attr.ib()

    def serialize_graph(self, graph: Graph) -> Dict[str, Any]:
        return {}

    def serialize_node(self, node: Node) -> Dict[str, Any]:
        graphics_node = self.graphics_state.get_graphics_node(node)
        return {
            "editor": {
                "position": [graphics_node.pos().x(), graphics_node.pos().y()],
            },
        }

    def serialize_port(self, port: Port) -> Dict[str, Any]:
        return {}

    def serialize_connection(
        self, connection: Connection, parent_node: Node
    ) -> Dict[str, Any]:
        return {}
