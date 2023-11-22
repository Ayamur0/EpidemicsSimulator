import random
import sys
import time
from typing import List
from node_group import NodeGroup


class Network:
    def __init__(self) -> None:
        self.group_id_counter: int = 0
        self.groups: List[str] = []

    def add_group(self, size: int, aic: float, dic: float) -> bool:
        tmp_group = NodeGroup(self, size, aic, dic)
        self.groups.append(tmp_group.group_id)
        return True

    def delete_group(self, group_id: str) -> bool:
        for group in self.groups:
            tmp_group = NodeGroup.all_instances_by_id[group]
            if tmp_group.group_id != group_id:
                continue
            self.groups.remove(group)
            return True
        return False


if __name__ == '__main__':
    n = Network()
    n.add_group(10, 20, 4)
    g = NodeGroup.all_instances_by_id['0']
    g.create_members(100)
    for i in range(0, 1):
        g.create_internal_connections()
        print(g)
        g.reset_connections()


