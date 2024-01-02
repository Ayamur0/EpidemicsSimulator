from typing import List


class Node:
    # Class variable to store instances
    all_instances_by_id: dict[str, "Node"] = {}

    def __init__(self, group):
        self.id: str = f"{group.id}-{group.node_id_counter}"  # auto set new id
        group.node_id_counter += 1
        self.group = group
        self.int_connections: List["Node"] = []  # node ids this node is connected to
        self.ext_connections: List["Node"] = []  # node ids this node is connected to
        self.infected_time: int = 0
        self.infected = None
        self.num_of_infections: int = 0
        self.vaccinated: bool = False
        self.alive: bool = True
        # other properties, e.g. infected, was infected x times, etc.
        Node.all_instances_by_id[self.id] = self

    @property
    def siblings(self) -> List["Node"]:
        # return all siblings from parent group
        return self.connections

    @property
    def int_conn_amount(self) -> int:
        return len(self.int_connections)

    def get_ext_conn_amount(self, to_group: str = None) -> int:
        if to_group is None:
            return len(self.ext_connections)
        else:
            return len([i for i in self.ext_connections if to_group in i.id.split("-")[0]])

    def add_int_connection(self, target_id: str) -> bool:
        if (target := self.group.get_member(target_id)) is None:
            raise KeyError
        if target in self.int_connections:
            return False
        self.int_connections.append(target)
        target.int_connections.append(self)
        self.group.add_internal_edge(self.id, target_id)
        return True

    def add_ext_connection(self, target_id: str) -> bool:
        target_group = self.group.network.get_group_by_id(target_id.split("-")[0])
        if (target := target_group.get_member(target_id)) is None:
            raise KeyError
        if target in self.ext_connections:
            return False
        self.ext_connections.append(target)
        target.ext_connections.append(self)
        self.group.add_external_edge(self.id, target_id)
        return True

    def has_connection(self, target_id: str) -> bool:
        for node in [self.int_connections, self.ext_connections]:
            if node.id == target_id:
                return True
        return False

    def clear_connections(self) -> None:
        self.int_connections.clear()
        self.ext_connections.clear()

    def __str__(self):
        tmp = f"ID: {self.id}, Connections: ["
        for con in self.connections:
            tmp += f"{con.id}, "
        if tmp.endswith(", "):
            tmp = tmp[0:-2]
        return tmp + "]"

    def to_dict(self):
        return {
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, data, group):
        instance = cls(group=group)
        instance.id = data["id"]
        return instance
