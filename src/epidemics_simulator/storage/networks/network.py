import random
import sys
import time
from typing import List


# from storage import NodeGroup


class Network:
    def __init__(self) -> None:
        self.group_id_counter: int = 0
        self.groups: List["ng.NodeGroup"] = []

    def add_group(self, group: "ng.NodeGroup") -> bool:
        self.groups.append(group)
        return True

    def delete_group(self, group_id: str) -> bool:
        ret = any(g.group_id == group_id for g in self.groups)
        self.groups = [g for g in self.groups if g.group_id != group_id]
        return ret


if __name__ == "__main__":
    n = Network()
    n.add_group(10, 20, 4)
    g = "NodeGroup".all_instances_by_id["0"]
    g.create_members(100)
    for i in range(0, 1):
        g.create_internal_connections()
        print(g)
        g.reset_connections()
