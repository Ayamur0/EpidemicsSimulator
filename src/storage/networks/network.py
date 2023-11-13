from typing import List
from storage.networks.node_group import NodeGroup


class Network:
    def __init__(self) -> None:
        self.groups: List[NodeGroup] = []

    def add_group(self):
        pass

    def delete_group(self):
        pass

