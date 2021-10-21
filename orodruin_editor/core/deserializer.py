from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

import attr
from orodruin.core.deserializer import ExternalDeserializer

if TYPE_CHECKING:
    from orodruin_editor.ui.editor.graphics_state import GraphicsState
    from orodruin.core import Node, Connection, Graph, Port


@attr.s
class EditorDeserializer(ExternalDeserializer):
    """Deserialize nodes editor state."""

    graphics_state: GraphicsState = attr.ib()

    def deserialize_graph(self, data: Dict[str, Any], graph: Graph) -> None:
        return None

    def deserialize_node(self, data: Dict[str, Any], node: Node) -> None:
        pos = data.get("editor", {}).get("position", None)

        if pos is not None:
            graphics_node = self.graphics_state.get_graphics_node(node)
            graphics_node.setPos(*pos)

    def deserialize_port(self, data: Dict[str, Any], port: Port) -> None:
        return None

    def deserialize_connection(
        self, data: Dict[str, Any], connection: Connection
    ) -> None:
        return None
