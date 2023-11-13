from typing import List
from storage.graphs.node_group import NodeGroup
from storage.graphs.node import Node

class Node:
    def __init__(self, group: NodeGroup):
        self.id: str = 'a1' # auto set new id
        self.group: NodeGroup = group
        self.connections: List[Node] = [] # node ids this node is connected to
        # other properties, eg. infected, was infected x times, etc.

    @property
    def siblings(self) -> List[Node]:
        # return all siblings from parent group
        pass

    def add_connection(self, id: str) -> bool:
        pass

    def remove_connection(self, id: str) -> bool:
        pass

